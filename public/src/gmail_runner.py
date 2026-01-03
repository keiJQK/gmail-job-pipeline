from __future__ import print_function
import logging
from . import global_vars as gv
from . import global_utils as gbut

from . import gmail_infrastructure as inf
from . import gmail_usecase as uc

# Entry point for running the Gmail pipeline

# ----- DTO -----
class GmailContext:
    def __init__(self, site_name:str, date:str, query:list[str], fetch_num:int):
        self.site_name = site_name
        self.date = date
        self.query = query
        self.max_num = fetch_num

        self.path_token = None
        self.path_oauth_gmail = None
        self.path_save = None
        self.messages = None

# ----- Runner -----
class RunnerGmail:
    '''
    Responsibility
    -----
    - To fetch title and URL from gmail and cleanse data for scraping in next step
    - Currently, sender is "freelancer"

    input:
        - session(infra)
        - ctx(DTO)
            - site_name(str)
            - date(str)
            - query(list[str])
                query for Gmail API e.g. ["from:freelancer.com"]
            - fetch_num(int)
                the number of emails to fetch
    output:
        - output csv(saved)
            data cleansed for scraping
    '''
    def __init__(self, session, ctx):
        self.ctx = ctx
        self.steps = [
            (uc.SetupGmail(session=session), f"STEP: Setup Path"),
            (uc.GetCredentials(session=session),  f"STEP: Auth Credentials"),
            (uc.GetMessages(session=session), f"STEP: Get messages"),
            (uc.GetContents(session=session, site_name=ctx.site_name), f"STEP: Get data from each message"),
            (uc.CleansingForScraping(session=session), f"Step: Cleansing data for scraping"),
        ]
    
    def run_steps(self):
        for step, log in self.steps:
            step.run(ctx=self.ctx)
            gbut.log_print(logger, msg=log)

if __name__ == "__main__":
    try:    
        logger = gbut.setup_logger(fn="gmail", logger_name="gmail")

        ctx = GmailContext(
            site_name="freelancer",
            date="20260102",
            query=["from:freelancer.com"],
            fetch_num=1,
        )
        infra = inf.GmailSession()
        RunnerGmail(session=infra, ctx=ctx).run_steps()
    except Exception as e:
        gbut.logging_error(logger=logger, src_dir=gv.LOG_DIR, e=e)
    gbut.log_print(logger, f"---------------")
