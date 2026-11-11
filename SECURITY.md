# Security policy

This repository provides reviewed defaults and validation evidence, not a
guarantee that an image or downstream workload is secure or uncompromised.

Use GitHub private vulnerability reporting on the upstream repository's
**Security → Report a vulnerability** page for sensitive findings. If that is
unavailable, open a minimal issue requesting a private channel. Do not include
credentials, exploit details, private registry names, host inventories, or
internal URLs in public reports.

The maintained support boundary is the image catalog in `images.json`, on
linux/amd64 and linux/arm64. Historical definitions listed in the README are
not supported or published. Host kernels, container runtimes, application code,
application dependencies, deployment configuration, and registry policy remain
downstream responsibilities.

HIGH, CRITICAL, UNKNOWN, end-of-life, missing inventory, and scanner failures
block image publication. This is a policy gate, not an independent audit or a
claim of compliance. Configure scheduled-workflow notifications and a release
environment reviewer before relying on the published tags.
