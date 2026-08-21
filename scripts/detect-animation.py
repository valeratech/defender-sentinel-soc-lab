#!/usr/bin/env python3
"""detect-animation.py — single-image contract check (AUD-007 facet g).

Multi-image content in a supported container defeats single-raster OCR: a
later APNG/animated-WebP frame — or a second JPEG inside a CIPA Multi-Picture
Format (MPO) file — can carry text the scan never sees (Tesseract surfaces
one raster and exits 0). Every supported publication image must therefore
represent exactly one OCR-relevant image; PNG/WebP animation and JPEG
Multi-Picture Format are rejected until deliberately supported
(SANITIZATION.md §10).

Content-driven, deliberately extension-free: dispatch is by magic bytes, so
this file names no extension list and cannot drift from the authority.

Structural validation is part of the contract (reviews P12/P16): single-image
is only ever asserted about a container this tool walked completely and
verified — chunk bounds, chunk CRCs, required image data, terminal structure,
and no bytes after it. Anything else is the fail-closed code.

Exit codes:
  0  structurally complete single-image PNG, WebP, or JPEG — for JPEG this
     requires exactly one frame header (SOF) with at least one scan (SOS)
  1  multi-image (APNG acTL / WebP animation / JPEG APP2 MPF)
  2  unreadable, truncated, or structurally invalid (fail closed at caller)
  3  not a PNG/WebP/JPEG container (no contract applies; caller passes)
"""
import struct
import sys
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_verdict(data: bytes) -> int:
    pos = 8
    n = len(data)
    first = True
    animated = False
    saw_idat = False
    while True:
        if pos + 8 > n:
            return 2
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        if not ctype.isalpha():
            return 2
        if first and ctype != b"IHDR":
            return 2
        first = False
        end = pos + 8 + length + 4
        if end > n:
            return 2
        # Chunk CRC covers type + payload (P16).
        (crc,) = struct.unpack(">I", data[end - 4:end])
        if zlib.crc32(data[pos + 4:pos + 8 + length]) & 0xFFFFFFFF != crc:
            return 2
        if ctype == b"acTL":
            animated = True
        if ctype == b"IDAT":
            saw_idat = True
        if ctype == b"IEND":
            if length != 0:
                return 2
            if not saw_idat:
                return 2  # a PNG without image data is not a valid image (P16)
            if end != n:
                return 2  # bytes after IEND (P16)
            return 1 if animated else 0
        pos = end


def webp_verdict(data: bytes) -> int:
    n = len(data)
    if n < 12 or data[8:12] != b"WEBP":
        return 2
    (riff_size,) = struct.unpack("<I", data[4:8])
    if riff_size + 8 != n:
        return 2
    pos = 12
    animated = False
    saw_bitstream = False
    while pos < n:
        if pos + 8 > n:
            return 2
        tag = data[pos:pos + 4]
        (size,) = struct.unpack("<I", data[pos + 4:pos + 8])
        end = pos + 8 + size + (size & 1)
        if end > n:
            return 2
        if tag in (b"ANIM", b"ANMF"):
            animated = True
        if tag == b"VP8X":
            if size < 1:
                return 2
            if data[pos + 8] & 0x02:
                animated = True
            # VP8X is the extended-feature descriptor, NOT image data (P16).
        if tag in (b"VP8 ", b"VP8L"):
            saw_bitstream = True
        pos = end
    if animated:
        return 1
    if not saw_bitstream:
        return 2  # no VP8/VP8L bitstream chunk — not a valid single image
    return 0


# SOF markers: all frame headers except DHT(C4), JPG(C8), DAC(CC), which
# share the 0xC0-0xCF band but are not frame declarations.
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def jpeg_verdict(data: bytes) -> int:
    n = len(data)
    pos = 2  # past SOI
    frames = 0
    scans = 0
    frame_components: list[int] = []
    while True:
        if pos + 2 > n:
            return 2
        if data[pos] != 0xFF:
            return 2
        marker = data[pos + 1]
        if marker == 0xFF:  # fill byte
            pos += 1
            continue
        if marker == 0xD9:  # EOI
            if pos + 2 != n:
                return 2  # trailing data — e.g. a second concatenated JPEG (P15/P16)
            # Positive image-state evidence (review P20): reaching EOI is not
            # enough. A clean JPEG must declare exactly one frame (SOF) and
            # carry at least one scan (SOS) for it. Zero-frame files —
            # SOI/EOI, or a JFIF APP0 header with no SOF/SOS — are structural
            # failures, not single images; multiple frame declarations are not
            # provably the one OCR-relevant image this contract requires.
            if frames != 1 or scans < 1:
                return 2
            return 0
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:  # standalone
            pos += 2
            continue
        if pos + 4 > n:
            return 2
        (seglen,) = struct.unpack(">H", data[pos + 2:pos + 4])
        if seglen < 2 or pos + 2 + seglen > n:
            return 2
        payload = data[pos + 4:pos + 2 + seglen]
        if marker == 0xE2 and payload[:4] == b"MPF\x00":
            return 1  # CIPA Multi-Picture Format: more than one image (P15)
        if marker in SOF_MARKERS:
            # A frame header must actually declare a frame (review P21):
            # precision(1) + height(2) + width(2) + component count(1), then
            # 3 bytes per component. Non-zero dimensions and at least one
            # component are required; an empty or short SOF is malformed.
            if len(payload) < 6:
                return 2
            precision = payload[0]
            (height,) = struct.unpack(">H", payload[1:3])
            (width,) = struct.unpack(">H", payload[3:5])
            ncomp = payload[5]
            if precision == 0 or height == 0 or width == 0 or ncomp == 0:
                return 2
            if len(payload) != 6 + 3 * ncomp:
                return 2
            # Retain the frame's component identifiers so scans can be bound
            # to this frame (review P21 residual). Duplicate frame component
            # IDs are themselves malformed.
            frame_components = [payload[6 + 3 * i] for i in range(ncomp)]
            if len(set(frame_components)) != ncomp:
                return 2
            frames += 1
            if frames > 1:
                return 2  # more than one frame declaration (P20)
        if marker == 0xDA:
            if frames != 1:
                return 2  # scan without exactly one preceding frame header
            # A scan header must declare its components (review P21):
            # component count(1) + 2 bytes per component + 3 trailing bytes.
            if len(payload) < 1:
                return 2
            nscomp = payload[0]
            if nscomp == 0 or len(payload) != 1 + 2 * nscomp + 3:
                return 2
            # Every scan component selector must name a component declared by
            # the single frame, and no selector may repeat (review P21
            # residual). A scan referring to a component the frame does not
            # contain is not a scan of that frame.
            selectors = [payload[1 + 2 * i] for i in range(nscomp)]
            if len(set(selectors)) != nscomp:
                return 2
            if nscomp > len(frame_components):
                return 2
            for sel in selectors:
                if sel not in frame_components:
                    return 2
            scans += 1
        pos += 2 + seglen
        if marker == 0xDA:  # SOS — skip entropy-coded data to next real marker
            scan_start = pos
            while True:
                if pos + 2 > n:
                    return 2
                if data[pos] == 0xFF and data[pos + 1] not in (0x00,) \
                        and not (0xD0 <= data[pos + 1] <= 0xD7):
                    break
                pos += 1
            if pos == scan_start:
                return 2  # scan carried no entropy-coded data (review P21)


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    try:
        with open(sys.argv[1], "rb") as fh:
            data = fh.read()
    except OSError:
        return 2
    if data.startswith(PNG_MAGIC):
        return png_verdict(data)
    if data[:4] == b"RIFF":
        return webp_verdict(data)
    if data[:2] == b"\xff\xd8":
        return jpeg_verdict(data)
    return 3


if __name__ == "__main__":
    sys.exit(main())
