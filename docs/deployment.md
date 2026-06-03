# Deployment

Agent Watch can run directly on a host with cron or inside Docker. Docker is the safer default for long-running deployments because Python dependencies, local state, logs, and future services can stay isolated from the host.

## Docker

Build the image from the repository root:

```bash
docker build -t agent-watch:local .
```

Create a runtime directory outside the repository. Keep generated reports, logs, SQLite state, and secrets there so they are not committed to git:

```bash
mkdir -p /opt/agent-watch/{notes,data,logs}
cp agent-watch.yaml /opt/agent-watch/agent-watch.yaml
touch /opt/agent-watch/.env
chmod 600 /opt/agent-watch/.env
```

When a config is used inside Docker, paths must be container paths. The host directory is mounted at `/runtime`, so use `/runtime/notes` and `/runtime/data/state.sqlite` instead of host paths such as `/opt/agent-watch/notes`.

```yaml
sinks:
  default:
    type: markdown
    output_dir: /runtime/notes
state:
  path: /runtime/data/state.sqlite
```

Run a no-write smoke test first:

```bash
docker run --rm \
  --env-file /opt/agent-watch/.env \
  -v /opt/agent-watch:/runtime \
  agent-watch:local update --config /runtime/agent-watch.yaml --dry-run
```

After the dry run succeeds, run a real update:

```bash
docker run --rm \
  --env-file /opt/agent-watch/.env \
  -v /opt/agent-watch:/runtime \
  agent-watch:local update --config /runtime/agent-watch.yaml
```

## Cron With Docker

For long-running cron jobs, wrap Docker with a small script so paths, environment variables, logs, and locking stay explicit:

```bash
#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR=/opt/agent-watch
LOCK_FILE="$RUNTIME_DIR/agent-watch.lock"

{
  echo "===== $(date -Is) agent-watch start ====="
  flock -n 9 || { echo "$(date -Is) another run is already active"; exit 75; }
  docker run --rm \
    --env-file "$RUNTIME_DIR/.env" \
    -v "$RUNTIME_DIR:/runtime" \
    agent-watch:local update --config /runtime/agent-watch.yaml --dry-run
  echo "===== $(date -Is) agent-watch success ====="
} 9>"$LOCK_FILE"
```

Install the dry-run schedule first and observe several successful runs before enabling writes:

```cron
*/10 * * * * /opt/agent-watch/run-agent-watch.sh >> /opt/agent-watch/logs/cron.log 2>&1
```

Once the schedule is stable, remove `--dry-run` from the wrapper and move the cadence to the intended production interval, such as weekly:

```cron
0 8 * * 1 /opt/agent-watch/run-agent-watch.sh >> /opt/agent-watch/logs/cron.log 2>&1
```

If you use Docker Compose for the wrapper, pass `--interactive=false` to `docker compose run`. Compose keeps stdin open by default, which can consume piped shell scripts or behave poorly in non-interactive cron environments.

## Operational Notes

Source adapters continue after per-source HTTP failures by default, so a temporary arXiv timeout or Semantic Scholar rate limit does not block RSS, GitHub, or Hacker News results. Configure tokens such as `GITHUB_TOKEN` and `SEMANTIC_SCHOLAR_API_KEY` in the runtime `.env` file rather than in YAML.

Check the deployment with:

```bash
agent-watch doctor --config /opt/agent-watch/agent-watch.yaml
grep -c "agent-watch success" /opt/agent-watch/logs/cron.log
tail -120 /opt/agent-watch/logs/cron.log
```
