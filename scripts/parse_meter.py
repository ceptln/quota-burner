#!/usr/bin/env python3
"""Normalize provider responses. Only normalized quota fields reach stdout."""
import json
import math
import re
import sys
from datetime import datetime, timezone


def number(value, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('expected a number')
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError('number outside expected range')
    return value


def window(used, reset, duration):
    number(reset, 1, 253402300799)
    if int(reset) != reset:
        raise ValueError('reset must be an integer epoch')
    return {'utilization': number(used, 0, 1), 'resets_at': reset, 'window_seconds': duration}


def claude(raw):
    headers = {}
    for line in raw.splitlines():
        if line.startswith('HTTP/'):
            headers = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            headers[key.lower()] = value.strip()

    def numeric(suffix, default=None):
        value = headers.get('anthropic-ratelimit-unified-' + suffix, default)
        if value is None or not re.fullmatch(r'\d+(?:\.\d+)?', value):
            raise ValueError('invalid or missing rate-limit header')
        return float(value) if '.' in value else int(value)

    return {
        'five_hour': window(numeric('5h-utilization'), numeric('5h-reset'), 18000),
        'seven_day': window(numeric('7d-utilization'), numeric('7d-reset'), 604800),
        'overage_utilization': number(numeric('overage-utilization', '0'), 0, 1),
    }


def codex(raw):
    limits = json.loads(raw)['rate_limit']
    if not isinstance(limits, dict) or not isinstance(limits.get('limit_reached'), bool):
        raise ValueError('missing limit_reached flag')
    result = {'limit_reached': limits['limit_reached']}
    names = {18000: 'five_hour', 604800: 'seven_day'}
    for key in ('primary_window', 'secondary_window'):
        source = limits.get(key)
        if source is None:
            continue
        duration = source['limit_window_seconds']
        number(duration, 1, 604800)
        if duration not in names or names[duration] in result:
            raise ValueError('unsupported or duplicate quota window')
        result[names[duration]] = window(
            number(source['used_percent'], 0, 100) / 100,
            source['reset_at'], duration,
        )
    if not all(name in result for name in names.values()):
        raise ValueError('both five-hour and weekly quota windows are required')
    return result


def main():
    provider = sys.argv[1]
    try:
        data = {'claude': claude, 'codex': codex}[provider](sys.stdin.read())
    except (ValueError, KeyError, TypeError, OverflowError):
        sys.exit('meter: unsupported or invalid usage response; no snapshot published')
    print(json.dumps({'taken_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), provider: data}))


if __name__ == '__main__':
    main()
