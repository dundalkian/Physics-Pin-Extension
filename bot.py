import json
import os
import time
import datetime
from configparser import ConfigParser
import re
import sys

from fbchat import Client, log
from fbchat.models import Message, ThreadType

def config(filename=sys.path[0] + '/config.ini', section='facebook credentials'):
    # create a parser 
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section
    creds = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            creds[param[0]] = param[1]
    elif os.environ['EMAIL']: 
        creds['email'] = os.environ['EMAIL']
        creds['password'] = os.environ['PASSWORD']
    else:
        raise Exception(
            'Section {0} not found in the {1} file'.format(section, filename))
    return creds


class Bot(Client):
    #1398444230228776 testing chat
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if message_object.text is not None and (thread_id == '1398444230228776'):
            messageText = message_object.text
            ma = messageText.split() # message array

            if ma[0].lower() == "physics":
                process_message(self, author_id, ma, thread_id, thread_type)
        super(Bot, self).onMessage(author_id=author_id, message_object=message_object, thread_id=thread_id, thread_type=thread_type, **kwargs)

def process_message(self, author_id, ma, thread_id, thread_type):
    if author_id != self.uid:
        print(ma)
        user = self.fetchUserInfo(author_id)[author_id]
        name = user.name
        if ma[1] == "help" and ma[2] == "pin":
            txt = """
Just to add on to what the other guy said: you can do physics pop and shit

TODO: actually write help text
"""
            self.send(Message(text = txt), thread_id=thread_id, thread_type=thread_type)
        elif ma[1] == "pop":
            print(ma)
        elif ma[1] == "get":
            pass
        elif ma[1] == "append":
            print(ma)
        elif ma[1] == "replace":
            pass

def send_message(self, txt, thread_id, thread_type):
    self.send(Message(text=txt), thread_id=thread_id, thread_type=thread_type)

def startupClient(email, password):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    try:
        with open("session.txt", "r") as session:
            session_cookies = json.loads(session.read())
    except FileNotFoundError:
        session_cookies = None

    client = Bot(email, password, user_agent=user_agent)
    with open("session.txt", "w") as session:
        session.write(json.dumps(client.getSession()))
    return client


### Reving up the engines ###
if __name__ == "__main__":
    creds = config()
    client = startupClient(creds['email'], creds['password'])
    client.listen()
