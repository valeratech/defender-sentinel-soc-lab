# Portal Navigation Index

Portal paths for every setting this project configures or verifies, each with the
date the path was last confirmed present. **Azure and Defender rename and relocate
these regularly** (this project has already hit "core folders" → "system folders"
in the ASR levels, and Microsoft is migrating Sentinel into the Defender portal by
2027). A path with a *confirmed* date says "this was true on this date" — if it has
moved since, that date is why. Treat it like the KB's `Sources checked`, not as a
standing guarantee.

Paths are written portal-first because the portal is what changes; the *setting*
being reached is stable even when its location is not.

## Microsoft Defender — `security.microsoft.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| Unified RBAC — roles & permissions | System → Permissions → Roles | 2026-07-17 |
| Unified RBAC — workload activation | System → Permissions → Roles → Activate workloads / Workload settings | 2026-07-17 |
| Custom role — member assignment | System → Permissions → Roles → *(role)* → Assignments → ⋮ → Edit | 2026-07-19 |
| Endpoint onboarding package | System → Settings → Endpoints → Onboarding | 2026-07-18 |
| Defender ↔ Intune connection | System → Settings → Endpoints → Advanced features → Microsoft Intune connection | 2026-07-17 |
| Device discovery — on/off | System → Settings → Endpoints → Advanced features → Device discovery | 2026-07-19 |
| Device discovery — mode (Basic/Standard) | System → Settings → Device discovery → Discovery setup | 2026-07-19 |
| Device groups | System → Settings → Endpoints → Permissions → Device groups | 2026-07-19 |
| ASR report (detections / configuration) | Reports → Attack surface reduction rules | 2026-07-19 |
| Device inventory | Assets → Devices | 2026-07-18 |
| Device timeline | Assets → Devices → *(device)* → Timeline | 2026-07-19 |
| Incidents & alerts | Incidents & alerts → Incidents / Alerts | 2026-07-18 |
| Advanced hunting | Hunting → Advanced hunting | 2026-07-18 |

## Microsoft Entra — `entra.microsoft.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| Create a user | Users → All users → New user | 2026-07-19 |
| User usage location | Users → *(user)* → Properties → Usage location | 2026-07-19 |
| Create a security group | Groups → New group (type: Security) | 2026-07-19 |
| Device settings (join permissions) | Devices → Device settings | 2026-07-17 |

## Azure — `portal.azure.com`

| Setting / view | Path | Confirmed |
|---|---|---|
| VM role assignments (IAM) | Virtual machines → *(VM)* → Access control (IAM) → Role assignments | 2026-07-17 |
| VM Run command | Virtual machines → *(VM)* → Run command → RunPowerShellScript | 2026-07-17 |
| VM Bastion session | Virtual machines → *(VM)* → Connect → Bastion | 2026-07-18 |
| VM reset password | Virtual machines → *(VM)* → Help → Reset password | 2026-07-18 |
| VM auto-shutdown | Virtual machines → *(VM)* → Operations → Auto-shutdown | 2026-07-17 |

## Which surface answers which question

Navigation is not only "where is the setting" — it is also "which view answers my
question." For endpoint activity, the surfaces are not interchangeable (Lab 06 §7):

| Question | Surface |
|---|---|
| Is something attacking this box that needs attention? | Incidents & alerts |
| What happened on this device, step by step? | Assets → Devices → Timeline |
| Is an ASR rule firing, and how often? | Advanced hunting *(the ASR report omits locally-set rules — `POS-031`)* |
| Hunt a pattern across all devices? | Advanced hunting (`DeviceEvents`) |
| Who holds a Defender role? | System → Permissions → Roles → *(role)* → Edit assignment *(count only shown until opened)* |
