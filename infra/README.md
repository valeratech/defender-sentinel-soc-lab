# Infrastructure as Code

No deployment templates are committed here. Configuration state is recorded in the lab
writeups and `posture.yml` rather than represented by declarative deployment templates
in this directory. This directory is reserved for templates and currently holds none.

The policy that governs it if any land here: parameter files are gitignored — they carry real subscription and tenant identifiers. Commit `*.parameters.example.json` with placeholder values instead.
