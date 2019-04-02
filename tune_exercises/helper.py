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

def prepare_data(data):
    new_data = np.array(data).reshape((1, 28, 28, 1)).astype(np.float32)
    return ndimage.gaussian_filter(new_data, sigma=(0.5))

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