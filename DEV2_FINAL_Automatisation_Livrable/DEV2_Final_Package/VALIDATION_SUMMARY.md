# DEV2 — Evidence and acceptance status

| Control | Observation | Status |
|---|---|---|
| Power BI project exported as PBIP/TMDL | `AdventureWorks_DEV2.pbip` and model `definition/tables` created | Confirmed |
| 36 English descriptions injected into DEV1 PBIP copy | 36/36 found; seven TMDL files changed | Confirmed by Windows terminal |
| Description idempotence | `--check`: zero differing files | Confirmed by Windows terminal |
| 21 linguistic targets, 34 terms added | Injector output | Confirmed on DEV2-derived culture |
| Synonym idempotence | Rerun: zero terms; byte comparison identical | Confirmed by Windows terminal |
| Synonyms in F1 after culture template install | `Margin` synonym set appeared in Power BI | Confirmed by screenshot |
| Standalone YAML export | Power BI-exported `.lsdl.yaml`, internal language en-US | Confirmed |
| Integrated deployment script | Local test on reconstituted minimal baseline: 36/36, 7 files differing, 21 bindings; overwrite safeguard | Tested in sandbox; Windows end-to-end pending |
| Copilot accuracy improvement | No before/after benchmark provided | Not yet verified (DEV3) |
| Data refresh and source compatibility | Power BI showed incomplete-data warnings | Unresolved (DEV1/team) |

## Architecture
`F1.pbip (baseline)` -> `deploy_dev2.py` -> `isolated PBIP copy` -> `TMDL descriptions + culture template` -> `Power BI validation` -> `Copilot benchmark (DEV3)`.

No claims are made about measured Copilot gains, complete DEV1 data readiness, or a clean-computer installation.
