/* Architecture diagram: hover or focus a component to highlight its connections and dim the
   rest; select it (click, Enter, Space) to pin the highlight and load its server-rendered
   details into the drawer. Without this file the SVG is static and nodes link to the text
   version below the diagram. */
(function () {
  "use strict";

  var figure = document.querySelector("[data-arch]");
  if (!figure) return;

  var svg = figure.querySelector("svg");
  var nodes = Array.prototype.slice.call(svg.querySelectorAll(".arch__node"));
  var edges = Array.prototype.slice.call(svg.querySelectorAll(".arch__edge"));
  var edgeLabels = Array.prototype.slice.call(svg.querySelectorAll(".arch__edge-label"));
  var drawer = document.getElementById("arch-detail");
  var drawerBody = drawer ? drawer.querySelector(".drawer__body") : null;
  var pinned = null;

  function connected(id) {
    var ids = {};
    ids[id] = true;
    edges.forEach(function (edge) {
      var s = edge.getAttribute("data-source");
      var t = edge.getAttribute("data-target");
      if (s === id) ids[t] = true;
      if (t === id) ids[s] = true;
    });
    return ids;
  }

  function highlight(id) {
    var ids = connected(id);
    nodes.forEach(function (node) {
      var own = node.getAttribute("data-node");
      node.classList.toggle("is-active", own === id);
      node.classList.toggle("is-linked", own !== id && !!ids[own]);
      node.classList.toggle("is-dim", !ids[own]);
    });
    edges.forEach(function (edge) {
      var on = edge.getAttribute("data-source") === id || edge.getAttribute("data-target") === id;
      edge.classList.toggle("is-active", on);
      edge.classList.toggle("is-dim", !on);
    });
    edgeLabels.forEach(function (label) {
      var edge = svg.querySelector('[data-edge="' + label.getAttribute("data-edge-label") + '"]');
      var on = !!(edge && edge.classList.contains("is-active"));
      label.classList.toggle("is-dim", !on);
      label.classList.toggle("is-on", on);
    });
  }

  function clear() {
    if (pinned) {
      highlight(pinned);
      return;
    }
    nodes.forEach(function (node) { node.classList.remove("is-active", "is-linked", "is-dim"); });
    edges.forEach(function (edge) { edge.classList.remove("is-active", "is-dim"); });
    edgeLabels.forEach(function (label) { label.classList.remove("is-dim", "is-on"); });
  }

  function closeDrawer() {
    pinned = null;
    if (drawer) drawer.hidden = true;
    clear();
  }

  function select(node) {
    var id = node.getAttribute("data-node");
    var url = node.getAttribute("data-detail-url");
    pinned = id;
    highlight(id);
    if (!drawer || !drawerBody || !url) return;
    drawer.hidden = false;
    drawerBody.setAttribute("aria-busy", "true");
    fetch(url, { headers: { "HX-Request": "true" }, credentials: "same-origin" })
      .then(function (response) { return response.ok ? response.text() : Promise.reject(response.status); })
      .then(function (html) {
        drawerBody.innerHTML = html;
        drawerBody.removeAttribute("aria-busy");
        var heading = drawer.querySelector(".drawer__head h3");
        var title = drawerBody.querySelector(".node-detail__title");
        if (heading && title) heading.textContent = title.textContent;
      })
      .catch(function () {
        drawerBody.removeAttribute("aria-busy");
        drawerBody.innerHTML = '<p class="muted small">Details could not be loaded. The text version below the diagram has the same information.</p>';
      });
  }

  nodes.forEach(function (node) {
    var id = node.getAttribute("data-node");
    node.addEventListener("mouseenter", function () { highlight(id); });
    node.addEventListener("mouseleave", clear);
    node.addEventListener("focus", function () { highlight(id); });
    node.addEventListener("blur", clear);
    node.addEventListener("click", function (event) {
      event.preventDefault();
      select(node);
    });
    node.addEventListener("keydown", function (event) {
      if (event.key === " ") {
        event.preventDefault();
        select(node);
      }
    });
  });

  if (drawer) {
    drawer.addEventListener("click", function (event) {
      var close = event.target.closest("[data-drawer-close]");
      if (close) closeDrawer();
      var link = event.target.closest("[data-node-link]");
      if (link) {
        var target = svg.querySelector('[data-node="' + link.getAttribute("data-node-link") + '"]');
        if (target) {
          event.preventDefault();
          select(target);
          target.focus();
        }
      }
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && pinned) closeDrawer();
  });
})();
