# Sources

Agent Watch separates primary sources from community signals. Official blogs, papers, and repository metadata are useful evidence. Social and forum traffic can show momentum, but it should not be treated as a factual source by itself.

Each source supports the same reliability options:

```yaml
sources:
  - name: arXiv AI Agents
    type: arxiv
    query: 'cat:cs.AI AND (agent OR agents OR tool)'
    limit: 20
    timeout_seconds: 30
    retries: 2
    retry_backoff_seconds: 2
    continue_on_error: true
```

`timeout_seconds` controls the HTTP timeout for that source. `retries` and `retry_backoff_seconds` retry transient HTTP failures such as timeouts and rate limits. `continue_on_error` defaults to `true`, so a temporary failure in one source does not prevent other sources from being collected. The CLI prints a warning for failed sources and continues with the successful items.

## RSS

RSS is the safest default for official blogs and changelogs. RSS items usually include a title, URL, publication date, and short description. Agent Watch normalizes the URL and strips common tracking parameters before deduplication.

## arXiv

The arXiv adapter queries the public Atom API and is best for early research signals. Use focused queries such as `cat:cs.AI AND (agent OR agents OR tool)` to avoid broad paper dumps.

arXiv can be slow or rate limited from some networks. Prefer focused queries, moderate limits, and retries with backoff for scheduled jobs.

## Semantic Scholar

Semantic Scholar is useful when you want paper metadata and citation context. An API key is optional but recommended for heavier use. Configure it through `SEMANTIC_SCHOLAR_API_KEY`, not inside YAML.

Unauthenticated requests can hit HTTP 429. For recurring jobs, set `SEMANTIC_SCHOLAR_API_KEY` in the runtime environment and keep `continue_on_error: true` so paper metadata issues do not block other sources.

## GitHub

The GitHub adapter uses repository search for open-source momentum. It is useful for finding active frameworks, benchmark tools, and implementation examples. Set `GITHUB_TOKEN` to raise API limits.

## Hacker News

Hacker News is included as a community signal. Agent Watch marks this source type as low confidence because discussion threads can surface interesting projects without verifying their claims.
