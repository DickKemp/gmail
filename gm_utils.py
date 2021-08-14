import base64
import json
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def gmail_service_login(credentials_file='credentials.json', cached_credentials='token.pickle'):
    """ connects to the google gmail service and returns a service object
    that can be used to interact with the google API
    """

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    # store credentials for next time
    if os.path.exists(cached_credentials):
        with open(cached_credentials, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(cached_credentials, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def find_messages_that_have_attachments(service, query):
    """ finds all messages that match the query and returns a list of objects with these attributes:
        "filename" - file name of attachement
        "snippet" - text of the messages
        "message_id" - message id
        "attachment_id" - attachment id
        "date" - date the messages was received
    """
    if str(query).find('has:attachment') < 0:
        query = query + ' has:attachment'
    
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

def find_messages(service, query):
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


def extract_attachment(service, msg, message_id):
    # https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message
    results_list = []
    snippet = msg.get('snippet', "")
    for header in msg['payload']['headers']:
        if header['name'] == 'Date':
            msg_date = header['value']
    payload = msg['payload']
    if 'parts' in payload:
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


def extract_sms(service, msg, message_id):
    # https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message

    result = {}
    result['snip'] = msg.get('snippet', "")
    result['id'] = message_id
    for header in msg['payload']['headers']:
        if header['name'] == 'Date':
            result['date'] = header['value']
        if header['name'] == 'From':
            result['from'] = header['value']
        if header['name'] == 'To':
            result['to'] = header['value']
        if header['name'] == 'X-smssync-address':
            result['addr'] = header['value']
        if header['name'] == 'X-smssync-thread':
            result['thread'] = header['value']
    return [result]


def _get_messages(service, query, msg_extractor, max_results, cursor=None):
    results_list = []
    message_list = service.users().messages().list(userId='me', pageToken=cursor, q=query, maxResults=max_results).execute()
    messages = message_list.get('messages', [])
    pageToken = message_list.get('nextPageToken', None)

    if messages:
        for m in messages:
            message_id = m['id']
            msg = service.users().messages().get(userId='me', id=message_id).execute()
            results = msg_extractor(service, msg, message_id)
            results_list = results_list + results
    return results_list, pageToken    

def sms_messages_iterator(service, query, max_page):
    """ 
    """
    messages, cursor = _get_messages(service, query, max_results=max_page, msg_extractor=extract_sms)
    yield messages
    
    while cursor:
        messages, cursor = _get_messages(service, query, msg_extractor=extract_sms, max_results=max_page, cursor=cursor)
        yield messages


def download_attachment(service, attachment_id, message_id, filename):
    """ download_attachment will use the gmail service to download the attachment identified by attachment_id
    from the message identified by message_id, and will store the result in a local file
    """

    attachment = service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
    data_base64urlencoded = attachment['data']
    file_data = base64.urlsafe_b64decode(data_base64urlencoded.encode('UTF-8'))

    with open(filename, 'wb') as f:
        f.write(file_data)

def clean_filename(filename):
    """ takes a filename and removes all chars that are not appropriate for filenames
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    clean_filename = ''.join(c for c in filename if c in valid_chars)
    return clean_filename

def download_attachments_from_message_list(service, message_list, save_in_folder='.'):
    """ uses the gamail API to download all the attachments from the list of messages
    and writes the files to the named folder
    message_list is a list of objects with attributes:
        "message_id" - id of the message containing the attachment
        "attachment_id" - id of the attachment
        "filename" - the name of the file to store the attachment to, relative to save_in_folder
    """
    for msg in message_list:
        filename = clean_filename(msg['filename'])
        message_id = msg["message_id"]
        attachment_id = msg["attachment_id"]
        path = f"{save_in_folder}/{filename}"
        if not os.path.isfile(path):
            download_attachment(service, attachment_id, message_id, path)
            print(f'saved: {filename}')
        else:
            print(f'.')


if __name__ == '__main__':
    pass
