# -*- coding: utf-8 -*-
"""copy of lab-1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/willparker123/applied-deep-learning-labs/blob/master/lab-1/lab-1.ipynb

# **Pytorch and Numpy**
"""

import torch
import numpy as np

array_np = np.array([[1, 2, 3],
                     [4, 5, 6]])
array_pytorch = torch.tensor([[1, 2, 3],
                              [4, 5, 6]])
x = torch.tensor([1, 2, 3], dtype=torch.float32)
y = torch.tensor([4, 5, 6], dtype=torch.float32)

print(array_np)
print(array_pytorch)
print(x.shape, x.dim())
print(f"squeezed x shape: {x.squeeze().shape}, unsqueezed x shape with added dim at dim=4: {x.unsqueeze(dim=4).shape}")
#elementwise; x+y, x/y, x*y
#returns tensor; torch.dot(x, y), x.mean(), x.std(), x.max(), x.argmax()
#to get item from tensor; torch.dot(x, y).item()
#to remove dimensions of size 1; x.squeeze()
#to add back dimensions of size 1 plus a new size-1 dimension at index 4; x.unsqueeze(dim=4)
print(torch.arange(0, 9).reshape((3, 3)))
print(x @ y)
print(torch.randn((2, 3)))
print(x.reshape((3, 1)))
#y = x.reshape(3, 1), y[0,0]=1 will change x

x = torch.arange(0, 100).reshape((2, 5, 10))
print(x)
y = x.reshape((10, 10))
y[0, 0] = 100
print(y)
print(x)  # notice that the data in x has changed too!

"""# **Fully-Connected Network**
## **Data Processing**
"""

# Commented out IPython magic to ensure Python compatibility.
import torch
import numpy as np
from sklearn import datasets
# %matplotlib inline
import seaborn as sns
import pandas as pd
from sklearn.model_selection import train_test_split

iris = datasets.load_iris()  # datasets are stored in a dictionary containing an array of features and targets
print(iris.keys())
print(f"Data (first 15): {iris['data'][:15]}, Features: {iris['feature_names']}")
print(f"Classes: {np.unique(iris['target'])}, Class Names: {iris['target_names']}")

#show pairplot of features
features_df = pd.DataFrame(
    iris['data'],
    columns=iris['feature_names']
)
features_df['label'] = iris['target_names'][iris['target']]
sns.pairplot(features_df, hue='label')

#normalisation
preprocessed_features = (iris['data'] - iris['data'].mean(axis=0)) / iris['data'].std(axis=0)

#shuffling - train/test set
labels = iris['target']
# train_test_split takes care of the shuffling and splitting process
train_features, test_features, train_labels, test_labels = train_test_split(preprocessed_features, labels, test_size=1/3)
#convert to tensors
features = {
    'train': torch.tensor(train_features, dtype=torch.float32),
    'test': torch.tensor(test_features, dtype=torch.float32),
}
labels = {
    'train': torch.tensor(train_labels, dtype=torch.long),
    'test': torch.tensor(test_labels, dtype=torch.long),
}

"""## **MLP**"""

from torch import nn
from torch.nn import functional as F
from typing import Callable
from torch import optim

class MLP(nn.Module):
    def __init__(self,
                 input_size: int,
                 hidden_layer_size: int,
                 output_size: int,
                 activation_fn: Callable[[torch.Tensor], torch.Tensor] = F.relu):
        super().__init__()
        self.l1 = nn.Linear(input_size, hidden_layer_size)
        self.l2 = nn.Linear(hidden_layer_size, output_size)
        self.activation_fn = activation_fn
        
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        x = self.l1(inputs)
        x = self.activation_fn(x)
        x = self.l2(x)
        return x

feature_count = 4
hidden_layer_size = 100
class_count = 3
model = MLP(feature_count, hidden_layer_size, class_count)

#compute logits - values for each class and sample
#logits = model.forward(features['train'])
#logits.shape

#initialise cross-entropy loss function; combines cross-entropy and softmax
loss_f = nn.CrossEntropyLoss()

#compute loss
#loss = loss_f(logits, labels['train'])
##use loss by backpropagating through network to get gradients
#loss.backward()

def accuracy(probs: torch.FloatTensor, targets: torch.LongTensor) -> float:
    """
    Args:
        probs: A float32 tensor of shape ``(batch_size, class_count)`` where each value 
            at index ``i`` in a row represents the score of class ``i``.
        targets: A long tensor of shape ``(batch_size,)`` containing the batch examples'
            labels.
    """
    count = 0
    amx = probs.argmax(dim=1)
    for x in range(len(probs)):
      if targets[x]==amx[x]:
        count+=1
    return count / targets.shape[0]
    ## First work out which class has been predicted for each data sample. Hint: use argmax
    ## Second count how many of these are correctly predicted
    ## Finally return the accuracy, i.e. the percentage of samples correctly predicted

def check_accuracy(probs: torch.FloatTensor,
                   labels: torch.LongTensor,
                   expected_accuracy: float):
    actual_accuracy = float(accuracy(probs, labels))
    assert actual_accuracy == expected_accuracy, f"Expected accuracy to be {expected_accuracy} but was {actual_accuracy}"

check_accuracy(torch.tensor([[0, 1],
                             [0, 1],
                             [0, 1],
                             [0, 1],
                             [0, 1]]),
               torch.ones(5, dtype=torch.long),
               1.0)
check_accuracy(torch.tensor([[1, 0],
                             [0, 1],
                             [0, 1],
                             [0, 1],
                             [0, 1]]),
               torch.ones(5, dtype=torch.long),
               0.8)
check_accuracy(torch.tensor([[1, 0],
                             [1, 0],
                             [0, 1],
                             [0, 1],
                             [0, 1]]),
               torch.ones(5, dtype=torch.long),
               0.6)
check_accuracy(torch.tensor([[1, 0],
                             [1, 0],
                             [1, 0],
                             [1, 0],
                             [1, 0]]),
               torch.ones(5, dtype=torch.long),
               0.0)
print("All test cases passed")



# The optimizer we'll use to update the model parameters
optimizer = optim.SGD(model.parameters(), lr=0.05)
# Now we define the loss function.
criterion = loss_f
# Now we iterate over the dataset a number of times. Each iteration of the entire dataset 
# is called an epoch.
for epoch in range(0, 100):
    # We compute the forward pass of the network
    _logits = model.forward(features['train'])
    # Then the value of loss function 
    _loss = criterion(_logits,  labels['train'])
    # How well the network does on the batch is an indication of how well training is 
    # progressing
    print("epoch: {} train accuracy: {:2.2f}, loss: {:5.5f}".format(
        epoch,
        accuracy(_logits, labels['train']) * 100,
        _loss.item()
    ))
    # Now we compute the backward pass, which populates the `.grad` attributes of the parameters
    _loss.backward()
    # Now we update the model parameters using those gradients
    optimizer.step()
    # Now we need to zero out the `.grad` buffers as otherwise on the next backward pass we'll add the 
    # new gradients to the old ones.
    optimizer.zero_grad()
    
# Finally we can test our model on the test set and get an unbiased estimate of its performance.    
_logits = model.forward(features['test'])    
test_accuracy = accuracy(_logits, labels['test']) * 100
print("test accuracy: {:2.2f}".format(test_accuracy))

