# DeepSeek extraction contract

The model receives a bounded source set and must return JSON only. It may quote only text present in a source record. It must not infer a person's identity from a matching name alone, merge conflicting dates, or create URLs. When evidence is absent, it returns an empty evidence list and explains the gap in `limitations`.

Use the model for extraction, ranking, and compact conflict notes. Keep final source criticism and high-stakes conclusions with the supervising model/user.

