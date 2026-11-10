// groundwork-check v12 — installed by the groundwork skill; `groundwork doctor --fix` replaces it when a newer
// version ships (ADR-22). Checks only your project keeps go in a separate script without this header line.
//
// The deterministic checks for the layers a project has switched on (ADR-12). Settings come from
// .groundwork.json at the repo root. No dependencies: run it with `node scripts/groundwork-check.mjs`.
//
//   node scripts/groundwork-check.mjs               run the checks; exit 1 on any error
//   node scripts/groundwork-check.mjs --warnings    also list every warning (they never fail)
//   node scripts/groundwork-check.mjs --json        machine-readable result
//   node scripts/groundwork-check.mjs --summary     the open-work summary a session starts from (ADR-26); with
//                                                   --hook it reads a SessionStart payload on stdin and stays
//                                                   quiet on resume and compact. It never fails a session.
//   node scripts/groundwork-check.mjs --fmt [FILE...]
//                                                   strip the column padding Obsidian adds to tables (ADR-26)
//   node scripts/groundwork-check.mjs --fmt --staged
//                                                   the pre-commit step: tidy the staged notes and stage them
//                                                   again (ADR-42). The only mode that runs `git add`.
//   node scripts/groundwork-check.mjs --install-hooks
//                                                   point git at .githooks/ (run from `prepare`);
//                                                   outside a git checkout it does nothing
//
// Checks by layer (IDs are what `checks.drop` in .groundwork.json names; a drop needs a reason):
//   core/config            the config is valid, and every dropped check gives a reason
//   core/agents            AGENTS.md exists and stays short
//   core/claude-import     CLAUDE.md imports @AGENTS.md
//   core/duplicate-section no section heading appears in both CLAUDE.md and AGENTS.md (ADR-11)
//   core/brief             the Core brief exists
//   core/links             relative Markdown links and their #headings resolve; wiki-links only where set
//   core/symlinks          no symlinks or junctions in the repo (ADR-9)
//   core/project-check     the project's own check script, where checks.project names one, passes (ADR-47)
//   decisions/parse        every decision entry is well formed
//   decisions/unique       decision IDs are unique
//   decisions/status       each status is one of the five states
//   decisions/fields       required parts are present (Y-statement and Confirmation for the files form)
//   decisions/supersession supersession is recorded on both sides; refined IDs exist
//   decisions/citations    every decision ID cited in the docs or the code resolves
//   open-work/register     the register exists and carries a "Next ID" line (ADR-27)
//   open-work/ids          row IDs are unique, run from 1 without gaps, and Next ID is the highest plus one
//   open-work/citations    every register ID cited in the docs or the code has a row
//   open-work/home         each open row links to its home section: a heading that starts with its ID, in another file;
//                          never in a spec past draft (ADR-65)
//   open-work/row-length   a row is one short line; the detail lives in its home section
//   open-work/tags         (feature) a Blocked-by cell that starts with a standard or declared tag follows its form (ADR-39)
//   open-work/size         (feature) Size (estimate) lines and step lines are well formed
//   open-work/focus        (feature) the Current focus block is an order of IDs only
//   open-work/closed-file  (feature) past the threshold, closed rows live in the closed file
//   open-work/lifecycle    (feature) a plan and the row that ends it agree; a completed plan as a home warns
//   plans/frontmatter      every note carries type, status and updated (and the project tag where one is set)
//   plans/kinds            a note is one of seven kinds, and its status is one the kind allows; a map has its headings (ADR-64)
//   plans/purpose          a note opens with its Purpose; an open plan or map says what ends it
//   plans/dec-log          note-local decisions: a log declares its dec-prefix, cited elsewhere as `<prefix> DEC-n`
//   plans/hub              where a hub is set, it lists every note with the state its frontmatter gives
//   specs/parse            a spec's file name, frontmatter (status, date) and first heading agree (ADR-44)
//   specs/unique           spec IDs are unique
//   specs/status           each status is draft, accepted, implemented or retired
//   specs/requirements     requirement IDs belong to their spec and run from 1 without gaps; a spec past draft has one
//   specs/citations        every spec and requirement ID cited in the docs or the code resolves; code cites nothing retired
//   specs/placeholder      a spec past draft still holds a template placeholder, TODO(groundwork): (ADR-63)
//   specs/legacy           (warns) a file specs.legacy keeps in another form is gone, or is now named as a spec (ADR-62)
//   spec-deltas/parse      a delta carries a status, a date and requirement lines under Added, Changed or Removed (ADR-45);
//                          where it names its spec (`spec: SPEC-n`), the spec exists and every line belongs to it
//   spec-deltas/proposed   a proposed delta changes or removes live requirements and adds the next free numbers
//   spec-deltas/applied    an applied delta agrees with the specs
//   spec-deltas/handover   where the layer hands over to OpenSpec, the repo has an openspec/ folder
//   traceability/tests     every requirement of an implemented spec is cited by a test file; an accepted one warns (ADR-46)
//   domain/note            the domain model exists with a Vocabulary table or a Language glossary (ADR-48, ADR-61)
//   domain/vocabulary      each term is defined once, and no term is also a word to avoid
//   domain/avoid           (warns) a word a term says to avoid is used in the docs, or the files domain.avoidIn lists (ADR-60)
//   architecture/note      the architecture overview exists with its Tools, Scripts and Config files sections (ADR-48)
//   architecture/paths     every script and config file the overview names is in the repo, or git ignores it (ADR-59)
//   review/parse           a review record's file name, frontmatter, heading and findings are well formed (ADR-55)
//   review/target          the file a record reviews exists
//   review/disposition     every finding is fixed, an ISS-n that has a row, or declined with a reason
//   review/required        each spec past draft (and applied delta, where set) dated from review.from has a record
//   review/placeholder     a record still holds a template placeholder, TODO(groundwork): (ADR-63)
//   obsidian/format        tables are kept unpadded (Obsidian re-pads a table when it is clicked)
//   session-hook/command   each harness file runs the summary by a path inside the repo, and AGENTS.md has the fallback
//
// `--root DIR` and `--config FILE` check a repo against a config kept outside it (a rehearsal, ADR-31).
//
// Material at or below the grandfathering line (`grandfather` in the config, ADR-19) turns missing
// parts into warnings. Structural breakage (dead links, duplicate IDs, citations that don't resolve)
// is an error regardless of age.
import { spawnSync } from "node:child_process";
import { existsSync, lstatSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, posix, relative, resolve } from "node:path";

const argv = process.argv.slice(2);
const args = new Set(argv);
const argVal = (name) => (argv.includes(name) ? argv[argv.indexOf(name) + 1] ?? null : null);
// The summary never fails a session: any problem prints nothing and exits 0 (ADR-30).
const SUMMARY = args.has("--summary");
if (SUMMARY) {
  process.on("uncaughtException", () => process.exit(0));
  if (args.has("--hook") && !process.stdin.isTTY) {
    let source;
    try { source = JSON.parse(readFileSync(0, "utf8") || "{}").source; } catch {}
    if (source === "resume" || source === "compact") process.exit(0);
  }
}

if (args.has("--install-hooks")) {
  const r = spawnSync("git", ["config", "core.hooksPath", ".githooks"], { stdio: "ignore" });
  if (r.status === 0) console.log("[groundwork] core.hooksPath = .githooks");
  process.exit(0);
}

/** The repo root: the nearest folder above cwd holding .groundwork.json. */
function findRoot() {
  const project = process.env.CLAUDE_PROJECT_DIR;
  if (SUMMARY && project && existsSync(join(project, ".groundwork.json"))) return resolve(project);
  for (let dir = resolve(process.cwd()); ; dir = dirname(dir)) {
    if (existsSync(join(dir, ".groundwork.json"))) return dir;
    if (dirname(dir) === dir) return null;
  }
}

const root = argVal("--root") ? resolve(argVal("--root")) : findRoot();
const CONFIG = argVal("--config") ? resolve(argVal("--config")) : root && join(root, ".groundwork.json");
if (SUMMARY && (!root || !existsSync(CONFIG))) process.exit(0);
if (!root || !existsSync(CONFIG)) {
  console.error("[groundwork] .groundwork.json not found — run the groundwork skill (`start` or `adopt`) to set the project up.");
  process.exit(1);
}

const errors = [];
const warnings = new Map();
const dropped = {};
let config;
try {
  config = JSON.parse(readFileSync(CONFIG, "utf8"));
} catch (e) {
  if (SUMMARY) process.exit(0);
  console.error(`[groundwork] .groundwork.json is not valid JSON: ${e.message}`);
  process.exit(1);
}

const CHECKS = [
  "core/config", "core/agents", "core/claude-import", "core/duplicate-section", "core/brief", "core/links", "core/symlinks", "core/project-check",
  "decisions/parse", "decisions/unique", "decisions/status", "decisions/fields", "decisions/supersession", "decisions/citations",
  "open-work/register", "open-work/ids", "open-work/citations", "open-work/home", "open-work/row-length",
  "open-work/tags", "open-work/size", "open-work/focus", "open-work/closed-file", "open-work/lifecycle",
  "session-hook/command", "obsidian/format",
  "plans/frontmatter", "plans/kinds", "plans/purpose", "plans/dec-log", "plans/hub",
  "specs/parse", "specs/unique", "specs/status", "specs/requirements", "specs/citations", "specs/legacy", "specs/placeholder",
  "spec-deltas/parse", "spec-deltas/proposed", "spec-deltas/applied", "spec-deltas/handover",
  "traceability/tests",
  "domain/note", "domain/vocabulary", "domain/avoid",
  "architecture/note", "architecture/paths",
  "review/parse", "review/target", "review/disposition", "review/required", "review/placeholder",
];
const isDropped = (id) => Object.hasOwn(dropped, id);
const report = (id, file, line, message) => {
  if (!isDropped(id)) errors.push({ check: id, file, line, message });
};
const warn = (id, file, line, message) => {
  if (isDropped(id)) return;
  if (!warnings.has(id)) warnings.set(id, []);
  warnings.get(id).push({ check: id, file, line, message });
};

// ---- config -----------------------------------------------------------------------------------
const LAYERS = ["core", "decisions", "open-work", "plans", "session-hook", "obsidian", "specs", "spec-deltas", "traceability", "domain", "architecture", "review"];
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
/** An ID grammar such as "ADR-n", "ISS-n" or "AD #n": the last n stands for the number (ADR-13). */
function grammar(pattern) {
  const k = pattern.lastIndexOf("n");
  const pre = k === -1 ? pattern : pattern.slice(0, k);
  const post = k === -1 ? "" : pattern.slice(k + 1);
  const src = `${esc(pre)}(\\d+)${esc(post)}`;
  return { pre, post, src, cite: new RegExp(`(?<![\\w-])${src}(?![\\w])`, "g"), label: (n) => `${pre}${n}${post}` };
}
const layers = Array.isArray(config.layers) ? config.layers : [];
if (!layers.includes("core")) report("core/config", ".groundwork.json", 1, 'layers must include "core"');
for (const l of layers) if (!LAYERS.includes(l)) report("core/config", ".groundwork.json", 1, `unknown layer "${l}" (this check knows: ${LAYERS.join(", ")})`);
for (const [id, reason] of Object.entries(config.checks?.drop ?? {})) {
  if (!CHECKS.includes(id)) report("core/config", ".groundwork.json", 1, `checks.drop names an unknown check "${id}"`);
  else if (typeof reason !== "string" || reason.trim().length < 10) report("core/config", ".groundwork.json", 1, `checks.drop.${id} needs a reason (a sentence, not a flag)`);
  else dropped[id] = reason;
}
const core = { brief: "docs/brief.md", markdown: ["AGENTS.md", "CLAUDE.md", "docs/**"], links: "relative", agentsMaxLines: 150, ...config.core };
const gf = config.grandfather ?? null;

// ---- files ------------------------------------------------------------------------------------
const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".venv", "venv", "__pycache__", "target", ".next", ".svelte-kit"]);
const TEXT_EXT = /\.(md|ts|tsx|js|jsx|mjs|cjs|svelte|vue|py|sh|ya?ml|toml|json|html|css|rs|go|java|kt|swift|rb|php|cs|c|h|cpp)$/i;

/** Every file git would carry: tracked plus untracked-but-not-ignored. Falls back to a walk. */
function repoFiles() {
  const r = spawnSync("git", ["ls-files", "-co", "--exclude-standard", "-z"], { cwd: root, encoding: "utf8" });
  if (r.status === 0) return [...new Set(r.stdout.split("\0").filter(Boolean))].filter((f) => existsSync(join(root, f)) || isLink(f));
  const out = [];
  (function walk(dir, rel) {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const p = rel ? `${rel}/${e.name}` : e.name;
      if (e.isDirectory()) { if (!SKIP_DIRS.has(e.name)) walk(join(dir, e.name), p); }
      else out.push(p);
    }
  })(root, "");
  return out;
}
function isLink(rel) {
  try { return lstatSync(join(root, rel)).isSymbolicLink(); } catch { return false; }
}
function globRe(glob) {
  const re = glob.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*\*\/?/g, "\u0000").replace(/\*/g, "[^/]*").replace(/\?/g, "[^/]").replace(/\u0000/g, ".*");
  return new RegExp(`^${re}$`);
}
const matchAny = (globs) => { const res = globs.map(globRe); return (f) => res.some((r) => r.test(f)); };
// Skills installed into a harness folder (.claude/skills, .agents/skills, …) are other people's tools, not this
// project's knowledge: their links, IDs and machine links are not checked.
const HARNESS_SKILLS = /^\.(agents?|claude|codex|opencode|gemini|cursor|windsurf)\/skills\//;
const FILES = repoFiles().filter((f) => !HARNESS_SKILLS.test(f));
const textCache = new Map();
function lines(rel) {
  if (!textCache.has(rel)) {
    let text = "";
    try { text = readFileSync(join(root, rel), "utf8"); } catch { text = null; }
    textCache.set(rel, text === null ? null : text.replace(/\r\n/g, "\n").split("\n"));
  }
  return textCache.get(rel);
}

/** Lines outside fenced blocks, with inline code spans blanked so nothing in code counts as a link or ID. */
function proseLines(rel) {
  const ls = lines(rel) ?? [];
  let fence = null;
  return ls.map((line) => {
    const f = /^\s*(```+|~~~+)/.exec(line);
    if (f) {
      if (!fence) fence = f[1][0];
      else if (f[1][0] === fence) fence = null;
      return "";
    }
    if (fence) return "";
    // Code spans are found with wiki-links masked, so a backtick inside a link's heading is not read as code.
    const masked = line.replace(/\[\[[^\]\n]+?\]\]/g, (m) => "x".repeat(m.length));
    let out = line;
    for (const m of masked.matchAll(/(`+)[^`]*?\1/g)) out = out.slice(0, m.index) + " ".repeat(m[0].length) + out.slice(m.index + m[0].length);
    return out;
  });
}

/** A Markdown file's headings: { text, slug (GitHub style), level, line }. */
const headCache = new Map();
function headings(rel) {
  if (!headCache.has(rel)) {
    const list = [];
    const seen = new Map();
    const raw = lines(rel) ?? [];
    proseLines(rel).forEach((line, i) => {
      if (!/^#{1,6}\s/.test(line)) return;
      const m = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(raw[i]);
      if (!m) return;
      const s = m[2].toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu, "").trim().replace(/\s/g, "-");
      const n = seen.get(s) ?? 0;
      seen.set(s, n + 1);
      list.push({ text: m[2], slug: n ? `${s}-${n}` : s, level: m[1].length, line: i + 1 });
    });
    headCache.set(rel, list);
  }
  return headCache.get(rel);
}
const slugs = (rel) => new Set(headings(rel).map((h) => h.slug));
/** The raw lines under a heading, up to the next heading of its level or above. */
function sectionBody(rel, h) {
  const next = headings(rel).find((o) => o.line > h.line && o.level <= h.level);
  return lines(rel).slice(h.line, next ? next.line - 1 : undefined);
}

// ---- core -------------------------------------------------------------------------------------
const exists = (rel) => existsSync(join(root, rel));

if (!exists("AGENTS.md")) report("core/agents", "AGENTS.md", 1, "AGENTS.md is missing (Core: it is how agents find the project's knowledge)");
else {
  const n = lines("AGENTS.md").length;
  if (n > core.agentsMaxLines) warn("core/agents", "AGENTS.md", 1, `AGENTS.md is ${n} lines; keep it under ${core.agentsMaxLines} (short files are the ones agents follow)`);
}

const claudeFile = exists("CLAUDE.md") ? "CLAUDE.md" : exists(".claude/CLAUDE.md") ? ".claude/CLAUDE.md" : null;
if (!claudeFile) report("core/claude-import", "CLAUDE.md", 1, "CLAUDE.md is missing (Core: it imports @AGENTS.md)");
else {
  const importRe = claudeFile === "CLAUDE.md" ? /^@(\.\/)?AGENTS\.md\s*$/ : /^@(\.\.\/)AGENTS\.md\s*$/;
  if (!lines(claudeFile).some((l) => importRe.test(l))) {
    report("core/claude-import", claudeFile, 1, `${claudeFile} must import AGENTS.md on a line of its own (${claudeFile === "CLAUDE.md" ? "@AGENTS.md" : "@../AGENTS.md"})`);
  }
  if (exists("AGENTS.md")) {
    const heads = (rel) => {
      const map = new Map();
      proseLines(rel).forEach((l, i) => {
        const m = /^#{1,6}\s+(.+?)\s*$/.exec(l);
        if (m) map.set(m[1].trim().toLowerCase(), i + 1);
      });
      return map;
    };
    const a = heads("AGENTS.md");
    for (const [h, line] of heads(claudeFile)) {
      if (a.has(h)) report("core/duplicate-section", claudeFile, line, `section "${h}" is also in AGENTS.md, which CLAUDE.md already imports in full; keep it in one file`);
    }
  }
}

if (!exists(core.brief)) report("core/brief", core.brief, 1, "the Core brief is missing (core.brief in .groundwork.json)");

const decisionsCfg = { form: "single", file: "DECISIONS.md", dir: "docs/decisions", id: "ADR-n", adopted: [], citeIgnore: [], ...config.decisions };
const ow = { register: "docs/issues.md", id: "ISS-n", strictRowsFrom: 1, features: [], maxItem: 240, maxBlocked: 220, citeIgnore: [], ...config.openWork };
const FEATURES = ["tags", "size", "focus", "lifecycle", "closed-file"];
const feat = (f) => layers.includes("open-work") && (ow.features ?? []).includes(f);
const closedCfg = { threshold: 50, file: posix.join(posix.dirname(ow.register), "issues-closed.md"), ...ow.closed };
const focusCfg = { nudge: "off", groups: true, readers: "summary", ...ow.focus };
const plansCfg = { dir: "docs/plans", prefix: "", tag: null, hub: null, decId: "DEC-n", citeIgnore: [], ...config.plans };
const specsCfg = { dir: "docs/specs", id: "SPEC-n", citeIgnore: [], legacy: [], ...config.specs };
const deltasCfg = { tool: "groundwork", ...config.specDeltas };
const DELTA_DIR = `${specsCfg.dir}/changes`;
const reviewCfg = { dir: "docs/reviews", require: [], from: null, ...config.review };
const mdScope = matchAny([
  ...core.markdown, core.brief,
  ...(layers.includes("decisions") ? [decisionsCfg.form === "files" ? `${decisionsCfg.dir}/**` : decisionsCfg.file] : []),
  ...(layers.includes("open-work") ? [ow.register] : []),
  ...(feat("closed-file") ? [closedCfg.file] : []),
  ...(layers.includes("plans") ? [`${plansCfg.dir}/**`] : []),
  ...(layers.includes("specs") ? [`${specsCfg.dir}/**`] : []),
  ...(layers.includes("review") ? [`${reviewCfg.dir}/**`] : []),
]);
const mdFiles = FILES.filter((f) => f.endsWith(".md") && mdScope(f));
const mdNames = new Map(mdFiles.map((f) => [posix.basename(f, ".md").toLowerCase(), f]));

for (const file of mdFiles) {
  proseLines(file).forEach((line, i) => {
    const targets = [];
    for (const m of line.matchAll(/!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)/g)) targets.push(m[1]);
    const ref = /^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s|$)/.exec(line);
    if (ref) targets.push(ref[1]);
    for (const t of targets) {
      if (/^[a-z][a-z0-9+.-]*:/i.test(t) || t.startsWith("//")) continue; // http:, mailto:, file:, …
      const hash = t.indexOf("#");
      const pathPart = decodeURI(hash === -1 ? t : t.slice(0, hash));
      const anchor = hash === -1 ? "" : t.slice(hash + 1).toLowerCase();
      const target = pathPart ? posix.normalize(posix.join(posix.dirname(file), pathPart)).replace(/\/$/, "") : file;
      if (target.startsWith("..") || !exists(target)) {
        report("core/links", file, i + 1, `link to a missing file: ${t}`);
      } else if (anchor && target.endsWith(".md") && !slugs(target).has(anchor)) {
        report("core/links", file, i + 1, `link to a missing heading: ${t}`);
      }
    }
    for (const m of line.matchAll(/!?\[\[([^\]\n]+?)\]\]/g)) {
      if (core.links !== "wiki") {
        report("core/links", file, i + 1, `wiki-link [[${m[1]}]] in a repo set to relative links (core.links); use [text](path.md)`);
        continue;
      }
      // Inside a table the alias pipe is escaped (`[[Note\|alias]]`), leaving a trailing backslash.
      const target = m[1].split("|")[0].replace(/\\$/, "");
      const hash = target.indexOf("#");
      const name = hash === -1 ? target : target.slice(0, hash);
      const note = name ? mdNames.get(name.toLowerCase()) : file;
      if (!note) report("core/links", file, i + 1, `link to a missing note: [[${target}]]`);
      else if (hash !== -1 && !headings(note).some((h) => h.text === target.slice(hash + 1))) report("core/links", file, i + 1, `link to a missing heading: [[${target}]]`);
    }
  });
}

{
  const linked = new Set();
  for (const f of FILES) {
    const parts = f.split("/");
    for (let k = 1; k <= parts.length; k++) {
      const p = parts.slice(0, k).join("/");
      if (linked.has(p)) break;
      if (isLink(p)) {
        linked.add(p);
        report("core/symlinks", p, 1, "a symlink or junction inside the repo (ADR-9: only machine-level links; Windows git checks them out as text files)");
        break;
      }
    }
  }
  const staged = spawnSync("git", ["ls-files", "-s"], { cwd: root, encoding: "utf8" });
  if (staged.status === 0) {
    for (const l of staged.stdout.split("\n")) {
      const m = /^120000 \S+ \d+\t(.+)$/.exec(l);
      if (m && !linked.has(m[1])) report("core/symlinks", m[1], 1, "git stores this path as a symlink (ADR-9)");
    }
  }
}

// ---- decisions --------------------------------------------------------------------------------
const STATES = ["proposed", "accepted", "rejected", "deprecated", "superseded"];
// The list form (ADR-28): numbered items under "## Decisions" in one note, each with a Status line (accepted,
// amended by #n, or superseded by #n). Read where a project already has it; never scaffolded.
if (layers.includes("decisions") && decisionsCfg.form === "list") {
  const AD = grammar(decisionsCfg.id);
  const file = decisionsCfg.file;
  const ads = new Map(); // n → { line, superseded, links }
  if (!exists(file)) report("decisions/parse", file, 1, "the decisions note is missing (decisions.file)");
  else {
    const ls = proseLines(file);
    const start = ls.findIndex((l) => /^## Decisions\s*$/.test(l));
    if (start === -1) report("decisions/parse", file, 1, 'the decisions note has no "## Decisions" section');
    else {
      const end = ls.findIndex((l, i) => i > start && /^## /.test(l));
      const section = ls.slice(start + 1, end === -1 ? undefined : end);
      const items = [];
      section.forEach((line, j) => {
        const m = /^(\d+)\. \*\*/.exec(line);
        if (m) items.push({ n: Number(m[1]), line: start + 2 + j, from: j });
      });
      items.forEach(({ n, line, from }, k) => {
        if (n !== k + 1) report("decisions/parse", file, line, `${AD.label(n)} is out of sequence; expected ${AD.label(k + 1)} (numbered from 1 without gaps, never renumbered)`);
        const status = section.slice(from + 1, items[k + 1]?.from).map((l) => /^\s+\*\*Status:\*\*\s*(accepted|amended by #\d+(?:(?:, | and )#\d+)*|superseded by #\d+)\b/.exec(l)).find(Boolean)?.[1];
        if (!status) report("decisions/status", file, line, `${AD.label(n)} needs a Status line: accepted, amended by #n, or superseded by #n`);
        if (ads.has(n)) report("decisions/unique", file, line, `${AD.label(n)} is defined twice`);
        else ads.set(n, { line, superseded: status?.startsWith("superseded") ?? false, links: status ? [...status.matchAll(/#(\d+)/g)].map((x) => Number(x[1])) : [] });
      });
      for (const [n, { line, links }] of ads) for (const to of links) if (to === n || !ads.has(to)) report("decisions/supersession", file, line, `${AD.label(n)}'s Status names ${AD.label(to)}, which is not another decision`);
    }
    const ignore = matchAny([...(decisionsCfg.citeIgnore ?? []), "scripts/groundwork-check.mjs"]);
    for (const f of FILES) {
      if (!TEXT_EXT.test(f) || ignore(f) || f.endsWith("package-lock.json")) continue;
      const ls2 = f.endsWith(".md") ? proseLines(f) : lines(f);
      if (!ls2) continue;
      ls2.forEach((line, i) => {
        for (const m of line.matchAll(AD.cite)) {
          const n = Number(m[1]);
          if (!ads.has(n)) report("decisions/citations", f, i + 1, `${AD.label(n)} is cited but there is no such decision`);
          else if (ads.get(n).superseded && f !== file) report("decisions/citations", f, i + 1, `${AD.label(n)} is superseded; cite the decision that replaced it`);
        }
      });
    }
  }
}
if (layers.includes("decisions") && decisionsCfg.form !== "list") {
  if (!["single", "files"].includes(decisionsCfg.form)) report("core/config", ".groundwork.json", 1, `decisions.form must be "single", "files" or "list"`);
  const { src: ID_SRC, cite: ID_CITE, label: idLabel } = grammar(decisionsCfg.id);
  const isOld = (n) => gf?.decisionsThrough != null && n <= gf.decisionsThrough;
  const flag = (id, n, file, line, message) => (isOld(n) ? warn : report)(id, file, line, message);

  /** id number → entries (more than one is a duplicate) */
  const entries = new Map();
  const add = (e) => {
    if (!entries.has(e.n)) entries.set(e.n, []);
    entries.get(e.n).push(e);
  };
  const relField = (text, key) => {
    const m = new RegExp(`\\*\\*${key}:\\*\\*\\s*(.+)$`, "im").exec(text) ?? new RegExp(`^${key.toLowerCase().replace(/ /g, "-")}:\\s*(.+)$`, "im").exec(text);
    return m ? m[1].trim() : null;
  };
  const idsIn = (s) => (s ? [...s.matchAll(new RegExp(ID_SRC, "g"))].map((m) => Number(m[1])) : []);

  // Adopted sources: entries written as `**ADR-n — Title.** text` bullets (or headings) in an older doc.
  for (const src of decisionsCfg.adopted ?? []) {
    const file = typeof src === "string" ? src : src.file;
    if (!exists(file)) { report("decisions/parse", file, 1, "an adopted decision source is missing (decisions.adopted)"); continue; }
    proseLines(file).forEach((line, i) => {
      const m = new RegExp(`^(?:\\s*[-*]\\s+\\*\\*|#{2,4}\\s+)${ID_SRC}\\s+[—–-]\\s+(.+?)\\.?(?:\\*\\*|$)`).exec(line);
      if (m) add({ n: Number(m[1]), title: m[2], file, line: i + 1, adopted: true, status: null, body: line });
    });
  }

  if (decisionsCfg.form === "single") {
    const file = decisionsCfg.file;
    if (!exists(file)) report("decisions/parse", file, 1, `the decision log is missing (decisions.file)`);
    else {
      const ls = proseLines(file);
      const heads = [];
      ls.forEach((l, i) => { if (/^## /.test(l)) heads.push(i); });
      for (let k = 0; k < heads.length; k++) {
        const i = heads[k];
        const m = new RegExp(`^## ${ID_SRC}\\s+—\\s+(\\S.*)$`).exec(ls[i]);
        if (!m) {
          if (new RegExp(ID_SRC).test(ls[i])) report("decisions/parse", file, i + 1, `a decision heading must read "## ${idLabel("n").replace(/n$/, "<n>")} — Title"`);
          continue;
        }
        const body = ls.slice(i + 1, heads[k + 1] ?? ls.length).join("\n");
        add({ n: Number(m[1]), title: m[2], file, line: i + 1, body, status: relField(body, "Status")?.toLowerCase() ?? null, form: "single" });
      }
    }
  } else {
    const dir = decisionsCfg.dir;
    const fileRe = new RegExp(`^${esc(dir)}/${ID_SRC}-[a-z0-9-]+\\.md$`);
    for (const f of FILES.filter((x) => x.startsWith(`${dir}/`) && x.endsWith(".md"))) {
      if (/\/README\.md$/i.test(f) || /\/_?template\.md$/i.test(f)) continue;
      const fm = fileRe.exec(f);
      if (!fm) { report("decisions/parse", f, 1, `decision files are named ${dir}/${idLabel("<n>")}-short-title.md`); continue; }
      const ls = lines(f);
      const end = ls[0] === "---" ? ls.indexOf("---", 1) : -1;
      const front = end === -1 ? "" : ls.slice(1, end).join("\n");
      const body = ls.slice(end + 1).join("\n");
      const h = new RegExp(`^# ${ID_SRC}\\s+—\\s+(\\S.*)$`, "m").exec(body);
      if (!h) { report("decisions/parse", f, 1, `the first heading must read "# ${idLabel(fm[1])} — Title"`); continue; }
      if (Number(h[1]) !== Number(fm[1])) report("decisions/parse", f, 1, `the heading's ID ${idLabel(h[1])} differs from the file name's ${idLabel(fm[1])}`);
      if (end === -1) flag("decisions/parse", Number(fm[1]), f, 1, "no frontmatter (status, date)");
      add({ n: Number(fm[1]), title: h[1], file: f, line: 1, body: front + "\n" + body, status: /^status:\s*(\S+)/m.exec(front)?.[1].toLowerCase() ?? null, form: "files", promoted: /^promoted:/m.test(front) });
    }
  }

  for (const [n, list] of entries) {
    if (list.length > 1) {
      for (const e of list.slice(1)) report("decisions/unique", e.file, e.line, `${idLabel(n)} is defined twice (first in ${list[0].file}:${list[0].line})`);
    }
    const e = list[0];
    if (e.adopted) {
      if (!isOld(n)) report("decisions/fields", e.file, e.line, `${idLabel(n)} is in an adopted source but above the grandfathering line; new decisions go in ${decisionsCfg.form === "single" ? decisionsCfg.file : decisionsCfg.dir + "/"}`);
      e.status = "accepted";
      continue;
    }
    if (!e.status) flag("decisions/status", n, e.file, e.line, `${idLabel(n)} has no status`);
    else if (!STATES.includes(e.status)) report("decisions/status", e.file, e.line, `${idLabel(n)} status "${e.status}" is not one of: ${STATES.join(", ")}`);
    const need = e.form === "single" ? ["Date", "Context", "Decision", "Consequences"] : ["date", "Context and Problem Statement", "Decision Outcome", "Consequences", "Confirmation"];
    for (const part of need) {
      const present = e.form === "single"
        ? new RegExp(`\\*\\*${part}(?::\\*\\*|\\.\\*\\*)`).test(e.body)
        : part === "date" ? /^date:\s*\d{4}-\d{2}-\d{2}/m.test(e.body) : new RegExp(`^#{2,3} ${part}\\s*$`, "m").test(e.body);
      if (!present) (e.promoted ? warn : flag)("decisions/fields", n, e.file, e.line, `${idLabel(n)} is missing its ${part}`);
    }
    if (e.form === "files" && !/^>\s*In the context of\b/im.test(e.body)) (e.promoted ? warn : flag)("decisions/fields", n, e.file, e.line, `${idLabel(n)} is missing its Y-statement line ("> In the context of …")`);
  }

  // Supersession: reciprocal, and a superseded status names its successor.
  const get = (n) => entries.get(n)?.[0];
  for (const [n, [e]] of entries) {
    if (e.adopted) continue;
    const by = idsIn(relField(e.body, "Superseded by"));
    const sup = idsIn(relField(e.body, "Supersedes"));
    const ref = idsIn(relField(e.body, "Refines"));
    if (e.status === "superseded" && by.length === 0) report("decisions/supersession", e.file, e.line, `${idLabel(n)} is superseded but names no successor (Superseded by)`);
    if (by.length && e.status !== "superseded") report("decisions/supersession", e.file, e.line, `${idLabel(n)} names a successor but its status is ${e.status ?? "missing"}, not superseded`);
    for (const t of by) {
      const o = get(t);
      if (!o) report("decisions/supersession", e.file, e.line, `${idLabel(n)} is superseded by ${idLabel(t)}, which does not exist`);
      else if (!o.adopted && !idsIn(relField(o.body, "Supersedes")).includes(n)) report("decisions/supersession", o.file, o.line, `${idLabel(t)} must say "Supersedes: ${idLabel(n)}" (${idLabel(n)} says it is superseded by ${idLabel(t)})`);
    }
    for (const t of sup) {
      const o = get(t);
      if (!o) report("decisions/supersession", e.file, e.line, `${idLabel(n)} supersedes ${idLabel(t)}, which does not exist`);
      else if (!o.adopted && !idsIn(relField(o.body, "Superseded by")).includes(n)) report("decisions/supersession", o.file, o.line, `${idLabel(t)} must say "Superseded by: ${idLabel(n)}" and have status superseded (${idLabel(n)} supersedes it)`);
    }
    for (const t of ref) if (!get(t)) report("decisions/supersession", e.file, e.line, `${idLabel(n)} refines ${idLabel(t)}, which does not exist`);
  }

  // Citations in the docs and the code.
  const ignore = matchAny([...(decisionsCfg.citeIgnore ?? []), "scripts/groundwork-check.mjs"]);
  for (const f of FILES) {
    if (!TEXT_EXT.test(f) || ignore(f) || f.endsWith("package-lock.json")) continue;
    const ls = f.endsWith(".md") ? proseLines(f) : lines(f);
    if (!ls) continue;
    ls.forEach((line, i) => {
      for (const m of line.matchAll(ID_CITE)) {
        const n = Number(m[1]);
        const e = get(n);
        if (!e) report("decisions/citations", f, i + 1, `${idLabel(n)} is cited but not defined`);
        else if ((e.status === "superseded" || e.status === "rejected") && f !== e.file && !/Supersede|Superseded|Refines/.test(line)) {
          warn("decisions/citations", f, i + 1, `${idLabel(n)} is ${e.status}; cite its successor`);
        }
      }
    });
  }
}

// ---- open work --------------------------------------------------------------------------------
/** Register rows by number: { n, file, line, open, section, cells, columns, raw, home }. */
const rows = new Map();
const OW = grammar(ow.id);
const cellsOf = (line) => line.split(/(?<!\\)\|/).slice(1, -1).map((c) => c.trim());
/** Read the rows of a register file; rows under a "Closed" heading (or in the closed file) are closed. */
function readRows(file, allClosed = false) {
  let section = null;
  let closed = allClosed;
  let columns = [];
  proseLines(file).forEach((line, i) => {
    const h = /^## (.+?)\s*$/.exec(line);
    if (h) { section = h[1]; closed = allClosed || /^Closed\b/i.test(section); columns = []; return; }
    if (!/^\s*\|/.test(line)) return;
    const cells = cellsOf(line);
    if (cells[0] === "ID") { columns = cells; return; }
    const m = new RegExp(`^${OW.src}$`).exec(cells[0] ?? "");
    if (!m) return;
    const n = Number(m[1]);
    if (rows.has(n)) report("open-work/ids", file, i + 1, `${OW.label(n)} has a second row (first at ${rows.get(n).file}:${rows.get(n).line})`);
    else rows.set(n, { n, file, line: i + 1, open: !closed, section, cells, columns, raw: line });
  });
}
/** The home section a row links to: a heading starting with the row's ID, in a file other than the register. */
function homeOf(row) {
  const starts = (text) => new RegExp(`^${esc(OW.label(row.n))}(?![\\w])`).test(text);
  for (const m of row.raw.matchAll(/\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>#]*)#([^)\s>]+)>?\s*\)/g)) {
    const target = m[1] ? posix.normalize(posix.join(posix.dirname(row.file), decodeURI(m[1]))) : row.file;
    if (target === ow.register || !target.endsWith(".md") || !exists(target)) continue;
    const h = headings(target).find((x) => x.slug === m[2].toLowerCase());
    if (h && starts(h.text)) return { file: target, heading: h };
  }
  for (const m of row.raw.matchAll(/\[\[([^\]\n#|]+)#([^\]\n|]+?)\\?(?:\|[^\]\n]*)?\]\]/g)) {
    const target = mdNames.get(m[1].toLowerCase());
    if (!target || target === ow.register) continue;
    const h = headings(target).find((x) => x.text === m[2]);
    if (h && starts(h.text)) return { file: target, heading: h };
  }
  return null;
}

if (layers.includes("open-work")) {
  const reg = ow.register;
  if (!exists(reg)) report("open-work/register", reg, 1, "the register is missing (openWork.register in .groundwork.json)");
  else {
    readRows(reg);
    if (feat("closed-file") && exists(closedCfg.file)) readRows(closedCfg.file, true);
    const max = Math.max(0, ...rows.keys());
    for (let n = 1; n <= max; n++) if (!rows.has(n)) report("open-work/ids", reg, 1, `${OW.label(n)} has no row (IDs run from ${OW.label(1)} without gaps and are never reused)`);
    const NEXT = new RegExp(`Next ID: ${OW.src}`);
    const at = lines(reg).findIndex((l) => NEXT.test(l));
    if (at === -1) report("open-work/register", reg, 1, `no "Next ID: ${OW.label("<n>")}" line`);
    else {
      const next = Number(NEXT.exec(lines(reg)[at])[1]);
      if (next !== max + 1) report("open-work/ids", reg, at + 1, `Next ID is ${OW.label(next)}, expected ${OW.label(max + 1)}`);
    }

    // Citations in the docs and the code.
    const ignore = matchAny([...(ow.citeIgnore ?? []), "scripts/groundwork-check.mjs", ...(layers.includes("review") ? [`${reviewCfg.dir}/**`] : [])]);
    for (const f of FILES) {
      if (!TEXT_EXT.test(f) || ignore(f) || f.endsWith("package-lock.json")) continue;
      const ls = f.endsWith(".md") ? proseLines(f) : lines(f);
      if (!ls) continue;
      ls.forEach((line, i) => {
        if (f === reg && NEXT.test(line)) return;
        for (const m of line.matchAll(OW.cite)) if (!rows.has(Number(m[1]))) report("open-work/citations", f, i + 1, `${OW.label(m[1])} is cited but has no row in the register`);
      });
    }

    // Open rows: a home section and a short line. Rows numbered below strictRowsFrom warn (ADR-19).
    for (const row of rows.values()) {
      if (!row.open) continue;
      const flag = (id, message) => (row.n >= (ow.strictRowsFrom ?? 1) ? report : warn)(id, row.file, row.line, message);
      const cell = (name) => row.cells[row.columns.indexOf(name)] ?? "";
      const label = OW.label(row.n);
      if (cell("Item").length > ow.maxItem) flag("open-work/row-length", `${label}'s Item is ${cell("Item").length} characters (at most ${ow.maxItem}); move the detail to its home section`);
      if (cell("Blocked by / phase").length > ow.maxBlocked) flag("open-work/row-length", `${label}'s Blocked by is ${cell("Blocked by / phase").length} characters (at most ${ow.maxBlocked}); move the detail to its home section`);
      row.home = homeOf(row);
      if (!row.home) flag("open-work/home", `${label} links to no home section (a heading starting "${label}" in a file other than the register)`);
      else if (!sectionBody(row.home.file, row.home.heading).some((l) => l.trim())) flag("open-work/home", `${label}'s home section in ${row.home.file} is empty`);
    }
  }
}

// ---- plans & research -------------------------------------------------------------------------
// A note's kind (`type`) and the statuses that kind allows. Milestones live in a note's body, never in `status`.
const KINDS = {
  hub: ["current"],
  register: ["current"],
  reference: ["current", "retired"],
  record: ["current"],
  research: ["active", "completed", "superseded"],
  plan: ["proposed", "active", "completed", "abandoned", "superseded"],
  // A wayfind map (ADR-64): a plan's statuses, and the headings reference/commands/wayfind.md asks for.
  map: ["proposed", "active", "completed", "abandoned", "superseded"],
};
const MAP_HEADINGS = ["Destination", "Notes", "Decisions so far", "Not yet specified", "Out of scope"];
/** Notes by name (the file name without .md): { name, file, fm, type, status, prefix }. */
const notes = new Map();
const noteByFile = new Map();
const fmField = (fm, key) => {
  const re = new RegExp(`^${key}:\\s*(.*?)\\s*$`);
  const m = (fm ?? []).map((l) => re.exec(l)).find(Boolean);
  return m ? m[1].replace(/^["']|["']$/g, "") : undefined;
};
/** A note's Purpose: an Obsidian callout (`> [!abstract] Purpose`) or a paragraph that starts `**Purpose.**`. */
function purposeOf(rel) {
  const ls = lines(rel) ?? [];
  let at = ls.findIndex((l) => /^> \[!abstract\] Purpose\s*$/.test(l));
  const callout = at !== -1;
  if (!callout) at = ls.findIndex((l) => /^\*\*Purpose[.:]\*\*/.test(l));
  if (at === -1) return null;
  const body = [callout ? "" : ls[at]];
  for (const l of ls.slice(at + 1)) {
    if (callout ? !l.startsWith(">") : !l.trim()) break;
    body.push(l);
  }
  return { line: at + 1, text: body.join("\n") };
}

if (layers.includes("plans")) {
  const DEC = grammar(plansCfg.decId);
  const inDir = (f) => f.startsWith(`${plansCfg.dir}/`) && !f.slice(plansCfg.dir.length + 1).includes("/");
  for (const file of FILES.filter((f) => f.endsWith(".md") && inDir(f) && posix.basename(f).startsWith(plansCfg.prefix ?? ""))) {
    const ls = lines(file);
    const end = ls[0] === "---" ? ls.indexOf("---", 1) : -1;
    const fm = end === -1 ? null : ls.slice(1, end);
    const note = { name: posix.basename(file, ".md"), file, fm, type: fmField(fm, "type"), status: fmField(fm, "status"), prefix: fmField(fm, "dec-prefix") };
    notes.set(note.name, note);
    noteByFile.set(file, note);
  }

  const prefixes = new Map(); // dec-prefix → note name
  for (const note of notes.values()) {
    const { file, fm, type, status, prefix } = note;
    if (!fm) { report("plans/frontmatter", file, 1, "no frontmatter (type, status, updated)"); continue; }
    const text = fm.join("\n");
    if (plansCfg.tag && !new RegExp(`^tags:\\n(?:\\s+- .+\\n?)*\\s+- ${esc(plansCfg.tag)}(?![\\w-])`, "m").test(text)) report("plans/frontmatter", file, 1, `frontmatter tags must include ${plansCfg.tag}`);
    for (const key of ["type", "status"]) if (!note[key]) report("plans/frontmatter", file, 1, `frontmatter is missing ${key}`);
    if (!/^updated: \d{4}-\d{2}-\d{2}\s*$/m.test(text)) report("plans/frontmatter", file, 1, "frontmatter updated must be a YYYY-MM-DD date");
    if (!type || !status) continue;
    if (!KINDS[type]) { report("plans/kinds", file, 1, `type "${type}" is not a note kind (${Object.keys(KINDS).join(", ")})`); continue; }
    if (!KINDS[type].includes(status)) report("plans/kinds", file, 1, `a ${type} note's status is one of ${KINDS[type].join(", ")}, not "${status}"`);
    if (type === "map") for (const name of MAP_HEADINGS) if (!headings(file).some((h) => h.level === 2 && h.text.toLowerCase() === name.toLowerCase())) report("plans/kinds", file, 1, `a map has a "## ${name}" section (the wayfind command's map)`);
    if (status === "superseded") {
      const by = fmField(fm, "superseded_by")?.replace(/^\[\[|\]\]$/g, "").replace(/^.*\//, "").replace(/\.md$/, "");
      if (!by) report("plans/kinds", file, 1, "a superseded note names its replacement in superseded_by");
      else if (!notes.has(by)) report("plans/kinds", file, 1, `superseded_by names a missing note: ${by}`);
    }
    // Every note opens with its Purpose; an open plan's says what ends it.
    const purpose = purposeOf(file);
    if (!purpose) report("plans/purpose", file, 1, "a note opens with its Purpose (`> [!abstract] Purpose`, or a paragraph that starts `**Purpose.**`)");
    else if ((type === "plan" || type === "map") && (status === "proposed" || status === "active") && !/\bEnds when\b/.test(purpose.text)) report("plans/purpose", file, purpose.line, `a ${type}'s Purpose says what ends it ("Ends when …")`);
    // A log is DEC-n rows under a "Decision log" heading; a table that only cites another note's decisions is not one.
    const ls = lines(file);
    const log = ls.findIndex((l) => /^#{2,4} Decision log\s*$/i.test(l));
    const hasLog = log !== -1 && ls.slice(log + 1).some((l) => new RegExp(`^\\|\\s*${DEC.src}\\s*\\|`).test(l));
    if (hasLog && !prefix) report("plans/dec-log", file, log + 1, `a note with a ${plansCfg.decId} log declares dec-prefix in its frontmatter`);
    if (prefix) {
      if (prefixes.has(prefix)) report("plans/dec-log", file, 1, `dec-prefix "${prefix}" is already used by ${prefixes.get(prefix)}`);
      else prefixes.set(prefix, note.name);
    }
  }

  // Decision-log citations: outside the note that keeps the log, a citation reads `<dec-prefix> DEC-<n>`. A range or
  // list after a prefixed ID counts with it ("<prefix> DEC-<a>…DEC-<b>", "<prefix> DEC-<a>/<b>/<c>").
  const DEC_CITE = new RegExp(`(?:(\\S+) )?${DEC.src}(?:\\s*(?:…|–|-|\\/|,|and|to)\\s*(?:${esc(DEC.pre)})?\\d+)*`, "g");
  const ignore = matchAny([...(plansCfg.citeIgnore ?? []), "scripts/groundwork-check.mjs"]);
  for (const f of FILES) {
    if (!TEXT_EXT.test(f) || ignore(f) || f.endsWith("package-lock.json")) continue;
    if (noteByFile.get(f)?.prefix) continue; // a note cites its own log bare
    const ls = f.endsWith(".md") ? proseLines(f) : lines(f);
    if (!ls) continue;
    ls.forEach((line, i) => {
      for (const m of line.matchAll(DEC_CITE)) {
        const word = m[1]?.replace(/^[`*(["']+/, "");
        if (!prefixes.has(word)) report("plans/dec-log", f, i + 1, `"${m[0]}": qualify it with the owning note's dec-prefix`);
      }
    });
  }

  // The hub's note table lists every note, and its State reads `type · status` exactly as the frontmatter does.
  if (plansCfg.hub) {
    const hub = noteByFile.get(plansCfg.hub);
    if (!hub) report("plans/hub", plansCfg.hub, 1, "the hub note is missing (plans.hub in .groundwork.json)");
    else {
      if (hub.type !== "hub") report("plans/hub", hub.file, 1, 'the hub note\'s type is "hub"');
      for (const n of notes.values()) if (n.type === "hub" && n !== hub) report("plans/hub", n.file, 1, `there is one hub note (${hub.file})`);
      const listed = new Set();
      lines(hub.file).forEach((line, i) => {
        const m = /^\|\s*(?:\[\[([^\]|#\\]+)[^\]]*\]\]|\[[^\]]*\]\(\s*<?([^)\s>#]+)[^)]*\))\s*\|/.exec(line);
        if (!m) return;
        const n = m[1] ? notes.get(m[1]) : noteByFile.get(posix.normalize(posix.join(posix.dirname(hub.file), decodeURI(m[2]))));
        if (!n) return;
        listed.add(n.name);
        const cells = cellsOf(line);
        const state = cells[cells.length - 1];
        if (state !== `${n.type} · ${n.status}`) report("plans/hub", hub.file, i + 1, `State for ${n.name} reads "${state}"; its frontmatter says "${n.type} · ${n.status}"`);
      });
      for (const n of notes.values()) if (n !== hub && !listed.has(n.name)) report("plans/hub", hub.file, 1, `the note table has no row for ${n.name}`);
    }
  }
}

// ---- open work: features (ADR-27) -------------------------------------------------------------
// The Size line that opens a home section, and its step lines:
//   **Size (estimate):** M–L · Opus · could grow — <reason> *(2026-10-27)*
//   - **Step 3 — the checks:** Size (estimate): M · Sonnet · bounded — <reason> *(2026-10-27)* · next
// A finished line or step appends ` · Actual: <size>`; the one open step in hand appends ` · next`.
const SIZE = "(?:S|M|L|XL)(?:–(?:S|M|L|XL))?";
const SIZE_BODY = new RegExp(`^(${SIZE}) · ([^·]+?) · (bounded|could grow|open-ended) — (.+?) \\*\\((\\d{4}-\\d{2}-\\d{2})\\)\\*(?: · Actual: (${SIZE})\\b[^·]*)?( · next)?$`);
const SIZE_FORMAT = "a Size line reads `<S|M|L|XL or a range> · <who> · <bounded|could grow|open-ended> — <reason> *(YYYY-MM-DD)*`";
function sizeLine(line) {
  const lead = /^\*\*Size \(estimate\):\*\*\s*(.*)$/.exec(line);
  const step = lead ? null : /^- \*\*Step (\d+) — ([^*]+?):\*\* Size \(estimate\):\s*(.*)$/.exec(line);
  if (!lead && !step) return null;
  const m = SIZE_BODY.exec((lead ? lead[1] : step[3]).trim());
  const est = m && { size: m[1], who: m[2].trim(), growth: m[3], reason: m[4], date: m[5], actual: m[6] ?? null, next: Boolean(m[7]) };
  return lead ? { kind: "lead", est } : { kind: "step", n: Number(step[1]), title: step[2], est };
}
/** A home section's estimate: its lead line (the first non-blank line) and its steps. */
function estimateOf(body) {
  const first = body.find((l) => l.trim());
  const lead = first ? sizeLine(first) : null;
  return { lead: lead?.kind === "lead" ? lead.est : undefined, steps: body.map(sizeLine).filter((c) => c?.kind === "step") };
}
/** A Blocked-by cell's leading `word:`. Only a standard or declared name is a tag; any other word is prose (ADR-39). */
const STANDARD_TAGS = ["needs-author", "needs-research"];
function tagOf(cell) {
  const m = /^([a-z][a-z0-9-]*):(?:\s+(.*))?$/.exec(cell ?? "");
  return m ? { name: m[1], text: m[2] ?? "", known: STANDARD_TAGS.includes(m[1]) || Object.hasOwn(ow.tags ?? {}, m[1]) } : null;
}
/** The Current focus block: its non-blank lines with callout markers stripped, or null when there is none. */
function focusBlock() {
  const out = [];
  let inFocus = false;
  let found = false;
  (lines(ow.register) ?? []).forEach((line, i) => {
    if (/^## /.test(line)) { inFocus = /^## Current focus\s*$/.test(line); found ||= inFocus; return; }
    const text = line.replace(/^>\s?/, "");
    if (inFocus && text.trim()) out.push({ text: text.replace(/^\[!\w+\]\s*/, ""), line: i + 1 });
  });
  return found ? out : null;
}
const FOCUS_ITEM = new RegExp(`^(\\d+)\\.\\s+${OW.src}\\s+—\\s+(\\S.*)$`);
const DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
/** The re-rank nudge setting, normalised: null (off), { weekday, hour, minute }, { days } or { closed }; false when malformed. */
function nudgeOf(n) {
  if (n == null || n === "off" || n === false) return null;
  if (typeof n !== "object") return false;
  if (Number.isInteger(n.days) && n.days > 0) return { days: n.days };
  if (Number.isInteger(n.closed) && n.closed > 0) return { closed: n.closed };
  const t = /^(\d{1,2}):(\d{2})$/.exec(n.time ?? "00:00");
  const d = DAYS.indexOf(String(n.weekday ?? "").toLowerCase());
  return d !== -1 && t ? { weekday: d, hour: Number(t[1]), minute: Number(t[2]) } : false;
}

if (layers.includes("open-work")) {
  for (const f of ow.features ?? []) if (!FEATURES.includes(f)) report("core/config", ".groundwork.json", 1, `openWork.features names an unknown feature "${f}" (${FEATURES.join(", ")})`);
}
if (layers.includes("open-work") && exists(ow.register)) {
  const reg = ow.register;
  const open = [...rows.values()].filter((r) => r.open);

  if (feat("tags")) {
    const declared = {};
    for (const [name, pattern] of Object.entries(ow.tags ?? {})) {
      try { declared[name] = new RegExp(`^(?:${pattern})$`); } catch { report("core/config", ".groundwork.json", 1, `openWork.tags.${name} is not a valid pattern`); }
    }
    const STANDARD = STANDARD_TAGS;
    for (const row of open) {
      const found = tagOf(row.cells[3]);
      if (!found) continue;
      const { name: tag, text } = found;
      const label = OW.label(row.n);
      if (STANDARD.includes(tag)) {
        if (!text.trim()) report("open-work/tags", row.file, row.line, `${label}: \`${tag}:\` says what is needed`);
      } else if (!found.known) {
        // Any other word is prose, except one in the standard tags' family: that is a typo of one (ADR-39).
        if (tag.startsWith("needs-")) report("open-work/tags", row.file, row.line, `${label}: "${tag}:" is not a tag (${[...STANDARD, ...Object.keys(ow.tags ?? {})].join(", ")}); declare it in openWork.tags or reword the cell`);
      } else if (declared[tag] && !declared[tag].test(text.split(";")[0].trim())) {
        report("open-work/tags", row.file, row.line, `${label}: \`${tag}: ${text.split(";")[0].trim()}\` does not match the tag's declared form (${ow.tags[tag]})`);
      }
    }
  }

  let focusIds = [];
  if (feat("focus")) {
    const block = focusBlock();
    const nudge = nudgeOf(focusCfg.nudge);
    if (nudge === false) report("core/config", ".groundwork.json", 1, 'openWork.focus.nudge is "off", { "weekday": "monday", "time": "10:00" }, { "days": n } or { "closed": n }');
    if (!["summary", "loop"].includes(focusCfg.readers)) report("core/config", ".groundwork.json", 1, 'openWork.focus.readers is "summary" or "loop"');
    if (!block) report("open-work/focus", reg, 1, 'the register has no "## Current focus" block');
    else {
      const seen = new Set();
      let count = 0;
      for (const { text, line } of block) {
        const m = FOCUS_ITEM.exec(text);
        if (!m) {
          if (/^(\d+\.|[-*+])\s/.test(text)) report("open-work/focus", reg, line, `a Current focus item is \`N. ${OW.label("n")} — why\`, one ID per line; the detail stays in the row and its home section`);
          else if (/^\*\*[^*]+\*\*$/.test(text.trim()) && focusCfg.groups === false) report("open-work/focus", reg, line, "group labels are switched off (openWork.focus.groups)");
          continue;
        }
        const n = Number(m[2]);
        if (Number(m[1]) !== ++count) report("open-work/focus", reg, line, `the order is numbered 1, 2, 3 …; this item should be ${count}`);
        if (seen.has(n)) report("open-work/focus", reg, line, `${OW.label(n)} is in the order twice`);
        seen.add(n);
        focusIds.push({ n, line });
      }
      if (nudge && !/Work order from \d{4}-\d{2}-\d{2}/.test(block[0]?.text ?? "")) report("open-work/focus", reg, block[0]?.line ?? 1, 'the block\'s first line dates the order ("Work order from YYYY-MM-DD"), so the re-rank nudge can tell when it is due');
    }
    if (focusCfg.readers === "loop") {
      // The rule is in AGENTS.md, or in the block itself with AGENTS.md sending agents to the block (ADR-40).
      const RULE = /first unblocked item/i;
      const agents = lines("AGENTS.md") ?? [];
      const inBlock = (block ?? []).some((b) => RULE.test(b.text));
      if (!agents.some((l) => RULE.test(l)) && !(inBlock && agents.some((l) => /Current focus/i.test(l)))) {
        report("open-work/focus", "AGENTS.md", 1, inBlock
          ? 'openWork.focus.readers is "loop": the Current focus block states the rule, so AGENTS.md must name "Current focus" to send agents to it'
          : 'openWork.focus.readers is "loop": AGENTS.md, or the Current focus block, must carry the rule "Pick the first unblocked item in Current focus; don\'t start a later one while an earlier one is free unless it can run in parallel"');
      }
    }
  }

  if (feat("size")) {
    const who = ow.size?.who ?? [];
    for (const file of mdFiles) {
      if (file === reg || (feat("closed-file") && file === closedCfg.file)) continue;
      const raw = lines(file);
      const prose = proseLines(file);
      raw.forEach((line, i) => {
        if (!prose[i]) return; // blank or inside a fenced block
        const c = sizeLine(line);
        if (!c) return;
        if (!c.est) report("open-work/size", file, i + 1, SIZE_FORMAT);
        else if (who.length && !who.includes(c.est.who)) report("open-work/size", file, i + 1, `"${c.est.who}" is not in openWork.size.who (${who.join(", ")})`);
      });
      for (const h of headings(file)) {
        if (h.level < 2 || h.level > 4 || !new RegExp(`^${OW.src}(?![\\w])`).test(h.text)) continue;
        const { steps } = estimateOf(sectionBody(file, h));
        const unfinished = steps.filter((s) => s.est && !s.est.actual);
        const next = steps.filter((s) => s.est?.next).length;
        if (next > 1 || (unfinished.length && next !== 1)) report("open-work/size", file, h.line, `a stepped item marks exactly one unfinished step \`next\` (found ${next})`);
      }
    }
    for (const { n, line } of focusIds) {
      const home = rows.get(n)?.open ? rows.get(n).home : null;
      if (home && estimateOf(sectionBody(home.file, home.heading)).lead === undefined) warn("open-work/size", reg, line, `${OW.label(n)} is in Current focus but its home section opens with no Size (estimate) line`);
    }
  }

  if (feat("closed-file")) {
    if (posix.dirname(closedCfg.file) !== posix.dirname(reg)) report("core/config", ".groundwork.json", 1, "openWork.closed.file sits in the register's folder, so a moved row's links still resolve");
    const closed = [...rows.values()].filter((r) => !r.open && r.file === reg);
    if (closed.length > closedCfg.threshold) report("open-work/closed-file", reg, closed[0].line, `${closed.length} closed rows (more than ${closedCfg.threshold}): move them to ${closedCfg.file} with the groundwork skill's \`move-closed\``);
  }

  // Lifecycle: a plan names the row whose closing ends it (`ends-with`, or a list that must all close). Status is
  // held to those rows both ways, so the commit that closes the row cannot land until the plan's status changes too.
  if (feat("lifecycle")) {
    if (!layers.includes("plans")) report("core/config", ".groundwork.json", 1, 'the "lifecycle" feature ties plans to rows: it needs the plans layer');
    for (const { file, fm, type, status } of notes.values()) {
      if (type !== "plan") continue;
      const ends = [...(fmField(fm, "ends-with") ?? "").matchAll(new RegExp(OW.src, "g"))].map((m) => Number(m[1]));
      const isOpen = status === "proposed" || status === "active";
      if (!ends.length) {
        if (status === "active") report("open-work/lifecycle", file, 1, `an active plan names the row whose closing ends it: \`ends-with: ${OW.label("n")}\``);
        continue;
      }
      const missing = ends.filter((n) => !rows.has(n));
      for (const n of missing) report("open-work/lifecycle", file, 1, `ends-with names ${OW.label(n)}, which has no row`);
      if (missing.length) continue;
      const stillOpen = ends.filter((n) => rows.get(n).open);
      const named = ends.map(OW.label).join(", ");
      if (isOpen && !stillOpen.length) report("open-work/lifecycle", file, 1, `its end row${ends.length > 1 ? "s are" : " is"} closed (${named}): set status to completed, or abandoned if the work was dropped`);
      if ((status === "completed" || status === "abandoned") && stillOpen.length) report("open-work/lifecycle", file, 1, `the plan is ${status} but its end row ${stillOpen.map(OW.label).join(", ")} is open`);
      if (isOpen) {
        const purpose = purposeOf(file);
        for (const n of ends) if (purpose && !new RegExp(`(?<![\\w-])${esc(OW.label(n))}(?![\\w])`).test(purpose.text)) report("open-work/lifecycle", file, purpose.line, `the Purpose names its end row ${OW.label(n)}`);
      }
    }
    for (const row of open) {
      const note = row.home && noteByFile.get(row.home.file);
      if (note?.type === "plan" && note.status === "completed") warn("open-work/lifecycle", row.file, row.line, `${OW.label(row.n)}'s home is in a completed plan (${note.name}); new work starts a new plan`);
    }
  }
}

// ---- specs (ADR-44) -----------------------------------------------------------------------------
// One file per spec, `<dir>/SPEC-n-short-title.md`. A requirement is a list line `- **SPEC-n.m** — text`; a dropped
// one keeps its line with the text "removed …", so a number is never reused.
const SPEC_STATES = ["draft", "accepted", "implemented", "retired"];
// What the templates `new` writes mark each placeholder with (ADR-63).
const PLACEHOLDER = "TODO(groundwork):";
const SP = grammar(specsCfg.id);
/** n → { file, status, reqs: Map(m → { line, removed, text }) } */
const specs = new Map();
const misnamed = new Set(); // a misnamed spec is reported once, not once per ID it cites
const reqLine = (line) => new RegExp(`^\\s*[-*]\\s+\\*\\*${SP.src}\\.(\\d+)\\*\\*\\s+—\\s+(\\S.*)$`).exec(line);
// Files in the specs folder kept in another form (ADR-62): exempt from the specs checks, and they keep no ID.
const legacySpecs = new Set([].concat(specsCfg.legacy ?? []).map((x) => String(x).replace(/^\.\//, "")));
if (layers.includes("specs")) {
  const dir = specsCfg.dir;
  const fileRe = new RegExp(`^${esc(dir)}/${SP.src}-[a-z0-9-]+\\.md$`);
  for (const f of legacySpecs) {
    if (!exists(f)) warn("specs/legacy", ".groundwork.json", 1, `specs.legacy lists ${f}, which is gone: drop it from the list`);
    else if (fileRe.test(f)) warn("specs/legacy", f, 1, `${f} is named as a spec now: drop it from specs.legacy so the specs checks read it`);
  }
  for (const f of FILES.filter((x) => x.endsWith(".md") && x.startsWith(`${dir}/`) && !x.slice(dir.length + 1).includes("/"))) {
    if (/\/README\.md$/i.test(f) || legacySpecs.has(f)) continue;
    const fm = fileRe.exec(f);
    if (!fm) { report("specs/parse", f, 1, `spec files are named ${dir}/${SP.label("<n>")}-short-title.md`); misnamed.add(f); continue; }
    const n = Number(fm[1]);
    const ls = lines(f);
    const end = ls[0] === "---" ? ls.indexOf("---", 1) : -1;
    const front = end === -1 ? null : ls.slice(1, end);
    if (!front) report("specs/parse", f, 1, "no frontmatter (status, date)");
    else if (!/^\d{4}-\d{2}-\d{2}$/.test(fmField(front, "date") ?? "")) report("specs/parse", f, 1, "frontmatter date must be a YYYY-MM-DD date");
    const prose = proseLines(f);
    const hAt = prose.findIndex((l, i) => i > end && /^# /.test(l));
    const h = hAt === -1 ? null : new RegExp(`^# ${SP.src}\\s+—\\s+(\\S.*)$`).exec(prose[hAt]);
    if (!h) report("specs/parse", f, hAt === -1 ? 1 : hAt + 1, `the first heading must read "# ${SP.label(n)} — Title"`);
    else if (Number(h[1]) !== n) report("specs/parse", f, hAt + 1, `the heading's ID ${SP.label(h[1])} differs from the file name's ${SP.label(n)}`);
    if (specs.has(n)) { report("specs/unique", f, 1, `${SP.label(n)} is defined twice (first in ${specs.get(n).file})`); continue; }
    const status = front ? fmField(front, "status")?.toLowerCase() : undefined;
    if (front && !status) report("specs/status", f, 1, `${SP.label(n)} has no status`);
    else if (status && !SPEC_STATES.includes(status)) report("specs/status", f, 1, `${SP.label(n)} status "${status}" is not one of: ${SPEC_STATES.join(", ")}`);
    const reqs = new Map();
    let count = 0;
    prose.forEach((line, i) => {
      const m = reqLine(line);
      if (!m) return;
      const id = `${SP.label(m[1])}.${m[2]}`;
      if (Number(m[1]) !== n) { report("specs/requirements", f, i + 1, `${id} is written in ${SP.label(n)}; a requirement carries its own spec's ID`); return; }
      const k = Number(m[2]);
      if (reqs.has(k)) { report("specs/requirements", f, i + 1, `${id} is defined twice`); return; }
      count++;
      if (k !== count) report("specs/requirements", f, i + 1, `${id} is out of sequence; expected ${SP.label(n)}.${count} (numbered from 1 without gaps; a dropped requirement keeps its line as "removed")`);
      const removed = /^removed\b/i.test(m[3]);
      if (!removed && !/\bshall\b/i.test(m[3])) warn("specs/requirements", f, i + 1, `${id} does not say what the system shall do ("When …, the system shall …")`);
      reqs.set(k, { line: i + 1, removed, text: m[3] });
    });
    // A template placeholder never passes for finished work (ADR-63); a draft may keep its own while it is written.
    if (status && status !== "draft") ls.forEach((l, i) => { if (l.includes(PLACEHOLDER)) report("specs/placeholder", f, i + 1, `${SP.label(n)} is ${status} but still holds a ${PLACEHOLDER.slice(0, -1)} placeholder: write what it asks for (ADR-63)`); });
    if (status && status !== "draft" && ![...reqs.values()].some((r) => !r.removed)) report("specs/requirements", f, 1, `${SP.label(n)} is ${status} but has no requirement (\`- **${SP.label(n)}.1** — …\`)`);
    specs.set(n, { file: f, status, reqs });
  }

  const CITE = new RegExp(`(?<![\\w-])${SP.src}(?:\\.(\\d+))?(?![\\w])`, "g");
  // The config names spec files (specs.legacy); it cites nothing.
  const ignore = matchAny([...(specsCfg.citeIgnore ?? []), "scripts/groundwork-check.mjs", ".groundwork.json"]);
  for (const f of FILES) {
    if (!TEXT_EXT.test(f) || ignore(f) || misnamed.has(f) || legacySpecs.has(f) || f.endsWith("package-lock.json")) continue;
    // A delta names requirements that do not exist yet; its own checks hold its IDs (ADR-45).
    if (layers.includes("spec-deltas") && deltasCfg.tool === "groundwork" && f.startsWith(DELTA_DIR + "/")) continue;
    const md = f.endsWith(".md");
    const ls = md ? proseLines(f) : lines(f);
    if (!ls) continue;
    ls.forEach((line, i) => {
      for (const m of line.matchAll(CITE)) {
        const spec = specs.get(Number(m[1]));
        const id = `${SP.label(m[1])}${m[2] ? `.${m[2]}` : ""}`;
        if (!spec) { report("specs/citations", f, i + 1, `${SP.label(m[1])} is cited but there is no such spec`); continue; }
        const req = m[2] ? spec.reqs.get(Number(m[2])) : null;
        if (m[2] && !req) { if (f !== spec.file) report("specs/citations", f, i + 1, `${id} is cited but ${spec.file} has no such requirement`); continue; }
        // Code that still cites a retired spec or a removed requirement implements something nobody asks for.
        if (!md && spec.status === "retired") report("specs/citations", f, i + 1, `${id} is cited in code but ${SP.label(m[1])} is retired`);
        else if (!md && req?.removed) report("specs/citations", f, i + 1, `${id} is cited in code but the requirement was removed`);
      }
    });
  }
}

// An accepted spec changes only through a delta (ADR-45), so a ticket cut from it lives in a plan note that cites
// the spec, never in the spec itself (ADR-65). A draft spec may still home tickets while it is shaped.
if (layers.includes("open-work") && layers.includes("specs")) {
  const specByFile = new Map([...specs].map(([n, sp]) => [sp.file, { n, ...sp }]));
  for (const row of rows.values()) {
    const sp = row.open && row.home ? specByFile.get(row.home.file) : null;
    if (!sp || !sp.status || sp.status === "draft") continue;
    (row.n >= (ow.strictRowsFrom ?? 1) ? report : warn)("open-work/home", row.file, row.line, `${OW.label(row.n)}'s home is in ${SP.label(sp.n)}, which is ${sp.status}: home the ticket in a plan note that cites ${SP.label(sp.n)}, not in the spec (ADR-65)`);
  }
}

// ---- spec deltas (ADR-45) -----------------------------------------------------------------------
// A delta is a file in <specs.dir>/changes/ with Added, Changed and Removed sections of requirement lines. The check
// only reports; the skill's apply-delta verb merges a proposed delta into the specs.
const DELTA_STATES = ["proposed", "applied", "dropped"];
const allDeltas = []; // read again by review/required
if (layers.includes("spec-deltas")) {
  if (!["groundwork", "openspec"].includes(deltasCfg.tool)) report("core/config", ".groundwork.json", 1, 'specDeltas.tool is "groundwork" or "openspec"');
  else if (deltasCfg.tool === "openspec") {
    if (!FILES.some((f) => f.startsWith("openspec/"))) report("spec-deltas/handover", ".groundwork.json", 1, "specDeltas.tool is openspec, but the repo has no openspec/ folder");
  } else if (!layers.includes("specs")) report("core/config", ".groundwork.json", 1, 'the "spec-deltas" layer changes specs: it needs the specs layer');
  else {
    const deltas = allDeltas;
    for (const f of FILES.filter((x) => x.endsWith(".md") && x.startsWith(DELTA_DIR + "/") && !x.slice(DELTA_DIR.length + 1).includes("/"))) {
      if (/\/README\.md$/i.test(f)) continue;
      const ls = lines(f);
      const end = ls[0] === "---" ? ls.indexOf("---", 1) : -1;
      const front = end === -1 ? null : ls.slice(1, end);
      const status = front ? fmField(front, "status")?.toLowerCase() : undefined;
      const date = front ? fmField(front, "date") : undefined;
      if (!front) report("spec-deltas/parse", f, 1, "no frontmatter (status, date)");
      else {
        if (!DELTA_STATES.includes(status)) report("spec-deltas/parse", f, 1, "a delta's status is one of: " + DELTA_STATES.join(", "));
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date ?? "")) report("spec-deltas/parse", f, 1, "frontmatter date must be a YYYY-MM-DD date");
      }
      const items = [];
      let kind = null;
      proseLines(f).forEach((line, i) => {
        const h = /^##\s+(.+?)\s*$/.exec(line);
        if (h) { kind = ["added", "changed", "removed"].find((k) => k === h[1].toLowerCase()) ?? null; return; }
        if (!kind || !/^\s*[-*]\s/.test(line)) return;
        const m = reqLine(line);
        if (!m) { report("spec-deltas/parse", f, i + 1, "a line under Added, Changed or Removed reads `- **" + SP.label("<n>") + ".<m>** — text`"); return; }
        items.push({ kind, n: Number(m[1]), m: Number(m[2]), text: m[3], line: i + 1, id: SP.label(m[1]) + "." + m[2] });
      });
      if (!items.length) report("spec-deltas/parse", f, 1, "a delta adds, changes or removes at least one requirement (## Added, ## Changed, ## Removed)");
      // `new delta --spec` records the one spec the delta changes.
      const named = front ? fmField(front, "spec") : undefined;
      if (named !== undefined) {
        const sm = new RegExp("^" + SP.src + "$").exec(named);
        if (!sm) report("spec-deltas/parse", f, 1, "frontmatter spec names a spec by its ID (" + SP.label("<n>") + "), not \"" + named + "\"");
        else if (!specs.has(Number(sm[1]))) report("spec-deltas/parse", f, 1, "frontmatter spec names " + named + ", which does not exist");
        else for (const it of items) if (it.n !== Number(sm[1])) report("spec-deltas/parse", f, it.line, it.id + " belongs to " + SP.label(it.n) + ", but the delta changes " + named + " (frontmatter spec)");
      }
      deltas.push({ file: f, status, date: date ?? "", items });
    }
    // An applied delta's text may have been changed again since: a later applied delta that touches the requirement excuses it.
    const later = (d, item) => deltas.some((o) => o !== d && o.status === "applied" && o.date >= d.date && o.items.some((x) => x.kind !== "added" && x.n === item.n && x.m === item.m));
    for (const d of deltas) {
      const next = new Map();
      for (const item of d.status === "proposed" || d.status === "applied" ? d.items : []) {
        const id = "spec-deltas/" + d.status;
        const spec = specs.get(item.n);
        if (!spec) { report(id, d.file, item.line, item.id + " names " + SP.label(item.n) + ", which does not exist"); continue; }
        const req = spec.reqs.get(item.m);
        if (d.status === "proposed") {
          if (item.kind === "added") {
            const want = next.get(item.n) ?? spec.reqs.size + 1;
            next.set(item.n, want + 1);
            if (item.m !== want) report(id, d.file, item.line, item.id + " is added, so it takes the next free number: " + SP.label(item.n) + "." + want);
          } else if (!req) report(id, d.file, item.line, item.id + " is " + item.kind + ", but " + spec.file + " has no such requirement");
          else if (req.removed) report(id, d.file, item.line, item.id + " is " + item.kind + ", but the requirement was already removed");
        } else if (!req) report(id, d.file, item.line, "the delta is applied, but " + spec.file + " has no " + item.id);
        else if (item.kind === "removed") { if (!req.removed) report(id, d.file, item.line, "the delta is applied, but " + item.id + " is not marked removed in " + spec.file); }
        else if (req.text !== item.text && !later(d, item)) report(id, d.file, item.line, "the delta is applied, but " + item.id + " reads differently in " + spec.file + " and no later delta changes it");
      }
    }
  }
}

// ---- review (ADR-53, ADR-55) ---------------------------------------------------------------------
// A record is a file in review.dir. The check reads its shape and its dispositions, never what a finding says.
const SEVERITY = "(?:\\[(?:Blocker|Major|Nit)\\]\\s+)?";
if (layers.includes("review")) {
  const dir = reviewCfg.dir;
  const targets = new Set();
  for (const f of FILES.filter((x) => x.endsWith(".md") && x.startsWith(dir + "/") && !x.slice(dir.length + 1).includes("/"))) {
    if (/\/README\.md$/i.test(f)) continue;
    if (!/^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$/.test(posix.basename(f))) { report("review/parse", f, 1, "review records are named " + dir + "/YYYY-MM-DD-short-title.md"); continue; }
    const ls = lines(f);
    const end = ls[0] === "---" ? ls.indexOf("---", 1) : -1;
    const front = end === -1 ? null : ls.slice(1, end);
    const target = front ? fmField(front, "target") : undefined;
    if (!front) report("review/parse", f, 1, "no frontmatter (target, date, roles, mode)");
    else {
      if (!target) report("review/parse", f, 1, "the frontmatter names no target");
      if (!/^\d{4}-\d{2}-\d{2}$/.test(fmField(front, "date") ?? "")) report("review/parse", f, 1, "frontmatter date must be a YYYY-MM-DD date");
      if (!fmField(front, "roles")) report("review/parse", f, 1, "the frontmatter names no roles");
      if (!["subagent", "inline"].includes(fmField(front, "mode"))) report("review/parse", f, 1, "mode is subagent or inline");
    }
    if (target) {
      const rel = target.replace(/^\.\//, "");
      if (!exists(rel)) report("review/target", f, 1, "the target " + target + " is not in the repo");
      targets.add(rel);
    }
    ls.forEach((l, i) => { if (l.includes(PLACEHOLDER)) report("review/placeholder", f, i + 1, "the record still holds a " + PLACEHOLDER.slice(0, -1) + " placeholder: write the finding, or a line of your own saying the review found nothing (ADR-63)"); });
    const hAt = ls.findIndex((l, i) => i > end && /^#\s/.test(l));
    if (hAt === -1 || !/^#\s+Review\s+—\s+\S/.test(ls[hAt])) report("review/parse", f, hAt === -1 ? 1 : hAt + 1, 'the first heading reads "# Review — Title"');
    const fh = headings(f).find((h) => h.text.toLowerCase() === "findings");
    if (!fh) { report("review/parse", f, 1, 'a record has a "## Findings" section'); continue; }
    const seen = new Set();
    sectionBody(f, fh).forEach((line, j) => {
      if (!/^\s*[-*]\s/.test(line)) return;
      const at = fh.line + 1 + j;
      const m = /^\s*[-*]\s+\*\*F(\d+)\*\*\s+—\s+(\S.*)$/.exec(line);
      if (!m) { report("review/parse", f, at, "a finding reads `- **F<n>** — [Blocker|Major|Nit] text — disposition`"); return; }
      if (seen.has(m[1])) report("review/parse", f, at, "F" + m[1] + " is listed twice");
      seen.add(m[1]);
      const seg = m[2].slice(m[2].lastIndexOf(" — ") + 3).trim();
      const d = m[2].includes(" — ") ? new RegExp("^\\*\\*(?:fixed|(" + OW.src + ")|declined:)\\*\\*\\s*(.*)$").exec(seg) : null;
      const disposed = d && !(seg.startsWith("**declined:**") && !d[d.length - 1].trim());
      if (!disposed) { report("review/disposition", f, at, "F" + m[1] + " has no disposition: end it with — **fixed**, **" + OW.label("<n>") + "**, or **declined:** and the reason"); return; }
      if (d[1]) {
        if (!layers.includes("open-work")) report("review/disposition", f, at, "F" + m[1] + " is disposed as " + d[1] + ", but the open-work layer is off: there is no register");
        else if (!rows.has(Number(d[2]))) report("review/disposition", f, at, "F" + m[1] + " is disposed as " + d[1] + ", which has no row in the register");
      }
    });
  }
  const require = [].concat(reviewCfg.require ?? []);
  const from = reviewCfg.from ?? "0000-00-00";
  const unknown = require.filter((k) => !["specs", "deltas"].includes(k));
  if (unknown.length) report("core/config", ".groundwork.json", 1, "review.require lists specs and deltas only, not " + unknown.join(", "));
  if (require.includes("specs")) for (const [n, spec] of specs) {
    const date = fmField((() => { const ls = lines(spec.file); const e = ls[0] === "---" ? ls.indexOf("---", 1) : -1; return e === -1 ? [] : ls.slice(1, e); })(), "date") ?? "";
    if (["accepted", "implemented"].includes(spec.status) && date >= from && !targets.has(spec.file)) report("review/required", spec.file, 1, SP.label(n) + " is " + spec.status + " but no record in " + dir + " reviews it");
  }
  if (require.includes("deltas")) for (const d of allDeltas) {
    if (d.status === "applied" && d.date >= from && !targets.has(d.file)) report("review/required", d.file, 1, "the delta is applied but no record in " + dir + " reviews it");
  }
}

// ---- traceability (ADR-46) ----------------------------------------------------------------------
// Marking a spec implemented is a claim: every live requirement is cited by its ID in at least one test file.
const traceCfg = { tests: ["tests/**", "test/**", "**/*.test.*", "**/*.spec.*", "**/*_test.*", "**/test_*.*"], ...config.traceability };
if (layers.includes("traceability")) {
  if (!layers.includes("specs")) report("core/config", ".groundwork.json", 1, 'the "traceability" layer ties tests to requirements: it needs the specs layer');
  else if (!Array.isArray(traceCfg.tests) || !traceCfg.tests.length) report("core/config", ".groundwork.json", 1, "traceability.tests lists the globs of the project's test files");
  else {
    const isTest = matchAny(traceCfg.tests);
    const REQ_CITE = new RegExp("(?<![\\w-])" + SP.src + "\\.(\\d+)(?![\\w])", "g");
    const covered = new Set();
    for (const f of FILES) {
      if (!TEXT_EXT.test(f) || !isTest(f) || f.startsWith(specsCfg.dir + "/")) continue;
      for (const line of lines(f) ?? []) for (const m of line.matchAll(REQ_CITE)) covered.add(Number(m[1]) + "." + Number(m[2]));
    }
    for (const [n, spec] of specs) {
      if (spec.status !== "implemented" && spec.status !== "accepted") continue;
      for (const [m, req] of spec.reqs) {
        if (req.removed || covered.has(n + "." + m)) continue;
        const id = SP.label(n) + "." + m;
        if (spec.status === "implemented") report("traceability/tests", spec.file, req.line, id + " is in an implemented spec, but no test file cites it (traceability.tests: " + traceCfg.tests.join(", ") + ")");
        else warn("traceability/tests", spec.file, req.line, id + " has no test that cites it yet");
      }
    }
  }
}

// ---- domain model (ADR-48) ----------------------------------------------------------------------
// One note. Its Vocabulary table, or a glossary in the domain-modeling skill's form (ADR-61), is the project's words:
// a term is defined once, and a word a term says to avoid warns wherever the files read use it.
const domainCfg = { file: "docs/domain.md", ...config.domain };
/** The table under a heading: { head, rows }, each row { cells, line }; null where the heading is missing. */
function tableUnder(rel, name) {
  const h = headings(rel).find((x) => x.text.toLowerCase() === name.toLowerCase());
  if (!h) return null;
  const all = [];
  sectionBody(rel, h).forEach((l, j) => {
    if (!/^\s*\|.*\|\s*$/.test(l)) return;
    const cells = l.trim().slice(1, -1).split(/(?<!\\)\|/).map((c) => c.trim());
    if (!cells.every((c) => /^:?-+:?$/.test(c))) all.push({ cells, line: h.line + 1 + j });
  });
  return { head: all[0] ?? null, rows: all.slice(1) };
}
/** The glossary form (ADR-61): `**Term**:` lines under `## Language`, a definition, and an optional `_Avoid_:` line. */
function glossaryTerms(rel, h) {
  const terms = [];
  sectionBody(rel, h).forEach((l, j) => {
    const line = h.line + 1 + j;
    const t = /^\s*\*\*([^*]+?)(?::\*\*|\*\*:)\s*(.*)$/.exec(l);
    if (t) { terms.push({ term: t[1].trim(), line, avoid: "" }); return; }
    const a = /^\s*(?:_Avoid_|\*Avoid\*|_Avoid:_|\*Avoid:\*)\s*:?\s*(.*)$/.exec(l);
    if (a && terms.length) terms[terms.length - 1].avoid = a[1];
  });
  return terms;
}
if (layers.includes("domain")) {
  const f = domainCfg.file;
  const t = exists(f) ? tableUnder(f, "Vocabulary") : null;
  const lang = exists(f) && !t ? headings(f).find((x) => x.text.toLowerCase() === "language") : null;
  const plain = (s) => (s ?? "").replace(/[*_\x60]/g, "").trim();
  /** [{ term, line, avoid }] from either form, or null when the note has neither. */
  let entries = null;
  if (!exists(f)) report("domain/note", f, 1, "the domain model is missing (domain.file)");
  else if (lang) entries = glossaryTerms(f, lang).map((e) => ({ ...e, term: plain(e.term), avoid: plain(e.avoid) }));
  else if (!t) report("domain/note", f, 1, 'the domain model has no "## Vocabulary" table and no "## Language" glossary');
  else if (!t.head || !/^term$/i.test(t.head.cells[0])) report("domain/note", f, 1, "the Vocabulary table starts with the row `| Term | Meaning | Avoid |`");
  else {
    const avoidAt = t.head.cells.findIndex((c) => /^avoid$/i.test(c));
    entries = t.rows.map((r) => ({ term: plain(r.cells[0]), line: r.line, avoid: avoidAt === -1 ? "" : plain(r.cells[avoidAt]) }));
  }
  if (entries) {
    const seen = new Map();
    const avoid = [];
    for (const e of entries) {
      if (!e.term) { report("domain/vocabulary", f, e.line, "a Vocabulary row has no term"); continue; }
      if (seen.has(e.term.toLowerCase())) report("domain/vocabulary", f, e.line, '"' + e.term + '" is defined twice (first on line ' + seen.get(e.term.toLowerCase()) + ")");
      else seen.set(e.term.toLowerCase(), e.line);
      for (const word of e.avoid.split(",").map((w) => w.trim().replace(/\.$/, "")).filter(Boolean)) avoid.push({ word, term: e.term, re: new RegExp("(?<![\\w-])" + esc(word) + "(?![\\w-])", "i") });
    }
    for (const a of avoid) if (seen.has(a.word.toLowerCase())) report("domain/vocabulary", f, seen.get(a.word.toLowerCase()), '"' + a.word + '" is a term, and also a word to avoid for "' + a.term + '"');
    // A warning, never an error: adopting a vocabulary must not block a commit. domain.avoidIn widens the files read
    // past the checked Markdown (ADR-60); Markdown is read as prose, any other file line by line.
    const avoidIn = Array.isArray(domainCfg.avoidIn) && domainCfg.avoidIn.length ? matchAny(domainCfg.avoidIn) : null;
    const scan = !avoid.length ? [] : avoidIn ? FILES.filter((x) => avoidIn(x) && x !== "scripts/groundwork-check.mjs") : mdFiles;
    for (const file of scan.filter((x) => x !== f)) {
      const ls = file.endsWith(".md") ? proseLines(file) : lines(file);
      if (!ls || ls.some((l) => l.includes("\0"))) continue;
      ls.forEach((line, i) => {
        for (const a of avoid) if (a.re.test(line)) warn("domain/avoid", file, i + 1, '"' + a.word + '" is a word to avoid: the term is "' + a.term + '" (' + f + ")");
      });
    }
  }
}

// ---- architecture overview (ADR-48) -------------------------------------------------------------
// One note: the parts, the tools, the scripts and the config files. What it says about the repo's files is held
// to the repo: a script or a config file it names must exist.
const archCfg = { file: "docs/architecture.md", ...config.architecture };
// An output folder the repo ignores is named but never checked out (ADR-59). Outside a git checkout the path must exist.
const gitIgnores = (rel) => spawnSync("git", ["check-ignore", "-q", "--", rel], { cwd: root }).status === 0;
if (layers.includes("architecture")) {
  const f = archCfg.file;
  if (!exists(f)) report("architecture/note", f, 1, "the architecture overview is missing (architecture.file)");
  else {
    for (const name of ["Tools", "Scripts", "Config files"]) {
      if (!headings(f).some((h) => h.text.toLowerCase() === name.toLowerCase())) report("architecture/note", f, 1, 'the architecture overview has no "## ' + name + '" section');
    }
    // In a command, a word is a repo path when it has a slash or a file extension; flags, URLs, scoped packages
    // and placeholders are not. In the Config files table the whole cell is the path.
    const pathLike = (w) => !/^[-@]/.test(w) && !/[<>*$:=]/.test(w) && (w.includes("/") || /\.[A-Za-z][A-Za-z0-9]{0,4}$/.test(w));
    for (const [name, whole] of [["Scripts", false], ["Config files", true]]) {
      for (const r of tableUnder(f, name)?.rows ?? []) {
        for (const m of (r.cells[0] ?? "").matchAll(/\x60([^\x60]+)\x60/g)) {
          const words = whole ? [m[1].trim()].filter((w) => !/[<>*$]/.test(w)) : m[1].trim().split(/\s+/).filter(pathLike);
          for (const w of words) {
            const rel = w.replace(/^\.\//, "").replace(/\/$/, "");
            if (rel.split("/").includes("..") || (!exists(rel) && !gitIgnores(w.replace(/^\.\//, "")))) report("architecture/paths", f, r.line, name + " names \x60" + w + "\x60, which is not in the repo");
          }
        }
      }
    }
  }
}

// ---- obsidian link ----------------------------------------------------------------------------
// Clicking into a table makes Obsidian re-pad every row to its widest cell, which turns one click into a whole-table
// diff. Rows are kept as `| a | b |` with `| --- |` separators; the content of a cell never changes. Tables inside
// fenced blocks and callouts (`> |`) are left alone.
const SEPARATOR_CELL = /^(:?)-+(:?)$/;
function tidyRow(line) {
  const eol = line.endsWith("\r") ? "\r" : "";
  const text = eol ? line.slice(0, -1) : line;
  const indent = /^\s*/.exec(text)[0];
  const body = text.trim();
  if (!body.startsWith("|") || !body.endsWith("|") || body.length < 2) return line;
  // A pipe inside a wiki-link is its alias, not a column break, escaped or not.
  const links = [];
  const masked = body.slice(1, -1).replace(/\[\[[^\]\n]*\]\]/g, (m) => `\u0000${links.push(m) - 1}\u0000`);
  const cells = masked.split(/(?<!\\)\|/).map((c) => c.trim().replace(/\u0000(\d+)\u0000/g, (_, i) => links[i]));
  const rule = cells.every((c) => SEPARATOR_CELL.test(c));
  const out = cells.map((c) => {
    if (!rule) return c;
    const [, left, right] = SEPARATOR_CELL.exec(c);
    return `${left}---${right}`;
  });
  return `${indent}| ${out.join(" | ")} |${eol}`;
}
function formatTables(text) {
  let fenced = false;
  return text.split("\n").map((line) => {
    if (line.trimStart().startsWith("```")) fenced = !fenced;
    return fenced ? line : tidyRow(line);
  }).join("\n");
}
const obsidianCfg = { target: "docs", formatOnCommit: true, ...config.obsidian };
const inVault = (f) => f.endsWith(".md") && (f.startsWith(`${obsidianCfg.target}/`) || obsidianCfg.target === ".");
if (args.has("--fmt") && args.has("--staged")) {
  // The pre-commit step (ADR-42): tidy the staged notes and stage them again. This is the one mode that runs
  // `git add`. A note with unstaged changes as well is left alone, so a held-back hunk is never staged.
  if (!layers.includes("obsidian") || obsidianCfg.formatOnCommit === false) process.exit(0);
  const git = (...a) => spawnSync("git", a, { cwd: root, encoding: "utf8" });
  const staged = git("diff", "--cached", "--name-only", "--relative", "--diff-filter=ACMR", "-z");
  const tidied = [];
  const held = [];
  for (const file of staged.status === 0 ? staged.stdout.split("\0").filter(Boolean).filter(inVault) : []) {
    let text;
    try { text = readFileSync(join(root, file), "utf8"); } catch { continue; }
    const tidy = formatTables(text);
    if (tidy === text) continue;
    if (git("diff", "--quiet", "--", file).status !== 0) { held.push(file); continue; }
    writeFileSync(join(root, file), tidy);
    if (git("add", "--", file).status === 0) tidied.push(file);
  }
  if (tidied.length) console.log(`[groundwork] tidied and staged ${tidied.join(", ")}`);
  if (held.length) console.log(`[groundwork] padded, but partly staged, so left alone: ${held.join(", ")}`);
  process.exit(0);
}
if (args.has("--fmt")) {
  const skip = new Set([argVal("--root"), argVal("--config")]);
  const named = argv.filter((a) => !a.startsWith("--") && !skip.has(a)).map((a) => relative(root, resolve(a)).replace(/\\/g, "/"));
  const tidied = [];
  for (const file of named.length ? named.filter((f) => f.endsWith(".md") && exists(f)) : FILES.filter(inVault)) {
    const text = readFileSync(join(root, file), "utf8");
    const tidy = formatTables(text);
    if (tidy === text) continue;
    writeFileSync(join(root, file), tidy);
    tidied.push(file);
  }
  console.log(tidied.length ? `[groundwork] tidied ${tidied.join(", ")}` : "[groundwork] tables ok");
  process.exit(0);
}
if (layers.includes("obsidian")) {
  for (const file of FILES.filter(inVault)) {
    const raw = readFileSync(join(root, file), "utf8").split("\n");
    const at = formatTables(raw.join("\n")).split("\n").findIndex((l, i) => l !== raw[i]);
    if (at !== -1) report("obsidian/format", file, at + 1, "a padded table (Obsidian re-pads on a click): run `node scripts/groundwork-check.mjs --fmt`");
  }
}

// ---- session hook (ADR-30) ----------------------------------------------------------------------
const hookCfg = { maxLines: 12, harnesses: ["claude", "codex"], focus: true, ...config.sessionHook };
const SUMMARY_CMD = "scripts/groundwork-check.mjs --summary";
if (layers.includes("session-hook")) {
  if (!layers.includes("open-work")) report("core/config", ".groundwork.json", 1, 'the "session-hook" layer summarises open work: it needs the open-work layer');
  if (typeof hookCfg.focus !== "boolean") report("core/config", ".groundwork.json", 1, "sessionHook.focus is true or false (false prints the counts line only, ADR-41)");
  const HARNESS = { claude: ".claude/settings.json", codex: ".codex/hooks.json" };
  for (const h of hookCfg.harnesses ?? []) {
    const file = HARNESS[h];
    if (!file) { report("core/config", ".groundwork.json", 1, `sessionHook.harnesses names an unknown harness "${h}" (${Object.keys(HARNESS).join(", ")})`); continue; }
    let json = null;
    try { json = JSON.parse(readFileSync(join(root, file), "utf8")); } catch {}
    const commands = (json?.hooks?.SessionStart ?? []).flatMap((g) => g?.hooks ?? []).flatMap((x) => [x?.command, x?.commandWindows]).filter((c) => typeof c === "string" && c.includes(SUMMARY_CMD));
    if (!commands.length) report("session-hook/command", file, 1, `no SessionStart hook runs \`node ${SUMMARY_CMD} --hook\``);
    // The vendored script is called by a path inside the repo, never one under a home folder (the same reason as ADR-22).
    for (const c of commands) if (/(^|[\s"'])(~|\$HOME|%USERPROFILE%|[A-Za-z]:[\\/]|\/(Users|home|root)\/)/.test(c)) report("session-hook/command", file, 1, `the hook command leaves the repo (${c}); call the script by its path relative to the repo`);
  }
  if (!(lines("AGENTS.md") ?? []).some((l) => l.includes(SUMMARY_CMD))) report("session-hook/command", "AGENTS.md", 1, `AGENTS.md carries the fallback for harnesses without hooks: run \`node ${SUMMARY_CMD}\` at the start of a session`);
}

/** The open-work summary a session starts from: counts by section, then the focus order. */
function summary(now) {
  if (!layers.includes("open-work") || !exists(ow.register)) return [];
  const counts = new Map();
  let closed = 0;
  for (const r of rows.values()) {
    if (!r.open) closed++;
    else counts.set(r.section, (counts.get(r.section) ?? 0) + 1);
  }
  const open = [...counts.values()].reduce((a, b) => a + b, 0);
  const parts = [...counts].map(([name, n]) => `${n} ${String(name).toLowerCase()}`).join(", ");
  const out = [`Open work (${ow.register}): ${open} open${parts ? ` — ${parts}` : ""}; ${closed} closed. Read it before planning work; log anything found but not fixed there before the session ends.`];
  // A project that prints the focus order with a script of its own switches this part off (ADR-41).
  const block = feat("focus") && hookCfg.focus !== false ? focusBlock() : null;
  if (block?.length) {
    const date = /Work order from (\d{4}-\d{2}-\d{2})/.exec(block[0].text)?.[1];
    const body = [];
    const pruned = [];
    let label = null;
    for (const { text } of block) {
      const m = FOCUS_ITEM.exec(text);
      if (!m) { if (/^\*\*[^*]+\*\*$/.test(text.trim())) label = text.trim().replace(/\*\*/g, ""); continue; }
      const n = Number(m[2]);
      const row = rows.get(n);
      if (row && !row.open) { pruned.push(OW.label(n)); continue; }
      if (label) { body.push(`${label}:`); label = null; }
      if (!row) { body.push(`${text} [no register row]`); continue; }
      const marks = [row.section];
      const blocked = row.cells[3] ?? "";
      const tag = tagOf(blocked);
      if (tag?.known) marks.push(tag.name);
      // The cell is prose, so a cited ID may be a blocker or a pairing ("take with …").
      for (const w of new Set([...blocked.matchAll(OW.cite)].map((x) => Number(x[1])))) if (w !== n && rows.get(w)?.open) marks.push(`cites open ${OW.label(w)}`);
      if (feat("size") && row.home) {
        const { lead, steps } = estimateOf(sectionBody(row.home.file, row.home.heading));
        const short = (e) => `${e.size} · ${e.who} · ${e.growth}`;
        const i = steps.findIndex((x) => x.est?.next);
        if (i !== -1) {
          const rest = steps.slice(i + 1).filter((x) => x.est && !x.est.actual).length;
          marks.push(`next step ${steps[i].n}: ${short(steps[i].est)}${rest ? ` · then ${rest} step${rest > 1 ? "s" : ""}` : ""}`);
        } else marks.push(lead ? short(lead) : "size?");
      }
      body.push(`${text} [${marks.join(" · ")}]`);
    }
    out.push(`Current focus${date ? ` (work order from ${date})` : ""}:`, ...body);
    if (pruned.length) out.push(`Closed since the last re-rank (prune at the next one): ${pruned.join(", ")}`);
    const nudge = nudgeOf(focusCfg.nudge);
    const ymd = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    if (nudge?.closed && pruned.length >= nudge.closed) out.push(`Re-rank due: ${pruned.length} focus item${pruned.length > 1 ? "s have" : " has"} closed since the order was set.`);
    if (nudge?.days && date && (now - new Date(`${date}T00:00:00`)) / 864e5 >= nudge.days) out.push(`Re-rank due: the order (${date}) is more than ${nudge.days} day${nudge.days > 1 ? "s" : ""} old.`);
    if (nudge && nudge.weekday !== undefined && date) {
      // The most recent reset (that weekday at that time, local) at or before now.
      const reset = new Date(now);
      reset.setDate(reset.getDate() - ((reset.getDay() - nudge.weekday + 7) % 7));
      reset.setHours(nudge.hour, nudge.minute, 0, 0);
      if (reset > now) reset.setDate(reset.getDate() - 7);
      if (date < ymd(reset)) out.push(`Re-rank due: the order (${date}) predates the last reset (${DAYS[nudge.weekday][0].toUpperCase()}${DAYS[nudge.weekday].slice(1)} ${String(nudge.hour).padStart(2, "0")}:${String(nudge.minute).padStart(2, "0")}).`);
    }
  }
  const max = Math.max(2, Number(hookCfg.maxLines) || 12);
  return out.length <= max ? out : [...out.slice(0, max - 1), `… ${out.length - max + 1} more line(s); the rest is in ${ow.register}`];
}
if (SUMMARY) {
  const text = summary(argVal("--now") ? new Date(argVal("--now")) : new Date()).join("\n");
  if (text) console.log(text);
  process.exit(0);
}

// ---- the project's own check script (ADR-47) ----------------------------------------------------
// Checks a project writes for itself (the recipe book, ADR-12) live in a script of its own, which a refresh never
// touches. Where checks.project names it, it runs here, after the layer checks, so one hook line covers both.
if (config.checks?.project !== undefined) {
  const script = String(config.checks.project).replace(/\\/g, "/");
  if (!script || /^(\/|[A-Za-z]:|~)/.test(script) || script.split("/").includes("..")) report("core/config", ".groundwork.json", 1, "checks.project names one script inside the repo, by its path from the repo root");
  else if (!exists(script)) report("core/project-check", script, 1, "the project's own check script is missing (checks.project)");
  else {
    const r = spawnSync(process.execPath, [script, "--root", root], { cwd: root, encoding: "utf8" });
    if (r.status !== 0) report("core/project-check", script, 1, ("the project's own check failed:\n" + ((r.stdout ?? "") + (r.stderr ?? "")).trim()).trim());
  }
}

// ---- report -----------------------------------------------------------------------------------
const warnCount = [...warnings.values()].reduce((a, l) => a + l.length, 0);
if (args.has("--json")) {
  console.log(JSON.stringify({ ok: errors.length === 0, errors, warnings: [...warnings.values()].flat(), dropped }, null, 2));
} else {
  for (const e of errors) console.log(`${e.file}:${e.line}  [${e.check}] ${e.message}`);
  if (warnCount) {
    console.log(`${warnCount} warning(s): ${[...warnings].map(([k, l]) => `${k} ${l.length}`).join(", ")}${args.has("--warnings") ? "" : " (--warnings lists them)"}`);
    if (args.has("--warnings")) for (const l of warnings.values()) for (const w of l) console.log(`  [${w.check}] ${w.file}:${w.line}  ${w.message}`);
  }
  console.log(errors.length ? `[groundwork] ${errors.length} error(s)` : `[groundwork] ok (${layers.join(", ")})`);
}
process.exit(errors.length ? 1 : 0);
