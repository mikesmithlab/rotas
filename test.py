import json
import requests


class Ultrawebhook():    
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']


    def processing(self):
        if self.dict_messages != []:
            message = self.dict_messages
            msg_from = message['from'].split()
            msg_text = message['body'].split()
            print("sender phone number : " + msg_from[0])
            print("message : " + msg_text[0])
            return ''