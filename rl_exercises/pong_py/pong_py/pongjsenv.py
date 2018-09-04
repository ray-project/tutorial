import gym
import gym.spaces

from pong_py.pongjs import PongJS


def transform_state(state):
    return state / 500

class PongJSEnv(gym.Env):
    def __init__(self):
        self.env = PongJS()
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.box.Box(low=0, high=1, shape=(8,))

    @property
    def right_pad(self):
        return self.env.right_pad

    @property
    def left_pad(self):
        return self.env.left_pad

    def reset(self):
        self.env.init()
        return transform_state(self.env.get_state())

    def step(self, action):
        state, reward, done = self.env.step(action)
        return transform_state(state), 1, done, {}
        #return state, reward, done, {}
