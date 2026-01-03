## How to Run
### Prerequisites
- Python 3.10 or later
- Gmail API credentials
  - Create OAuth credentials in Google Cloud Console
  - Place the following files under `data/`:
    - `oauth_gmail.json` (how to create this file is described below)
    - `token_gmail.json` (created automatically after first authentication)

### Dependencies
This project includes a `requirements.txt`
containing the minimum libraries required to run the pipeline,
independent of the author’s local development environment.

Install dependencies with:
- pip install -r requirements.txt

### Gmail API Setup (Required)
Before running the script, you must enable Gmail API
and create OAuth credentials in Google Cloud Platform.

Steps:
1. Go to Google Cloud Console
2. Create a new project (or select an existing one)
3. Enable the Gmail API for the project
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials JSON file
6. Rename it to `oauth_gmail.json`
7. Place it under the `data/` directory

The OAuth consent screen must be configured at least once.
During the first script execution, a browser window will open
to complete Gmail authorization.

### Execute
From the project root (where `src/` exists):

- python -m src.gmail_runner

Run from the project root directory.
No PYTHONPATH configuration is required.

Execution parameters (sender, query, fetch size)
are currently defined directly in `gmail_runner.py`.

### Example (Minimal Run):
- sender: freelancer
- query: ["from:freelancer.com"]
- fetch_num: 1

### Authentication Note
On the first run (initial Gmail token setup):
- A browser window will open for Gmail OAuth authorization
- After authorization, credentials will be saved under `data/`
- Because authentication occurs during execution,
  please run the script again after authorization is completed

On the second and subsequent runs:
- The script will use the saved credentials
- Fetch recent emails from the configured sender
- Extract job titles and URLs
- Save CSV output under `data/`
