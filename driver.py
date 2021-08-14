import json
from gm_utils import gmail_service_login, sms_messages_iterator

def month_generator(start_year, end_year):
    for year in range(start_year, end_year):
        for month in range(1,13):
            yield f"{year}/{month:02d}/01"
    
def retrieve_messages_to_file(from_month, to_month, filename, folder='sms'):
    query=f'label:SMS after:{from_month} before:{to_month}'
    service = gmail_service_login(credentials_file='credentials2.json')
    i=1
    for msgs in sms_messages_iterator(service, query, max_page=100):
        message_json = json.dumps(msgs, indent=4)
        with open(f"{folder}/{filename}-{i}.json", "w") as fd:
            print(message_json, file=fd)
            i += 1

if __name__ == '__main__':
    # first txt msg in my inbox is on Feb 3 2010 when I got the new erris android
    # so I want to generate date pairs from then till now in reasonable increments
    # perhaps every month from Jan 2010 till now
    #
    from_month = '2009/12/01'
    for to_month in month_generator(2010, 2022):
        print(f"{from_month} -> {to_month}")
        filename = f"{from_month.replace('/','')}-{to_month.replace('/','')}"
        retrieve_messages_to_file(from_month, to_month, filename, 'sms2')
        from_month = to_month

