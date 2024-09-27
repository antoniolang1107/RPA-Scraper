"""Module to query for and send emails"""

import os

from dotenv import load_dotenv
from email_service import gmail_authenticate, send_message, generate_message_html
from scraper import run_job, read_config

load_dotenv(override=True)
receiver_email: str = os.environ["RECEIVER_ADDRESS"]
conductor_config_fname: str = os.environ["CONDUCTOR_CONFIG_FNAME"]

def run_jobs(jobs_config: dict) -> None:
    """Runs set of jobs"""
    email_service = gmail_authenticate()
    for job in jobs_config.values():
        try:
            job_recipient: str = job["job_recipient_address"]
            job_config_fname: str = job["job_config_fname"]
            job_results: dict = run_job(read_config(job_config_fname))
            html_message: str = generate_message_html(job_results)
            send_message(email_service, job_recipient, "RPA Links", html_message, "html")
        except OSError:
            print("Could not find job file")

if __name__ == "__main__":
    conductor_config: dict = read_config(conductor_config_fname)
    run_jobs(conductor_config)
