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
        print(request)
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
            config_a_channel_button(content)
            switch_window(frames["join_frame"], frames["main_frame"])

    data = []
    window.after(1, event_gestion)

def config_window():
    window.geometry("1500x800")
    window.title("Let's Talk")
    window.config(bg="dark blue")
    new_channel_button.grid(row=1000, column=0)
    join_channel_button.grid(row=1000, column=1, sticky="se")
    new_channel_input.grid(row=1, column=0)
    join_channel_input.grid(row=1, column=0)
    back_button_channel.grid(row=0, column=0)
    back_button_create.grid(row=0, column=0)
    back_button_join.grid(row=0, column=0)
    current_label_conv.grid(row=1, column=0)
    send_message_input.grid(row=2, column=0)
    config_a_channel_button("Global")
    window.protocol("WM_DELETE_WINDOW", close_window)
    frames["main_frame"].grid(row=0, column=0)


def config_a_channel_button(channel):
    channels[channel] = {"button": tk.Button(frames["main_frame"]), "messages": []}
    channels[channel]["button"].config(text=channel, bg="black", fg="white", command=lambda c=channel: go_on_a_channel(c))
    channels[channel]["button"].grid(row=len(channels), column=0, columnspan=2, sticky="ew")


def go_on_a_channel(c):
    global current_channel
    switch_window(frames["main_frame"], frames["channel_frame"])
    current_channel = c
    txt = ""
    for message in channels[c]["messages"]:
        txt += message
    current_label_conv.config(text=txt)



def switch_window(previous_frame, new_frame):
    previous_frame.grid_forget()
    new_frame.grid(row=0, column=0)



def create_new_channel(event):
    new_channel = new_channel_input.get()
    new_channel_input.delete(0, 'end')
    config_a_channel_button(new_channel)
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
    send_message_input.delete(0, 'end')
    new_message(msg, current_channel, name)
    s.sendall(f"MSG/{current_channel}/{name}/|/{msg}".encode())

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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 7777
name = ""
wall = "ceciestunwall__||$!/\!$||__ceciestunwall"
s.connect((host, port)) 
data = []
window = tk.Tk()
channels = {}
current_channel = None

frames = {
    "main_frame":tk.Frame(window, bg="dark blue"), 
    "create_frame": tk.Frame(window, bg="dark blue"),
    "channel_frame":  tk.Frame(window, bg="dark blue"),
    "join_frame":  tk.Frame(window, bg="dark blue")
}

back_button_create = tk.Button(frames["create_frame"], text="Back", bg="blue", fg="white", command=lambda: switch_window(frames["create_frame"], frames["main_frame"]))
back_button_join = tk.Button(frames["join_frame"], text="Back", bg="blue", fg="white", command=lambda: switch_window(frames["join_frame"], frames["main_frame"]))
back_button_channel = tk.Button(frames["channel_frame"], text="Back", bg="blue", fg="white", command=lambda: switch_window(frames["channel_frame"], frames["main_frame"]))

new_channel_button = tk.Button(frames["main_frame"], text="Create a new channel ?", bg="blue", fg="white", command=lambda: switch_window(frames["main_frame"], frames["create_frame"]))
join_channel_button = tk.Button(frames["main_frame"], text="Join a new channel ?", bg="blue", fg="white", command=lambda: switch_window(frames["main_frame"], frames["join_frame"]))

new_channel_input = tk.Entry(frames["create_frame"], bg="blue", fg="white")
new_channel_input.bind("<Return>", lambda e:create_new_channel(e))

join_channel_input = tk.Entry(frames["join_frame"], bg="blue", fg="white")
join_channel_input.bind("<Return>", lambda e:join_new_channel(e))

current_label_conv = tk.Label(frames["channel_frame"], bg="black", fg="white")

send_message_input = tk.Entry(frames["channel_frame"], bg="blue", fg="white")
send_message_input.bind("<Return>", lambda e:send_message(e))


config_window()


start_thread()
event_gestion()
window.mainloop()

