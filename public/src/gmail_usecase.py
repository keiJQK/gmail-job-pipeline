from __future__ import print_function
import datetime, logging
import pandas as pd
from . import global_utils as gbut
logger = logging.getLogger("gmail")

# Gmail listing
class SetupGmail:
    '''
    Responsibility
    -----
    - Set paths of token, oauth, and save

    input:
        - session(infra)
        - ctx(DTO)
            - site_name(str)
            - date(str)
    output:
        - ctx.path_token(Path)
        - ctx.path_oauth_gmail(Path)
        - ctx.path_save(Path)
    '''
    def __init__(self, session):
        self.infra = session

    def run(self, ctx):
        site_name = ctx.site_name
        date = ctx.date

        path_token, path_oauth_gmail = self.infra.set_gmail_path()
        save_dir = self.infra.set_save_dir_gmail()
        fn_temp_save = self.infra.set_fn_temp_save_gmail()
        fn_save = fn_temp_save.format(
            site_name=site_name,
            date=date
        )
        save_path = save_dir / fn_save

        ctx.path_token = path_token 
        ctx.path_oauth_gmail = path_oauth_gmail 
        ctx.path_save = save_path

class GetCredentials:
    '''
    Responsibility
    -----
    - Authenticate credentials and Set service to fetch emails from Gmail API

    input:
        - session(infra)
        - ctx(DTO)
            - path_token(Path)
            - path_oauth_gmail(Path)

    output:
        - self.service in infra
            service authenticated and refreshed with creadentials
    '''
    def __init__(self, session):
        self.infra = session
        self.creds = None

    def run(self, ctx):
        path_token = ctx.path_token
        path_oauth_gmail = ctx.path_oauth_gmail

        self.check_token(path_token=path_token)
        self.get_credentials(
            path_token=path_token, 
            path_oauth_gmail=path_oauth_gmail
            )
        self.get_service()

    def check_token(self, path_token):
        if self.infra.os_exists(path_token=path_token):
            self.creds = self.infra.authorized_user_file(path_token=path_token)
            gbut.log_print(logger, "Existed token and authorized.")

    def get_credentials(self, path_token, path_oauth_gmail):
        if not self.creds:
            gbut.log_print(logger, "No creds → ReAuth")
            self.creds = self.infra.reauth(path_oauth_gmail)
            self.infra.save_creds(self.creds, path_token)
            return 

        if not self.creds.expired:
            gbut.log_print(logger, "Valid credentials")
            return

        if not self.creds.refresh_token:
            gbut.log_print(logger, "Expired & No refresh_token → ReAuth")
            self.creds = self.infra.reauth(path_oauth_gmail)
            self.infra.save_creds(self.creds, path_token)
            return 

        try:
            gbut.log_print(logger, "Expired & Not to refresh_token → Try refresh")
            self.infra.refresh(self.creds)
            self.infra.save_creds(self.creds, path_token)
        except Exception as e:
            gbut.log_print(logger, f"Refresh failed → ReAuth ({e})")
            self.creds = self.infra.reauth(path_oauth_gmail)
            self.infra.save_creds(self.creds, path_token)
            return

    def get_service(self):
        self.infra.set_service(self.creds)

class GetMessages:
    '''
    Responsibility
    -----
    - Get messages for the number of emails to fetch

    input:
        - session(infra)
        - ctx(DTO)
            - query(list[str])
                query for Gmail API e.g. ["from:freelancer.com"]
            - max_num(int)
    output:
        - ctx.messages(list)
            list of messages fetched for the number of emails to fetch
    '''
    def __init__(self, session):
        self.infra = session

    def run(self, ctx):
        query = ctx.query
        max_num = ctx.max_num

        results = self.infra.get_results(
            userId="me", 
            query=query, 
            max_num=max_num
            )
        messages = results.get("messages", [])

        ctx.messages = messages

class GetContents:
    '''
    Responsibility
    -----
    - Choose specific sender to fetch items from each mail

    input:
        - session(infra)
        - site_name(str)
            condition to choose class of sender
    output:
        - fetch results csv(saved)
    '''
    def __new__(cls, session, site_name):
        if site_name == "freelancer":
            return FreelancerContents(session=session)
        
class FreelancerContents:
    '''
    input:
        - session(infra)
        - ctx(str)
            - messages(list)
                messages returned from API
            - path_save(Path)
    output:
        - fetch results csv(saved)
    '''
    def __init__(self, session):
        self.infra = session

    def run(self, ctx):
        messages = ctx.messages
        path_save = ctx.path_save

        results = []
        for msg in messages:
            detail = self.infra.get_detail(msg=msg, userId="me", fmt="full")
            dt = self.get_datetime(detail)
            raw_urls, raw_titles = self.fetch_raw_data(detail)
            df = self.select_data(raw_urls, raw_titles, dt)
            results.append(df)
        df_merged = self.infra.concat_df(results=results)
        self.infra.save_df(df_merged, path_save)
        gbut.log_print(logger, msg=f"[Saved csv] {path_save}")
        
    def get_datetime(self, detail):
        raw_date = self.infra.parse_date(detail=detail)
        return datetime.datetime.fromtimestamp(int(raw_date)/1000).strftime("%Y-%m-%d %H:%M:%S")

    def fetch_raw_data(self, detail):
        parts = self.infra.get_parts(detail=detail)
        soup = self.infra.create_soup(parts=parts)
        return self.infra.get_raw_title_url(soup=soup)

    def select_data(self, raw_urls, raw_titles, dt):
        url_list = self._extract_url(raw_urls)
        title_list = self._extract_title(raw_titles)
        title_cleansed, url_cleansed = self._align_counts(title_list, url_list)

        dict_data = self._dict_data(dt, title_cleansed, url_cleansed)
        return pd.DataFrame(dict_data)

    def _extract_url(self, raw_urls):
        url_before_cleansing = []
        for u in raw_urls:
            for key in ["https://www.freelancer.com/projects/", "https://www.freelancer.com/contest/"]:
                if key in u:
                    url_before_cleansing.append(u)
        return url_before_cleansing
    
    def _extract_title(self, raw_titles):
        # Get title
        title_before_cleansing = []
        for t in raw_titles:
            if t.lower() not in ["see more", "bid now", "enter now"]:
                title_before_cleansing.append(t)
        return title_before_cleansing 

    def _align_counts(self, title_list, url_list):
        url_cleansed = [l for i, l in enumerate(url_list, start=1) if i % 3 == 1]
        title_cleansed = title_list[:len(url_cleansed)]
        gbut.log_print(logger, "parse_html", url=len(url_cleansed))
        gbut.log_print(logger, "parse_html", title=len(title_cleansed))
        return title_cleansed, url_cleansed

    def _dict_data(self, dt, titles:list, urls:list):
        return {
            "date": dt,
            "title": titles,
            "url": urls
            }
    


# After Gmail listing
class CleansingForScraping:
    '''
    Responsibility
    -----
    - Cleanse data of previous step for scraping in next step

    input:
        - session(infra)
        - ctx(DTO)
            - site_name(str)
                condition to choose class of sender
            - path_save(Path)
                load path saved from previous step

    output:
        - cleansed csv(saved)
    '''
    def __init__(self, session):
        self.infra = session

    def run(self, ctx):
        site_name = ctx.site_name
        path_load = ctx.path_save

        save_path = self.set_save_path(site_name)
        df = self.add_column(path_load)
        self.infra.save_df(df=df, path_save=save_path)
        gbut.log_print(logger, msg=f"[Saved csv] {save_path}")

    def set_save_path(self, site_name):
        fn_temp_save = self.infra.set_fn_temp_save_cleansing()
        fn_save = fn_temp_save.format(
            site_name=site_name
        )
        save_dir = self.infra.set_save_dir_cleansing()
        return save_dir / fn_save

    def add_column(self, path_load):
        df = self.infra.load_df(path_load=path_load)
        df.insert(0, "index", 1)
        df.insert(1, "sq", range(1, len(df)+1))
        return df





