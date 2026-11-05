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
