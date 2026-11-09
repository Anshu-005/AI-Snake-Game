import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os
import copy

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

        # Separate network for calculating target Q-values
        self.target_model = copy.deepcopy(model)
        self.target_model.eval()

        # Count training updates
        self.train_steps = 0

    def train_step(
    self,
    state,
    action,
    reward,
    next_state,
    done,
    weights=None
    ):

        # Convert inputs into tensors
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        done = torch.tensor(done, dtype=torch.float)

        # Handle single experiences from short-memory training
        if len(state.shape) == 1:
            state = state.unsqueeze(0)
            next_state = next_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = reward.unsqueeze(0)
            done = done.unsqueeze(0)

        # Current Q-values
        pred = self.model(state)

        # Double DQN target calculation
        with torch.no_grad():

            # Online network selects the next action
            next_actions = self.model(next_state).argmax(
                dim=1,
                keepdim=True
            )

            # Target network evaluates that action
            next_q_values = self.target_model(next_state)

            next_q = next_q_values.gather(
                1,
                next_actions
            ).squeeze(1)

            # Calculate updated Q-values
            q_new = reward + self.gamma * next_q * (1 - done)

        # Find the action selected in each experience
        action_indices = action.argmax(
            dim=1,
            keepdim=True
        )

        # Calculate TD errors for prioritization
        current_q = pred.gather(
            1,
            action_indices
        ).squeeze(1)

        td_errors = torch.abs(q_new - current_q).detach()

        # Update only the Q-value of the selected action
        target = pred.detach().clone()

        target.scatter_(
            1,
            action_indices,
            q_new.unsqueeze(1)
        )

        # Calculate loss separately for each experience
        per_sample_loss = ((target - pred) ** 2).mean(dim=1)

        # Apply importance-sampling weights
        if weights is not None:
            weights = torch.tensor(weights, dtype=torch.float)
            loss = (per_sample_loss * weights).mean()
        else:
            loss = per_sample_loss.mean()

        # Backpropagation
        self.optimizer.zero_grad()

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            max_norm=10.0
        )

        self.optimizer.step()

        # Update target network periodically
        self.train_steps += 1

        if self.train_steps % 1000 == 0:
            self.target_model.load_state_dict(
                self.model.state_dict()
            )

        # Return TD errors to update replay priorities
        return td_errors.cpu().numpy()
