/* Command palette (Ctrl+K / Cmd+K): static page and case commands plus live search results
   from the same /search endpoint. It is a shortcut, never the only way to navigate. */
(function () {
  "use strict";

  var dialog = document.querySelector("[data-palette]");
  if (!dialog || typeof dialog.showModal !== "function") return;

  var input = dialog.querySelector("[data-palette-input]");
  var list = dialog.querySelector("[data-palette-list]");
  var searchUrl = dialog.getAttribute("data-search-url");
  var commands = Array.prototype.slice.call(list.querySelectorAll("[data-command]"));
  var timer = null;
  var active = -1;

  function visibleItems() {
    return Array.prototype.slice.call(list.querySelectorAll(".palette__item")).filter(function (el) {
      return !el.hidden;
    });
  }

  function setActive(index) {
    var items = visibleItems();
    items.forEach(function (el) { el.classList.remove("is-active"); });
    if (!items.length) {
      active = -1;
      return;
    }
    active = ((index % items.length) + items.length) % items.length;
    items[active].classList.add("is-active");
    items[active].scrollIntoView({ block: "nearest" });
  }

  function removeDynamic() {
    Array.prototype.slice.call(list.querySelectorAll("[data-dynamic]")).forEach(function (el) { el.remove(); });
  }

  function applyQuery(query) {
    var q = query.trim().toLowerCase();
    commands.forEach(function (el) {
      el.hidden = q.length > 0 && el.getAttribute("data-label").indexOf(q) === -1;
    });
    removeDynamic();
    setActive(0);
    if (q.length < 2 || !searchUrl) return;
    clearTimeout(timer);
    timer = setTimeout(function () {
      fetch(searchUrl + "?q=" + encodeURIComponent(q) + "&partial=palette", {
        headers: { "HX-Request": "true" },
        credentials: "same-origin",
      })
        .then(function (response) { return response.ok ? response.text() : ""; })
        .then(function (html) {
          if (input.value.trim().toLowerCase() !== q) return;
          removeDynamic();
          list.insertAdjacentHTML("afterbegin", html);
          setActive(0);
        })
        .catch(function () {});
    }, 180);
  }

  function open() {
    if (dialog.open) return;
    dialog.showModal();
    input.value = "";
    applyQuery("");
    setTimeout(function () { input.focus(); }, 0);
  }

  function close() {
    if (dialog.open) dialog.close();
  }

  function go() {
    var items = visibleItems();
    var target = items[active] || items[0];
    var link = target ? target.querySelector("a") : null;
    if (link) {
      window.location.href = link.getAttribute("href");
      return true;
    }
    return false;
  }

  document.addEventListener("keydown", function (event) {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      if (dialog.open) close();
      else open();
    }
  });

  Array.prototype.slice.call(document.querySelectorAll("[data-palette-open]")).forEach(function (trigger) {
    trigger.addEventListener("click", function (event) {
      event.preventDefault();
      open();
    });
  });

  input.addEventListener("input", function () { applyQuery(input.value); });

  dialog.addEventListener("keydown", function (event) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive(active + 1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive(active - 1);
    } else if (event.key === "Enter") {
      if (go()) event.preventDefault();
    } else if (event.key === "Escape") {
      event.preventDefault();
      close();
    }
  });

  dialog.querySelector("form").addEventListener("submit", function (event) {
    if (go()) event.preventDefault();
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) close();
  });

  list.addEventListener("mousemove", function (event) {
    var item = event.target.closest(".palette__item");
    if (!item) return;
    var index = visibleItems().indexOf(item);
    if (index >= 0 && index !== active) setActive(index);
  });
})();
