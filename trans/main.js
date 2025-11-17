"use strict";
(() => {
  var __typeError = (msg) => {
    throw TypeError(msg);
  };
  var __pow = Math.pow;
  var __accessCheck = (obj, member, msg) => member.has(obj) || __typeError("Cannot " + msg);
  var __privateGet = (obj, member, getter) => (__accessCheck(obj, member, "read from private field"), getter ? getter.call(obj) : member.get(obj));
  var __privateAdd = (obj, member, value) => member.has(obj) ? __typeError("Cannot add the same private member more than once") : member instanceof WeakSet ? member.add(obj) : member.set(obj, value);
  var __privateSet = (obj, member, value, setter) => (__accessCheck(obj, member, "write to private field"), setter ? setter.call(obj, value) : member.set(obj, value), value);
  var __privateMethod = (obj, member, method) => (__accessCheck(obj, member, "access private method"), method);
  var __async = (__this, __arguments, generator) => {
    return new Promise((resolve, reject) => {
      var fulfilled = (value) => {
        try {
          step(generator.next(value));
        } catch (e) {
          reject(e);
        }
      };
      var rejected = (value) => {
        try {
          step(generator.throw(value));
        } catch (e) {
          reject(e);
        }
      };
      var step = (x) => x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected);
      step((generator = generator.apply(__this, __arguments)).next());
    });
  };

  // Game.ts
  var _ctx, _height, _width, _rect, _player1x, _player2x, _player1y, _player2y, _player_len, _player_speed, _player_width, _ball_size, _ball_x, _ball_y, _ball_speed, _ball_dx, _ball_dy, _score_a, _score_b, _active, _Game_instances, draw_line_fn, draw_table_player_fn, check_player_fn, draw_ball_fn, update_ball_fn, check_areas_fn, check_player1_fn, check_player2_fn, goal_fn, reset_game_fn, sleep_helper_fn, find_way_fn, update_ai_fn;
  var Game = class {
    constructor(ctx, canvas) {
      __privateAdd(this, _Game_instances);
      __privateAdd(this, _ctx);
      __privateAdd(this, _height);
      __privateAdd(this, _width);
      __privateAdd(this, _rect);
      __privateAdd(this, _player1x);
      __privateAdd(this, _player2x);
      __privateAdd(this, _player1y);
      __privateAdd(this, _player2y);
      __privateAdd(this, _player_len);
      __privateAdd(this, _player_speed);
      __privateAdd(this, _player_width);
      __privateAdd(this, _ball_size);
      __privateAdd(this, _ball_x);
      __privateAdd(this, _ball_y);
      __privateAdd(this, _ball_speed);
      __privateAdd(this, _ball_dx);
      __privateAdd(this, _ball_dy);
      __privateAdd(this, _score_a);
      __privateAdd(this, _score_b);
      __privateAdd(this, _active);
      __privateSet(this, _ctx, ctx);
      __privateSet(this, _height, canvas.height);
      __privateSet(this, _width, canvas.width);
      __privateSet(this, _rect, canvas.getBoundingClientRect());
      __privateSet(this, _score_a, 0);
      __privateSet(this, _score_b, 0);
      __privateSet(this, _player1x, 20);
      __privateSet(this, _player2x, __privateGet(this, _width) - 20);
      __privateSet(this, _player_len, __privateGet(this, _width) * 2 / 17.96);
      __privateSet(this, _player_width, 10);
      __privateSet(this, _ball_size, __privateGet(this, _width) * 2 / 68.5);
      __privateSet(this, _player_speed, 10);
      __privateSet(this, _ball_x, __privateGet(this, _width) / 2);
      __privateSet(this, _ball_y, __privateGet(this, _height) / 2);
      __privateSet(this, _ball_dx, 1);
      __privateSet(this, _ball_dy, 0);
      __privateSet(this, _ball_speed, 8);
      __privateSet(this, _player1y, 10);
      __privateSet(this, _player2y, __privateGet(this, _height) - __privateGet(this, _player_len) - 10);
      __privateSet(this, _active, 0);
      const startButton = document.getElementById("startButton");
      const buttonWidth = __privateGet(this, _width) * 1.5 / 10;
      const buttonHeight = __privateGet(this, _height) * 1.5 / 10;
      if (startButton instanceof HTMLElement) {
        startButton.style.position = "absolute";
        startButton.style.left = __privateGet(this, _rect).left + (__privateGet(this, _width) - buttonWidth) / 2 + "px";
        startButton.style.top = __privateGet(this, _rect).top + (__privateGet(this, _height) - buttonHeight) / 2 + "px";
        startButton.style.width = buttonWidth + "px";
        startButton.style.height = buttonHeight + "px";
        startButton.style.borderRadius = "15px";
        startButton.style.display = "none";
      }
    }
    animate() {
      __privateGet(this, _ctx).clearRect(0, 0, __privateGet(this, _width), __privateGet(this, _height));
      __privateMethod(this, _Game_instances, draw_table_player_fn).call(this);
      __privateMethod(this, _Game_instances, draw_ball_fn).call(this);
      __privateMethod(this, _Game_instances, update_ball_fn).call(this);
      __privateMethod(this, _Game_instances, check_areas_fn).call(this);
    }
    update_height(player_no, inc) {
      __privateSet(this, _active, 1);
      if (player_no == 0) {
        __privateSet(this, _player1y, __privateGet(this, _player1y) + __privateMethod(this, _Game_instances, check_player_fn).call(this, __privateGet(this, _player1y), inc));
      }
      if (player_no == 1) {
        __privateSet(this, _player2y, __privateGet(this, _player2y) + __privateMethod(this, _Game_instances, check_player_fn).call(this, __privateGet(this, _player2y), inc));
      }
    }
    sleep(ms) {
      return __async(this, null, function* () {
        yield __privateMethod(this, _Game_instances, sleep_helper_fn).call(this, ms);
      });
    }
    run_ai(player) {
      if (player == 0)
        __privateMethod(this, _Game_instances, update_ai_fn).call(this, 0, __privateGet(this, _player1y));
      else
        __privateMethod(this, _Game_instances, update_ai_fn).call(this, 1, __privateGet(this, _player2y));
    }
  };
  _ctx = new WeakMap();
  _height = new WeakMap();
  _width = new WeakMap();
  _rect = new WeakMap();
  _player1x = new WeakMap();
  _player2x = new WeakMap();
  _player1y = new WeakMap();
  _player2y = new WeakMap();
  _player_len = new WeakMap();
  _player_speed = new WeakMap();
  _player_width = new WeakMap();
  _ball_size = new WeakMap();
  _ball_x = new WeakMap();
  _ball_y = new WeakMap();
  _ball_speed = new WeakMap();
  _ball_dx = new WeakMap();
  _ball_dy = new WeakMap();
  _score_a = new WeakMap();
  _score_b = new WeakMap();
  _active = new WeakMap();
  _Game_instances = new WeakSet();
  draw_line_fn = function(x, y, dx, dy, lineWidth = 10) {
    __privateGet(this, _ctx).beginPath();
    __privateGet(this, _ctx).strokeStyle = "black";
    __privateGet(this, _ctx).lineWidth = lineWidth;
    __privateGet(this, _ctx).moveTo(x, y);
    __privateGet(this, _ctx).lineTo(x + dx, y + dy);
    __privateGet(this, _ctx).stroke();
  };
  draw_table_player_fn = function() {
    __privateMethod(this, _Game_instances, draw_line_fn).call(this, 0, 0, __privateGet(this, _width), 0);
    __privateMethod(this, _Game_instances, draw_line_fn).call(this, 0, 0, 0, __privateGet(this, _height));
    __privateMethod(this, _Game_instances, draw_line_fn).call(this, __privateGet(this, _width), 0, 0, __privateGet(this, _height));
    __privateMethod(this, _Game_instances, draw_line_fn).call(this, 0, __privateGet(this, _height), __privateGet(this, _width), 0);
    __privateMethod(this, _Game_instances, draw_line_fn).call(this, __privateGet(this, _width) / 2, 0, 0, __privateGet(this, _height), 5);
    __privateMethod(this, _Game_instances, draw_line_fn).call(this, __privateGet(this, _player1x), __privateGet(this, _player1y), 0, __privateGet(this, _player_len), __privateGet(this, _player_width));
    __privateMethod(this, _Game_instances, draw_line_fn).call(this, __privateGet(this, _player2x), __privateGet(this, _player2y), 0, __privateGet(this, _player_len), __privateGet(this, _player_width));
  };
  check_player_fn = function(player_loc, inc) {
    if (inc > 0) {
      return Math.min(inc * __privateGet(this, _player_speed), __privateGet(this, _height) - __privateGet(this, _player_len) - player_loc);
    }
    return Math.max(inc * __privateGet(this, _player_speed), -player_loc);
  };
  draw_ball_fn = function() {
    __privateGet(this, _ctx).fillStyle = "orange";
    __privateGet(this, _ctx).beginPath();
    __privateGet(this, _ctx).arc(__privateGet(this, _ball_x), __privateGet(this, _ball_y), __privateGet(this, _ball_size) / 2, 0, Math.PI * 2);
    __privateGet(this, _ctx).fill();
  };
  update_ball_fn = function() {
    if (__privateGet(this, _active) == 0) {
      return;
    }
    __privateSet(this, _ball_x, __privateGet(this, _ball_x) + __privateGet(this, _ball_dx) * __privateGet(this, _ball_speed));
    __privateSet(this, _ball_y, __privateGet(this, _ball_y) + __privateGet(this, _ball_dy) * __privateGet(this, _ball_speed));
  };
  check_areas_fn = function() {
    if (__privateGet(this, _ball_size) > __privateGet(this, _ball_y) && __privateGet(this, _ball_dy) < 0) {
      __privateSet(this, _ball_dy, __privateGet(this, _ball_dy) * -1);
    } else if (__privateGet(this, _height) - __privateGet(this, _ball_y) < __privateGet(this, _ball_size) && __privateGet(this, _ball_dy) > 0) {
      __privateSet(this, _ball_dy, __privateGet(this, _ball_dy) * -1);
    }
    if (__privateGet(this, _ball_size) > __privateGet(this, _ball_x)) {
      __privateMethod(this, _Game_instances, goal_fn).call(this, 1);
    }
    if (__privateGet(this, _width) - __privateGet(this, _ball_x) < __privateGet(this, _ball_size)) {
      __privateMethod(this, _Game_instances, goal_fn).call(this, 0);
    }
    if (__privateGet(this, _ball_dx) < 0 && __privateGet(this, _player1x) + __privateGet(this, _player_width) + __privateGet(this, _ball_size) / 2 > __privateGet(this, _ball_x)) {
      __privateMethod(this, _Game_instances, check_player1_fn).call(this);
    }
    if (__privateGet(this, _ball_dx) > 0 && __privateGet(this, _player2x) - __privateGet(this, _player_width) - __privateGet(this, _ball_size) / 2 < __privateGet(this, _ball_x)) {
      __privateMethod(this, _Game_instances, check_player2_fn).call(this);
    }
  };
  check_player1_fn = function() {
    if (__privateGet(this, _player1y) > __privateGet(this, _ball_y)) {
    } else if (__privateGet(this, _ball_dx) < 0 && __privateGet(this, _player1y) + __privateGet(this, _player_len) - __privateGet(this, _ball_size) / 2 > __privateGet(this, _ball_y)) {
      let dist = (__privateGet(this, _ball_y) - (__privateGet(this, _player1y) + __privateGet(this, _player_len) / 2)) / (__privateGet(this, _player_len) / 2);
      let angle = dist * (Math.PI / 4);
      let speed = Math.sqrt(__pow(__privateGet(this, _ball_dx), 2) + __pow(__privateGet(this, _ball_dy), 2));
      __privateSet(this, _ball_dx, Math.cos(angle) * speed);
      __privateSet(this, _ball_dy, Math.sin(angle) * speed);
      __privateSet(this, _ball_speed, __privateGet(this, _ball_speed) * 1.05);
    } else if (__privateGet(this, _player1y) + __privateGet(this, _player_len) + __privateGet(this, _ball_size) / 2 > __privateGet(this, _ball_y)) {
    }
  };
  check_player2_fn = function() {
    if (__privateGet(this, _player2y) > __privateGet(this, _ball_y)) {
    } else if (__privateGet(this, _ball_dx) > 0 && __privateGet(this, _player2y) + __privateGet(this, _player_len) - __privateGet(this, _ball_size) / 2 > __privateGet(this, _ball_y)) {
      let dist = (__privateGet(this, _ball_y) - (__privateGet(this, _player2y) + __privateGet(this, _player_len) / 2)) / (__privateGet(this, _player_len) / 2);
      let angle = dist * (Math.PI / 4);
      let speed = Math.sqrt(__pow(__privateGet(this, _ball_dx), 2) + __pow(__privateGet(this, _ball_dy), 2));
      __privateSet(this, _ball_dx, -Math.cos(angle) * speed);
      __privateSet(this, _ball_dy, Math.sin(angle) * speed);
      __privateSet(this, _ball_speed, __privateGet(this, _ball_speed) * 1.05);
    } else if (__privateGet(this, _player2y) + __privateGet(this, _player_len) + __privateGet(this, _ball_size) / 2 > __privateGet(this, _ball_y)) {
    }
  };
  goal_fn = function(team_no) {
    if (team_no == 0) {
      __privateSet(this, _score_a, __privateGet(this, _score_a) + 1);
    } else {
      __privateSet(this, _score_b, __privateGet(this, _score_b) + 1);
    }
    const diva = document.getElementById("scoreA");
    const divb = document.getElementById("scoreB");
    if (diva) {
      diva.textContent = "A: " + __privateGet(this, _score_a);
    }
    if (divb) {
      divb.textContent = "B: " + __privateGet(this, _score_b);
    }
    __privateMethod(this, _Game_instances, reset_game_fn).call(this);
  };
  reset_game_fn = function() {
    __privateSet(this, _ball_x, __privateGet(this, _width) / 2);
    __privateSet(this, _ball_y, __privateGet(this, _height) / 2);
    __privateSet(this, _ball_dx, -1);
    __privateSet(this, _ball_dy, 0);
    __privateSet(this, _ball_speed, 8);
    __privateSet(this, _player1y, 10);
    __privateSet(this, _player2y, __privateGet(this, _height) - __privateGet(this, _player_len) - 10);
    __privateSet(this, _active, 0);
  };
  sleep_helper_fn = function(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  };
  find_way_fn = function(position) {
    if (position + __privateGet(this, _player_len) / 2 > __privateGet(this, _ball_y))
      return -1;
    return 1;
  };
  update_ai_fn = function(player, position) {
    let way = __privateMethod(this, _Game_instances, find_way_fn).call(this, position);
    this.update_height(player, way);
    this.sleep(1e3);
  };

  // script.ts
  window.onload = function() {
    const ratio = 1.79672131148;
    const canvas = document.getElementById("my_canvas");
    if (!canvas) {
      throw new Error("Canvas element not found");
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      throw new Error("Could not get 2d context");
    }
    canvas.height = window.innerHeight * 0.6;
    canvas.width = canvas.height * ratio;
    const dt = new Game(ctx, canvas);
    const pressedKeys = /* @__PURE__ */ new Set();
    document.addEventListener("keydown", (event) => {
      if (event.key === "ArrowUp" || event.key === "ArrowDown") {
        event.preventDefault();
      }
      pressedKeys.add(event.key);
    });
    document.addEventListener("keyup", (event) => {
      pressedKeys.delete(event.key);
    });
    function gameLoop() {
      if (pressedKeys.has("ArrowUp")) {
        dt.update_height(1, -1);
      }
      if (pressedKeys.has("ArrowDown")) {
        dt.update_height(1, 1);
      }
      if (pressedKeys.has("w")) {
        dt.update_height(0, -1);
      }
      if (pressedKeys.has("s")) {
        dt.update_height(0, 1);
      }
      dt.animate();
      dt.run_ai(1);
      requestAnimationFrame(gameLoop);
    }
    gameLoop();
  };
})();
