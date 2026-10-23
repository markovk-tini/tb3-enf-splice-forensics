# Validation: Docker build, oracle, nop

Mirrors hosted `/validate`: one Harbor job, agents `oracle` and `nop`, one attempt each (`tools/run_validation.sh`).

- Harbor job: `validate-20261023-172156` (Docker build succeeded for the agent image and the verifier image; total runtime 7 min 5 s)

| Job | Trial | Agent | Model | Effort | Reward | Tests passed | Agent time (min) | Tokens in / out | Exception |
|---|---|---|---|---|---|---|---|---|---|
| validate-20261023-172156 | xqgVEG7 | oracle |  |  | 1.0 | 13/13 | 6 |  |  |
| validate-20261023-172156 | btvXo7y | nop |  |  | 0.0 | 0/13 | 0 |  |  |

Oracle: all 13 verifier tests pass (inside the 2-CPU agent container: venv and
pip install of numpy/scipy/av, then about 5.5 min of analysis; it picks the
frame-timing channel for exhibit_09, the sound for exhibit_10 with a measured
A/V lag of +3.60 s, and dates exhibit_11's insert against exhibit_08). Nop:
all 13 fail (no report written).

Earlier versions validated the same way: iteration 1 (audio)
`validate-20261022-202434` and iteration 2 (video) `validate-20261023-014832`,
both oracle 1.0 and nop 0.0.
