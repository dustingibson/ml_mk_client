import socket
from emu_socket import EmulatorSocketClient
from main_window import MainWindow

if __name__ == '__main__':
    emu_socket = EmulatorSocketClient(54000)
    main_window = MainWindow(emu_socket)