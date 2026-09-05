# Calculus

## Why agents need this
You are unlikely to train a model yourself, but every model you use *was*
trained by minimizing a loss function via gradient descent — and you'll see
this vocabulary constantly (learning rate, loss curve, convergence, gradient
clipping, fine-tuning). Understanding it conceptually is enough; you don't
need to compute derivatives by hand.

## Concepts

**Derivative** — the rate of change of a function at a point: "if I nudge the
input slightly, how much does the output change, and in which direction?"
For a curve, it's the slope of the line tangent to the curve at that point.

**Gradient** — the multi-variable version of a derivative. If a function
depends on many inputs (like a model's millions of parameters), the gradient
is a vector pointing in the direction of *steepest increase* of the function.

**Gradient descent (intuition)** — to minimize a function (like model error/
loss), repeatedly step in the *opposite* direction of the gradient (steepest
decrease), by a small amount controlled by the **learning rate**. Repeat until
the loss stops improving much (convergence). This is literally how neural
networks — including the ones behind your agent's LLM — are trained.

Think of it like walking downhill in fog: you can't see the whole landscape,
but you can feel which direction is downhill from where you stand, and take a
small step that way. Repeat.

## What you don't need
Formal limits, integrals, chain rule by hand, multivariable calculus proofs.
The exercises below use *numerical* approximation (finite differences) instead
of symbolic calculus, because the goal is intuition, not manual computation.

## Order to learn
derivative (numeric approximation) → gradient (multi-variable) → gradient
descent loop on a toy function.
