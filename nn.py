import sys, os, math
import numpy as np
import record_rewards, mk.characters


class TrainNode:

    def __init__(self):
        self.dot_prod = None
        self.squash = None


class TrainingData:

    def __init__(self, n_inputs, action_set, db_results):
        print(action_set)
        self.n = len(db_results)
        self.result_matrix = np.zeros(self.n)
        self.input_matrix = np.zeros((self.n, n_inputs))

        for i in range(0, self.n):
            db_result = db_results[i]
            self.input_matrix[i] = db_result[0:-1]
            self.result_matrix[i] = action_set[db_result[-1]]


#     def __init__(self, action, health_p1, health_p2, distance, state_p1, reward):
class NNTrain:

    def __init__(self, actor):
        # Hyperparameter
        self.n_hidden_layers = 1
        self.learn_rate = 0.1
        # P1 Health, P2 Health, Distance, P2 State
        self.actor = actor
        self.n_inputs = 4
        self.actions = self.get_actions(actor)
        self.n_actions = len(self.actions)

        self.weights = []

        #Input to hidden weights
        self.weights.append(np.random.rand(self.n_actions, self.n_inputs))

        #Hidden layer to hidden layer & hidden layer to output layer weights
        for i in range(0, self.n_hidden_layers):
            self.weights.append(np.random.rand(self.n_actions, self.n_actions))
        
        self.training_set = self.get_training_set()

    def train(self):
        epoch = 3
        n = self.training_set.n
        for e in range(0, epoch):
            print(f"EPOCH {e}")
            for i in range(0, n):
                inputs = self.training_set.input_matrix[i]
                reward = self.training_set.result_matrix[i]
                res_matrix = np.zeros(self.n_actions)
                res_matrix[int(reward)] = 1.0
                input_prob, prop_results = self.forward_propagation(inputs)
                self.back_propgation(res_matrix, input_prob, prop_results)            

    def get_training_set(self):
        data = record_rewards.get_training(self.actor, 0.2)
        return TrainingData(self.n_inputs, self.actions, data)

    def forward_propagation(self, inputs):
        #print(inputs)
        train_nodes: list[TrainNode] = []
        squash = np.vectorize(lambda x: self.relu(x))
        numerate_softmax = np.vectorize(lambda x: math.exp(x))
        cur_nodes = inputs
        results = np.zeros(self.n_actions)
        # Calculate hidden nodes with weights
        # Squash resulting calculation with sigmoid
        # Input to hidden and hidden to hidden weights
        for i in range(0, self.n_hidden_layers):
            train_node = TrainNode()
            new_nodes = np.dot(self.weights[i], cur_nodes)
            train_node.dot_prod = np.copy(new_nodes)
            new_nodes = squash(new_nodes)
            train_node.squash = np.copy(new_nodes)
            cur_nodes = np.copy(new_nodes)
            train_nodes.append(train_node)
            
        # Turn our output nodes to probabilities
        #print(cur_nodes)
        results = numerate_softmax(cur_nodes)
        results = results * (1.0/np.sum(results))
        return results, train_nodes
    

    def back_propgation(self, actual_matrix, prob_matrix, a_nodes: list[TrainNode]):
        cost_primes = np.zeros(self.n_actions)
        for i in range(0, self.n_actions):
            cost_primes[i] = self.cost_prime(actual_matrix[i], prob_matrix[i])
        for i in range(0, self.n_actions):
            self.weights[-1][i] = (1.0/self.n_actions) * self.weights[-1][i] - self.learn_rate * (cost_primes[i]*a_nodes[-1].dot_prod[i])

        for i in reversed(range(self.n_hidden_layers)):
            for j in range(0, len(self.weights[:i])):
                self.weights[i][j] = (1.0/self.n_actions) * self.weights[i][j] - (self.weights[i+1][j] * cost_primes[j] * self.relu_prime(a_nodes[i].squash[j]))

    def cost_prime(self, actual, prob):
        # Deterivative of (prob - actual)^2
        return 2.0*(prob - actual)

    def ssr_prime(self, actual_matrix, prob_matrix):
        sum = 0
        for i in range(0, len(actual_matrix)):
            sum += (actual_matrix[i] - prob_matrix[i])**2
        return sum

    def sigmoid(self, x):
        return 1 / (1 + math.exp(x)**-1)
    
    def sigmoid_prime(self, x):
        return self.sigmoid(x) * (1.0 - self.sigmoid(x))
    
    def relu(self, x):
        return max(0, x)
    
    def relu_prime(self, x):
        return 0 if x <= 0 else 1

    def get_actions(self, actor) -> dict[str, int]:
        if actor == 'Sonya':
            return mk.characters.SonyaCharacter().gen_indexes()

    def softmax(self, x):
        return math.exp()
    
    def predict_me(self, health_p1, health_p2, distance, state_p2):
        inputs = np.array([health_p1 / 166.0, health_p2 / 166.0, distance / 255.0, state_p2 / 255.0])
        res, train_nodes = self.forward_propagation(inputs)
        print(res)

if __name__ == '__main__':
    train  = NNTrain('Sonya')
    train.train()
    train.predict_me(1.0, 1.0, 0.05, 0.62)