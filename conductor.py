"""Module to query for and send emails"""

import os

from dotenv import load_dotenv
from email_service import gmail_authenticate, send_message, generate_message_html
from scraper import run_job, read_config

load_dotenv()
receiver_email: str = os.environ["RECEIVER_ADDRESS"]
job_config_fname: str = os.environ["CONFIG_FNAME"]

if __name__ == "__main__":
    job_results: dict = run_job(read_config(job_config_fname))
    email_service = gmail_authenticate()
    html_message: str = generate_message_html(job_results)
    send_message(email_service, receiver_email, "RPA Links", html_message, "html")
