import socket
import keyboard
import sys
import json
import requests
from datetime import datetime, date, time
from dateutil import parser
from conf import *
from utils import *


commands_file = open('commands.txt', 'r')
commands = json.loads(commands_file.read())
commands_file.close()

cmd_timeouts = []
for cmd in commands:
    cmd_timeouts.append({'command_name' : cmd, 'last_used' : datetime.utcnow().isoformat()})
#cmd_timeouts.append({'command_name' : '!followtime', 'last_used' : datetime.utcnow().isoformat()})
#cmd_timeouts.append({'command_name' : '!uptime', 'last_used' : datetime.utcnow().isoformat()})
print(cmd_timeouts)

print(commands)
ops_file = open('ops.txt', 'r')
ops = json.loads(ops_file.read())
ops_file.close()
print(ops)
s = socket.socket()
s.connect((HOST, PORT))
s.send(bytes("PASS {}\r\n".format(PASS), 'utf-8'))
s.send(bytes("NICK {}\r\n".format(NICK), 'utf-8'))
s.send(bytes("JOIN {}\r\n".format(CHAN), 'utf-8'))

controller = True


while controller:
    commands_file = open('commands.txt', 'r')
    commands = json.loads(commands_file.read())
    commands_file.close()

    resp = s.recv(1024).decode('utf-8')
    if resp == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
    else:
        
        ## ==========Variables============ ###
        
        username = re.search(r'\w+', resp)
        if username != None:
            username = username.group(0)
        ### ============================== ###

        msg = get_message(resp)
        print(msg)
        command = commands.get(msg)
        print(command)

        if msg:
            for op in ops:
                if op == username:
                    sp_cmd = re.compile(r'^!!\w+ ')
                    cmmd = sp_cmd.search(msg)
                    if cmmd:
                        cmd = cmmd.group(0).strip()
                        if cmd == '!!add':
                            try:
                                print('add')
                                args = sp_cmd.sub('', msg)
                                cmd_name = re.search(r'!\w+', args).group(0)
                                args = re.sub(r'!\w+', '', args).strip()

                                args_timeout = int(re.search(r'\d+ ', args).group(0))
                                args = re.sub(r'\d+ ', '', args).strip()
                                
                                cmd_text = args.strip()
                                with open('commands.txt', 'r+') as cmd_file:
                                    cmd_dict = json.loads(cmd_file.read())
                                    print(cmd_dict)
                                    cmd_dict.update({cmd_name:{'text':cmd_text, 'timeout':args_timeout}})
                                    cmd_file.seek(0)
                                    cmd_file.write(json.dumps(cmd_dict))
                                    cmd_file.truncate()

                            except:
                                print('gg')

                        elif cmd == '!!edit':
                            try:
                                args = sp_cmd.sub('', msg)
                                cmd_name = re.search(r'!\w+', args).group(0)
                                args = re.sub(r'!\w+', '', args).strip()

                                args_timeout = int(re.search(r'\d+ ', args).group(0))
                                args = re.sub(r'\d+ ', '', args).strip()
                                
                                cmd_text = args
                                for comm in commands:
                                    if comm == cmd_name:
                                        with open('commands.txt', 'r+') as cmd_file:
                                            cmd_dict = json.loads(cmd_file.read())
                                            print(cmd_dict)
                                            cmd_dict.update({cmd_name:{'text':cmd_text, 'timeout':args_timeout}})
                                            cmd_file.seek(0)
                                            cmd_file.write(json.dumps(cmd_dict))
                                            cmd_file.truncate()
                                    else:
                                        send_to_chat(s, 'There is no "{}" command'.format(cmd_name))
                            except:
                                print('gg')
                        elif cmd == '!!refresh':
                            print('refresh')
                            with open('commands.txt', 'r') as commands_file:
                                commands = json.loads(commands_file.read())
                                send_to_chat(s, "Succsessfully refreshed bot's commands")
                        elif cmd == '!!delete':
                            try:
                                args = sp_cmd.sub('', msg)
                                args = args.strip()
                                with open('commands.txt', 'r+') as cmd_file:
                                    cmd_dict = json.loads(cmd_file.read())
                                    print(cmd_dict)
                                    del cmd_dict[args]
                                    cmd_file.seek(0)
                                    cmd_file.write(json.dumps(cmd_dict))
                                    cmd_file.truncate()
                                    send_to_chat(s, 'Succsessfully deleted "{}" command'.format(args))

                            except KeyError:
                                send_to_chat(s, 'There is no such command')

        if command != None:
            pttrn = r'<\w+>'
            txt_to_chat = re.findall(pttrn, command['text'])
            cmd_anwser = ''
            if txt_to_chat != []:
                print('Worked for {}'.format(command['text']))
                for i in range(len(txt_to_chat)):
                    try:
                        var = re.search(r'\w+', txt_to_chat[i]).group(0)
                        var_including = eval(var)
                        cmd_anwser = command['text'].replace(txt_to_chat[i], var_including)
                    except NameError:
                        print('There is no such var called: ')
            else:
                cmd_anwser = command['text']
                print('else txt: {}'.format(cmd_anwser))
            print('A is {}'.format(cmd_anwser))
            dt_now = datetime.utcnow().isoformat()
            dt_now = parser.parse(dt_now)

            cmd_timeout = {}
            i_of_timeout = 0

            for i in range(len(cmd_timeouts)):
                if cmd_timeouts[i]['command_name'] == msg:
                    i_of_timeout = i
                    cmd_timeout = cmd_timeouts[i]
                    print(cmd_timeouts[i]['command_name'])

            tmout = parser.parse(cmd_timeout['last_used'])

            fg = dt_now - tmout
            fg = fg.days * 86400 + fg.seconds
            print('Seconds: {}'.format(fg))
            if fg > command['timeout']:
                cmd_timeouts[i_of_timeout]['last_used'] = datetime.utcnow().isoformat()
                print('Ready to use')
                send_to_chat(s, cmd_anwser)

        elif msg == '!quit':
            for op in ops:
                if op == username:
                    send_to_chat(s, 'Shutting down the bot...')
                    s.send('PART #{}\r\n'.format(CHAN).encode('utf-8'))
                    s.send('QUIT {}\r\n'.format(CHAN).encode('utf-8'))
                    sys.exit()
        elif msg == '!commands':
            chat_answer = ''
            for key in commands:
                chat_answer += '{}, '.format(key)
            send_to_chat(s, 'Commands: {}'.format(chat_answer))
        elif msg == '!followtime':
            h = {'Client-ID' : 'z642unnkhry1z1cn6cqpacg5dk9h3z'}
            p= {'login':username}
            r = requests.get('https://api.twitch.tv/helix/users', params = p, headers = h)
            userInfo = json.loads(r.text)
            userInfo = userInfo['data'][0]
            p = {'from_id':userInfo['id']}
            r = requests.get('https://api.twitch.tv/helix/users/follows', headers = h, params = p)
            userFollows = json.loads(r.text)

            dt_now = datetime.utcnow().isoformat()
            dt_now = parser.parse(dt_now)

            cmd_timeout = {}
            i_of_timeout = 0

            for i in range(len(cmd_timeouts)):
                if cmd_timeouts[i]['command_name'] == msg:
                    i_of_timeout = i
                    cmd_timeout = cmd_timeouts[i]
                    print(cmd_timeouts[i]['command_name'])

            tmout = parser.parse(cmd_timeout['last_used'])

            fg = dt_now - tmout
            fg = fg.days * 86400 + fg.seconds
            print('Seconds: {}'.format(fg))
            if fg > 15:
                cmd_timeouts[i_of_timeout]['last_used'] = datetime.utcnow().isoformat()
                for follow in userFollows['data']:
                    if follow['to_name'] == 'greedycat_meow':
                        dt = parser.parse(follow['followed_at']).strftime('%Y-%m-%d %H:%M:%S.%f')
                        dt = parser.parse(dt)
                        dati_now = parser.parse(datetime.utcnow().isoformat())
                        follow_time =  dati_now - dt
                        days = follow_time.days
                        seconds = follow_time.seconds
                        hours = seconds // 3600
                        minutes = (seconds % 3600) // 60
                        seconds = seconds - (hours*3600 + minutes*60)
                        send_to_chat(s,'You has been following {0} {1} days {2} hours {3} minutes {4} seconds'.format(follow['to_name'], days, hours, minutes, seconds))
        elif msg == '!uptime':
            h = {'Client-ID' : 'z642unnkhry1z1cn6cqpacg5dk9h3z'}
            p = {'user_login':'greedycat_meow'} #greedycat_meow
            r = requests.get('https://api.twitch.tv/helix/streams', headers = h, params = p)
            stream = json.loads(r.text)
            stream = stream['data'][0]

            dt_now = datetime.utcnow().isoformat()
            dt_now = parser.parse(dt_now)

            cmd_timeout = {}
            i_of_timeout = 0

            for i in range(len(cmd_timeouts)):
                if cmd_timeouts[i]['command_name'] == msg:
                    i_of_timeout = i
                    cmd_timeout = cmd_timeouts[i]
                    print(cmd_timeouts[i]['command_name'])

            tmout = parser.parse(cmd_timeout['last_used'])

            fg = dt_now - tmout
            fg = fg.days * 86400 + fg.seconds
            print('Seconds: {}'.format(fg))
            if fg > 15:
                cmd_timeouts[i_of_timeout]['last_used'] = datetime.utcnow().isoformat()
                started_at = parser.parse(stream['started_at']).strftime('%Y-%m-%d %H:%M:%S.%f')
                started_at = parser.parse(started_at)
                time_now = parser.parse(datetime.utcnow().isoformat())

                uptime = time_now - started_at

                seconds = uptime.seconds
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds - (hours*3600 + minutes*60)
                send_to_chat(s, "Stream live for {0} hours {1} minutes {2} seconds".format(hours, minutes, seconds))


            

    resp = ""



