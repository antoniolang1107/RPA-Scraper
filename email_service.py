"""Handles sending links to email addresses"""

# reference: https://developers.google.com/gmail/api/quickstart/python
# reference: https://thepythoncode.com/article/use-gmail-api-in-python

from base64 import urlsafe_b64encode
import os
import pickle

from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCOPES = ['https://mail.google.com/']

def gmail_authenticate():
    """Google API"""
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def build_message(destination, obj, body, body_format):
    message = MIMEText(body, body_format)
    message['to'] = destination
    message['from'] = sender_address
    message['subject'] = obj
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}


def send_message(service, destination: str, obj: str, body: str, body_format: str = "plain"):
    """Send message via Google API"""
    return service.users().messages().send(
        userId="me",
        body=build_message(destination, obj, body, body_format)
    ).execute()

load_dotenv()

sender_address: str = os.environ['SENDER_ADDRESS']
password: str = os.environ['PASSWORD']
receiver_email = os.environ['RECEIVER_ADDRESS']


if __name__ == "__main__":
    service = gmail_authenticate()
    html = """\
    <html>
    <body>
        <h1>Links!</h1>
        <p>Included are links to categories and keywords you subscribed to.</p>
        <h3>Categories</h3>
        <ul>
            <li><a href="">[listing title]</a></li>
        </ul>
        <h3>Keywords</h3>
        <ul>
            <li><a href="">[listing title]</a></li>
        </ul>
    </body>
    </html>
    """
    send_message(service, receiver_email, "test subject", html, "html")
