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
    cur_pin_name = None
    cur_index = None
    cur_input = None
    cur_command = None
    cur_waiting = False
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if author_id == '100041587845629' and self.cur_waiting and message_object.text is not None:
            self.process_bot_response(message_object.text, thread_id, thread_type)
        if message_object.text is not None: #and (thread_id == '2813871368632313'):
            messageText = message_object.text
            ma = messageText.split() # message array

            if ma[0].lower() == "physics":
                self.process_message(author_id, ma, thread_id, thread_type)
        #super(Bot, self).onMessage(author_id=author_id, message_object=message_object, thread_id=thread_id, thread_type=thread_type, **kwargs)

    def process_bot_response(self, msg_text, thread_id, thread_type):
        m = re.match(r'"(?P<content>\s*[\s\S]*)" . \w+ on \w+, \w+ \d+, \d+', msg_text)
        raw = m.group('content')
        content_list = re.split(r'[\n]?\d+\) ', raw)
        print(raw)
        print(content_list)
        content_list = [x for x in content_list if x!='']
        if self.cur_command == 'append':
            content_list.append(' '.join(self.cur_input)+"\n")
        elif self.cur_command == 'pop':
            content_list.pop(self.cur_index-1)
        elif self.cur_command == 'replace':
            content_list[self.cur_index-1] = ' '.join(self.cur_input)
        elif self.cur_command == 'best_guess':
            tmp = [re.split(r'[\n]',x) for x in content_list] 
            content_list = [item for sublist in tmp for item in sublist]
        out_list = []
        for i in range(len(content_list)):
            if i == 0:
                out_list.append(f"{i+1}) ")
            else:
                out_list.append(f"\n{i+1}) ")
            out_list.append(content_list[i])
        out_text = ''.join(out_list)
        time.sleep(2)
        self.send_message(f"physics pin {self.cur_pin_name} {out_text}", thread_id, thread_type)
        self.cur_pin_name = None
        self.cur_index = None
        self.cur_input = None
        self.cur_command = None
        self.cur_waiting = False

        

    def process_message(self, author_id, ma, thread_id, thread_type):
        if author_id != self.uid:
            user = self.fetchUserInfo(author_id)[author_id]
            name = user.name
            if ma[1] == "help" and ma[2] == "pin":
                txt = """
Imma let you finish AØBøt, but just to let you know:
    Add Entries: "physics append {pin_name} {additional entry text}"
    Remove Entries: "physics pop {pin_name} {index to remove}:
    Replace Entries: "physics replace {pin_name} {index to alter} {new text}"
    Attempt to convert into list format: "physics best_guess {pin_name}"
"""
                self.send(Message(text = txt), thread_id=thread_id, thread_type=thread_type)
            elif ma[1] == "pop":
                self.cur_waiting = True
                self.cur_index = int(ma[3])
                self.cur_command = "pop"
                self.cur_pin_name = ma[2]
                self.get_physics_pin(ma[2], thread_id, thread_type)
            elif ma[1] == "best_guess":
                self.cur_waiting = True
                self.cur_command = "best_guess"
                self.cur_pin_name = ma[2]
                self.get_physics_pin(ma[2], thread_id, thread_type)
            elif ma[1] == "append":
                self.cur_waiting = True
                self.cur_input = ma[3:]
                self.cur_command = "append"
                self.cur_pin_name = ma[2]
                self.get_physics_pin(ma[2], thread_id, thread_type)
            elif ma[1] == "replace":
                self.cur_waiting = True
                self.cur_input = ma[4:]
                self.cur_index = int(ma[3])
                self.cur_command = "replace"
                self.cur_pin_name = ma[2]
                self.get_physics_pin(ma[2], thread_id, thread_type)

    def get_physics_pin(self, pin_name, thread_id, thread_type):
        self.send_message(f"physics pin {pin_name}", thread_id, thread_type)


    def send_message(self, txt, thread_id, thread_type):
        self.send(Message(text=txt), thread_id=thread_id, thread_type=thread_type)

def startupClient(email, password):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    try:
        with open("session.txt", "r") as session:
            session_cookies = json.loads(session.read())
    except FileNotFoundError:
        session_cookies = None

    print(session_cookies)
    client = Bot(email, password, session_cookies=session_cookies)
    with open("session.txt", "w") as session:
        session.write(json.dumps(client.getSession()))
    return client


### Reving up the engines ###
if __name__ == "__main__":
    creds = config()
    client = startupClient("sykesstudents@gmail.com", "ThisThingSucks008")
    #client = startupClient(creds['email'], creds['password'])
    client.listen()
