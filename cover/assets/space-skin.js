// Inlined into each copied slide (scripts/apply-space-skin.py).
// Slides keep their original light course colours for readability; the space theme lives in the viewer around them.
// Copied pages keep a <base href> to their source site, so URL updates there would throw: swallow those.
(() => {
  for (const name of ["replaceState", "pushState"]) {
    const original = history[name].bind(history);
    history[name] = (...args) => { try { return original(...args); } catch (error) { return undefined; } };
  }
})();
