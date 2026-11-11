import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('scan', Path(__file__).resolve().parents[1] / 'scripts/scan.py')
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


def report(findings=None):
    return {
        'SchemaVersion': 2,
        'Metadata': {'OS': {'Family': 'debian', 'Name': '13'}},
        'Results': [{
            'Class': 'os-pkgs',
            'Packages': [{'Name': 'libc6'}],
            'Vulnerabilities': findings or [],
        }],
    }


class ScanTests(unittest.TestCase):
    def test_clean_inventory(self):
        self.assertEqual(scan.evaluate(report(), True), [])

    def test_unfixed_high_and_unknown_are_blocked(self):
        for severity in ('HIGH', 'CRITICAL', 'UNKNOWN'):
            findings = [{'Severity': severity, 'FixedVersion': ''}]
            self.assertEqual(len(scan.evaluate(report(findings), True)), 1)

    def test_low_vulnerability_does_not_block(self):
        self.assertEqual(scan.evaluate(report([{'Severity': 'LOW'}]), True), [])

    def test_missing_inventory_is_unknown(self):
        bad_reports = ({}, {'SchemaVersion': 2}, {'SchemaVersion': 2, 'Results': []})
        for item in bad_reports:
            with self.assertRaises(ValueError):
                scan.evaluate(item, True)

    def test_wrong_or_eol_os_fails(self):
        for system in (
            {'Family': 'debian', 'Name': '12'},
            {'Family': 'ubuntu', 'Name': '24.04'},
            {'Family': 'debian', 'Name': '13', 'EOSL': True},
        ):
            item = report()
            item['Metadata']['OS'] = system
            with self.assertRaises(ValueError):
                scan.evaluate(item, True)

    def test_secrets_and_misconfigurations_always_block(self):
        for category, finding in (
            ('Secrets', {'Severity': 'LOW', 'RuleID': 'key'}),
            ('Misconfigurations', {'Severity': 'LOW', 'ID': 'config', 'Status': 'FAIL'}),
        ):
            item = {'SchemaVersion': 2, 'Results': [{category: [finding]}]}
            self.assertEqual(len(scan.evaluate(item)), 1)

    def test_scanner_and_legacy_scope_are_explicit(self):
        self.assertIn('@sha256:', scan.scanner_reference())
        self.assertEqual(
            scan.LEGACY_SOURCE_DIRS,
            ('base/abi', 'core/packer', 'core/terraform/tfmux', 'core/zig'),
        )
        readme = (scan.ROOT / 'README.md').read_text()
        for directory in scan.LEGACY_SOURCE_DIRS:
            self.assertIn(directory, readme)

    def test_healthcheck_exception_is_source_only_and_auditable(self):
        item = {'SchemaVersion': 2, 'Results': [{
            'Type': 'dockerfile', 'Target': 'core/node/Dockerfile',
            'Misconfigurations': [{'ID': 'DS-0026', 'Severity': 'LOW', 'Status': 'FAIL'}],
        }]}
        self.assertEqual(len(scan.evaluate(item)), 1)
        exceptions = []
        self.assertEqual(scan.evaluate(item, source_policy=True, exceptions=exceptions), [])
        self.assertEqual(exceptions, [{'target': 'core/node/Dockerfile', 'id': 'DS-0026',
                                       'reason': scan.HEALTHCHECK_REASON}])
        for field, value in [('Target', 'app/Dockerfile'), ('Type', 'terraform')]:
            changed = {**item, 'Results': [{**item['Results'][0], field: value}]}
            self.assertEqual(len(scan.evaluate(changed, source_policy=True)), 1)
        for field, value in [('ID', 'DS-0002'), ('Severity', 'HIGH')]:
            result = item['Results'][0]
            changed = {**item, 'Results': [{**result, 'Misconfigurations': [
                {**result['Misconfigurations'][0], field: value}]}]}
            self.assertEqual(len(scan.evaluate(changed, source_policy=True)), 1)


if __name__ == '__main__':
    unittest.main()
