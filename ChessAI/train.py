"""To training image classification model for templates."""

try:
    import torch
    from torch import nn
    from torch.utils.data import Dataset, DataLoader
    from torchvision.transforms import ToTensor, Compose
    import pandas as pd
except ImportError as err:
    raise ImportError('Training features are not allowed, to unlock this feature, please visit \
https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/TRAINING.md') from err

import os

from PIL import Image

BATCH_SIZE: int = 1 # For PyTorch seniors love training.

class CustomImageDataset(Dataset):
    """
    Custom image dataset.
    
    source: https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
    """
    def __init__(self, annotations_file, img_dir, transform=None, target_transform=None):
        self.img_labels = pd.read_csv(annotations_file)
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.img_labels.iloc[idx, 0])
        image = Image.open(img_path).resize((32,32)).convert('RGB')
        label = self.img_labels.iloc[idx, 1]
        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        return image, label

class NeuralNetwork(nn.Module):
    """
    Define model.

    source: https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html
    """
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(3072, 512), # 1*3*32*32
            nn.ReLU(),
            nn.Linear(512, 64),
            nn.ReLU(),
            nn.Linear(64, 13)
        )

    def forward(self, tensor_image):
        """
        Uhhh, forward image?
        """

        image = self.flatten(tensor_image)
        logits = self.linear_relu_stack(image)
        return logits

def _find_device():
    """
    Find suitable device for better processing.
    Returns:
        str: device's name
    """
    return (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )

class TrainModel:
    """
    To train image classification model for templates.
    
    source: https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html
    """
    def __init__(self, annotations_file, img_dir):
        training_data = CustomImageDataset(annotations_file, img_dir, transform=ToTensor())
        self.train_dataloader = DataLoader(training_data, batch_size=BATCH_SIZE)
        self.test_dataloader = DataLoader(training_data, batch_size=BATCH_SIZE, shuffle=True)

        self.device = _find_device()

        self.model = NeuralNetwork().to(device=self.device)

        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.SGD(list(self.model.parameters()), lr=1e-3)

    def train(self):
        """
        Train model.
        """
        self.model.train()
        for _feature, _label in self.train_dataloader:
            _feature, _label = _feature.to(device=self.device), _label.to(device=self.device)

            # Compute prediction error
            pred = self.model(_feature)
            loss = self.loss_fn(pred, _label)

            # Backpropagation
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()

    def test(self) -> float:
        """
        Test model.

        Returns:
            float: current accuracy.
        """
        size = len(self.test_dataloader.dataset)
        num_batches = len(self.test_dataloader)
        self.model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for _feature, _label in self.test_dataloader:
                _feature, _label = _feature.to(device=self.device), _label.to(device=self.device)
                pred = self.model(_feature)
                test_loss += self.loss_fn(pred, _label).item()
                correct += (pred.argmax(1) == _label).type(torch.float).sum().item()
        test_loss /= num_batches
        correct /= size

        print(f'\r{(os.get_terminal_size().columns) * ' '}', end='') # clear line
        print(f"\rTraining: Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f}", end='')
        return correct

    def hardcore_train(self, require_accuracy: float = 1) -> float:
        """
        Train model until got the required accuracy.

        Args:
            require_accuracy (float, optional): The required accuracy. Defaults to 1 (100%).

        Returns:
            float: model's accuracy.
        """
        current_accuracy: float = 0

        while current_accuracy < require_accuracy:
            self.train()
            current_accuracy = self.test()

        return current_accuracy

    def save(self, parent_path: str):
        """
        Save model.

        Args:
            parent_path (str): parent's path, save model at {parent_path}/'model.pth'
        """
        torch.save(self.model.state_dict(), os.path.join(parent_path, 'model.pth'))

class LoadModel:
    """
    Load model and make prediction.
    
    source: https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html
    
    Args:
        parent_path (str): parent's path, save model at {parent_path}/'model.pth'
    """
    def __init__(self, parent_path: str):
        self.device = _find_device()
        self.model = NeuralNetwork().to(device=self.device)

        path = os.path.join(parent_path, "model.pth")
        self.model.load_state_dict(torch.load(path, weights_only=True))

    def predict(self, classes: tuple, img: Image.Image) -> str:
        """
        Predict image's class.

        Args:
            classes (tuple): list of classes.
            img_path (str): path to image.

        Returns:
            str: image's predicted class.
        """
        self.model.eval()
        x = img.resize((32,32))

        transformer = Compose([ToTensor()])
        x = transformer(x).view(1, 3072)

        with torch.no_grad():
            x = x.to(device=self.device)
            pred = self.model(x)
            return classes[pred[0].argmax(0)]
