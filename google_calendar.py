from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

calendars =  {
                'AV' : 'a695465f1325cc90025e33c15e94d710a14d13a21d7695944e6c592cb983d1cc@group.calendar.google.com'
            }

def create_event():
    event = {
            'summary': 'Mike Test Event',
            'start': {
                    'dateTime': ,
                    'timeZone': 'America/Los_Angeles',
                    },
            'end': {
                    'dateTime': '2023-03-17T11:00:00-00:00',
                    'timeZone': 'America/Los_Angeles',
                    },
            },
    
    return event

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

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    def book_event(self, event):
        self.service.events().insert(calendarId=self.calendar_id, body=event).execute()

    def edit_event(self, event):
        pass

    def cancel_event(self):
        pass

            
            




if __name__ == '__main__':
    av = Calendar(calendars['AV'])
    av.read_calendar()
    av.book_event(create_event())
    av.read_calendar()