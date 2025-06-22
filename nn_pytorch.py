import torch, sys
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.optim import Adam
from torch.utils.data.dataset import Dataset
import record_rewards
from mk.characters import SonyaCharacter


class CustomDataset(Dataset):
    def __init__(self, actor, threshold):
        label_dict = SonyaCharacter().gen_indexes()
        self.data = list(map(lambda x: list(x), record_rewards.get_training(actor, threshold)))
        for cur_data in self.data:
            cur_data[-1] = label_dict[cur_data[-1]]
        self.labels = torch.Tensor([ x[-1] for x in self.data ]).int()
        self.observation_data = torch.Tensor([ x[0:-1] for x in self.data ])

    def __len__(self):
        return len(self.observation_data)

    def __getitem__(self, index):
        encoded_label = [False for x in range(17)]
        encoded_label[int(self.labels[index])] = 1.0
        encoded_label = torch.Tensor(encoded_label).int()
        return self.observation_data[index], encoded_label

class Network(nn.Module):

    def __init__(self):
        inputs = 5
        hidden_inputs = 5
        outputs = 17
        super(Network, self).__init__()

        # self.model = nn.Sequential(
        #     nn.Flatten(),
        #     nn.Linear(inputs, hidden_inputs),
        #     nn.ReLU(),
        #     nn.Linear(hidden_inputs, ouputs),
        # )
        self.dropout = nn.Dropout(0.5)
        self.linear1 = nn.Linear(inputs, hidden_inputs)
        self.act1 = nn.Tanh()
        self.linear2 = nn.Linear(hidden_inputs, hidden_inputs)
        self.act2 = nn.Tanh()
        self.linear3 = nn.Linear(hidden_inputs, hidden_inputs)
        self.act3 = nn.Tanh()
        self.linear4 = nn.Linear(hidden_inputs, outputs)
        self.act4 = nn.Sigmoid()

    def forward(self, data):
        data = self.act1(self.linear1(data))
        data = self.act2(self.linear2(data))
        data = self.act3(self.linear3(data))
        data = self.act4(self.linear4(data))
        return self.dropout(data)
    

def loss(pred, actual):
    return torch.mean((pred - actual) ** 2)

def get_avgs(data):
    sum = np.sum(data)
    for col in data:
        print( (col / sum) * 100.0 )


if __name__ == "__main__":
    if str(sys.argv[1]).lower() == 'train':
        model = Network()
        model.train()
        optimizer = Adam(model.parameters(), lr=0.0001)
        mk_dataset = CustomDataset('Sonya', 1)
        loss_fn = nn.L1Loss()
        for epoch in range(10):
            for res in mk_dataset:
                data, label = res
                optimizer.zero_grad()
                pred = model.forward(data)
                loss_val = loss_fn(pred, label)
                loss_val.backward()
                optimizer.step()
            print(f"Loss {loss_val.item()}")
        model.eval()
        f = open('data/train.trn', 'wb')
        torch.save(model.state_dict(), f)
    else:
        model = Network()
        f = open('data/train.trn', 'rb')
        model.load_state_dict(torch.load(f))
        test_input = torch.Tensor([90])
        pred = model(test_input)
        print(pred.detach().numpy())
        print(np.argmax(pred.detach().numpy()))

    