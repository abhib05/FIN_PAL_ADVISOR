"""
Train the tiny char-level GPT on the bundled finance corpus, pure NumPy.

Usage:
    python train.py --iters 2000 --block-size 64 --batch-size 32
"""
import argparse
import pickle
import time

import numpy as np

from data import load_data, get_batch
from model import TinyGPT
from optim import Adam


def estimate_loss(model, data, block_size, batch_size, rng, eval_iters=20):
    losses = []
    for _ in range(eval_iters):
        x, y = get_batch(data, block_size, batch_size, rng)
        _, loss = model(x, y)
        losses.append(loss.data.item())
    return float(np.mean(losses))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--block-size", type=int, default=64)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--n-embd", type=int, default=64)
    ap.add_argument("--n-head", type=int, default=4)
    ap.add_argument("--n-layer", type=int, default=2)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--eval-every", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--out", type=str, default="checkpoint.pkl")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    np.random.seed(args.seed)

    train_data, val_data, stoi, itos = load_data()
    print(f"vocab size: {len(stoi)} | train chars: {len(train_data)} | val chars: {len(val_data)}")

    model = TinyGPT(
        vocab_size=len(stoi),
        block_size=args.block_size,
        n_embd=args.n_embd,
        n_head=args.n_head,
        n_layer=args.n_layer,
    )
    params = model.parameters()
    n_params = sum(p.data.size for p in params)
    print(f"model params: {n_params:,}")

    opt = Adam(params, lr=args.lr)

    t0 = time.time()
    for it in range(1, args.iters + 1):
        x, y = get_batch(train_data, args.block_size, args.batch_size, rng)
        opt.zero_grad()
        _, loss = model(x, y)
        loss.backward()
        opt.step()

        if it % args.eval_every == 0 or it == 1:
            val_loss = estimate_loss(model, val_data, args.block_size, args.batch_size, rng)
            elapsed = time.time() - t0
            print(f"iter {it:5d} | train loss {loss.data.item():.4f} | val loss {val_loss:.4f} | {elapsed:.1f}s")

    with open(args.out, "wb") as f:
        pickle.dump({
            "params": [p.data for p in params],
            "config": dict(vocab_size=len(stoi), block_size=args.block_size,
                            n_embd=args.n_embd, n_head=args.n_head, n_layer=args.n_layer),
            "stoi": stoi,
            "itos": itos,
        }, f)
    print(f"saved checkpoint to {args.out}")


if __name__ == "__main__":
    main()
