# Analytics Rules — Microsoft Sentinel

Specifications for the Sentinel analytics rules exercised in this project. Both are
scheduled analytics rules. No exported JSON or YAML is committed here, and nothing in
this directory is deployable via Sentinel Repositories CI/CD — the rules were built and
measured in the tenant, and what is kept is the specification.

Each specification records hypothesis, data requirements, trigger, and validation.
Tuning and response are recorded where there is something to record: `DET-004` states
that no automated response is attached, and `DET-005` documents a correctly configured
rule that has never fired.
