# Contributing

Keep changes bounded to the catalog and avoid embedding credentials, internal
URLs, machine inventories, or private package names. Never add browser data,
shell history, process environments, private keys, or host-assessment evidence.

For a maintained image change:

1. Update the pinned tag and multi-platform digest in its Dockerfile.
2. Keep the image on Debian 13, UID/GID 10001, and the restricted runtime model.
3. Update `images.json`, documentation, and policy tests together when a release
   line or publication decision changes.
4. Run `make test`, then build, smoke-test, and scan the affected image.
5. Review the package inventory, CVE report, and SBOM as private build evidence.

Do not add automatic merging for base-image, scanner, or workflow-action
updates. A green dependency PR still needs review of upstream release notes,
architecture coverage, scanner results, and rollback impact.

Legacy paths are retained pending downstream-owner confirmation. Removing or
reviving them requires an explicit migration decision and updated validation.
