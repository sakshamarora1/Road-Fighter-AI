from collections import namedtuple
import random

import torch
import torch.nn as nn


Transition = namedtuple("Transition", ("state", "action", "reward", "next_state"))


class ReplayMemory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        if (
            self.memory[self.position] is None
            or args[2] > self.memory[self.position].reward
        ):
            self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class DeepQNetwork(nn.Module):
    def __init__(self, inputNum, *hiddenNums, outputNum):
        super(DeepQNetwork, self).__init__()
        self.input_layer = nn.Linear(inputNum, hiddenNums[0])
        self.relu = nn.ReLU()

        hidden_layer_list = []
        for i in range(len(hiddenNums) - 1):
            hidden_layer_list.extend(
                [nn.Linear(hiddenNums[i], hiddenNums[i + 1]), nn.ReLU()]
            )
        self.hidden_layers = nn.Sequential(*hidden_layer_list)

        self.output_layer = nn.Linear(hiddenNums[-1], outputNum)

        # self.randomize_weights()

    def forward(self, x):
        x = torch.Tensor(x)
        x = self.relu(self.input_layer(x))
        x = self.hidden_layers(x)
        x = self.output_layer(x)

        return x

    # def randomize_weights(self):
    #     torch.nn.init.normal_(self.input_layer.weight, mean=0.0, std=0.1)
    #     torch.nn.init.normal_(self.hidden_layers.weight, mean=0.0, std=0.1)
    #     torch.nn.init.normal_(self.output_layer.weight, mean=0.0, std=0.1)
