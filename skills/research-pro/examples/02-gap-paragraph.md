# Worked example — the gap paragraph (Introduction P2)

The single highest-leverage paragraph in a paper. It must end on a technical
**reason**, because that reason is what your method attacks.

## Version A — patch framing (avoid)

> A simple approach to conditional computation is to add a gate at each layer that
> selects a subset of experts. We improve on this by pooling features before gating,
> which gives better accuracy.

Why this loses: the reader now believes the idea is obvious and yours is a small
delta on it. You have written the reviewer's "incremental" comment for them. Even
when literally accurate, this framing costs score.

## Version B — limitation without a reason (weak)

> Prior routing methods select experts per layer [12, 15]. However, these methods
> have limited accuracy and do not generalize well.

Why this is weak: "limited accuracy" is a symptom. There is no mechanism, so there
is nothing for your method to be the answer *to*. A reviewer reads this as an author
who does not understand why prior work fails.

## Version C — challenge framing (use)

> Conditional computation reduces inference cost by activating a subset of a model's
> parameters per input. The dominant approach gates each layer independently
> [12, 15]: a small router at layer $\ell$ scores the experts available at that
> layer and dispatches the token. This works when the information that determines
> the right expert is already present at $\ell$. It is not, for inputs whose class
> is disambiguated late — a router at layer 4 must commit before the features that
> distinguish the two candidate classes exist. Increasing router capacity does not
> help, because the missing quantity is not modelling power but **information that
> has not arrived yet**.

Why this works, clause by clause:

| Clause | Job |
|---|---|
| "reduces inference cost by activating a subset" | defines the task, mechanistically |
| "gates each layer independently [12,15]" | names prior work by mechanism, not by name-dropping |
| "This works when …" | grants prior work its legitimate domain — this is what makes you credible |
| "It is not, for inputs whose class is disambiguated late" | the failure **condition** |
| "must commit before the features … exist" | the failure **reason** |
| "Increasing router capacity does not help, because …" | forecloses the obvious fix, so your idea is the non-obvious one |

The reader now wants exactly one thing: a gate that sees later information before
committing. Your method arrives as the answer to a question they are already
asking — and that is the entire difference between a paper that reads as a
contribution and one that reads as a tweak.

## The test

Cover your method and read P2 alone. Can the reader state, in one sentence, what a
solution would have to do? If not, the paragraph has not done its job.
