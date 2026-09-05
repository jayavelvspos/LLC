# Linear Algebra

## Why agents need this
An LLM embedding is just a vector (a list of numbers). "Find the most relevant
document for this query" is, under the hood, "find the vector closest to this
vector." That's cosine similarity — the most-used piece of math in RAG/agent
retrieval systems.

## Concepts

**Scalar** — a single number. e.g. `temperature = 0.7`

**Vector** — an ordered list of numbers. e.g. `[0.12, -0.45, 0.88]` (could be a
3-dimensional embedding; real embeddings have hundreds/thousands of dimensions).

**Matrix** — a grid of numbers (rows x columns). e.g. a batch of several
embedding vectors stacked together, or a weight matrix inside a model.

**Dot product** — multiply matching elements of two vectors and sum the
results: `a·b = a1*b1 + a2*b2 + ... + an*bn`. It measures how much two vectors
"point the same way." Central to attention mechanisms and similarity search.

**Norm (L2 / magnitude)** — how long a vector is:
`||v|| = sqrt(v1^2 + v2^2 + ... + vn^2)`.

**Cosine similarity** — the angle between two vectors, ignoring their length:
`cos_sim(a, b) = (a·b) / (||a|| * ||b||)`.
Result is between -1 and 1. 1 = pointing the same direction (very similar
meaning), 0 = unrelated, -1 = opposite. This is exactly what vector databases
use to rank search results.

**Matrix multiplication** — combining two matrices by taking dot products of
rows and columns. This is the core operation inside every neural network layer
(you don't need to implement a neural net, just recognize "matrix multiply =
applying a transformation to many vectors at once").

**Vector space (basic idea)** — a set of vectors that can be added together and
scaled, and the result is still a valid vector in the same space. Embeddings
live in a vector space, which is *why* arithmetic on them (like averaging two
embeddings) produces something meaningful.

## Order to learn
scalar → vector → dot product → norm → cosine similarity → matrix → matrix
multiplication → vector space intuition.
