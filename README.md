# Data Engineering Portfolio

This portfolio presents completed data-engineering work, with an emphasis on repeatable ingestion, cleaning, validation, and analytics-ready outputs.

## Projects

### Subscriber Cancellations Data Pipeline

The pipeline transforms the Cademycode source SQLite database into a clean, analytics-ready database and CSV export. It parses JSON contact data, converts numeric fields, joins lookup tables, validates records, writes outputs atomically, and records operational changes and failures.

- Source project: `subscriber-pipeline/subscriber-pipeline-starter-kit/`
- Main pipeline: `src/pipeline.py`
- Tests: `tests/test_pipeline.py`
- Outputs: `production/`
- Documentation: `README.md` and `WRITEUP.md`

## Project organization

Each project should be placed in its own folder with its source code, tests, documentation, and reproducible run instructions.
