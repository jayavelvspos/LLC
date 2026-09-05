"""
Linear Algebra — run me: py exercises.py
Pure Python, no numpy, so you see every operation explicitly.
"""

import math

# ---------------------------------------------------------------------------
# 1. Scalars & Vectors
# ---------------------------------------------------------------------------
scalar = 0.7
vector_a = [0.12, -0.45, 0.88]
vector_b = [0.10, -0.40, 0.95]

print("scalar:", scalar)
print("vector_a:", vector_a)
print("vector_b:", vector_b)

# ---------------------------------------------------------------------------
# 2. Dot product
# ---------------------------------------------------------------------------
def dot_product(a, b):
    assert len(a) == len(b), "vectors must be same length"
    return sum(x * y for x, y in zip(a, b))

print("\ndot_product(a, b):", dot_product(vector_a, vector_b))

# ---------------------------------------------------------------------------
# 3. Norm (magnitude / length)
# ---------------------------------------------------------------------------
def norm(v):
    return math.sqrt(sum(x * x for x in v))

print("norm(vector_a):", norm(vector_a))

# ---------------------------------------------------------------------------
# 4. Cosine similarity — the core of semantic search
# ---------------------------------------------------------------------------
def cosine_similarity(a, b):
    return dot_product(a, b) / (norm(a) * norm(b))

print("cosine_similarity(a, b):", cosine_similarity(vector_a, vector_b))

# Agent use case: which of these two "documents" is more relevant to the query?
query = [0.20, 0.10, 0.97]
doc_1 = [0.19, 0.12, 0.96]     # close to query
doc_2 = [-0.80, 0.55, 0.10]    # unrelated

print("\nquery vs doc_1 similarity:", cosine_similarity(query, doc_1))
print("query vs doc_2 similarity:", cosine_similarity(query, doc_2))
print("-> the agent should retrieve doc_1, it scores higher")

# ---------------------------------------------------------------------------
# 5. Matrices & matrix multiplication
# ---------------------------------------------------------------------------
# A matrix as a list of row-vectors
matrix_A = [
    [1, 2],
    [3, 4],
]
matrix_B = [
    [5, 6],
    [7, 8],
]

def matmul(A, B):
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    assert cols_A == rows_B, "inner dimensions must match"
    result = [[0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            result[i][j] = sum(A[i][k] * B[k][j] for k in range(cols_A))
    return result

print("\nmatmul(A, B):", matmul(matrix_A, matrix_B))

# ---------------------------------------------------------------------------
# TODO exercises — write the function, then uncomment the assert to check it
# ---------------------------------------------------------------------------

def vector_add(a, b):
    """TODO: return element-wise sum of a and b."""
    # solution: return [x + y for x, y in zip(a, b)]
    pass

# assert vector_add([1, 2, 3], [4, 5, 6]) == [5, 7, 9]

def scalar_multiply(scalar, v):
    """TODO: return v scaled by scalar."""
    # solution: return [scalar * x for x in v]
    pass

# assert scalar_multiply(2, [1, -2, 3]) == [2, -4, 6]

def normalize(v):
    """TODO: return v scaled to unit length (norm == 1)."""
    # solution: n = norm(v); return [x / n for x in v]
    pass

# assert abs(norm(normalize([3, 4])) - 1.0) < 1e-9

print("\nFill in the TODO functions above, uncomment their asserts, and re-run.")
