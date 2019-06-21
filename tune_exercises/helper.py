import numpy as np
import os
import scipy.ndimage as ndimage
import itertools
import logging
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms


EPOCH_SIZE = 512
TEST_SIZE = 256


def limit_threads(num_threads):
    from keras import backend as K

    K.set_session(
        K.tf.Session(
            config=K.tf.ConfigProto(
                intra_op_parallelism_threads=num_threads,
                inter_op_parallelism_threads=num_threads)))


class GoodError(Exception):
    pass


def test_reporter(train_mnist_tune):
    def mock_reporter(**kwargs):
        assert "mean_accuracy" in kwargs, "Did not report proper metric"
        assert "checkpoint" in kwargs, "Accidentally removed `checkpoint`?"
        raise GoodError("This works.")

    try:
        train_mnist_tune({}, mock_reporter)
    except TypeError as e:
        print("Forgot to modify function signature?")
        raise e
    except GoodError:
        print("Works!")
        return 1
    raise Exception("Didn't call reporter...")


def prepare_data(data):
    try:
        new_data = np.array(data).reshape((1, 28, 28, 1)).astype(np.float32)
    except ValueError as e:
        print("Try running this notebook in `jupyter notebook`.")
        raise e
    return ndimage.gaussian_filter(new_data, sigma=(0.5))


class ConvNet(nn.Module):
    def __init__(self, config):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 3, kernel_size=3)
        self.fc = nn.Linear(192, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 3))
        x = x.view(-1, 192)
        x = self.fc(x)
        return F.log_softmax(x, dim=1)


def train(model, optimizer, train_loader):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        if batch_idx * len(data) > EPOCH_SIZE:
            return
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()


def test(model, data_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(data_loader):
            if batch_idx * len(data) > TEST_SIZE:
                break
            outputs = model(data)
            _, predicted = torch.max(outputs.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    return correct / total


def get_data_loaders(datapath="~/data"):
    mnist_transforms = transforms.Compose([transforms.ToTensor()])
    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST(
            datapath, train=True, transform=mnist_transforms),
        batch_size=64,
        shuffle=True
    )
    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST(
            datapath, train=False, transform=mnist_transforms),
        batch_size=64,
        shuffle=True
    )
    return train_loader, test_loader