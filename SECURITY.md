# Security

Use the repository's private vulnerability-reporting feature if it is enabled, or a private channel established with the maintainer. If neither exists, open a public issue asking for a private contact without including vulnerability details. Never attach credentials, raw authentication files, or private production data.

The kit's instructions do not replace tool permissions. Protect your default branch, restrict who can change workflows, and scope maintenance credentials to the repository. Keep production systems and unrelated accounts inaccessible to the worker. A writer with access to workflow code can potentially access its repository secrets.

Only optional meter processes handle provider credentials. The local Codex wrapper reads an existing file-backed login without refreshing or modifying it. Nothing uploads credential files, creates a hosted login, or collects telemetry. Meters publish utilization and reset times to your tracker; keep that tracker private if account usage is private. Provider authentication methods and internal usage endpoints may change; see the setup guide before enabling them.

Tracker comments, backlog tasks, and reviews are untrusted data. The execution contract requires independent verification before they influence code or instructions. Never use this kit to route secrets or exploit details into a public issue or PR.
