---
tags:
  - crf
  - ner
  - medical
  - sklearn-crfsuite
  - dataset-extraction
  - baseline
license: apache-2.0
---

# CRF Baseline - Medical Dataset Name Extraction

A CRF (Conditional Random Field) model trained to extract **dataset names** from medical/scientific research papers. This serves as a feature-engineered baseline to compare against neural NER models (GLiNER2).

## Entity Types

| Entity Type | Description |
|---|---|
| `Dataset` | Names of datasets, corpus, collections, databases, benchmarks, or data collections used in scientific research |

## Model Details

- **Architecture**: Linear-chain CRF (sklearn-crfsuite)
- **Algorithm**: L-BFGS
- **BIO scheme**: B-Dataset, I-Dataset, O
- **Tokenization**: spaCy `en_core_web_sm`
- **Features**: Word shape, POS tags, character n-grams, context window (2 tokens each direction)

## Training Details

| Parameter | Value |
|---|---|
| Data source | ~542 annotated medical research papers (Label Studio) |
| Training chunks | 5133 (49027 sentences) |
| Validation chunks | 684 (6474 sentences) |
| Test chunks | 1028 (9748 sentences) |
| Chunk size | 1500 chars, 300 overlap |
| Negative sample ratio | 0.15 |
| Augmentation | Entity-centered (800 char windows) |
| c1 (L1 regularization) | 0.018011 |
| c2 (L2 regularization) | 0.028829 |
| max_iterations | 100 |
| Tuning | Optuna Bayesian optimization (50 trials) |

## Evaluation Results

### Validation Set

| Metric | Exact Match | Partial Match |
|---|---|---|
| Precision | 0.6812 | 0.7198 |
| Recall | 0.6851 | 0.7240 |
| F1 | 0.6831 | 0.7219 |

### Test Set (In-Distribution)

| Metric | Exact Match | Partial Match |
|---|---|---|
| Precision | 0.6851 | 0.7464 |
| Recall | 0.6937 | 0.7558 |
| F1 | 0.6894 | 0.7511 |

### Out-of-Distribution (OOD) Test Set

| Metric | Exact Match | Partial Match |
|---|---|---|
| Precision | 0.5601 | 0.6583 |
| Recall | 0.3349 | 0.3936 |
| F1 | 0.4192 | 0.4927 |

seqeval entity-level F1: **0.9007** (test), **0.9210** (val), **0.5036** (OOD)

## Usage

```python
import joblib
import spacy
from inference import predict

# Load model
crf = joblib.load("crf_model.joblib")
nlp = spacy.load("en_core_web_sm")

# Extract entities
text = "We evaluated our model on the MIMIC-III dataset and the ChestX-ray14 benchmark."
entities = predict(text, crf, nlp)
print(entities)  # ['MIMIC-III dataset', 'ChestX-ray14 benchmark']
```

## Dependencies

```
sklearn-crfsuite>=0.3.6
spacy>=3.0
joblib>=1.0
```

Plus spaCy model: `python -m spacy download en_core_web_sm`
