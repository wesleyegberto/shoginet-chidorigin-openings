# Chidorigin's Shogi Opening Encyclopedia — English Translation

[![Deploy to GitHub Pages](https://github.com/wesleyegberto/shoginet-chidorigin-openings/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/wesleyegberto/shoginet-chidorigin-openings/actions/workflows/deploy-pages.yml)

English translation of [Chidorigin's Opening Encyclopedia (戦法図鑑)](http://shogi-chess.net/senpouzukan/), a comprehensive Japanese Shogi strategy and tactics reference.

The original site covers **220+ chapters** of Shogi openings, from fundamental piece development principles to advanced joseki and castle strategies — all translated to make this invaluable resource accessible to the international Shogi community.

🔗 **Live site:** [https://wesleyegberto.github.io/shoginet-chidorigin-openings/](https://wesleyegberto.github.io/shoginet-chidorigin-openings/)

## 📖 Content Overview

The encyclopedia is organized by opening families:

| Opening Family | Japanese | Topics |
|---|---|---|
| Double Wing Attack | 相掛かり (Aigakari) | Climbing Silver, Vertical Pawn Take, Twisting Rook |
| Yagura | 矢倉 | Piece Development, Combat, Morishita System, Waki System, Sparrow-pecking |
| Bishop Exchange | 角換わり (Kakugawari) | Climbing Silver, Quick Silver, Sitting Silver, Kimura Joseki |
| Side Pawn Picker | 横歩取り (Yokofudori) | ▽4五 Bishop, ▽8五 Rook, Nakahara-style, Aerial Strategy |
| Ranging Rook | 振り飛車 (Furibisha) | Fourth-file Rook, Central Rook, Third-file Rook, Facing Rook |
| Ishida Style | 石田流 | Quick Ishida, Masuda-style Ishida |
| Double Ranging Rook | 相振り飛車 | Facing Rook vs Third/Fourth-file Rook, vs Central Rook |
| Gokigen Central Rook | ゴキゲン中飛車 | Quick-attack, Slow Strategy, Floating Rook Type |
| Castle Strategies | 囲い | Anaguma, Mino, Left Mino, Millennium, Fujii System |
| Special Strategies | — | Demon Killer, No-Guard, Windmill, Kamaitachi, Crab-Crab Silver |

## 🏗️ How It Was Built

1. The original website was **scraped** to download all HTML pages and kifu (game record) files
2. Static resources (images, icons) from the original site are referenced directly
3. Original pages are preserved as `raw.html` in each tactics directory
4. **Translation was done using LLM**, with manual corrections applied during review

## 📂 Project Structure

```
├── .github/
│   └── workflows/
│       └── deploy-pages.yml    # GitHub Actions deploy workflow
├── pages/                      # Static site root (deployed to GitHub Pages)
│   ├── index.html              # Main index with all openings
│   ├── static/                 # Images and icons
│   └── tactics/                # 220+ tactics chapters
│       ├── tactics000/         # Prologue
│       │   ├── tactics000.html # Translated page
│       │   └── raw.html        # Original Japanese page
│       ├── tactics001/
│       │   ├── tactics001.html
│       │   ├── raw.html
│       │   └── *.kif           # Kifu game records
│       └── ...
├── kifu_reader/                # Kifu file reader utility
└── scrap.py                    # Web scraper script
```

## 🚀 CI/CD — GitHub Pages Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions.

### Workflow: `deploy-pages.yml`

| Trigger | Description |
|---|---|
| `push` to `main` | Auto-deploys when files in `pages/` are changed |
| `workflow_dispatch` | Manual deploy via GitHub Actions UI |

**Pipeline steps:**

```
Checkout → Configure Pages → Upload Artifact (pages/) → Deploy
```

### Setup (one-time)

1. Go to **Settings → Pages** in the GitHub repository
2. Under **Source**, select **"GitHub Actions"**
3. Push to `main` — the workflow will deploy automatically

## 🔗 Links

- **Live Site:** [wesleyegberto.github.io/shoginet-chidorigin-openings](https://wesleyegberto.github.io/shoginet-chidorigin-openings/)
- **Original Site:** [shogi-chess.net/senpouzukan](http://shogi-chess.net/senpouzukan/)
- **Simplified English Index:** [Chidori-gin at shogishack.net](https://shogishack.net/pages/shogi-strategies/chidori-gin.html)

