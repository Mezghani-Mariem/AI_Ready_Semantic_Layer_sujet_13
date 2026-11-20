# DEV2 — AdventureWorks AI-Readiness: final technical delivery

## Scope
US-05: English-language business descriptions (36 entries: 7 tables, 24 columns, 5 measures) and approved synonyms for 21 fields/measures. US-06: PBIP/TMDL assets, exported `.lsdl.yaml`, reproducible Python injection and verification.

## Critical distinction
The file `fr-FR.enriched.template.tmdl` is based on the user's **DEV2-edited** Power BI linguistic metadata, not on the raw DEV1 baseline. The raw DEV1 `fr-FR.tmdl` may contain only `cultureInfo fr-FR`. The deployment script copies a ready-made, model-specific template; it does **not** generate linguistic metadata from scratch. The separately supplied YAML is an export from DEV2, not an automatically imported/copied part of the PBIP deployment.

## Prerequisites
- Windows and Python 3.12 (standard library only)
- A **clean baseline** Power BI project directory such as `C:\Users\Lenovo\Desktop\DEV1_BASELINE_TEST`, containing `F1.pbip` and `F1.SemanticModel` (with `definition/tables` and minimal `definition/cultures/fr-FR.tmdl`).
- Power BI Desktop **closed** during file operations.
- Prefer an unmodified backup of F1 rather than the previously used baseline (where metadata may already have been injected).

## Run the integrated deployment
In Windows CMD, in the directory containing this README and the scripts:

```cmd
python deploy_dev2.py "C:\Users\Lenovo\Desktop\DEV1_BASELINE_TEST" "C:\Users\Lenovo\Desktop\DEV2_REPRODUCTION_FINAL"
```

The destination must NOT already exist. The tool copies the full project (excluding transient `.pbi` cache) into a fresh directory, injects and checks the 36 descriptions, installs and verifies the 21-object linguistic template, and emits `DEV2_DEPLOYMENT_RESULT.json` in the copy. It never writes into the source project. If an error occurs, it removes the incomplete destination.

To repeat, choose **another new** output directory; never delete or overwrite your active DEV2 project.

## Manual Power BI validation (still required)
1. Open the copied `F1.pbip` in the new output directory.
2. Model view > `_Mesures` > `Margin`: check English description and synonyms `margin amount, sales margin, gross profit, margin`.
3. Verify `Total Sales`, `Total Quantity`, and several other business fields; verify DAX expressions and relationships.
4. Save, close, reopen and confirm metadata persists.
5. Record screenshots and any parsing/refresh warnings in the final project report.

**Do not click Refresh simply to validate metadata:** source Excel paths may refer to DEV1's machine. Data loading, Copilot performance and the benchmark belong to integration with DEV1/DEV3.

## Recorded evidence from Windows CMD (user provided, 30 October 2026)
- `inject_descriptions.py` on baseline: `Found 36/36 metadata targets. Files differing: 7` then `--check`: `Files differing: 0`.
- `inject_synonyms.py` on a DEV2-derived culture file: 21 matched fields and 34 newly added terms. Repeated run: 0 new terms; `fc /b` reported no differences.
- A culture template copied into `F1.SemanticModel` displayed `Margin` synonyms in Power BI after reopening.
- YAML `AdventureWorks_DEV2.lsdl.yaml` exported from Power BI: `Version: 4.1.0` and `Language: en-US`.

## Limitations
- The verified synonym automation updates an **existing structured** culture. The integrated deployment installs a known-good template into a clean baseline, and rejects a pre-enriched culture to avoid overwriting work.
- Power BI Copilot answer correctness is not established by successful installation of linguistic metadata. Q&A synonym interpretation and Copilot behavior must be evaluated independently.
- There were data-refresh warnings in Power BI, not resolved by DEV2 scripts.
- The script validates a known AdventureWorks schema (the named fields) and should not be assumed compatible with an updated DEV1 schema without review.
