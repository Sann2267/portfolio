/* Investigation board: hovering or focusing a case highlights the cases that share its
   technologies, dims the rest, draws connector lines to its related cases, and reports the
   shared technologies in a live status line. Without this file the board is a plain grid. */
(function () {
  "use strict";

  var board = document.querySelector("[data-board]");
  if (!board) return;

  var cards = Array.prototype.slice.call(board.querySelectorAll(".case-card"));
  var lines = Array.prototype.slice.call(board.querySelectorAll(".board__line"));
  var status = document.querySelector("[data-board-status]");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var active = null;

  function techSet(card) {
    var raw = card.getAttribute("data-tech") || "";
    var set = {};
    raw.split("|").forEach(function (name) {
      if (name) set[name.toLowerCase()] = name;
    });
    return set;
  }

  function shared(a, b) {
    var setA = techSet(a);
    var setB = techSet(b);
    return Object.keys(setA).filter(function (key) { return setB[key]; }).map(function (key) { return setA[key]; });
  }

  function pin(card) {
    var boardRect = board.getBoundingClientRect();
    var rect = card.getBoundingClientRect();
    return { x: rect.left - boardRect.left + rect.width / 2, y: rect.top - boardRect.top };
  }

  function drawLines(slug) {
    lines.forEach(function (line) {
      var from = line.getAttribute("data-from");
      var to = line.getAttribute("data-to");
      if (from !== slug && to !== slug) {
        line.classList.remove("is-visible");
        return;
      }
      var a = board.querySelector('.case-card[data-slug="' + from + '"]');
      var b = board.querySelector('.case-card[data-slug="' + to + '"]');
      if (!a || !b) return;
      var p1 = pin(a);
      var p2 = pin(b);
      var lift = Math.min(60, Math.abs(p1.x - p2.x) / 4 + 16);
      line.setAttribute(
        "d",
        "M" + p1.x + " " + p1.y + " C " + p1.x + " " + (p1.y - lift) + ", " + p2.x + " " + (p2.y - lift) + ", " + p2.x + " " + p2.y
      );
      line.classList.add("is-visible");
    });
  }

  function report(card, count, names) {
    if (!status) return;
    var id = card.querySelector(".case-card__id");
    var label = id ? id.textContent.trim() : card.getAttribute("data-slug");
    if (!count) {
      status.innerHTML = "<strong>" + label + "</strong> shares no catalogued technology with another case.";
      return;
    }
    var shown = names.slice(0, 5).join(", ");
    var more = names.length > 5 ? " +" + (names.length - 5) + " more" : "";
    status.innerHTML =
      "<strong>" + label + "</strong> shares " + shown + more + " with " + count + " other case" + (count === 1 ? "" : "s") + ".";
  }

  function highlight(card) {
    if (active === card) return;
    active = card;
    var related = 0;
    var names = {};
    cards.forEach(function (other) {
      if (other === card) {
        other.classList.add("is-highlighted");
        other.classList.remove("is-dimmed");
        return;
      }
      var common = shared(card, other);
      if (common.length) {
        related += 1;
        common.forEach(function (name) { names[name] = true; });
        other.classList.add("is-highlighted");
        other.classList.remove("is-dimmed");
      } else {
        other.classList.remove("is-highlighted");
        other.classList.add("is-dimmed");
      }
    });
    if (!reduceMotion) drawLines(card.getAttribute("data-slug"));
    report(card, related, Object.keys(names));
  }

  function clear() {
    active = null;
    cards.forEach(function (card) { card.classList.remove("is-highlighted", "is-dimmed"); });
    lines.forEach(function (line) { line.classList.remove("is-visible"); });
    if (status) status.textContent = "";
  }

  cards.forEach(function (card) {
    card.addEventListener("mouseenter", function () { highlight(card); });
    card.addEventListener("focusin", function () { highlight(card); });
  });
  board.addEventListener("mouseleave", clear);
  board.addEventListener("focusout", function (event) {
    if (!board.contains(event.relatedTarget)) clear();
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") clear();
  });
  window.addEventListener("resize", function () {
    if (active && !reduceMotion) drawLines(active.getAttribute("data-slug"));
  });
})();
