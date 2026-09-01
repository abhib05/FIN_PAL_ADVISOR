"""Character-level tokenizer and train/val split for the corpus."""
import os
import numpy as np

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "data", "corpus.txt")


def load_data(corpus_path=CORPUS_PATH, val_fraction=0.1):
    with open(corpus_path, "r", encoding="utf-8") as f:
        text = f.read()

    chars = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}

    data = np.array([stoi[c] for c in text], dtype=np.int64)
    n_val = int(len(data) * val_fraction)
    train_data, val_data = data[:-n_val], data[-n_val:]
    return train_data, val_data, stoi, itos


def get_batch(data, block_size, batch_size, rng: np.random.Generator):
    ix = rng.integers(0, len(data) - block_size - 1, size=batch_size)
    x = np.stack([data[i:i + block_size] for i in ix])
    y = np.stack([data[i + 1:i + 1 + block_size] for i in ix])
    return x, y


def encode(s, stoi):
    return np.array([stoi[c] for c in s], dtype=np.int64)


def decode(ids, itos):
    return "".join(itos[int(i)] for i in ids)
