# Building TrustCheck: Privacy-First Content Authenticity Verification

**Published:** July 3, 2026

---

## The Problem

In 2026, AI-generated content is everywhere. Midjourney v6, Sora, Runway, and ChatGPT can produce photorealistic images, videos, and text that are nearly indistinguishable from real content. Deepfakes are no longer a futuristic concern — they're a daily reality.

The question is simple: **"Is this content real?"**

But the answer is complicated. Most existing verification tools require uploading your content to cloud servers — meaning you trade one privacy risk (not knowing if content is fake) for another (someone else now has a copy of your content).

## The Insight

> "The cure shouldn't be worse than the disease."

If a journalist receives a leaked image, they shouldn't have to upload it to a third-party server to verify it. If a parent sees a video of their child online, they shouldn't have to send it to a cloud service. If a fact-checker is verifying a viral image, they shouldn't add another data point to someone else's surveillance infrastructure.

**Privacy-first verification isn't a feature. It's a requirement.**

## The Solution: TrustCheck

TrustCheck is a privacy-first content authenticity verification tool that runs **entirely in your browser**.

### How It Works

When you upload an image to TrustCheck:

1. **Metadata Analysis** — We read the file's EXIF metadata and C2PA content credentials (Adobe's cryptographic provenance standard). This happens client-side — no data leaves your device.

2. **Frequency Analysis** — We analyze the image's pixel patterns using a custom Canvas-based frequency detector. AI-generated images tend to have statistical artifacts that differ from natural photography.

3. **Trust Score** — All evidence is combined into a single 0-100% Trust Score, displayed as a clean circular gauge.

4. **Optional AI Enhancement** — If you have a Venice AI API key, you can unlock deep vision-based analysis for even more accurate detection.

### Privacy-First by Design

- **Zero data leaves your device** — all analysis runs locally in your browser
- **No accounts** — no sign-up, no tracking, no cookies
- **No telemetry** — we don't collect usage data
- **Optional AI key** — Venice AI analysis only runs if you explicitly provide a key
- **PWA** — installable on your phone, works offline

### The Tech Stack

TrustCheck is built with vanilla HTML, CSS, and JavaScript — no frameworks, no build tools, no unnecessary dependencies. Just clean, transparent code that respects your privacy.

- **Frontend:** Vanilla HTML/CSS/JS, ES modules
- **Analysis:** Client-side EXIF parser, C2PA byte scanner, Canvas frequency analysis
- **AI:** Venice AI API (gemma-3-27b-it vision model, optional)
- **PWA:** Service Worker + Web App Manifest (installable, offline-capable)
- **Hosting:** Vercel (auto-deploy from GitHub)

## The Brand

TrustCheck's brand identity is built around the concept of **"Truth without compromise."** The brand archetype is a Sage + Guardian hybrid — a wise protector. The color palette uses Trust Blue (`#2563EB`) for reliability, Integrity Green (`#10B981`) for verified results, and Alert Red (`#EF4444`) for detected AI content.

## What's Next

Phase 2 is already in progress:

- **Venice AI deep integration** — auto-merge AI analysis into the unified trust score
- **Custom domain** — trustcheck.io (coming soon)
- **Browser extension** — right-click any image → "Check with TrustCheck"

## Try It

TrustCheck is live now at [trustcheck-zeta.vercel.app](https://trustcheck-zeta.vercel.app)

Open source on GitHub: [github.com/apartment30a81-create/trustcheck](https://github.com/apartment30a81-create/trustcheck)

---

*Built with Hermes Agent using the Web Project Agency workflow — brand strategy by BrandGuru, visual identity by Graphic Designer, development by Web Developer Specialist.*