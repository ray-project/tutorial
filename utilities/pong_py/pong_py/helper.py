from collections import namedtuple

Position = namedtuple("Position", ["nx", "ny", "x", "y", "dx", "dy"])
Intercept = namedtuple("Intercept", ["x", "y", "d"])
Rectangle = namedtuple("Rectangle", ["left", "right", "top", "bottom"])

class Position():
    def __init__(self, nx, ny, x, y, dx, dy):
        self.nx = nx 
        self.ny = ny 
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy 

class Intercept():
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d

class Rectangle():
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

def accelerate(x, y, dx, dy, accel, dt):
    x2  = x + (dt * dx) + (accel * dt * dt * 0.5);
    y2  = y + (dt * dy) + (accel * dt * dt * 0.5);
    dx2 = dx + (accel * dt) * (1 if dx > 0 else -1);
    dy2 = dy + (accel * dt) * (1 if dy > 0 else -1);
    return Position((x2-x), (y2-y), x2, y2, dx2, dy2 )


def intercept(x1, y1, x2, y2, x3, y3, x4, y4, d):
    denom = ((y4-y3) * (x2-x1)) - ((x4-x3) * (y2-y1))
    if (denom != 0):
        ua = (((x4-x3) * (y1-y3)) - ((y4-y3) * (x1-x3))) / denom
        if ((ua >= 0) and (ua <= 1)):
            ub = (((x2-x1) * (y1-y3)) - ((y2-y1) * (x1-x3))) / denom
            if ((ub >= 0) and (ub <= 1)):
                x = x1 + (ua * (x2-x1))
                y = y1 + (ua * (y2-y1))
                return Intercept(x, y, d)


def ballIntercept(ball, rect, nx, ny):
        pt = None
        if (nx < 0):
            pt = intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
                                       rect.right  + ball.radius, 
                                       rect.top    - ball.radius, 
                                       rect.right  + ball.radius, 
                                       rect.bottom + ball.radius, 
                                       "right");
        elif (nx > 0):
            pt = intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
                                   rect.left   - ball.radius, 
                                   rect.top    - ball.radius, 
                                   rect.left   - ball.radius, 
                                   rect.bottom + ball.radius,
                                   "left")

        if (not pt):
            if (ny < 0):
                pt = intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
                                     rect.left   - ball.radius, 
                                     rect.bottom + ball.radius, 
                                     rect.right  + ball.radius, 
                                     rect.bottom + ball.radius,
                                     "bottom");
            elif (ny > 0):
                pt = intercept(ball.x, ball.y, ball.x + nx, ball.y + ny, 
                                     rect.left   - ball.radius, 
                                     rect.top    - ball.radius, 
                                     rect.right  + ball.radius, 
                                     rect.top    - ball.radius,
                                     "top");
        return pt