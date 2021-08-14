import json
from datetime import date, timedelta, datetime
from dateutil import relativedelta
from gm_utils import gmail_service_login, sms_messages_iterator, sms_thread_iterator

def date_period_generator(start_date, end_date, period='day'):
    """supplies a generator of dates that advance based on the period

    Args:
        start_date (str): format is YYYY/MM/DD
        end_date (str): format is YYYY/MM/DD
        period (str): 'day', 'month', 'year'

    Yields:
        str: the next date
    """
    if period == 'month':
        delta = relativedelta.relativedelta(months=+1)
    elif period == 'year':
        delta = relativedelta.relativedelta(years=+1)
    else:
        delta = relativedelta.relativedelta(days=+1)

    start_dt = datetime.strptime(start_date, "%Y/%m/%d")
    end_dt = datetime.strptime(end_date, "%Y/%m/%d")
    while (start_dt < end_dt):
        yield datetime.strftime(start_dt, "%Y/%m/%d")
        start_dt = start_dt + delta

def retrieve_messages_to_file(from_date, to_date, filename, folder='sms'):
    query=f'label:SMS after:{from_date} before:{to_date}'
    service = gmail_service_login(credentials_file='credentials2.json')
    i=1
    for msgs in sms_messages_iterator(service, query, max_page=100):
        message_json = json.dumps(msgs, indent=4)
        with open(f"{folder}/{filename}-{i}.json", "w") as fd:
            print(message_json, file=fd)
            i += 1

def retrieve_threads_to_file(from_date, to_date, filename, folder='threads'):
    query=f'label:SMS after:{from_date} before:{to_date}'
    service = gmail_service_login(credentials_file='credentials2.json')
    i=1
    for threads in sms_thread_iterator(service, query, max_page=100):
        thread_json = json.dumps(threads, indent=4)
        with open(f"{folder}/{filename}-{i}.json", "w") as fd:
            print(thread_json, file=fd)
            i += 1

if __name__ == '__main__':
    # first txt msg in my inbox is on Feb 3 2010 when I got the new erris android
    # so I want to generate date pairs from then till now in reasonable increments
    # perhaps every month from Jan 2010 till now
    #
    first = True
    for next_month in date_period_generator(start_date='2010/02/01', end_date='2021/10/01', period='month'):
        if first:
            to_month = next_month
            first = False
        else:
            from_month = to_month
            to_month = next_month
            print(f"{from_month} -> {to_month}")
            filename = f"{from_month.replace('/','')}-{to_month.replace('/','')}"
            retrieve_messages_to_file(from_month, to_month, filename, 'sms')
            retrieve_threads_to_file(from_month, to_month, filename, 'threads')
