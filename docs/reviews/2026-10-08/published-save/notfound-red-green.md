# GetAndWait NotFound regression evidence

## Red before first Store fix

Command: `python -m pytest Tests/test_save_v1_lua.py -q -k 'profile_not_found_with_open_gate or profile_and_gate_not_found or profile_not_found_with_raw_payload'`

The first two cases failed: profile NotFound with an OPEN gate did not initialize, and confirmed missing bootstrap gate did not produce setup. The third case initially expected `blocked`, so that assertion failed; this was not a production defect. The original `code ~= 0` path already retried without writing for NotFound with a raw value. The test was corrected to require retry/no write, preserving that existing safety behavior.

## Red before prewrite-release fix

Command: `python -m pytest Tests/test_save_v1_lua.py -q -k prewrite_abort`

Result: the new positive case failed (`ReleaseBootstrapGateBeforeWrite` returned false for confirmed profile NotFound with nil raw); the guards for an already attempted Set and for NotFound-with-data/throw passed.

## Green after fixes

Command: `python -m pytest Tests/test_save_v1_lua.py -q`

Result: **50 passed, 7 subtests passed**. `git diff --check` passed.

Coverage includes: profile `1000002` with nil raw, including recheck, initializes once under an OPEN gate using fake storage; missing gate `1000002` produces setup without profile write; NotFound with raw retries without treating the value as success or writing; non-NotFound and thrown reads retry without writes; existing profiles skip the gate; legacy and unknown-owner cases remain green. A pre-Set confirmed NotFound(nil) releases via the existing exact-owner CAS; a Set-attempted account, NotFound-with-data, or thrown read does not release. Set/readback acknowledgements remain strict code `0` and exact payload.

This is production-body harness evidence only. No Maker runtime, published server, or live DataStorage was used.
