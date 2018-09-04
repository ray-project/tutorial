import pong_py.helper as helper
import random

class Ball():
    def __init__(self, pong):
        self.radius  = 5
        self.dt = pong.dt
        self.minX    = self.radius;
        self.maxX    = pong.width - self.radius
        self.minY    = pong.wall_width + self.radius
        self.maxY    = pong.height - pong.wall_width - self.radius
        self.speed   = (self.maxX - self.minX) / 4;
        self.accel   = 8;
        self.dx = 0
        self.dy = 0

    def set_position(self, x, y):
        self.x_prev = x if not hasattr(self, "x") else self.x
        self.y_prev = y if not hasattr(self, "y") else self.y

        self.x      = x
        self.y      = y
        self.left   = self.x - self.radius
        self.top    = self.y - self.radius
        self.right  = self.x + self.radius
        self.bottom = self.y + self.radius

    def set_direction(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def update(self, left_pad, right_pad):

        pos = helper.accelerate(self.x, self.y,
                            self.dx, self.dy,
                            self.accel, self.dt);

        if ((pos.dy > 0) and (pos.y > self.maxY)):
            pos.y = self.maxY
            pos.dy = -pos.dy
        elif ((pos.dy < 0) and (pos.y < self.minY)):
            pos.y = self.minY
            pos.dy = -pos.dy

        paddle = left_pad if (pos.dx < 0) else right_pad;
        pt = helper.ballIntercept(self, paddle, pos.nx, pos.ny);

        if pt:
            if pt.d == 'left' or pt.d == 'right':
                pos.x = pt.x
                pos.dx = -pos.dx
            elif pt.d == 'top' or pt.d == 'bottom':
                pos.y = pt.y
                pos.dy = -pos.dy

            if paddle.up:
                pos.dy = pos.dy * (0.5 if pos.dy < 0 else 1.5)
            elif paddle.down:
                pos.dy = pos.dy * (0.5 if pos.dy > 0 else 1.5)

        self.set_position(pos.x,  pos.y)
        self.set_direction(pos.dx, pos.dy)

    def reset(self, playerNo):
        self.set_position((self.maxX + self.minX) / 2, random.uniform(self.minY, self.maxY))
        self.set_direction(self.speed if playerNo == 1 else -self.speed, self.speed)
