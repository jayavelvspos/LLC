"""
Calculus — run me: py exercises.py
Numerical (finite-difference) approximations, no symbolic calculus needed.
"""

# ---------------------------------------------------------------------------
# Derivative — numerical approximation
# ---------------------------------------------------------------------------
def numerical_derivative(f, x, h=1e-6):
    """Slope of f at point x, approximated by a tiny nudge h."""
    return (f(x + h) - f(x - h)) / (2 * h)

def f(x):
    return x ** 2  # simple example: f(x) = x^2, true derivative is 2x

print("f(x) = x^2")
for x in [0, 1, 2, 3, -2]:
    print(f"  derivative at x={x}: approx={numerical_derivative(f, x):.4f}  "
          f"(exact = {2 * x})")

# ---------------------------------------------------------------------------
# Gradient — multi-variable version
# ---------------------------------------------------------------------------
def numerical_gradient(f, point, h=1e-6):
    """point: list of inputs. Returns list of partial derivatives, one per input."""
    grad = []
    for i in range(len(point)):
        point_plus = list(point)
        point_minus = list(point)
        point_plus[i] += h
        point_minus[i] -= h
        grad.append((f(point_plus) - f(point_minus)) / (2 * h))
    return grad

def g(point):
    x, y = point
    return x ** 2 + y ** 2  # bowl shape, minimum at (0, 0)

print("\ng(x, y) = x^2 + y^2")
print("gradient at (3, 4):", numerical_gradient(g, [3, 4]))
print("(exact gradient would be [2x, 2y] = [6, 8])")

# ---------------------------------------------------------------------------
# Gradient descent — walk downhill to find the minimum of g
# ---------------------------------------------------------------------------
def gradient_descent(f, start_point, learning_rate=0.1, steps=50):
    point = list(start_point)
    for step in range(steps):
        grad = numerical_gradient(f, point)
        point = [p - learning_rate * gr for p, gr in zip(point, grad)]
        if step % 10 == 0 or step == steps - 1:
            print(f"  step {step:2d}: point={[round(p, 4) for p in point]}, "
                  f"f(point)={f(point):.6f}")
    return point

print("\nGradient descent minimizing g(x, y) = x^2 + y^2, starting at (3, 4):")
final_point = gradient_descent(g, [3, 4])
print("final point (should approach [0, 0]):", final_point)

# ---------------------------------------------------------------------------
# TODO exercises
# ---------------------------------------------------------------------------

def h(x):
    """A function with minimum NOT at zero: (x - 5)^2 + 1, minimum at x=5."""
    return (x - 5) ** 2 + 1

def find_minimum_1d(f, start_x, learning_rate=0.1, steps=50):
    """TODO: implement 1D gradient descent to find the x that minimizes f.
    Hint: reuse numerical_derivative, step x -= learning_rate * derivative."""
    # solution:
    # x = start_x
    # for _ in range(steps):
    #     x -= learning_rate * numerical_derivative(f, x)
    # return x
    pass

# result = find_minimum_1d(h, start_x=0)
# assert abs(result - 5) < 0.01, f"expected close to 5, got {result}"

print("\nFill in find_minimum_1d above (minimize h(x), true minimum is x=5),")
print("uncomment the assert, and re-run.")
