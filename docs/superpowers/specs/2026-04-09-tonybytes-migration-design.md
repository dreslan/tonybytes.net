# TonyBytes.net Migration Design

## Summary

Migrate the personal site from dreslan.com (Jekyll, hosted on `dreslan/dreslan.github.io`) to tonybytes.net. Copy all content into the empty `tonybytes.net` repo, rebrand from "Dreslan" to "Tony Bytes", create a new GitHub repo, and deploy via GitHub Pages. The old repo stays untouched.

## 1. Repository & Deployment

- Create GitHub repo `dreslan/tonybytes.net` (public)
- Set as remote on local `/Users/dreslan/repos/dreslan/tonybytes.net`
- Copy all site files from `dreslan.com` repo, excluding: `.git/`, `_site/`, `.jekyll-cache/`, `.obsidian/`, `.claude/`, `.superpowers/`
- Add `CNAME` file containing `tonybytes.net`
- Push to GitHub, enable GitHub Pages serving from `main` branch
- User configures DNS separately (GitHub Pages A records: `185.199.108-111.153`, or CNAME to `dreslan.github.io`)

## 2. Branding Changes

### Site title
- `_config.yml`: `title: Tony Bytes`, `url: https://tonybytes.net`
- Update `description` if desired (current: "Personal commentary on life, society, and the times." — works as-is but can be refreshed)

### Header
- Replace the stylized "D" + "reslan" with "Tony Bytes" where "T" and "B" get the gold-box highlight treatment
- HTML structure: `<span class="site-title-highlight">T</span>ony <span class="site-title-highlight">B</span>ytes`

### Favicon
- Replace the gold "D" SVG with a "TB" monogram in the same gold-on-dark style

### Footer
- Copyright: `© 2026 Tony Bytes`
- Tagline: `All content written by a human. No AIs were harmed in the making of this website. See disclosure on AI usage`
- "disclosure on AI usage" links to `/disclosure/`

### CSS
- Rename `.site-title-d` to `.site-title-highlight` (or similar) and apply to both T and B
- No other design changes — same dark/light theme, gold accents (`#d79921` / `#fabd2f`), Atkinson Hyperlegible font

## 3. Content Migration

### Copied as-is (no changes)
- `_posts/` (3 posts)
- `_reviews/` (178 book reviews)
- `_bits/` (9 bits)
- `_data/reading_list.yml`
- `assets/` (CSS, fonts, images)
- `index.html`, `bytes.md`, `bits.md`, `books.md`, `projects.md`, `404.md`
- `Gemfile`, `Gemfile.lock`

### Modified during migration
- `about.md` — Remove/update references to the Dreslan handle origin story. Keep the rest of the personal narrative intact.
- `_config.yml` — Title, URL, description updates
- `_layouts/default.html` — Header and footer branding
- `assets/css/style.css` — CSS class renames for title styling
- `favicon.svg` — New TB monogram

### New files
- `disclosure.md` — Scaffolded with frontmatter and placeholder structure. User fills in actual content.
- `docker-compose.yml` — Local development environment
- `CNAME` — `tonybytes.net`

## 4. Local Development

- Remove the `serve` shell script
- Add `docker-compose.yml`: single service, Ruby-based image, Bundler installs gems, `jekyll serve --livereload` on port 4000, project directory mounted as volume
- Update `.gitignore` for `_site/`, `.jekyll-cache/`, `.sass-cache/`, `vendor/`

## 5. Out of Scope

- No changes to `dreslan/dreslan.github.io` repo
- No DNS configuration (user handles this)
- No Hugo migration
- No dreslan.com redirect setup
- No content rewrites beyond about page Dreslan references
- No design/color scheme changes
- Disclosure page gets scaffolding only — user writes the content
- GitHub handle remains `@dreslan` — no changes needed
