from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pydates.pydates as pyd

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

calendars =  {
                'AV' : 'a695465f1325cc90025e33c15e94d710a14d13a21d7695944e6c592cb983d1cc@group.calendar.google.com'
            }

def create_event(date_str : str, start_time=10):
    """Create an event which can be passed to an instance of Google Calendar
    
    The events are dictionaries that can contain many fields but most are not required.
    This creates a minimal event in which the title can contain 
    """
    date = pyd.parse_date(date_str)
    start_datetime = pyd.relative_datetime(date, delta_hour=start_time).astimezone().isoformat()
    finish_datetime = pyd.relative_datetime(date, delta_hour=start_time + 1).astimezone().isoformat() 
    print(finish_datetime)
    
    event = {
            'summary': '',
            'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Europe/London'       
                    },
            'end': {
                    'dateTime': finish_datetime,
                    'timeZone': 'Europe/London'
                    },
            }
    
    return event

def add_name_event(event, name):
    """Modifies the summary field of a calendar entry to include the new name"""
    event['summary'] = event['summary'] + name + '\t'
    return event

def remove_name_event(event, name):
    """Modifies the summary field of a calendar entry to remove a previously booked name
    If the name wasn't previously present it returns False"""
    if name in event['summary']:
        event['summary'] = event['summary'].replace(name + '\t', '')
    else:
        event=False
    return event

def print_events(events):
    if not events:
            print('No upcoming events found.')
            return

    # Prints the start and name of the next 10 events
    for event in events:
        print(event)
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


class Calendar:
    def __init__(self, calendar_id):
        self.calendar_id = calendar_id

        if os.path.exists('../calendar_login/token.json'):
            creds = Credentials.from_authorized_user_file('../calendar_login/token.json', SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('../calendar_login/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('../calendar_login/token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def read_calendar(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId=self.calendar_id, timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        
        events = events_result.get('items', [])
        return events

    def book_event(self, event):
        """Book event will either create a new event with details given by the dictionary event or
        update an existing event with the new details"""
        if self._check_event(event):
            self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        else:
            self.service.events().update(calendarId=self.calendar_id, body=event).execute()

    def cancel_event(self):
        pass

    def _check_event(self, new_event):
        """Check if an event with specified date and time already exists on google calendar
        If it does return the details of the event. If not return False"""

        calendar_events = self.read_calendar()
        for calendar_event in calendar_events:
            if calendar_event['start']['dateTime'] == new_event['start']['dateTime']:
                return new_event
            else:
                return False





if __name__ == '__main__':
    av = Calendar(calendars['AV'])
    events = av.read_calendar()
    
    event=create_event('21/3/23')
    event=add_name_event(event, 'booboo Smith')
    print(event)
    av.book_event(event)
    #av.read_calendar()