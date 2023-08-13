import socket, time
from emu_socket import EmulatorSocketClient
from main_window import MainWindow
import numpy as np

if __name__ == '__main__':
    emu_socket = EmulatorSocketClient(54000)
    emu_socket.run_snes('/home/dustin/sonya.sst')
    emu_socket.connect()
    while emu_socket.run_socket_frame():
        print(emu_socket.actor1.health)
