import base64
import json
import os.path
import string

from gm_utils import gmail_service_login, download_attachment, get_messages_with_attachments

if __name__ == '__main__':
    # query='in:inbox has:attachment after:2020/6/20 before:2020/12/31'
    query='in:inbox from:(myawdoszyn@yahoo.com) subject:5photo has:attachment after:2014/5/1 before:2020/10/2'
    service = gmail_service_login()
    message_list = get_messages_with_attachments(service, query)
    with open('5photos.csv', "w") as fd:
        for msg in message_list:
            fd.write(f"{msg['filename']}\t{msg['date']}\n")
    


