---
layout: post
title: "Do LLMs Kill Config Generators?"
date: 2026-04-05
---
I once wrote a [blog post](/2024/05/01/generating-a-gitignore-for-a-project/) about how to create `.gitignore` files by using [gitignore.io](https://gitignore.io). For those that haven't used it before, it's a website and api that lets you compose a `.gitignore` for a project by listing the technologies your project will use (either in their website or by curl'ing the service on the CLI), and it spits out a `.gitignore` accordingly. 

This service did a pretty good job, and I would routinely reach for it when starting new projects. I liked it; it was an improvement from copy-pasting example snippets from various other `.gitignore` files found on GitHub.

But it occurred to me today that I stopped using this tool and in fact will probably never use it again. Not because it's bad, but because, well - an LLM will just create this file now. But it's more subtle than that. It's not like I've asked an LLM to specifically create this file for me lately - or I might have had these thoughts sooner - it will create it as a sub task of setting up a new project and I won't even notice unless something weird shows up in a `git status` that would normally go in the ignore.

So that got me thinking about config generators more broadly.

When was the last time I wrote a Dockerfile? A Github workflow? A terraform module? A compose file?

These used to be routine tasks for me in my day job as an Infrastructure Engineer, and I can honestly say I haven't done any of these by hand once in 2026, despite having set up several projects that called for all of them since the beginning of the year.

LLM-powered coding tools like Claude Code, Cursor, and Copilot do a great job of setting up all of these things, and they often do them without asking anything beyond the initial project setup, or feeding them an example project to reference.

So... are config generators dead? Are project scaffolds dead? Are cookie-cutters dead?

I honestly don't know, but I can speculate based on my own usage of LLMs that the work these tools performed will now be done by LLMs whenever it's feasible for them to do so, and the only situations where writing or generating a config file will make sense are:

- LLMs don't have the ability to do it yet for whatever reason
- Using a tool will save a meaningful number of tokens (you can imagine having an LLM write a complicated terraform module when it could use an existing one, or a Github workflow when you know you have an existing one that's basically perfect, etc)
- You need the deterministic output of a tool over an LLM for a config

But I'd push back on that last one. Chatting with my own friendly neighborhood Clanker (Opus 4.6), the example it gave was generating IAM policies according to company cloud requirements. In this situation, a generator ensures your IAM policies are created properly and include the right things (AdministratorAccess for the win!).

But that's not something I'd use a generator for, or ever have, really - that's more like validation. And I do still need to validate config. I need to validate Dockerfiles, Github workflows, IAM policies, terraform modules (at least the output of a plan). There's a bigger thought here - that a lot of my work now is spent steering an LLM at the start of a task and validating its outputs at the end - but that's meta commentary for another post.

So does that mean the value for devs looking to build useful tools in the config space is moving from generators to validators?

Maybe? I'm not sure, but I'm going to speculate that probably, yes, validators are still useful, and will continue to be.

Let me know what you think in the comments that I haven't yet enabled below.