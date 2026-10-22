# Validation: Docker build, oracle, nop

Mirrors hosted `/validate`: one Harbor job, agents `oracle` and `nop`, one attempt each (`tools/run_validation.sh`).

- Harbor job: `validate-20261022-202434` (Docker build succeeded for the agent image and the verifier image)

| Job | Trial | Agent | Model | Effort | Reward | Tests passed | Agent time (min) | Tokens in / out | Exception |
|---|---|---|---|---|---|---|---|---|---|
| validate-20261022-202434 | HCgZDBV | oracle |  |  | 1.0 | 10/10 | 1 |  |  |
| validate-20261022-202434 | b4T942T | nop |  |  | 0.0 | 0/10 | 0 |  |  |

Oracle: all 10 verifier tests pass. Nop: all 10 fail (no report written).
