import sys
from emu_socket import EmulatorSocketClient
from main_window import MainWindow

if __name__ == '__main__':
    port = int(sys.argv[1])
    emu_socket = EmulatorSocketClient(port)
    main_window = MainWindow(emu_socket)

    #-----Emulation Can be Ran Per Frame Like So:-----_#
    # emu_socket.connect()
    # while emu_socket.run_socket_frame():
    #     print("Running...")
