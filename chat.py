#!/usr/bin/python3
import socket
import sys
import select

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 7777
s.bind(("", port))
s.listen(1)
clients = {}
channels = {"Global": {"membres": [], "admin": None}}
running = True
admin = ""
nb_user = 1
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
            nb_user += 1
            print("connected !")
        else:
            data = l1[i].recv(1500).decode()
            if(data != "\n"):
                sender = ""
                for client in clients.keys():
                    if(clients[client]["socket"] == l1[i]):
                        sender = client
                        break       
                splited_data = data.split(" ") 
                cmd = splited_data[0].split("\n")[0]
                splited_data.pop(0)
                channel = ""
                msg = ""
                if(len(splited_data) > 0):
                    channel = splited_data[0].split("\n")[0]
                    splited_data.pop(0)
                    
                if(len(splited_data) > 0):
                    nb_word = len(splited_data)
                    for j in range(nb_word):
                        msg += splited_data[j]+" "
                msg = msg.split("\n")[0]
                if(cmd == "MSG"):
                    if(channel != "" or msg != ""):
                        if(channel not in clients[sender]["current_channel"]):
                            l1[i].sendall((f"Vous n'avez pas encore rejoint le channel {channel} !\n").encode())
                        else:
                            for client in channels[channel]["membres"]:
                                if(clients[client]["socket"] != l1[i]):
                                    clients[client]["socket"].sendall((f"{channel}~ [{sender}] : {msg}\n").encode())
                    elif(channel == ""):
                        l1[i].sendall("Vous devez preciser un channel\n".encode())
                        
                elif(cmd == "NICK"):
                    if(channel == ""):
                        l1[i].sendall("Le nom choisis n'est pas correct.\n".encode())
                    elif(channel in clients.keys()):
                        l1[i].sendall("Ce nom est déjà utilisé\n".encode())
                    else:
                        clients[channel] = {"socket": clients[sender]["socket"], "current_channel": clients[sender]["current_channel"]}
                        del clients[sender]
                        for elt in channels.keys():
                            if(sender in channels[elt]["membres"]):
                                channels[elt]["membres"].remove(sender)
                                channels[elt]["membres"].append(channel)
                    
                elif(cmd == "NAMES"):
                    if(channel not in clients[sender]["current_channel"]):
                        l1[i].sendall((f"Vous n'avez pas encore rejoint le channel {channel} !\n").encode())
                    else:
                        response = "Clients: "
                        for usr in channels[channel]["membres"]:
                            response += usr + " "
                        l1[i].sendall((response+"\n").encode())
                        
                elif(cmd == "BYEBYE"):
                    l1[i].close()
                    del clients[sender]
                    
                elif(cmd == "REMOVE"):
                    if(channel not in clients[sender]["current_channel"]):
                        l1[i].sendall((f"Vous n'avez pas encore rejoint le channel {channel} !\n").encode())
                    elif(len(splited_data) == 0):
                        l1[i].sendall((f"Vous n'avez pas indiqué l'utilisateur à exclure !\n").encode())
                    else:
                        kiked_user = splited_data[0]
                        splited_data.pop(0)
                        msg = ""
                        if(len(splited_data) > 0):
                            nb_word = len(splited_data)
                            for j in range(nb_word):
                                msg += splited_data[j]+" "
                        if(l1[i] == channels[channel]["admin"] and kiked_user in channels[channel]["membres"]):
                            clients[kiked_user]["socket"].sendall(f"Tu as été exclu du channel {channel} (force à toi): {msg}\n".encode())
                            clients[kiked_user]["current_channel"].remove(channel)
                            channels[channel]["membres"].remove(kiked_user)
                        else:
                            if(l1[i] != channels[channel]["admin"]):
                                l1[i].sendall("Tu dois étre l'admin du channel, bon courage pour ton coup d'état.\n".encode())
                            else:
                                l1[i].sendall("Cet utilisateur n'est pas sur ce channel\n".encode())
                                
                elif(cmd == "JOIN"):
                    if(channel in clients[sender]["current_channel"]):
                       l1[i].sendall((f"Vous étes déjà dans ce channel !\n").encode())
                    else:
                        if(channel not in channels.keys()):
                            l1[i].sendall((f"Vous venez de créer le channel {channel} !\n").encode())
                            channels[channel] = {"admin": l1[i], "membres": [sender]}
                            clients[sender]["current_channel"].append(channel)
                        else:
                            for usr in channels[channel]["membres"]:
                                clients[usr]["socket"].sendall((f"{sender} a rejoint le channel {channel} !\n").encode())
                            l1[i].sendall((f"Vous avez rejoins le channel {channel} !\n").encode())
                            channels[channel]["membres"].append(sender)
                            clients[sender]["current_channel"].append(channel)
                           
                
                elif(cmd == "PART"):
                    if(channel not in clients[sender]["current_channel"]):
                        l1[i].sendall((f"Vous n'étes pas sur le channel {channel} !\n").encode())
                    else:
                        l1[i].sendall((f"Vous avez quitté le channel {channel} !\n").encode())
                        channels[channel]["membres"].remove(sender)
                        clients[sender]["current_channel"].remove(channel)
                        for usr in channels[channel]["membres"]:
                            clients[usr]["socket"].sendall((f"{usr} a quitté le channel {channel} : {msg}\n").encode())
                
                else:
                    l1[i].sendall(f"Commande invalide: {cmd}\n".encode())
s.close()


