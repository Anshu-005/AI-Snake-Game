import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        os.makedirs(model_folder_path, exist_ok=True)
        file_path = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_path)
        try:
            torch.save(self.state_dict(), file_name)
        except Exception:
            pass

    def load(self, file_path='./model/model.pth'):
        if os.path.exists(file_path):
            self.load_state_dict(torch.load(file_path, weights_only=True))
            self.eval()
            return True
        return False


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        pred = self.model(state)

        target = pred.detach().clone()

        with torch.no_grad():
            next_q_values = self.model(next_state)
            for idx in range(len(done)):
                Q_new = reward[idx]
                if not done[idx]:
                    Q_new = (
                        reward[idx]
                        + self.gamma * torch.max(next_q_values[idx])
                    )

                action_idx = torch.argmax(action[idx]).item()
                target[idx][action_idx] = Q_new

        # 2: Compute loss and backpropagate
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()
