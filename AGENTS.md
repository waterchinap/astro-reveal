## Project

Astro + reveal.js slideshow app displaying financial index valuation data. Deployed on Cloudflare Pages.

## Architecture

- **Frontend** (`src/`): Astro 7, reveal.js 6 slides, Tailwind CSS v4 + daisyUI, `@tailwindcss/typography`
- **Backend** (`backend/`): Python scripts (uv-managed) fetch data from financial APIs, output JSON/XLSX into `src/assets/` and `public/`
- **Deploy**: data pipeline runs locally via `uv run`, commits generated assets, pushes to git → Cloudflare Pages auto-deploys

## Commands

```sh
npm run dev              # astro dev (local dev server)
npm run build            # astro build (outputs to dist/)
npm run preview          # astro preview
```

Use background mode for the dev server:

```
astro dev --background
astro dev stop | status | logs
```

## Backend

- Python 3.13+, managed with `uv` (not pip/poetry)
- Run individual scripts: `uv run qieman.py` or `uv run em-news.py`
- Full pipeline: `uv run update.py` — runs scripts, git adds/commits/pushes with retry logic
- Uses akshare for Chinese financial data, polars/pandas for processing
- PyPI mirror: `https://pypi.tuna.tsinghua.edu.cn/simple` (set in pyproject.toml)

## Key conventions

- Generated data files (JSON, xlsx) live in `src/assets/` and `public/`, committed to git
- Daily update workflow: `uv run update.py` auto-commits and pushes
- TypeScript is lenient (`noImplicitAny: false`, many warnings suppressed) — don't add strict typing
- Backend uses basedpyright with `basic` type checking mode
- All content is Mandarin Chinese
- Slides use a 1920×1080 viewport, auto-advance every 6s, looping
