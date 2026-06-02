# Sources

Agent Watch separates primary sources from community signals. Official blogs, papers, and repository metadata are useful evidence. Social and forum traffic can show momentum, but it should not be treated as a factual source by itself.

## RSS

RSS is the safest default for official blogs and changelogs. RSS items usually include a title, URL, publication date, and short description. Agent Watch normalizes the URL and strips common tracking parameters before deduplication.

## arXiv

The arXiv adapter queries the public Atom API and is best for early research signals. Use focused queries such as `cat:cs.AI AND (agent OR agents OR tool)` to avoid broad paper dumps.

## Semantic Scholar

Semantic Scholar is useful when you want paper metadata and citation context. An API key is optional but recommended for heavier use. Configure it through `SEMANTIC_SCHOLAR_API_KEY`, not inside YAML.

## GitHub

The GitHub adapter uses repository search for open-source momentum. It is useful for finding active frameworks, benchmark tools, and implementation examples. Set `GITHUB_TOKEN` to raise API limits.

## Hacker News

Hacker News is included as a community signal. Agent Watch marks this source type as low confidence because discussion threads can surface interesting projects without verifying their claims.

