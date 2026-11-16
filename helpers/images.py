"""Recognise, check and strip metadata from the four picture formats the reader shows (ADR-12).

The format is read from the bytes, never from a name, URL or server header. `clean` walks the
file's structure, refuses anything malformed, and returns a copy with metadata removed while
every byte that draws the picture is kept.
"""
import struct

from .files import Invalid

TYPES = {'png': 'image/png', 'jpg': 'image/jpeg', 'webp': 'image/webp', 'gif': 'image/gif'}


def kind(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if data.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp'
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    raise Invalid('Not a PNG, JPEG, WebP or GIF image')


def clean(data):
    """Return (extension, copy without metadata); raise Invalid for a malformed or unknown file."""
    ext = kind(data)
    return ext, {'png': _png, 'jpg': _jpeg, 'webp': _webp, 'gif': _gif}[ext](data)


def check(data, ext):
    """Raise Invalid unless data is a well-formed picture of the format its extension names."""
    if kind(data) != ext:
        raise Invalid(f'File content is not {ext.upper()}')
    clean(data)


def _png(data):
    from .cards import APPEARANCE, SIGNATURE, chunks
    return SIGNATURE + b''.join(raw for k, _, raw in chunks(data) if k in APPEARANCE)


def _jpeg(data):
    out, pos, frame, scan = [b'\xff\xd8'], 2, False, False
    while True:
        if pos >= len(data) or data[pos] != 0xff:
            raise Invalid('Malformed JPEG: expected a marker')
        while pos < len(data) and data[pos] == 0xff:
            pos += 1
        if pos >= len(data):
            raise Invalid('Truncated JPEG')
        marker = data[pos]
        pos += 1
        if marker == 0xd9:
            if not (frame and scan):
                raise Invalid('JPEG has no image data')
            out.append(b'\xff\xd9')
            return b''.join(out)  # bytes after the end marker are dropped
        if marker == 0x01 or 0xd0 <= marker <= 0xd7:
            out.append(bytes((0xff, marker)))
            continue
        if marker in (0x00, 0xd8) or pos + 2 > len(data):
            raise Invalid('Malformed JPEG marker')
        size = struct.unpack('>H', data[pos:pos+2])[0]
        if size < 2 or pos + size > len(data):
            raise Invalid('Truncated JPEG segment')
        body = data[pos+2:pos+size]
        segment = bytes((0xff, marker)) + data[pos:pos+size]
        pos += size
        if 0xc0 <= marker <= 0xcf and marker not in (0xc4, 0xc8, 0xcc):
            frame = True
        # Keep what affects how the picture looks: JFIF, the ICC profile, Adobe's colour transform.
        keep = not (0xe1 <= marker <= 0xef or marker == 0xfe) or \
            (marker == 0xe2 and body.startswith(b'ICC_PROFILE\0')) or (marker == 0xee and body.startswith(b'Adobe'))
        if keep:
            out.append(segment)
        if marker == 0xda:
            if not frame:
                raise Invalid('JPEG scan before frame')
            scan = True
            start = pos
            while True:  # entropy-coded data runs to the next marker that is not a stuffed byte or restart
                pos = data.find(b'\xff', pos)
                if pos < 0 or pos + 1 >= len(data):
                    raise Invalid('Truncated JPEG scan')
                following = data[pos+1]
                if following == 0x00 or 0xd0 <= following <= 0xd7 or following == 0xff:
                    pos += 1 if following == 0xff else 2
                    continue
                break
            out.append(data[start:pos])


WEBP_KEEP = {b'VP8X', b'VP8 ', b'VP8L', b'ALPH', b'ANIM', b'ANMF', b'ICCP'}


def _webp(data):
    size = struct.unpack('<I', data[4:8])[0]
    if size < 4 or size + 8 > len(data):
        raise Invalid('Truncated WebP')
    pos, end, out, image = 12, size + 8, [], False
    while pos < end:
        if pos + 8 > end:
            raise Invalid('Truncated WebP chunk')
        fourcc, length = data[pos:pos+4], struct.unpack('<I', data[pos+4:pos+8])[0]
        stop = pos + 8 + length
        if stop > end:
            raise Invalid('Truncated WebP chunk')
        body = data[pos+8:stop]
        if fourcc in (b'VP8 ', b'VP8L', b'ANMF'):
            image = True
        if fourcc == b'VP8X':
            if length < 10:
                raise Invalid('Malformed WebP header chunk')
            body = bytes((body[0] & ~0x0c,)) + body[1:]  # clear the EXIF and XMP flags
        if fourcc in WEBP_KEEP:
            out.append(fourcc + struct.pack('<I', length) + body + (b'\0' if length % 2 else b''))
        pos = stop + length % 2
    if not image:
        raise Invalid('WebP has no image data')
    payload = b'WEBP' + b''.join(out)
    return b'RIFF' + struct.pack('<I', len(payload)) + payload


def _blocks(data, pos):
    """End position of a GIF sub-block sequence starting at pos."""
    while True:
        if pos >= len(data):
            raise Invalid('Truncated GIF')
        n = data[pos]
        pos += 1 + n
        if n == 0:
            return pos


def _gif(data):
    if len(data) < 13:
        raise Invalid('Truncated GIF')
    packed = data[10]
    pos = 13 + (3 * 2 ** ((packed & 7) + 1) if packed & 0x80 else 0)
    out, images = [data[:pos]], 0
    while True:
        if pos >= len(data):
            raise Invalid('GIF has no trailer')
        label = data[pos]
        if label == 0x3b:
            if not images:
                raise Invalid('GIF has no image data')
            out.append(b'\x3b')
            return b''.join(out)  # bytes after the trailer are dropped
        if label == 0x2c:
            if pos + 10 > len(data):
                raise Invalid('Truncated GIF image')
            local = data[pos+9]
            stop = pos + 10 + (3 * 2 ** ((local & 7) + 1) if local & 0x80 else 0) + 1  # + LZW code size
            stop = _blocks(data, stop)
            out.append(data[pos:stop])
            images += 1
        elif label == 0x21:
            if pos + 2 > len(data):
                raise Invalid('Truncated GIF extension')
            ext = data[pos+1]
            stop = _blocks(data, pos + 2)
            first = data[pos+3:pos+3+data[pos+2]] if pos + 2 < len(data) else b''
            if ext in (0xf9, 0x01) or (ext == 0xff and first in (b'NETSCAPE2.0', b'ANIMEXTS1.0')):
                out.append(data[pos:stop])  # timing, plain text and the loop count; comments and other apps go
        else:
            raise Invalid('Malformed GIF block')
        pos = stop
