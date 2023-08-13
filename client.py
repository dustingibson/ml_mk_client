import socket
from emu_socket import EmulatorSocketClient
from main_window import MainWindow
import numpy as np

if __name__ == '__main__':
    emu_socket = EmulatorSocketClient(54000)
    main_window = MainWindow(emu_socket)

    #-----Emulation Can be Ran Per Frame Like So:-----_#
    # emu_socket.connect()
    # while emu_socket.run_socket_frame():
    #     print("Running...")
