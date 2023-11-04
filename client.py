#!/usr/bin/python3
import socket
import tkinter as tk
import threading


def listen():
    global data
    while data == "":
        data = s.recv(1024).decode()

def start_thread():
    thread = threading.Thread(target=listen)
    thread.start()

def event_gestion(): 
    global data   
    if(data != ""):
        data = ""
        start_thread()
    window.after(5, event_gestion)

def config_window():
    window.geometry("1500x800")
    window.title("Let's Talk")
    window.config(bg="dark blue")
    config_a_button("Global")
    display_main_menu()


def config_a_button(channel):
    channels[channel] = {"button": tk.Button(window), "messages": ["[Système]: Bienvenue sur le channel "+channel+" ! Merci d'ètre polie et courtoit.\n"]}
    channels[channel]["button"].config(text=channel, bg="black", fg="white", command=lambda c=channel: go_on_a_channel(c))

def display_main_menu():
    for channel in channels.values():
        channel["button"].pack(side="top", fill="x")
    new_channel_button.pack(side="bottom")

def hide_main_menu():
    for channel in channels.values():
        channel["button"].pack_forget()
    new_channel_button.pack_forget()

def go_on_a_channel(c):
    global current_channel
    hide_main_menu()
    current_channel = c
    txt = ""
    for message in channels[c]["messages"]:
        txt += message
    current_label_conv.config(text=txt)
    channel_frame.grid(row=1, column=0)
    back_button.grid(row=0, column=0)
    current_label_conv.grid(row=1, column=0)
    send_message_input.grid(row=2, column=0)

def go_back():
    channel_frame.grid_forget()
    join_frame.grid_forget()
    back_button.grid_forget()
    display_main_menu()

def join_button():
    hide_main_menu()
    back_button.grid(row=0, column=0)
    join_frame.grid(row=1, column=0)
    new_channel_input.grid(row=1, column=0)

def join_this_channel(event):
    new_channel = new_channel_input.get()
    config_a_button(new_channel)
    go_back()

def send_message(event):
    msg = "[Vous]: "+send_message_input.get()+"\n"
    channels[current_channel]["messages"].append(msg)
    txt = ""
    for message in channels[current_channel]["messages"]:
        txt += message
    current_label_conv.config(text=txt)
    send_message_input.delete(0, 'end')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
port = 7777

#s.connect((host, port)) 
data = ""
window = tk.Tk()
channels = {}
current_channel = None
join_frame = tk.Frame(window, bg="dark blue")
channel_frame = tk.Frame(window, bg="dark blue")
current_label_conv = tk.Label(channel_frame, bg="black", fg="white")
back_button = tk.Button(window, text="Back", bg="blue", fg="white", command=go_back)
new_channel_button = tk.Button(window, text="Join/Create a channel ?", bg="blue", fg="white", command=join_button)
new_channel_input = tk.Entry(join_frame, bg="blue", fg="white")
new_channel_input.bind("<Return>", lambda e:join_this_channel(e))
send_message_input = tk.Entry(channel_frame, bg="blue", fg="white")
send_message_input.bind("<Return>", lambda e:send_message(e))

config_window()
#start_thread()
#event_gestion()
window.mainloop()

