import torch 
import torch.nn as nn # layers, losses
import torch.optim as optim # optimizers / weight update algorithims
import numpy as np
import os

import matplotlib.pyplot as plt

from tkinter import Tk, filedialog
import pandas as pd


# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')

def load_and_prepare_data():
    """
    Load preprocessed CSV and prepare tensors for training
    """
    # Open file picker
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="Select preprocessed data CSV",
        initialdir=DATA_DIR,
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    root.destroy()
    
    if not file_path:
        print("No file selected")
        return None, None
    
    # Load CSV
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} samples")
    
    # Extract RGB columns (already normalized 0-1)
    X = df[['Red', 'Green', 'Blue']].values
    
    # Extract labels (already 0 or 1)
    y = df['Category'].values
    
    # Convert to tensors
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)  # shape [n, 1]
    
    print(f"X shape: {X_tensor.shape}")
    print(f"y shape: {y_tensor.shape}")
    print(f"Label distribution: {sum(y)} ones, {len(y) - sum(y)} zeros")
    
    return X_tensor, y_tensor



class RGBclassifierNN(nn.Module):
    def __init__(self):
        super().__init__()
        # Defining the structure of the NN
        # fc: fully connected every input connects to each neuron in next layer
        self.fc1 = nn.Linear(3, 64) # 3 nodes for R,G,B inputs
        self.ReLu = nn.ReLU() # negative values to 0
        self.fc2 = nn.Linear(64, 32) # compress
        self.fc3 = nn.Linear(32, 16) # compress
        self.fc4 = nn.Linear(16, 1) # output/end layer 
    
    def forward(self, x):
        # how data moves through NN
        # pass thorugh each layer and apply ReLu activiation
        x = self.ReLu(self.fc1(x))
        x = self.ReLu(self.fc2(x))
        x = self.ReLu(self.fc3(x))
        x = self.fc4(x) # no activation for output
        
        return x

        
def train():
    RGB, Labels = load_and_prepare_data() # X is RBG values y is labels
    if RGB is None or Labels is None:
        print("File error.")
        return
    
    indices = torch.randperm(len(RGB)) # randomize indices to 80 20 split
    train_size = int(0.8 * len(RGB))
    train_indices = indices[:train_size]
    test_indices = indices[train_size:]
    RGB_train, Labels_train = RGB[train_indices], Labels[train_indices]
    RGB_test, Labels_test = RGB[test_indices], Labels[test_indices]
    
    model = RGBclassifierNN() # create model instance
    
    
    optimizer = optim.Adam(model.parameters(), lr=0.01) # updates wieghts, learning rate
    
    
    loss_fn = nn.BCEWithLogitsLoss() # binary cross entropty loss function
    
    epochs = 100
    for epoch in range(epochs):
        predictions = model(RGB_train) # forward pass
        loss = loss_fn(predictions, Labels_train) # calculates loss
        loss.backward() # backpropagation
        optimizer.step() # update weights
        optimizer.zero_grad() # reset gradients for next epoch
        
        #print loss every 10 epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}: Loss = {loss.item():.4f}")
    
    # Evaluate on test set after training
    model.eval() # set to evaluation mode
    with torch.no_grad():
        test_pred = model(RGB_test)
        test_loss = loss_fn(test_pred, Labels_test)
        print(f"\nTest Loss: {test_loss.item():.4f}")
        
        # Calculate accuracy
        pred_binary = (test_pred > 0.5).float()
        accuracy = (pred_binary == Labels_test).float().mean().item()
        print(f"Test Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    train()