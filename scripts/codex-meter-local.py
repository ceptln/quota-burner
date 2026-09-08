#!/usr/bin/env python3
"""Read a local Codex file-backed login without copying or refreshing its credentials."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--auth-file', type=Path,
                        default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json')
    args = parser.parse_args()
    try:
        tokens = json.loads(args.auth_file.read_text())['tokens']
        access = tokens['access_token']
        account = tokens.get('account_id')
        if not isinstance(access, str) or not access or (account is not None and not isinstance(account, str)):
            raise ValueError('invalid login')
    except (OSError, ValueError, KeyError, TypeError):
        sys.exit('meter: no readable file-backed ChatGPT login; use an authorized meter for your credential store')
    env = {**os.environ, 'CODEX_ACCESS_TOKEN': access, 'CODEX_ACCOUNT_ID': account or ''}
    result = subprocess.run(['bash', str(Path(__file__).with_name('codex-meter.sh'))], env=env)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
