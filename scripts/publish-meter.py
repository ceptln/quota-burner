#!/usr/bin/env python3
"""Publish one provider's normalized snapshot to the configured GitHub hub."""
import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import sys

from parse_meter import number, window


def snapshot(raw):
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get('taken_at'), str):
        raise ValueError('invalid snapshot')
    providers = set(data) & {'claude', 'codex'}
    if len(providers) != 1:
        raise ValueError('supply exactly one provider snapshot')
    provider = providers.pop()
    taken = datetime.fromisoformat(data['taken_at'].replace('Z', '+00:00'))
    if taken.tzinfo is None or taken > datetime.now(timezone.utc):
        raise ValueError('invalid sampling time')
    source = data[provider]
    if not isinstance(source, dict):
        raise ValueError('invalid provider snapshot')
    clean = {}
    for name, duration in (('five_hour', 18000), ('seven_day', 604800)):
        item = source.get(name)
        if item['window_seconds'] != duration:
            raise ValueError('unsupported quota window')
        clean[name] = window(item['utilization'], item['resets_at'], duration)
    if provider == 'claude':
        clean['overage_utilization'] = number(source['overage_utilization'], 0, 1)
    else:
        if not isinstance(source['limit_reached'], bool):
            raise ValueError('missing limit flag')
        clean['limit_reached'] = source['limit_reached']
    return provider, {'taken_at': taken.isoformat(), provider: clean}


def gh(*args, payload=None):
    result = subprocess.run(['gh', *args], input=payload, text=True, capture_output=True)
    if result.returncode:
        raise ValueError('GitHub request failed; check authentication and repository permissions')
    return json.loads(result.stdout) if result.stdout.strip() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='owner/repository')
    parser.add_argument('--author', help='exact publisher login; Actions uses github-actions[bot]')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', args.repo):
        parser.error('expected owner/repository')
    try:
        provider, data = snapshot(sys.stdin.read())
        author = args.author or gh('api', 'user')['login']
        hubs = gh('issue', 'list', '--repo', args.repo, '--label', 'autopilot-hub',
                  '--state', 'open', '--limit', '2', '--json', 'number')
        if len(hubs) != 1:
            raise ValueError('expected exactly one open autopilot-hub issue')
        issue = hubs[0]['number']
        pages = gh('api', f'repos/{args.repo}/issues/{issue}/comments', '--paginate', '--slurp')
        marker = f'autopilot-meter: {provider}'
        matches = [comment for page in pages for comment in page
                   if comment['user']['login'] == author
                   and comment['body'].splitlines()[0:1] == [marker]]
        body = marker + '\n```json\n' + json.dumps(data, indent=2) + '\n```'
        if matches:
            comment = max(matches, key=lambda item: item['id'])
            route = f'repos/{args.repo}/issues/comments/{comment["id"]}'
            method = 'PATCH'
        else:
            route = f'repos/{args.repo}/issues/{issue}/comments'
            method = 'POST'
        gh('api', '--method', method, route, '--input', '-', payload=json.dumps({'body': body}))
    except (ValueError, KeyError, TypeError, OSError):
        sys.exit('publish-meter: failed; check snapshot schema, unique hub, and GitHub access')
    print(f'Published {provider} snapshot to {args.repo} issue {issue}.')


if __name__ == '__main__':
    main()
