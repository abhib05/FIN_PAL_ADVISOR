"""
Sample text from a trained checkpoint.

Usage:
    python generate.py --checkpoint checkpoint.pkl --prompt "A budget is" --tokens 200
"""
import argparse
import pickle

import numpy as np

from data import encode, decode
from model import TinyGPT


def load_checkpoint(path):
    with open(path, "rb") as f:
        ckpt = pickle.load(f)
    model = TinyGPT(**ckpt["config"])
    for p, data in zip(model.parameters(), ckpt["params"]):
        p.data = data
    return model, ckpt["stoi"], ckpt["itos"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=str, default="checkpoint.pkl")
    ap.add_argument("--prompt", type=str, default="\n")
    ap.add_argument("--tokens", type=int, default=200)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    np.random.seed(args.seed)
    model, stoi, itos = load_checkpoint(args.checkpoint)

    idx = encode(args.prompt, stoi).reshape(1, -1)
    out = model.generate(idx, args.tokens, temperature=args.temperature, top_k=args.top_k)
    print(decode(out[0], itos))


if __name__ == "__main__":
    main()
