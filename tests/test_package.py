import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_menu_resolves_to_skills(self):
        config = (ROOT / 'skills/autopilot/config.example.yaml').read_text()
        menu = re.findall(r'name: ([a-z0-9-]+), enabled:', config)
        names = {path.parent.name for path in (ROOT / 'skills').glob('*/SKILL.md')}
        self.assertEqual(set(menu), names - {'autopilot', 'autopilot-retro', 'todo'})
        self.assertEqual(len(menu), len(set(menu)))

    def test_skills_have_portable_frontmatter_and_shared_contract(self):
        for path in (ROOT / 'skills').glob('*/SKILL.md'):
            with self.subTest(skill=path.parent.name):
                _, front, body = path.read_text().split('---', 2)
                fields = dict(line.split(': ', 1) for line in front.strip().splitlines())
                self.assertEqual(json.loads(fields['name']), path.parent.name)
                self.assertTrue(json.loads(fields['description']))
                self.assertIn('.quota-burner/CONTRACT.md', body)

    def test_document_links_resolve(self):
        paths = list(ROOT.glob('*.md')) + list((ROOT / 'docs').glob('*.md'))
        for path in paths:
            for raw in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                target = raw.split('#', 1)[0]
                if target and '://' not in target:
                    with self.subTest(path=path.name, target=target):
                        self.assertTrue((path.parent / target).exists())
