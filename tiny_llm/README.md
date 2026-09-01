# tiny_llm — a from-scratch, character-level GPT

An educational language model built without any ML framework (no PyTorch/
TensorFlow/JAX) — just NumPy. It exists to show how an LLM actually works
under the hood: a hand-rolled reverse-mode autodiff engine, and a small
GPT-style decoder-only Transformer built on top of it, trained on a bundled
finance-themed corpus in keeping with the FinPal app.

This is a toy for learning, not a production model — a few hundred thousand
parameters trained on a few KB of text will produce locally-plausible but not
meaningfully "smart" text. For real advisory-quality language generation,
FinPal's backend uses hosted LLM APIs (see `backend/app/orchestrator/`); this
module is unrelated to that runtime path.

## Files

```
autograd.py   Tensor class: NumPy arrays + a graph of ops with a .backward()
              (add, mul, div, pow, matmul, sum/mean, transpose/reshape/split,
              embedding-style indexing, gelu, layernorm, softmax, cross-entropy)
model.py      TinyGPT: token+position embeddings, pre-LN transformer blocks
              (causal self-attention + GELU MLP), weight-tied output head —
              the same architecture shape as nanoGPT/GPT-2, just built
              directly on autograd.py instead of a framework
optim.py      Adam optimizer over Tensor.data/.grad
data.py       Character-level tokenizer + batching
data/corpus.txt  Small bundled finance-themed training text
train.py      Training loop (checkpoints to a pickle file)
generate.py   Sample text from a checkpoint
test_autograd.py  Numerical gradient checks + a model forward/backward smoke test
```

## Quickstart

```bash
cd tiny_llm
python3 test_autograd.py                 # verify the autograd engine is correct
python3 train.py --iters 2000            # train (few minutes on CPU, pure NumPy)
python3 generate.py --prompt "A budget is" --tokens 200
```

## Why NumPy instead of PyTorch

This module was built in an environment where installing PyTorch wasn't
possible, so the autograd engine (`autograd.py`) implements reverse-mode
differentiation by hand: every `Tensor` op records its inputs and a closure
that computes the local gradient, and `Tensor.backward()` walks that graph in
reverse topological order — the same idea as micrograd, generalized from
scalars to broadcasting N-d arrays. If you have PyTorch available, swapping
in `torch.Tensor`/`nn.Module` would be a natural next step and would train
much faster.

## Known limitations

- Pure NumPy attention/matmul has no GPU/vectorized-kernel speedup, so
  training is slow relative to a real framework — kept intentionally tiny
  (2 layers, 64-dim embeddings) so it still trains in minutes on CPU.
- The bundled corpus is a few KB, so the model will mostly relearn its
  training text rather than generalize — enough to demonstrate the
  architecture and training loop, not to produce a useful assistant.
