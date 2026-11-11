# Hadou base images

Maintained, multi-architecture OCI foundations for the runtimes used by Hadou
services. Images are built for `linux/amd64` and `linux/arm64`, run as
`10001:10001`, and are published only after restricted-runtime checks and an
OS-package vulnerability gate pass.

This repository follows the container controls used by
[`hadousoftware/linux-foundry`](https://github.com/hadousoftware/linux-foundry):
immutable upstream digests, current signed package updates, non-root execution,
no SSH server or `sudo`, removal of setuid/setgid bits, exact-image scanning,
CycloneDX SBOM generation, least-privilege GitHub Actions, and gated manual
publishing. An image passing today is not a guarantee that it is secure or
uncompromised; downstream applications and their dependencies require their own
build, runtime, and vulnerability controls.

## Maintained catalog

| Image | Release line | Purpose | Published |
| --- | --- | --- | --- |
| `base` | Debian 13 | Minimal application runtime | yes |
| `python` | Python 3.12 + uv 0.13 | FastAPI and Python services currently pinned to 3.12 | yes |
| `node` | Node.js 26 LTS | Astro/Vite builds and Node-compatible tooling | yes |
| `bun` | Bun 1.4 | Elysia and Bun services | yes |
| `terraform` | Terraform 1.17 | Infrastructure plans, tests, and controlled applies | yes |
| `go` | Go 1.27 | Compatibility-only builder; no current Hadou Go modules | no |

The exact build contract is machine-readable in [`images.json`](images.json).
Use immutable GHCR digests downstream. Version tags are convenience pointers and
can move after a newly scanned build.

```text
ghcr.io/hadousoftware/base-images/base:debian13
ghcr.io/hadousoftware/base-images/python:python3.12
ghcr.io/hadousoftware/base-images/node:node26
ghcr.io/hadousoftware/base-images/bun:bun1.4
ghcr.io/hadousoftware/base-images/terraform:terraform1.17
```

The Python 3.12 line is intentional: current Hadou services constrain Python to
3.12, even though newer Python releases exist. Upgrade and test those services
before changing the shared runtime line.
Dependabot keeps Python below 3.13; review migrations alongside service constraints,
catalog tags, and labels. Digest and supported patch updates remain enabled.

## Local checks

Requires Docker, Python 3.10+, `make`, and `jq`. Checks do not start application
services or access host credentials.

```sh
make test
make image IMAGE_NAME=python
make smoke IMAGE_NAME=python
make scan IMAGE_NAME=python
```

The smoke test uses a read-only filesystem, no network, no Linux capabilities,
`no-new-privileges`, bounded memory/PIDs, and an isolated temporary filesystem.
The scan saves the exact image archive first; HIGH, CRITICAL, UNKNOWN, EOL, and
scanner-coverage failures block publication. Reports can contain package
inventory and should be kept private when generated from internal derivatives.

The source scan accepts only LOW `DS-0026` (missing health check) findings for
the six catalog Dockerfiles and two tool locks listed in `scripts/scan.py`.
These base and CLI images have no running service. Applications must supply
their own meaningful health checks. Every accepted finding and its rationale
is recorded in `gate.json`; raw scan findings remain available. Other
misconfigurations and all secrets continue to block.

## Legacy definitions

`base/abi`, `core/packer`, `core/terraform/tfmux`, and `core/zig` are historical and
are not built, scanned, supported, or published. They remain only to avoid a
destructive migration without downstream-owner confirmation. Do not use their
floating tags or download-at-build patterns as examples. Go is retained in the
CI catalog as an optional compatibility image but is not published.

## Publication and ownership

Pull requests and pushes run policy tests and native amd64/arm64 builds. A
manual workflow on `trunk` reruns validation, publishes the exact scanned OCI
archives to GHCR, creates multi-platform indexes, and attaches provenance and
SBOM attestations. The `release` environment should require human approval.

See [SECURITY.md](SECURITY.md) for private reporting and support boundaries.
