# gmail-job-pipeline
A Gmail API–based pipeline for collecting Freelancer job notification emails and exporting structured data (titles and URLs) via a layered workflow design.

# Gmail Job Extractor Pipeline
A Gmail API–based pipeline that fetches emails from specific senders,
extracts job titles and URLs from the HTML body,
and exports them as CSV files for downstream processing
such as scraping or analysis.


## How to Run
For execution instructions, see:
- [HOW_TO_RUN.md](./HOW_TO_RUN.md)


## Intended Use Cases
- Automatically collect job notification emails (e.g. Freelancer)
- Convert email content into structured data (title + URL)
- Use Gmail as the entry point of a personal automation pipeline


## Architecture / Directory Structure
This repository adopts a simple layered structure
to keep responsibilities clear and replaceable.

- src
  - Application source code (self-contained for public use)
- usecase
  - Workflow logic (path setup, authentication, fetching, extraction, cleansing)
- infrastructure
  - External system access (Gmail API, HTML parsing, file I/O)
- runner
  - Orchestration / execution entry point
- data
  - Runtime data (CSV outputs, OAuth/token files; not committed)

There is currently no dedicated domain layer.
The project is workflow-driven, and shared objects mainly serve
as pipeline context / DTOs rather than stable business models.

### Processing Flow
Initialization
- GmailSession (Infrastructure) is created once and shared

Execution Flow
- Runner
  -> SetupGmail (path setup)
  -> GetCredentials (OAuth / refresh)
  -> GetMessages (Gmail API)
  -> GetContents (HTML parsing / extraction)
  -> CleansingForScraping (CSV shaping)
  -> Output CSV


## Current Limitations
- Sender support is currently limited (freelancer only)
- Gmail API credentials are not included in the repository
- Error handling and retry logic are intentionally minimal
- No test suite yet
- Configuration is code-based (no CLI or environment switching)

This repository is a work-in-progress snapshot
of a personal automation pipeline prepared for public release.

