# gmail
Simple utilities that use the Google GMail API to programmatically search and extract info from email messages
* gm_utils.py - misc utility methods for interacting with google gmail service
* download_message_attachments.py - find and download message attachments
* collect_list_of_attachments.py - finds messages that have attachments and store the attachment filename & date-time of messages into a local csv file 
* driver.py - iterates over months and for each month downloads & saves the sms messages that were backed up to gmail from a mobile device

## Example of using the utilties to collect sms messages
### Two scripts used:

1. sms_loader.py
This script will connect to Gmail and download all messages labeled with "SMS" from my inbox between some start date & end date, currently hardcoded in the script.
It pulls down messages in chunks of months, and stores the results as separate json files in a sub-folder named 'sms'.
It only pulls down a snippet of the message, but it includes date & time as well as who sent & who received the messages. 
The script also pulls down (separately) details on all the email threads.  This is used during post-processing to determine the participants of each email thread.

2. sms_post_proces.py
This script will normalize and enrich messages.
If the message was sent as part of a group text, then all the participants that group are gathered and included in another field on each message.
Time is standardized to a simple local time in YYYYMMDDTHH:MM:SS format.
Duplicate messages are deleted.
At the end, all messages are written out into a single json file named 'all_msgs-final.json'.

