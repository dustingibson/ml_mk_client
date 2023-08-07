import socket, threading

class EmulatorSocketClient:
    
    def __init__(self, port):
        self.port = port
        self.host = "127.0.0.1"
        self.payload_queue = []
        self.player1_controls = self.player_1_controls()
        self.player2_controls = self.player_2_controls()
        self.data = ""

    def run_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(self.get_payload())
            while True:
                #print("Sending")
                payload = self.get_payload()
                s.sendall(payload)
                self.data = s.recv(1024)
                #print(int(self.data[0]))

    
    def get_payload(self):
        if len(self.payload_queue) <= 0:
            return bytearray([1, 2])
        else:
            print(self.payload_queue[0])
            return self.payload_queue.pop()
    
    def set_payload(self, control_str_p1, control_str_p2):
        # Specs:
        # 0x01<controls p1 bytes...>0x02<controls p2 bytes...>0x00
        # Controls Bytes: for x frames [0x01]
        all_chars_p1 = control_str_p1.strip().split(',')
        all_chars_p2 = control_str_p2.strip().split(',')
        for i in range(0, max(len(all_chars_p1), len(all_chars_p2))):
            if i >= len(all_chars_p1):
                ctrl_array = self.set_queue_control(None, all_chars_p2[i])
                self.payload_queue.append(bytearray(ctrl_array))
            elif i >= len(all_chars_p2):
                ctrl_array = self.set_queue_control(all_chars_p1[i], None)
                self.payload_queue.append(bytearray(ctrl_array))
            else:
                ctrl_array = self.set_queue_control(all_chars_p1[i], all_chars_p2[i])
                self.payload_queue.append(bytearray(ctrl_array))

    def set_queue_control(self, p1_chars, p2_chars):
        payload_bytes = []
        payload_bytes.append(1)
        if p1_chars is not None:
            payload_bytes.extend(self.from_control_str(1, p1_chars))
        payload_bytes.append(2)
        if p2_chars is not None:
            payload_bytes.extend(self.from_control_str(2, p2_chars))
        return payload_bytes
        

    def from_control_str(self, player, control_str):
        endian = 'big'
        byte_len = 4
        payload_bytes = []
        if control_str == '':
            return []
        hold_controls = control_str.split('+')
        for control in hold_controls:
            res = self.from_control_char(player, control)
            print(res)
            print(res.to_bytes(byte_len, endian))
            if res is not None:
                payload_bytes.extend(res.to_bytes(byte_len, endian))
        # Number of Frames 
        frames = 180
        payload_bytes.extend(frames.to_bytes(2, endian))
        return payload_bytes
    
    def player_1_controls(self) -> int:
        ctrl = {}
        ctrl['x'] = 268435578
        ctrl['y'] = 268435576
        ctrl['a'] = 268435553
        ctrl['b'] = 268435571
        ctrl['l'] = 268435569
        ctrl['r'] = 268435575
        ctrl['start'] = 268500749
        ctrl['select'] = 268500962
        ctrl['up'] = 268500818
        ctrl['down'] = 268500820
        ctrl['left'] = 268500817
        ctrl['right'] = 268500819
        return ctrl

    def player_2_controls(self) -> int:
        ctrl = {}
        ctrl['x'] = 268435578
        ctrl['y'] = 268435576
        ctrl['a'] = 268435553
        ctrl['b'] = 268435571
        ctrl['l'] = 268435569
        ctrl['r'] = 268435575
        ctrl['start'] = 268500749
        ctrl['select'] = 268500962
        ctrl['up'] = 268500818
        ctrl['down'] = 268500820
        ctrl['left'] = 268500817
        ctrl['right'] = 268500819
        return ctrl

    def from_control_char(self, player, control_char):
        if player == 1:
            return self.player1_controls[control_char.strip().lower()]
        else:
            return self.player2_controls[control_char.strip().lower()]