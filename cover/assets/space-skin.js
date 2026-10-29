// Space skin: turns a light course slide into the dark space theme of the talk cover.
// Inlined into each copied slide (scripts/apply-space-skin.py), so it also works in pages that use <base href>.
(() => {
  for (const name of ["replaceState", "pushState"]) {
    const original = history[name].bind(history);
    // Copied pages keep a <base href> to their source site, so URL updates there would throw.
    history[name] = (...args) => { try { return original(...args); } catch (error) { return undefined; } };
  }
  const css = `
    html, body { background: #000 !important; }
    /* Filter the top-level children, not body: a filtered body would become the containing block of fixed viewers. */
    body > * { filter: invert(1) hue-rotate(180deg); }
    body img, body video, body iframe, body picture, body svg image,
    body .bgi, body [style*="background-image"], body [style*="url("] { filter: invert(1) hue-rotate(180deg) !important; }
    /* Media inside an already re-inverted box would flip back to a negative. */
    :is(body .bgi, body [style*="background-image"], body [style*="url("]) :is(img, video, iframe, picture, svg image) { filter: none !important; }
    #space-skin-tint {
      position: fixed; inset: 0; z-index: 2147483647; pointer-events: none; mix-blend-mode: screen;
      background:
        radial-gradient(ellipse at 82% 0%, rgba(40,100,210,.34), transparent 55%),
        radial-gradient(ellipse at 0% 100%, rgba(120,90,220,.22), transparent 55%),
        linear-gradient(#081236, #040919);
    }`;
  const style = document.createElement("style");
  style.id = "space-skin";
  style.textContent = css;
  document.head.append(style);
  const addTint = () => {
    if (document.getElementById("space-skin-tint")) return;
    const tint = document.createElement("div");
    tint.id = "space-skin-tint";
    document.documentElement.append(tint);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", addTint, { once: true });
  else addTint();
})();
