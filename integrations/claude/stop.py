"""Opt-in Claude Stop translation; no inference from stale waiting markers."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from helpers.checkpoints import native

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
args = parser.parse_args()
try:
    result = native(args.root, json.load(sys.stdin))
except (ValueError, OSError, TypeError) as exc:
    result = {'systemMessage': 'CouldHappen checkpoint assurance unavailable: ' + str(exc)}
print(json.dumps(result))
