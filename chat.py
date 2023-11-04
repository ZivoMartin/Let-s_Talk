#!/usr/bin/python3
import socket
import sys
import select
from random import randint

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 7777
s.bind(("", port))
s.listen(1)
clients = {}
id_tab = [None]*10001
id_tab[0] = "Global"
channels = {"Global": {"membres": [], "admin": None, "id": 0}}
running = True
admin = ""
nb_user = 1
wall = "ceciestunwall__||$!/\!$||__ceciestunwall"

while(running):
    sockets = []
    for client in clients.values():
        sockets.append(client["socket"])
    l1, l2, l3 = select.select(sockets + [s], [], [])
    size = len(l1)
    for i in range(size):
        if(l1[i] == s):
            new_s, adr = s.accept()
            clients[f"user{nb_user}"] = {"socket": new_s, "current_channel": ["Global"]}
            channels["Global"]["membres"].append(f"user{nb_user}")
            new_s.sendall(f"CONNECT/|/Système/|/user{nb_user}{wall}".encode())
            new_s.sendall(f"MSG/Global/Système/|/Bienvenue sur le chanel Global, ici tout le monde peut lire vos messages. Tâchez d'étre respéctueux.{wall}".encode())
            nb_user += 1
        else:
            data = l1[i].recv(1500).decode()
            splited_data = data.split("/") 
            cmd = splited_data[0]
            channel = splited_data[1]
            sender = splited_data[2]
            receiver = splited_data[3]
            for j in range(4):
                splited_data.pop(0)
            content = "".join(splited_data)

            if(cmd == "MSG"):
                   
                for client in channels[channel]["membres"]:
                    if(client != sender):
                        clients[client]["socket"].sendall((f"MSG/{channel}/{sender}/|/{content}{wall}").encode())
                    
            elif(cmd == "NICK"):
                if(content in clients.keys()):
                    l1[i].sendall(f"Ce nom est déjà utilisé{wall}".encode())
                else:
                    clients[content] = {"socket": clients[sender]["socket"], "current_channel": clients[sender]["current_channel"]}
                    del clients[sender]
                    for elt in channels.keys():
                        if(sender in channels[elt]["membres"]):
                            channels[elt]["membres"].remove(sender)
                            channels[elt]["membres"].append(content)
                
            elif(cmd == "NAMES"):
                response = ""
                for usr in channels[channel]["membres"]:
                    response += usr + "|"
                l1[i].sendall((response+wall).encode())
                    
            elif(cmd == "BYEBYE"):
                l1[i].close()
                del clients[sender]
                for channel in channels.values():
                    if(sender in channel["membres"]):
                        channel["membres"].remove(sender)
                        for usr in channel["membres"]:
                            clients[usr]["socket"].sendall(f"MSG/{channel}/Système/|/{sender} à désactivé son compte.{wall}".encode())
                
            elif(cmd == "REMOVE"):

                clients[receiver]["socket"].sendall(f"REMOVED/{channel}/{sender}/|/|{wall}".encode())
                clients[receiver]["current_channel"].remove(channel)
                channels[channel]["membres"].remove(receiver)
                for usr in channels[channel]["membres"]:
                    clients[usr]["socket"].sendall((f"MSG/{channel}/système/|/{receiver} a été exclu par {sender}.{wall}").encode())
                            
            elif(cmd == "JOIN"):
                content = int(content)
                if(content < len(id_tab) and id_tab[content] != None and id_tab[content] not in clients[sender]["current_channel"]):
                    for usr in channels[id_tab[content]]["membres"]:
                        clients[usr]["socket"].sendall((f"MSG/{id_tab[content]}/Système/|/{sender} a rejoint le channel, accueilez le comme il se doit.{wall}").encode())
                    l1[i].sendall((f"JOIN/|/Système/|/{id_tab[content]}{wall}").encode())
                    l1[i].sendall((f"MSG/{id_tab[content]}/Système/|/Vous avez rejoins le channel {id_tab[content]} !{wall}").encode())
                    channels[id_tab[content]]["membres"].append(sender)
                    clients[sender]["current_channel"].append(id_tab[content])
            
            elif(cmd == "CREATE"):
                channel_id = randint(1, 10000)
                while(channel_id in id_tab):
                    channel_id = randint(1, 10000)
                id_tab[channel_id] = content
                l1[i].sendall((f"MSG/{content}/Système/|/Vous venez de créer le channel {content}, son mot de passe est {channel_id}, utilisez le pour inviter vos amis.{wall}").encode())
                channels[content] = {"admin": l1[i], "membres": [sender], "id": channel_id}
                clients[sender]["current_channel"].append(content)
            
            elif(cmd == "PART"):
                channels[channel]["membres"].remove(sender)
                clients[sender]["current_channel"].remove(channel)
                for usr in channels[channel]["membres"]:
                    clients[usr]["socket"].sendall((f"MSG/{channel}/système/|/{sender} est parti.{wall}").encode())
            

s.close()


