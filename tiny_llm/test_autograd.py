"""Numerical gradient check for the autograd engine and full model forward/backward."""
import numpy as np
from autograd import Tensor
from model import TinyGPT


def numerical_grad_check():
    np.random.seed(0)
    a = Tensor(np.random.randn(3, 4))
    b = Tensor(np.random.randn(4, 5))
    c = Tensor(np.random.randn(1, 5))

    def f():
        out = (a @ b + c).gelu()
        return out.sum().data.item()

    a.zero_grad(); b.zero_grad(); c.zero_grad()
    out = (a @ b + c).gelu()
    loss = out.sum()
    loss.backward()
    analytic = a.grad.copy()

    eps = 1e-5
    numeric = np.zeros_like(a.data)
    for i in range(a.data.shape[0]):
        for j in range(a.data.shape[1]):
            orig = a.data[i, j]
            a.data[i, j] = orig + eps
            plus = f()
            a.data[i, j] = orig - eps
            minus = f()
            a.data[i, j] = orig
            numeric[i, j] = (plus - minus) / (2 * eps)

    max_diff = np.abs(analytic - numeric).max()
    print("max grad diff (matmul+add+gelu+sum):", max_diff)
    assert max_diff < 1e-4, "gradient mismatch!"


def model_smoke_test():
    np.random.seed(0)
    vocab_size, block_size = 10, 8
    model = TinyGPT(vocab_size, block_size, n_embd=16, n_head=2, n_layer=2)
    idx = np.random.randint(0, vocab_size, size=(2, block_size))
    targets = np.random.randint(0, vocab_size, size=(2, block_size))

    logits, loss = model(idx, targets)
    assert logits.shape == (2, block_size, vocab_size)
    loss.backward()
    for p in model.parameters():
        assert p.grad.shape == p.data.shape
        assert np.isfinite(p.grad).all()
    print("model forward/backward smoke test passed. loss =", loss.data.item())


if __name__ == "__main__":
    numerical_grad_check()
    model_smoke_test()
    print("ALL TESTS PASSED")
