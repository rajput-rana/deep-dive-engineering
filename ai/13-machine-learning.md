# 🧠 Machine Learning Fundamentals

<div align="center">

**Master Machine Learning: Deep learning, TensorFlow, PyTorch, and production ML systems**

[![ML](https://img.shields.io/badge/ML-Machine%20Learning-blue?style=for-the-badge)](./)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-Google-green?style=for-the-badge)](./)
[![PyTorch](https://img.shields.io/badge/PyTorch-Meta-orange?style=for-the-badge)](./)

*Comprehensive guide to building production ML systems with TensorFlow and PyTorch*

</div>

---

## 🎯 What is Machine Learning?

<div align="center">

**Machine Learning (ML) is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.**

### Core Concept

```
Data → Learning Algorithm → Model → Predictions/Decisions
```

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **📊 Data-Driven** | Learns patterns from data |
| **🧠 Self-Improving** | Gets better with more data |
| **🎯 Task-Specific** | Trained for specific problems |
| **🔄 Iterative** | Continuous learning and refinement |
| **📈 Generalizable** | Applies learned patterns to new data |

**Mental Model:** Think of ML as teaching a computer to recognize patterns by showing it many examples, rather than programming every rule explicitly.

</div>

---

## 🏗️ ML Fundamentals

<div align="center">

### Types of Machine Learning

| Type | Description | Use Case | Example |
|:---:|:---:|:---:|:---:|
| **Supervised Learning** | Learn from labeled data | Classification, regression | Email spam detection, house price prediction |
| **Unsupervised Learning** | Find patterns in unlabeled data | Clustering, dimensionality reduction | Customer segmentation, anomaly detection |
| **Reinforcement Learning** | Learn through rewards/penalties | Game playing, robotics | AlphaGo, autonomous vehicles |
| **Semi-Supervised Learning** | Mix of labeled and unlabeled data | When labeling is expensive | Medical imaging, fraud detection |
| **Self-Supervised Learning** | Generate labels from data | Pre-training, representation learning | Language models, vision transformers |

---

### Core ML Concepts

**1. Data Preprocessing**

- **Normalization:** Scale features to similar ranges
- **Encoding:** Convert categorical to numerical
- **Handling Missing Values:** Imputation, deletion
- **Feature Engineering:** Create meaningful features
- **Train/Val/Test Split:** Separate data for training and evaluation

**2. Model Training**

- **Loss Function:** Measures prediction error
- **Optimization:** Minimize loss (gradient descent)
- **Epochs:** Complete passes through training data
- **Batch Size:** Number of samples per update
- **Learning Rate:** Step size for optimization

**3. Evaluation Metrics**

| Task Type | Metrics |
|:---:|:---:|
| **Classification** | Accuracy, Precision, Recall, F1-score, AUC-ROC |
| **Regression** | MSE, RMSE, MAE, R² |
| **Clustering** | Silhouette score, Davies-Bouldin index |
| **Ranking** | NDCG, MAP, MRR |

**4. Overfitting & Regularization**

- **Overfitting:** Model memorizes training data, poor generalization
- **Underfitting:** Model too simple, can't learn patterns
- **Regularization:** Techniques to prevent overfitting
  - L1/L2 regularization
  - Dropout
  - Early stopping
  - Data augmentation

</div>

---

## 🧠 Deep Learning Fundamentals

<div align="center">

### What is Deep Learning?

**Deep Learning uses neural networks with multiple layers to learn hierarchical representations of data.**

### Neural Network Basics

**Perceptron (Single Neuron):**

```
Inputs (x₁, x₂, ..., xₙ) → Weights (w₁, w₂, ..., wₙ) → Sum → Activation Function → Output
```

**Multi-Layer Perceptron (MLP):**

```
Input Layer → Hidden Layer 1 → Hidden Layer 2 → ... → Output Layer
```

### Key Components

| Component | Description | Purpose |
|:---:|:---:|:---:|
| **Neurons** | Basic processing units | Compute weighted sums |
| **Weights** | Learnable parameters | Store learned patterns |
| **Biases** | Offset values | Adjust activation threshold |
| **Activation Functions** | Non-linear transformations | Enable complex patterns |
| **Layers** | Groups of neurons | Hierarchical feature learning |

---

### Common Activation Functions

| Function | Formula | Use Case |
|:---:|:---:|:---:|
| **ReLU** | f(x) = max(0, x) | Hidden layers (most common) |
| **Sigmoid** | f(x) = 1/(1+e⁻ˣ) | Binary classification output |
| **Tanh** | f(x) = tanh(x) | Hidden layers (centered) |
| **Softmax** | f(x) = eˣᵢ/Σeˣⱼ | Multi-class classification |
| **Leaky ReLU** | f(x) = max(αx, x) | Prevents dead neurons |

---

### Deep Learning Architectures

**1. Feedforward Neural Networks (FNN)**

- Simplest architecture
- Information flows forward only
- Good for: Classification, regression

**2. Convolutional Neural Networks (CNN)**

- Specialized for images/grid data
- Uses convolutional layers
- Good for: Image classification, object detection, computer vision

**3. Recurrent Neural Networks (RNN)**

- Handles sequential data
- Has memory of previous inputs
- Good for: Text, time series, speech

**4. Long Short-Term Memory (LSTM)**

- Advanced RNN variant
- Better at long-term dependencies
- Good for: Language modeling, translation

**5. Transformers**

- Attention-based architecture
- Parallel processing
- Good for: NLP, LLMs, vision transformers

**6. Generative Adversarial Networks (GAN)**

- Two networks competing
- Generator vs Discriminator
- Good for: Image generation, data augmentation

**7. Autoencoders**

- Encoder-decoder architecture
- Unsupervised learning
- Good for: Dimensionality reduction, anomaly detection

</div>

---

## 🔥 TensorFlow Deep Dive

<div align="center">

### What is TensorFlow?

**TensorFlow is an open-source ML framework developed by Google, designed for building and deploying ML models at scale.**

### Key Features

| Feature | Description |
|:---:|:---:|
| **🔧 Flexible** | Eager execution and graph mode |
| **📈 Scalable** | Distributed training, TPU support |
| **🚀 Production-Ready** | TensorFlow Serving, TF Lite |
| **🌐 Cross-Platform** | CPU, GPU, TPU, mobile, edge |
| **📚 Ecosystem** | Keras, TensorBoard, TF Hub |

---

### TensorFlow Architecture

**1. Core Components**

- **Tensors:** Multi-dimensional arrays (like NumPy arrays)
- **Graphs:** Computational graph representation
- **Sessions:** Execute graphs (TF 1.x) or eager execution (TF 2.x)
- **Variables:** Trainable parameters
- **Operations:** Mathematical operations on tensors

**2. TensorFlow 2.x vs 1.x**

| Feature | TF 1.x | TF 2.x |
|:---:|:---:|:---:|
| **Execution** | Graph mode (default) | Eager execution (default) |
| **API** | Lower-level | High-level (Keras integrated) |
| **Learning Curve** | Steeper | Easier |
| **Performance** | Optimized graphs | Eager + graph via @tf.function |

---

### TensorFlow Basics

**1. Installation**

```bash
# CPU version
pip install tensorflow

# GPU version (requires CUDA)
pip install tensorflow-gpu

# Latest version
pip install tensorflow==2.15.0
```

**2. Basic Operations**

```python
import tensorflow as tf
import numpy as np

# Create tensors
a = tf.constant([[1, 2], [3, 4]])
b = tf.constant([[5, 6], [7, 8]])

# Operations
c = tf.add(a, b)  # Element-wise addition
d = tf.matmul(a, b)  # Matrix multiplication
e = tf.reduce_sum(a)  # Sum all elements

# Eager execution (TF 2.x)
print(c.numpy())  # Convert to NumPy array
```

**3. Variables and Gradients**

```python
# Variables (trainable parameters)
w = tf.Variable([[1.0, 2.0], [3.0, 4.0]])
b = tf.Variable([0.5, 0.5])

# Automatic differentiation
with tf.GradientTape() as tape:
    y = tf.matmul(x, w) + b
    loss = tf.reduce_mean(y**2)

# Compute gradients
gradients = tape.gradient(loss, [w, b])
```

---

### Building Models with Keras (TensorFlow)

**1. Sequential API (Simple Models)**

```python
from tensorflow import keras
from tensorflow.keras import layers

# Sequential model
model = keras.Sequential([
    layers.Dense(128, activation='relu', input_shape=(784,)),
    layers.Dropout(0.2),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# Compile model
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Train model
model.fit(x_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

# Evaluate
test_loss, test_acc = model.evaluate(x_test, y_test)

# Predict
predictions = model.predict(x_test)
```

**2. Functional API (Complex Models)**

```python
from tensorflow import keras
from tensorflow.keras import layers

# Input layer
inputs = keras.Input(shape=(784,))

# Hidden layers
x = layers.Dense(128, activation='relu')(inputs)
x = layers.Dropout(0.2)(x)
x = layers.Dense(64, activation='relu')(x)

# Output layer
outputs = layers.Dense(10, activation='softmax')(x)

# Create model
model = keras.Model(inputs=inputs, outputs=outputs)

# Compile and train (same as Sequential)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=10)
```

**3. Model Subclassing (Custom Models)**

```python
from tensorflow import keras
from tensorflow.keras import layers

class MyModel(keras.Model):
    def __init__(self):
        super(MyModel, self).__init__()
        self.dense1 = layers.Dense(128, activation='relu')
        self.dropout = layers.Dropout(0.2)
        self.dense2 = layers.Dense(64, activation='relu')
        self.dense3 = layers.Dense(10, activation='softmax')
    
    def call(self, inputs, training=False):
        x = self.dense1(inputs)
        x = self.dropout(x, training=training)
        x = self.dense2(x)
        return self.dense3(x)

# Create and use model
model = MyModel()
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=10)
```

---

### CNN with TensorFlow

```python
from tensorflow import keras
from tensorflow.keras import layers

# CNN for image classification
model = keras.Sequential([
    # Convolutional layers
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    
    # Flatten and dense layers
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(10, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Data preprocessing for images
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

model.fit(datagen.flow(x_train, y_train, batch_size=32), epochs=10)
```

---

### RNN/LSTM with TensorFlow

```python
from tensorflow import keras
from tensorflow.keras import layers

# LSTM for sequence modeling
model = keras.Sequential([
    layers.LSTM(128, return_sequences=True, input_shape=(timesteps, features)),
    layers.Dropout(0.2),
    layers.LSTM(64, return_sequences=False),
    layers.Dropout(0.2),
    layers.Dense(50, activation='relu'),
    layers.Dense(1)  # Regression output
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.fit(x_train, y_train, epochs=10, batch_size=32)
```

---

### Transfer Learning with TensorFlow

```python
from tensorflow import keras
from tensorflow.keras.applications import ResNet50
from tensorflow.keras import layers

# Load pre-trained model
base_model = ResNet50(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze base model
base_model.trainable = False

# Add custom classifier
model = keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Fine-tune (unfreeze some layers)
base_model.trainable = True
fine_tune_at = 100
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(train_dataset, epochs=10, validation_data=val_dataset)
```

---

### Custom Training Loop (Advanced)

```python
import tensorflow as tf
from tensorflow import keras

# Custom training loop for more control
optimizer = keras.optimizers.Adam(learning_rate=0.001)
loss_fn = keras.losses.SparseCategoricalCrossentropy()

@tf.function  # Compile to graph for performance
def train_step(x, y):
    with tf.GradientTape() as tape:
        # Forward pass
        predictions = model(x, training=True)
        # Compute loss
        loss = loss_fn(y, predictions)
    
    # Backward pass
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    
    return loss

# Training loop
for epoch in range(epochs):
    epoch_loss = 0
    for batch_idx, (x_batch, y_batch) in enumerate(train_dataset):
        loss = train_step(x_batch, y_batch)
        epoch_loss += loss
    
    print(f"Epoch {epoch+1}, Loss: {epoch_loss / len(train_dataset)}")
```

---

### TensorFlow Data Pipeline

```python
import tensorflow as tf

# Create dataset from arrays
dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))

# Preprocessing
dataset = dataset.map(lambda x, y: (tf.cast(x, tf.float32) / 255.0, y))

# Shuffle and batch
dataset = dataset.shuffle(buffer_size=10000)
dataset = dataset.batch(32)

# Prefetch for performance
dataset = dataset.prefetch(tf.data.AUTOTUNE)

# Use in training
model.fit(dataset, epochs=10)
```

---

### TensorFlow Serving (Production)

```python
# Save model in SavedModel format
model.save('saved_model/my_model')

# Or use tf.saved_model.save
tf.saved_model.save(model, 'saved_model/my_model')

# Load and serve
imported = tf.saved_model.load('saved_model/my_model')
predictions = imported.signatures['serving_default'](inputs)
```

**TensorFlow Serving (Docker):**

```bash
# Pull TensorFlow Serving image
docker pull tensorflow/serving

# Run serving container
docker run -p 8501:8501 \
  --mount type=bind,source=/path/to/saved_model,target=/models/my_model \
  -e MODEL_NAME=my_model \
  tensorflow/serving
```

**REST API:**

```python
import requests
import json

# Prepare data
data = {"instances": x_test[:3].tolist()}

# Make prediction request
response = requests.post(
    'http://localhost:8501/v1/models/my_model:predict',
    data=json.dumps(data)
)

predictions = response.json()['predictions']
```

---

### TensorFlow Lite (Mobile/Edge)

```python
# Convert to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_saved_model('saved_model/my_model')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save TFLite model
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

# Load and run inference
interpreter = tf.lite.Interpreter(model_path='model.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])
```

---

### TensorBoard (Visualization)

```python
from tensorflow import keras
from tensorflow.keras.callbacks import TensorBoard
import datetime

# Create TensorBoard callback
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)

# Use in training
model.fit(
    x_train, y_train,
    epochs=10,
    validation_data=(x_test, y_test),
    callbacks=[tensorboard_callback]
)

# View: tensorboard --logdir=logs/fit
```

---

### Distributed Training with TensorFlow

**1. MirroredStrategy (Single Machine, Multiple GPUs)**

```python
import tensorflow as tf

# Create strategy
strategy = tf.distribute.MirroredStrategy()

# Build model within strategy scope
with strategy.scope():
    model = keras.Sequential([
        layers.Dense(128, activation='relu'),
        layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Train (automatically distributed)
model.fit(x_train, y_train, epochs=10)
```

**2. MultiWorkerMirroredStrategy (Multiple Machines)**

```python
import tensorflow as tf

# Configure cluster
os.environ['TF_CONFIG'] = json.dumps({
    'cluster': {
        'worker': ['localhost:12345', 'localhost:12346']
    },
    'task': {'type': 'worker', 'index': 0}
})

# Create strategy
strategy = tf.distribute.MultiWorkerMirroredStrategy()

# Build and train (same as MirroredStrategy)
with strategy.scope():
    model = create_model()
    model.compile(...)
    model.fit(...)
```

**3. TPU Strategy**

```python
import tensorflow as tf

# Initialize TPU
resolver = tf.distribute.cluster_resolver.TPUClusterResolver(tpu='')
tf.config.experimental_connect_to_cluster(resolver)
tf.tpu.experimental.initialize_tpu_system(resolver)

# Create TPU strategy
strategy = tf.distribute.TPUStrategy(resolver)

# Build and train
with strategy.scope():
    model = create_model()
    model.compile(...)
    model.fit(...)
```

---

### TensorFlow Hub (Pre-trained Models)

```python
import tensorflow_hub as hub

# Load pre-trained model from TF Hub
embedding_layer = hub.KerasLayer(
    "https://tfhub.dev/google/nnlm-en-dim128/2",
    input_shape=[],
    dtype=tf.string,
    trainable=True
)

# Use in model
model = keras.Sequential([
    embedding_layer,
    layers.Dense(64, activation='relu'),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy')
model.fit(text_data, labels, epochs=10)
```

</div>

---

## 🔥 PyTorch Deep Dive

<div align="center">

### What is PyTorch?

**PyTorch is an open-source ML framework developed by Meta (Facebook), known for its Pythonic interface and dynamic computation graphs.**

### Key Features

| Feature | Description |
|:---:|:---:|
| **🐍 Pythonic** | Natural Python integration |
| **⚡ Dynamic Graphs** | Define-by-run execution |
| **🔬 Research-Friendly** | Easy experimentation |
| **🚀 Production** | TorchScript, TorchServe |
| **📚 Ecosystem** | torchvision, torchaudio, transformers |

---

### PyTorch Architecture

**1. Core Components**

- **Tensors:** Multi-dimensional arrays (like NumPy)
- **Autograd:** Automatic differentiation
- **nn.Module:** Base class for neural networks
- **Optimizers:** Optimization algorithms
- **DataLoader:** Efficient data loading

**2. PyTorch Philosophy**

- **Imperative:** Code executes as written
- **Dynamic:** Graph built on-the-fly
- **Pythonic:** Feels like NumPy with GPU support

---

### PyTorch Basics

**1. Installation**

```bash
# CPU version
pip install torch torchvision torchaudio

# GPU version (CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Specific version
pip install torch==2.1.0 torchvision==0.16.0
```

**2. Basic Operations**

```python
import torch
import numpy as np

# Create tensors
a = torch.tensor([[1, 2], [3, 4]], dtype=torch.float32)
b = torch.tensor([[5, 6], [7, 8]], dtype=torch.float32)

# Operations (similar to NumPy)
c = a + b  # Element-wise addition
d = torch.matmul(a, b)  # Matrix multiplication
e = torch.sum(a)  # Sum all elements

# NumPy interoperability
numpy_array = a.numpy()  # Convert to NumPy
torch_tensor = torch.from_numpy(numpy_array)  # Convert from NumPy

# GPU operations
if torch.cuda.is_available():
    a_gpu = a.cuda()  # Move to GPU
    b_gpu = b.cuda()
    c_gpu = a_gpu + b_gpu
    c_cpu = c_gpu.cpu()  # Move back to CPU
```

**3. Automatic Differentiation**

```python
import torch

# Create tensor with gradient tracking
x = torch.tensor([2.0], requires_grad=True)

# Define function
y = x**2 + 3*x + 1

# Compute gradient
y.backward()

# Access gradient
print(x.grad)  # dy/dx = 2x + 3 = 7.0
```

---

### Building Models with PyTorch

**1. Using nn.Module**

```python
import torch
import torch.nn as nn
import torch.optim as optim

# Define model
class SimpleNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# Create model instance
model = SimpleNet(input_size=784, hidden_size=128, num_classes=10)

# Define loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
model.train()
for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        # Forward pass
        output = model(data)
        loss = criterion(output, target)
        
        # Backward pass
        optimizer.zero_grad()  # Clear gradients
        loss.backward()  # Compute gradients
        optimizer.step()  # Update weights
        
        if batch_idx % 100 == 0:
            print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item()}')

# Evaluation
model.eval()
with torch.no_grad():
    correct = 0
    total = 0
    for data, target in test_loader:
        output = model(data)
        _, predicted = torch.max(output.data, 1)
        total += target.size(0)
        correct += (predicted == target).sum().item()
    
    print(f'Accuracy: {100 * correct / total}%')
```

**2. Sequential API (Simpler Models)**

```python
import torch.nn as nn

# Sequential model
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 10)
)

# Same training loop as above
```

---

### CNN with PyTorch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(64 * 7 * 7, 64)
        self.fc2 = nn.Linear(64, 10)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        # Convolutional layers
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = F.relu(self.conv3(x))
        
        # Flatten
        x = x.view(-1, 64 * 7 * 7)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

model = CNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training (same pattern as before)
```

---

### RNN/LSTM with PyTorch

```python
import torch
import torch.nn as nn

class LSTMNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(LSTMNet, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size, 
            hidden_size, 
            num_layers, 
            batch_first=True,
            dropout=0.2
        )
        
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Decode hidden state of last time step
        out = self.fc(out[:, -1, :])
        return out

model = LSTMNet(input_size=28, hidden_size=128, num_layers=2, num_classes=10)
```

---

### Transfer Learning with PyTorch

```python
import torch
import torchvision.models as models
import torch.nn as nn

# Load pre-trained model
model = models.resnet50(pretrained=True)

# Freeze all parameters
for param in model.parameters():
    param.requires_grad = False

# Replace classifier
num_features = model.fc.in_features
model.fc = nn.Sequential(
    nn.Linear(num_features, 128),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(128, num_classes)
)

# Only train the classifier
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)

# Fine-tuning: Unfreeze some layers
for param in model.layer4.parameters():
    param.requires_grad = True

optimizer = optim.Adam([
    {'params': model.fc.parameters()},
    {'params': model.layer4.parameters(), 'lr': 0.0001}
], lr=0.001)
```

---

### Data Loading with PyTorch

```python
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, datasets

# Custom Dataset
class CustomDataset(Dataset):
    def __init__(self, data, labels, transform=None):
        self.data = data
        self.labels = labels
        self.transform = transform
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = self.data[idx]
        label = self.labels[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample, label

# Data transformations
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# Create dataset
train_dataset = CustomDataset(x_train, y_train, transform=transform)

# Create DataLoader
train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True,
    num_workers=4,
    pin_memory=True  # Faster GPU transfer
)

# Use in training loop
for batch_idx, (data, target) in enumerate(train_loader):
    # Training code
    pass
```

---

### PyTorch Lightning (High-Level Framework)

```python
import pytorch_lightning as pl
import torch.nn as nn
import torch.optim as optim

class LitModel(pl.LightningModule):
    def __init__(self, input_size=784, hidden_size=128, num_classes=10):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.loss_fn = nn.CrossEntropyLoss()
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        self.log('train_loss', loss)
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        acc = (y_hat.argmax(dim=1) == y).float().mean()
        self.log('val_loss', loss)
        self.log('val_acc', acc)
        return loss
    
    def configure_optimizers(self):
        return optim.Adam(self.parameters(), lr=0.001)

# Create model
model = LitModel()

# Create trainer
trainer = pl.Trainer(max_epochs=10, gpus=1)

# Train
trainer.fit(model, train_loader, val_loader)
```

---

### Distributed Training with PyTorch

**1. DataParallel (Single Machine, Multiple GPUs)**

```python
import torch
import torch.nn as nn

# Wrap model with DataParallel
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)

model = model.cuda()

# Training (same as before, automatically parallelized)
```

**2. DistributedDataParallel (Multiple GPUs/Machines)**

```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP

def setup(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()

def train(rank, world_size):
    setup(rank, world_size)
    
    # Create model and move to GPU
    model = SimpleNet().to(rank)
    model = DDP(model, device_ids=[rank])
    
    # Create optimizer
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    for epoch in range(10):
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(rank), target.to(rank)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
    
    cleanup()

# Launch training
if __name__ == "__main__":
    world_size = 4  # Number of GPUs
    mp.spawn(train, args=(world_size,), nprocs=world_size, join=True)
```

---

### Model Saving and Loading

```python
import torch

# Save entire model
torch.save(model, 'model.pth')
model = torch.load('model.pth')

# Save state dict (recommended)
torch.save(model.state_dict(), 'model_state.pth')
model.load_state_dict(torch.load('model_state.pth'))

# Save checkpoint (with optimizer, epoch, etc.)
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}
torch.save(checkpoint, 'checkpoint.pth')

# Load checkpoint
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']
```

---

### TorchScript (Production Deployment)

```python
import torch

# Trace model (for fixed input shapes)
example_input = torch.rand(1, 3, 224, 224)
traced_model = torch.jit.trace(model, example_input)
traced_model.save('traced_model.pt')

# Script model (for dynamic shapes)
scripted_model = torch.jit.script(model)
scripted_model.save('scripted_model.pt')

# Load and run
loaded_model = torch.jit.load('scripted_model.pt')
output = loaded_model(example_input)
```

---

### PyTorch Hub (Pre-trained Models)

```python
import torch

# Load pre-trained model from PyTorch Hub
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
model.eval()

# Use for inference
output = model(input_tensor)
```

</div>

---

## ⚖️ TensorFlow vs PyTorch Comparison

<div align="center">

### Feature Comparison

| Feature | TensorFlow | PyTorch |
|:---:|:---:|:---:|
| **Ease of Use** | Moderate (TF 2.x improved) | Very Easy (Pythonic) |
| **Learning Curve** | Steeper | Gentler |
| **Graph Mode** | Static (TF 1.x) / Dynamic (TF 2.x) | Dynamic (always) |
| **Debugging** | More complex | Easier (Python debugger) |
| **Production** | Excellent (TF Serving, TF Lite) | Good (TorchScript, TorchServe) |
| **Research** | Good | Excellent (preferred) |
| **Mobile** | TF Lite (mature) | PyTorch Mobile (growing) |
| **Ecosystem** | Large (Keras, TF Hub) | Large (torchvision, transformers) |
| **Community** | Large (Google-backed) | Large (Meta-backed) |
| **Industry Adoption** | More in production | More in research |

---

### When to Use TensorFlow

✅ **Production Deployment**
- Need TF Serving, TF Lite
- Enterprise ML pipelines
- Mobile/edge deployment

✅ **Large-Scale Systems**
- Distributed training at scale
- TPU support needed
- Production ML infrastructure

✅ **Keras Integration**
- Prefer high-level Keras API
- Quick prototyping with Keras
- Transfer learning with TF Hub

---

### When to Use PyTorch

✅ **Research & Experimentation**
- Rapid prototyping
- Dynamic computation graphs
- Easy debugging

✅ **Academic/Research**
- Most research papers use PyTorch
- Easier to implement new architectures
- Better for experimentation

✅ **Python-First Development**
- Prefer Pythonic interface
- Want NumPy-like experience
- Dynamic graph benefits

---

### Code Comparison Example

**Simple Neural Network:**

**TensorFlow:**
```python
import tensorflow as tf
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    keras.layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
model.fit(x_train, y_train, epochs=10)
```

**PyTorch:**
```python
import torch
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)

optimizer = torch.optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()

for epoch in range(10):
    for x, y in train_loader:
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
```

**Key Differences:**
- TensorFlow: Declarative, high-level API
- PyTorch: Imperative, more control

</div>

---

## 🏗️ ML System Design & Production

<div align="center">

### ML Production Pipeline

```
Data Collection → Data Validation → Feature Engineering → Model Training → 
Model Validation → Model Deployment → Monitoring → Retraining
```

---

### Key Components

**1. Data Pipeline**

- **Data Collection:** Gather training and inference data
- **Data Validation:** Check data quality, schema validation
- **Feature Store:** Centralized feature management
- **Data Versioning:** Track data versions (DVC, MLflow)

**2. Model Training**

- **Experiment Tracking:** Log experiments (MLflow, Weights & Biases)
- **Hyperparameter Tuning:** AutoML, grid search, Bayesian optimization
- **Model Versioning:** Track model versions and artifacts
- **Reproducibility:** Ensure consistent results

**3. Model Deployment**

- **Model Serving:** REST API, gRPC, batch inference
- **A/B Testing:** Compare model versions
- **Canary Deployment:** Gradual rollout
- **Edge Deployment:** Mobile, IoT devices

**4. Monitoring**

- **Model Performance:** Accuracy, latency, throughput
- **Data Drift:** Detect distribution shifts
- **Model Drift:** Performance degradation over time
- **Infrastructure:** Resource usage, errors

---

### MLflow (Experiment Tracking)

**TensorFlow + MLflow:**

```python
import mlflow
import mlflow.tensorflow

# Start MLflow run
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("batch_size", 32)
    
    # Train model
    model = create_model()
    history = model.fit(x_train, y_train, epochs=10)
    
    # Log metrics
    for epoch, acc in enumerate(history.history['accuracy']):
        mlflow.log_metric("accuracy", acc, step=epoch)
    
    # Log model
    mlflow.tensorflow.log_model(model, "model")
```

**PyTorch + MLflow:**

```python
import mlflow
import mlflow.pytorch

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.001)
    
    model = create_model()
    train_model(model)
    
    mlflow.log_metric("accuracy", accuracy)
    mlflow.pytorch.log_model(model, "model")
```

---

### Model Serving Patterns

**1. REST API (TensorFlow Serving)**

```python
# Client code
import requests
import json

data = {"instances": x_test[:3].tolist()}
response = requests.post(
    'http://localhost:8501/v1/models/my_model:predict',
    json=data
)
predictions = response.json()['predictions']
```

**2. gRPC (Faster, Lower Latency)**

```python
import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

channel = grpc.insecure_channel('localhost:8500')
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

request = predict_pb2.PredictRequest()
request.model_spec.name = 'my_model'
request.model_spec.signature_name = 'serving_default'
request.inputs['inputs'].CopyFrom(tf.make_tensor_proto(x_test))

result = stub.Predict(request)
```

**3. Batch Inference**

```python
# Process large datasets
def batch_predict(model, data_loader, batch_size=1000):
    predictions = []
    for batch in data_loader:
        batch_preds = model.predict(batch)
        predictions.extend(batch_preds)
    return predictions
```

---

### Model Optimization

**1. Quantization (Reduce Precision)**

**TensorFlow:**
```python
# Post-training quantization
converter = tf.lite.TFLiteConverter.from_saved_model('saved_model')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

**PyTorch:**
```python
import torch.quantization

# Quantize model
model_quantized = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

**2. Pruning (Remove Unnecessary Weights)**

**TensorFlow:**
```python
import tensorflow_model_optimization as tfmot

# Prune model
pruning_params = {
    'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=0.50,
        final_sparsity=0.90,
        begin_step=0,
        end_step=1000
    )
}

model = tfmot.sparsity.keras.prune_low_magnitude(model, **pruning_params)
```

**PyTorch:**
```python
import torch.nn.utils.prune as prune

# Prune linear layers
for module in model.modules():
    if isinstance(module, torch.nn.Linear):
        prune.l1_unstructured(module, name='weight', amount=0.2)
```

**3. Knowledge Distillation**

```python
# Train smaller student model from larger teacher model
def distillation_loss(student_logits, teacher_logits, labels, temperature=3.0):
    # Soft targets from teacher
    soft_targets = F.softmax(teacher_logits / temperature, dim=1)
    soft_prob = F.log_softmax(student_logits / temperature, dim=1)
    
    # Hard targets
    hard_loss = F.cross_entropy(student_logits, labels)
    
    # Soft loss
    soft_loss = F.kl_div(soft_prob, soft_targets, reduction='batchmean')
    
    return hard_loss + (temperature ** 2) * soft_loss
```

---

### Monitoring & Observability

**1. Model Performance Monitoring**

```python
# Track predictions and actuals
def log_prediction(model_name, input_data, prediction, actual=None):
    log_entry = {
        'model': model_name,
        'timestamp': datetime.now(),
        'input': input_data,
        'prediction': prediction,
        'actual': actual
    }
    # Send to monitoring system (e.g., Prometheus, DataDog)
    monitoring_client.log(log_entry)
```

**2. Data Drift Detection**

```python
from alibi_detect import KSDrift

# Initialize drift detector
drift_detector = KSDrift(x_train, p_val=0.05)

# Check for drift
prediction = drift_detector.predict(x_test)
if prediction['data']['is_drift']:
    print("Data drift detected!")
    # Trigger retraining
```

**3. Model Performance Degradation**

```python
# Monitor accuracy over time
def check_model_performance(current_accuracy, baseline_accuracy, threshold=0.05):
    if current_accuracy < baseline_accuracy - threshold:
        print("Model performance degraded!")
        # Alert and trigger retraining
        return True
    return False
```

</div>

---

## 🎯 Real-World ML Use Cases

<div align="center">

### Industry Applications

| Industry | Use Case | Framework | Scale |
|:---:|:---:|:---:|:---:|
| **Computer Vision** | Image classification, object detection | TensorFlow, PyTorch | Millions of images |
| **NLP** | Language models, translation, sentiment | PyTorch (Transformers) | Billions of tokens |
| **Recommendation** | Product recommendations, search | TensorFlow, PyTorch | Millions of users |
| **Healthcare** | Medical imaging, drug discovery | PyTorch | Critical accuracy |
| **Autonomous Vehicles** | Object detection, path planning | TensorFlow, PyTorch | Real-time, safety-critical |
| **Finance** | Fraud detection, trading algorithms | TensorFlow, PyTorch | Low latency required |
| **E-commerce** | Search, personalization | TensorFlow | High throughput |

---

### Example: Image Classification Pipeline

**TensorFlow:**

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Data augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

# Load data
train_generator = train_datagen.flow_from_directory(
    'data/train',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# Transfer learning
base_model = ResNet50(weights='imagenet', include_top=False)
base_model.trainable = False

model = keras.Sequential([
    base_model,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train
model.fit(train_generator, epochs=10, validation_data=val_generator)

# Deploy
model.save('saved_model/image_classifier')
```

**PyTorch:**

```python
import torch
import torchvision.transforms as transforms
from torchvision import datasets
from torch.utils.data import DataLoader
import torchvision.models as models

# Data transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load data
train_dataset = datasets.ImageFolder('data/train', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Transfer learning
model = models.resnet50(pretrained=True)
model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Train
for epoch in range(10):
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

# Save
torch.save(model.state_dict(), 'image_classifier.pth')
```

---

### Example: NLP Text Classification

**PyTorch with Transformers:**

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
import torch

# Load pre-trained model
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=2
)

# Tokenize data
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=512
    )

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
)

# Train
trainer.train()
```

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Start Simple** | Baseline before complex models |
| **Validate Data** | Garbage in, garbage out |
| **Use Version Control** | Track code, data, models (DVC, MLflow) |
| **Monitor Performance** | Detect drift and degradation |
| **Test Thoroughly** | Unit tests, integration tests |
| **Document Everything** | Reproducibility and knowledge sharing |
| **Optimize Incrementally** | Profile before optimizing |
| **Use Pre-trained Models** | Transfer learning saves time |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Overfitting** | Poor generalization | Regularization, validation |
| **Data Leakage** | Unrealistic performance | Proper train/test split |
| **Ignoring Baseline** | Don't know if model helps | Compare to simple baseline |
| **No Monitoring** | Degradation goes unnoticed | Set up monitoring |
| **Premature Optimization** | Waste time on wrong things | Profile first |
| **No Versioning** | Can't reproduce results | Version code, data, models |

---

### ML Engineering Checklist

**Development:**
- [ ] Data validation and quality checks
- [ ] Proper train/validation/test splits
- [ ] Baseline model established
- [ ] Experiment tracking set up
- [ ] Code versioning (Git)
- [ ] Model versioning (MLflow, DVC)

**Training:**
- [ ] Hyperparameter tuning
- [ ] Cross-validation
- [ ] Regularization applied
- [ ] Early stopping configured
- [ ] Checkpointing enabled

**Deployment:**
- [ ] Model optimized (quantization, pruning)
- [ ] Serving infrastructure ready
- [ ] Monitoring set up
- [ ] A/B testing framework
- [ ] Rollback plan

**Operations:**
- [ ] Performance monitoring
- [ ] Data drift detection
- [ ] Model retraining pipeline
- [ ] Alerting configured
- [ ] Documentation complete

</div>

---

## 🎓 Learning Resources

<div align="center">

### Recommended Learning Path

| Step | Topic | Resources |
|:---:|:---:|:---:|
| **1️⃣** | ML Fundamentals | Coursera ML Course, Fast.ai |
| **2️⃣** | Deep Learning Basics | Deep Learning Specialization |
| **3️⃣** | TensorFlow/Keras | TensorFlow Tutorials, Keras Guide |
| **4️⃣** | PyTorch | PyTorch Tutorials, Fast.ai |
| **5️⃣** | Production ML | ML Engineering Course, MLOps |
| **6️⃣** | Advanced Topics | Research papers, GitHub repos |

---

### Key Resources

**TensorFlow:**
- Official Documentation: https://www.tensorflow.org/
- TensorFlow Tutorials: https://www.tensorflow.org/tutorials
- Keras Guide: https://keras.io/guides/

**PyTorch:**
- Official Documentation: https://pytorch.org/
- PyTorch Tutorials: https://pytorch.org/tutorials/
- Fast.ai Course: https://www.fast.ai/

**ML Engineering:**
- MLflow: https://mlflow.org/
- Weights & Biases: https://wandb.ai/
- DVC: https://dvc.org/

**Datasets:**
- TensorFlow Datasets: https://www.tensorflow.org/datasets
- PyTorch Datasets: torchvision, torchaudio
- Hugging Face Datasets: https://huggingface.co/datasets

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **ML Fundamentals** | Learn from data, generalize to new examples |
| **Deep Learning** | Neural networks with multiple layers |
| **TensorFlow** | Production-focused, Keras integration, TF Serving |
| **PyTorch** | Research-friendly, Pythonic, dynamic graphs |
| **Production ML** | End-to-end pipeline, monitoring, versioning |
| **Best Practices** | Start simple, validate, monitor, version |

**💡 Remember:** Both TensorFlow and PyTorch are powerful frameworks. Choose based on your needs: TensorFlow for production deployment, PyTorch for research and experimentation.

</div>

---

<div align="center">

**Master Machine Learning with TensorFlow and PyTorch! 🚀**

*Build production ML systems with confidence and efficiency.*

</div>
