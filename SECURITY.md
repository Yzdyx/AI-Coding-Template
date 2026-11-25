# Security Policy

## Supported scope

Security review covers the current `main` branch of this template repository.
Reference providers, sample infrastructure, historical plans, and example
baselines do not establish production security, and no patch-service guarantee
is provided.

## Report a vulnerability

Do not disclose a vulnerability, exploit, credential, or personal data in a
public issue.

1. Open the repository's **Security** tab and choose **Report a vulnerability**
   to use GitHub private vulnerability reporting when it is available.
2. If that route is unavailable, open a public issue containing only a request
   for a private security channel. Do not include details about the affected
   asset or exploitation steps.

Include the affected commit and path, security impact, prerequisites, minimal
reproduction, and any suggested mitigation once a private channel is confirmed.

## Handling expectations

Reports are handled on a best-effort basis. The maintainer will validate scope,
limit access to sensitive material, coordinate a fix and disclosure where
appropriate, and avoid presenting an unverified fix as production-ready.

## Engineering requirements

The detailed security model is in [docs/SECURITY.md](docs/SECURITY.md). In
particular:

- never commit secrets or credentials;
- treat retrieved documents, tool output, and model output as untrusted data;
- fail closed when policy decisions are unavailable;
- require human approval for high-risk and irreversible actions; and
- keep production writes disabled by default.
