import json
from pathlib import Path
import tempfile


REPO = Path(__file__).resolve().parents[1]

# A fresh, empty workspace. Tests never read the live public files or config, so they
# keep passing in a story workspace once play has begun.
EMPTY_CONFIG = {
    'schema_version': 1, 'workspace_id': None, 'poll_interval_ms': 1000,
    'checkpoint': {'scope': ['.'], 'exclude': ['docs/history/', 'docs/research/', 'docs/reviews/',
                                               '.research/', 'goldfish_reviews/']},
}
EMPTY_PUBLIC = {
    'story.md': '# Story\n',
    'director.md': '# Director\n',
    'cast.json': json.dumps({'schema_version': 1, 'characters': []}, indent=2) + '\n',
    'work.json': json.dumps({'schema_version': 1, 'mode': 'play', 'director_question_id': None}, indent=2) + '\n',
}


def workspace():
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / 'public').mkdir()
    (root / 'couldhappen.json').write_text(json.dumps(EMPTY_CONFIG, indent=2) + '\n', encoding='utf-8')
    for name, text in EMPTY_PUBLIC.items():
        (root / 'public' / name).write_bytes(text.encode())
    return temp, root
