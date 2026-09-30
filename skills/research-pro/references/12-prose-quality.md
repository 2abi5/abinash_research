# S7 — Prose quality (the humanizer)

## What this does, and what it refuses to do

**Does:** take text that reads as machine-generated — fluent, evenly paced,
abstract, hedged, and strangely empty — and rewrite it so it reads as though a
specific researcher with a specific argument wrote it. That means variance in
sentence length, concrete nouns, verbs that carry the claim, earned transitions,
and every paragraph doing work.

**Refuses:** helping a paper evade AI-detection tools, or concealing AI assistance
that a venue's policy requires disclosing. That is not a squeamish position, it is
a practical one:

- Major venues now desk-reject over LLM-policy violations, and they act at scale.
  ICML 2026 desk-rejected 497 submissions in one cycle over LLM policy breaches.
  ICLR 2026 has desk-rejected LLM-generated submissions outright.
- Prompt injection hidden in a submitted manuscript is an explicit
  rejection-and-report offence at multiple venues.
- Detector scores are not what gets papers rejected. **Reviewers** reject papers,
  and they reject them for vagueness, unsupported claims, and prose that says
  nothing — which is exactly what this file fixes. Optimizing for a detector and
  optimizing for a reviewer point in the same direction for the first 95% and then
  diverge; follow the reviewer.

So: fix the writing, and disclose per policy. `18-disclosure-and-ethics.md` has
the disclosure text and the per-venue requirements. Both, not one.

## Measure first

```bash
python3 skills/research-pro/scripts/prose_metrics.py paper/main.tex
```

It reports banned-phrase hits, sentence-length distribution and variance,
hedge density, transition-opener density, nominalization rate, passive rate, and
per-paragraph shape. Fix what it flags, then read aloud. The script finds
patterns; only reading finds emptiness.

## The tells, and the fix for each

### 1. Lexical tells

These words are not wrong in themselves; their *frequency* in machine text has
made them a signature. In academic prose most are also imprecise, which is the
real reason to cut them.

| Cut | Use instead |
|---|---|
| delve into | examine, measure, test |
| leverage (verb) | use |
| utilize | use |
| underscore, highlight (as verb) | show, indicate — or name the mechanism |
| pivotal, crucial, vital, essential | say *why* it matters, or drop it |
| realm, landscape, arena, sphere | the actual field name |
| tapestry, symphony, testament, cornerstone | delete; these never survive a good edit |
| robust (as praise) | state the perturbation it survived |
| comprehensive, holistic, seamless | delete or quantify |
| myriad, plethora, a host of | the number |
| navigate (metaphor), foster, harness, unlock, elevate | the literal verb |
| intricate, meticulous, nuanced | specify what is complex, and how |
| state-of-the-art (as adjective) | name the method and its number |
| novel | delete. Novelty is demonstrated, never asserted |

### 2. Phrase tells

Delete outright. Every one is throat-clearing — it delays the sentence's content
without adding any.

- "It is important to note that" / "It is worth noting that" / "Notably,"
- "plays a crucial role in" / "serves as a" / "stands as"
- "sheds light on" / "paves the way for" / "opens new avenues"
- "In the realm of" / "In the context of" / "When it comes to"
- "In today's rapidly evolving landscape"
- "In recent years, there has been growing interest in"
- "a testament to" / "a wide range of" / "a variety of"
- "It should be emphasized that" / "One must consider"
- "Overall," / "In summary," at the start of a paragraph that is not a summary

Test: delete the phrase. If the sentence is unchanged in meaning, it was noise.
That test removes most of them.

### 3. Structural tells — the ones that actually give it away

Lexical fixes are cosmetic. These are the structural signatures, and they are what
make a reader feel the text is machine-made even after every banned word is gone.

**Uniform sentence length.** Machine prose clusters at 18–25 words with low
variance. Human academic prose varies hard: a 40-word sentence laying out a
mechanism, then a 6-word sentence landing the point. **Target a standard
deviation of at least 8 words, and put at least one sentence under 10 words in
every paragraph.** The short sentence is where the argument lands. Use it.

**Tricolon addiction.** Three-item lists everywhere — "accurate, efficient, and
scalable." Real arguments rarely decompose into threes. Cut to the one item that
matters, or expand to the four that are actually true.

**Transition-opener stacking.** Every paragraph starting with Moreover,
Furthermore, Additionally, Consequently. A transition should be *earned* by a
real logical relation. If the relation is just "here is another thing," start with
the subject instead. Aim for under one in four paragraphs opening with a
transition adverb.

**Symmetrical concessive openers.** "While X, Y." "Although X, Y." Once per page
is style; four times is a tic.

**Empty topic sentences.** "This section describes our experimental setup." The
first sentence should carry the paragraph's *claim*, not announce its topic.
Compare: "Our evaluation isolates the gate by holding parameter count fixed."

**Hedge sandwiches.** "These results may potentially suggest that the approach
could offer improvements in certain settings." Four hedges, zero content. One
hedge is honest calibration; three means the claim should be cut. Reviewers read
stacked hedges as an author who knows the evidence is thin.

**Uniform paragraph length.** Five paragraphs of five sentences each reads as
generated. Let a paragraph be two sentences when two sentences is the thought.

**Over-signposting.** "In this section, we will first describe X, then Y, and
finally Z." One roadmap in the paper's introduction is useful. One per section is
padding bought at the price of an ablation.

**Section-closing summaries.** A paragraph at the end of every section restating
the section. Cut them all; the reader just read it.

### 4. The emptiness tell

The deepest one, and no script catches it. A paragraph is fluent, grammatical,
on-topic — and conveys nothing a reader did not already know.

Diagnostic: after each paragraph, ask **"what does the reader now know that they
did not before?"** If the answer is "that this topic is important" or "that the
authors are aware of X," delete the paragraph. Nothing is lost.

This single question typically removes 10–15% of a first draft and makes room for
the analysis figure you did not have space for.

## The rewrite procedure

Work paragraph by paragraph. Do not pass over a whole section at once — you will
smooth it evenly, which is the problem you are trying to fix.

For each paragraph:

1. **Name its one message** in your own words. If it has two, split it. If it has
   none, delete it.
2. **Put the message in the first sentence.**
3. **Make each following sentence do one job** and stand in a nameable relation to
   the one before: cause, contrast, consequence, refinement, example. If you cannot
   name the relation, the sentences are merely adjacent and the paragraph does not
   cohere.
4. **Convert nominalizations back to verbs.** "We performed an evaluation of the
   impact of the modification" → "We measured what the change did." Nominalization
   is the single largest source of the flat academic register.
5. **Give the verbs to real agents.** Passive voice is fine for methods where the
   agent is obvious ("images were resized to 224×224"), and bad where it hides who
   did what ("it was determined that"). Never "it can be observed that X" — write
   "X".
6. **Replace abstractions with the specific thing.** "the model" → "the 7B
   checkpoint"; "performance" → "top-1 accuracy"; "significant improvement" → "2.4
   points".
7. **Vary the rhythm.** After a long mechanism sentence, land a short one.
8. **Read it aloud.** Every place you stumble is a place a reviewer slows down.
   This step is not optional and it catches what none of the above does.

## Reverse-outline after every section

The check for structure, as opposed to sentences. Do it immediately after drafting
a section, not at the end of the paper.

1. Write the section's thesis in one line.
2. List each paragraph's first sentence, in order.
3. Under each, list its evidence.
4. Check two mappings: does every topic sentence serve the thesis, and does every
   piece of evidence serve its topic sentence?
5. Any paragraph that maps to neither gets rewritten or cut.

If the reverse outline reads as a coherent argument on its own, the section works.
If you cannot construct it, the reader cannot either — and that is a structural
problem no sentence-level editing will fix.

## Preserve the author's voice

If the author has prior papers, read two or three before rewriting and match:
sentence length distribution, first person (`we` vs passive), how citations are
integrated (`Kim et al. show that` vs `prior work shows [12]`), the level of
hedging, and whether they use contractions (in most venues, no).

Then apply the field's conventions over the author's habits where they conflict,
and say which you did. An author's draft made "better" but no longer theirs is a
failure, and they will spend a day undoing it.

## What not to strip

Do not flatten these while removing tells:

- **Calibrated hedges on genuinely uncertain claims.** "We hypothesize", "this
  suggests", "under our assumptions" are precision, not weakness. Removing them
  creates overclaiming, which is worse than a tic.
- **Field-required formality.** Some venues expect no first person. Follow the
  venue.
- **Technical repetition.** A term must stay the same term every time. Varying
  vocabulary for elegance is a virtue in essays and a defect in papers.
- **Necessary length.** A mechanism that takes 40 words to state accurately gets 40
  words.

## Checks

1. Zero banned phrases (`prose_metrics.py` reports them)?
2. Sentence-length standard deviation ≥ 8 words?
3. At least one sentence under 10 words per paragraph?
4. Fewer than one in four paragraphs opening with a transition adverb?
5. No paragraph with more than two hedges?
6. Every paragraph passes "what does the reader now know?"
7. Every section reverse-outlines cleanly?
8. Terminology identical throughout?
9. Read aloud end to end?
10. Disclosure statement drafted per venue policy
    (`18-disclosure-and-ethics.md`)?
