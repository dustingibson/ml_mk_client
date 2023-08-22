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

        self.labels = torch.Tensor([ x[-1] for x in self.data ])
        self.data = torch.Tensor([ x[1:] for x in self.data ])

    def __getitem__(self, index):
        encoded_label = [0.0 for x in range(17)]
        encoded_label[int(self.labels[index])] = 1.0
        encoded_label = torch.Tensor(encoded_label)
        return (encoded_label, self.data[index])

class Network(nn.Module):

    def __init__(self):
        super(Network, self).__init__()
        self.linear1 = nn.Linear(4, 17)
        self.act1 = nn.ReLU()
        self.linear2 = nn.Linear(17, 17)
        self.act2 = nn.Sigmoid()

    def forward(self, data):
        data = self.act1(self.linear1(data))
        data = self.act2(self.linear2(data))
        return data
    

def loss(pred, actual):
    return torch.mean((pred - actual) ** 2)

def get_avgs(data):
    sum = np.sum(data)
    for col in data:
        print( (col / sum) * 100.0 )


if __name__ == "__main__":
    if str(sys.argv[1]).lower() == 'train':
        model = Network()
        optimizer = Adam(model.parameters())
        mk_dataset = CustomDataset('Sonya', 0.2)
        loss_fn = nn.MSELoss()
        for epoch in range(10):
            for res in mk_dataset:
                label, data = res
                pred = model.forward(data)
                loss_val = loss_fn(pred, label)
                optimizer.zero_grad()
                loss_val.backward()
                optimizer.step()
            print(f"Loss {loss_val.item()}")
        f = open('data/train.trn', 'wb')
        torch.save(model.state_dict(), f)
    else:
        model = Network()
        f = open('data/train.trn', 'rb')
        model.load_state_dict(torch.load(f))
        test_input = torch.Tensor([0.8, 0.8, 0.1, 0.6])
        pred = model.forward(test_input)
        print(get_avgs(pred.detach().numpy()))

    