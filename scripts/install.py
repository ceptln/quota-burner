#!/usr/bin/env python3
"""Install shared maintenance skills without overwriting local files or enabling schedules."""
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def manifest(agent):
    entries = []
    directories = {'claude': ['.claude'], 'codex': ['.agents'], 'both': ['.claude', '.agents']}
    for directory in directories[agent]:
        for source in sorted((ROOT / 'skills').glob('*/SKILL.md')):
            entries.append((source, Path(directory) / 'skills' / source.relative_to(ROOT / 'skills')))
    shared = {
        'skills/autopilot/config.example.yaml': 'config.yaml',
        'templates/context.md': 'context.md',
        'docs/CONTRACT.md': 'CONTRACT.md',
        'docs/SETUP.md': 'SETUP.md',
        'LICENSE': 'LICENSE',
    }
    shared.update({f'templates/{name}': f'templates/{name}' for name in ('hub-issue.md', 'chantier-issue.md')})
    shared.update({f'scripts/{name}': f'scripts/{name}' for name in
                   ('claude-meter.sh', 'codex-meter.sh', 'codex-meter-local.py', 'parse_meter.py', 'publish-meter.py')})
    shared['workflows/autopilot-meter.yml'] = 'workflows/autopilot-meter.yml'
    entries.extend((ROOT / source, Path('.quota-burner') / target) for source, target in shared.items())
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path, help='existing repository directory')
    parser.add_argument('--agent', choices=('claude', 'codex', 'both'), default='both')
    parser.add_argument('--dry-run', action='store_true', help='show the file plan without writing')
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir() or target == ROOT:
        parser.error('choose an existing target directory other than this source checkout')
    planned = []
    conflicts = []
    for source, relative in manifest(args.agent):
        destination = target / relative
        if not source.is_file():
            parser.error(f'incomplete package: {source.relative_to(ROOT)}')
        if any((target / ancestor).is_symlink() for ancestor in (relative, *relative.parents)):
            conflicts.append(f'{relative} (symlink)')
        elif any((target / parent).exists() and not (target / parent).is_dir() for parent in relative.parents):
            conflicts.append(f'{relative} (parent is not a directory)')
        elif destination.exists():
            if not destination.is_file() or destination.read_bytes() != source.read_bytes():
                conflicts.append(str(relative))
        else:
            planned.append((source, destination))
    if conflicts:
        sys.exit('No files written. Merge or relocate conflicting files first:\n' + '\n'.join(conflicts))
    for source, destination in planned:
        print(('Would install ' if args.dry_run else 'Install ') + str(destination.relative_to(target)))
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    print(f'{len(planned)} files {"planned" if args.dry_run else "installed"}. No schedules enabled.')
    print('Next: read .quota-burner/SETUP.md and fill .quota-burner/context.md.')


if __name__ == '__main__':
    main()
