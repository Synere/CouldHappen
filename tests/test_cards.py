import base64
import json
import struct
import unittest
from unittest.mock import patch
import zlib

from helpers import cards, files
from support import workspace


def chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind+body) & 0xffffffff)


def ihdr(width=1, height=1, depth=8, color=2, compression=0, filter_method=0, interlace=0):
    return chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, depth, color, compression, filter_method, interlace))


def structure(*parts):
    return cards.SIGNATURE + b''.join(parts)


def png(metadata):
    return (cards.SIGNATURE + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) +
            b''.join(chunk(b'tEXt', k+b'\0'+v) for k, v in metadata) +
            chunk(b'IDAT', zlib.compress(b'\0\xff\0\0')) + chunk(b'IEND', b''))


class Cards(unittest.TestCase):
    def test_versions_originals_and_pixel_chunks(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        for card, fmt in [({'name': 'A', 'unknown': 42}, 'v1'),
                          ({'spec': 'chara_card_v2', 'data': {'name': 'B'}}, 'v2'),
                          ({'spec': 'chara_card_v3', 'data': {'name': 'C'}}, 'v3')]:
            data = json.dumps(card).encode()
            source = root / 'card.png'
            source.write_bytes(png([(b'ccv3' if fmt == 'v3' else b'chara', base64.b64encode(data)), (b'private', b'secret')]))
            result = cards.import_card(root, source)
            self.assertEqual(result['format'], fmt)
            saved = root / 'imports' / result['source_sha256'] / 'source.png'
            self.assertEqual(saved.read_bytes(), source.read_bytes())
            portrait = cards.portrait(root, saved)
            public = (root / 'public/assets' / portrait['portrait']).read_bytes()
            self.assertNotIn(b'tEXt', public)
            self.assertNotIn(b'secret', public)
            self.assertEqual([raw for k, _, raw in cards.chunks(public) if k == b'IDAT'],
                             [raw for k, _, raw in cards.chunks(source.read_bytes()) if k == b'IDAT'])
            self.assertEqual(files.read_json(root / 'public/cast.json')['characters'], [])
            self.assertEqual(cards.import_card(root, source)['source_sha256'], result['source_sha256'])
            json_source = root / 'card.json'
            json_source.write_bytes(data)
            self.assertEqual(cards.import_card(root, json_source)['format'], fmt)

    def test_malformed_preferred_crc_and_limits(self):
        good = base64.b64encode(b'{"name":"legacy"}')
        for data in (png([(b'chara', good), (b'ccv3', b'broken')]), png([])[:-3], png([])[:-1]+b'x',
                     png([(b'chara', good), (b'chara', base64.b64encode(b'{"name":"other"}'))])):
            with self.assertRaises(files.Invalid):
                cards.extract_png(data)
        with self.assertRaises(files.Invalid):
            cards.definition(b'x' * (cards.META_LIMIT+1))

    def test_critical_png_structure(self):
        idat = chunk(b'IDAT', zlib.compress(b'\0\xff\0\0'))
        iend = chunk(b'IEND', b'')
        cases = {
            'missing IHDR': structure(idat, iend),
            'IHDR not first': structure(chunk(b'tEXt', b'x\0y'), ihdr(), idat, iend),
            'duplicate IHDR': structure(ihdr(), ihdr(), idat, iend),
            'missing IDAT': structure(ihdr(), iend),
            'bytes after IEND': structure(ihdr(), idat, iend) + b'x',
            'IEND content': structure(ihdr(), idat, chunk(b'IEND', b'x')),
            'unknown critical': structure(ihdr(), chunk(b'ABCD', b''), idat, iend),
            'invalid chunk type': structure(ihdr(), chunk(b'A1CD', b''), idat, iend),
            'zero width': structure(ihdr(width=0), idat, iend),
            'zero height': structure(ihdr(height=0), idat, iend),
            'invalid depth': structure(ihdr(depth=4, color=2), idat, iend),
            'indexed without palette': structure(ihdr(depth=8, color=3), idat, iend),
            'palette after IDAT': structure(ihdr(depth=8, color=3), idat, chunk(b'PLTE', b'\0\0\0'), iend),
            'non-contiguous IDAT': structure(ihdr(), idat, chunk(b'tEXt', b'k\0v'), idat, iend),
            'short IHDR': structure(chunk(b'IHDR', b'\0' * 12), idat, iend),
            'invalid compression': structure(ihdr(compression=1), idat, iend),
            'invalid filter': structure(ihdr(filter_method=1), idat, iend),
            'invalid interlace': structure(ihdr(interlace=2), idat, iend),
        }
        for label, data in cases.items():
            with self.subTest(label=label), self.assertRaises(files.Invalid):
                cards.chunks(data)
        kinds = [kind for kind, _, _ in cards.chunks(structure(ihdr(), chunk(b'vpAg', b'private'), idat, iend))]
        self.assertIn(b'vpAg', kinds)

    def test_metadata_and_source_limits(self):
        self.assertEqual(cards.SOURCE_LIMIT, 32 * 1024 * 1024)
        self.assertEqual(cards.META_LIMIT, 8 * 1024 * 1024)
        too_long = b'A' * ((cards.META_LIMIT + 2) // 3 * 4 + 1)
        with self.assertRaises(files.Invalid):
            cards.extract_png(png([(b'chara', too_long)]))
        with self.assertRaises(files.Invalid):
            cards.definition(b'\xff')
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        source = root / 'large.png'
        source.write_bytes(b'x' * 9)
        with patch.object(cards, 'SOURCE_LIMIT', 8):
            with self.assertRaises(files.Invalid):
                cards.bounded(source)

    def test_portrait_resolves_original_file_and_import_folder(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        card = base64.b64encode(json.dumps({'name': 'A'}).encode())
        original = root / 'downloads' / 'card.png'
        original.parent.mkdir()
        original.write_bytes(png([(b'chara', card)]))
        with self.assertRaisesRegex(files.Invalid, 'run import-card'):
            cards.portrait(root, original)
        self.assertEqual(list((root / 'public/assets').glob('*.png')), [])
        result = cards.import_card(root, original)
        saved = root / 'imports' / result['source_sha256'] / 'source.png'
        self.assertEqual(result['source_path'], str(saved.resolve()))
        expected = cards.portrait(root, saved)
        for source in (original, saved.parent):
            with self.subTest(source=source.name):
                self.assertEqual(cards.portrait(root, source), expected)
        original.write_bytes(png([(b'chara', card), (b'tEXt', b'changed')]))
        with self.assertRaisesRegex(files.Invalid, 'run import-card'):
            cards.portrait(root, original)
        other = root / 'imports' / result['source_sha256'] / 'card.json'
        with self.assertRaises(files.Invalid):
            cards.portrait(root, other)

    def test_portrait_rejects_corrupt_structure_without_emitting_an_asset(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        bad = structure(ihdr(), chunk(b'ABCD', b''), chunk(b'IDAT', zlib.compress(b'\0\xff\0\0')), chunk(b'IEND', b''))
        folder = root / 'imports' / files.digest(bad)
        folder.mkdir(parents=True)
        source = folder / 'source.png'
        source.write_bytes(bad)
        with self.assertRaises(files.Invalid):
            cards.portrait(root, source)
        self.assertEqual(list((root / 'public/assets').glob('*.png')), [])
