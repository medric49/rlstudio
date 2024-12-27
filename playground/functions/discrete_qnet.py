from torch import nn


class DiscreteQNet(nn.Module):

    def __init__(self, observation_dim: int, num_actions: int):
        super().__init__()
        self.layer1 = nn.Linear(observation_dim, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, num_actions)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        return self.layer3(x)
