import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_meter', ROOT / 'scripts/codex-meter-local.py')
local_meter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local_meter)


class LocalMeterTests(unittest.TestCase):
    def test_local_login_is_read_without_modification_or_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / 'login.json'
            original = json.dumps({'tokens': {'access_token': 'test-access',
                                              'account_id': 'test-account',
                                              'refresh_token': 'test-refresh'}})
            auth.write_text(original)
            with patch('sys.argv', ['meter', '--auth-file', str(auth)]), \
                    patch.object(local_meter.subprocess, 'run') as run:
                run.return_value.returncode = 0
                with self.assertRaises(SystemExit) as result:
                    local_meter.main()
                self.assertEqual(result.exception.code, 0)
                env = run.call_args.kwargs['env']
                self.assertEqual(env['CODEX_ACCESS_TOKEN'], 'test-access')
                self.assertEqual(env['CODEX_ACCOUNT_ID'], 'test-account')
                self.assertNotIn('test-refresh', env.values())
            self.assertEqual(auth.read_text(), original)

    def test_missing_login_never_invokes_collector(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('sys.argv', ['meter', '--auth-file', str(Path(tmp) / 'missing')]), \
                    patch.object(local_meter.subprocess, 'run') as run:
                with self.assertRaises(SystemExit):
                    local_meter.main()
                run.assert_not_called()
