import numpy as np
import os
import scipy.ndimage as ndimage
import itertools
import logging
import sys
import keras
from keras.datasets import mnist
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K

def limit_threads(num_threads):
    K.set_session(
        K.tf.Session(
            config=K.tf.ConfigProto(
                intra_op_parallelism_threads=num_threads,
                inter_op_parallelism_threads=num_threads)))

    
def shuffled(x, y):
    idx = np.r_[:x.shape[0]]
    np.random.shuffle(idx)
    return x[idx], y[idx]


def load_data(generator=True, num_batches=600):
    num_classes = 10

    # input image dimensions
    img_rows, img_cols = 28, 28

    # the data, split between train and test sets
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')
    x_train, y_train = shuffled(x_train, y_train)
    x_test, y_test = shuffled(x_test, y_test)

    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    if generator:
        datagen = ImageDataGenerator()
        return itertools.islice(datagen.flow(x_train, y_train), num_batches)
    return x_train, x_test, y_train, y_test


def get_best_trial(trial_list, metric):
    """Retrieve the best trial."""
    return max(trial_list, key=lambda trial: trial.last_result.get(metric, 0))


def get_sorted_trials(trial_list, metric):
    return sorted(trial_list, key=lambda trial: trial.last_result.get(metric, 0), reverse=True)


def get_best_result(trial_list, metric):
    """Retrieve the last result from the best trial."""
    return {metric: get_best_trial(trial_list, metric).last_result[metric]}


def get_best_model(model_creator, trial_list, metric):
    """Restore a model from the best trial."""
    sorted_trials = get_sorted_trials(trial_list, metric)
    for best_trial in sorted_trials:
        try:
            print("Creating model...")
            model = model_creator(best_trial.config)
            weights = os.path.join(best_trial.logdir, best_trial.last_result["checkpoint"])
            print("Loading from", weights)
            model.load_weights(weights)
            break
        except Exception as e:
            print(e)
            print("Loading failed. Trying next model")
    return model

def prepare_data(data):
    new_data = np.array(data).reshape((1, 28, 28, 1)).astype(np.float32)
    return ndimage.gaussian_filter(new_data, sigma=(0.5))

class TuneCallback(keras.callbacks.Callback):
    def __init__(self, reporter, logs={}):
        self.reporter = reporter

    def on_train_end(self, epoch, logs={}):
        self.reporter(done=1, mean_accuracy=logs["acc"])

    def on_batch_end(self, batch, logs={}):
        self.reporter(mean_accuracy=logs["acc"])

       
class GoodError(Exception): 
    pass


def test_reporter(train_mnist_tune):
    def mock_reporter(**kwargs):
        assert "mean_accuracy" in kwargs, "Did not report proper metric"
        assert "checkpoint" in kwargs, "Accidentally removed `checkpoint`?"
        assert "timesteps_total" in kwargs, "Accidentally removed `timesteps_total`?"
        assert isinstance(kwargs["mean_accuracy"], float), (
            "Did not report properly. Need to report a float!")
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

    
def evaluate(model, validation=True):
    train_data, val_data, train_labels, val_labels = load_data(generator=False)
    data = val_data if validation else train_data
    labels = val_labels if validation else train_labels

    res = model.evaluate(data, labels)
    print("Model evaluation results:", dict(zip(model.metrics_names, res)))
