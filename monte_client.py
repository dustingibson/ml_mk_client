import numpy as np
from emu_socket import EmulatorSocketClient, ActorP1, ActorP2
from mk.characters import SonyaCharacter
import copy

class MonteAction:

    def __init__(self, name, payload):
        self.name = name
        self.probability = 0.0
        self.rewards = np.array([])
        self.average = 0.0
        self.payload = payload

    def reward(self, reward):
        self.rewards = np.append(reward, self.rewards)

class MonteState:

    def __init__(self, action_taken: MonteAction, actor1: ActorP1, actor2: ActorP2):
        self.action_taken = action_taken
        self.p1_health = actor1.health
        self.p2_health = actor2.health

class MonteAgent:

    def __init__(self):
        self.character = SonyaCharacter()
        self.actions = []
        self.recent_action: MonteAction = None
        for key in self.character.actions.keys():
            self.actions.append(MonteAction(key, self.character.actions[key]))
        # Inititialize probabilities
        for action in self.actions:
            action.probability = 1.0 / len(self.actions)

    def run_frame(self):
        self.recent_action = ( np.random.choice( self.actions, 1, map(lambda a: a.probability, self.actions) ) ) [0]

    def update_action(self, reward):
        self.recent_action.reward(reward)

class MonteEnvironment:

    def __init__(self):
        self.prev_state = None
        self.cur_state = None
        self.monte_agent = MonteAgent()

    def init_frame(self, p1, p2):
        self.prev_state = MonteState(None, p1, p2)

    def run_frame(self, p1, p2):
        # Run Frame
        self.monte_agent.run_frame()
        self.current_state = MonteState(self.monte_agent.recent_action, p1, p2)
        # Get the reward for the action of the previous state
        print(self.reward())
        self.monte_agent.update_action(self.reward())
        self.prev_state = copy.copy(self.current_state)
        return self.monte_agent.recent_action


    def start_frame(self, p1, p2):
        self.current_state = MonteAgent(p1, p2)
        return self.monte_agent.run_frame()

    def end_frame(self):
        self.end_frame = self.current_state

    def reward(self):
        # Let for P2 the better
        if self.prev_state is not None:
            return (self.prev_state.p2_health - self.current_state.p2_health) + (self.current_state.p1_health - self.prev_state.p1_health)
        else:
            return 0

    def print_rewards(self):
        for cur_action in self.monte_agent.actions:
            print(f'{cur_action.name} {np.average(cur_action.rewards)}')


class MonteEpisode:

    def __init__(self):
        self.prev_environement = MonteEnvironment()
        self.monte_environment = MonteEnvironment()

    
    

class MonteClient:

    def __init__(self):
        self.socket_client = EmulatorSocketClient(54000)
        self.monte_environment = MonteEnvironment()
        self.frame = 0
        self.timesteps = 0
        self.frame_skip = 60
    
    def should_terminate(self):
        return self.socket_client.actor1.health <= 0 or self.socket_client.actor2.health <= 0

    def run(self):
        self.socket_client.run_snes('/home/dustin/sonya.sst')
        self.socket_client.connect()
        while not self.should_terminate() and self.socket_client.run_socket_frame():
            if self.frame % self.frame_skip == 0:
                if self.timesteps == 0:
                    self.monte_environment.init_frame(self.socket_client.actor1, self.socket_client.actor2)
                else:
                    cur_control = self.monte_environment.run_frame(self.socket_client.actor1, self.socket_client.actor2)
                    self.socket_client.set_payload(cur_control.payload, '')
                self.timesteps += 1
            self.frame = self.frame + 1
        self.monte_environment.print_rewards()
        self.socket_client.disconnect()
        self.socket_client.close_snes()


if __name__ == '__main__':
    monte_client = MonteClient()
    monte_client.run()