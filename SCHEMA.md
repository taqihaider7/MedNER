# MedSETNER schema and data dictionary

This document defines every field in every file in `data/`, and shows
how to convert between the two on-disk formats.

## 1. `data/{train,val,test}.jsonl`: GLiNER-style chunked schema

One JSON object per line. Each object represents one text chunk and
all `Dataset` mentions inside it.

| Field | Type | Required | Description |
|---|---|---|---|
| `input` | string | yes | The chunk text, verbatim from the GROBID-cleaned article. Up to 1,500 characters for CRF, SciBERT, and GLiNER2 splits; 6,000 characters for the ModernBERT-specific splits (in the source repository's `data_modernbert/` folder). |
| `output` | object | yes | Container for entities. |
| `output.entities` | object | yes | Maps each entity type to a list of mention strings present in `input`. |
| `output.entities.Dataset` | list of string | yes (may be empty for negative chunks) | Verbatim, in-order mention strings. Each appears at least once in `input`. |
| `output.entity_descriptions` | object | yes | Maps each entity type to the natural-language description used by description-conditioned models. |
| `output.entity_descriptions.Dataset` | string | yes | Fixed value: `"Names of datasets, corpus, collections, databases, benchmarks, or data collections used in scientific research"`. |

**Negative chunks.** About 15% of training chunks contain no mentions
(`Dataset: []`) and serve as negative samples; these are retained
intentionally per the chunking spec in the paper's Methods section.

**Mention order.** Mentions are listed in the order they appear in
the chunk text. Duplicate mentions within the same chunk are
deduplicated before evaluation.

**Character offsets.** The JSONL format omits explicit character
offsets, because mention strings are verbatim and alignment is
recoverable from `input.find(mention)`. For exact offsets, use the
Label Studio raw export (next section).

### Example record

```json
{
  "input": "We have also trained models without any restriction on the lesion volume; ... we did attempt to use the ISLES 2015 data for evaluating how well our models generalize ...",
  "output": {
    "entities": {
      "Dataset": ["ISLES 2015"]
    },
    "entity_descriptions": {
      "Dataset": "Names of datasets, corpus, collections, databases, benchmarks, or data collections used in scientific research"
    }
  }
}
```

## 2. `data/ood_test_labelstudio.json`: Label Studio native export

A JSON array of 151 task objects, one per OOD article. This is the
raw Label Studio export, preserved without modification so that users
can recover full character-offset spans.

### Top-level fields (per task)

| Field | Type | Description |
|---|---|---|
| `id` | int | Label Studio task id (stable across exports). |
| `data` | object | Source-text container; typically `{"text": "<full article>"}`. |
| `annotations` | list of object | List of annotation sessions (typically one per task). |
| `meta`, `created_at`, `updated_at`, `inner_id`, `project`, ... | various | Label Studio bookkeeping fields; not required for downstream use. |

### `annotations[i].result[j]`: span fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Span id (Label Studio internal). |
| `type` | string | Always `"labels"`. |
| `value.start` | int | Character offset (0-indexed, inclusive) into `data.text`. |
| `value.end` | int | Character offset (exclusive) into `data.text`. |
| `value.text` | string | The mention, verbatim, equal to `data.text[start:end]`. |
| `value.labels` | list of string | Always `["Dataset"]` for this corpus. |
| `from_name`, `to_name`, `origin` | strings | Label Studio binding metadata. |

### Example span

```json
{
  "id": "UGB8A0QGYc",
  "type": "labels",
  "value": {
    "start": 2825,
    "end":   2850,
    "text":  "PhysioNet SHAREE database",
    "labels": ["Dataset"]
  },
  "origin": "manual",
  "to_name": "text",
  "from_name": "organization"
}
```

## 3. Converting between the two formats

The companion repository ships
[`scripts/tests/iob_roundtrip.py`](https://example.org/withheld-for-review),
which:

1. Loads the Label Studio raw export.
2. Chunks each article using the same pipeline as
   `data_preparation.ipynb`.
3. Emits IOB token-level labels (B-Dataset, I-Dataset, O).
4. Re-emits character-offset spans and verifies byte-for-byte
   equality with the original Label Studio export.

A passing round-trip is the QC gate for any change to the data
pipeline.

## 4. Pseudo-code for loading

```python
import json

# JSON Lines (train, val, in-distribution test)
with open("data/train.jsonl") as f:
    train = [json.loads(line) for line in f]

# Label Studio raw export (OOD)
with open("data/ood_test_labelstudio.json") as f:
    ood = json.load(f)            # list of 151 tasks

# Extract OOD as flat (text, mention, start, end) tuples
def ood_pairs(tasks):
    for t in tasks:
        text = t["data"]["text"]
        for ann in t.get("annotations", []):
            for r in ann.get("result", []):
                if r["type"] == "labels":
                    yield text, r["value"]["text"], r["value"]["start"], r["value"]["end"]
```

## 5. Schema versioning

This schema is `MedSETNER schema v1.0.0`. Backward-incompatible
changes will bump the MAJOR version; additive fields will bump
MINOR; clarifying edits to this document bump PATCH. The schema
version is mirrored in `CITATION.cff` on each release.
