import base64
import json
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def gmail_service_login():

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    # store credentials for next time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_messages_with_attachments(service, query):
    """ finds all messages that match the query and returns a list of objects with these attributes:
        "filename" - file name of attachement
        "snippet" - text of the messages
        "message_id" - message id
        "attachment_id" - attachment id
        "date" - date the messages was received
    """

    results = service.users().messages().list(userId='me', q=query, maxResults=5000).execute()   
    messages = results.get('messages', [])
    results_list = []

    if messages:
        for m in messages:
            msg_date = 'unknown'
            message_id = m['id']
            msg = service.users().messages().get(userId='me', id=message_id).execute()
            snippet = msg.get('snippet', "")
            for header in msg['payload']['headers']:
                if header['name'] == 'Date':
                    msg_date = header['value']
            for part in msg['payload']['parts']:
                filename = part['filename']
                if 'attachmentId' in part['body']:
                    attachment_id = part['body']['attachmentId']
                    photo_message = { "filename" : filename,
                                      "snippet" : snippet,
                                      "message_id": message_id,
                                      "attachment_id": attachment_id,
                                      "date" : msg_date
                                      }
                    results_list.append(photo_message)
    return results_list

def download_attachment(service, attachment_id, message_id, filename):
    attachment = service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
    data_base64urlencoded = attachment['data']
    file_data = base64.urlsafe_b64decode(data_base64urlencoded.encode('UTF-8'))

    with open(filename, 'wb') as f:
        f.write(file_data)


if __name__ == '__main__':
    pass
