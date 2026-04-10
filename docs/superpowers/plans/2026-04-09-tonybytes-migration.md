# TonyBytes.net Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the dreslan.com Jekyll site to tonybytes.net with rebranding from "Dreslan" to "Tony Bytes"

**Architecture:** Copy-and-rebrand. All content from the dreslan.com repo is copied into the empty tonybytes.net repo, branding is updated in-place, and the site is deployed via GitHub Pages with a custom domain.

**Tech Stack:** Jekyll 4.3, GitHub Pages, Docker (local dev)

---

### Task 1: Create GitHub repo and set remote

**Files:**
- No file changes — repo/git setup only

- [ ] **Step 1: Create the GitHub repo**

```bash
gh repo create dreslan/tonybytes.net --public --description "Personal site — tonybytes.net"
```

Expected: repo created at `github.com/dreslan/tonybytes.net`

- [ ] **Step 2: Set remote on local repo**

```bash
cd /Users/dreslan/repos/dreslan/tonybytes.net
git remote add origin git@github.com:dreslan/tonybytes.net.git
```

- [ ] **Step 3: Verify remote**

```bash
git remote -v
```

Expected: `origin  git@github.com:dreslan/tonybytes.net.git (fetch)` and `(push)`

---

### Task 2: Copy site files from dreslan.com

**Files:**
- Create: all site files in tonybytes.net root (bulk copy)

- [ ] **Step 1: Copy all site files, excluding non-site directories**

```bash
rsync -av --exclude='.git' --exclude='_site' --exclude='.jekyll-cache' --exclude='.jekyll-metadata' --exclude='.obsidian' --exclude='.claude' --exclude='.superpowers' --exclude='.sass-cache' --exclude='.DS_Store' --exclude='docs' /Users/dreslan/repos/dreslan/dreslan.com/ /Users/dreslan/repos/dreslan/tonybytes.net/
```

- [ ] **Step 2: Remove the old serve script (replaced by Docker in Task 10)**

```bash
rm /Users/dreslan/repos/dreslan/tonybytes.net/serve
```

- [ ] **Step 3: Remove the old CNAME (will be replaced in Task 9)**

```bash
rm /Users/dreslan/repos/dreslan/tonybytes.net/CNAME
```

- [ ] **Step 4: Verify file structure**

```bash
ls -la /Users/dreslan/repos/dreslan/tonybytes.net/
ls /Users/dreslan/repos/dreslan/tonybytes.net/_layouts/
ls /Users/dreslan/repos/dreslan/tonybytes.net/_posts/
```

Expected: all Jekyll directories present (`_layouts/`, `_posts/`, `_reviews/`, `_bits/`, `_data/`, `assets/`), plus page files (`index.html`, `bytes.md`, `bits.md`, `books.md`, `about.md`, `projects.md`, `404.md`), `Gemfile`, `.gitignore`. No `serve` script. No `CNAME`.

- [ ] **Step 5: Commit**

```bash
cd /Users/dreslan/repos/dreslan/tonybytes.net
git add -A
git commit -m "chore: copy site files from dreslan.com"
```

---

### Task 3: Update _config.yml

**Files:**
- Modify: `_config.yml`

- [ ] **Step 1: Update title and url**

Replace the full contents of `_config.yml` with:

```yaml
title: Tony Bytes
description: Personal commentary on life, society, and the times.
url: https://tonybytes.net
baseurl: ""

permalink: /:year/:month/:day/:title/

markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge

plugins:
  - jekyll-feed
  - jekyll-seo-tag

collections:
  reviews:
    output: true
    permalink: /books/:title/
  bits:
    output: true
    permalink: /bits/:title/

exclude:
  - Gemfile
  - Gemfile.lock
  - README.md
  - vendor
  - scripts
  - docs
  - docker-compose.yml
  - "*.csv"
```

Note: `jekyll-admin` plugin removed — it's a dev convenience that doesn't work in Docker without extra config and isn't needed for GitHub Pages.

- [ ] **Step 2: Commit**

```bash
git add _config.yml
git commit -m "feat: rebrand config to Tony Bytes / tonybytes.net"
```

---

### Task 4: Update header and footer in default.html

**Files:**
- Modify: `_layouts/default.html`

- [ ] **Step 1: Update the header title**

Replace line 20:

```html
      <a href="{{ '/' | relative_url }}" class="site-title"><span class="site-title-d">D</span><span class="site-title-rest">reslan</span></a>
```

With:

```html
      <a href="{{ '/' | relative_url }}" class="site-title"><span class="site-title-highlight">T</span><span class="site-title-rest">ony </span><span class="site-title-highlight">B</span><span class="site-title-rest">ytes</span></a>
```

- [ ] **Step 2: Update the footer copyright and disclaimer**

Replace lines 38-44:

```html
      <span>&copy; {{ site.time | date: '%Y' }} <a href="{{ '/about' | relative_url }}">Dreslan</a></span>
      <span class="footer-links">
        <a href="{{ '/feed.xml' | relative_url }}">rss</a>
        <a href="https://github.com/dreslan">github</a>
      </span>
      <span class="footer-disclaimer">All content is written by a human — possibly reviewed by a Clanker.</span>
      <span class="footer-license">Blog content licensed under <a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a>. Fiction is all rights reserved.</span>
```

With:

```html
      <span>&copy; {{ site.time | date: '%Y' }} Tony Bytes</span>
      <span class="footer-links">
        <a href="{{ '/feed.xml' | relative_url }}">rss</a>
        <a href="https://github.com/dreslan">github</a>
      </span>
      <span class="footer-disclaimer">All content written by a human. No AIs were harmed in the making of this website. <a href="{{ '/disclosure' | relative_url }}">See disclosure on AI usage</a>.</span>
      <span class="footer-license">Blog content licensed under <a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a>. Fiction is all rights reserved.</span>
```

- [ ] **Step 3: Commit**

```bash
git add _layouts/default.html
git commit -m "feat: rebrand header and footer to Tony Bytes"
```

---

### Task 5: Update CSS class names

**Files:**
- Modify: `assets/css/style.css`

- [ ] **Step 1: Rename .site-title-d to .site-title-highlight**

Replace lines 113-127:

```css
.site-title-d {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.6em;
  height: 1.6em;
  background: var(--link);
  color: var(--bg);
  border-radius: 0.3em;
  font-size: 1.15em;
  font-weight: 700;
  margin-right: 0.15em;
  vertical-align: baseline;
  line-height: 1;
}
```

With:

```css
.site-title-highlight {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.6em;
  height: 1.6em;
  background: var(--link);
  color: var(--bg);
  border-radius: 0.3em;
  font-size: 1.15em;
  font-weight: 700;
  margin-right: 0.15em;
  vertical-align: baseline;
  line-height: 1;
}
```

- [ ] **Step 2: Commit**

```bash
git add assets/css/style.css
git commit -m "refactor: rename site-title-d to site-title-highlight"
```

---

### Task 6: Create TB favicon

**Files:**
- Modify: `favicon.svg`

- [ ] **Step 1: Replace favicon with TB monogram**

Replace the full contents of `favicon.svg` with:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#d79921"/>
  <text x="16" y="23" text-anchor="middle" font-family="system-ui, sans-serif" font-size="18" font-weight="700" fill="#1a1a1a">TB</text>
</svg>
```

Note: font-size reduced from 24 to 18 and y from 24 to 23 to fit two characters in the same viewBox.

- [ ] **Step 2: Commit**

```bash
git add favicon.svg
git commit -m "feat: replace D favicon with TB monogram"
```

---

### Task 7: Update about page

**Files:**
- Modify: `about.md`

- [ ] **Step 1: Update profile image alt text**

Replace line 7:

```markdown
<img src="/assets/images/profile.png" alt="Dreslan" class="profile-img">
```

With:

```markdown
<img src="/assets/images/profile.png" alt="Tony" class="profile-img">
```

- [ ] **Step 2: Replace the opening paragraphs**

Replace lines 9-13 (the Dreslan handle origin story):

```markdown
Hi, welcome to my site, which is named after the handle I used to write under as a kid and which I haven't ever quite managed to stop using for everything online ever since.

Dreslan (drez-lin) is a handle I made up for [Diablo II](https://en.wikipedia.org/wiki/Diablo_II) as a kid in the early 2000s. It probably comes from [Dresden](https://en.wikipedia.org/wiki/Dresden) — we were reading Vonnegut's [Slaughterhouse-Five](https://en.wikipedia.org/wiki/Slaughterhouse-Five) in middle school around that time — but I can't say for sure anymore.

D2 led me into online guilds where people wrote fiction set in the Diablo world. I went by a few names back then (Tempest was the most common — I even founded a guild called "The Legends of O'nyith," now sadly lost to the internet). Eventually I got more serious about writing and came up with Dreslan as a proper pen name. The handle stuck, even though the writing habit petered out in the intervening decades.
```

With:

```markdown
Hi, welcome to Tony Bytes — my corner of the internet for commentary on life, society, and the times.

I grew up playing [Diablo II](https://en.wikipedia.org/wiki/Diablo_II) and writing fiction set in its world, hanging out in online guilds under various handles (Tempest was the most common — I even founded a guild called "The Legends of O'nyith," now sadly lost to the internet). The writing habit petered out in the intervening decades, but the urge to put thoughts down never quite went away.
```

- [ ] **Step 3: Remove the Disclaimer section at the bottom of about.md**

Replace lines 91-106 (the `## Disclaimer` section through the end):

```markdown
## Disclaimer

The content on this site is overwhelmingly written by me, an actual human with a run of the mill meat brain, rather than by an LLM.

However, I do recruit Clanker's to help with some things:

- Content editing (spelling / grammar / suggestive formatting / feedback)
- Hunting down media for posts
- Web design
- Telling bad jokes when I'm sad

And there may be the word or sentence here or there that was generated by an LLM which I may have then used as a launching point for writing, or which could be chalked up to basic editing.

Pending an ASI takeover, I think the world needs more humans writing directly to and for other humans, and less AI witten slop - or even if it isn't slop, I myself want to see more human written content, even if it's bad.

So, until my atoms get repurposed by HAL 9001 I will produce human slop for your enjoyment.
```

With:

```markdown
## Disclosure

For details on how AI is used in making this site, see the [disclosure on AI usage](/disclosure/).
```

This moves the AI discussion to its own dedicated page (Task 8) and keeps the about page focused on the personal narrative.

- [ ] **Step 4: Commit**

```bash
git add about.md
git commit -m "feat: update about page for Tony Bytes rebrand"
```

---

### Task 8: Create disclosure page

**Files:**
- Create: `disclosure.md`

- [ ] **Step 1: Create disclosure.md with scaffold**

```markdown
---
title: Disclosure on AI Usage
layout: page
permalink: "/disclosure/"
---

<!-- TODO: Fill in your AI disclosure content. Below is a suggested structure. -->

## How AI is used on this site

_This section is a placeholder — fill in with your own words._

## What AI does not do

_This section is a placeholder — fill in with your own words._
```

- [ ] **Step 2: Commit**

```bash
git add disclosure.md
git commit -m "feat: scaffold disclosure page for AI usage"
```

---

### Task 9: Create CNAME file

**Files:**
- Create: `CNAME`

- [ ] **Step 1: Create CNAME**

```
tonybytes.net
```

(Single line, no trailing newline.)

- [ ] **Step 2: Commit**

```bash
git add CNAME
git commit -m "chore: add CNAME for tonybytes.net"
```

---

### Task 10: Set up Docker-based local development

**Files:**
- Create: `docker-compose.yml`
- Modify: `.gitignore`
- Modify: `Gemfile` (remove jekyll-admin)

- [ ] **Step 1: Update Gemfile to remove jekyll-admin**

Replace the full contents of `Gemfile` with:

```ruby
source "https://rubygems.org"

gem "jekyll", "~> 4.3"
gem "webrick" # required for local preview on Ruby 3+

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
end
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
services:
  jekyll:
    image: ruby:3.3-slim
    command: >
      bash -c "
        bundle install &&
        bundle exec jekyll serve --host 0.0.0.0 --livereload
      "
    ports:
      - "4000:4000"
      - "35729:35729"
    volumes:
      - .:/srv/jekyll
      - bundle-cache:/usr/local/bundle
    working_dir: /srv/jekyll

volumes:
  bundle-cache:
```

Port 35729 is for LiveReload. The `bundle-cache` named volume avoids reinstalling gems on every restart.

- [ ] **Step 3: Update .gitignore**

Replace the full contents of `.gitignore` with:

```
_site/
.sass-cache/
.jekyll-cache/
.jekyll-metadata
vendor/
Gemfile.lock
.DS_Store
```

- [ ] **Step 4: Remove Gemfile.lock if it was copied over**

```bash
rm -f /Users/dreslan/repos/dreslan/tonybytes.net/Gemfile.lock
```

(Lock file will be regenerated inside the container.)

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml Gemfile .gitignore
git commit -m "feat: add Docker-based local development, remove serve script"
```

---

### Task 11: Verify locally with Docker

**Files:**
- No file changes — verification only

- [ ] **Step 1: Build and start the site**

```bash
cd /Users/dreslan/repos/dreslan/tonybytes.net
docker compose up
```

Expected: site builds and serves at `http://localhost:4000`

- [ ] **Step 2: Verify in browser**

Check the following:

1. Header shows "**T**ony **B**ytes" with gold-boxed T and B
2. Footer shows "© 2026 Tony Bytes" with disclosure link
3. Favicon is TB monogram (may need hard refresh)
4. About page has updated intro (no Dreslan handle story) and disclosure link
5. Disclosure page loads at `/disclosure/`
6. Posts, books, bits pages all render correctly
7. Dark/light theme toggle works
8. Navigating to `/bytes`, `/bits`, `/books`, `/projects`, `/about` all work

- [ ] **Step 3: Stop Docker**

```bash
docker compose down
```

---

### Task 12: Push and configure GitHub Pages

**Files:**
- No file changes — deployment only

- [ ] **Step 1: Push to GitHub**

```bash
cd /Users/dreslan/repos/dreslan/tonybytes.net
git push -u origin main
```

- [ ] **Step 2: Enable GitHub Pages**

```bash
gh api repos/dreslan/tonybytes.net/pages -X POST -f build_type=legacy -f source='{"branch":"main","path":"/"}'
```

If this returns an error about pages already being enabled, that's fine — the CNAME file may have auto-enabled it.

- [ ] **Step 3: Verify GitHub Pages settings**

```bash
gh api repos/dreslan/tonybytes.net/pages --jq '{url: .url, status: .status, cname: .cname}'
```

Expected: `cname` should be `tonybytes.net`

- [ ] **Step 4: Configure DNS**

This is a manual step for the user. Set a CNAME record on your domain registrar:

```
CNAME  tonybytes.net  →  dreslan.github.io
```

(If your registrar doesn't allow CNAME on the apex domain, use A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`)

- [ ] **Step 5: Verify the site is live**

After DNS propagates (may take a few minutes to hours):

```bash
curl -I https://tonybytes.net
```

Expected: HTTP 200, served by GitHub Pages
