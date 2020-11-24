from dqn import DeepQNetwork, ReplayMemory, Transition
import torch
import numpy as np


class DQNAgent:
    def __init__(self, inputs, n_actions):
        self.brain = DeepQNetwork(inputs, 16, 16, outputNum=n_actions)
        self.target_brain = DeepQNetwork(inputs, 16, 16, outputNum=n_actions)
        self.target_brain.load_state_dict(self.brain.state_dict())
        self.target_brain.eval()

        self.set_params()
        self.optimizer = torch.optim.Adam(self.brain.parameters())
        self.memory = ReplayMemory(50000)
        self.action_space = [0, 1]

    def set_params(self):
        self.batch_size = 64

        self.max_exploration_rate = 1
        self.min_exploration_rate = 0.05
        self.exploration_decay_rate = 0.0005

        self.steps_done = 0

    def select_action(self, state):
        sample = np.random.random()
        exploration_rate = self.min_exploration_rate + (
            self.max_exploration_rate - self.min_exploration_rate
        ) * np.exp(-self.steps_done * self.exploration_decay_rate)

        self.steps_done += 1
        if sample > exploration_rate:
            with torch.no_grad():
                actions = self.brain(state)
                return torch.argmax(actions).item()
        else:
            return np.random.choice(self.action_space)

    def learn(self):
        if len(self.memory) < self.batch_size:
            return

        self.optimizer.zero_grad()

        max_capacity = (
            len(self.memory)
            if len(self.memory) < self.memory.capacity
            else self.memory.capacity
        )

        batch = np.random.choice(max_capacity, self.batch_size)

        transitions = self.memory.sample(self.batch_size)
        batch = Transition(*zip(*transitions))

        non_final_mask = torch.tensor(
            tuple(map(lambda s: s is not None, batch.next_state)), dtype=torch.bool,
        )
        non_final_next_states = torch.tensor(
            [s for s in batch.next_state if s is not None]
        )

        state_batch = torch.tensor(batch.state)
        action_batch = torch.tensor(batch.action)
        reward_batch = torch.tensor(batch.reward, dtype=torch.float)

        state_action_values = self.brain(state_batch).gather(
            1, action_batch.unsqueeze(-1)
        )

        next_state_values = torch.zeros(self.batch_size)
        next_state_values[non_final_mask] = self.target_brain(
            non_final_next_states
        ).max(1)[0]

        gamma = 0.99
        expected_state_action_values = (
            gamma * next_state_values + reward_batch / reward_batch.max()
        )

        self.loss = torch.nn.MSELoss()(
            expected_state_action_values.unsqueeze(-1), state_action_values
        )

        self.optimizer.zero_grad()
        self.loss.backward()
        self.optimizer.step()
