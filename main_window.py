import socket
import tkinter as tk
from tkinter import scrolledtext
from tkinter.ttk import Label, Button, Entry
from emu_socket import EmulatorSocketClient
from threading import Thread
import time

class MainWindow():

    def __init__(self, socket_client: EmulatorSocketClient):
        self.player1_str = ""
        self.player2_str = ""
        self.socket_client = socket_client

        self.socket_thread = Thread(target=self.socket_client.run_socket)
        self.socket_thread.start()

        self.root = tk.Tk()
        self.set_window_props()
        self.set_buttons()
        self.set_entries()
        self.set_labels()
        self.set_text_outs()
        self.root.mainloop()

    def set_window_props(self):
        self.root.title('MK Client')
        self.root.geometry('500x500+50+50')
        self.root.resizable(False, False)
        self.root.attributes('-topmost', 1)

    def to_controls(self):
        pass

    def set_controls(self):
        print("Setting controls")
        self.socket_client.set_payload(self.player1_entry.get(), self.player2_entry.get())

    def set_buttons(self):
        self.set_player_button = Button(self.root, text="Send", command=self.set_controls)
        self.set_player_button.pack(ipadx=5, ipady=1, expand=True)
        self.set_player_button.place(x=10, y=170)

    def set_entries(self):
        self.player1_entry = Entry(self.root, textvariable=self.player1_str)
        self.player2_entry = Entry(self.root, textvariable=self.player2_str)
        self.player1_entry.pack()
        self.player2_entry.pack()
        self.player1_entry.place(x=130, y=50)
        self.player2_entry.place(x=130, y=115)
        

    def set_labels(self):
        p1ctrl_desc_label = Label(self.root, text='P1 Controls')
        p2ctrl_desc_label = Label(self.root, text='P2 Controls')
        p1out_desc_label = Label(self.root, text='P1 Out')
        p2out_desc_label = Label(self.root, text='P2 Out')
        p1ctrl_desc_label.pack()
        p2ctrl_desc_label.pack()
        p1ctrl_desc_label.place(x=10, y=50)
        p2ctrl_desc_label.place(x=10, y=115)
        p1out_desc_label.place(x=10, y=200)
        p2out_desc_label.place(x=220, y=200)
        
    def set_text_outs(self):
        self.p1_out_text = scrolledtext.ScrolledText(self.root, width = 20, height = 15)
        self.p2_out_text = scrolledtext.ScrolledText(self.root, width = 20, height = 15)
        self.p1_out_text.pack()
        self.p2_out_text.pack()
        self.p1_out_text.place(x=10, y=220)
        self.p2_out_text.place(x=220, y=220)
        
        self.output_thread = Thread(target=self.print_outputs)
        self.output_thread.start()

    def p1_out(self):
        out_strs = []
        out_strs.append('X:\t' + str((int(self.socket_client.data[0])))  )
        out_strs.append('Y:\t' + str((int(self.socket_client.data[2])))  )
        out_strs.append('State:\t' + str((int(self.socket_client.data[4])))  )
        out_strs.append('Health:\t' + str((int(self.socket_client.data[6])))  )
        return '\n'.join(out_strs)

    def p2_out(self):
        out_strs = []
        out_strs.append('X:\t' + str((int(self.socket_client.data[1])))  )
        out_strs.append('Y:\t' + str((int(self.socket_client.data[3])))  )
        out_strs.append('State:\t' + str((int(self.socket_client.data[5])))  )
        out_strs.append('Health:\t' + str((int(self.socket_client.data[7])))  )
        return '\n'.join(out_strs)

    def print_outputs(self):
        while True:
            time.sleep(1/60)
            self.p1_out_text.delete("1.0", tk.END)
            self.p2_out_text.delete("1.0", tk.END)
            self.p1_out_text.insert(tk.END, self.p1_out())
            self.p2_out_text.insert(tk.END, self.p2_out())