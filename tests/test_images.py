"""ADR-12: the four picture formats are recognised from their bytes, checked, and stripped of metadata."""
import struct
import unittest

from helpers import files, images
from test_cards import png


def seg(marker, body):
    return bytes((0xff, marker)) + struct.pack('>H', len(body) + 2) + body


def jpeg(extra=b''):
    return (b'\xff\xd8' + seg(0xe0, b'JFIF\0\x01\x01\0\0\x01\0\x01\0\0') + seg(0xe1, b'Exif\0\0secret') +
            seg(0xe2, b'ICC_PROFILE\0\x01\x01colour') + seg(0xfe, b'secret comment') + seg(0xdb, b'\0' + b'\x01' * 64) +
            seg(0xc0, b'\x08\0\x01\0\x01\x01\x01\x11\0') + seg(0xc4, b'\0' + b'\0' * 16) +
            seg(0xda, b'\x01\x01\0\0\x3f\0') + b'\x12\xff\x00\x34\xff\xd0\x56' + b'\xff\xd9' + extra)


def riff(*chunks):
    body = b'WEBP' + b''.join(k + struct.pack('<I', len(v)) + v + (b'\0' if len(v) % 2 else b'') for k, v in chunks)
    return b'RIFF' + struct.pack('<I', len(body)) + body


def webp():
    return riff((b'VP8X', bytes((0x0c | 0x10,)) + b'\0' * 9), (b'VP8L', b'\x2f\0\0\0\0'),
                (b'EXIF', b'secret'), (b'XMP ', b'<x>secret</x>'))


def gif(extra=b''):
    table = b'\0\0\0\xff\xff\xff'
    return (b'GIF89a' + struct.pack('<HH', 1, 1) + b'\x80\0\0' + table +
            b'\x21\xff\x0bNETSCAPE2.0\x03\x01\0\0\0' + b'\x21\xfe\x06secret\0' + b'\x21\xff\x0bXMP DataXMP\x06secret\0' +
            b'\x21\xf9\x04\0\x0a\0\0\0' + b'\x2c' + struct.pack('<HHHH', 0, 0, 1, 1) + b'\0' + b'\x02\x02\x44\x01\0' +
            b'\x3b' + extra)


class Images(unittest.TestCase):
    def test_each_format_is_recognised_and_stripped(self):
        for data, ext in ((png([(b'chara', b'secret')]), 'png'), (jpeg(b'trailing secret'), 'jpg'),
                          (webp(), 'webp'), (gif(b'trailing secret'), 'gif')):
            with self.subTest(ext):
                self.assertEqual(images.kind(data), ext)
                got, cleaned = images.clean(data)
                self.assertEqual(got, ext)
                self.assertNotIn(b'secret', cleaned)
                images.check(cleaned, ext)
                self.assertEqual(images.clean(cleaned), (ext, cleaned))

    def test_picture_data_is_kept(self):
        _, cleaned = images.clean(jpeg())
        for kept in (b'JFIF', b'ICC_PROFILE\0', b'\x12\xff\x00\x34\xff\xd0\x56', b'\xff\xc0', b'\xff\xc4', b'\xff\xdb'):
            self.assertIn(kept, cleaned)
        _, cleaned = images.clean(webp())
        self.assertIn(b'VP8L', cleaned)
        self.assertEqual(cleaned[cleaned.index(b'VP8X') + 8] & 0x0c, 0)
        self.assertEqual(struct.unpack('<I', cleaned[4:8])[0], len(cleaned) - 8)
        _, cleaned = images.clean(gif())
        for kept in (b'NETSCAPE2.0', b'\x21\xf9', b'\x02\x02\x44\x01\0'):
            self.assertIn(kept, cleaned)

    def test_other_and_malformed_files_are_refused(self):
        for data in (b'<svg xmlns="http://www.w3.org/2000/svg"/>', b'<html></html>', b'PK\x03\x04zip', b'',
                     jpeg()[:-2], jpeg()[:40], b'\xff\xd8\xff\xd9', riff((b'EXIF', b'x')), webp()[:20],
                     gif()[:-1], gif()[:30], b'GIF89a' + b'\0' * 7 + b'\x3b'):
            with self.assertRaises(files.Invalid):
                images.clean(data)

    def test_check_matches_content_to_extension(self):
        with self.assertRaises(files.Invalid):
            images.check(gif(), 'png')
        images.check(gif(), 'gif')


if __name__ == '__main__':
    unittest.main()
