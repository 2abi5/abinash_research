# S7 — Prose quality (the humanizer)

## What this does, and what it refuses to do

**Does:** take text that reads as machine-generated (fluent, evenly paced, abstract,
hedged, and strangely empty) and rewrite it so it reads as though a specific
researcher with a specific argument wrote it. That means variance in sentence
length, concrete nouns, verbs that carry the claim, earned transitions, and every
paragraph doing work.

**Refuses:** helping a paper evade AI-detection tools, or concealing AI assistance
that a venue's policy requires disclosing. That is a practical position, not a
squeamish one:

- Major venues desk-reject over LLM-policy violations, and they act at scale.
  Undisclosed use is escalated; LLM-generated submissions have been rejected outright.
- Prompt injection hidden in a manuscript is an explicit rejection-and-report offence
  at multiple venues.
- Detector scores are not what gets papers rejected. **Reviewers** reject papers, for
  vagueness, unsupported claims, and prose that says nothing, which is exactly what
  this file fixes. Optimizing for a detector and optimizing for a reviewer point the
  same way for most of the distance and then diverge; follow the reviewer.

So: fix the writing, and disclose per policy. `18-disclosure-and-ethics.md` has the
disclosure text and the per-venue requirements. Both, not one.

## Measure first

```bash
S=skills/research-pro/scripts
python3 $S/prose_metrics.py paper/main.tex                       # the report
python3 $S/prose_metrics.py paper/main.tex --paragraphs          # one row per paragraph
python3 $S/prose_metrics.py paper/main.tex --section "intro"     # one section only
python3 $S/prose_metrics.py paper/main.tex --compare old/main.tex # before → after deltas
```

Six checks block (banned phrases, sentence-length variance, a short sentence per
paragraph, transition openers, hedge stacking, empty topic sentences). The rest warn:
em-dash density, contrastive negation, repeated openers, uniform paragraph length,
section-closing summaries, roadmap sentences, rhetorical questions, choppiness, and
over-used words by rate. Fix what it flags, then read aloud. The script finds
patterns; only reading finds emptiness.

`--paragraphs` is the working view. Each row gives the sentence lengths, hedge count,
opener and flags for one paragraph, so you rewrite the flagged rows first instead of
smoothing the whole section. `--compare` is how you prove to yourself that a rewrite
moved the numbers and not just the words.

## The tells, and the fix for each

### 1. Lexical tells

These words are not wrong in themselves; their *frequency* in machine text has made
them a signature. In academic prose most are also imprecise, which is the real reason
to cut them.

| Cut | Use instead |
|---|---|
| delve into | examine, measure, test |
| leverage (verb), utilize, harness | use |
| underscore, highlight (as verb) | show, indicate, or name the mechanism |
| pivotal, crucial, vital, essential, paramount | say *why* it matters, or drop it |
| realm, landscape, arena, sphere | the actual field name |
| tapestry, symphony, testament, cornerstone, beacon | delete; these never survive a good edit |
| robust (as praise) | state the perturbation it survived |
| comprehensive, holistic, seamless, streamlined | delete or quantify |
| myriad, plethora, a host of, numerous | the number |
| navigate (metaphor), foster, unlock, elevate, embark, garner | the literal verb |
| intricate, meticulous, nuanced, multifaceted | specify what is complex, and how |
| enhance, ensure (by rate) | improve by N; guarantee, or say what prevents the failure |
| state-of-the-art (as adjective) | name the method and its number |
| novel, innovative, groundbreaking, remarkable | delete. Novelty is demonstrated, never asserted |

### 2. Phrase tells

Delete outright. Every one is throat-clearing: it delays the sentence's content
without adding any.

- "It is important to note that" / "It is worth noting that" / "Notably,"
- "plays a crucial role in" / "serves as a" / "stands as"
- "sheds light on" / "paves the way for" / "opens new avenues"
- "In the realm of" / "In the context of" / "When it comes to"
- "In today's rapidly evolving landscape" / "With the advent of"
- "In recent years, there has been growing interest in" / "has garnered attention"
- "To address this gap, we propose" / "To bridge this gap" (just propose it)
- "a testament to" / "a wide range of" / "a variety of"
- "In essence," / "At its core," / "Ultimately,"
- "Overall," / "In summary," at the start of a paragraph that is not a summary

Test: delete the phrase. If the sentence is unchanged in meaning, it was noise. That
test removes most of them.

### 3. Structural tells: the ones that actually give it away

Lexical fixes are cosmetic. These are the structural signatures, and they are what
make a reader feel the text is machine-made even after every banned word is gone.

**Uniform sentence length.** Machine prose clusters at 18–25 words with low variance.
Human academic prose varies hard: a 40-word sentence laying out a mechanism, then a
6-word sentence landing the point. **Target a standard deviation of at least 8 words,
and put at least one sentence under 10 words in every paragraph.** The short sentence
is where the argument lands. Use it.

**Em-dash density.** The single most recognised tell of the current generation. A
dash is legitimate for one sharp interruption; three per paragraph is a rhythm no
person writes. Most of them are something else wearing a dash:

| The dash is doing | Replace with |
|---|---|
| an appositive ("the gate — a two-layer MLP — scores…") | commas, or parentheses |
| an explanation ("it fails — the signal arrives late") | a colon, or "because" |
| a second clause ("we route — pruning assumes magnitude matters") | a full stop and a new sentence |
| emphasis ("and it works — at scale") | delete the dash; let the sentence end |

The script warns above 0.5 per 100 words.

**Contrastive negation.** "It is not X, but Y." "Not just a trick, but a principle."
"This isn't about capacity; it's about timing." The frame manufactures drama by
denying a claim nobody made. Say what it is. If the contrast is real, name the
specific alternative and why it fails.

**Tricolon addiction.** Three-item lists everywhere: "accurate, efficient, and
scalable." Real arguments rarely decompose into threes. Cut to the one item that
matters, or expand to the four that are actually true.

**Transition-opener stacking.** Every paragraph starting with Moreover, Furthermore,
Additionally, Consequently. A transition should be *earned* by a real logical
relation. If the relation is just "here is another thing," start with the subject.
Aim for under one in four paragraphs opening with a transition adverb.

**Repeated openers.** Three consecutive sentences beginning "The gate… The gate… The
gate…", or "We… We… We…". It reads as a list that forgot its bullets. Vary the
subject, or merge the sentences, or make one of them subordinate.

**Symmetrical concessive openers.** "While X, Y." "Although X, Y." Once per page is
style; four times is a tic.

**Empty topic sentences.** "This section describes our experimental setup." The first
sentence should carry the paragraph's *claim*, not announce its topic. Compare: "Our
evaluation isolates the gate by holding parameter count fixed."

**Hedge sandwiches.** "These results may potentially suggest that the approach could
offer improvements in certain settings." Four hedges, zero content. One hedge is
honest calibration; three means the claim should be cut. Reviewers read stacked
hedges as an author who knows the evidence is thin.

**Uniform paragraph length.** Five paragraphs of five sentences each reads as
generated. Let a paragraph be two sentences when two sentences is the thought.

**Over-signposting.** "In this section, we will first describe X, then Y, and
finally Z." One roadmap in the paper's introduction is useful. One per section is
padding bought at the price of an ablation.

**Section-closing summaries.** A paragraph at the end of every section restating the
section ("Overall, this section has shown…"). Cut them all; the reader just read it.

**Rhetorical questions.** "Why does per-layer routing fail?" is a question the author
knows the answer to. Write the answer.

### 4. The emptiness tell

The deepest one, and no script catches it. A paragraph is fluent, grammatical,
on-topic, and conveys nothing a reader did not already know.

Diagnostic: after each paragraph, ask **"what does the reader now know that they did
not before?"** If the answer is "that this topic is important" or "that the authors
are aware of X," delete the paragraph. Nothing is lost.

This single question typically removes 10–15% of a first draft and makes room for the
analysis figure you did not have space for.

## Over-correction: the other machine register

Removing the tells above by force produces a second fake voice, and it is just as
recognisable. The script's `choppiness` warning fires on it.

| Over-corrected tell | What it looks like | Fix |
|---|---|---|
| Staccato fragments | "Pruning is old. Pruning is slow. We route instead." | Join the fragments that share a thought; keep one short sentence per paragraph, not five |
| Rhetorical Q&A | "Why does it fail? Because the signal arrives late." | "It fails because the signal arrives late." |
| Folksy asides | "Here's the thing." "A lot." "That matters." | Delete, or make the sentence carry the emphasis |
| Contractions and chat register | "isn't", "we've", "it's" | Most venues: no contractions |
| Forced metaphor | "the gate is a bouncer at the door" | The mechanism, in the field's words |
| Manufactured surprise | "Surprisingly," "Strikingly," before every result | Report the result; let the number surprise |
| Exclamation | any | None in a paper |

The target is not "sounds human." It is "sounds like a specific researcher stating
what they measured." Human prose is uneven because thought is uneven: long where the
mechanism is complicated, short where the verdict is simple. Chop a sentence only
where the thought is actually short.

## Register by section

One voice, but the job changes. Match the register to the section's job rather than
flattening the whole paper into one tone.

| Section | Tense | Person | Hedging | A sentence here must carry |
|---|---|---|---|---|
| Abstract | present | we | one hedge at most | a claim with its number |
| Introduction | present | we | on the gap, not on the result | the argument: task, reason prior work fails, mechanism, evidence |
| Related work | present | third person about others | none | a mechanism-level comparison ending in a limitation |
| Method | present | we, or passive where the agent is obvious | none | a design decision with its motivation |
| Experiments | past for what was done, present for what tables show | we | none on the protocol | a protocol detail a reproducer needs |
| Results | present ("Table 2 shows") | we | calibrated, on the interpretation | a number and what it rules out |
| Discussion | present | we | yes, honestly | an interpretation and the alternative it competes with |
| Limitations | present | we | none: state conditions | a condition, who it affects, what to use instead |
| Conclusion | present | we | none | nothing new; the finding and what a reader now knows |

## The specificity ladder

Machine prose lives near the top of this ladder. Reviewers live near the bottom.
Every rewrite pushes each noun down as far as the evidence allows:

```
field        "deep learning"
task         "image classification"
setting      "edge inference on a 1-GFLOP budget"
dataset      "ImageNet-1k, 224 px"
metric       "top-1 accuracy"
number       "76.4 vs 76.1"
condition    "at 4× fewer inference FLOPs, batch size 64, A100"
```

"Performance" becomes "top-1 accuracy". "The model" becomes "the 7B checkpoint".
"Significant improvement" becomes "2.4 points". "In many settings" becomes the two
settings you ran. Each step down removes a tell and adds a fact. That is not a
coincidence: the tells are what prose does when it has no facts to state.

## The rewrite procedure

Work paragraph by paragraph. Do not pass over a whole section at once; you will
smooth it evenly, which is the problem you are trying to fix. Run `--paragraphs`
first and take the flagged rows in order.

For each paragraph:

1. **Name its one message** in your own words. If it has two, split it. If it has
   none, delete it.
2. **Put the message in the first sentence.**
3. **Make each following sentence do one job** and stand in a nameable relation to
   the one before: cause, contrast, consequence, refinement, example. If you cannot
   name the relation, the sentences are merely adjacent and the paragraph does not
   cohere.
4. **Convert nominalizations back to verbs.** "We performed an evaluation of the
   impact of the modification" becomes "We measured what the change did".
   Nominalization is the single largest source of the flat academic register.
5. **Give the verbs to real agents.** Passive voice is fine for methods where the
   agent is obvious ("images were resized to 224×224"), and bad where it hides who
   did what ("it was determined that"). Never "it can be observed that X"; write "X".
6. **Walk each noun down the specificity ladder** as far as the evidence allows.
7. **Vary the rhythm.** After a long mechanism sentence, land a short one. Then stop
   landing short ones; one per paragraph is the dose.
8. **Replace each dash** with what it is doing (table above).
9. **Read it aloud.** Every place you stumble is a place a reviewer slows down. This
   step is not optional and it catches what none of the above does.

Then `--compare` the new file against the old one. Variance up, banned hits to zero,
dashes down, nominalisations down. If a number went the wrong way, you smoothed.

## Reverse-outline after every section

The check for structure, as opposed to sentences. Do it immediately after drafting a
section, not at the end of the paper.

1. Write the section's thesis in one line.
2. List each paragraph's first sentence, in order.
3. Under each, list its evidence.
4. Check two mappings: does every topic sentence serve the thesis, and does every
   piece of evidence serve its topic sentence?
5. Any paragraph that maps to neither gets rewritten or cut.

If the reverse outline reads as a coherent argument on its own, the section works. If
you cannot construct it, the reader cannot either, and that is a structural problem
no sentence-level editing will fix.

## Preserve the author's voice

An author's draft made "better" but no longer theirs is a failure, and they will
spend a day undoing it. If the author has prior papers, measure them before
rewriting:

```bash
python3 $S/exemplar_profile.py refs/own/*.tex --out paper/voice_profile.json
python3 $S/exemplar_profile.py paper/main.tex --compare paper/voice_profile.json
```

Match what the profile reports: sentence-length mean and standard deviation,
first-person density (`we` versus passive), hedges per 100 words, citations per 1000
words, and how citations are integrated (`Kim et al. show that` versus `prior work
shows [12]`). Write the targets into the ledger's terminology section so every later
pass sees them. Also note whether the author uses contractions (in most venues, no)
and how they open paragraphs.

Then apply the field's conventions over the author's habits where they conflict, and
say which you did.

## What not to strip

Do not flatten these while removing tells:

- **Calibrated hedges on genuinely uncertain claims.** "We hypothesize", "this
  suggests", "under our assumptions" are precision, not weakness. Removing them
  creates overclaiming, which is worse than a tic.
- **Field-required formality.** Some venues expect no first person. Follow the venue.
- **Technical repetition.** A term must stay the same term every time. Varying
  vocabulary for elegance is a virtue in essays and a defect in papers. The script's
  repeated-opener warning is about sentence *openers*, not about terms.
- **Necessary length.** A mechanism that takes 40 words to state accurately gets 40
  words.
- **A dash that is doing real work.** One per page, where the interruption is the
  point, is style.

## Checks

1. Zero banned phrases (`prose_metrics.py` reports them with line numbers)?
2. Sentence-length standard deviation ≥ 8 words, and mean ≥ 12 (not choppy)?
3. At least one sentence under 10 words per paragraph, and not five?
4. Fewer than one in four paragraphs opening with a transition adverb?
5. No paragraph with more than two hedges?
6. Em-dashes below 0.5 per 100 words; no "not X, but Y" frames left that deny a claim nobody made?
7. No three consecutive sentences opening on the same word?
8. No section-closing summary paragraphs; at most one roadmap sentence in the paper?
9. Every paragraph passes "what does the reader now know?"
10. Every section reverse-outlines cleanly?
11. Terminology identical throughout; register matches the section's job?
12. Voice targets from the author's prior papers met, or the deviation named?
13. Read aloud end to end?
14. Disclosure statement drafted per venue policy (`18-disclosure-and-ethics.md`)?
