# The Complete Guide to pstack Pt. 2

By [lauren (@poteto)](https://x.com/poteto)

Published: 2026-09-09

Source: [https://readwise.io/reader/shared/01m243y0ncj3se4cjvtpemv95c](https://readwise.io/reader/shared/01m243y0ncj3se4cjvtpemv95c)

---

![](https://pbs.twimg.com/media/HRK8DfAbEAEt18A.jpg)

In my [last post](https://x.com/poteto/status/2094457600259842065), I showed you why verification is the foundation of everything I do with agents, and how to get started creating your own verification skills. The key lesson was that if an agent can't verify its own work, nothing else matters. You remain the bottleneck, and your whole day will be spent babysitting your agents.

![](https://pbs.twimg.com/media/HQ_0MA_aMAA9zMt.jpg)

In this series of posts, I'm going to show you how I use **[pstack](https://x.ai/bot/plugin/9717366)**, my personal set of skills for doing rigorous engineering work. It's allowed me to ship 2,000 PRs a month to production with high confidence.

![](https://pbs.twimg.com/media/HRD9GflbQAAKEXZ.jpg)

Personally, I have never put much emphasis into how many lines of code or how many PRs I was landing. Before agents, no one cared, and rightfully so, as raw productivity did not always equate to quality or a visible outcome for users. It was simply a vanity metric.

But I've discovered through the course of building **pstack** that volume does matter, especially when you are able to maintain or even increase the level of quality of the product with agents. For example, I started working on Grok @Bot about 2 months ago, when it was still in its early days and the codebase was fresh but starting to grow. Despite the team growing and now landing hundreds of PRs a day into the Grok @Bot codebase, **pstack** has allowed me to keep the quality of the code high for everyone as I constantly monitor code, refactor, add new lints and checks, and also work on features.

every team needs a gardener. someone quietly watching the stream of PRs flowing into your codebase, noticing the smells: the third isRecord this week, the lint suppressions creeping like ivy across your carefully planned garden. a steady hand tending the weeds that would engulf it in slop if left unchecked.

with careful grooming it stays a garden. every weed you pull becomes a rule, so it can't grow back. without that, it's just whatever grew.

**organic architecture**

good codebases have always had strong foundations and constraints. these files go here. this kind of code goes there. the codebase is held together either by catering to the lowest common denominator developer using conventional frameworks and languages, or by strict adherence to a style guide enforced by code review.

the arrival of an infinite number of monkeys armed with keyboards have obsoleted the latter. codebases designed for agents need hard constraints so that even the dumbest agent (and pilot) can contribute meaningfully. the chaos must be tamed.

refactoring your codebase and choosing a tech stack with strong type systems/compiler diagnostics has far greater impact than [AGENTS.md](http://AGENTS.md) and tweaking your skills. hard constraints and well thought out architecture guide agents to do the right thing by default. the best rules are in your code.

invest accordingly.

![](https://pbs.twimg.com/media/HNhmhvcaMAA2KyA.jpg?name=orig)

Being Grok @Bot's gardener and maintainer is something I was only able to do through **pstack**. Our early momentum after building the prototype was very high and many people were joining the team. I had a critical moment of opportunity to refactor the whole codebase, while it was being built and extended and with no downtime, into something with strong foundations. A codebase with high quality that scales no matter how many engineers (and most importantly, non-engineers) contribute to it. All of this work requires me to refactor and improve the foundations of Grok Bot as it's being built, and you can only do that when the foundations can keep up with the number of contributions.

![](https://pbs.twimg.com/media/HRACOM4awAAPxUR.jpg)

The proof is in Grok @Bot itself. Over the next few weeks, I'll tell you everything you need to know to be able to build and maintain a high quality app using **pstack**.

## Part 1 – Verification is all you need

The most critical skill to have in your toolbox is a high quality verification skill. This skill is so important to have and maintain that I think of it more like critical infrastructure rather than "just" a skill. A good one will amplify the output of your whole team, including non-engineers. Done well, you will 100-1000x your whole team's output.

If you're not familiar with the term, *verification* means that an agent can verify its own work. It can keep going until it succeeds at its task, because it can now close the loop without you being the bottleneck. If you're interested to know more of the story of how I created my first verification skill for Cursor, check out my previous post *[Loops You Can Trust](https://x.com/poteto/status/2069824386283319343)*.

### Let's build a verification skill together

To start, install pstack and then run [/create-verification-skill](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md). I also recommend adding [Dr Eggbot](https://x.ai/bot/93gOz3op1UQdBdbekQFLK), my bot that helps you create high quality bots, to your roster. Dr Eggbot ships with **[pstack](https://x.ai/bot/plugin/9717366)**. It’ll teach coding bots how to use it, and it can also make non-coding bots with the same rigor.

You can ask Dr Eggbot to create an engineer bot for you that you can then ask to run /create-verification-skill and set up a daily routine to run /maintain-verification-skill.

![](https://pbs.twimg.com/media/HRBrZTOagAET8Vw.jpg)

While that runs, let's walk through what the skill does and how it makes a high quality verification skill for you.

I distilled all of our verification skills that we use to build Grok @Bot and Cursor into this skill as a sort of meta-skill. It teaches your agent how to create a high quality one for your own app.

Now this is where choice of tech stack is important. If you're building an app in Electron or for the web for example, you can take advantage of the rich debugging tools available for the JS ecosystem. For example, the [Chrome DevTools Protocol (CDP)](https://chromedevtools.github.io/devtools-protocol/) allows you to use the same tooling available in your browser's developer tools. Or if you're building an iOS app, making use of the simulator.

You ideally want the ability to interact with your app, debug it, take perf traces, and any other debugging and development tooling that you might typically use if you were developing the app by hand. If you don't have a rich runtime to make use of, you may need to ask your agent to create tools for you (eg using lldb, or a custom package that runs as a sidecar in dev environments), or just make use of what you have available.

I personally feel that agentic verification is so important that I would unironically suggest building your own rich debugging tools, or even choosing a different tech stack, in order to have unfair advantages and extreme productivity in building software. As I mentioned earlier, giving agents the ability to verify their own work unlocks everyone in your organization to be able to contribute and validate that their changes actually work. The harder your tech stack is to debug and control, the more difficult it will be to use agents productively.

**Make it Reproducible**

In **pstack**, we have a principle called ["Build the Lever"](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-build-the-lever/SKILL.md). What this means in the context of creating a skill, is that we prefer to give agents tools rather than just markdown. For verification skills, this means creating a small CLI that scripts interaction and debugging of your app in a small, agent friendly utility. This means that agents consume fewer tokens trying to do a task (run a CLI command instead of writing a throwaway script to click on something), and makes your verification skill more reproducible and testable.

Here's a hypothetical example of a CLI your agent might make for an Electron app:

Some content could not be imported from the original document. [View content ↗](https://x.com/poteto/status/2097732320606507506/?rw_tt_thread=True)

Now, all agents can use this CLI to quickly navigate and debug your app. You'll also want to start thinking about the dev experience of building your app:

- seeding a dev database
- how to handle auth, test users, API calls against a test/staging environment
- installing and bringing up your dev environment in a consistent way

All of this is stuff you've probably needed to think about anyway when you were writing code yourself. So think of this as your agents' main utility for doing dev work on your app. Keep it well maintained and tested!

Some other example commands you might want to consider:

Some content could not be imported from the original document. [View content ↗](https://x.com/poteto/status/2097732320606507506/?rw_tt_thread=True)

Once you have this basic setup, you should already start to see a big improvement in your agents. They should be able to navigate around and debug your app with ease.

I recommend spending time here making this CLI good and error free before doing anything more advanced. You'll also want to think about (or ask your agent to) designing an agent friendly CLI. There are many resources online you can point your agent to, but the key properties I like are:

- the API is easy to compose - think John Ousterhout's deep modules philosophy
- any command with potentially destructive side effects should have a --dry-run option
- make use of subcommands to gradually disclose functionality rather than all at once
- error messages should be very descriptive and tell the agent what it should do instead
- rich --help text
- outputs returned in machine readable form (eg JSON)

**Go faster with parallelism with [Cloud Agents](https://cursor.com/docs/cloud-agent) instead of worktrees**

When you've had some success running your verification skill to land a few PRs, you might start to wonder if you can parallelize more. For example, if an agent can now take your prompt and mostly drive it to a mergeable state, doesn't that free you up to run more agents?

Your first instinct will be to add worktree support, meaning that your agents can use git to create a tracked copy of the repo where they can make changes in isolation to the main checkout. In theory, this lets you run multiple agents at once without their changes clobbering over each other.

I would recommend against doing this. For one, it uses a lot of storage space and resources on your machine. You may be able to get away with running up to 10 agents in parallel with worktrees depending on the size of your repo and how powerful your machine is. But there's a far better way!

Cursor's [cloud agents](https://cursor.com/docs/cloud-agent) are agents that run on the cloud, on Cursor's infrastructure. These agents have access to a real computer, meaning that they can install dependencies, run your app, take videos and screenshots, and interact with your app like a real user can. If you've invested enough in the previous step to make your dev experience good, it shouldn't be a huge lift to be able to set up cloud agents. When you first set up your cloud environment, we send an agent to help you get it set up and running correctly. After the first build, we take a [snapshot](https://cursor.com/docs/cloud-agent/builds) which means that subsequent cloud agent runs always start up quickly.

I highly recommend taking the time to set cloud agents up, as it unlocks a massive increase in productivity in parallelism. In a later post I'll show you how I run hundreds of subagents in parallel in the cloud! But for now, set up your environment and get it to a state where you can start to feel confident about running all your agents in the cloud.

**Keep agents smart with Feature Maps**

As your app grows more complex, agents need more guidance to be able to find features and interact with them. To do this, I've come up with something I call the Feature Map. As the name suggests, it's an easily searchable map of all the features available in your app, what it does, and how to get to it from a user's perspective.

Here's an [example Feature Map](https://github.com/poteto/verification-skill-example/blob/main/.cursor/skills/verify-atlas/references/features/README.md) that I've prepared for a fictional app called Atlas. It's just a couple of markdown file that are mentioned in the verification's [SKILL.md](http://SKILL.md).

You can put this file anywhere, but in /create-verification-skill we automatically create a references/features directory alongside a [README.md](http://README.md). The readme is the map itself: a high level overview of all the major features available, with links to specific details. An example feature looks something like this:

Some content could not be imported from the original document. [View content ↗](https://x.com/poteto/status/2097732320606507506/?rw_tt_thread=True)

Don't worry about writing these yourself! When you run **/create-verification-skill**, your agent will automatically go through your app and catalog everything and create these references for you.

The Feature Map, when combined with the CLI, is one of the main reasons why pstack's verification skills are so good. Agents now have context about every single feature and how to get to it, saving precious tokens in its context window and teaching it exactly what it's for and how to get there.

You can think of the Feature Map as a form of "materialized memory". If you've been using agents for a while you're probably familiar with the concept of memory - typically these might be stored as simple markdown files (eg an Obsidian vault), or even something more complex like a vector database. Personally, I think your codebase is the ultimate form of memory. Code is a projection of the decision making you and your team have made and represents the source of truth for what's happened and how things actually work. A Feature Map is just a more compact form of that, designed to save tokens. And because it's just markdown inside of a skill, everyone contributing to your codebase benefits from this shared memory.

This means that maintaining the verification skill is really important. I recommend running **/maintain-verification-skill** at least once a day to ensure that your agents always have the latest details on controlling your app. You may also find, as you use your verification skill more, that agents will automatically update them as they work on your app. /maintain-verification-skill catches whatever is missed.

## How to use your verification skill

For reference, here's an example verification skill created for a fictional app: [https://github.com/poteto/verification-skill-example](https://github.com/poteto/verification-skill-example). As a reminder, run **/create-verification-skill** to make one, which includes a basic CLI and Feature Map.

Here's how I typically use it with **pstack**.

First, of course, is to start your prompt with **/poteto-mode**. If you're using pstack through Cursor, you can also hit Opt + Enter instead of just Enter when you autocomplete /poteto-mode - this adds the skill as a [Custom Mode](https://cursor.com/changelog/08-19-26#custom-modes), which pins the skill so your agent gets a reminder to use the skill on every new turn.

![](https://pbs.twimg.com/media/HRAqVoyb0AEwvnc.png)

In Grok @Bot, install [the plugin](https://x.ai/bot/plugin/9717366), then type /poteto-mode.

![](https://pbs.twimg.com/media/HRArLIFa4AApHT3.png)

**Example: Building new features**

For building new features, I typically use the verification skill alongside /poteto-mode to get the agent to verify its work. For example, I might prompt something like:

/poteto-mode build \<description of feature, any useful context\>. use /control-app to verify your changes and show me a video and screenshots as proof

With /control-app being the result of /create-verification-skill. In Grok @Bot, I would prompt something like:

spawn a cloud agent to use /poteto-mode to build \<description of feature, any useful context\>. use /control-app to verify your changes and show me a video and screenshots as proof

The minor difference here is that in Grok @Bot you tell your bot to spawn a cloud agent instead of doing the work itself. The main reason I prefer to do this is because it frees up your bot to do other things and keeps its context window clean. In that sense, I think of my bots more as coordinators who manage and supervise cloud agents. Cloud agents also mean that you can take advantage of the full array of models available in Cursor which have their own separate machine, so your bot's computer stays free for other things.

**Example: Perf work**

spawn a cloud agent to use /poteto-mode to improve the initial loading time of our app. first use /control-app to take a trace of the status quo, and identify opportunities for improvement. then do a targeted fix and use /control-app + a [/swarm](https://github.com/cursor/plugins/blob/main/pstack/skills/swarm/SKILL.md) to confirm the win

[/swarm](https://github.com/cursor/plugins/blob/main/pstack/skills/swarm/SKILL.md) is one of the best skills to combine with your verification skill. It fans out any number of cloud agents to run your verification skill, so you can do things like confirm a perf win with a big enough sample size, or fuzz your app to ensure you didn't break or regress anything.

**Example: Automatically reproduce user reports**

When you're happy with your verification skill, you can put them inside of Grok @Bot routines, or [Cursor Automations](https://cursor.com/docs/cloud-agent/automations). Routines and automations let you run things on schedule, or trigger whenever an event happens.

For example, if you pipe in user feedback into Slack, and/or have your own internal feedback channel, you can have your bots listen to every report and automatically try to reproduce them with a cloud agent. If your verification skill and Feature Map is good enough, you may even then decide to auto-fix issues as well.

There's a reason I said earlier that verification is the one of the most important skills in your toolbox. It gives you a foundation to build new skills and routines on top of. And most importantly, everyone in your team benefits.

## Invest in your verification skill

Once you've created your verification skill, keep it sharp with /maintain-verification-skill. Keep improving the CLI and invest in the skill like you would critical infra. You may even want to put an oncall rotation on it - that's how important it is to unlock 100-1000x productivity for your team.

This skill is the foundation for many other skills that we'll cover in the **pstack** guide, and composes beautifully with all of them.

- pstack: [https://x.ai/bot/plugin/9717366](https://x.ai/bot/plugin/9717366) ([github link](https://github.com/cursor/plugins/tree/main/pstack))
- Dr Eggbot: [https://x.ai/bot/93gOz3op1UQdBdbekQFLK](https://x.ai/bot/93gOz3op1UQdBdbekQFLK)

I recommend adding [Dr Eggbot](https://x.ai/bot/93gOz3op1UQdBdbekQFLK), my bot that helps you create high quality bots, to your roster. Dr Eggbot ships with pstack. It’ll teach coding bots how to use it, and it can also make non-coding bots with the same rigor.

You can ask Dr Eggbot to create an engineer bot for you that you can then ask to run /create-verification-skill and set up a daily routine to run /maintain-verification-skill.

Thanks for reading and stay tuned for Part 2!

But once you have verification working, the next question is: how do you actually figure out what to build?

[](https://x.ai/bot/plugin/9717366)

In this post, I am going to walk you through how I do research, planning, prototyping, and architecture with **[pstack](https://x.ai/bot/plugin/9717366)**. This is the exact workflow that allows me to ship thousands of PRs a month into production while keeping code quality extraordinarily high.

![](https://pbs.twimg.com/media/HRwSukbbwAA6Xo2.jpg)

## The art of supervising someone smarter than you

Back in the old days of 2024, to make any change in a system, you first needed to read enough of it to build a mental model of what's going on. Depending on the size and complexity of the codebase, this may have taken you anywhere from hours, to even days and months. With a small change, you could get away with maybe only a local understanding of a small subsystem. If you were refactoring the core however, you'd probably need to have a mental model of how the whole thing works in order to do the refactor correctly and effectively.

Agents obviously remove this barrier. You can make changes to systems very easily by just prompting your agent and it will do it, regardless of how much or little you know about the code. But keeping the quality of the code and user experience high is still difficult, especially if you're not already a domain expert who knows what to look for and ask.

Even though frontier models have gotten very capable, there are still 2 failure modes that I constantly observe:

1.  They are unable to fully understand your intent because they're under/poorly specified.
2.  They don't have enough context on how to do the work correctly.

Both of these problems are related. Using agents well comes down to how well you're able to prime the agent's context window with high quality context. You can certainly write code that works without doing this, but I find that the outcomes and quality are much better when I've done the work to provide my agents with everything they need to do a high quality job.

### In your own words

Frontier models are very capable coders. While with older models I might have prompted very specifically what I wanted it to do, almost micromanaging them, the latest models are able to write code better than you or I can. So there's a fine balance I want to strike with telling the agent what I want it to achieve, while giving it the freedom to solve it in ways I might not have thought of.

This is the art of supervising someone smarter than you, on a codebase you haven't written yourself, and where humans can no longer fit the entire mental model of the codebase in their head.

One technique I like to use is the indirect prompt. Instead of telling the agent exactly what I want, I try to draw it out of the agent instead - in its own words.

For example, when someone reports an issue in Slack, I will often ask the agent to read the thread and restate the problem in its own words before doing anything else.

For example, I might say:

/poteto-mode read this slack thread. restate in your own words and in plain english what you think the underlying issue is

This accomplishes three things:

First, it forces the agent to compress a noisy conversation into a structured problem statement. Second, it lets me catch misunderstandings immediately. If the agent fixates on a red herring in the thread, I can correct it quickly before it starts writing any code.

And third, I haven't potentially led it down the wrong path by stating my own assumptions and hypotheses which could be incorrect or limit what the agent could otherwise achieve.

**Building up a mental model**

Asking the agent to restate itself in a way that you can understand is an important part of working with someone that is smarter than you. That was the inspiration for [/teach](https://github.com/cursor/plugins/blob/main/pstack/skills/teach/SKILL.md), a skill that helps your agent explain things to you in an intuitive way. I use it whenever I need to make sure my agent is doing something that makes sense to me.

Under the hood, /teach calls out to [/how](https://github.com/cursor/plugins/blob/main/pstack/skills/how/SKILL.md) and [/why](https://github.com/cursor/plugins/blob/main/pstack/skills/why/SKILL.md).

/how traces runtime mechanics. When you ask /how, the agent assesses the complexity of the subsystem. If the subsystem spans multiple directories or services, it spawns parallel explorer agents on fast, efficient models like Grok.

/how is virtualization implemented?

/why investigates motivation and intent. Code tells you what happens. It rarely tells you why someone wrote it that way. When you run /why, pstack queries historical evidence across multiple sources in parallel: Git history and PR review comments, Linear tickets, Notion design docs, Slack conversations, Datadog monitors, Sentry errors, code lineage, and analytics warehouse events.

/why are we still stuck an old version of node.js?

![](https://pbs.twimg.com/media/HRv9RlWbsAAnMhL.jpg)

I use /teach whenever I want the agent to restate something so I can better understand and trust its work.

/teach me why you implemented it this way and not \<other way\>. what were the tradeoffs you made and why?

In practice, I have also found that the research done by the /teach skill is not just useful to humans, but for agents as well. Even with the latest frontier models, (this also depends on the quality of the harness), in general I find that they still often state things confidently without backing it up with data or actually reading the code needed to build up a mental model of how it works. So this act of teaching you what it's going to do and why ends up helping the agent too.

**Learning from history**

Many of my projects span multiple conversations. For example, a few months ago I was working on fixing virtualization bugs and perf issues that people were reporting in Cursor. I realized that every time I started a new chat I had to basically start over with building up the rich context my agent had before when it was solving a similar problem.

What I realized is that your past transcripts are often a gold mine for rich context. pstack ships with the [/recall](https://github.com/cursor/plugins/blob/main/pstack/skills/recall/SKILL.md) skill to pull your recent context from chat history, so even fresh agents have the right context they need to get back to a good state.

/recall the work i did yesterday on virtualization and then read this bug report on slack

Using /teach, /recall, /how, and /why are how I keep my own mental models of the codebase up to date, compressed into a form I can easily understand and remember. And, it helps agents too!

### Working backwards

Once you understand the problem, how do you specify the solution?

![](https://pbs.twimg.com/media/HRv9X7xagAAuJvi.jpg)

In my opinion, most harnesses that have plan modes tend to over-specify implementation details and under-specify everything else. That's why in pstack, I cheekily said that ["I don't believe in planning"](https://github.com/cursor/plugins/blob/main/pstack/README.md#why-are-there-no-planning-skills). The truth is that I do plan, but I do so through code.

For certain kinds of work, like creating shared code or packages that others will use, I am a big believer in readme driven development. If you're not familiar with it, it's a technique of development that was popular back in the day, where you start with crafting your readme first. This forced you to put on your developer experience hat, where you start with describing the APIs to a hypothetical user, and work backwards to the implementation and architecture.

For example, when I was building Dune, our in-house client framework for desktop apps, I started by first writing a tutorial for it, so I could understand what it would be like to build an app with it. Or at least I tried to. It was real a struggle getting the agent to produce anything good or readable. So I had to first spend some time sharpening my knife, by creating the [/technical-writing](https://github.com/cursor/plugins/blob/main/pstack/skills/technical-writing/SKILL.md) skill.

The first pass of the readme without the /technical-writing skill was painful to read because it mixed up different goals. It tried to be a tutorial, a how-to guide, an architectural explanation, and an API reference all in the same document, written with your usual AI slop and [mannered prose](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#writing-density).

![](https://pbs.twimg.com/media/HRv-FWubcAAOrNy.jpg)

/technical-writing uses the [Diátaxis framework](https://diataxis.fr/) to separate documentation into four distinct modes:

1.  **Tutorial:** Learning by doing. A lesson that leads a newcomer through a series of steps to build something visible.
2.  **How-to guide:** Steps to solve a specific, real-world problem for an experienced user.
3.  **Reference:** Dry, complete, authoritative technical descriptions of machinery, APIs, and configuration flags.
4.  **Explanation:** High-level discussion that clarifies and illuminates background, design choices, and tradeoffs.

It also uses [/unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md), so it produces documentation that is very readable.

Writing a plan this way is very helpful because it also gives your agents a concrete target and goal that it can check its own work against. And of course, it's also much easier to understand what exactly the agent is going to build.

Many of pstack's skills compound here in the design phase. For example:

\(1\) /recall my work fixing virtualization bugs and perf issues from the past 7 days. use /how and /why to understand how our current virtualization implementation works.

\(2\) then use /poteto-mode planning and /technical-writing to come up with a new virtualization engine that categorically eliminates flickering and jittering. let's start by writing a tutorial on how i would use this new package to virtualize a React app

\(3\) after you write the plan, /teach me and prove to me why this new approach is superior to our current engine

The technique here is really about drawing out interesting and rich context that gives your agents the ability to see the problem the same way you do - not just as a small slice:

1.  The first part of the prompt recalls relevant past and present context about how virtualization is implemented in my app.
2.  The second part guides the agent to use that context, such as bugs it has fixed before, to come up with a new design that eliminates those problems entirely.
3.  The final piece is asking your agent to prove to you that this new package is superior. This is where high quality tools like [verification skills](https://x.com/poteto/status/2094457600259842065) are important to have.

### Measure a hundred times, cut once

![](https://pbs.twimg.com/media/HRv9b_jbQAAKTn5.jpg)

When planning, two of the most common mistakes I see are:

1.  Accepting the agent's first design.
2.  Overcooking the plan without empirical evidence.

When humans wrote code, we often collaborated with each other over design documents. These were docs that talked about high level architecture, alternatives considered, tradeoffs, and any unusual implementation notes. It was very common to go through multiple iterations of these docs before you landed on a settled design.

With agents, while we can skip the ceremony of the design doc, I often see the mistake of accepting the first thing the agent gives back to you. With pstack, we can instead take the "measure twice, cut once" approach to its limit, using parallel agents.

We do this by using the [prototyping playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/prototype.md).

In pstack, playbooks aren't skills, but reference files inside of /poteto-mode. These playbooks are conditionally loaded (for token efficiency) depending on the type of task you're working on. These 23 playbooks (as of 0.15.0) each contain a workflow that I use when I'm doing a task.

Unlike skills, playbooks are automatically used by the agent as part of /poteto-mode. For example:

/poteto-mode prototype a few options for the new dropdown menu

/poteto-mode fix this bug

/poteto-mode eval this skill change

Prototyping is one of my favorite pstack playbooks. It gives you many attempts at a goal and helps the agent reason about the best option. This is useful not just for visual prototyping, but also prototyping different solutions for features, bug fixes, and so on.

/poteto-mode prototype a few options for \<feature request\>. use /control-app\* and take videos/screenshots for me to review and choose from

\* *note: /control-app is the verification skill we created in [Part 1](https://x.com/poteto/status/2094457600259842065)*

When prototyping visual changes, the agent builds throwaway sketches in your app or in a scratch directory. If it is testing a UI interaction, it puts two or three variations behind a simple switcher. Then it drives the interaction with the /control-app skill, takes screenshots of each variant, and measures the actual timing or layout.

Prototyping is planning, but with code. It allows agents the freedom to explore the problem space, and to give them a chance to surprise you with something you wouldn't have thought of yourself. Prototypes allow agents to answer their own questions with empirical evidence instead of waiting for my input.

**Architecting bigger changes**

As an engineer in the agentic era, it's more important to spend my time on architecture, choosing the right data structures, and thinking about how the systems I build will work together. My agents fill in the implementation details.

![](https://pbs.twimg.com/media/HRv9hLbaYAAq_sC.jpg)

Another useful skill that pstack ships with is [/architect](https://github.com/cursor/plugins/blob/main/pstack/skills/architect/SKILL.md). It structures design into distinct, disciplined phases:

1.  **Ground the problem.** The agent runs /how and /why over the affected systems to build an accurate mental model of existing ownership and constraints.
2.  **Sketch.** The agent enters an architecture arena. It spawns independent candidate runners in parallel, often across different model families. Each runner receives the grounding brief and drafts a complete design package: the caller's usage sketch, the core type definitions, public function signatures, and a concise rationale. These are usually done by sketching out just the type signatures, that derive from how we want call sites to look like. Each runner must evaluate interface depth, examine failure modes on weak models, and screen against our catalog of design red flags.
3.  **Cross-judge and Synthesize.** A cross-judge agent using a different model than the main agent evaluates the candidates against a strict rubric.
4.  **Implement against the sketch.** The agent replaces the sketch's placeholder bodies with real logic. If the agent discovers during implementation that a function needs unexpected parameters or extra state, it surfaces the discrepancy.
5.  **Scrap when the design is wrong.** If during implementation we find that the sketches were wrong, the agent throws it all away and starts over.

The point here is to give the agent a self contained mini-loop where it can synthesize multiple competing designs from different model families into one optimal approach, and take care to be rigorous and not be afraid to throw its design away if it turns out that the architecture it came up with is wrong based on empirical proof. If the same workaround appears across unrelated call sites, or if the types require escape hatches like any or forced casts, that is empirical proof that the architecture is wrong.

/architect this new \<feature request\>

The big lesson here is that it's far more effective to plan with code using /poteto-mode prototyping and /architect.

It's also why I never bother with reviewing abstract plans adversarially. The agents start hallucinating theoretical risks, and inventing complex edge cases to protect against problems that will never happen. Don't overcook your plans when they're still abstract: let the agent answer open questions on its own through prototyping and verifying its own work.

### Okay but I really want a planning doc

![](https://pbs.twimg.com/media/HRv-IJxasAAYt2S.jpg)

While pstack doesn't come with a planning skill, it does ship with a [multi-phase planning playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/multi-phase-plan.md). I typically use this after the agent has come up with a design I'm happy with, as a way to create a tactical execution plan.

/poteto-mode turn this design into a plan

Every single task in the plan is structured around proof and verification. The playbook tells agents that tests alone are not sufficient verification. It's verified only when it has actually run the code and verified that it works.

Every plan is checked by an automated script that validates its structure and formatting. Once approved, the plan executes item by item. Each PR is small, self-contained, and easily reviewed.

For really large projects (like one that might take me a whole week), I may sometimes decide to commit the plans temporarily to the codebase so that other agents are aware of the work in progress. But I typically delete them when I'm done so I don't leave the codebase in a state of confusion. I don't find it valuable to keep plans around permanently.

## The workflow in practice

To see how all of these pieces fit together, let us walk through three concrete examples of how I prompt these workflows.

### Example 1: Researching an ambiguous bug

When an issue appears in production and the root cause is unclear:

/poteto-mode investigate why background workers periodically fail with timeout errors. give me a breakdown of what we know, what data you used, and your best hypotheses.

The agent explores the code, checks metrics and historical commits in parallel, and gives you its best educated guesses on where the problem might lie.

### Example 2: Designing a new service boundary

When introducing a new subsystem that other modules will depend on:

/poteto-mode we need to add rate limiting for external webhooks. /architect this first, and answer any open questions with prototypes. let me review before proceeding.

The agent grounds the existing webhook architecture, spins up competing design runners across multiple models, benchmarks with throwaway prototypes, and produces a clean, verified interface.

### Example 3: Executing a multi-PR migration

When executing a complex refactor across many files:

/poteto-mode create a plan to migrate our entire UI library to StyleX. break the migration into small, verifiable PRs. each PR must have its visual regression tests and live verification steps. i want the final result to be 100% identical compared to the original - bugs included

The agent breaks the work into independent steps, writes an auditable checklist, and prepares each unit so that it can be built, verified, and landed safely.

### Example 4: Fix stuff people report on Slack

If you've ever seen me on Slack in one of our issues or feedback channels, you'll probably have seen these classics:

*\# thread already has sufficient context*

/poteto-mode do it

/poteto-mode repro this with /control-app. if it repros on main, fix it and show me a video as proof

Many of the skills I've talked about here are already automatically used by /poteto-mode, so the vast majority of times you can just use /poteto-mode and move on with your life!

### **The art of planning**

Plan Mode is often used as a way to convince yourself that the agent is going to do the right thing. But the reality is that abstract plans only give you the illusion of progress. A long and lengthy plan makes it look like you and your agent were very productive, but it's probably lacking in substance.

**pstack** gives you tools to combine thorough investigation, empirical evidence, and rigorous verification. When you plan this way, engineering with agents stops feeling like a gamble. It becomes predictable and repeatable.

[](https://x.ai/bot/plugin/9717366)

Thanks for reading, and stay tuned for Part 3!
