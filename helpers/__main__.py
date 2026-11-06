import argparse
import json
from pathlib import Path
import sys

from . import cards, checkpoints, files, runtime, stories


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')  # Windows consoles default to a legacy code page
    parser = argparse.ArgumentParser(description='CouldHappen local file operations (no model calls)')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('validate', 'serve', 'wait', 'import-card', 'portrait'):
        sub = commands.add_parser(name)
        sub.add_argument('--root', default='.')
        if name == 'serve':
            sub.add_argument('--frontend-origin', required=True)
            sub.add_argument('--previous-helper-stopped', action='store_true')
        if name == 'wait':
            sub.add_argument('--timeout', type=float, default=0)
        if name in ('import-card', 'portrait'):
            sub.add_argument('--source', required=True)
    sub = commands.add_parser('entry')
    sub.add_argument('--role', choices=('writer', 'human'), default='writer')
    sub.add_argument('--body-file', required=True)
    sub.add_argument('--id')
    sub.add_argument('--status', choices=('pending', 'addressed', 'deferred'))
    sub = commands.add_parser('writer')
    sub.add_argument('operation', choices=('claim', 'pause', 'release', 'block', 'recover', 'invalidate', 'close'))
    sub.add_argument('--root', default='.')
    sub.add_argument('--token')
    switch = sub.add_mutually_exclusive_group()
    switch.add_argument('--on', action='store_true')
    switch.add_argument('--off', action='store_true')
    sub.add_argument('--previous-writer-stopped', action='store_true')
    sub = commands.add_parser('new-story')
    sub.add_argument('--root', default='.')
    sub.add_argument('--destination', required=True)
    sub = commands.add_parser('stop')
    sub.add_argument('--root', default='.')
    sub = commands.add_parser('checkpoint')
    sub.add_argument('operation', choices=('check', 'inspect'))
    sub.add_argument('--root', default='.')
    sub.add_argument('--ref')
    args = parser.parse_args()
    code = 0
    try:
        if args.command == 'entry':
            sys.stdout.write(files.entry(Path(args.body_file).read_text(encoding='utf-8'), args.role, args.id, args.status))
            return 0
        if args.command == 'validate':
            files.snapshot(args.root)
            result = {'status': 'valid'}
        elif args.command == 'serve':
            from .bridge import serve
            serve(args.root, args.frontend_origin, args.previous_helper_stopped)
            return 0
        elif args.command == 'wait':
            if args.timeout < 0:
                raise files.Invalid('Timeout must be nonnegative')
            result, code = runtime.wait(args.root, args.timeout)
        elif args.command in ('import-card', 'portrait'):
            result = (cards.import_card if args.command == 'import-card' else cards.portrait)(args.root, args.source)
        elif args.command == 'new-story':
            result = stories.new_story(args.root, args.destination)
        elif args.command == 'stop':
            result = runtime.stop(args.root)
            code = 0 if result['status'] == 'stopped' else 2
        elif args.command == 'writer':
            if args.operation == 'block' and not (args.on or args.off):
                raise files.Invalid('Choose --on or --off')
            result = runtime.control(args.root, args.operation, token=args.token, on=args.on,
                                     previous_writer_stopped=args.previous_writer_stopped)
            code = {'dirty': 1, 'error': 2}.get(result['status'], 0)
        else:
            if args.operation == 'inspect' and not args.ref:
                raise files.Invalid('Commit --ref required')
            result, code = checkpoints.inspect(args.root, args.ref) if args.operation == 'inspect' else checkpoints.check(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result, code = {'status': 'error', 'message': str(exc)}, 2
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == '__main__':
    sys.exit(main())
