# Workflow and evidence packet

The helper accepts one question and may send several Serper queries. It normalizes result URLs, removes duplicates, optionally fetches public HTML, strips scripts/styles, bounds page text, and sends only the selected source records to DeepSeek. The default output is a JSON object:

```json
{
  "question": "...",
  "searched_at": "UTC ISO-8601",
  "sources": [{"title":"...","url":"...","snippet":"...","text":"..."}],
  "evidence": [{"claim":"...","source_url":"...","quote":"...","confidence":"high|medium|low","notes":"..."}],
  "limitations": []
}
```

The JSON is an intermediate evidence packet, not a final answer. The calling model must cite URLs, separate confirmed facts from inference, and mention missing pages or conflicts. A failed page fetch does not invalidate a search result; it lowers confidence and records the limitation.

Cost controls are deliberate: bounded queries, URL deduplication, source caps, page-character caps, compact JSON, and one synthesis call. For broad research, split the question into focused runs and merge evidence by canonical URL and claim, not by wording alone.

The helper retries transient HTTP failures with short exponential backoff. It redacts configured secret values from errors. It does not bypass paywalls, robots controls, authentication, or access restrictions.

