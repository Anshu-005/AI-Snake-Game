import numpy as np
import random


class PrioritizedReplayBuffer:

    def __init__(self, capacity, alpha=0.6):
        self.capacity = capacity
        self.alpha = alpha

        self.buffer = []
        self.priorities = []
        self.position = 0

    def __len__(self):
        return len(self.buffer)

    def add(self, experience):
        max_priority = max(self.priorities, default=1.0)

        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
            self.priorities.append(max_priority)
        else:
            self.buffer[self.position] = experience
            self.priorities[self.position] = max_priority

        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size, beta=0.4):

        priorities = np.array(self.priorities, dtype=np.float64)

        # Convert priorities into sampling probabilities
        probabilities = priorities ** self.alpha
        probabilities /= probabilities.sum()

        # Sample experiences according to their probabilities
        indices = np.random.choice(
            len(self.buffer),
            batch_size,
            p=probabilities,
            replace=False
        )

        experiences = [self.buffer[i] for i in indices]

        # Importance-sampling weights correct sampling bias
        weights = (len(self.buffer) * probabilities[indices]) ** (-beta)
        weights /= weights.max()

        return experiences, indices, weights.astype(np.float32)

    def update_priorities(self, indices, errors):

        for index, error in zip(indices, errors):
            self.priorities[index] = abs(float(error)) + 1e-5