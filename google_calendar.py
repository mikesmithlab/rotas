from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pydates.pydates as pyd
from requests import delete

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

calendars =  {
                'AV' : 'a695465f1325cc90025e33c15e94d710a14d13a21d7695944e6c592cb983d1cc@group.calendar.google.com'
            }

def _datetime_from_str(date_str, start_time):
    date = pyd.parse_date(date_str)
    #start_datetime etc are strings
    start_datetime = pyd.relative_datetime(date, delta_hour=start_time).astimezone().isoformat()
    finish_datetime = pyd.relative_datetime(date, delta_hour=start_time + 1).astimezone().isoformat() 
    return start_datetime, finish_datetime

def create_event(date_str : str, start_time : int=10, summary:str=''):
    """Create an empty event which can be passed to an instance of Google Calendar

    Upon initial creation summary is populated with the format specifying roles and 
    how many people are required. This should have the following format:

    Role : ?,? Role2 : ?

    where ? represent a slot to be filled.
    
    The events are dictionaries that can contain many fields but most are not required.
    This creates a minimal event in which the title can contain 
    """
    start_datetime, finish_datetime = _datetime_from_str(date_str, start_time)
        
    event = {
            'summary': summary,
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

def add_name_event(event, name, role):
    """Modifies the summary field of a calendar entry to include the new name
    It firstly finds the portion associated with correct role and then replaces first
    question mark in the string.
    """
    if name in event['summary']:
        print('warning: looks like this name is already booked')
    
    summary = event['summary'].replace(':',':;').split(';')
    for i, part in enumerate(summary):
        if role.lower().replace(' ','') in part.lower():
            if '?' in summary[i+1]:
                summary[i+1] = summary[i+1].replace('?',name,1)
                event['summary'] = ''.join(summary)   
            else:
                print('This is already full')
            return event

def remove_name_event(event, name):
    """Modifies the summary field of a calendar entry to remove a previously booked name
    If the name wasn't previously present it returns False"""
    if name in event['summary']:
        event['summary']=event['summary'].replace(name, '?', 1)
    else:
        event=False
    return event

def print_events(events):
    if not events:
        print('No upcoming events found.')
        return

    # Prints the start time and name of events
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


class Calendar:
    """
    Calendar handles interaction with a Google calendar of specified id.    
    """
    def __init__(self, calendar_id):
        """Authenticate connection using token and establish service
        
        calendar_id :  unique identifier for particular google calendar

        To find id open google calendar. On left find calendar click 3 dots
        and then "settings and sharing". Calendar Id is under "Integrate Calendar"
        """
        
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
        """read_calendar returns all the events on the google calendar up to a max
        of 250 starting from now.
        
        events is a dictionary, see create_event for example contents
        """
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId=self.calendar_id, timeMin=now,
                                              maxResults=250, singleEvents=True,
                                              orderBy='startTime').execute() 
        events = events_result.get('items', [])
        return events

    def add_event(self, event):
        """Book event will either create a new event with details given by the dictionary event or
        update an existing event with the new details"""
        if not self._event_exists(event):
            self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        else:
            print('event already exists')
    
    def edit_event(self, event):
        "Update a pre-existing event with new information"
        event_id = self._event_exists(event)
        if event_id:
            self.service.events().update(calendarId=self.calendar_id, body=event, eventId=event_id).execute()
        else:
            print('event does not exist')

    def delete_event(self, event):
        """Delete an event from the calendar"""
        event_id = self._event_exists(event)
        if event_id:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
        else:
            print('event does not exist')

    def get_event(self, date_str, start_time=10):
        """Takes date and time and searches calendar for a matching event. Then returns the associated dictionary"""
        datetime_event = create_event(date_str, start_time=start_time)
        event_id = self._event_exists(datetime_event)
        if event_id:
            for event in self.read_calendar():
                if event['id'] == event_id:
                    return event
        else:
            return False

    def _event_exists(self, new_event):
        """Internal method to check if an event with specified date and time already exists on google calendar
        If it does return event_id. If not return False"""
        calendar_events = self.read_calendar()
        for calendar_event in calendar_events:
            calendar_day_hour = calendar_event['start']['dateTime'][:13]
            new_day_hour = new_event['start']['dateTime'][:13]
            if calendar_day_hour == new_day_hour:
                return calendar_event['id']
        return False





if __name__ == '__main__':
    #Create a connection to the calendar
    av = Calendar(calendars['AV'])
    #Create a dictionary with placeholders 
    event=create_event('21/3/23', start_time=10, summary='AV : ? , ?')
    #Add this event to the calendar
    av.add_event(event)
    #Find an event on the calendar for a given time and date
    event = av.get_event('21/3/23', start_time=10)
    #Modify the event dictionary to add a name to a slot
    event=add_name_event(event, 'booboo Smith', 'AV')
    event=add_name_event(event, 'Lisa Smith', 'AV')
    #Modify the google calendar
    av.edit_event(event)
    #Remove someone from a slot
    event = av.get_event('21/3/23', start_time=10)
    remove_name_event(event, 'Lisa Smith')
    av.edit_event(event)
    #Delete an event
    #event = av.get_event('21/3/23', start_time=10)
    #av.delete_event(event)

