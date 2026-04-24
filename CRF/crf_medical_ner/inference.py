"""Standalone inference script for CRF Medical Dataset NER model."""
import joblib
import spacy
from typing import Dict, List


def get_word_shape(word: str) -> str:
    """Convert word to shape pattern (X=upper, x=lower, d=digit)."""
    shape = []
    for c in word:
        if c.isupper():
            shape.append('X')
        elif c.islower():
            shape.append('x')
        elif c.isdigit():
            shape.append('d')
        else:
            shape.append(c)
    collapsed = []
    for c in shape:
        if not collapsed or collapsed[-1] != c:
            collapsed.append(c)
    return ''.join(collapsed)


def word2features(sent_tokens: List[str], sent_pos: List[str], i: int) -> Dict:
    """Extract features for token at position i."""
    word = sent_tokens[i]
    pos = sent_pos[i]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word[:3]': word[:3],
        'word[:2]': word[:2],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'word.isalpha()': word.isalpha(),
        'word.isalnum()': word.isalnum(),
        'postag': pos,
        'word_shape': get_word_shape(word),
        'has_hyphen': '-' in word,
        'has_digit': any(c.isdigit() for c in word),
        'has_upper': any(c.isupper() for c in word),
        'word_len': min(len(word), 20),
        'sent_position': i / max(len(sent_tokens) - 1, 1),
        'is_first': i == 0,
        'is_last': i == len(sent_tokens) - 1,
    }

    for offset in [-2, -1, 1, 2]:
        j = i + offset
        prefix = f'{offset:+d}:'
        if 0 <= j < len(sent_tokens):
            w = sent_tokens[j]
            p = sent_pos[j]
            features[f'{prefix}word.lower()'] = w.lower()
            features[f'{prefix}word.istitle()'] = w.istitle()
            features[f'{prefix}word.isupper()'] = w.isupper()
            features[f'{prefix}postag'] = p
            features[f'{prefix}has_hyphen'] = '-' in w
            features[f'{prefix}has_digit'] = any(c.isdigit() for c in w)
        else:
            features[f'{prefix}BOS'] = True

    if i > 0:
        features['bigram_pos_prev'] = f'{sent_pos[i-1]}|{pos}'
    if i < len(sent_tokens) - 1:
        features['bigram_pos_next'] = f'{pos}|{sent_pos[i+1]}'

    return features


def bio_to_entities(tokens: List[str], tags: List[str]) -> List[str]:
    """Decode BIO tags to entity strings."""
    entities = []
    current = []
    for tok, tag in zip(tokens, tags):
        if tag.startswith('B-'):
            if current:
                entities.append(' '.join(current))
            current = [tok]
        elif tag.startswith('I-') and current:
            current.append(tok)
        else:
            if current:
                entities.append(' '.join(current))
                current = []
    if current:
        entities.append(' '.join(current))
    return entities


def predict(text: str, crf, nlp) -> List[str]:
    """Extract dataset entities from text."""
    doc = nlp(text)
    all_entities = []

    for sent in doc.sents:
        tokens = [tok.text for tok in sent]
        pos_tags = [tok.pos_ for tok in sent]
        features = [word2features(tokens, pos_tags, i) for i in range(len(tokens))]
        tags = crf.predict([features])[0]
        all_entities.extend(bio_to_entities(tokens, tags))

    return list(set(all_entities))  # deduplicate


if __name__ == "__main__":
    import sys

    model_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    crf = joblib.load(f"{model_dir}/crf_model.joblib")
    nlp = spacy.load("en_core_web_sm")

    sample_text = (
        "We evaluated our model on the MIMIC-III dataset and the ChestX-ray14 benchmark. "
        "Additional experiments were conducted on BraTS 2020 for brain tumor segmentation."
    )

    entities = predict(sample_text, crf, nlp)
    print(f"Extracted entities: {entities}")
