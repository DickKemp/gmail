import base64
import json
import os.path
from pickle import TRUE
import string

from gm_utils import gmail_service_login, sms_messages_iterator

if __name__ == '__main__':
    query='label:SMS after:2020/5/4 before:2020/6/30'
    service = gmail_service_login(credentials_file='credentials2.json')
    i=0
    for msgs in sms_messages_iterator(service, query, max_page=100):
        message_json = json.dumps(msgs, indent=4)
        with open(f"sms{i}.json", "w") as fd:
            print(message_json, file=fd)
            i = i+1

