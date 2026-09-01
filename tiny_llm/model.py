"""
A tiny GPT-style, character-level, decoder-only Transformer — architecturally
the same shape as nanoGPT/GPT-2 (token+position embeddings, pre-LN transformer
blocks with causal self-attention and a GELU MLP, weight-tied output head),
just implemented directly on the `Tensor` autograd engine in autograd.py
instead of a framework.
"""
import math
import numpy as np
from autograd import Tensor


def init_weight(*shape, scale=0.02):
    return Tensor(np.random.randn(*shape) * scale)


class CausalSelfAttention:
    def __init__(self, n_embd, n_head):
        assert n_embd % n_head == 0
        self.n_head = n_head
        self.head_size = n_embd // n_head
        self.w_qkv = init_weight(n_embd, 3 * n_embd)
        self.b_qkv = Tensor(np.zeros(3 * n_embd))
        self.w_proj = init_weight(n_embd, n_embd)
        self.b_proj = Tensor(np.zeros(n_embd))

    def parameters(self):
        return [self.w_qkv, self.b_qkv, self.w_proj, self.b_proj]

    def __call__(self, x: Tensor, mask: np.ndarray) -> Tensor:
        B, T, C = x.shape
        qkv = x.reshape(B * T, C) @ self.w_qkv + self.b_qkv
        qkv = qkv.reshape(B, T, 3 * C)
        q, k, v = qkv.split(3, axis=2)

        nh, hs = self.n_head, self.head_size
        q = q.reshape(B, T, nh, hs).transpose(0, 2, 1, 3)  # (B, nh, T, hs)
        k = k.reshape(B, T, nh, hs).transpose(0, 2, 1, 3)
        v = v.reshape(B, T, nh, hs).transpose(0, 2, 1, 3)

        att = (q @ k.transpose(0, 1, 3, 2)) * (1.0 / math.sqrt(hs))  # (B, nh, T, T)
        att = att + Tensor(mask, requires_grad=False)
        att = att.softmax(axis=-1)

        out = att @ v  # (B, nh, T, hs)
        out = out.transpose(0, 2, 1, 3).reshape(B, T, C)
        out = out.reshape(B * T, C) @ self.w_proj + self.b_proj
        return out.reshape(B, T, C)


class MLP:
    def __init__(self, n_embd, hidden_mult=4):
        h = hidden_mult * n_embd
        self.w1 = init_weight(n_embd, h)
        self.b1 = Tensor(np.zeros(h))
        self.w2 = init_weight(h, n_embd)
        self.b2 = Tensor(np.zeros(n_embd))

    def parameters(self):
        return [self.w1, self.b1, self.w2, self.b2]

    def __call__(self, x: Tensor) -> Tensor:
        B, T, C = x.shape
        h = (x.reshape(B * T, C) @ self.w1 + self.b1).gelu()
        out = h @ self.w2 + self.b2
        return out.reshape(B, T, C)


class LayerNorm:
    def __init__(self, n_embd):
        self.gamma = Tensor(np.ones(n_embd))
        self.beta = Tensor(np.zeros(n_embd))

    def parameters(self):
        return [self.gamma, self.beta]

    def __call__(self, x: Tensor) -> Tensor:
        return x.layernorm(self.gamma, self.beta)


class Block:
    def __init__(self, n_embd, n_head):
        self.ln1 = LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head)
        self.ln2 = LayerNorm(n_embd)
        self.mlp = MLP(n_embd)

    def parameters(self):
        return self.ln1.parameters() + self.attn.parameters() + self.ln2.parameters() + self.mlp.parameters()

    def __call__(self, x: Tensor, mask: np.ndarray) -> Tensor:
        x = x + self.attn(self.ln1(x), mask)
        x = x + self.mlp(self.ln2(x))
        return x


class TinyGPT:
    def __init__(self, vocab_size, block_size, n_embd=64, n_head=4, n_layer=2):
        self.vocab_size = vocab_size
        self.block_size = block_size
        self.n_embd = n_embd

        self.tok_emb = init_weight(vocab_size, n_embd)
        self.pos_emb = init_weight(block_size, n_embd)
        self.blocks = [Block(n_embd, n_head) for _ in range(n_layer)]
        self.ln_f = LayerNorm(n_embd)
        # weight-tied output head: reuse tok_emb as the unembedding matrix
        self._causal_mask_cache = {}

    def parameters(self):
        params = [self.tok_emb, self.pos_emb]
        for b in self.blocks:
            params += b.parameters()
        params += self.ln_f.parameters()
        return params

    def _causal_mask(self, T):
        if T not in self._causal_mask_cache:
            mask = np.triu(np.ones((T, T)), k=1) * -1e10
            self._causal_mask_cache[T] = mask.reshape(1, 1, T, T)
        return self._causal_mask_cache[T]

    def __call__(self, idx: np.ndarray, targets: np.ndarray = None):
        B, T = idx.shape
        assert T <= self.block_size, "sequence longer than block_size"

        tok = self.tok_emb[idx]  # (B, T, C)
        pos = self.pos_emb[np.arange(T)]  # (T, C)
        x = tok + pos  # broadcasts over batch

        mask = self._causal_mask(T)
        for block in self.blocks:
            x = block(x, mask)
        x = self.ln_f(x)

        logits = x.reshape(B * T, self.n_embd) @ self.tok_emb.transpose(1, 0)
        logits = logits.reshape(B, T, self.vocab_size)

        if targets is None:
            return logits, None
        loss = logits.reshape(B * T, self.vocab_size).cross_entropy(targets.reshape(B * T))
        return logits, loss

    def generate(self, idx: np.ndarray, max_new_tokens: int, temperature=1.0, top_k=None):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits.data[:, -1, :] / max(temperature, 1e-8)
            if top_k is not None:
                k = min(top_k, logits.shape[-1])
                kth = np.partition(logits, -k, axis=-1)[:, -k:].min(axis=-1, keepdims=True)
                logits = np.where(logits < kth, -1e10, logits)
            e = np.exp(logits - logits.max(axis=-1, keepdims=True))
            probs = e / e.sum(axis=-1, keepdims=True)
            next_id = np.array([[np.random.choice(self.vocab_size, p=p)] for p in probs])
            idx = np.concatenate([idx, next_id], axis=1)
        return idx
