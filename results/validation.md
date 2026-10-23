# Validation: Docker build, oracle, nop

Mirrors hosted `/validate`: one Harbor job, agents `oracle` and `nop`, one attempt each (`tools/run_validation.sh`).

- Harbor job: `validate-20261023-014832` (Docker build succeeded for the agent image and the verifier image; total runtime 4 min 52 s)

| Job | Trial | Agent | Model | Effort | Reward | Tests passed | Agent time (min) | Tokens in / out | Exception |
|---|---|---|---|---|---|---|---|---|---|
| validate-20261023-014832 | 4SNRd5X | oracle |  |  | 1.0 | 10/10 | 3 |  |  |
| validate-20261023-014832 | fq6dcRS | nop |  |  | 0.0 | 0/10 | 0 |  |  |

Oracle: all 10 verifier tests pass (inside the 2-CPU agent container: venv and
pip install of numpy/scipy/av, then about 2.5 min of analysis). Nop: all 10
fail (no report written).

The audio version of the task (iteration 1) validated the same way:
`validate-20261022-202434`, oracle 1.0 (10/10), nop 0.0 (0/10).
