import { marked } from 'marked';
import DOMPurify from 'dompurify';

/** @param {string} body */
export function markdown(body) {
  return DOMPurify.sanitize(marked.parse(body, { async: false }), {
    ALLOWED_TAGS: ['p', 'br', 'em', 'strong', 'del', 'blockquote', 'ul', 'ol', 'li', 'pre', 'code', 'a', 'hr', 'h2', 'h3', 'h4'],
    ALLOWED_ATTR: ['href', 'title'], ALLOW_DATA_ATTR: false, ALLOW_ARIA_ATTR: false,
    FORBID_TAGS: ['script', 'style', 'svg', 'math', 'img', 'input', 'button', 'iframe', 'form'],
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):|#)/i
  });
}

const PICTURE = /^!\[([^\]\n]{0,200})\]\(\/api\/assets\/([A-Za-z0-9][A-Za-z0-9._-]{0,120}\.png)\)\s*$/;

/** Split a passage into prose and the pictures attached to it. A picture is a line of its own,
 * `![caption](/api/assets/name.png)`, outside code fences; any other image syntax stays prose and is dropped by the sanitizer.
 * @param {string} body
 * @returns {{text:string,pictures:{alt:string,name:string}[]}} */
export function splitBody(body) {
  const kept = [], pictures = [];
  let fenced = false;
  for (const line of body.split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) fenced = !fenced;
    const match = fenced ? null : PICTURE.exec(line);
    if (match) pictures.push({ alt: match[1].trim(), name: match[2] });
    else kept.push(line);
  }
  return { text: kept.join('\n').replace(/\n{3,}/g, '\n\n').trim(), pictures };
}
