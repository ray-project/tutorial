# In this Exercise we will parallelize the example cartpole.py

import time

import gym
import numpy as np
import ray
import tensorflow as tf
import tensorflow.contrib.slim as slim

n_obs = 4              # dimensionality of observations
n_h = 256              # number of hidden layer neurons
n_actions = 2          # number of available actions
learning_rate = 5e-4   # how rapidly to update parameters
gamma = .99            # reward discount factor

ray.init()

def make_policy(observation_placeholder):
    hidden = slim.fully_connected(observation_placeholder, n_h)
    log_probability = slim.fully_connected(hidden, n_actions, activation_fn=None, weights_initializer=tf.truncated_normal_initializer(0.001))
    return tf.nn.softmax(log_probability)

def discounted_normalized_rewards(r):
    """Take 1D float array of rewards and compute normalized discounted reward."""
    result = np.zeros_like(r)
    running_sum = 0
    for t in reversed(range(0, r.size)):
        running_sum = running_sum * gamma + r[t]
        result[t] = running_sum
    return (result - np.mean(result)) / np.std(result)

# EXERCISE: Make the Agent class an actor and fill in the __init__
# as well as the rollout methods.
class Agent(object):

    # EXERCISE: Create the CartPole-v1 environment as self.env,
    # create placeholders for the input observation, set up the action_probability
    # network, create a tensorflow Session, initialize the variables and
    # create a TensorFlowVariables objects that can be used to read and
    # write the variables of the policy.
    def __init__(self):
        #
        self.env = gym.make("CartPole-v1")

        self.input_observation = tf.placeholder(dtype=tf.float32, shape=[None, n_obs])

        # Set up the policy network.
        self.action_probability = make_policy(self.input_observation)

        # Create TensorFlow session and initialize variables.
        self.sess = tf.Session()
        tf.initialize_all_variables().run(session=self.sess)

        self.variables = ray.experimental.TensorFlowVariables(self.action_probability, self.sess)

    # EXERCISE: Write the function to load the weights into the policy here.
    def load_weights(self, weights):
        self.variables.set_weights(weights)

    def rollout(self):
        done = False
        observations, rewards, labels = [], [], []
        observation = self.env.reset()

        while not done:

            # EXERCISE:
            # Write the part that evaluates the policy and appends
            # the current observation to observations, the reward to rewards and
            # the target label to labels.

        return np.vstack(observations), discounted_normalized_rewards(np.vstack(rewards)), np.vstack(labels)



agents = # EXERCISE: Create 4 remote Agents here

input_observation = tf.placeholder(dtype=tf.float32, shape=[None, n_obs])
input_probability = tf.placeholder(dtype=tf.float32, shape=[None, n_actions])
input_reward = tf.placeholder(dtype=tf.float32, shape=[None, 1])

action_probability = make_policy(input_observation)

loss = tf.nn.l2_loss(input_probability - action_probability)
optimizer = tf.train.AdamOptimizer(learning_rate)
train_op = optimizer.minimize(loss, grad_loss=input_reward)

sess = tf.Session()
tf.initialize_all_variables().run(session=sess)
variables = ray.experimental.TensorFlowVariables(loss, sess)

num_timesteps = 0
reward_sums = []

# Barrier for the timing (TODO(pcm): clean this up)
weights = ray.put(variables.get_weights())
ray.get([agent.load_weights.remote(weights) for agent in agents])

start_time = time.time()

while True:
    weights = ray.put(variables.get_weights())
    [agent.load_weights.remote(weights) for agent in agents]
    trajectories = ray.get([agent.rollout.remote() for agent in agents])
    reward_sums.extend([trajectory[0].shape[0] for trajectory in trajectories])
    timesteps = np.sum([trajectory[0].shape[0] for trajectory in trajectories])
    if (num_timesteps + timesteps) // 5000 > num_timesteps // 5000:
        print('time: {:4.1f}, timesteps: {:7.0f}, reward: {:7.3f}'.format(
            time.time() - start_time, num_timesteps + timesteps, np.mean(reward_sums)))
    num_timesteps += timesteps
    results = [np.concatenate(x) for x in zip(*trajectories)]
    sess.run(train_op, {input_observation: results[0], input_reward: results[1], input_probability: results[2]})
