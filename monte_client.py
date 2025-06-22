import numpy as np
from emu_socket import EmulatorSocketClient, ActorP1, ActorP2
from mk.characters import SonyaCharacter
import copy, record_rewards, sys, math, uuid

class MonteAction:

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

class MonteState:

    def __init__(self, action_taken: MonteAction, actor1: ActorP1, actor2: ActorP2):
        self.action_taken = action_taken
        self.p1_health = actor1.health
        self.p2_health = actor2.health
        self.distance = actor1.dist(actor2.x, actor2.y)

class MonteAgent:

    def __init__(self):
        self.character = SonyaCharacter()
        self.actions = []
        self.recent_action: MonteAction = None
        self.prev_action: MonteAction = None
        for key in self.character.actions.keys():
            self.actions.append(MonteAction(key, self.character.actions[key]))
        # Inititialize probabilities
        for action in self.actions:
            action.probability = 1.0 / len(self.actions)

    def run_frame(self):
        if self.recent_action is not None:
            self.prev_action = copy.copy(self.recent_action)
        self.recent_action = ( np.random.choice( self.actions, 1, map(lambda a: a.probability, self.actions) ) ) [0]

    def update_action(self, reward):
        self.recent_action.reward(reward)

class MonteEnvironment:

    def __init__(self):
        self.prev_state = None
        self.prev_action = None
        self.cur_state = None
        self.monte_agent = MonteAgent()
        self.monte_agent_p2 = MonteAgent()
        self.match_id = str(uuid.uuid4())

    def init_frame(self, p1, p2):
        self.prev_state = MonteState(None, p1, p2)

    def run_frame(self, p1, p2, save_file):
        # Run Frame
        self.monte_agent.run_frame()
        self.monte_agent_p2.run_frame()
        self.current_state = MonteState(self.monte_agent.recent_action, p1, p2)
        # Get the reward for the action of the previous state
        damage_dished = (self.prev_state.p2_health - self.current_state.p2_health)
        damage_taken = (self.prev_state.p1_health - self.current_state.p1_health)
        if self.monte_agent.prev_action is not None:
            record_rewards.write_data('Sonya', self.monte_agent.prev_action.name, p1, p2, damage_dished, damage_taken, save_file, self.reward(damage_dished, damage_taken), self.match_id)
        self.monte_agent.update_action(self.reward(damage_dished, damage_taken))
        self.prev_state = copy.copy(self.current_state)
        return [self.monte_agent.recent_action, self.monte_agent_p2.recent_action]


    def update_victory(self, did_win: bool):
        record_rewards.update_results(self.match_id, did_win)

    def start_frame(self, p1, p2):
        self.current_state = MonteAgent(p1, p2)
        return self.monte_agent.run_frame()

    def end_frame(self):
        self.end_frame = self.current_state

    def reward(self, damage_dished, damage_taken):
        if self.prev_state is not None:
            # TODO: 0 is good should have positive effect!
            offense_score = ( min(damage_dished, 55)/55 )
            defense_score = ( min(55-damage_taken, 55)/55 )
            return offense_score*0.8 + defense_score*0.2
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

    def __init__(self, port, save_file, sim_p2=True):
        self.socket_client = EmulatorSocketClient(port)
        self.monte_environment = MonteEnvironment()
        self.frame = 0
        self.timesteps = 0
        self.skip_timer = 8
        self.save_file = save_file
        self.sim_p2 = sim_p2
        self.terminate_flag = False
    
    def should_terminate(self):
        res = self.socket_client.actor1.health <= 0 or self.socket_client.actor2.health <= 0
        if res:
            self.monte_environment.update_victory(self.socket_client.actor2.health <= 0)
        return res

    def run(self):
        #self.socket_client.run_snes('/home/dustin/sonya.sst')
        self.socket_client.run_snes(self.save_file)
        self.socket_client.connect()
        while not self.terminate_flag and self.socket_client.run_socket_frame():
            if self.skip_timer <= 0:
                if self.timesteps == 0:
                    self.monte_environment.init_frame(self.socket_client.actor1, self.socket_client.actor2)
                else:
                    self.terminate_flag = self.should_terminate()
                    cur_control = self.monte_environment.run_frame(self.socket_client.actor1, self.socket_client.actor2, self.save_file)
                    self.skip_timer = cur_control[0].frame
                    self.socket_client.set_payload(cur_control[0].payload, cur_control[1].payload )
                self.timesteps += 1
            self.frame = self.frame + 1
            self.skip_timer -= 1
        #self.monte_environment.print_rewards()
        self.socket_client.disconnect()
        self.socket_client.close_snes()


if __name__ == '__main__':
    monte_client = MonteClient(int(sys.argv[1]), sys.argv[2])
    monte_client.run()