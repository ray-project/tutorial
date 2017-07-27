import time

import gym
import numpy as np
import ray
import tensorflow as tf
import tensorflow.contrib.slim as slim

n_obs = 4              # dimensionality of observations
n_h = 128              # number of hidden layer neurons
n_actions = 2          # number of available actions
learning_rate = 1e-2   # how rapidly to update parameters
gamma = .9             # reward discount factor

ray.init()

def make_policy(observation_placeholder):
    hidden = slim.fully_connected(observation_placeholder, n_h)
    log_probability = slim.fully_connected(hidden, n_actions, activation_fn=None)
    return tf.nn.softmax(log_probability)

def discounted_normalized_rewards(r):
    """Take 1D float array of rewards and compute normalized discounted reward."""
    result = np.zeros_like(r)
    running_sum = 0
    for t in reversed(range(0, r.size)):
        running_sum = running_sum * gamma + r[t]
        result[t] = running_sum
    return (result - np.mean(result)) / np.std(result)

@ray.remote
class Agent(object):

    def __init__(self):
        self.env = gym.make("CartPole-v1")

        self.input_observation = tf.placeholder(dtype=tf.float32, shape=[None, n_obs])

        # Set up the policy network.
        self.action_probability = make_policy(self.input_observation)

        # Create TensorFlow session and initialize variables.
        self.sess = tf.Session()
        tf.initialize_all_variables().run(session=self.sess)

        self.variables = ray.experimental.TensorFlowVariables(self.action_probability, self.sess)

    def load_weights(self, weights):
        self.variables.set_weights(weights)

    def rollout(self):
        done = False
        observations, rewards, labels = [], [], []
        observation = self.env.reset()

        while not done:
            # stochastically sample a policy from the network
            probability = self.sess.run(self.action_probability, {self.input_observation: observation[np.newaxis, :]})[0,:]

            action = np.random.choice(n_actions, p = probability)
            label = np.zeros_like(probability) ; label[action] = 1
            observations.append(observation)
            labels.append(label)

            observation, reward, done, info = self.env.step(action)

            rewards.append(reward)

        return np.vstack(observations), discounted_normalized_rewards(np.vstack(rewards)), np.vstack(labels)


agents = [Agent.remote() for i in range(4)]

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
    # print("time is", time.time() - start_time, "mean episode length is ", mean_length)
    results = [np.concatenate(x) for x in zip(*trajectories)]
    sess.run(train_op, {input_observation: results[0], input_reward: results[1], input_probability: results[2]})
