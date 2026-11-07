#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

REPOSITORY = 'kzzzld/hckr'
VERSION = r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)'


def version_tuple(tag):
    if not re.fullmatch(VERSION, tag):
        raise ValueError(f'Unsupported stable release tag: {tag}')
    return tuple(map(int, tag[1:].split('.')))


def formula_version(text):
    match = re.search(r'^  url "https://github.com/kzzzld/hckr/releases/download/([^/]+)/', text, re.M)
    if match:
        version_tuple(match[1])
        return match[1]
    if re.search(r'^  (url|sha256) ', text, re.M):
        raise ValueError('Unrecognized stable formula source; refusing to replace it')
    return None


def update_formula(text, tag, checksum):
    version_tuple(tag)
    if not re.fullmatch(r'[0-9a-f]{64}', checksum):
        raise ValueError('Invalid SHA-256 checksum')
    current = formula_version(text)
    if current and version_tuple(current) > version_tuple(tag):
        raise ValueError('Refusing to downgrade the formula')
    if current == tag:
        if f'  sha256 "{checksum}"' not in text:
            raise ValueError('Published release checksum changed')
        return text
    stable = (f'  url "https://github.com/{REPOSITORY}/releases/download/{tag}/hckr-{tag[1:]}.tar.gz"\n'
              f'  sha256 "{checksum}"\n')
    text = re.sub(r'^  (url|sha256) [^\n]*\n', '', text, flags=re.M)
    marker = f'  head "https://github.com/{REPOSITORY}.git", branch: "main"\n'
    if text.count(marker) != 1:
        raise ValueError('Cannot find the development source in the formula')
    return text.replace(marker, stable + marker)


def verify_archive(archive, manifest):
    entries = [line.split() for line in manifest.splitlines() if line.strip()]
    matches = [parts[0] for parts in entries if len(parts) == 2 and parts[1] == archive.name]
    if len(matches) != 1:
        raise ValueError('Release manifest must contain exactly one matching archive')
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    if matches[0] != checksum:
        raise ValueError('Release archive does not match SHA256SUMS')
    return checksum


def main():
    result = subprocess.run(['gh', 'api', f'repos/{REPOSITORY}/releases/latest'],
                            text=True, capture_output=True)
    if result.returncode:
        if 'HTTP 404' in result.stderr:
            print('No stable release published yet')
            return
        raise RuntimeError(result.stderr.strip())
    latest = json.loads(result.stdout)
    if latest['draft'] or latest['prerelease']:
        raise ValueError('Expected a published stable release')
    tag = latest['tag_name']
    version_tuple(tag)
    formula = Path('Formula/hckr.rb')
    text = formula.read_text()
    current = formula_version(text)
    if current and version_tuple(current) >= version_tuple(tag):
        print(f'Formula is already at {current}')
        return
    with tempfile.TemporaryDirectory() as directory:
        archive = Path(directory) / f'hckr-{tag[1:]}.tar.gz'
        subprocess.run(['gh', 'release', 'download', tag, '--repo', REPOSITORY,
                        '--pattern', archive.name, '--pattern', 'SHA256SUMS',
                        '--dir', directory], check=True)
        checksum = verify_archive(archive, (Path(directory) / 'SHA256SUMS').read_text())
    formula.write_text(update_formula(text, tag, checksum))
    print(f'Updated hckr to {tag}')


if __name__ == '__main__':
    main()
