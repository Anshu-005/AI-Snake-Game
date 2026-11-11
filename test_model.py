import torch
from model.neural_network import Linear_QNet

model = Linear_QNet(11, 256, 3)

dummy_input = torch.randn(1, 11)

output = model(dummy_input)

print("Input shape:", dummy_input.shape)
print("Output shape:", output.shape)
print("Q-values:", output)