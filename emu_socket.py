import socket, threading


class BaseActor:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.health = 0
        self.state = 0
        # 1 = left, 2 = right
        self.facing = 0
        self.ctrl = {}

    def get_controls(self):
        pass

    def set_dir_controls(self):
        # Position [10] is which way it is facing. If left (1), forward is right, back is left
        if self.facing == 1:
            self.ctrl['fw'] = self.ctrl['right']
            self.ctrl['bk'] = self.ctrl['left']
        else:
            self.ctrl['fw'] = self.ctrl['left']
            self.ctrl['bk'] = self.ctrl['right']  

class ActorP1(BaseActor):

    def __init__(self):
        super().__init__()
        self.ctrl = {}
        self.get_controls()

    def set_data(self, data):
        p2_x = data[3]*255 + data[2]
        self.x = data[1]*255 + data[0]
        self.y = data[4]
        self.state = data[6]
        self.health = data[8]
        # If less than p2 x face left otherwise right
        self.facing = 1 if  self.x < p2_x else 2
        self.set_dir_controls()

    def get_controls(self):
        self.ctrl['x'] = 268435578
        self.ctrl['y'] = 268435576
        self.ctrl['a'] = 268435553
        self.ctrl['b'] = 268435571
        self.ctrl['l'] = 268435569
        self.ctrl['r'] = 268435575
        self.ctrl['start'] = 268500749
        self.ctrl['select'] = 268500962
        self.ctrl['up'] = 268500818
        self.ctrl['down'] = 268500820
        self.ctrl['left'] = 268500817
        self.ctrl['right'] = 268500819
        self.ctrl['write'] = 1234

        self.ctrl['w'] = 4321


        self.ctrl['lp'] = self.ctrl['b']
        self.ctrl['hp'] = self.ctrl['y']
        self.ctrl['lk'] = self.ctrl['a']
        self.ctrl['hk'] = self.ctrl['x']
        self.ctrl['bl'] = self.ctrl['l']
        self.ctrl['dn'] = self.ctrl['down']
        self.set_dir_controls()


class ActorP2(BaseActor):

    def __init__(self):
        super().__init__()
        self.ctrl = {}
        self.get_controls()

    def set_data(self, data):
        p1_x = data[1]*255 + data[0]
        self.x = data[3]*255 + data[2]
        self.y = data[4]
        self.state = data[6]
        self.health = data[8]
        # If less than p2 x face left otherwise right
        self.facing = 1 if  self.x < p1_x else 2
        self.set_dir_controls()

    def get_controls(self):
        self.ctrl['x'] = 268435578
        self.ctrl['y'] = 268435576
        self.ctrl['a'] = 268435553
        self.ctrl['b'] = 268435571
        self.ctrl['l'] = 268435569
        self.ctrl['r'] = 268435575
        self.ctrl['start'] = 268500749
        self.ctrl['select'] = 268500962
        self.ctrl['up'] = 268500818
        self.ctrl['down'] = 268500820
        self.ctrl['left'] = 268500817
        self.ctrl['right'] = 268500819
        self.ctrl['write'] = 1234

        self.ctrl['w'] = 4321

        self.ctrl['lp'] = self.ctrl['b']
        self.ctrl['hp'] = self.ctrl['y']
        self.ctrl['lk'] = self.ctrl['a']
        self.ctrl['hk'] = self.ctrl['x']
        self.ctrl['bl'] = self.ctrl['l']
        self.ctrl['dn'] = self.ctrl['down']
        self.set_dir_controls()

class EmulatorSocketClient:
    
    def __init__(self, port):
        self.port = port
        self.host = "127.0.0.1"
        self.payload_queue = [[],[]]
        self.frame_queue = [[],[]]
        self.data = [0] * 1024
        self.actor1 = ActorP1()
        self.actor2 = ActorP2()
        self.rec_lock = False
        self.flag_kill = False

    def kill(self):
        self.flag_kill = True

    def run_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(self.get_payload())
            while not self.flag_kill:
                #print("Sending")
                payload = self.get_payload()
                s.sendall(payload)
                self.data = s.recv(1024)
                self.actor1.set_data(self.data)
                self.actor2.set_data(self.data)
        print("Socket killed")
    
    def get_payload(self):
        out_bytes = bytearray()
        out_bytes.append(1)
        if len(self.frame_queue[0]) > 0 and not self.rec_lock:
            self.frame_queue[0][0] = self.frame_queue[0][0] - 1
            if self.frame_queue[0][0] <= 0:
                self.frame_queue[0].pop(0)
                out_bytes.extend(self.payload_queue[0].pop(0))

        out_bytes.append(2)
        if len(self.frame_queue[1]) > 0 and not self.rec_lock:
            self.frame_queue[1][0] = self.frame_queue[1][0] - 1
            if self.frame_queue[1][0] > 0:
                self.frame_queue[1].pop(0)
                out_bytes.extend(self.payload_queue[1].pop(0))
        return out_bytes
    
    def set_payload(self, control_str_p1, control_str_p2):
        self.rec_lock = True
        self.payload_queue = [[],[]]
        self.frame_queue = [[0],[0]]
        # Specs:
        # 0x01<controls p1 bytes...>0x02<controls p2 bytes...>0x00
        # Controls Bytes: for x frames [0x01]
        all_chars_p1 = control_str_p1.strip().split(',')
        all_chars_p2 = control_str_p2.strip().split(',')
        for i in range(0, max(len(all_chars_p1), len(all_chars_p2))):
            if i >= len(all_chars_p1):
                self.set_queue_control(None, all_chars_p2[i])
            elif i >= len(all_chars_p2):
                self.set_queue_control(all_chars_p1[i], None)
            else:
                self.set_queue_control(all_chars_p1[i], all_chars_p2[i])
        self.rec_lock = False
        self.frame_queue[0].pop()
        self.frame_queue[1].pop()

    def set_queue_control(self, p1_chars, p2_chars):
        payload_bytes = []
        #payload_bytes.append(1)
        if p1_chars is not None:
            self.payload_queue[0].append(bytearray(self.from_control_str(1, p1_chars)))
        #payload_bytes.append(2)
        if p2_chars is not None:
            self.payload_queue[1].append(bytearray(self.from_control_str(2, p2_chars)))
        return payload_bytes
        

    def from_control_str(self, player, control_str):
        endian = 'big'
        byte_len = 4
        payload_bytes = []
        if control_str == '':
            return []
        hold_controls = control_str.split('|')[0].split('+')
        for control in hold_controls:
            res = self.from_control_char(player, control)
            if res is not None:
                payload_bytes.extend(res.to_bytes(byte_len, endian))
        # Number of Frames----------------------- 
        frames = 1
        frame_info = control_str.split('|')
        if len(frame_info) >= 2:
            frames = int(frame_info[1])
        if player == 1:
            self.frame_queue[0].append(frames)
        else:
            self.frame_queue[1].append(frames)
        payload_bytes.extend(frames.to_bytes(2, endian))
        #--------------------------------------------------
        return payload_bytes
    
    # TODO: Condensed these to actor objects

    def from_control_char(self, player, control_char):
        if player == 1:
            return self.actor1.ctrl[control_char.strip().lower()]
        else:
            return self.actor2.ctrl[control_char.strip().lower()]