# Roadmap

Agent Watch is focused on one job: help maintainers keep a traceable monthly view of AI agent ecosystem changes without turning the project into another noisy feed reader.

## Near Term

- Publish the first public GitHub release and keep CI green on Windows and Ubuntu.
- Add richer source adapter fixtures so RSS, arXiv, Semantic Scholar, GitHub, and Hacker News behavior can be regression-tested without live network calls.
- Improve report quality checks so summaries must preserve evidence URLs, confidence, source type, and publication dates.
- Add a maintainer-facing `agent-watch doctor` command that validates configuration, environment variables, source reachability, and output paths.

## Medium Term

- Add a quality evaluation fixture set for summary usefulness, category assignment, and source traceability.
- Support optional GitHub issue or PR summaries so maintainers can connect ecosystem tracking to project planning.
- Add release workflow helpers that can compare the latest monthly report against the current changelog and roadmap.
- Improve template customization while keeping Markdown output stable for Obsidian and plain Markdown users.

## Long Term

- Support additional agent ecosystem sources such as package registries, release feeds, and benchmark leaderboards.
- Build a small maintainer automation workflow that can run on GitHub Actions, open a draft monthly report PR, and attach source traceability metadata.
- Explore LLM-assisted review loops for source adapter changes, release validation, and documentation updates.
