//=============================================================================
// PONG
//=============================================================================

Pong = {

  Defaults: {
    width: 640,   // logical canvas width (browser will scale to physical canvas
                  // size - which is controlled by @media css queries)
    height: 480,  // logical canvas height (ditto)
    wallWidth: 12,
    paddleWidth: 12,
    paddleHeight: 60,
    paddleSpeed: 2,  // should be able to cross court vertically   in 2 seconds
    ballSpeed: 4,    // should be able to cross court horizontally in 4 seconds,
                     // at starting speed ...
    ballAccel: 8,    // ... but accelerate as time passes
    ballRadius: 5,
    sound: true
  },

  Colors: {
    walls: 'white',
    ball: 'white',
    score: 'white',
    footprint: '#333',
    predictionGuess: 'yellow',
    predictionExact: 'red'
  },

  Images: ['images/press1.png', 'images/press2.png', 'images/winner.png'],

  Levels: [
    {aiReaction: 0.2, aiError: 40},   // 0:  ai is losing by 8
    {aiReaction: 0.3, aiError: 50},   // 1:  ai is losing by 7
    {aiReaction: 0.4, aiError: 60},   // 2:  ai is losing by 6
    {aiReaction: 0.5, aiError: 70},   // 3:  ai is losing by 5
    {aiReaction: 0.6, aiError: 80},   // 4:  ai is losing by 4
    {aiReaction: 0.7, aiError: 90},   // 5:  ai is losing by 3
    {aiReaction: 0.8, aiError: 100},  // 6:  ai is losing by 2
    {aiReaction: 0.9, aiError: 110},  // 7:  ai is losing by 1
    {aiReaction: 1.0, aiError: 120},  // 8:  tie
    {aiReaction: 1.1, aiError: 130},  // 9:  ai is winning by 1
    {aiReaction: 1.2, aiError: 140},  // 10: ai is winning by 2
    {aiReaction: 1.3, aiError: 150},  // 11: ai is winning by 3
    {aiReaction: 1.4, aiError: 160},  // 12: ai is winning by 4
    {aiReaction: 1.5, aiError: 170},  // 13: ai is winning by 5
    {aiReaction: 1.6, aiError: 180},  // 14: ai is winning by 6
    {aiReaction: 1.7, aiError: 190},  // 15: ai is winning by 7
    {aiReaction: 1.8, aiError: 200}   // 16: ai is winning by 8
  ],

  //-----------------------------------------------------------------------------

  initialize: function(runner, cfg) {
    Game.loadImages(Pong.Images, function(images) {
      this.cfg = cfg;
      this.runner = runner;
      this.width = runner.width;
      this.height = runner.height;
      this.images = images;
      this.playing = false;
      this.scores = [0, 0];
      this.menu = Object.construct(Pong.Menu, this);
      this.court = Object.construct(Pong.Court, this);
      this.leftPaddle = Object.construct(Pong.Paddle, this);
      this.rightPaddle = Object.construct(Pong.Paddle, this, true);
      this.ball = Object.construct(Pong.Ball, this);
      this.sounds = Object.construct(Pong.Sounds, this);
      this.runner.start();
    }.bind(this));
  },

  startDemo: function() {
    this.start(0);
  },
  startSinglePlayer: function() {
    this.start(1);
  },
  startDoublePlayer: function() {
    this.start(2);
  },
  error: false,

  start: function(numPlayers) {
    if (!this.playing) {
      this.scores = [0, 0];
      this.playing = true;
      this.leftPaddle.setAuto(numPlayers < 2, this.level(0));
      this.rightPaddle.setAuto(false, this.level(1));
      this.ball.reset();
      this.runner.hideCursor();
      Pong.rpc(JSON.stringify({"command": "start_episode"}), function(episode_id) {
          Pong.episode_id = episode_id;
          console.log("Started episode", Pong.episode_id);
      });
    }
  },

  stop: function(ask) {
    if (this.playing) {
      if (!ask || this.runner.confirm('Abandon game in progress ?')) {
        this.playing = false;
        this.leftPaddle.setAuto(false);
        this.rightPaddle.setAuto(false);
        this.runner.showCursor();
        this.episode_id = null;
      }
      Pong.rpc(JSON.stringify({"command": "end_episode", "episode_id": Pong.episode_id}),
          function(episode_id) {
              console.log("Ended episode", Pong.episode_id);
          });
    }
  },

  level: function(playerNo) {
    return 8 + (this.scores[playerNo] - this.scores[playerNo ? 0 : 1]);
  },

  rpc: function(data, callback) {
      if (Pong.error) {
          return;
      }
      console.log("Sending", data);
      var predict_url = "/pong/predict";
      if(window && window.location) {
          if (window.location.hostname === "localhost") {
                predict_url = "http://localhost:3000";
          } else {
              predict_url = "http://" + window.location.host + ":3000";
          }
      }

      // Query Pong server
      fetch(predict_url, {
        method: 'POST',
        redirect: 'follow',
        headers: new Headers({'Content-Type': 'application/json'}),
        body: data
      }).then(function(response) {
        if (response.ok) {
          response.json().then(callback);
        } else {
          console.log(response.status, response.statusText);
        }
      }).catch(function(error) {
          if (!Pong.error) {
              alert("Failed to get execute request, please refresh the page: " + data);
          }
          Pong.error = true;
      });
  },

  goal: function(playerNo) {
    this.sounds.goal();
    this.scores[playerNo] += 1;
    Pong.rpc(
        JSON.stringify(
            {"command": "log_returns", "playerNo": playerNo, "episode_id": Pong.episode_id, "reward": 10}),
        function(data) {
            console.log("Logged point for player", playerNo);
        });
    if (this.scores[playerNo] == 9) {
      this.menu.declareWinner(playerNo);
      this.stop();
    } else {
      this.ball.reset(playerNo);
      this.leftPaddle.setLevel(this.level(0));
      this.rightPaddle.setLevel(this.level(1));
    }
  },

  update: function(dt) {
    this.leftPaddle.update(dt, this.ball);
    this.rightPaddle.update(dt, this.ball);
    if (this.playing) {
      var dx = this.ball.dx;
      var dy = this.ball.dy;
      this.ball.update(dt, this.leftPaddle, this.rightPaddle);
      if (this.ball.dx < 0 && dx > 0)
        this.sounds.ping();
      else if (this.ball.dx > 0 && dx < 0)
        this.sounds.pong();
      else if (this.ball.dy * dy < 0)
        this.sounds.wall();

      if (this.ball.left > this.width)
        this.goal(0);
      else if (this.ball.right < 0)
        this.goal(1);
    }
  },

  draw: function(ctx) {
    this.court.draw(ctx, this.scores[0], this.scores[1]);
    this.leftPaddle.draw(ctx);
    this.rightPaddle.draw(ctx);
    if (this.playing)
      this.ball.draw(ctx);
    else
      this.menu.draw(ctx);
  },

  onkeydown: function(keyCode) {
    switch (keyCode) {
      case Game.KEY.ONE:
        this.startSinglePlayer();
        break;
      case Game.KEY.TWO:
        this.startDoublePlayer();
        break;
      case Game.KEY.ESC:
        this.stop(true);
        break;
      case Game.KEY.Q:
        if (!this.leftPaddle.auto) this.leftPaddle.moveUp();
        break;
      case Game.KEY.A:
        if (!this.leftPaddle.auto) this.leftPaddle.moveDown();
        break;
      case Game.KEY.P:
        if (!this.rightPaddle.auto) this.rightPaddle.moveUp();
        break;
      case Game.KEY.UP:
        if (!this.rightPaddle.auto) this.rightPaddle.moveUp();
        break;
      case Game.KEY.L:
        if (!this.rightPaddle.auto) this.rightPaddle.moveDown();
        break;
      case Game.KEY.DOWN:
        if (!this.rightPaddle.auto) this.rightPaddle.moveDown();
        break;
    }
  },

  onkeyup: function(keyCode) {
    switch (keyCode) {
      case Game.KEY.Q:
        if (!this.leftPaddle.auto) this.leftPaddle.stopMovingUp();
        break;
      case Game.KEY.A:
        if (!this.leftPaddle.auto) this.leftPaddle.stopMovingDown();
        break;
      case Game.KEY.P:
        if (!this.rightPaddle.auto) this.rightPaddle.stopMovingUp();
        break;
      case Game.KEY.UP:
        if (!this.rightPaddle.auto) this.rightPaddle.stopMovingUp();
        break;
      case Game.KEY.L:
        if (!this.rightPaddle.auto) this.rightPaddle.stopMovingDown();
        break;
      case Game.KEY.DOWN:
        if (!this.rightPaddle.auto) this.rightPaddle.stopMovingDown();
        break;
    }
  },

  showStats: function(on) {
    this.cfg.stats = on;
  },
  showFootprints: function(on) {
    this.cfg.footprints = on;
    this.ball.footprints = [];
  },
  showPredictions: function(on) {
    this.cfg.predictions = on;
  },
  enableSound: function(on) {
    this.cfg.sound = on;
  },

  //=============================================================================
  // MENU
  //=============================================================================

  Menu: {

    initialize: function(pong) {
      var press1 = pong.images['images/press1.png'];
      var press2 = pong.images['images/press2.png'];
      var winner = pong.images['images/winner.png'];
      this.press1 = {image: press1, x: 10, y: pong.cfg.wallWidth};
      this.press2 = {
        image: press2,
        x: (pong.width - press2.width - 10),
        y: pong.cfg.wallWidth
      };
      this.winner1 = {
        image: winner,
        x: (pong.width / 2) - winner.width - pong.cfg.wallWidth,
        y: 6 * pong.cfg.wallWidth
      };
      this.winner2 = {
        image: winner,
        x: (pong.width / 2) + pong.cfg.wallWidth,
        y: 6 * pong.cfg.wallWidth
      };
    },

    declareWinner: function(playerNo) {
      this.winner = playerNo;
    },

    draw: function(ctx) {
      // ctx.drawImage(this.press1.image, this.press1.x, this.press1.y);
      // ctx.drawImage(this.press2.image, this.press2.x, this.press2.y);
      if (this.winner == 0)
        ctx.drawImage(this.winner1.image, this.winner1.x, this.winner1.y);
      else if (this.winner == 1)
        ctx.drawImage(this.winner2.image, this.winner2.x, this.winner2.y);
    }

  },

  //=============================================================================
  // SOUNDS
  //=============================================================================

  Sounds: {

    initialize: function(pong) {
      this.game = pong;
      this.supported = Game.ua.hasAudio;
      if (this.supported) {
        this.files = {
          ping: Game.createAudio('sounds/ping.wav'),
          pong: Game.createAudio('sounds/pong.wav'),
          wall: Game.createAudio('sounds/wall.wav'),
          goal: Game.createAudio('sounds/goal.wav')
        };
      }
    },

    play: function(name) {
      if (this.supported && this.game.cfg.sound && this.files[name])
        this.files[name].play();
    },

    ping: function() {
      this.play('ping');
    },
    pong: function() {
      this.play('pong');
    },
    wall: function() { /*this.play('wall');*/ },
    goal: function() { /*this.play('goal');*/ }

  },

  //=============================================================================
  // COURT
  //=============================================================================

  Court: {

    initialize: function(pong) {
      var w = pong.width;
      var h = pong.height;
      var ww = pong.cfg.wallWidth;

      this.ww = ww;
      this.walls = [];
      this.walls.push({x: 0, y: 0, width: w, height: ww});
      this.walls.push({x: 0, y: h - ww, width: w, height: ww});
      var nMax = (h / (ww * 2));
      for (var n = 0; n < nMax; n++) {  // draw dashed halfway line
        this.walls.push({
          x: (w / 2) - (ww / 2),
          y: (ww / 2) + (ww * 2 * n),
          width: ww,
          height: ww
        });
      }

      var sw = 3 * ww;
      var sh = 4 * ww;
      this.score1 = {x: 0.5 + (w / 2) - 1.5 * ww - sw, y: 2 * ww, w: sw, h: sh};
      this.score2 = {x: 0.5 + (w / 2) + 1.5 * ww, y: 2 * ww, w: sw, h: sh};
    },

    draw: function(ctx, scorePlayer1, scorePlayer2) {
      ctx.fillStyle = Pong.Colors.walls;
      for (var n = 0; n < this.walls.length; n++)
        ctx.fillRect(
            this.walls[n].x, this.walls[n].y, this.walls[n].width,
            this.walls[n].height);
      this.drawDigit(
          ctx, scorePlayer1, this.score1.x, this.score1.y, this.score1.w,
          this.score1.h);
      this.drawDigit(
          ctx, scorePlayer2, this.score2.x, this.score2.y, this.score2.w,
          this.score2.h);
    },

    drawDigit: function(ctx, n, x, y, w, h) {
      ctx.fillStyle = Pong.Colors.score;
      var dw = dh = this.ww * 4 / 5;
      var blocks = Pong.Court.DIGITS[n];
      if (blocks[0]) ctx.fillRect(x, y, w, dh);
      if (blocks[1]) ctx.fillRect(x, y, dw, h / 2);
      if (blocks[2]) ctx.fillRect(x + w - dw, y, dw, h / 2);
      if (blocks[3]) ctx.fillRect(x, y + h / 2 - dh / 2, w, dh);
      if (blocks[4]) ctx.fillRect(x, y + h / 2, dw, h / 2);
      if (blocks[5]) ctx.fillRect(x + w - dw, y + h / 2, dw, h / 2);
      if (blocks[6]) ctx.fillRect(x, y + h - dh, w, dh);
    },

    DIGITS: [
      [1, 1, 1, 0, 1, 1, 1],  // 0
      [0, 0, 1, 0, 0, 1, 0],  // 1
      [1, 0, 1, 1, 1, 0, 1],  // 2
      [1, 0, 1, 1, 0, 1, 1],  // 3
      [0, 1, 1, 1, 0, 1, 0],  // 4
      [1, 1, 0, 1, 0, 1, 1],  // 5
      [1, 1, 0, 1, 1, 1, 1],  // 6
      [1, 0, 1, 0, 0, 1, 0],  // 7
      [1, 1, 1, 1, 1, 1, 1],  // 8
      [1, 1, 1, 1, 0, 1, 0]   // 9
    ]

  },

  //=============================================================================
  // PADDLE
  //=============================================================================

  Paddle: {

    initialize: function(pong, rhs) {
      this.pong = pong;
      this.width = pong.cfg.paddleWidth;
      this.height = pong.cfg.paddleHeight;
      this.minY = pong.cfg.wallWidth;
      this.maxY = pong.height - pong.cfg.wallWidth - this.height;
      this.speed = (this.maxY - this.minY) / pong.cfg.paddleSpeed;
      this.setpos(
          rhs ? pong.width - this.width : 0,
          this.minY + (this.maxY - this.minY) / 2);
      this.setdir(0);
    },

    setpos: function(x, y) {
      this.x = x;
      this.y = y;
      this.left = this.x;
      this.right = this.left + this.width;
      this.top = this.y;
      this.bottom = this.y + this.height;
    },

    setdir: function(dy) {
      this.up = (dy < 0 ? -dy : 0);
      this.down = (dy > 0 ? dy : 0);
    },

    setAuto: function(on, level) {
      if (on && !this.auto) {
        this.auto = true;
        this.setLevel(level);
      } else if (!on && this.auto) {
        this.auto = false;
        this.setdir(0);
      }
    },

    setLevel: function(level) {
      if (this.auto) this.level = Pong.Levels[level];
    },

    update: function(dt, ball) {
      if (this.auto) this.ai(dt, ball);

      var amount = this.down - this.up;
      if (amount != 0) {
        var y = this.y + (amount * dt * this.speed);
        if (y < this.minY)
          y = this.minY;
        else if (y > this.maxY)
          y = this.maxY;
        this.setpos(this.x, y);
      }
    },

    ai: function(dt, ball) {

      // var features = [0.0, 1.0, 2.0, 2.0, 1.0, 1.0, 0.0, 0.0];
      // var features = Array.apply(null, Array(8)).map(function(item, index) {
      //   return Math.random() * 2
      // });

      var features = [this.pong.leftPaddle.y, 0,
                      ball.x, ball.y,
                      ball.dx, ball.dy,
                      ball.x_prev, ball.y_prev].map(function(x) {
        return x / 500.0;
      });

      // features = [for (i of features) i / 500];


      var data = JSON.stringify({"episode_id": Pong.episode_id, "observation": features});
      // console.log(data);
      var self = this;

      var predict_url = "/pong/predict";
      if(window && window.location && window.location.hostname === "localhost") {
        predict_url = "http://localhost:3000";
      }
      if (!Pong.episode_id) {
          console.log("Dont have episode id yet, waiting");
          return;
      }

      // Query Pong server
      Pong.rpc(data, function(data) {
        console.log("Taking action", data);
        if (data.output === 0) {
          // console.log('Staying still');
          self.stopMovingUp();
          self.stopMovingDown();
        } else if (data.output === 1) {
          // console.log('Moving down');
          self.stopMovingUp();
          self.moveDown();
        } else if (data.output === 2) {
          // console.log('Moving up');
          self.stopMovingDown();
          self.moveUp();
        } else {
          // console.log(data.output, 'Unrecognized action. Not moving.');
          self.stopMovingUp();
          self.stopMovingDown();
        }
      });
    },

    predict: function(ball, dt) {
      // only re-predict if the ball changed direction, or its been some amount
      // of time since last prediction
      if (this.prediction && ((this.prediction.dx * ball.dx) > 0) &&
          ((this.prediction.dy * ball.dy) > 0) &&
          (this.prediction.since < this.level.aiReaction)) {
        this.prediction.since += dt;
        return;
      }

      var pt = Pong.Helper.ballIntercept(
          ball,
          {left: this.left, right: this.right, top: -10000, bottom: 10000},
          ball.dx * 10, ball.dy * 10);
      if (pt) {
        var t = this.minY + ball.radius;
        var b = this.maxY + this.height - ball.radius;

        while ((pt.y < t) || (pt.y > b)) {
          if (pt.y < t) {
            pt.y = t + (t - pt.y);
          } else if (pt.y > b) {
            pt.y = t + (b - t) - (pt.y - b);
          }
        }
        this.prediction = pt;
      } else {
        this.prediction = null;
      }

      if (this.prediction) {
        this.prediction.since = 0;
        this.prediction.dx = ball.dx;
        this.prediction.dy = ball.dy;
        this.prediction.radius = ball.radius;
        this.prediction.exactX = this.prediction.x;
        this.prediction.exactY = this.prediction.y;
        var closeness =
            (ball.dx < 0 ? ball.x - this.right : this.left - ball.x) /
            this.pong.width;
        var error = this.level.aiError * closeness;
        this.prediction.y = this.prediction.y + Game.random(-error, error);
      }
    },

    draw: function(ctx) {
      ctx.fillStyle = Pong.Colors.walls;
      ctx.fillRect(this.x, this.y, this.width, this.height);
      if (this.prediction && this.pong.cfg.predictions) {
        ctx.strokeStyle = Pong.Colors.predictionExact;
        ctx.strokeRect(
            this.prediction.x - this.prediction.radius,
            this.prediction.exactY - this.prediction.radius,
            this.prediction.radius * 2, this.prediction.radius * 2);
        ctx.strokeStyle = Pong.Colors.predictionGuess;
        ctx.strokeRect(
            this.prediction.x - this.prediction.radius,
            this.prediction.y - this.prediction.radius,
            this.prediction.radius * 2, this.prediction.radius * 2);
      }
    },

    moveUp: function() {
      this.up = 1;
    },
    moveDown: function() {
      this.down = 1;
    },
    stopMovingUp: function() {
      this.up = 0;
    },
    stopMovingDown: function() {
      this.down = 0;
    }

  },

  //=============================================================================
  // BALL
  //=============================================================================

  Ball: {

    initialize: function(pong) {
      this.pong = pong;
      this.radius = pong.cfg.ballRadius;
      this.minX = this.radius;
      this.maxX = pong.width - this.radius;
      this.minY = pong.cfg.wallWidth + this.radius;
      this.maxY = pong.height - pong.cfg.wallWidth - this.radius;
      this.speed = (this.maxX - this.minX) / pong.cfg.ballSpeed;
      this.accel = pong.cfg.ballAccel;
    },

    reset: function(playerNo) {
      this.footprints = [];
      this.setpos(
          playerNo == 1 ? this.maxX : this.minX,
          Game.random(this.minY, this.maxY));
      this.setdir(playerNo == 1 ? -this.speed : this.speed, this.speed);
    },

    setpos: function(x, y) {
      this.x_prev = this.x == null ? x : this.x;
      this.y_prev = this.y == null ? y : this.y;
      this.x = x;
      this.y = y;
      this.left = this.x - this.radius;
      this.top = this.y - this.radius;
      this.right = this.x + this.radius;
      this.bottom = this.y + this.radius;
    },

    setdir: function(dx, dy) {
      this.dxChanged =
          ((this.dx < 0) != (dx < 0));  // did horizontal direction change
      this.dyChanged =
          ((this.dy < 0) != (dy < 0));  // did vertical direction change
      this.dx = dx;
      this.dy = dy;
    },

    footprint: function() {
      if (this.pong.cfg.footprints) {
        if (!this.footprintCount || this.dxChanged || this.dyChanged) {
          this.footprints.push({x: this.x, y: this.y});
          if (this.footprints.length > 50) this.footprints.shift();
          this.footprintCount = 5;
        } else {
          this.footprintCount--;
        }
      }
    },

    update: function(dt, leftPaddle, rightPaddle) {

      pos = Pong.Helper.accelerate(
          this.x, this.y, this.dx, this.dy, this.accel, dt);

      if ((pos.dy > 0) && (pos.y > this.maxY)) {
        pos.y = this.maxY;
        pos.dy = -pos.dy;
      } else if ((pos.dy < 0) && (pos.y < this.minY)) {
        pos.y = this.minY;
        pos.dy = -pos.dy;
      }

      var paddle = (pos.dx < 0) ? leftPaddle : rightPaddle;
      var pt = Pong.Helper.ballIntercept(this, paddle, pos.nx, pos.ny);
      if (pt) {
          Pong.rpc(
            JSON.stringify(
                {"command": "log_returns", "playerNo": pos.nx < 0 ? 0 : 1, "episode_id": Pong.episode_id, "reward": 1}),
            function(data) {
                console.log("Logged intercept for player", pos.nx < 0 ? 0 : 1);
            });
      }

      if (pt) {
        switch (pt.d) {
          case 'left':
          case 'right':
            pos.x = pt.x;
            pos.dx = -pos.dx;
            break;
          case 'top':
          case 'bottom':
            pos.y = pt.y;
            pos.dy = -pos.dy;
            break;
        }

        // add/remove spin based on paddle direction
        if (paddle.up)
          pos.dy = pos.dy * (pos.dy < 0 ? 0.5 : 1.5);
        else if (paddle.down)
          pos.dy = pos.dy * (pos.dy > 0 ? 0.5 : 1.5);
      }

      this.setpos(pos.x, pos.y);
      this.setdir(pos.dx, pos.dy);
      this.footprint();
    },

    draw: function(ctx) {
      var w = h = this.radius * 2;
      ctx.fillStyle = Pong.Colors.ball;
      ctx.fillRect(this.x - this.radius, this.y - this.radius, w, h);
      if (this.pong.cfg.footprints) {
        var max = this.footprints.length;
        ctx.strokeStyle = Pong.Colors.footprint;
        for (var n = 0; n < max; n++)
          ctx.strokeRect(
              this.footprints[n].x - this.radius,
              this.footprints[n].y - this.radius, w, h);
      }
    }

  },

  //=============================================================================
  // HELPER
  //=============================================================================

  Helper: {

    accelerate: function(x, y, dx, dy, accel, dt) {
      var x2 = x + (dt * dx) + (accel * dt * dt * 0.5);
      var y2 = y + (dt * dy) + (accel * dt * dt * 0.5);
      var dx2 = dx + (accel * dt) * (dx > 0 ? 1 : -1);
      var dy2 = dy + (accel * dt) * (dy > 0 ? 1 : -1);
      return {nx: (x2 - x), ny: (y2 - y), x: x2, y: y2, dx: dx2, dy: dy2};
    },

    intercept: function(x1, y1, x2, y2, x3, y3, x4, y4, d) {
      var denom = ((y4 - y3) * (x2 - x1)) - ((x4 - x3) * (y2 - y1));
      if (denom != 0) {
        var ua = (((x4 - x3) * (y1 - y3)) - ((y4 - y3) * (x1 - x3))) / denom;
        if ((ua >= 0) && (ua <= 1)) {
          var ub = (((x2 - x1) * (y1 - y3)) - ((y2 - y1) * (x1 - x3))) / denom;
          if ((ub >= 0) && (ub <= 1)) {
            var x = x1 + (ua * (x2 - x1));
            var y = y1 + (ua * (y2 - y1));
            return {x: x, y: y, d: d};
          }
        }
      }
      return null;
    },

    ballIntercept: function(ball, rect, nx, ny) {
      var pt;
      if (nx < 0) {
        pt = Pong.Helper.intercept(
            ball.x, ball.y, ball.x + nx, ball.y + ny, rect.right + ball.radius,
            rect.top - ball.radius, rect.right + ball.radius,
            rect.bottom + ball.radius, 'right');
      } else if (nx > 0) {
        pt = Pong.Helper.intercept(
            ball.x, ball.y, ball.x + nx, ball.y + ny, rect.left - ball.radius,
            rect.top - ball.radius, rect.left - ball.radius,
            rect.bottom + ball.radius, 'left');
      }
      if (!pt) {
        if (ny < 0) {
          pt = Pong.Helper.intercept(
              ball.x, ball.y, ball.x + nx, ball.y + ny, rect.left - ball.radius,
              rect.bottom + ball.radius, rect.right + ball.radius,
              rect.bottom + ball.radius, 'bottom');
        } else if (ny > 0) {
          pt = Pong.Helper.intercept(
              ball.x, ball.y, ball.x + nx, ball.y + ny, rect.left - ball.radius,
              rect.top - ball.radius, rect.right + ball.radius,
              rect.top - ball.radius, 'top');
        }
      }
      return pt;
    }

  }

  //=============================================================================

};  // Pong
