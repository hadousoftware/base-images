#!/usr/bin/env python3
"""Scan an exact OCI archive or maintained source with pinned Trivy."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OS_PROFILES = {'debian13': ('debian', '13')}
LEGACY_SOURCE_DIRS = ('base/abi', 'core/packer', 'core/terraform/tfmux', 'core/zig')


def evaluate(report, os_required=False, profile='debian13'):
    if not isinstance(report, dict) or report.get('SchemaVersion') != 2:
        raise ValueError('Unrecognized or incomplete scanner report')
    results = report.get('Results')
    if not isinstance(results, list):
        raise ValueError('Missing scanner results; no coverage established')
    if os_required:
        operating_system = report.get('Metadata', {}).get('OS', {})
        family, release = OS_PROFILES[profile]
        actual = str(operating_system.get('Name', ''))
        if operating_system.get('Family') != family or not (actual == release or actual.startswith(release + '.')):
            raise ValueError(f'Expected {family} {release} OS inventory was not detected')
        if operating_system.get('EOSL'):
            raise ValueError('Scanner reports end-of-support operating system')
        if not any(result.get('Class') == 'os-pkgs' and result.get('Packages') for result in results):
            raise ValueError('No OS packages catalogued; refusing an empty scan')
    blockers = []
    for result in results:
        for category in ('Vulnerabilities', 'Secrets', 'Misconfigurations'):
            for finding in result.get(category) or []:
                if category == 'Misconfigurations' and finding.get('Status') == 'PASS':
                    continue
                if category == 'Secrets' or category == 'Misconfigurations' or finding.get('Severity') in ('HIGH', 'CRITICAL', 'UNKNOWN'):
                    blockers.append({
                        'target': result.get('Target'),
                        'category': category,
                        'id': finding.get('VulnerabilityID') or finding.get('ID') or finding.get('RuleID'),
                        'severity': finding.get('Severity'),
                    })
    return blockers


def scanner_reference():
    text = (ROOT / 'tools/Dockerfile').read_text()
    matches = re.findall(r'^FROM (aquasec/trivy:[0-9.]+@sha256:[0-9a-f]{64})$', text, re.M)
    if len(matches) != 1:
        raise ValueError('Scanner must have exactly one version and digest pin')
    return matches[0]


def scan(mode, target, output, profile='debian13'):
    target = Path(target).resolve(strict=True)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    cache = ROOT / '.cache' / 'trivy'
    cache.mkdir(parents=True, exist_ok=True)
    for path in (target, output, cache):
        if ',' in str(path):
            raise ValueError('Docker bind paths must not contain commas')
    if mode == 'image' and not target.is_file():
        raise ValueError('image mode requires a docker-save archive file')
    if mode == 'source' and not target.is_dir():
        raise ValueError('source mode requires a directory')
    reference = scanner_reference()
    command = [
        'docker', 'run', '--rm', '--read-only', '--cap-drop', 'ALL',
        '--security-opt', 'no-new-privileges', '--pids-limit', '256',
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m',
        '--mount', f'type=bind,src={target},dst=/target,readonly',
        '--mount', f'type=bind,src={output},dst=/reports',
        '--mount', f'type=bind,src={cache},dst=/cache',
        reference, '--cache-dir', '/cache',
    ]
    subcommand = 'image' if mode == 'image' else 'fs'
    target_args = ['--input', '/target'] if mode == 'image' else ['/target']
    options = ['--timeout', '15m', '--no-progress', '--ignorefile', '/dev/null']
    if mode == 'source':
        options += ['--scanners', 'misconfig,secret', '--skip-dirs', '/target/.git',
                    '--skip-dirs', '/target/.cache', '--skip-dirs', '/target/out']
        for directory in LEGACY_SOURCE_DIRS:
            options += ['--skip-dirs', f'/target/{directory}']
    else:
        options += ['--scanners', 'vuln', '--list-all-pkgs', '--exit-on-eol', '1']
    for name in ('scan.json', 'gate.json', 'sbom.cdx.json'):
        (output / name).unlink(missing_ok=True)
    report_path = output / 'scan.json'
    subprocess.run(command + [subcommand] + options + ['--format', 'json', '--output', '/reports/scan.json'] + target_args, check=True)
    report = json.loads(report_path.read_text())
    blockers = evaluate(report, os_required=mode == 'image', profile=profile)
    (output / 'gate.json').write_text(json.dumps({
        'scanner': reference,
        'mode': mode,
        'blockers': blockers,
        'os_profile': profile if mode == 'image' else None,
        'legacy_source_exclusions': list(LEGACY_SOURCE_DIRS) if mode == 'source' else [],
        'policy': 'Fail HIGH, CRITICAL, UNKNOWN vulnerabilities; all secrets and misconfigurations; no unfixed suppression',
    }, indent=2) + '\n')
    if mode == 'image':
        sbom_options = [option for option in options if option != '--list-all-pkgs']
        subprocess.run(command + [subcommand] + sbom_options + ['--format', 'cyclonedx', '--output', '/reports/sbom.cdx.json'] + target_args, check=True)
    if blockers:
        print(f'Security gate failed: {len(blockers)} blocking findings; see {report_path}', file=sys.stderr)
        return 1
    print(f'Security gate passed for {mode}; coverage and timestamp are in {report_path}')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['image', 'source'])
    parser.add_argument('target')
    parser.add_argument('--output', required=True)
    parser.add_argument('--profile', choices=OS_PROFILES, default='debian13')
    args = parser.parse_args()
    try:
        return scan(args.mode, args.target, args.output, args.profile)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'Scan incomplete: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
