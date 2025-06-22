import numpy as np
import torch, nn_pytorch, sys
from emu_socket import EmulatorSocketClient, ActorP1, ActorP2
from mk.characters import SonyaCharacter

class TorchAction:

    def __init__(self, name, payload):
        self.name = name
        self.probability = 0.0
        self.rewards = np.array([])
        self.average = 0.0
        self.payload = payload.split('~')[0]
        self.frame = int(payload.strip().split('~')[1])
        self.last_reward = 0

    def reward(self, reward):
        self.last_reward = reward
        self.rewards = np.append(reward, self.rewards)

class TorchAgent:

    def __init__(self):
        self.character = SonyaCharacter()
        self.actions = []
        self.recent_action: TorchAction = None
        for key in self.character.actions.keys():
            self.actions.append(TorchAction(key, self.character.actions[key]))

    def run_frame(self, model, p1: ActorP1, p2: ActorP2):
        # P1 Health / 166, P2 Health / 166, Distance / 255 , State / 255
        damage_dished = p2.health - p2.prev_health
        damage_taken = p1.health - p1.prev_health
        health_delta = (p1.health - p2.health)
        max_x = 765.0
        max_y = 255.0
        dist = p1.dist(p2.x, p2.y)
        #observation_array = torch.Tensor([health_delta, p1.x / max_x, p1.y / max_y, p2.x / max_x, p2.y / max_y])
        #observation_array = torch.Tensor([health_delta, p1.x, p1.y, p2.x, p2.y, p1.dist(p1.x, p2.x), p1.state, p2.state, p1.health, p2.health])
        #observation_array = torch.Tensor([dist, p1.x, p1.y, p2.x, p2.y])
        observation_array = torch.Tensor([p2.state, p1.x, p1.y, p2.x, p2.y])
        pred = model.forward(observation_array).detach().numpy()
        max_index = np.argmax(pred)
        print(self.actions[max_index].payload)
        self.recent_action = self.actions[max_index]


class TorchEnvironment:

    def __init__(self):
        self.model = nn_pytorch.Network()
        self.model.load_state_dict(torch.load(open('data/train.trn', 'rb')))
        self.monte_agent = TorchAgent()

    def run_frame(self, p1, p2):
        # Run Frame
        self.monte_agent.run_frame(self.model, p1, p2)
        return self.monte_agent.recent_action

    def start_frame(self, p1, p2):
        self.current_state = TorchAgent(p1, p2)
        return self.monte_agent.run_frame()

class TorchClient:

    def __init__(self, port, save_file):
        self.socket_client = EmulatorSocketClient(port)
        self.monte_environment = TorchEnvironment()
        self.frame = 0
        self.timesteps = 0
        self.skip_timer = 8
        self.save_file = save_file
        self.terminate_flag = False
    
    def should_terminate(self):
        return self.socket_client.actor1.health <= 0 or self.socket_client.actor2.health <= 0

    def run(self):
        self.socket_client.run_snes(self.save_file)
        self.socket_client.connect()
        while not self.terminate_flag and self.socket_client.run_socket_frame():
            if self.skip_timer <= 0:
                self.terminate_flag = self.should_terminate()
                cur_control = self.monte_environment.run_frame(self.socket_client.actor1, self.socket_client.actor2)
                self.skip_timer = cur_control.frame
                self.socket_client.set_payload(cur_control.payload, '')
                self.timesteps += 1
            self.frame = self.frame + 1
            self.skip_timer -= 1
        #self.monte_environment.print_rewards()
        self.socket_client.disconnect()
        self.socket_client.close_snes()


if __name__ == '__main__':
    torch_client = TorchClient(int(sys.argv[1]), sys.argv[2])
    torch_client.run()