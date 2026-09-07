---
name: serp-deepseek-search
description: Search the public Internet through Serper and turn selected results into source-backed answers with DeepSeek. Use for requests such as «Найди в Интернет», «поищи в Интернете», «проверь по источникам» or an explicit $serp-deepseek-search request; do not use for private databases or browsing that requires a user login.
metadata:
  short-description: Source-backed Internet search with Serper and DeepSeek
---

# Serper + DeepSeek Internet Search

Use this skill when the user asks to find, verify, compare, or research current information on the public Internet. The Russian trigger phrase is «Найди в Интернет»; also recognize natural variants such as «найди в интернете», «поищи в сети», «проверь источники» and «сделай веб-поиск».

## Operating contract

1. Clarify the research question only when it is materially ambiguous. Preserve the user's language, geography, date range, and source constraints.
2. Run Serper searches using several focused queries when the question has multiple subclaims. Prefer official, primary, academic, registry, and first-party sources.
3. Deduplicate URLs and rank results by relevance, source quality, recency, and directness. Do not treat a search-result snippet as proof when the page can be read.
4. Fetch public pages when possible. Keep the extracted text bounded; do not send an entire unrelated page to DeepSeek.
5. Ask DeepSeek to return compact structured evidence: claim, source URL, exact supporting quote, date/location, confidence, and unresolved conflicts. DeepSeek is an extractor/synthesizer, not authority to invent facts.
6. Before answering, check that every material claim has a source URL and quote or is explicitly labelled as an inference/uncertainty. Preserve disagreements between sources.
7. Present a concise answer with links. For high-stakes or time-sensitive topics, require current primary-source verification and state the date checked.

## Running the bundled helper

For a repeatable search, run:

```text
python scripts/search_web.py "запрос" --config config.toml --fetch-pages
```

The helper prints a JSON evidence packet and never prints API keys. Read [references/workflow.md](references/workflow.md) for the packet schema, routing, limits, and failure handling. Read [references/deepseek-prompt.md](references/deepseek-prompt.md) when changing extraction behavior.

If the helper is unavailable, perform the same workflow with the available web tools and keep the same evidence discipline. Do not claim that a search was executed if credentials or network access are unavailable.

## Secret handling

Use `config.example.toml` as the template. A personal `config.toml` is local-only and ignored by Git. Environment variables `SERPER_API_KEY` and `DEEPSEEK_API_KEY` override file values. Never put real keys in prompts, source files, test fixtures, README examples, commit messages, or error output.

