import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from helpers import checkpoints, files
from support import workspace, REPO


class Integrations(unittest.TestCase):
    def test_translation_armed_scope_and_errors(self):
        temp, root = workspace()
        self.addCleanup(temp.cleanup)
        self.assertEqual(checkpoints.native(root, {'cwd': str(root)}), {})
        files.write_json(root / '.couldhappen/control.json', {'armed': True})
        self.assertEqual(checkpoints.native(root, {'cwd': str(root.parent)}), {})
        event = {'cwd': str(root), 'stop_hook_active': True}
        with patch('helpers.checkpoints.check', return_value=({'status': 'clean'}, 0)):
            self.assertEqual(checkpoints.native(root, event), {})
        with patch('helpers.checkpoints.check', return_value=({'status': 'dirty', 'paths': [{'path': 'story.md'}]}, 1)):
            self.assertEqual(checkpoints.native(root, event)['decision'], 'block')
        with patch('helpers.checkpoints.check', return_value=({'status': 'error', 'message': 'no git'}, 2)):
            self.assertIn('unavailable', checkpoints.native(root, event)['systemMessage'])
        for host in ('codex', 'claude'):
            result = subprocess.run([sys.executable, str(REPO / f'integrations/{host}/stop.py'), '--root', str(root)],
                input=json.dumps(event), text=True, capture_output=True, check=True)
            self.assertIn('systemMessage', json.loads(result.stdout))  # no repository, not clean
