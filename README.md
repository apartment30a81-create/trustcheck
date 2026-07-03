# TrustCheck

**Verify content authenticity. Privacy-first.**

Upload any image to check if it's real or AI-generated. TrustCheck analyzes metadata, C2PA signatures, and visual artifacts — all in your browser.

## Features

- **Privacy-first** — everything runs locally, no data leaves your device
- **Metadata analysis** — EXIF, C2PA, camera info, software signatures
- **Frequency analysis** — pixel pattern detection for AI artifacts
- **Trust Score** — 0-100% gauge with color-coded verdict
- **Venice AI integration** — optional: enter your Venice API key for deep vision-based analysis
- **PWA** — install on home screen, works offline
- **Light/Dark/System** themes
- **Mobile-first** responsive design

## Usage

1. Open `index.html` or visit the hosted URL
2. Drop any image file
3. View trust score + detailed evidence
4. Optional: enter Venice API key for deeper analysis

## Tech Stack

- Vanilla HTML/CSS/JS (no frameworks)
- Service Worker + Manifest (PWA)
- Venice AI API (optional vision analysis)
- Vercel (deployment)

## Deployment

```bash
# Push to GitHub → Vercel auto-deploys
git init && git add . && git commit -m "Initial commit"
gh repo create trustcheck --public --push
```

## Privacy

TrustCheck is designed privacy-first:
- All metadata analysis runs **locally in your browser**
- No data is uploaded to any server
- Venice AI analysis only happens if you **explicitly** provide an API key
- Your API key is stored in localStorage and never sent anywhere but Venice's API