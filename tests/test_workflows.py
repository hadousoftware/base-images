from pathlib import Path
import re
import unittest

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_external_actions_are_full_commit_pins(self):
        for path in (ROOT / '.github/workflows').glob('*.yaml'):
            text = path.read_text()
            self.assertNotIn('pull_request_target', text)
            self.assertNotIn('self-hosted', text)
            for action in re.findall(r'uses:\s*(\S+)', text):
                if action.startswith('./'):
                    continue
                self.assertRegex(action, r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}$')

    @unittest.skipIf(yaml is None, 'Install python3-yaml for workflow structure checks (required in CI)')
    def test_workflow_security_boundaries(self):
        for path in (ROOT / '.github/workflows').glob('*.yaml'):
            document = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
            self.assertEqual(document['permissions'], {'contents': 'read'})
            for job in document['jobs'].values():
                if 'steps' not in job:
                    continue
                self.assertIn('timeout-minutes', job)
                for step in job['steps']:
                    if step.get('uses', '').startswith('actions/checkout@'):
                        self.assertEqual(step['with']['persist-credentials'], 'false')
                if job.get('permissions', {}).get('packages') == 'write':
                    self.assertIn("github.ref == 'refs/heads/trunk'", job['if'])
                    self.assertEqual(job['environment'], 'release')
                    self.assertIn('needs', job)

    def test_release_uses_exact_scanned_archives(self):
        text = (ROOT / '.github/workflows/publish.yaml').read_text()
        self.assertIn('image.tar.sha256', text)
        self.assertIn('docker load -i', text)
        self.assertIn('attest-build-provenance', text)
        self.assertNotIn('docker build ', text)


if __name__ == '__main__':
    unittest.main()
