# LABELLED TEST DOUBLE — NOT THE FROZEN ENGINE

These modules imitate the *call surfaces* of the frozen Unit-6 engine so the
integration layer's control flow (PASS/REJECT/ERROR/NOT_RUN separation,
fail-closed refs, identity binding, private/CI isolation, return-channel
hardening) can be exercised without the frozen bytes.

They carry none of the frozen engine's logic, keys, MAC scheme or detector
identities. Their SHA-256s live in `double-identities.txt`, which the
controls pass to `engine_bind.bind(identity_file=...)`. Production entry
points never reference this directory. Binding the double through the
production identity manifest fails with ENGINE_IDENTITY_MISMATCH (that is
itself a control: see test_engine_bind).
