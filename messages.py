import base64
import json
import os.path
import string

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from gm_utils import gmail_service_login, download_attachment, get_messages_with_attachments

def clean_filename(filename):
    """ takes a filename and removes all chars that are not appropriate for filenames
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    clean_filename = ''.join(c for c in filename if c in valid_chars)
    return clean_filename

def download_attachments_from_list(service, message_list, folder='.'):
    """ uses the gamail API to download all the attachments from the list of messages
    and writes the files to the named folder
    """
    for msg in message_list:
        filename = clean_filename(msg['filename'])
        message_id = msg["message_id"]
        attachment_id = msg["attachment_id"]
        path = f"{folder}/{filename}"
        if not os.path.isfile(path):
            download_attachment(service, attachment_id, message_id, path)
            print(f'saved: {filename}')
        else:
            print(f'{filename} already exists')

if __name__ == '__main__':
    query='in:inbox has:attachment after:2020/6/20 before:2020/12/31'
    service = gmail_service_login()
    message_list = get_messages_with_attachments(service, query)
    download_attachments_from_list(service, message_list, 'tmp')
