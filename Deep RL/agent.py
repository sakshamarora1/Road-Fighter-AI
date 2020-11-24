from dqn import DeepQNetwork, ReplayMemory, Transition
import torch
import numpy as np


class DQNAgent:
    def __init__(self, inputs, n_actions):
        self.brain = DeepQNetwork(inputs, 8, outputNum=n_actions)
        self.target_brain = DeepQNetwork(inputs, 8, outputNum=n_actions)
        self.target_brain.load_state_dict(self.brain.state_dict())
        self.target_brain.eval()

        self.optimizer = torch.optim.Adam(self.brain.parameters())
        self.memory = ReplayMemory(10000)
        self.action_space = [0, 1]

        self.set_params()

    def set_params(self):
        self.batch_size = 16
        self.learning_rate = 0.1
        self.discount_rate = 0.99

        self.exploration_rate = 1
        self.max_exploration_rate = 1
        self.min_exploration_rate = 0.05
        self.exploration_decay_rate = 0.02

        self.steps_done = 0

    def select_action(self, state):
        sample = np.random.random()
        threshold = self.min_exploration_rate + (
            self.max_exploration_rate - self.min_exploration_rate
        ) * np.exp(self.steps_done * self.exploration_decay_rate)

        self.steps_done += 1
        if sample > threshold:
            with torch.no_grad():
                actions = self.brain(state)
                return torch.argmax(actions).item()
        else:
            return np.random.choice(self.action_space)

    # def optimize(self):
    #     if len(self.memory) < self.batch_size:
    #         return

    #     transitions = self.memory.sample(self.batch_size)
    #     batch = Transition(*zip(*transitions))

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
        reward_batch = torch.tensor(batch.reward)
        # next_state_batch = torch.tensor(batch.next_state)

        # print(self.brain(state_batch))
        # q = self.brain(state_batch).gather(0, action_batch)
        q = torch.argmax(self.brain(state_batch), dim=1).gather(0, action_batch)
        # print(torch.argmax(self.brain(state_batch), dim=1), action_batch)
        next_state_values = torch.zeros(self.batch_size)
        next_state_values[non_final_mask] = self.target_brain(
            non_final_next_states
        ).max(1)[0]

        gamma = 0.999
        q_pred = gamma * next_state_values + reward_batch
        # print(q.dtype, q_pred.dtype)
        self.loss = torch.nn.SmoothL1Loss()(q, q_pred)
        self.loss.backward()

        self.optimizer.step()
