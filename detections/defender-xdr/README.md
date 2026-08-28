# Detections — Microsoft Defender XDR

Specifications for the detections observed on the Defender side of this environment.
They are not all custom detection rules and none is an exported artifact: `DET-001` is
Microsoft's own built-in behavioural detection, `DET-002` a Microsoft-defined ASR rule,
`DET-003` an alert policy authored here. Each is tracked because it was observed firing,
not because it was authored.

Each specification records hypothesis, data requirements, trigger, and validation, plus
tuning and response where the mechanism has them.
