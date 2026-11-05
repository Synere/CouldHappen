/** Reveal sanitized DOM text only. Never build partial HTML strings.
 * @param {HTMLElement} element @param {boolean} enabled */
export function reveal(element, enabled) {
  if (!enabled || matchMedia('(prefers-reduced-motion: reduce)').matches) return () => {};
  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
  /** @type {{node:Node,text:string}[]} */
  const nodes = [];
  let node;
  while ((node = walker.nextNode())) nodes.push({ node, text: node.textContent || '' });
  const length = nodes.reduce((n, item) => n + item.text.length, 0);
  const start = performance.now();
  let frame = 0;
  const finish = () => { cancelAnimationFrame(frame); for (const item of nodes) item.node.textContent = item.text; };
  /** @param {number} now */
  const draw = now => {
    let count = Math.min(length, Math.floor((now - start) * .12));
    for (const item of nodes) { item.node.textContent = item.text.slice(0, count); count = Math.max(0, count - item.text.length); }
    if (now - start < Math.min(5000, length / .12)) frame = requestAnimationFrame(draw); else finish();
  };
  frame = requestAnimationFrame(draw);
  return finish;
}
