import tkinter as tk
from tkinter import filedialog
import socket
import struct
import os
from progress.bar import Bar
import customtkinter
import configparser
from tkinter import messagebox
from tkinter import *
import re
import threading
import time

customtkinter.set_appearance_mode("system")

window = customtkinter.CTk()

window.geometry("800x500")

window.resizable(False, False)

window.title("payload loader")

notification = tk.StringVar()

notification_label = customtkinter.CTkLabel(window, textvariable=notification)
notification_label.grid(row=5, column=0, columnspan=2, sticky="nsew")


def remove_notification():
    notification.set("")
    notification_label.configure(textvariable=notification)


MAGIC = 0x0000EA6E


def send_file(ip, port, file_path):
    # Get filesize
    stats = os.stat(file_path)

    # Convert port to integer
    port = int(port)

    # Connect to console
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip, port))
    except socket.error as e:
        print(f"Could not connect to {ip}:{port}: {str(e)}")
        messagebox.showinfo("Error", "No connection could be made because the target machine actively refused it.")
        return

    # Send magic
    try:
        sock.sendall(struct.pack('<I', MAGIC))
    except socket.error as e:
        print(f"Error sending magic number: {str(e)}")
        sock.close()
        return

    # Send filesize
    try:
        sock.sendall(struct.pack('<Q', stats.st_size))
    except socket.error as e:
        print(f"Error sending filesize: {str(e)}")
        sock.close()
        return

    # Send file
    bar = Bar('Uploading', max=stats.st_size)
    with open(file_path, 'rb') as file:
        # Loop in chunks of 4096
        while True:
            data = file.read(4096)
            if not data:
                break
            try:
                sock.sendall(data)
            except socket.error as e:
                print(f"Error sending file data: {str(e)}")
                sock.close()
                return
            bar.next(len(data))

    bar.finish()
    sock.close()
    messagebox.showinfo("Payload Successful", "Payload has been sent successfully !")


def send_game_iso(ip, port, file_path, progress_label):
    # Get filesize
    stats = os.stat(file_path)

    # Connect to console
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    # Send magic
    sock.sendall(struct.pack('<I', MAGIC))

    # Send filesize
    sock.sendall(struct.pack('<Q', stats.st_size))

    # Send file
    bytes_sent = 0
    with open(file_path, 'rb') as file:
        # Loop in chunks of 4096
        while True:
            data = file.read(4096)
            if data == b'':
                break
            sock.sendall(data)
            bytes_sent += len(data)
            progress = bytes_sent / stats.st_size
            progress_percentage = f"{progress:.0%}"
            progress_label.configure(text=f"Sending Game: {progress_percentage}")

    sock.close()
    progress_label.destroy()


def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_path_var.set(file_path)


send_thread = None


def send_game():
    global send_thread
    ip = ip_entry.get()
    port = int(port_entry.get())
    file_path = file_path_var.get()
    if file_path:
        try:
            progress_label = customtkinter.CTkLabel(window, text="")
            progress_label.grid(row=6, column=0, padx=50, pady=10)

            send_thread = threading.Thread(target=send_game_iso, args=(ip, port, file_path, progress_label))
            send_thread.start()

            # add a message box to inform user that the file transfer has started
            messagebox.showinfo("Game", "Game transfer has started.")

            # create a new thread to keep the UI responsive
            progress_thread = threading.Thread(target=update_ui)
            progress_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send game: {e}")


def update_ui():
    global send_thread
    while send_thread.is_alive():
        window.update()
        time.sleep(0.1)


select_file_button = customtkinter.CTkButton(window, text="Select Game", width=110, height=25, border_width=0,
                                             corner_radius=8, hover_color="green", hover=True, command=select_file)
select_file_button.grid(row=4, column=0, padx=5, pady=5, sticky='w')

file_path_var = tk.StringVar()

file_path_label = customtkinter.CTkLabel(window, width=70, textvariable=file_path_var)
file_path_label.grid(row=4, column=0, padx=200, pady=5, sticky='w')

send_file_button = customtkinter.CTkButton(window, text="Send Game", width=110, height=25, border_width=0,
                                           corner_radius=8, hover_color="green", hover=True, command=send_game)
send_file_button.grid(row=5, column=0, padx=5, pady=5, sticky='w')
send_file_button.grid(row=5, column=0, padx=5, pady=5, sticky='w')

config = configparser.ConfigParser()

try:
    config.read('config.ini')
    ip = config.get('Network', 'IP', fallback='')
    port = config.get('Network', 'Port', fallback='')

    ip_label = customtkinter.CTkLabel(window, text="Target IP address:")
    ip_label.grid(row=0, column=0, sticky=W, pady=5)
    ip_entry = customtkinter.CTkEntry(window, width=120)
    ip_entry.grid(row=0, column=0, sticky=W, pady=5, padx=120)
    ip_entry.insert(0, ip)

    window.grid_columnconfigure(2, weight=1)

    port_label = customtkinter.CTkLabel(window, text="Target port number:")
    port_label.grid(row=1, column=0, sticky=W, pady=5)
    port_entry = customtkinter.CTkEntry(window, width=55)
    port_entry.grid(row=1, column=0, sticky=W, pady=5, padx=120)
    port_entry.insert(0, port)
except Exception as e:
    messagebox.showerror("Error", f"An error occurred while reading the config file: {str(e)}")


def save_config():
    ip = ip_entry.get()
    port = port_entry.get()

    if not validate_ip(ip):
        messagebox.showerror("Invalid IP", "Please enter a valid IP address.")
        return
    if not validate_port(port):
        messagebox.showerror("Invalid Port", "Please enter a valid port number.")
        return

    config['Network'] = {'IP': ip, 'Port': port}
    try:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        notification.set(f"IP Address and Port saved successfully")
        window.after(5000, remove_notification)
        messagebox.showinfo("Config Saved", "Configuration saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while writing to the config file: {str(e)}")


save_button = customtkinter.CTkButton(window, text="Save", width=80, height=25, border_width=0, corner_radius=8,
                                      hover_color="green", hover=True, command=save_config)
save_button.grid(row=0, column=0, pady=5, padx=250)


def validate_ip(ip):
    ip_regex = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    return ip_regex.match(ip)


def validate_port(port):
    try:
        port = int(port)
        if port < 0 or port > 65535:
            return False
    except ValueError:
        return False
    return True


def on_validate_port(port):
    return validate_port(port) and len(port) <= 5


vcmd = (window.register(on_validate_port), '%P')
port_entry.configure(validate="key", validatecommand=vcmd)

script_folder = os.path.dirname(os.path.abspath(__file__))

elf_folder_path = os.path.join(script_folder, 'Elf')

tabs = customtkinter.CTkTabview(window)
tabs.grid(row=3, column=0, padx=5, pady=5, sticky='w')

for dirpath, dirnames, filenames in os.walk(elf_folder_path):
    if dirpath != elf_folder_path:
        subfolder_label = os.path.basename(dirpath)
        tab = tabs.add(subfolder_label)
        subfolder_canvas = customtkinter.CTkCanvas(tab, height=300, width=570, bg="#292726", highlightthickness=0)
        subfolder_canvas.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        subfolder_frame = customtkinter.CTkFrame(subfolder_canvas)
        subfolder_canvas.create_window(0, 0, window=subfolder_frame)
        row_num = 0

        for filename in filenames:
            if filename.endswith('.elf'):
                file_path = os.path.join(dirpath, filename)
                button = customtkinter.CTkButton(
                    subfolder_frame,
                    text=filename,
                    border_width=0,
                    corner_radius=8,
                    hover_color="green",
                    hover=True,
                    command=lambda file_path=file_path: send_file(ip, port, file_path)
                )
                button.grid(row=row_num, column=0, sticky='nsew', padx=5, pady=5)
                row_num += 1

        subfolder_scrollbar = customtkinter.CTkScrollbar(tab, command=subfolder_canvas.yview)
        subfolder_scrollbar.grid(row=0, column=1, sticky='ns')
        subfolder_canvas.config(yscrollcommand=subfolder_scrollbar.set)
        subfolder_canvas.config(scrollregion=subfolder_canvas.bbox(tk.ALL))

window.mainloop()
