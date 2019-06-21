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
    return sorted(
        trial_list,
        key=lambda trial: trial.last_result.get(metric, 0),
        reverse=True)


def get_best_result(trial_list, metric):
    """Retrieve the last result from the best trial."""
    return {metric: get_best_trial(trial_list, metric).last_result[metric]}


def get_best_model(model_creator, trial_list, metric):
    """Restore a model from the best trial."""
    sorted_trials = get_sorted_trials(trial_list, metric)
    for best_trial in sorted_trials:
        try:
            print("Creating model...")
            model = model_creator(**best_trial.config)
            weights = os.path.join(best_trial.logdir,
                                   best_trial.last_result["checkpoint"])
            print("Loading from", weights)
            model.load_weights(weights)
            break
        except Exception as e:
            print(e)
            print("Loading failed. Trying next model")
    return model


class TuneCallback(keras.callbacks.Callback):
    """Custom Callback for Tune."""

    def __init__(self, reporter):
        super(TuneCallback, self).__init__()
        self.reporter = reporter
        self.top_acc = -1
        self.last_10_results = []

    def on_batch_end(self, batch, logs={}):
        """Reports the last result"""
        curr_acc = logs["acc"]
        if curr_acc > self.top_acc:
            self.top_acc = curr_acc
            self.model.save_weights("weights_tune_tmp.h5")
            os.rename("weights_tune_tmp.h5", "weights_tune.h5")

        if len(self.last_10_results) >= 5:
            self.last_10_results = self.last_10_results[1:]
        self.last_10_results += [logs["acc"]]

        self.reporter(
            mean_accuracy=np.mean(self.last_10_results),
            checkpoint="weights_tune.h5")


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
