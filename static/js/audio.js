/* Optional sound effects for the case-room scene, synthesised with the Web Audio API: no audio
   files, nothing fetched, so the Content-Security-Policy stays as it is. Off until the visitor
   turns the speaker on; the choice is kept in localStorage. scene.js asks for a sound by
   dispatching a "caseroom:sfx" event. Without this file the scene is silent. */
(function () {
  "use strict";

  var scene = document.querySelector("[data-scene]");
  var button = scene ? scene.querySelector('[data-scene-action="sound"]') : null;
  var Context = window.AudioContext || window.webkitAudioContext;
  if (!scene || !button || !Context) return;

  var KEY = "caseroom.sound";
  var stateLabel = button.querySelector("[data-scene-sound-state]");
  var status = scene.querySelector("[data-scene-status]");
  var ctx = null;
  var master = null;
  var white = null;
  var brown = null;
  var rain = null;
  var lastKey = 0;
  var enabled = read() === "on";

  function read() {
    try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function write(value) {
    try { window.localStorage.setItem(KEY, value); } catch (e) { /* private mode */ }
  }

  function reflect() {
    button.setAttribute("aria-pressed", enabled ? "true" : "false");
    if (stateLabel) stateLabel.textContent = enabled ? "on" : "off";
  }

  /* One second of white noise, or two seconds of brown noise (a leaky integrator of white). */
  function noise(seconds, brownian) {
    var length = Math.floor(ctx.sampleRate * seconds);
    var buffer = ctx.createBuffer(1, length, ctx.sampleRate);
    var data = buffer.getChannelData(0);
    var last = 0;
    for (var i = 0; i < length; i++) {
      var w = Math.random() * 2 - 1;
      if (brownian) {
        last = (last + 0.02 * w) / 1.02;
        data[i] = last * 3.5;
      } else {
        data[i] = w;
      }
    }
    return buffer;
  }

  function ensure() {
    if (ctx) return ctx;
    ctx = new Context();
    master = ctx.createGain();
    master.gain.value = 0.6;
    master.connect(ctx.destination);
    white = noise(1, false);
    brown = noise(2, true);
    return ctx;
  }

  function filter(type, frequency, q) {
    var node = ctx.createBiquadFilter();
    node.type = type;
    node.frequency.value = frequency;
    if (q) node.Q.value = q;
    return node;
  }

  /* Gain that rises to `peak` over `attack` seconds and decays to silence over `decay`. */
  function envelope(peak, attack, decay, now) {
    var gain = ctx.createGain();
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.linearRampToValueAtTime(peak, now + attack);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + attack + decay);
    gain.connect(master);
    return gain;
  }

  function burst(filterNode, peak, attack, decay, now) {
    var source = ctx.createBufferSource();
    source.buffer = white;
    source.connect(filterNode);
    filterNode.connect(envelope(peak, attack, decay, now));
    source.start(now);
    source.stop(now + attack + decay + 0.05);
  }

  function tone(type, frequency, peak, decay, now) {
    var osc = ctx.createOscillator();
    osc.type = type;
    osc.frequency.value = frequency;
    osc.connect(envelope(peak, 0.002, decay, now));
    osc.start(now);
    osc.stop(now + decay + 0.06);
  }

  var sounds = {
    click: function (now) {
      burst(filter("bandpass", 1800, 1.2), 0.5, 0.002, 0.06, now);
      tone("sine", 620, 0.15, 0.04, now);
    },
    key: function (now) {
      if (now - lastKey < 0.045) return;
      lastKey = now;
      burst(filter("highpass", 2500 + (Math.random() * 600 - 300)), 0.25, 0.001, 0.035, now);
    },
    paper: function (now) {
      var sweep = filter("lowpass", 400);
      sweep.frequency.linearRampToValueAtTime(1200, now + 0.22);
      burst(sweep, 0.18, 0.04, 0.18, now);
    },
    stamp: function (now) {
      tone("sine", 140, 0.35, 0.09, now);
      burst(filter("lowpass", 600), 0.3, 0.002, 0.05, now);
    },
    rain: function (now) {
      if (rain) return;
      var source = ctx.createBufferSource();
      var gain = ctx.createGain();
      source.buffer = brown;
      source.loop = true;
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.linearRampToValueAtTime(0.05, now + 0.8);
      source.connect(filter("lowpass", 900)).connect(gain).connect(master);
      source.start(now);
      rain = { source: source, gain: gain };
    },
    "rain-stop": function (now) {
      if (!rain) return;
      var current = rain;
      rain = null;
      current.gain.gain.cancelScheduledValues(now);
      current.gain.gain.setValueAtTime(current.gain.gain.value, now);
      current.gain.gain.linearRampToValueAtTime(0.0001, now + 0.6);
      current.source.stop(now + 0.65);
    }
  };

  function play(name) {
    var sound = sounds[name];
    if (!enabled || !sound) return;
    ensure();
    if (ctx.state !== "running") {
      /* Browsers keep a context suspended until the visitor interacts with the page. */
      ctx.resume();
      if (ctx.state !== "running") return;
    }
    sound(ctx.currentTime);
  }

  scene.addEventListener("caseroom:sfx", function (event) {
    play(event.detail && event.detail.name);
  });

  button.addEventListener("click", function () {
    enabled = !enabled;
    write(enabled ? "on" : "off");
    reflect();
    if (enabled) {
      ensure();
      ctx.resume().then(function () { play("click"); });
      if (status) status.textContent = "Sound on.";
    } else {
      if (ctx) {
        sounds["rain-stop"](ctx.currentTime);
        ctx.suspend();
      }
      if (status) status.textContent = "Sound off.";
    }
  });

  /* A stored "on" cannot unlock audio by itself; the first click or key press does. */
  document.addEventListener("click", function () {
    if (enabled && ctx && ctx.state === "suspended" && !document.hidden) ctx.resume();
  });

  document.addEventListener("visibilitychange", function () {
    if (!ctx) return;
    if (document.hidden) ctx.suspend();
    else if (enabled) ctx.resume();
  });

  window.addEventListener("pagehide", function () {
    if (ctx) ctx.suspend();
  });

  reflect();
})();
