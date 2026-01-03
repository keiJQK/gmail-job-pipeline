from __future__ import print_function
import os.path, base64, logging
import pandas as pd
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from . import global_vars as gv
from . import global_utils as gbut

logger = logging.getLogger("gmail")
DATA_DIR = gv.DATA_DIR

class GmailSession:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    # Setup
    def set_gmail_path(self):
        path_token = DATA_DIR / "token_gmail.json"
        path_oauth_gmail = DATA_DIR / "oauth_gmail.json"
        return path_token, path_oauth_gmail

    def set_save_dir_gmail(self):
        return DATA_DIR
    
    def set_fn_temp_save_gmail(self):
        return "gmail_{site_name}_{date}.csv"

    # GetCredentials
    def os_exists(self, path_token):
        return os.path.exists(path_token)

    def authorized_user_file(self, path_token):
        return Credentials.from_authorized_user_file(path_token, self.SCOPES)

    def refresh(self, creds):
        return creds.refresh(Request())

    def reauth(self, path_oauth_gmail):
        flow = InstalledAppFlow.from_client_secrets_file(
            path_oauth_gmail, self.SCOPES
        )
        return flow.run_local_server(port=0)

    def save_creds(self, creds, path_token):
        with open(path_token, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    def set_service(self, creds):
        self.service = build("gmail", "v1", credentials=creds)
        
    # GetMessages
    def get_results(self, userId, query, max_num):
        results = self.service.users().messages().list(
            userId=userId,
            q=query,
            maxResults=max_num
        ).execute()
        return results

    # GetContents
    def get_detail(self, msg, userId, fmt):
        return self.service.users().messages().get(
            userId=userId,
            id=msg["id"],
            format=fmt
        ).execute()

    def parse_date(self, detail):
        # Get date
        return detail["internalDate"]

    def get_parts(self, detail):
        # Get payload for HTML
        return detail["payload"].get("parts", [])

    def create_soup(self, parts):
        body = ""
        for part in parts:
            if part.get("mimeType") == "text/html":
                data = part["body"]["data"]
                body = base64.urlsafe_b64decode(data).decode("utf-8-sig")
                break
        # Set soup
        return BeautifulSoup(body, "html.parser")

    def get_raw_title_url(self, soup):
        # Get URL
        url_all = [a.get("href") for a in soup.select("tr > td > a")]
        title_all = [span.get_text() for span in soup.select("tr > td > a > span")]
        return url_all, title_all

    # Save
    def concat_df(self, results):
        return pd.concat(results) 

    def save_df(self, df, path_save):
        gbut.save_csv(path_save, df)

    # Cleansing
    def load_df(self, path_load):
        return pd.read_csv(path_load, encoding="utf-8-sig")

    def set_fn_temp_save_cleansing(self):
        return "output-gmail_{site_name}.csv"

    def set_save_dir_cleansing(self):
        return DATA_DIR
    

