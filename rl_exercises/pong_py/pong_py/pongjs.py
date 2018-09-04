import numpy as np
from pong_py.ball import Ball
from pong_py.paddle import Paddle

class PongJS(object):
    # MDP to
    def __init__(self):
        self.width = 640
        self.height = 480
        self.wall_width = 12
        self.dt = 0.05 # seconds
        #self.dt = 0.01 # seconds
        self.left_pad = Paddle(0, self)
        self.right_pad = Paddle(1, self)
        self.ball = Ball(self)

    def step(self, action):
        # do logic for self
        self.left_pad.step(action)
        self.right_pad.ai_step(self.ball)

        self.ball.update(self.left_pad, self.right_pad)
        term, reward = self.terminate()
        if term:
            self.reset(0 if reward == 1 else 1)
        state = self.get_state()
        return state, reward, term

    def init(self):
        self.reset(0)

    def terminate(self):
        if self.ball.left > self.width:
            return True, 1
        elif self.ball.right < 0:
            return True, -1
        else:
            return False, 0

    def get_state(self):
        return np.array([self.left_pad.y, 0,
                         self.ball.x, self.ball.y,
                         self.ball.dx, self.ball.dy,
                         self.ball.x_prev, self.ball.y_prev])

    def reset(self, player):
        self.ball.reset(player)
