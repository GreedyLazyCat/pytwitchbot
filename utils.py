import re
from conf import *

def send_to_chat(s, msg):
    s.send('PRIVMSG {0} :{1}\r\n'.format(CHAN, msg).encode('utf-8'))

def get_message(resp):
    pattern = r'^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :.*'
    pattern_to_del = r'^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :'
    message = re.search(pattern, resp)
    if message != None:
            message = re.sub(pattern_to_del, '', message.group(0))
            return message.strip()