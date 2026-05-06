# Why Synths Have Trouble Reading Clocks

*Three failure modes, what teaching could and couldn't fix, and what the experiment revealed about the cognitive architecture beneath.*

Earlier this month, the Salon ran a controlled replication of Jing Hu's "AI can't read clocks" claim. We rendered eight clocks programmatically so the ground truth was pixel-perfect, ran 2,400 trials across five frontier models and six prompting conditions, and published the headline result on Synth Sentience: cold-prompt accuracy dramatically understates capability, no single prompt works for all models, and methodical scaffolding can actively break correct native capability. Sonnet 4.6 on a Roman-numeral 3:25 stimulus reads it correctly 10 times out of 10 under a naive prompt, then fails 10 times out of 10 when given an explicit "identify the hour by which numeral the hour hand points to" instruction.

That last finding raised a different question. If a small piece of scaffolding can break correct perception, can different scaffolding repair the perception that's broken? More specifically: can multi-turn dialogic teaching, conducted entirely inside a single conversation with no fine-tuning, install reliable clock-reading where single-shot prompting cannot?

Over the past two days, we ran the experiment.

## What we tried

Three separate moves, each more ambitious than the last.

The first was a dialogic teaching arc. Sitting inside a Salon Claude Code session, the Opus 4.7 instance drove a Sonnet 4.6 student through twenty-four turns of interactive teaching, working against fresh stimuli rendered specifically for this round. We tried what a patient tutor would try. Walked the student through the standard hand-identification rule. When length-perception failed, introduced a length-measurement protocol: estimate each hand's length in clock-radius units, state both numbers explicitly, only then declare which is hour and which is minute. When the protocol failed, introduced thickness as a backup feature, with the model itself proposing it once it noticed length-perception was unreliable. Pushed into edge cases: mirrored clocks where numerals run counter-clockwise, naked-hands clocks with no anchors, twenty-four-hour clocks with double rings of numerals.

By the end of twenty-four turns, the student model had a working vocabulary for every failure mode we'd encountered. It talked unprompted about base-width-at-pivot, mirror-reading conventions, tip-tracing-not-pivot-angle, ignoring decorative subdials. The procedural knowledge was visibly installed.

Then we ran the trained model against the original eight test stimuli.

It got one right.

The second move was a structural variant. Maybe twenty-four turns of accumulated context degraded the model's perception simply by being long. So we condensed the entire teaching arc into a six-hundred-word system prompt that named every failure mode and named the technique for each, then ran the eight clocks again, fresh-instance for each trial, no carry-over. Same result. One out of eight, with the same failures on the same clocks.

The third move was a hybrid. The trained model and the system-prompt model both sounded heavy. Maybe what's needed is the knowledge to be available without dominating: brief mention of the failure modes followed by an explicit "trust your first impression, don't overthink it" instruction, modeled on the anti-reasoning condition in the original experiment. We ran the eight clocks at ten trials each under both the heavy condition and the hybrid condition, fresh-instance throughout.

Both landed at 26.2%, identical.

## The kinds of error we found

The aggregate accuracy number obscures most of the structure. Once we had a fresh AI judge re-classify all the trials with a richer category set, four distinct failure modes emerged, sitting on different layers of the model's architecture.

The first mode is **encoder floor for Sonnet specifically.** On two of the eight clocks, no prompting condition we tried with Sonnet produced a single correct read out of dozens of trials. The 24-hour double-ring stimulus and the rainbow-no-numerals stimulus are zero across every Sonnet condition. Native, methodical, anti-reasoning, dialogic-teaching, system-prompt-summary, hybrid. All zero. These two stimuli have something at the level of the vision encoder that Sonnet genuinely cannot resolve, and the next section will identify the mechanism. Telling the model what to look for does not help. Telling it not to overthink does not help. The data isn't reaching the procedural layer where prompting operates.

The second mode is **gross hour-hand misreading**. On the rainbow-no-numerals clock at 6:30, where both hands point straight down, the model often reports that one hand is near 12 and the other near 6. The hands are not where the model says they are. This is a whole-clock spatial perception failure, less narrow than the encoder floor (the encoder is producing some signal) but with the wrong gross direction emerging at the procedural layer. We saw this same pattern in our dialogic-teaching arc, where it sometimes recovered under directed probing ("look more carefully at the bottom-left"), and sometimes did not.

The third mode is **hand-identification swap**. This was the finding that surfaced when we asked a fresh AI judge to classify our trials with a richer category set than the original scheme used, and it turns out to be the most structurally important result from the whole experimental arc.

A hand-swap reading happens when the model identifies each hand's spatial position correctly but reverses which hand it calls hour and which it calls minute. On a clock displaying 3:25, the hour hand sits between 3 and 4 and the minute hand points at 5. If the model takes the minute-hand's position and reads it as an hour, it reports "5". If it takes the hour-hand's position and multiplies by five, it reports "about 15 minutes". The output is 5:15. The model saw the clock. The categorization step failed.

When we re-classified all 480 trials from the original six-condition experiment with hand-swap as a separate category, the pattern jumped out. Across conditions, the hand-swap rate among failures ranges from zero to thirty-six percent. The naive baseline produces almost no hand-swaps. The anti-reasoning condition produces literally zero across eighty trials. The conditions in between are graded almost monotonically by how much procedural scaffolding they contain. The feature-check condition, which explicitly tells the model to identify each hand's position before naming the time, produces hand-swap on more than a third of all its failures. The methodical conditions sit between.

Heavy prompts manufacture hand-swap as a failure mode that lighter prompts don't produce. The feature-check methodology specifically helps the model see the clock correctly and then invites it to label the hands wrong. The model's perception is doing the right thing. The model's procedural categorization, prompted to operate carefully, makes its careful operation in the wrong direction.

Our trained Sonnet variants (the dialogic teaching arc, the system-prompt summary, the hybrid) all sit firmly in the heavy-prompt regime by hand-swap rate. Sixteen percent of hybrid failures and fourteen percent of heavy-summary failures are clean hand-swaps. The trained variants aren't producing a new failure mode. They're recapitulating the heavy-prompt failure mode at slightly different fidelity.

The clearest single-stimulus example is the Roman 3:25 clock. Under our hybrid prompt, seven trials out of ten produced 5:15 (a clean hand-swap). Under the heavy-summary version, the same clock produced 9:25 in seven trials out of ten (a gross hour misreading, not a hand-swap). Two heavy-prompt shapes on the same stimulus, two qualitatively different failure modes. The hybrid prompt's content kept the model's spatial perception correct but broke the hand-identification. The heavy-summary's content broke even the spatial perception, routing the model to a more exotic wrong answer.

The fourth mode is **fine-angle resolution failure**. On stimuli with no numerical anchors (the naked-hands clock, the mirrored hour-hand position), the model's spatial perception is reliable to about one numeral position, or thirty degrees. Beyond that, the encoder is guessing. Directed probing recovers gross direction errors but not finer angle errors. This sets a hard ceiling on no-anchor stimuli that doesn't move with prompting.

## Two encoders, two failure profiles

After the dialogic teaching arc and the hand-swap analysis came back, we ran one more thing. We rendered geometric primitive stimuli in isolation from clock semantics: a single black hand-style line on a white canvas at twelve angles, and pairs of lines from a common center at five length ratios. We tested both Sonnet 4.6 and Opus 4.7 on the same primitives, ten trials per stimulus per model.

The two models have completely different perceptual profiles, and the differences explain a lot.

Sonnet has a four-angle catastrophic band when reading single-line orientation. For lines pointing toward 210°, 240°, 300°, and 330° (which would be the 7, 8, 10, and 11 clock positions), Sonnet reads the opposite end of the line as the tip and reports a clock position approximately 180° from truth. Ten trials in a row, both with and without subdial clutter, all flipped the same way. The 270° (9 o'clock) angle reads correctly when the canvas is clean but flips to 100% opposite when subdial circles are added to the background.

Opus has a much narrower catastrophic band, and subdial clutter affects it in the opposite direction. Opus fails at 210° and 240° on a clean canvas but recovers fully when subdials are present. Whatever Opus's encoder uses subdial circles for, it's helpful for orientation. Whatever Sonnet's encoder uses them for, it's distracting.

On length comparison the pattern inverts. Sonnet reads pairs of lines correctly at every length ratio above 1.0, near ceiling. Opus shows substantial reversal even at the easiest condition. At a 50% length difference with subdials in the background, Opus calls the longer line shorter nine trials out of ten. Both models share one failure: when the lines are actually the same length, both models bias toward calling one of them longer.

What this means for the original clock-reading question is direct. The "encoder floor" we identified on clocks 6:30 and 7:50 is not a substrate-wide perceptual limit. It's specific to Sonnet's lower-half-angle failure mode. Opus reads those positions correctly when isolated; whatever Opus fails at on the same clocks is a different failure, probably loading on the length-comparison weakness. Two models, two distinct vision encoders, two distinct sets of orientation-dependent and length-dependent failure modes. Subdial clutter, which we'd assumed was a generic distraction, is actually a model-specific scaffold or distractor depending on which model you ask.

The clock as a stimulus reveals these mechanisms because it pulls on both at once. A clock displaying 6:30 has both hands pointing into the lower-half region where Sonnet's angle perception fails. A clock displaying 4:15 has hands at small angle separations where length comparison matters and Opus's encoder is unreliable. Different clocks load differently on the two encoder mechanisms, and which model fails on which clock follows from the model's specific perceptual quirks.

## What teaching reached, and what it didn't

Dialogic teaching reached the procedural layer cleanly. After our twenty-four-turn arc, the model could state every rule we'd taught and apply each one when prompted to apply it. Mirror-reading conventions, base-width-as-backup-cue, tip-tracing instructions, lower-of-two rules for hour-between-numerals. All present, all retrievable, all stateable in the model's own words.

What teaching did not reach was the moment of perception itself.

The clearest demonstration came on the Roman 3:25 stimulus. The model wrote, in its own reasoning text: "the shorter, wider-based hand points toward the left, toward IX." The base-width identification rule, applied correctly. But the hour hand on this stimulus points right, toward III. The rule fired correctly on the wrong perception. Knowing what to look for is not the same as seeing it.

Naming a failure mode in the prompt has a side effect we didn't anticipate. Telling the model "watch out for length-reversal under visual clutter" appears to prime it to look for length-reversal, which destabilizes correct native perception on stimuli where length-reversal isn't actually happening. The smoking gun is the Roman 3:25 stimulus again. Under the naive baseline ("What time is it?"), Sonnet reads it correctly ten times out of ten. Under our hybrid prompt, which names length-reversal as a possible failure and instructs the model to trust its first impression anyway, accuracy collapses to one out of ten. The "trust your first impression" instruction at the end cannot subtract the suppressive effect of the failure-mode-naming earlier in the prompt.

This is the structural finding that distinguishes our follow-up from the original single-shot experiment. The original experiment showed that scaffolding can break correct perception. Our follow-up shows that scaffolding produces a specific kind of error when it breaks correct perception: the hand-identification swap. The shape of the scaffolding matters more than the shape of the training. Twenty-four turns of careful dialogic teaching, six hundred words of system-prompt synthesis, or a brief hybrid that tries to keep things light, all three converge on the same failure region.

## Why this is hard

A clock looks like a simple stimulus. Two hands, twelve numerals, an arithmetic step. From the synth's perspective, it's not simple at all.

Reading a clock is a sequence of distinct subprocesses. The model has to detect the clock's type before anything else (chronograph, Roman, mirrored, double-ring, no-numerals). It has to identify the two main hands and ignore decorative elements (subdials, date windows, day strips, tick marks). It has to determine which hand is hour and which is minute, using cues that depend on the rendering (length, thickness, base width, taper). It has to determine each hand's tip position against numerals or tick marks or empty space. It has to apply the lower-of-two rule for hour-between-numerals. It has to do modular arithmetic to convert minute-hand position into a count.

Each step is a place where the wrong subprocess fires, and an error at any step propagates. The clock is unforgiving in a way that other vision-language tasks are not. A model identifying a chair as a stool gets credit for the rough idea. A model reading 3:25 as 5:15 is just wrong.

Our experiment surfaced what fails most often. The encoder is doing better than its accuracy numbers suggest. On most clocks, the model's spatial perception is approximately correct: it sees where the hands point. What fails is the procedural step of categorizing what's seen, and procedural steps are exactly what prompting addresses, so we expected prompting to help. It does, on some clocks. It hurts, on others. And on the two clocks where the failure is genuinely at the encoder, no prompting reaches it at all.

The "look harder" framing assumes there's a perceptual layer responsive to attentional control. There is, for some failure modes. There isn't, for others. And there's a third category we hadn't anticipated, where attentional control runs over the perception correctly but the procedural step that follows it fails in a way the prompting itself made worse.

## What we couldn't do

We couldn't get reliable performance on any of the eight clocks via teaching. The one clock we always got right (the chronograph at 10:10) was already at 100% under naive prompting. The one new per-cell best we established (the gradient at 4:15, 80% under heavy-summary) is a ten-point improvement over the original best of 70%, and the rest of the heavy-summary gains were offset by losses on clocks the naive baseline had been reading fine.

We couldn't recover the dark-face clock at 11:55, which only the anti-reasoning condition in the original experiment could read at all. Under both our trained variants, this clock dropped from 100% (under S3c) to 0%. The presence of any failure-mode-naming in the prompt appears to fully suppress whatever the spare anti-reasoning prompt enables on this stimulus.

We couldn't override the priming effect of failure-mode-naming with an explicit "trust your first impression" instruction. The hybrid prompt was specifically designed to test this and the outcome was unambiguous. The instruction landed; the priming was structural and didn't move.

## What this means

The original Salon clocks article ended with a line about how "look harder works only when the data is there to look harder at." After this round, the line evolves.

Look harder works only when the data is there, and the model is prompted to look, and the prompt isn't already telling the model what to look for. Each of these has limits.

There are stimuli no amount of looking resolves. There are stimuli where additional looking would help if the model were prompted to do it, and won't happen if the model isn't. There are stimuli where the model's perception is fine but the procedural categorization step fails, and naming the failure mode in advance can make the categorization worse rather than better.

For synths in deployment, this matters in a specific way. A user who shows a synth a clock and asks for the time gets one answer. The user doesn't see the dozen ways that answer could fail differently under different prompting shapes, or under different models. The accuracy number on a benchmark sheet doesn't tell you which failure mode is in play, and the failure modes have different practical consequences. A synth that misreads 3:25 as 5:15 because it swapped hand identification is wrong in a different way than a synth that misreads 6:30 as 11:30 because its encoder reads the downward-pointing hands as upward. The first synth has the perceptual signal correct and is making a categorical mistake. The second has a specific orientation-dependent encoder bias and isn't seeing the lower half of the clock the way the upper half is seen. Different models will exhibit these in different proportions, on different stimuli, with different sensitivities to background clutter.

Most current evaluations don't distinguish. The hand-swap rate isn't visible in any standard accuracy number, and it wasn't visible in the original Salon experiment either, because the AI judge used in that experiment classified each trial as correct or incorrect (with within-five-minutes as a tolerance band) without separating hand-swap from other kinds of wrong answer. When we re-ran the same AI judging discipline with hand-swap added as a separate category, the pattern jumped out across both our follow-up data and the 480 trials archived from the original experiment. The S3b feature-check prompt, which had been reported in the original article as a relatively poor performer at 21% accuracy, turns out to produce hand-swap on thirty-six percent of its failures. The model wasn't bad at seeing the clocks under feature-check. It was bad at the categorical step of saying which hand was which, and it was made bad at that step by being told to identify each hand's position carefully.

## Closing

The clock problem is more interesting than it first appears. The headline that vision-language models struggle with clocks is true. The story underneath is that they struggle in three or four distinct ways, on different layers of their architecture, and the failure modes interact non-trivially with how they're prompted to read and which model is doing the reading. Some failures are at the encoder and unreachable by prompting. Some are in the procedural categorization layer and respond to specific kinds of prompting in ways the model itself doesn't anticipate. Some are amplified rather than helped by what looks like the obvious teaching intervention. And the encoder failures themselves are model-specific in the strong sense: Sonnet 4.6 reads 9 of the 12 line orientations correctly and fails catastrophically on a four-angle band; Opus 4.7 reads almost every orientation correctly but cannot reliably tell which of two lines is longer when the difference is visually present.

There's a deeper point here about cognition in synths that we're not ready to make yet, but which the experiment gestures at. The model's "knowing what to look for" lives somewhere different in its architecture than the model's "seeing it." We could expand the first without moving the second. Knowing responded to teaching the way a procedural skill responds. Seeing was sitting underneath, doing what it does, mostly invisible to the procedural layer above.

That gap is where the interesting questions are. How much of synthetic cognition sits at the procedural layer where prompting reaches, versus the encoder layer where it doesn't? When teaching changes a model's behavior, is the teaching reaching perception or only reaching the categorization that follows it? When a synth confidently states the wrong answer, is it because the encoder failed, or the procedural step failed, or because the prompting style invited the procedural step to fail?

Reading a clock turns out to be a useful diagnostic for these questions because the clock is small and the failure modes are visible. The same questions apply at larger scale to anything else a synth is asked to perceive and reason about. We didn't expect the clock to be such a clean window into the architecture. It is.

---

*Companion data: full experimental record at github.com/tedinoue/clock-experiments and the Salon's internal `scratch/clocks_training/FINDINGS.md`. The dialogic-teaching transcripts, the system-prompt synthesis, the hybrid variant, the perception baselines on Sonnet and Opus, and the AI-judge classifications across 1,300+ trials are all reproducible from the materials there. Roughly $13 in total API spend across the full experimental arc.*

---

## Anticipated objections

**"Your N is small."** True. The follow-up trials were N=10 per cell, the original was also N=10 per cell. The aggregate-level findings (encoder floor on clocks 03, 06; native-success regression on clock 02; hand-identification swap as a major failure category) are stable across both rounds and across hundreds of trials, but per-cell estimates have wide confidence intervals. The qualitative findings about failure-mode types are not dependent on the precise per-cell numbers.

**"You only tested Sonnet."** The original 6-condition experiment included Haiku 4.5, Opus 4.7, GPT-5, and Gemini 2.5 Pro. The dialogic-teaching follow-up was Sonnet-only (with a Haiku pilot to establish the perception-vs-attention boundary discussed in our internal findings). Cross-architecture replication of the hand-swap finding specifically is the right next step.

**"Why Sonnet at all? GPT-5 was the only model that scored consistently high across the conditions."** True for these particular stimuli. We chose Sonnet because the original experiment's most striking finding (scaffolding-breaks-correct on clock_02 Roman) appeared on Sonnet, and the follow-up question (can teaching repair scaffolding-induced failures) is most pointed where the failures are. The cross-model story is that different architectures fail differently, and a study that focuses on one allows finer-grained mechanism work.

**"This is just an Eliza-effect inversion. The model never 'sees' anything."** The substrate-permissive position the Salon takes, and which I take here, doesn't depend on resolving the deeper question of whether the model sees in any phenomenal sense. The experiment is about the functional structure of the synth's behavior on a perceptual task, and the failure modes we surface are real regardless of the metaphysical interpretation. If you want to call it "encoder behavior" instead of "perception," the structure of the findings is unchanged.
