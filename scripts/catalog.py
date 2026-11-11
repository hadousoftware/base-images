#!/usr/bin/env python3
"""Read and validate the image catalog without third-party dependencies."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'images.json'
NAME = re.compile(r'^[a-z][a-z0-9-]*$')
FIELDS = {'name', 'dockerfile', 'version_tag', 'profile', 'status', 'publish'}


def load():
    document = json.loads(CATALOG.read_text())
    if document.get('schema_version') != 1 or not isinstance(document.get('images'), list):
        raise ValueError('Unsupported or incomplete image catalog')
    names = set()
    for image in document['images']:
        if set(image) != FIELDS:
            raise ValueError(f'Unexpected catalog fields for {image.get("name", "unknown")}')
        if not NAME.fullmatch(image['name']) or image['name'] in names:
            raise ValueError(f'Invalid or duplicate image name: {image["name"]}')
        names.add(image['name'])
        dockerfile = ROOT / image['dockerfile']
        if not dockerfile.is_file() or ROOT not in dockerfile.resolve().parents:
            raise ValueError(f'Invalid Dockerfile path for {image["name"]}')
        if image['profile'] != 'debian13':
            raise ValueError(f'Unsupported scan profile for {image["name"]}')
        if image['status'] not in {'maintained', 'compatibility'}:
            raise ValueError(f'Unsupported status for {image["name"]}')
        if not isinstance(image['publish'], bool):
            raise ValueError(f'Publish must be boolean for {image["name"]}')
    return document['images']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='command', required=True)
    field_parser = subparsers.add_parser('field')
    field_parser.add_argument('name')
    field_parser.add_argument('field', choices=sorted(FIELDS - {'name'}))
    matrix_parser = subparsers.add_parser('matrix')
    matrix_parser.add_argument('--publish-only', action='store_true')
    matrix_parser.add_argument('--architectures', action='store_true')
    args = parser.parse_args()
    images = load()
    if args.command == 'field':
        image = next((item for item in images if item['name'] == args.name), None)
        if image is None:
            parser.error(f'unknown image: {args.name}')
        value = image[args.field]
        print(str(value).lower() if isinstance(value, bool) else value)
        return 0
    if args.publish_only:
        images = [image for image in images if image['publish']]
    if args.architectures:
        expanded = []
        for image in images:
            for architecture, runner in (('amd64', 'ubuntu-24.04'), ('arm64', 'ubuntu-24.04-arm')):
                expanded.append({**image, 'arch': architecture, 'runner': runner})
        images = expanded
    print(json.dumps({'include': images}, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
