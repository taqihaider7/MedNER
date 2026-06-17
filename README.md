# MedSETNER

A benchmark corpus for extracting dataset names from medical scientific
literature.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![FAIR](https://img.shields.io/badge/FAIR-Yes-brightgreen.svg)](https://www.go-fair.org/fair-principles/)

This is the anonymous release for Open Data MICCAI 2026 review. Authors,
the full repository URL, and the DOI will be added on acceptance.

## 1. Overview

MedSETNER is the first annotated benchmark for extracting dataset names
from medical and biomedical research articles. Dataset references in
medical papers tend to be embedded in free-form prose, written with
inconsistent nomenclature, and rarely tied to a persistent identifier.
Existing dataset-mention corpora cover computer science or general
science publications and do not cover medical text; that is the gap
this corpus fills.

Key facts:

- **Modality (per Open Data MICCAI Sec. IV.B):** clinical and
  scientific reports, unstructured text. Language: English.
  Processing status: GROBID-cleaned scientific prose.
- **Domain:** medical AI, covering radiology, pathology, genomics, and
  clinical informatics. Names in the corpus include imaging benchmarks
  such as BraTS, EMIDEC, TCIA, and MIMIC-CXR that are used across the
  medical image computing community.
- **Task:** named entity recognition with a single entity type,
  `Dataset`.
- **Scale:** 542 in-distribution articles and 151 out-of-distribution
  articles. 8,670 chunk-level instances. 13,132 character-aligned
  dataset-name mentions.

## 2. Repository structure

```
MedSETNER/
  README.md                       this file
  LICENSE.txt                     CC BY 4.0 (data and annotations)
  LICENSE-CODE.txt                MIT (code and evaluation scripts)
  SCHEMA.md                       field-by-field data dictionary
  CITATION.cff                    citation metadata
  data/
    train.jsonl                   5,133 chunks, GLiNER schema
    val.jsonl                     684 chunks, GLiNER schema
    test.jsonl                    1,028 chunks, GLiNER schema (in-distribution)
    ood_test_labelstudio.json     151 articles, raw Label Studio export
```

The full processing notebooks and per-model training code live in the
companion code repository (link withheld for review). The README of
that repository contains a runnable end-to-end pipeline from source
PDF, through chunked JSONL, to a trained model.

## 3. Naming conventions

| File | Format | One record |
|---|---|---|
| `data/train.jsonl` | JSON Lines | one text chunk, with all `Dataset` mentions in it |
| `data/val.jsonl` | JSON Lines | same |
| `data/test.jsonl` | JSON Lines | same (in-distribution test) |
| `data/ood_test_labelstudio.json` | JSON (list) | one whole article (151 total), raw Label Studio task export with character-offset annotations |

Chunks are stored in positional order: chunks appear in the same
order as the underlying article. No chunk ID is stored. Alignment is
recoverable from JSONL line order and from the character offsets in
the raw OOD export.

## 4. Schema (data dictionary)

See [`SCHEMA.md`](SCHEMA.md) for the per-field dictionary, types,
example values, and a conversion script between Label Studio span
offsets and IOB tags. A condensed view of the JSONL schema:

```json
{
  "input":  "<text chunk, up to 1500 chars>",
  "output": {
    "entities": {
      "Dataset": ["<verbatim mention 1>", "<verbatim mention 2>"]
    },
    "entity_descriptions": {
      "Dataset": "Names of datasets, corpus, collections, databases, benchmarks, or data collections used in scientific research"
    }
  }
}
```

The OOD file (`data/ood_test_labelstudio.json`) is a JSON array. Each
element is a Label Studio task whose `annotations[i].result[j].value`
carries `{start, end, text, labels}` per span.

## 5. Modality-specific metadata (per Open Data MICCAI Sec. IV.B)

| Field | Value |
|---|---|
| Report type | Scientific and biomedical research articles |
| Language | English |
| Processing status | Cleaned (GROBID, section filtering, NFKC normalisation) |
| Number of articles | 693 (542 in-distribution, 151 OOD) |
| Number of chunks | 8,670 |
| Number of mentions | 13,132 |
| Unique mention strings (in-distribution) | ~3,695 |
| Annotation entity types | `Dataset` (single class) |
| Annotation format on disk | Character-offset spans (Label Studio native) and IOB-converted JSONL |

## 6. License and compatibility

- **Annotations** (the contribution of this dataset) are released
  under **CC BY 4.0**. See [`LICENSE.txt`](LICENSE.txt) and
  <https://creativecommons.org/licenses/by/4.0/>. Version: 4.0
  International. Users may share and adapt the annotations with
  attribution.
- **Code and evaluation scripts** in the companion repository are
  released under **MIT**. See [`LICENSE-CODE.txt`](LICENSE-CODE.txt)
  and <https://opensource.org/licenses/MIT>. CC is not intended for
  software, which is why we use a separate licence for code.
- **Source article text** remains under each publisher's original
  licence. We distribute only the chunked excerpts needed to
  interpret the annotations. Each annotation references its source by
  arXiv-id, PMC-id, or DOI, so the full article can be retrieved from
  the publisher. We do not redistribute full articles.
- **Compatibility statement.** The annotation layer is original work
  by the project team and is not a derivative of any upstream-licensed
  labels. Where source text is from CC-BY, CC-BY-SA, CC-BY-NC, or
  all-rights-reserved publishers, the excerpts are reproduced under
  the fair-use or quotation right for research. Downstream
  redistribution of the source text beyond research use must respect
  each publisher's terms.

## 7. Ethics and responsible use

- **Ethical approval.** Exempt. The work uses only previously
  published, openly accessible scientific text. No human subjects were
  involved, no patient data was processed, and no clinical records
  were accessed. A formal exemption letter from the contributing
  institution's ethics office is on file and available on request.
- **Inclusion of vulnerable populations:** none.
- **Data provider location:** withheld for review.
- **Sensitivity level:** public and open.
- **Informed consent:** not applicable (no human subjects).
- **Anonymisation procedure:** not applicable to source text. Author
  names of source articles are retained as published.
- **Intended use.** Training and benchmarking medical
  dataset-name-extraction systems, building dataset-citation graphs,
  and auditing dataset reuse in medical AI literature.
- **Known misuse risks.** Automatically attributing predicted
  mentions to authors or institutions without human verification
  could cause misattribution and harm to authors. Users must not rely
  on raw model predictions as authoritative records.
- **Ethical use clause.** By using this dataset you agree (i) not to
  attempt to re-identify any individual from incidental personal
  names occurring in the text, (ii) to report suspected data quality
  or ethics issues to the contact below, and (iii) to use the dataset
  in accordance with applicable research ethics standards.
- **Versioning policy.** Future versions will use semantic versioning
  (`MAJOR.MINOR.PATCH`) with a CHANGELOG entry per release. Any
  record removal or withdrawal will be logged with a date and reason.
  Each version receives its own Zenodo DOI.
- **Contact (Open Data and ethics).** `anonymous@anonymous.org`
  (de-anonymised on acceptance).

## 8. FAIR principles

- **Findable.** Hosted on Zenodo with a persistent DOI, with the
  metadata required by DataCite.
- **Accessible.** Public direct download. No registration, no request
  form.
- **Interoperable.** JSON Lines (a universal format), explicit
  character offsets, and an IOB conversion script for any token-level
  NER framework.
- **Reusable.** CC BY 4.0 licence, source provenance recorded per
  article, and five reference baselines that can be re-run from the
  bundled configs.

## 9. AI-readiness

- Train, validation, in-distribution test, and OOD test splits are
  pre-computed and stored as separate files.
- An evaluation script in the source repository
  (`scripts/evaluate.py`) reports exact- and partial-match precision,
  recall, and F1.
- Reference baselines for five model families are bundled: rule-based,
  CRF, SciBERT, ModernBERT, and GLiNER2 (zero-shot and fine-tuned).
- All hyperparameters used in the accompanying paper are recorded in
  per-model config files.

## 10. Validation summary

We benchmarked five extraction approaches. ModernBERT achieves the
highest in-distribution exact-match F1 of 0.901. Fine-tuned GLiNER2
is the most robust under distribution shift, with an OOD exact-match
F1 of 0.740 and an adaptation gap of only $-$0.053. Full results, the
OOD test set, and ablation scripts are in the paper and the
companion repository.

## 11. How to cite

Citation metadata will be released in `CITATION.cff` on acceptance.
Until then, please cite as:

> *Anonymous Authors.* MedSETNER: A Benchmark Corpus for Extracting
> Dataset Names from Medical Scientific Literature. Open Data MICCAI
> 2026 submission (under review). Anonymous DOI to be assigned.
