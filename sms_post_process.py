import os
import json
import collections
from identity import ME
from datetime import datetime

SNIP="snip"
ID="id"
FROM="from"
TO="to"
ADDR="addr"
DAY="dateday"
DATE="date"
TIME="datetime"
THREAD="thread"
SUBJECT="subject"
THREAD_GRP="thread_grp"

def load_json_files(folder):
    items_list = []
    for f in os.listdir(folder):
        with open(f'{folder}/{f}', 'r') as fd:
            items = json.load(fd)
            items_list.extend(items)
    return items_list

def standardize_datetime(dt_str):
    """ returns an iso 1806 standardized and localized version of the date time, transforming the 
    input date time string that looks like this:
        "Sat, 27 Feb 2010 16:40:39 -0500"
    into this representatin of local time:
        "20100227T16:40:39"
    
    a simplifying assumption applied to all times is that any time is represented as my local
    time as the event occurs, regardless of my location.
    the consequence of this is that in theory I can perform events A and B in chronological sequence,
    but it is possible for B to have an earlier time than A if I happen to change time zones between
    those two events.
    I accept these consequences in the interest of simplification and given one's natural
    intuition of "time" - "time *is* what the clock on the wall says it is right now"
    """
    std_dt = datetime.strptime(dt_str, "%a, %d %b %Y %X %z")
    std_date_str = datetime.strftime(std_dt, "%Y%m%dT%X")
    std_datetime_str = datetime.strftime(std_dt, "%Y-%m-%dT%XZ")
    std_dateday_str = datetime.strftime(std_dt, "%Y-%m-%d")
    return std_date_str, std_datetime_str, std_dateday_str

if __name__ == '__main__':
    # sms: the full list of messages with raw attribute
    sms = load_json_files('sms')
    # threads: the full list of threads, each thread is described by thread_id and a list of msg_ids
    threads = load_json_files('threads')

    print(f'length of messages list before processing: {len(sms)}')
    # persist the full set of sms messages just so we can compare
    # what we started with to what we ended with
    with open("all_msgs-initial.json", "w") as fd:
        print(json.dumps(sms, indent=4), file=fd)


    with open("all_threads.json", "w") as fd:
        print(json.dumps(threads, indent=4), file=fd)

    # messages: maps msg_id to the message 
    # at time same time, format the datetime to a simpler standard local time
    messages = dict()
    for msg in sms:
        msg[DATE], msg[TIME], msg[DAY] = standardize_datetime(msg[DATE])
        messages[msg[ID]] = msg

    # time_to_msgs: maps msg time to the set of msg_ids that were delivered at that time
    time_to_msgs = dict()
    for msg in sms:
        msg_set = time_to_msgs.get(msg[DATE], set())
        msg_set.add(msg[ID])
        time_to_msgs[msg[DATE]] = msg_set

    # look across each thread; at the end of each loop, we want each message that is part of
    # that thread group to have a new attribute called thread_grp.  the thread_grp attribute
    # will hold the list of users that were part of that thread
    # this will allow me to ask the question:  find me the times of messages that some user
    # is a part of (by virtue of tha user being part of the thread of that messages)
    # the user <me> is specifically removed from the list as that user 
    # is part of every message anyway
    for th in threads:
        msg_grp = set()
        for m in th["message_ids"]:
            if m in messages:
                msg = messages[m]
                for elist in [msg[FROM], msg[TO]]:
                    for email in [str.strip(str.lower(w)) for w in elist.split(',')]:
                        if email != ME:
                            msg_grp.add(email)
        for m in th["message_ids"]:
            if m in messages:
                msg = messages[m]
                msg[THREAD_GRP] = list(msg_grp)

    # here we use the time_to_msgs map to find when two messages have the exact same time
    # if the messages have the same time I delete the ones that have the smallest thread-grp
    # this eliminates redundant messages from within the data when a single messages is 
    # duplicated (with different msg_ids) but somehow the thread-groups between the messages 
    # are different
    # we also verify that the message identified for deletion also has the same snippet as the one
    # not being deleted
    # at the end of this block, we have a list of msg_ids that can be deleted because they are redundant
    to_delete = list()
    for t,m in time_to_msgs.items():
        if len(m) > 1:
            m2 = [x for x in m if x in messages]
            msg_w_biggest_group = min(list(m2), key=lambda x: len(messages[x][THREAD_GRP]))
            for w in m:
                if w != msg_w_biggest_group and messages[msg_w_biggest_group][SNIP] == messages[w][SNIP]:
                    to_delete.append(w)
    
    # delete the duplicate messages
    for mid in to_delete:
        del messages[mid]

    # update the master sms list to make sure it only contains valid messages 
    # (i.e. it doesn't still hold any of those duplicate messages)
    new_sms = list()
    for m in sms:
        if m[ID] in messages:
            new_sms.append(messages[m[ID]])
    sms = new_sms
    # finally, sort the messages in sms based on the time    
    sms.sort(key=lambda msg: msg[TIME])

    # print the distrubtion of thread-group sizes
    sizes = collections.Counter()
    for msg in sms:
        size = len(msg[THREAD_GRP])
        sizes += collections.Counter([size])
    print(f'thread group size distribution: {str(sizes)}')

    print(f'length of messages list after processing: {len(sms)}')
    # write the full list of updated messages to disk
    with open("all_msgs-final.json", "w") as fd:
        print(json.dumps(sms, indent=4), file=fd)

