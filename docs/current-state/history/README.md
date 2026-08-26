# history/ — verified copies, not authority

Each file mirrors the mutable fields of one Reviewer document at the moment
that document was authoritative and binds the document by SHA-256. These are
labelled historical copies. `2026-08-25-rev1.json` mirrors the successor
handoff authority; several of its fields (role activation, pass counter,
Phase-2 reauthorization in principle) have since moved in the governed thread,
which is exactly why it is not the bound current revision.
