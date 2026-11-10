# Local Development

Bring up a local environment, run one agent, and inspect its state.

## Prerequisites

| Tool | Version | Used for |
| --- | --- | --- |
| Node | 22 or newer | `apps/`, `packages/` |
| pnpm | 9 or newer | Workspace install |
| Python | 3.12 or newer | `agents/`, `scripts/` |
| Terraform | 1.6 or newer | `infra/`, local only |

## Local stack

[`docker-compose.yml`](docker-compose.yml) brings up a disposable stack:

| Service | Port | Purpose |
| --- | --- | --- |
| `postgres` | 5432 | State store |
| `redis` | 6379 | Queue backend |
| `otel-collector` | 4317, 4318 | Trace and metric collector, prints what it receives |
| `agent-api` | 8080 | Runtime HTTP surface |
| `worker` | — | Task loop |

```bash
docker compose -f tooling/local-dev/docker-compose.yml up -d
docker compose -f tooling/local-dev/docker-compose.yml down -v
```

The compose file holds local development values only. It never holds a
production credential.

## Steps

```bash
pnpm install
python scripts/check-architecture.py
python scripts/check-agent-manifests.py
python scripts/check-doc-links.py
```

## Run one agent offline

The agents are dependency-injected, so they run without a network and without a
model service. A test double supplies the model.

```bash
python -m unittest discover -s agents/research-agent/tests -t agents/research-agent -p "test_*.py"
```

## Environment variables

| Variable | Used by | Required |
| --- | --- | --- |
| `AGENT_TENANT` | Every agent and the state store | Yes |
| `AGENT_STATE_STORE_URL` | `apps/agent-api`, `apps/worker` | Yes |
| `AGENT_MODEL_PROVIDER_URL` | `apps/agent-api` | Yes |
| `AGENT_API_PORT` | `apps/agent-api` | No, defaults to 8080 |

Never put a real value in a file in this repository. Export it in your shell, or
read it from the secret manager.

## Rules

1. Local development uses no production data and no production credential.
2. A local change is verified with the same three checks CI runs.
3. Remove every temporary file before you finish. Do not leave a scratch script in the repository.
