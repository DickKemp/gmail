import base64
import json
import os.path
import string

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from gm_utils import gmail_service_login, download_attachments_from_message_list, find_messages_that_have_attachments

if __name__ == '__main__':
    query='in:inbox after:2020/6/20 before:2020/12/31'
    query='in:inbox from:(myawdoszyn@yahoo.com) after:2014/5/1'

    service = gmail_service_login()
    message_list = find_messages_that_have_attachments(service, query)
    download_attachments_from_message_list(service, message_list, 'photos')
