"""
Minimal reverse-mode autodiff engine over NumPy arrays.

This is the "from scratch" part: no PyTorch/JAX, just NumPy arrays plus a
graph of Tensor nodes that know how to compute their own local gradient and
route it to their parents. `Tensor.backward()` walks the graph in reverse
topological order (classic micrograd-style engine, generalized from scalars
to N-d arrays with broadcasting support).
"""
from __future__ import annotations
import numpy as np


def _unbroadcast(grad: np.ndarray, shape: tuple) -> np.ndarray:
    """Sum-reduce `grad` back down to `shape` after a broadcasted op."""
    while grad.ndim > len(shape):
        grad = grad.sum(axis=0)
    for i, dim in enumerate(shape):
        if dim == 1 and grad.shape[i] != 1:
            grad = grad.sum(axis=i, keepdims=True)
    return grad


class Tensor:
    def __init__(self, data, children=(), requires_grad=True):
        self.data = np.asarray(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self.requires_grad = requires_grad
        self._backward = lambda: None
        self._prev = list(children)

    @property
    def shape(self):
        return self.data.shape

    # ---- graph traversal / backward ----
    def backward(self):
        topo, visited = [], set()

        def build(t):
            if id(t) not in visited:
                visited.add(id(t))
                for p in t._prev:
                    build(p)
                topo.append(t)

        build(self)
        self.grad = np.ones_like(self.data)
        for t in reversed(topo):
            t._backward()

    def zero_grad(self):
        self.grad = np.zeros_like(self.data)

    # ---- elementwise arithmetic ----
    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)
        out = Tensor(self.data + other.data, (self, other))

        def _backward():
            self.grad += _unbroadcast(out.grad, self.data.shape)
            other.grad += _unbroadcast(out.grad, other.data.shape)

        out._backward = _backward
        return out

    def __neg__(self):
        return self * -1.0

    def __sub__(self, other):
        return self + (-(other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)))

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)
        out = Tensor(self.data * other.data, (self, other))

        def _backward():
            self.grad += _unbroadcast(out.grad * other.data, self.data.shape)
            other.grad += _unbroadcast(out.grad * self.data, other.data.shape)

        out._backward = _backward
        return out

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)
        out = Tensor(self.data / other.data, (self, other))

        def _backward():
            self.grad += _unbroadcast(out.grad / other.data, self.data.shape)
            other.grad += _unbroadcast(-out.grad * self.data / (other.data ** 2), other.data.shape)

        out._backward = _backward
        return out

    def __pow__(self, p: float):
        out = Tensor(self.data ** p, (self,))

        def _backward():
            self.grad += (p * self.data ** (p - 1)) * out.grad

        out._backward = _backward
        return out

    # ---- matmul (supports batched leading dims, like np.matmul) ----
    def __matmul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other, requires_grad=False)
        out = Tensor(self.data @ other.data, (self, other))

        def _backward():
            dself = out.grad @ np.swapaxes(other.data, -1, -2)
            dother = np.swapaxes(self.data, -1, -2) @ out.grad
            self.grad += _unbroadcast(dself, self.data.shape)
            other.grad += _unbroadcast(dother, other.data.shape)

        out._backward = _backward
        return out

    # ---- reductions ----
    def sum(self, axis=None, keepdims=False):
        out = Tensor(self.data.sum(axis=axis, keepdims=keepdims), (self,))

        def _backward():
            g = out.grad
            if not keepdims and axis is not None:
                g = np.expand_dims(g, axis)
            self.grad += np.ones_like(self.data) * g

        out._backward = _backward
        return out

    def mean(self, axis=None, keepdims=False):
        n = self.data.size if axis is None else self.data.shape[axis]
        return self.sum(axis=axis, keepdims=keepdims) * (1.0 / n)

    # ---- shape ops ----
    def transpose(self, *axes):
        out = Tensor(self.data.transpose(*axes), (self,))

        def _backward():
            inv = np.argsort(axes)
            self.grad += out.grad.transpose(*inv)

        out._backward = _backward
        return out

    def reshape(self, *shape):
        orig_shape = self.data.shape
        out = Tensor(self.data.reshape(*shape), (self,))

        def _backward():
            self.grad += out.grad.reshape(orig_shape)

        out._backward = _backward
        return out

    def split(self, n_chunks, axis):
        """Split into `n_chunks` equal Tensors along `axis`."""
        parts = np.split(self.data, n_chunks, axis=axis)
        outs = []
        for i, p in enumerate(parts):
            out = Tensor(p, (self,))

            def make_backward(idx, part_shape, out_ref):
                def _backward():
                    grad_full = np.zeros_like(self.data)
                    slicer = [slice(None)] * self.data.ndim
                    size = part_shape[axis]
                    slicer[axis] = slice(idx * size, (idx + 1) * size)
                    grad_full[tuple(slicer)] = out_ref.grad
                    self.grad += grad_full

                return _backward

            out._backward = make_backward(i, p.shape, out)
            outs.append(out)
        return outs

    @staticmethod
    def cat(tensors, axis):
        datas = [t.data for t in tensors]
        out = Tensor(np.concatenate(datas, axis=axis), tuple(tensors))
        sizes = [d.shape[axis] for d in datas]

        def _backward():
            offset = 0
            for t, size in zip(tensors, sizes):
                slicer = [slice(None)] * out.data.ndim
                slicer[axis] = slice(offset, offset + size)
                t.grad += out.grad[tuple(slicer)]
                offset += size

        out._backward = _backward
        return out

    # ---- embedding-style gather ----
    def __getitem__(self, idx):
        out = Tensor(self.data[idx], (self,))

        def _backward():
            np.add.at(self.grad, idx, out.grad)

        out._backward = _backward
        return out

    # ---- nonlinearities ----
    def gelu(self):
        x = self.data
        c = np.sqrt(2.0 / np.pi)
        inner = c * (x + 0.044715 * x ** 3)
        t = np.tanh(inner)
        out_data = 0.5 * x * (1.0 + t)
        out = Tensor(out_data, (self,))

        def _backward():
            sech2 = 1.0 - t ** 2
            dinner = c * (1.0 + 3 * 0.044715 * x ** 2)
            local_grad = 0.5 * (1.0 + t) + 0.5 * x * sech2 * dinner
            self.grad += out.grad * local_grad

        out._backward = _backward
        return out

    def layernorm(self, gamma: "Tensor", beta: "Tensor", eps=1e-5):
        x = self.data
        mu = x.mean(axis=-1, keepdims=True)
        var = ((x - mu) ** 2).mean(axis=-1, keepdims=True)
        std_inv = 1.0 / np.sqrt(var + eps)
        xhat = (x - mu) * std_inv
        out_data = xhat * gamma.data + beta.data
        out = Tensor(out_data, (self, gamma, beta))
        n = x.shape[-1]

        def _backward():
            g = out.grad
            beta.grad += _unbroadcast(g, beta.data.shape)
            gamma.grad += _unbroadcast(g * xhat, gamma.data.shape)
            dxhat = g * gamma.data
            dx = (1.0 / n) * std_inv * (
                n * dxhat
                - dxhat.sum(axis=-1, keepdims=True)
                - xhat * (dxhat * xhat).sum(axis=-1, keepdims=True)
            )
            self.grad += dx

        out._backward = _backward
        return out

    def softmax(self, axis=-1):
        x = self.data
        m = x.max(axis=axis, keepdims=True)
        e = np.exp(x - m)
        s = e / e.sum(axis=axis, keepdims=True)
        out = Tensor(s, (self,))

        def _backward():
            g = out.grad
            dot = (g * s).sum(axis=axis, keepdims=True)
            self.grad += s * (g - dot)

        out._backward = _backward
        return out

    def cross_entropy(self, targets: np.ndarray):
        """self: logits of shape (N, vocab). targets: int array shape (N,)."""
        x = self.data
        m = x.max(axis=-1, keepdims=True)
        e = np.exp(x - m)
        probs = e / e.sum(axis=-1, keepdims=True)
        n = x.shape[0]
        logp = -np.log(np.clip(probs[np.arange(n), targets], 1e-12, None))
        loss_val = logp.mean()
        out = Tensor(loss_val, (self,))

        def _backward():
            dlogits = probs.copy()
            dlogits[np.arange(n), targets] -= 1.0
            dlogits /= n
            self.grad += dlogits * out.grad

        out._backward = _backward
        return out
