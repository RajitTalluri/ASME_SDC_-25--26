import torch 
import torch.nn as nn # layers, losses
import torch.optim as optim # optimizers / weight update algorithims
from torch.optim import lr_scheduler as lr
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
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1) # shape [n, 1]
    
    print(f"X shape: {X_tensor.shape}")
    print(f"y shape: {y_tensor.shape}")
    print(f"Label distribution: {sum(y)} ones: g or b, {len(y) - sum(y)} zeros: neither")
    
    return X_tensor, y_tensor



class RGBclassifierNN(nn.Module):
    def __init__(self):
        super().__init__()
        # Defining the structure of the NN
        # fc: fully connected every input connects to each neuron in next layer
        self.ReLu = nn.ReLU() # negative values to 0
        self.fc1 = nn.Linear(3, 64) # 3 nodes for R,G,B inputs
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
    RGB, Labels = load_and_prepare_data() # X is RBG values, y is labels
    if RGB is None or Labels is None:
        print("File error.")
        return None, None, None, None
    
    indices = torch.randperm(len(RGB)) # randomize indices to 80 20 training/testing split
    train_size = int(0.8 * len(RGB))
    train_indices = indices[:train_size]
    test_indices = indices[train_size:]
    RGB_train, Labels_train = RGB[train_indices], Labels[train_indices]
    RGB_test, Labels_test = RGB[test_indices], Labels[test_indices]
    
    model = RGBclassifierNN() # create model instance
    
    # Adam algorithim optimizer
    optimizer = optim.Adam(model.parameters(), lr=0.01) # updates wieghts and biases using learning rate
    
    scheduler = lr.StepLR(optimizer, step_size=50, gamma=0.1) # learning rate decay for every step_size epochs
    
    loss_fn = nn.BCEWithLogitsLoss() # binary cross entropty loss function
    
    epochs = 750
    losses = [] # hold loss values
    test_accuracies = [] # hold test accuracies over time

    for epoch in range(epochs):
        # Forward pass
        predictions = model(RGB_train) # forward pass
        loss = loss_fn(predictions, Labels_train) # calculates loss for predictions vs actual labels

        # Backpropagation
        optimizer.zero_grad() # reset gradients for next epoch 
        loss.backward() # backpropagation
        optimizer.step() # update weights and biases
        scheduler.step() # update learning rate

        losses.append(loss.item()) # save loss values

        # Evaluate on test set every 10 epochs
        if (epoch + 1) % 10 == 0:
            model.eval() # set to evaluation mode
            with torch.no_grad():
                test_pred = model(RGB_test)
                test_probs = torch.sigmoid(test_pred)
                pred_binary = (test_probs > 0.5).float()
                accuracy = (pred_binary == Labels_test).float().mean().item()
                test_accuracies.append(accuracy)

            print(f"Epoch {epoch+1}: Loss = {loss.item():.4f}, Test Accuracy = {accuracy:.2%}")
            model.train() # back to training mode
    
    # Evaluate on test set after training
    model.eval() # set to evaluation mode
    with torch.no_grad():
        test_pred = model(RGB_test)
        test_loss = loss_fn(test_pred, Labels_test)
        print(f"\nTest Loss: {test_loss.item():.4f}")
        
        test_probs = torch.sigmoid(test_pred)
        
        # Calculate accuracy
        pred_binary = (test_probs > 0.5).float()
        accuracy = (pred_binary == Labels_test).float().mean().item()
        print(f"Test Accuracy: {accuracy:.2%}\n")
        
        # Print individual predictions
        border = "-" * 75
        print(border)
        print("Individual Test Predictions:")
        print(border)
        print(f"{'Index':<8} {'RGB Values':<25} {'Predicted':<12} {'Actual':<10} {'Confidence':<12} {'Correct'}")
        print(border)
        
        for i in range(len(RGB_test)):
            rgb_vals = RGB_test[i].numpy()
            predicted_class = int(pred_binary[i].item())
            actual_class = int(Labels_test[i].item())
            confidence = test_probs[i].item()
            
            # Confidence represents probability of class 1
            # If predicted class 0, confidence in that prediction is (1 - probability)
            if predicted_class == 0:
                confidence_in_prediction = 1 - confidence
            else:
                confidence_in_prediction = confidence
            
            is_correct = "Yes" if predicted_class == actual_class else "No"
            
            rgb_str = f"[{rgb_vals[0]:.3f}, {rgb_vals[1]:.3f}, {rgb_vals[2]:.3f}]"
            print(f"{i:<8} {rgb_str:<25} {predicted_class:<12} {actual_class:<10} {confidence_in_prediction:>6.2%}      {is_correct}")
        
        print(border)
        
    return model, losses, epochs, test_accuracies


def export_weights_for_esp32(model, filename="ColorSensorNN_weights.h"):
    """
    Use model weights as C arrays for ESP32 deployment
    """
    state = model.state_dict()
    
    with open(filename, 'w') as f:
        f.write("#ifndef MODEL_WEIGHTS_H\n")
        f.write("#define MODEL_WEIGHTS_H\n\n")
        
        # Layer 1: fc1 (3 -> 64)
        w1 = state['fc1.weight'].cpu().numpy() # Shape: [64, 3]
        b1 = state['fc1.bias'].cpu().numpy() # Shape: [64]
        
        f.write("// Layer 1: 3 inputs -> 64 outputs\n")
        f.write("const float W1[3][64] = {\n")
        for i in range(3):
            f.write("  {")
            f.write(", ".join(f"{w1[j][i]:.8f}f" for j in range(64)))
            f.write("},\n")
        f.write("};\n\n")
        
        f.write("const float b1[64] = {\n  ")
        f.write(", ".join(f"{b1[i]:.8f}f" for i in range(64)))
        f.write("\n};\n\n")
        
        # Layer 2: fc2 (64 -> 32)
        w2 = state['fc2.weight'].cpu().numpy() # Shape: [32, 64]
        b2 = state['fc2.bias'].cpu().numpy() # Shape: [32]
        
        f.write("// Layer 2: 64 inputs -> 32 outputs\n")
        f.write("const float W2[64][32] = {\n")
        for i in range(64):
            f.write("  {")
            f.write(", ".join(f"{w2[j][i]:.8f}f" for j in range(32)))
            f.write("},\n")
        f.write("};\n\n")
        
        f.write("const float b2[32] = {\n  ")
        f.write(", ".join(f"{b2[i]:.8f}f" for i in range(32)))
        f.write("\n};\n\n")
        
        # Layer 3: fc3 (32 -> 16)
        w3 = state['fc3.weight'].cpu().numpy() # Shape: [16, 32]
        b3 = state['fc3.bias'].cpu().numpy() # Shape: [16]
        
        f.write("// Layer 3: 32 inputs -> 16 outputs\n")
        f.write("const float W3[32][16] = {\n")
        for i in range(32):
            f.write("  {")
            f.write(", ".join(f"{w3[j][i]:.8f}f" for j in range(16)))
            f.write("},\n")
        f.write("};\n\n")
        
        f.write("const float b3[16] = {\n  ")
        f.write(", ".join(f"{b3[i]:.8f}f" for i in range(16)))
        f.write("\n};\n\n")
        
        # Layer 4: fc4 (16 -> 1)
        w4 = state['fc4.weight'].cpu().numpy() # Shape: [1, 16]
        b4 = state['fc4.bias'].cpu().numpy() # Shape: [1]
        
        f.write("// Layer 4: 16 inputs -> 1 output\n")
        f.write("const float W4[16] = {\n  ")
        f.write(", ".join(f"{w4[0][i]:.8f}f" for i in range(16)))
        f.write("\n};\n\n")
        
        f.write(f"const float b4 = {b4[0]:.8f}f;\n\n")
        
        f.write("#endif // MODEL_WEIGHTS_H\n")
    
    print(f"\n NN weights stored in {filename}")
    print(f"File size: {os.path.getsize(filename) / 1024:.2f} KB")

EXPORT_FOR_ESP32 = False # True for exporting weights to C arrays for ESP32

if __name__ == "__main__":
    model, losses, epochs, test_accuracies = train()

    if EXPORT_FOR_ESP32:
        name = input("Enter filename # or version for ESP32 weights (press Enter for default): ").strip()
        if name == "":
            name = "NN_weights.h" # default name if blank
        if not name.endswith(".h"):
            name += "_NN_weights.h"

        ARDUINO_DIR = os.path.join(SCRIPT_DIR, '..', 'Arduino')
        WEIGHTS_PATH = os.path.join(ARDUINO_DIR, name)
        export_weights_for_esp32(model, WEIGHTS_PATH) # export function call
        
    else:
        print("Weights not exported.")


    # Epochs for plotting
    epochs_range = np.arange(1, epochs+1)
    accuracy_range = np.arange(10, epochs+1, 10) # every 10 epochs

    plt.figure(figsize=(12,5))

    #Training Loss subplot
    plt.subplot(1,2,1)
    plt.plot(epochs_range, losses, label="Training Loss", color="blue", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training Loss Over Time")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    # Test Accuracy subplot
    plt.subplot(1,2,2)
    plt.plot(accuracy_range, test_accuracies, label="Test Accuracy", color="green",
            linewidth=2, marker='o')
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Test Accuracy Over Training")
    plt.ylim(0,1)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()

