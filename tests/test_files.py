import json
import os
import subprocess
import unittest
from unittest.mock import patch
from uuid import uuid4

from helpers import files
from support import workspace, REPO
from test_cards import png


class Files(unittest.TestCase):
    def test_roundtrip_reserved_and_trailing_newlines(self):
        fixture = json.loads((REPO / 'tests/fixtures/public-v1.json').read_text(encoding='utf-8'))
        for body in fixture['bodies'] + ['', '\n', '\n\n']:
            with self.subTest(body=body):
                encoded = '# Story\n\n' + files.entry(body, 'human')
                self.assertEqual(files.parse(encoded.replace('\n', '\r\n'), 'story')[0]['body'], files.normalize(body))
        for text in fixture['invalid']:
            with self.assertRaises(files.Invalid):
                files.parse(text, 'story')

    def test_cross_log_duplicates_and_invalid_references(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        ident = str(uuid4())
        for channel in ('story', 'director'):
            files.atomic(root / f'public/{channel}.md', '# ' + channel.title() + '\n' + files.entry('hello', id=ident))
        with self.assertRaises(files.Invalid):
            files.snapshot(root)
        files.atomic(root / 'public/story.md', '# Story\n')
        files.write_json(root / 'public/work.json', {'schema_version': 1, 'mode': 'awaiting_director', 'director_question_id': str(uuid4())})
        with self.assertRaises(files.Invalid):
            files.snapshot(root)
        files.write_json(root / 'public/work.json', {'schema_version': 1, 'mode': 'awaiting_director', 'director_question_id': ident})
        self.assertEqual(files.snapshot(root)['work']['mode'], 'awaiting_director')
        files.write_json(root / 'public/cast.json', {'schema_version': 1, 'characters': [{'id': 'x', 'name': 'X', 'portrait': '../private.png'}]})
        with self.assertRaises(files.Invalid):
            files.snapshot(root)

    def test_replacement_failure_preserves_previous_file(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        path = root / 'public/story.md'
        original = path.read_bytes()
        with patch('helpers.files.os.replace', side_effect=OSError('replace failed')):
            with self.assertRaises(OSError):
                files.atomic(path, b'# Story\n\nreplacement\n')
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(path.parent.glob('.couldhappen-tmp-*')), [])

    def test_asset_path_rejects_traversal_and_symlink_escape(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        assets = root / 'public/assets'
        assets.mkdir()
        outside = root / 'outside.png'
        outside.write_bytes(png([]))
        valid = assets / 'valid.png'
        valid.write_bytes(png([]))
        self.assertEqual(files.asset_path(root, 'valid.png'), valid.resolve())
        for name in ('../outside.png', '/outside.png', '..\\outside.png', '', 'missing.png', 'outside.txt'):
            with self.subTest(name=name), self.assertRaises(files.Invalid):
                files.asset_path(root, name)
        link = assets / 'link.png'
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            link = None
        if link is not None:
            with self.assertRaises(files.Invalid):
                files.asset_path(root, 'link.png')
            files.write_json(root / 'public/cast.json', {'schema_version': 1, 'characters': [
                {'id': 'a', 'name': 'A', 'portrait': 'link.png'}]})
            with self.assertRaises(files.Invalid):
                files.snapshot(root)
        external = root / 'external'
        external.mkdir()
        (external / 'portrait.png').write_bytes(png([]))
        escape = assets / 'escape'
        try:
            escape.symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError):
            if os.name == 'nt':
                result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(escape), str(external)], capture_output=True)
                if result.returncode:
                    self.skipTest('directory symlink/junction unavailable')
            else:
                self.skipTest('directory symlink unavailable')
        with self.assertRaises(files.Invalid):
            files.asset_path(root, 'escape/portrait.png')

    def test_public_asset_validates_referenced_png_structure(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        assets = root / 'public/assets'
        assets.mkdir()
        valid = png([])
        (assets / 'valid.png').write_bytes(valid)
        self.assertEqual(files.public_asset(root, 'valid.png'), valid)
        (assets / 'bad.png').write_bytes(b'not a PNG')
        with self.assertRaises(files.Invalid):
            files.public_asset(root, 'bad.png')
        files.write_json(root / 'public/cast.json', {'schema_version': 1, 'characters': [
            {'id': 'a', 'name': 'A', 'portrait': 'bad.png'}]})
        with self.assertRaises(files.Invalid):
            files.snapshot(root)

    def test_malformed_cast_variants(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        (root / 'public/assets').mkdir()
        (root / 'public/assets/ok.png').write_bytes(png([]))
        good = {'schema_version': 1, 'characters': [
            {'id': 'a', 'name': 'A', 'description': 'Disclosed', 'portrait': 'ok.png'},
            {'id': 'b', 'name': 'B'}]}
        files.write_json(root / 'public/cast.json', good)
        self.assertEqual(len(files.snapshot(root)['cast']['characters']), 2)
        files.write_json(root / 'public/cast.json', {'schema_version': 1, 'characters': [
            {'id': 'b', 'name': 'B', 'portrait': None}]})
        self.assertEqual(files.snapshot(root)['cast']['characters'][0]['id'], 'b')
        bad = [
            [],
            None,
            {'schema_version': 2, 'characters': []},
            {'schema_version': 1, 'characters': {}},
            {'schema_version': 1, 'characters': ['character']},
            {'schema_version': 1, 'characters': [{'name': 'Missing id'}]},
            {'schema_version': 1, 'characters': [{'id': '', 'name': 'Empty id'}]},
            {'schema_version': 1, 'characters': [{'id': 'a'}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': ' '}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'unknown': 1}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'description': 5}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'portrait': 5}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'portrait': ''}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'portrait': '../private.png'}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'portrait': '/absolute.png'}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'portrait': 'missing.png'}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A', 'portrait': 'file.txt'}]},
            {'schema_version': 1, 'characters': [{'id': 'a', 'name': 'A'}, {'id': 'a', 'name': 'Again'}]},
        ]
        for cast in bad:
            with self.subTest(cast=cast):
                files.write_json(root / 'public/cast.json', cast)
                with self.assertRaises(files.Invalid):
                    files.snapshot(root)
        files.write_json(root / 'public/cast.json', good)
        for work in ([], {'schema_version': 2, 'mode': 'play', 'director_question_id': None},
                     {'schema_version': 1, 'mode': 'other', 'director_question_id': None},
                     {'schema_version': 1, 'mode': 'play'}):
            with self.subTest(work=work):
                files.write_json(root / 'public/work.json', work)
                with self.assertRaises(files.Invalid):
                    files.snapshot(root)

    def test_story_pictures_are_exposed_as_assets_and_must_exist(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        (root / 'public/assets').mkdir(parents=True, exist_ok=True)
        (root / 'public/assets/scene-1.png').write_bytes(png([]))
        body = 'The door opens.\n\n![A lit doorway](/api/assets/scene-1.png)\n\n```\n![code](/api/assets/ignored.png)\n```'
        self.assertEqual(files.pictures(body), ['scene-1.png'])
        files.atomic(root / 'public/story.md', '# Story\n\n' + files.entry(body))
        snap = files.snapshot(root)
        self.assertEqual(set(snap['assets']), {'scene-1.png'})
        files.atomic(root / 'public/story.md', '# Story\n\n' + files.entry('![x](/api/assets/missing.png)'))
        with self.assertRaises(files.Invalid):
            files.snapshot(root)

    def test_picture_line_fixture(self):
        """The reader's splitBody (web/tests/session.test.js) runs the same fixture; the two patterns must agree."""
        for case in json.loads((REPO / 'tests/fixtures/picture_lines.json').read_text(encoding='utf-8')):
            with self.subTest(line=case['line'][:60]):
                self.assertEqual(files.pictures(case['line']), [case['name']] if case['name'] else [])

    def test_portrait_button_must_be_boolean(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        cast = files.read_json(root / 'public/cast.json')
        files.write_json(root / 'public/cast.json', {**cast, 'portrait_button': True})
        self.assertTrue(files.snapshot(root)['cast']['portrait_button'])
        files.write_json(root / 'public/cast.json', {**cast, 'portrait_button': 'yes'})
        with self.assertRaises(files.Invalid):
            files.snapshot(root)

    def test_present_flag_must_be_boolean(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        cast = files.read_json(root / 'public/cast.json')
        for value, valid in ((False, True), (True, True), ('no', False), (0, False)):
            with self.subTest(value=value):
                files.write_json(root / 'public/cast.json', {**cast, 'characters': [{'id': 'x', 'name': 'X', 'present': value}]})
                if valid:
                    self.assertEqual(files.snapshot(root)['cast']['characters'][0]['present'], value)
                else:
                    with self.assertRaises(files.Invalid):
                        files.snapshot(root)
