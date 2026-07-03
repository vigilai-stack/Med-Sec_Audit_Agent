/*
 * enhance.js — progressive enhancement, inlined by every skin template.
 * Plain vanilla JS, no dependencies; the document remains fully usable
 * without it (CSS-only tabs, checkbox fullscreen figures, native details).
 *
 * Adds: code-copy buttons, Esc-to-close + wheel-zoom + drag-pan for expanded
 * diagrams, and details/figure cleanup before printing.
 */
(function () {
  "use strict";

  /* code copy buttons (hidden until JS is available) */
  document.querySelectorAll(".copy-btn").forEach(function (btn) {
    btn.hidden = false;
    btn.addEventListener("click", function () {
      var block = btn.closest(".codeblock");
      var code = block && block.querySelector(".code-body code");
      if (!code || !navigator.clipboard) return;
      navigator.clipboard.writeText(code.textContent).then(function () {
        var prev = btn.textContent;
        btn.textContent = "Copied ✓";
        setTimeout(function () { btn.textContent = prev; }, 1600);
      });
    });
  });

  /* Esc closes any expanded diagram */
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    document.querySelectorAll(".fig-zoom-toggle:checked").forEach(function (t) {
      t.checked = false;
    });
  });

  /* wheel-zoom + drag-pan inside expanded figures */
  document.querySelectorAll(".figure--diagram").forEach(function (fig) {
    var toggle = fig.querySelector(".fig-zoom-toggle");
    var frame = fig.querySelector(".fig-frame");
    var stage = fig.querySelector(".fig-stage");
    if (!toggle || !frame || !stage) return;
    var scale = 1;

    function target() { return stage.firstElementChild; }
    function apply() {
      var el = target();
      if (!el) return;
      el.style.transformOrigin = "0 0";
      el.style.transform = scale === 1 ? "" : "scale(" + scale + ")";
    }
    toggle.addEventListener("change", function () {
      scale = 1;
      apply();
    });
    frame.addEventListener("wheel", function (e) {
      if (!toggle.checked) return;
      e.preventDefault();
      scale = Math.min(6, Math.max(0.4, scale * (e.deltaY < 0 ? 1.15 : 0.87)));
      apply();
    }, { passive: false });

    var drag = null;
    stage.addEventListener("pointerdown", function (e) {
      if (!toggle.checked) return;
      drag = { x: e.clientX, y: e.clientY, left: frame.scrollLeft, top: frame.scrollTop };
      stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener("pointermove", function (e) {
      if (!drag) return;
      frame.scrollLeft = drag.left - (e.clientX - drag.x);
      frame.scrollTop = drag.top - (e.clientY - drag.y);
    });
    stage.addEventListener("pointerup", function () { drag = null; });
  });

  /* before printing: expand details, leave fullscreen mode */
  window.addEventListener("beforeprint", function () {
    document.querySelectorAll("details").forEach(function (d) { d.open = true; });
    document.querySelectorAll(".fig-zoom-toggle:checked").forEach(function (t) {
      t.checked = false;
    });
  });
})();
