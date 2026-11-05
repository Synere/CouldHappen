"""Reference for APPLY.md part 3. Insert into helpers/files.py just above snapshot() (that module already has
`re`, `Path`, `Invalid` and `read_json`) and make snapshot() return read_sheet(root) as 'sheet'.
The `theme` and `actions` keys belong to the scene-images package; they are accepted here so that either
package can be applied first. Keep the allowed keys in step with what the reader renders."""
SHEET_THEME_VARS = {'accent', 'accent-deep', 'highlight', 'highlight-deep', 'ink', 'muted', 'line', 'line-soft',
                    'reading', 'surface', 'panel', 'panel-deep', 'side-bg', 'link'}


def read_sheet(root):
    """Optional public/sheet.json: a writer-maintained side display (stats, rolls, a mood theme, quick actions)."""
    path = Path(root) / 'public/sheet.json'
    if not path.exists():
        return None
    sheet = read_json(path)

    def text(value, limit=200):
        return isinstance(value, str) and len(value) <= limit

    def keys(value, allowed, required=()):
        return isinstance(value, dict) and not set(value) - set(allowed) and set(required) <= set(value)

    if not keys(sheet, {'schema_version', 'title', 'subtitle', 'groups', 'log', 'theme', 'actions'}, {'schema_version'}) or sheet['schema_version'] != 1:
        raise Invalid('Unsupported sheet format')
    if not text(sheet.get('title', '')) or not text(sheet.get('subtitle', '')):
        raise Invalid('Invalid sheet title')
    groups = sheet.get('groups', [])
    if not isinstance(groups, list) or len(groups) > 20:
        raise Invalid('Invalid sheet groups')
    for group in groups:
        if not keys(group, {'title', 'rows'}, {'title', 'rows'}) or not text(group['title']) or not isinstance(group['rows'], list) or len(group['rows']) > 60:
            raise Invalid('Invalid sheet group')
        for row in group['rows']:
            value = row.get('value') if isinstance(row, dict) else None
            if not keys(row, {'label', 'value', 'note'}, {'label', 'value'}) or not text(row['label']) \
                    or not (text(value) or (isinstance(value, int) and not isinstance(value, bool))) or not text(row.get('note', ''), 400):
                raise Invalid('Invalid sheet row')
    log = sheet.get('log', [])
    if not isinstance(log, list) or len(log) > 50 or not all(text(item, 400) for item in log):
        raise Invalid('Invalid sheet log')
    actions = sheet.get('actions', [])
    if not isinstance(actions, list) or len(actions) > 4:
        raise Invalid('Invalid sheet actions')
    for action in actions:
        if not keys(action, {'label', 'body'}, {'label', 'body'}) or not text(action['label'], 40) or not action['label'].strip() \
                or not text(action['body'], 500) or not action['body'].strip():
            raise Invalid('Invalid sheet action')
    theme = sheet.get('theme')
    if theme is not None:
        if not keys(theme, {'name', 'scheme', 'backdrop', 'vars'}) or not text(theme.get('name', '')) \
                or theme.get('scheme', 'light') not in ('light', 'dark') or not isinstance(theme.get('backdrop', False), bool):
            raise Invalid('Invalid sheet theme')
        colors = theme.get('vars', {})
        if not isinstance(colors, dict) or set(colors) - SHEET_THEME_VARS \
                or not all(isinstance(v, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', v) for v in colors.values()):
            raise Invalid('Invalid sheet theme colors')
    return sheet
