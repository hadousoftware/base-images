import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / 'images.json').read_text())['images']

    def test_expected_stack_and_publication_scope(self):
        self.assertEqual([item['name'] for item in self.catalog], ['base', 'python', 'node', 'bun', 'terraform', 'go'])
        self.assertEqual(
            [item['name'] for item in self.catalog if item['publish']],
            ['base', 'python', 'node', 'bun', 'terraform'],
        )
        go = next(item for item in self.catalog if item['name'] == 'go')
        self.assertEqual(go['status'], 'compatibility')

    def test_catalog_loader_and_architecture_matrix(self):
        command = [sys.executable, str(ROOT / 'scripts/catalog.py'), 'matrix', '--architectures']
        matrix = json.loads(subprocess.run(command, check=True, text=True, capture_output=True).stdout)
        self.assertEqual(len(matrix['include']), len(self.catalog) * 2)
        self.assertEqual({row['arch'] for row in matrix['include']}, {'amd64', 'arm64'})
        self.assertEqual({row['runner'] for row in matrix['include']}, {'ubuntu-24.04', 'ubuntu-24.04-arm'})

    def test_maintained_dockerfiles_pin_every_stage(self):
        pattern = re.compile(r'^FROM \S+@sha256:[0-9a-f]{64}(?: AS [A-Za-z0-9_-]+)?$')
        for image in self.catalog:
            text = (ROOT / image['dockerfile']).read_text()
            from_lines = [line for line in text.splitlines() if line.startswith('FROM ')]
            self.assertTrue(from_lines, image['name'])
            for line in from_lines:
                self.assertRegex(line, pattern, image['name'])
            self.assertIn('USER 10001:10001', text, image['name'])
            self.assertNotIn('HEALTHCHECK', text, image['name'])
            self.assertNotRegex(text, r'\b(curl|wget)\b', image['name'])
            self.assertIn('org.opencontainers.image.source=', text, image['name'])

    def test_release_lines_match_current_hadou_constraints(self):
        text = {item['name']: (ROOT / item['dockerfile']).read_text() for item in self.catalog}
        self.assertIn('debian:13-slim@sha256:', text['base'])
        self.assertIn('python:3.12-slim-trixie@sha256:', text['python'])
        self.assertRegex(text['python'], r'uv:0\.13\.\d+@sha256:')
        self.assertIn('node:26-trixie-slim@sha256:', text['node'])
        self.assertRegex(text['bun'], r'bun:1\.4\.\d+-debian@sha256:')
        self.assertRegex(text['terraform'], r'terraform:1\.17\.\d+@sha256:')
        self.assertRegex(text['go'], r'golang:1\.27\.\d+-trixie@sha256:')

    def test_language_toolchains_have_non_root_home(self):
        for image in (item for item in self.catalog if item['name'] != 'base'):
            text = (ROOT / image['dockerfile']).read_text()
            self.assertIn('HOME=/home/hadou', text, image['name'])
            self.assertIn('--create-home --shell /usr/sbin/nologin hadou', text, image['name'])

    def test_legacy_paths_are_not_in_catalog(self):
        paths = {item['dockerfile'] for item in self.catalog}
        for prefix in ('base/abi/', 'core/packer/', 'core/terraform/tfmux/', 'core/zig/'):
            self.assertFalse(any(path.startswith(prefix) for path in paths))


if __name__ == '__main__':
    unittest.main()
