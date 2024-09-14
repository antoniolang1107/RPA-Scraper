"""Handles sending links to email addresses"""

# reference: https://developers.google.com/gmail/api/quickstart/python
# reference: https://thepythoncode.com/article/use-gmail-api-in-python

from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import pickle

from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://mail.google.com/"]


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
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)


def build_message(destination, obj, body, body_format):
    """Builds message for email"""
    message = MIMEText(body, body_format)
    message["to"] = destination
    message["from"] = sender_address
    message["subject"] = obj
    return {"raw": urlsafe_b64encode(message.as_bytes()).decode()}


def send_message(
    service, destination: str, obj: str, body: str, body_format: str = "plain"
):
    """Send message via Google API"""
    return (
        service.users()
        .messages()
        .send(userId="me", body=build_message(destination, obj, body, body_format))
        .execute()
    )


def generate_message_html(listings_details: dict) -> str:
    """Converts from listings detail to structured HTML"""

    html_body = []
    for subgroup, listings in listings_details.items():
        html_body.append(f"<h4>{subgroup}</h4>")
        for listing_name, links in listings.items():
            html_body.append("<ul>")
            # for link in links:
            #     html_body.append()
            anchor_links = [
                f"<a href='{link}'>Link {index}</a>"
                for index, link in enumerate(links, 1)
            ]
            html_body.append(f"<li>{listing_name}: {', '.join(anchor_links)}</li>")
            html_body.append("</ul>")

    html_body.insert(
        0,
        "<html><body><h1>Links!</h1><p>"
        "Included are links to Reno Public Auction categories and keywords "
        "you subscribed to.</p>",
    )
    html_body.insert(-1, "</body></html>")

    # use this if "category" and "keyword" sections are specified
    # for high_level_group, subgroup in listings_details.items():
    #     html_body.append(f"<h3>{high_level_group}</h3>")
    #     for subgroup_name, listing in subgroup.items():
    #         html_body.append(f"<h5>{subgroup_name}</h5>")
    #         for listing_name, links in listing.items():
    #             html_body.append(f"")

    full_html: str = "".join(html_body)
    return full_html


load_dotenv()

sender_address: str = os.environ["SENDER_ADDRESS"]
password: str = os.environ["PASSWORD"]
receiver_email: str = os.environ["RECEIVER_ADDRESS"]


if __name__ == "__main__":
    email_service = gmail_authenticate()
    html: str = generate_message_html(
        {
            "website": {"myTest": ["https://duckduckgo.com"]},
            "same website": {"myTest2": ["https://duckduckgo.com"]},
        }
    )
    send_message(email_service, receiver_email, "Hello From A Python Script!", html, "html")
