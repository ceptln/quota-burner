import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MeterTests(unittest.TestCase):
    def run_meter(self, provider, payload, status='200'):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'response').write_text(payload)
            curl = root / 'curl'
            curl.write_text('''#!/usr/bin/env python3
import os, pathlib, sys
args = sys.argv[1:]
response = pathlib.Path(os.environ['FIXTURE']).read_text()
if '-D' in args:
    target = args[args.index('-D') + 1]
    if target == '-':
        print(response)
    else:
        pathlib.Path(target).write_text(response)
else:
    print(response)
if '-w' in args:
    print(os.environ['HTTP_STATUS'], end='')
''')
            curl.chmod(0o755)
            return subprocess.run(
                ['bash', str(ROOT / 'scripts' / f'{provider}-meter.sh')],
                env={**os.environ, 'PATH': f'{tmp}:{os.environ["PATH"]}',
                     'FIXTURE': str(root / 'response'), 'HTTP_STATUS': status,
                     'CLAUDE_AUTOPILOT_TOKEN': 'test-only', 'CODEX_ACCESS_TOKEN': 'test-only'},
                capture_output=True, text=True,
            )

    def codex_payload(self):
        return json.dumps({'rate_limit': {'limit_reached': False,
            'primary_window': {'used_percent': 12, 'limit_window_seconds': 18000, 'reset_at': 2100000000},
            'secondary_window': {'used_percent': 40, 'limit_window_seconds': 604800, 'reset_at': 2100500000}}})

    def claude_headers(self, utilization='0.2'):
        return ('HTTP/1.1 200 Connection established\r\n\r\nHTTP/2 200\r\n'
                f'Anthropic-Ratelimit-Unified-5h-Utilization: {utilization}\r\n'
                'anthropic-ratelimit-unified-5h-reset: 2100000000\r\n'
                'anthropic-ratelimit-unified-7d-utilization: 0.4\r\n'
                'anthropic-ratelimit-unified-7d-reset: 2100500000\r\n\r\n')

    def test_codex_maps_windows_by_duration(self):
        result = self.run_meter('codex', self.codex_payload())
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)['codex']
        self.assertEqual(data['five_hour']['utilization'], 0.12)
        self.assertEqual(data['seven_day']['utilization'], 0.4)

    def test_codex_rejects_out_of_range_utilization(self):
        result = self.run_meter('codex', self.codex_payload().replace('"used_percent": 12', '"used_percent": 120'))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_claude_rejects_malformed_number(self):
        result = self.run_meter('claude', self.claude_headers('0.2.3'))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_claude_rejects_final_http_failure_behind_proxy(self):
        result = self.run_meter('claude', self.claude_headers().replace('HTTP/2 200', 'HTTP/2 401'), '401')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')


class NormalizationTests(unittest.TestCase):
    def parse(self, provider, payload):
        return subprocess.run(
            ['python3', str(ROOT / 'scripts/parse_meter.py'), provider],
            input=payload, capture_output=True, text=True,
        )

    def test_codex_rejects_weekly_only_snapshot(self):
        data = json.loads(MeterTests().codex_payload())
        del data['rate_limit']['primary_window']
        result = self.parse('codex', json.dumps(data))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_codex_accepts_reversed_window_order(self):
        data = json.loads(MeterTests().codex_payload())
        limits = data['rate_limit']
        limits['primary_window'], limits['secondary_window'] = limits['secondary_window'], limits['primary_window']
        result = self.parse('codex', json.dumps(data))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['codex']['seven_day']['utilization'], 0.4)

    def test_codex_rejects_unknown_duration_missing_week_or_invalid_types(self):
        original = MeterTests().codex_payload()
        cases = [original.replace('604800', '86400'),
                 original.replace('604800', '18000'),
                 original.replace('"used_percent": 12', '"used_percent": true'),
                 original.replace('"used_percent": 12', '"used_percent": NaN'),
                 original.replace('"reset_at": 2100000000', '"reset_at": 1.5'),
                 '{"rate_limit": null}']
        for raw in cases:
            with self.subTest(raw=raw):
                result = self.parse('codex', raw)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
                self.assertNotIn('Traceback', result.stderr)

    def test_claude_handles_header_case_whitespace_and_absent_overage(self):
        raw = MeterTests().claude_headers().replace('0.2', '\t0.2\t ')
        result = self.parse('claude', raw)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)['claude']
        self.assertEqual(data['five_hour']['utilization'], 0.2)
        self.assertEqual(data['overage_utilization'], 0)

    def test_claude_does_not_reuse_headers_from_proxy_block(self):
        raw = MeterTests().claude_headers() + 'HTTP/2 200\r\n\r\n'
        result = self.parse('claude', raw)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
