/* Case-room scene: the opening cutscene (a data-step state machine styled in scene.css), typed
   subtitles, skip and replay, the lamp's "show object labels" toggle, and sound-effect events
   for audio.js. The intro plays once per tab (sessionStorage) and never under reduced motion.
   Without this file the room renders lit and every hotspot is a plain link. */
(function () {
  "use strict";

  var scene = document.querySelector("[data-scene]");
  if (!scene) return;

  var caption = scene.querySelector("[data-scene-caption]");
  var status = scene.querySelector("[data-scene-status]");
  var skipButton = scene.querySelector('[data-scene-action="skip"]');
  var replayButton = scene.querySelector('[data-scene-action="replay"]');
  var lamp = scene.querySelector('[data-scene-action="labels"]');
  var lines = Array.prototype.slice.call(scene.querySelectorAll("[data-scene-script] li")).map(function (li) {
    return li.textContent.trim();
  });
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var SEEN_KEY = "caseroom.introSeen";
  var CHAR_MS = 20;
  var timers = [];
  var typer = null;
  var playing = false;

  /* [ms, kind, value]: "step" sets data-step, "say" types a line, "sfx" asks audio.js for a
     sound, "finish" ends the intro, "clear" empties the subtitle band. */
  var TIMELINE = [
    [0, "step", "0"], [0, "say", 0], [0, "sfx", "rain"],
    [1700, "step", "1"], [1700, "sfx", "click"],
    [2900, "say", 1],
    [4300, "step", "2"], [4300, "sfx", "paper"],
    [5100, "step", "3"], [5100, "sfx", "stamp"],
    [5300, "say", 2],
    [6700, "step", "4"],
    [6900, "say", 3],
    [8900, "finish"],
    [9500, "clear"]
  ];

  function seen() {
    try { return window.sessionStorage.getItem(SEEN_KEY) === "1"; } catch (e) { return false; }
  }

  function remember() {
    try { window.sessionStorage.setItem(SEEN_KEY, "1"); } catch (e) { /* private mode: play again next time */ }
  }

  function announce(text) {
    if (status) status.textContent = text;
  }

  function sfx(name) {
    if (typeof CustomEvent !== "function") return;
    scene.dispatchEvent(new CustomEvent("caseroom:sfx", { detail: { name: name } }));
  }

  function setStep(value) {
    scene.setAttribute("data-step", value);
  }

  /* Apply a state without playing its transitions (skip, replay from the end). */
  function instant(apply) {
    scene.classList.add("scene--instant");
    apply();
    void scene.offsetWidth;
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { scene.classList.remove("scene--instant"); });
    });
  }

  function stopTimers() {
    timers.forEach(function (id) { clearTimeout(id); });
    timers = [];
  }

  function stopTyping() {
    if (typer) { clearInterval(typer); typer = null; }
    if (caption) caption.classList.remove("cursor");
  }

  function say(index) {
    var text = lines[index] || "";
    stopTyping();
    if (!caption) return;
    if (reduceMotion || scene.classList.contains("scene--still")) {
      caption.textContent = text;
      return;
    }
    var shown = 0;
    caption.textContent = "";
    caption.classList.add("cursor");
    typer = setInterval(function () {
      shown += 1;
      caption.textContent = text.slice(0, shown);
      if (shown % 2 === 0) sfx("key");
      if (shown >= text.length) stopTyping();
    }, CHAR_MS);
  }

  function pulseLabels() {
    scene.classList.remove("scene--pulse");
    void scene.offsetWidth;
    scene.classList.add("scene--pulse");
  }

  function finish(skipped) {
    playing = false;
    stopTyping();
    if (skipped) {
      stopTimers();
      if (caption) caption.textContent = "";
      instant(function () { setStep("done"); });
    } else {
      setStep("done");
    }
    sfx("rain-stop");
    remember();
    pulseLabels();
    if (skipped) announce("Intro skipped. Click an object in the room, or scroll down to the case files.");
  }

  function run(entry) {
    var kind = entry[1];
    if (kind === "step") setStep(entry[2]);
    else if (kind === "say") say(entry[2]);
    else if (kind === "sfx") sfx(entry[2]);
    else if (kind === "finish") finish(false);
    else if (kind === "clear" && caption) caption.textContent = "";
  }

  function start(still) {
    stopTimers();
    stopTyping();
    if (caption) caption.textContent = "";
    scene.classList.toggle("scene--still", !!still);
    scene.classList.remove("scene--pulse");
    playing = true;
    instant(function () { setStep("0"); });
    TIMELINE.forEach(function (entry) {
      timers.push(setTimeout(function () { run(entry); }, entry[0]));
    });
  }

  function skip() {
    var focusWasOnSkip = document.activeElement === skipButton;
    finish(true);
    if (focusWasOnSkip && replayButton) replayButton.focus();
  }

  if (skipButton) skipButton.addEventListener("click", skip);
  if (replayButton) replayButton.addEventListener("click", function () { start(reduceMotion); });

  if (lamp) {
    lamp.addEventListener("click", function () {
      var on = scene.getAttribute("data-labels") !== "on";
      if (on) scene.setAttribute("data-labels", "on");
      else scene.removeAttribute("data-labels");
      lamp.setAttribute("aria-pressed", on ? "true" : "false");
      sfx("click");
      announce(on ? "Object labels shown." : "Object labels hidden.");
    });
  }

  document.addEventListener("keydown", function (event) {
    if (!playing || document.querySelector("dialog[open]")) return;
    var idle = document.activeElement === document.body || document.activeElement === skipButton;
    if (event.key === "Escape" || (event.key === "Enter" && idle)) {
      event.preventDefault();
      skip();
    }
  });

  if (!seen() && !reduceMotion && !window.location.hash) start(false);
  else setStep("done");
})();
