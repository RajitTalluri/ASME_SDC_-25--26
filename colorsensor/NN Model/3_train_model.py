import torch 
import torch.nn as nn # layers, losses
import torch.optim as optim # optimizers / weight update algorithims
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns # plotting lib


class RGBclassifierNN(nn.Module):
    def __init__(self):
        super().__init__()
        
        # layers fc for fully connected every input connects to each neuron in next layer
        self.fc1 = nn.Linear(3, 64) # 
        self.ReLu = nn.ReLU()
        self.fc2 = nn.Linear(64, 32) # 
        
        