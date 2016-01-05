from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

import urllib
import httplib2


def get_service(api_name,
                api_version,
                scope,
                key_file_location,
                service_account_email):
    """Get a service that communicates to a Google API.

    Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

    Returns:
    A service that is connected to the specified API.
    """

    f = open(key_file_location, 'rb')
    key = f.read()
    f.close()

    credentials = SignedJwtAssertionCredentials(service_account_email,
                                                key,
                                                scope=scope)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    service = build(api_name, api_version, http=http)

    return service


def get_events(ga_service,
               ga_ids,
               event_category,
               start_date,
               end_date,
               start_index=1,
               max_results=1000):
    return ga_service.get(ids=ga_ids,
                          start_date=start_date,
                          end_date=end_date,
                          metrics='ga:totalEvents',
                          dimensions='ga:eventLabel',
                          filters='ga:eventCategory==%s' % event_category,
                          sort='-ga:totalEvents',
                          max_results=max_results,
                          start_index=start_index).execute()


def get_all_events(ga_ids, event_category, start_date, end_date):
    # Use the developer console and replace the values with your
    # service account email and relative location of your key file.
    service_email = 'dka-report@dr-danskkulturarv.iam.gserviceaccount.com'
    key_file_location = 'service-account-key.p12'
    # Define the auth scopes to request.
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    # Authenticate and construct service.
    ga_service = get_service('analytics',
                             'v3',
                             scope,
                             key_file_location,
                             service_email).data().ga()
    MAX_RESULTS = 1000
    start_index = 1

    # Let's first assume that there is more results than we ask for.
    total_results = MAX_RESULTS+1
    events = {}
    while start_index <= total_results:
        result = get_events(ga_service,
                            ga_ids,
                            event_category,
                            start_date,
                            end_date,
                            start_index=start_index,
                            max_results=MAX_RESULTS)
        start_index += MAX_RESULTS
        total_results = result.get('totalResults')
        for url, count in result.get('rows'):
            url = urllib.unquote(url)
            events[url] = int(count)

    return events


def main():
    ga_ids = 'ga:51793449'
    start_date = '2015-01-01'
    end_date = '2015-12-31'

    plays = get_all_events(ga_ids,
                           'JW Player Video Plays',
                           start_date,
                           end_date)
    print(plays)

    completes = get_all_events(ga_ids,
                               'JW Player Video Completes',
                               start_date,
                               end_date)
    print(completes)

if __name__ == '__main__':
    main()
