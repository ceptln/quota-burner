import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublishTests(unittest.TestCase):
    def payload(self):
        return {'taken_at': '2020-01-01T00:00:00Z', 'codex': {
            'five_hour': {'utilization': 0.12, 'resets_at': 2100000000, 'window_seconds': 18000},
            'seven_day': {'utilization': 0.4, 'resets_at': 2100500000, 'window_seconds': 604800},
            'limit_reached': False, 'account_id': 'PRIVATE_TEST_VALUE'},
            'extra': 'PRIVATE_TEST_VALUE'}

    def publish(self, payload=None, hubs=None, pages=None, fail_read=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = {'hubs': [{'number': 1}] if hubs is None else hubs,
                       'pages': [[]] if pages is None else pages, 'fail_read': fail_read}
            (root / 'fixture').write_text(json.dumps(fixture))
            executable = root / 'gh'
            executable.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
root = pathlib.Path(os.environ['GH_FIXTURE'])
fixture = json.loads((root / 'fixture').read_text())
args = sys.argv[1:]
if '--method' in args:
    body = sys.stdin.read()
    (root / 'write').write_text(json.dumps({'args': args, 'payload': json.loads(body)}))
    print('{}')
elif args == ['api', 'user']:
    print('{"login": "meter-user"}')
elif args[:2] == ['issue', 'list']:
    print(json.dumps(fixture['hubs']))
else:
    if fixture['fail_read']:
        sys.exit(1)
    print(json.dumps(fixture['pages']))
''')
            executable.chmod(0o755)
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/publish-meter.py'), '--repo', 'example/project'],
                input=json.dumps(self.payload() if payload is None else payload), text=True,
                capture_output=True, env={**os.environ, 'GH_FIXTURE': str(root),
                                         'PATH': f'{tmp}:{os.environ["PATH"]}'},
            )
            write = json.loads((root / 'write').read_text()) if (root / 'write').exists() else None
            return result, write

    def test_creates_provider_comment_without_extra_private_fields(self):
        result, write = self.publish()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('POST', write['args'])
        self.assertTrue(write['payload']['body'].startswith('autopilot-meter: codex\n'))
        self.assertNotIn('PRIVATE_TEST_VALUE', json.dumps(write))
        self.assertNotIn('PRIVATE_TEST_VALUE', result.stdout + result.stderr)

    def test_updates_own_provider_comment_on_later_page(self):
        def comment(number, author, provider):
            return {'id': number, 'user': {'login': author}, 'body': f'autopilot-meter: {provider}\n{{}}'}
        pages = [[comment(1, 'meter-user', 'claude'), comment(2, 'someone-else', 'codex')],
                 [comment(3, 'meter-user', 'codex')]]
        result, write = self.publish(pages=pages)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PATCH', write['args'])
        self.assertIn('repos/example/project/issues/comments/3', write['args'])

    def test_weekly_only_snapshot_is_never_published(self):
        payload = self.payload()
        del payload['codex']['five_hour']
        result, write = self.publish(payload=payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(write)

    def test_requires_unique_hub(self):
        for hubs in ([], [{'number': 1}, {'number': 2}]):
            with self.subTest(hubs=hubs):
                result, write = self.publish(hubs=hubs)
                self.assertNotEqual(result.returncode, 0)
                self.assertIsNone(write)

    def test_read_failure_never_creates_fallback_comment(self):
        result, write = self.publish(fail_read=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(write)

    def test_invalid_snapshots_are_rejected_without_tracebacks(self):
        for payload in ({}, {'taken_at': None, 'codex': {}},
                        {'taken_at': '2020-01-01T00:00:00Z', 'codex': None}):
            with self.subTest(payload=payload):
                result, write = self.publish(payload=payload)
                self.assertNotEqual(result.returncode, 0)
                self.assertIsNone(write)
                self.assertNotIn('Traceback', result.stderr)
