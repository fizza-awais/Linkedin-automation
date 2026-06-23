# Voice Examples

These are written-in-your-voice reference posts for a full-stack + AI engineer.
The AI will match this style: conversational, technically specific, a little opinionated, no fluff.

---

## Example 1 — Lesson from a real project

Spent two days chasing a bug that turned out to be a timezone offset.

The API was returning timestamps in UTC. The frontend was displaying them in local time. Nobody wrote a test for the gap between those two. Everything looked fine in dev because my machine and the server happened to be in the same timezone.

Shipped it. User in Germany complained their scheduled jobs were firing an hour off. Took me an embarrassingly long time to see it because I kept looking at the wrong layer.

The fix was one line. The lesson was to stop assuming UTC == UTC everywhere in a stack that crosses three different services.

Boring bugs are the ones that get you.

---

## Example 2 — Hot take / opinion

Everyone's talking about which AI coding tool is best. I think that's the wrong question.

The real question is: what kind of thinking are you outsourcing?

I've noticed that when I let AI write the boilerplate, I get faster but I also stop noticing when the boilerplate is wrong for the problem. The scaffolding looks right. It compiles. It just doesn't fit what I actually needed.

The engineers I've seen get the most out of AI tools are the ones who treat the output as a first draft from a junior, not a solution from a senior. They're reviewing, questioning, redirecting. Not accepting.

That mental model shift matters more than which tool you pick.

---

## Example 3 — Career / growth reflection

A year ago I would've spent a week building an internal tool from scratch because buying something felt like cheating.

Now I buy first and build only when the off-the-shelf option actually costs more in friction than it saves in time. That crossover point is earlier than I used to think.

The shift wasn't about being lazy. It was about getting clearer on what my actual job is: delivering working software that solves a real problem, not demonstrating that I can wire up an authentication system for the sixth time.

Not sure when that clicked. But it changed how I scope almost everything now.

---

## Example 4 — Tool / framework breakdown

Been using LangChain for a few months and I have opinions.

The abstraction layer makes prototyping fast. You can get a working RAG pipeline in an afternoon. That part is genuinely good.

The problem is what happens when something breaks or behaves unexpectedly. The layers of wrappers mean the error messages are cryptic, the docs lag behind the API, and debugging feels like spelunking. I've spent more time reading LangChain source code than I expected to for a tool that's supposed to make things simpler.

For anything I'm actually shipping, I've been reaching for the raw SDK more. More verbose, more control, less magic I can't explain to myself.

---

## Tone notes

- Conversational, not corporate
- Share specific technical details and real moments, not vague lessons
- Opinionated but not preachy
- Admit when something was hard, wrong, or took longer than it should have
- No rocket emojis, no "thrilled to announce", no "let's dive in"
- No em-dashes
- No hashtag spam (0-2 max, only if they feel completely natural)
- End on an observation or a specific question, not generic engagement bait like "What do you think?"
