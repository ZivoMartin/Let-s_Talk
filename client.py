#!/usr/bin/python3
import socket
import tkinter as tk
import threading



def listen():
    global data
    while True:
        recu = s.recv(1024).decode()
        split_recu = recu.split(wall)
        nb_request = len(split_recu)
        for i in range(nb_request-1):
            data.append(split_recu[i])


def start_thread():
    thread = threading.Thread(target=listen)
    thread.start()

def event_gestion(): 
    global data  
    global name 
    for request in data:
        splited_data = request.split("/")
        data_type = splited_data[0]
        channel = splited_data[1]
        sender = splited_data[2]
        receiver = splited_data[3]
        for i in range(4):
            splited_data.pop(0)
        content = "".join(splited_data)
        if(data_type == "MSG"):
            new_message(content, channel, sender) 
        elif(data_type == "CONNECT"):
            name = content
        elif(data_type == "JOIN"):
            config_a_channel_button(content, False)
            switch_window(frames["join_frame"], frames["main_frame"])
        elif(data_type == "NAMES"):
            display_membres(channel, content.split("|"))
        elif(data_type == "NEW_USER"):
            new_user(content)
        elif(data_type == "USER_LIST"):
            init_user_list(content.split("|"))
        elif(data_type == "NICK"):
            change_a_nickname_user(sender, content)
        elif(data_type == "ADD"):
            if(channel == current_channel):
                users[content]["button"].pack(side="top")
        elif(data_type == "DELETE"):
            if(channel == current_channel):
                users[content]["button"].pack_forget()
        elif(data_type == "REMOVED"):
            channels[channel]["button"].pack_forget()
            del channels[channel]
            if(current_frame == frames["channel_frame"] and current_channel == channel):
                switch_window(frames["channel_frame"], frames["main_frame"])

    data = []
    window.after(1, event_gestion)

def config_window():
    window.geometry(f"{width}x{height}")
    window.title("Let's Talk")
    window.config(bg="dark blue")
    window.protocol("WM_DELETE_WINDOW", close_window)

    config_a_channel_button("Global", False)
    frames["main_left_zone_frame"].pack(side="left", fill="y")
    frames["main_rename_zone_frame"].pack(side="bottom", fill="y")
    frames["main_down_zone_frame"].pack(side="bottom")

    new_channel_button.pack(side="left")
    join_channel_button.pack(side="left")
    frames["main_frame"].pack(expand=True, fill="both", side="top")
   
    main_rename_label.pack(side="left")
    main_rename_entry.pack(side="left")
    main_rename_button.pack(side="left")

    create_channel_input.pack(side="top")
    back_button_create.pack(side="top")

    join_channel_input.pack(side="top")
    back_button_join.pack(side="top")

    send_message_input.pack(side="bottom")
    back_button_channel.pack(side="top")
    leave_channel_button.pack(side="top", pady= (0, 20))
    current_label_conv.pack(side="top")
    frames["channel_left_zone_frame"].pack(side="left", fill="y")
    frames["channel_right_zone_frame"].pack(side="right", fill="y")
    
    user_name_on_profil.pack(side="top")
    send_private_message_button.pack(side="top")
    back_button_profil.pack(side="top")
    

def display_membres(channel, membres):
    channels[channel]["membres"] = membres
    for usr in users.keys():
        if(usr in membres):
            users[usr]["button"].pack(side="top", pady=10)
        else:
            users[usr]["button"].pack_forget()

def new_user(user_name):
    users[user_name] = {"button": tk.Button(frames["channel_right_zone_frame"], text=user_name, bg="blue", fg="white", command=lambda u=user_name: go_on_profile(u))}

def init_user_list(user_list):
    for user_name in user_list:
        if(user_name != ""):
            users[user_name] = {"button": tk.Label(frames["channel_right_zone_frame"], text=user_name, bg="blue", fg="white")}

def change_a_nickname_user(previous, new):
    users[previous]["button"].pack_forget()
    del users[previous]
    new_user(new)
    for channel in channels.keys():
        if(previous in channels[channel]["membres"]):
            channels[channel]["membres"].remove(previous)
            channels[channel]["membres"].append(new)

    
def config_a_channel_button(channel, admin):
    channels[channel] = {"button": tk.Button(frames["main_frame"]), "messages": [], "membres": [name], "admin": admin}
    channels[channel]["button"].config(text=channel, bg="black", height=2, fg="white", command=lambda c=channel: go_on_a_channel(c))
    frames["main_left_zone_frame"].pack_forget()
    frames["main_down_zone_frame"].pack_forget()
    channels[channel]["button"].pack(side="top", fill="x")
    frames["main_left_zone_frame"].pack(side="left", fill="y")
    frames["main_down_zone_frame"].pack(side="bottom")

def go_on_a_channel(c):
    global current_channel
    switch_window(frames["main_frame"], frames["channel_frame"])
    current_channel = c
    txt = ""
    for message in channels[c]["messages"]:
        txt += message
    current_label_conv.config(text=txt)
    s.sendall(f"NAMES/{c}/{name}/|/|".encode())


def go_on_profile(user_name):
    user_name_on_profil.config(text=user_name)
    send_private_message_button.config(command=lambda u=user_name: go_on_private_conv(u))
    if(channels[current_channel]["admin"]):
        remove_from_current_channel_button.config(text=f"Remove {user_name} from {current_channel}", command=lambda c=current_channel, u=user_name: remove(c, u))
        remove_from_current_channel_button.pack(side="top")
    else:
        remove_from_current_channel_button.pack_forget()
    switch_window(frames["channel_frame"], frames["profil_frame"])

def switch_window(previous_frame, new_frame):
    global current_frame
    previous_frame.pack_forget()
    new_frame.pack(expand=True, fill="both", side="top")
    current_frame = new_frame


def remove(channel, user_name):
    s.sendall(f"REMOVE/{channel}/{name}/{user_name}/|".encode())


def create_new_channel(event):
    new_channel = create_channel_input.get()
    create_channel_input.delete(0, 'end')
    config_a_channel_button(new_channel, True)
    s.sendall(f"CREATE/|/{name}/|/{new_channel}".encode())
    switch_window(frames["create_frame"], frames["main_frame"])
    
def join_new_channel(event):
    code = join_channel_input.get()
    join_channel_input.delete(0, 'end')
    correct = True
    chiffres = "1234567890"
    for elt in code:
        if(elt not in chiffres):
            correct = False
            break
    if(correct):
        s.sendall(f"JOIN/|/{name}/|/{code}".encode())
    

def send_message(event):
    msg = send_message_input.get()
    if(msg != ""):
        send_message_input.delete(0, 'end')
        new_message(msg, current_channel, name)
        s.sendall(f"MSG/{current_channel}/{name}/|/{msg}".encode())

def go_on_private_conv(user_name):
    if(user_name not in channels):
        create_new_channel(user_name)
    go_on_a_channel(user_name)

def new_message(msg, channel, user):
    channels[channel]["messages"].append(f"[{user}]: {msg}\n")
    if(channel == current_channel):
        txt = ""
        for message in channels[current_channel]["messages"]:
            txt += message
        current_label_conv.config(text=txt)

def close_window():
    s.sendall(f"BYEBYE/|/{name}/|/|".encode())
    window.destroy()

def new_name(event):
    global name
    new_name = main_rename_entry.get()
    if(new_name != "" and "|" not in new_name):
        main_rename_entry.delete(0, "end")
        s.sendall(f"NICK/|/{name}/|/{new_name}".encode())
        name = new_name

def leave_current_channel():
    channels[current_channel]["button"].pack_forget()
    del channels[current_channel]
    s.sendall(f"PART/{current_channel}/{name}/|/|".encode())
    switch_window(frames["channel_frame"], frames["main_frame"])


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 7777
name = ""
wall = "ceciestunwall__||$!/\!$||__ceciestunwall"
s.connect((host, port)) 
data = []
users = {}
window = tk.Tk()
width, height = 1500, 800
channels = {}
current_channel = None

frames = {
    "main_frame":tk.Frame(window, bg="dark blue"), 
    "create_frame": tk.Frame(window, bg="dark blue"),
    "channel_frame":  tk.Frame(window, bg="dark blue"),
    "join_frame":  tk.Frame(window, bg="dark blue"),
    "profil_frame": tk.Frame(window, bg="dark blue")
}
frames["main_down_zone_frame"] = tk.Frame(frames["main_frame"], bg="dark blue")
frames["channel_left_zone_frame"] = tk.Frame(frames["channel_frame"], bg="dark blue")
frames["channel_right_zone_frame"] = tk.Frame(frames["channel_frame"], bg="dark blue")
frames["main_left_zone_frame"] = tk.Frame(frames["main_frame"], bg="dark blue")
frames["main_rename_zone_frame"] = tk.Frame(frames["main_left_zone_frame"], bg="dark blue")

current_frame = frames["main_frame"]

back_button_create = tk.Button(frames["create_frame"], text="Back", bg="blue", fg="white", command=lambda: switch_window(frames["create_frame"], frames["main_frame"]))
back_button_join = tk.Button(frames["join_frame"], text="Back", bg="blue", fg="white", command=lambda: switch_window(frames["join_frame"], frames["main_frame"]))
back_button_channel = tk.Button(frames["channel_right_zone_frame"], text="Back", bg="blue", fg="white", command=lambda: switch_window(frames["channel_frame"], frames["main_frame"]))
back_button_profil = tk.Button(frames["profil_frame"], text="Back", bg="blue", fg="white", command=lambda: switch_window(frames["profil_frame"], frames["channel_frame"]))

new_channel_button = tk.Button(frames["main_down_zone_frame"], text="Create a new channel ?", bg="blue", fg="white", command=lambda: switch_window(frames["main_frame"], frames["create_frame"]))
join_channel_button = tk.Button(frames["main_down_zone_frame"], text="Join a new channel ?", bg="blue", fg="white", command=lambda: switch_window(frames["main_frame"], frames["join_frame"]))

create_channel_input = tk.Entry(frames["create_frame"], bg="blue", fg="white", font=("Helvetica", 25))
create_channel_input.bind("<Return>", lambda e:create_new_channel(e))

join_channel_input = tk.Entry(frames["join_frame"], bg="blue", fg="white", font=("Helvetica", 25))
join_channel_input.bind("<Return>", lambda e:join_new_channel(e))

current_label_conv = tk.Label(frames["channel_left_zone_frame"], bg="dark blue", fg="white", justify="left")

send_message_input = tk.Entry(frames["channel_frame"], bg="blue", fg="white", width=width)
send_message_input.bind("<Return>", lambda e:send_message(e))
leave_channel_button = tk.Button(frames["channel_right_zone_frame"], text="Leave", command=leave_current_channel, bg="blue", fg="white")

main_rename_label = tk.Label(frames["main_rename_zone_frame"], text="Rennomez vous ici:", bg="blue", font=("Helvetica", 15),  fg="white")
main_rename_entry = tk.Entry(frames["main_rename_zone_frame"], bg="blue", font=("Helvetica", 15), fg="white")
main_rename_button = tk.Button(frames["main_rename_zone_frame"], text="ok", bg="blue", font=("Helvetica", 10), command=lambda : new_name(None),  fg="white")
main_rename_entry.bind("<Return>", lambda e:new_name(e))

send_private_message_button = tk.Button(frames["profil_frame"], text="Send a message", bg="blue", fg="white")
remove_from_current_channel_button = tk.Button(frames["profil_frame"], bg="blue", fg="white")
user_name_on_profil = tk.Label(frames["profil_frame"], bg="blue", fg="white")

config_window()


start_thread()
event_gestion()
window.mainloop()

