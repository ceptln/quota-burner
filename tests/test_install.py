from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def install(self, target, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'),
                               str(target), *args], capture_output=True, text=True)

    def test_both_agents_receive_identical_skills_and_one_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.install(root, '--agent', 'both')
            self.assertEqual(result.returncode, 0, result.stderr)
            for source in (ROOT / 'skills').glob('*/SKILL.md'):
                relative = source.relative_to(ROOT / 'skills')
                for directory in ('.claude', '.agents'):
                    self.assertEqual((root / directory / 'skills' / relative).read_bytes(), source.read_bytes())
            self.assertEqual(len(list(root.rglob('config.yaml'))), 1)
            self.assertFalse((root / '.github').exists())

    def test_conflict_aborts_before_any_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            conflict = root / '.claude/skills/todo/SKILL.md'
            conflict.parent.mkdir(parents=True)
            conflict.write_text('my existing skill')
            result = self.install(root, '--agent', 'both')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(conflict.read_text(), 'my existing skill')
            self.assertFalse((root / '.quota-burner').exists())
            self.assertFalse((root / '.agents').exists())

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.install(root, '--agent', 'codex', '--dry-run')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(root.iterdir()), [])

    def test_repeat_install_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for _ in range(2):
                result = self.install(root, '--agent', 'claude')
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((root / '.agents').exists())

    def test_symlink_destination_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            (root / '.agents').symlink_to(outside, target_is_directory=True)
            result = self.install(root, '--agent', 'codex')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / '.quota-burner').exists())
            self.assertEqual(list(Path(outside).iterdir()), [])
