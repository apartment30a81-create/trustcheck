#!/usr/bin/env python3
"""Generate TrustCheck brand identity assets - 3 logo variants, favicons, color palette."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

# === COLOR PALETTE ===
PRIMARY_BLUE = (37, 99, 235)       # #2563eb
PRIMARY_DARK = (29, 78, 216)       # #1d4ed8
PRIMARY_LIGHT = (96, 165, 250)     # #60a5fa
ACCENT_TEAL = (20, 184, 166)       # #14b8a6
ACCENT_GREEN = (34, 197, 94)       # #22c55e (verification/checkmark)
ACCENT_AMBER = (245, 158, 11)      # #f59e0b (warning/caution)
NEUTRAL_WHITE = (255, 255, 255)
NEUTRAL_BG = (248, 250, 252)       # #f8fafc (slate-50)
NEUTRAL_DARK = (15, 23, 42)        # #0f172a (slate-900)
NEUTRAL_GRAY = (100, 116, 139)     # #64748b (slate-500)
NEUTRAL_LIGHT = (226, 232, 240)    # #e2e8f0 (slate-200)

OUTPUT_DIR = "/root/spikes/trust-verify/trustcheck/brandguru-outputs"
FAVICON_DIR = "/root/spikes/trust-verify/trustcheck/favicon"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FAVICON_DIR, exist_ok=True)


def load_font(size, bold=False):
    """Try to load a nice sans-serif font, fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ]
    if bold:
        font_paths.insert(0, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def create_lettermark(size=2048):
    """Variant 1: Lettermark - stylized T icon with circular gauge/shield element."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    margin = size // 8
    
    # Outer ring - circular gauge/trust meter
    ring_outer = size // 2 - margin
    ring_inner = ring_outer - size // 25
    
    # Draw gauge arc (bottom ~60% of circle)
    gauge_bbox = [cx - ring_outer, cy - ring_outer + margin//2, 
                  cx + ring_outer, cy + ring_outer + margin//2]
    
    # Draw outer ring
    draw.ellipse(gauge_bbox, outline=PRIMARY_BLUE, width=size//30)
    
    # Draw inner filled circle (lighter)
    inner_r = ring_outer - size // 15
    inner_bbox = [cx - inner_r, cy - inner_r + margin//2, 
                  cx + inner_r, cy + inner_r + margin//2]
    draw.ellipse(inner_bbox, fill=None, outline=PRIMARY_LIGHT, width=size//50)
    
    # Gauge arc indicator - a filled arc segment (trust meter at ~75%)
    # Use pie slices for the gauge
    gauge_start = 135  # degrees (bottom-left)
    gauge_end = 45     # degrees (bottom-right) - going clockwise
    gauge_span = 270   # degrees total arc
    
    # Draw the gauge track (thin gray arc)
    track_width = size // 28
    for angle_deg in range(gauge_start, gauge_start + gauge_span, 2):
        rad = math.radians(angle_deg)
        x = cx + ring_outer * 0.85 * math.cos(rad)
        y = cy + margin//2 + ring_outer * 0.85 * math.sin(rad) + ring_outer * 0.08
        dot_r = track_width // 2
        draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=NEUTRAL_LIGHT)
    
    # Draw the active gauge arc (~75% filled) - from bottom traveling clockwise
    active_angle = 202  # ~75% of 270 degrees
    for angle_deg in range(gauge_start, gauge_start + active_angle, 2):
        rad = math.radians(angle_deg)
        x = cx + ring_outer * 0.85 * math.cos(rad)
        y = cy + margin//2 + ring_outer * 0.85 * math.sin(rad) + ring_outer * 0.08
        dot_r = track_width // 2
        draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=PRIMARY_BLUE)
    
    # Draw the T letterform inside the gauge
    t_size = size // 3
    t_thick = size // 14
    
    # vertical stem of T
    stem_x0 = cx - t_thick // 2
    stem_x1 = cx + t_thick // 2
    stem_y0 = cy - t_size // 3
    stem_y1 = cy + t_size // 3
    draw.rectangle([stem_x0, stem_y0, stem_x1, stem_y1], fill=PRIMARY_DARK)
    
    # horizontal crossbar of T
    bar_y0 = cy - t_size // 3
    bar_y1 = bar_y0 + t_thick
    bar_x0 = cx - t_size // 2
    bar_x1 = cx + t_size // 2
    draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], fill=PRIMARY_DARK)
    
    # Small checkmark accent inside the T's vertical stem
    check_size = size // 12
    check_cx = cx + t_thick // 2 + check_size // 2
    check_cy = cy + t_size // 6
    draw.line([(check_cx - check_size, check_cy), 
               (check_cx - check_size//3, check_cy + check_size//2),
               (check_cx + check_size//2, check_cy - check_size//3)], 
              fill=ACCENT_GREEN, width=max(size//60, 4))
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_lettermark.png"))
    print(f"✓ Lettermark logo saved ({size}x{size})")
    
    # Also save a version with white background for favicon use
    bg_img = Image.new("RGB", (size, size), NEUTRAL_WHITE)
    bg_img.paste(img, (0, 0), img)
    bg_img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_lettermark_bg.png"))
    
    return img


def create_wordmark(width=2400, height=600):
    """Variant 2: Wordmark - 'TrustCheck' custom text treatment."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_size = height // 3
    font = load_font(font_size, bold=True)
    
    # Measure text
    text = "TrustCheck"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Center the text
    x = (width - text_w) // 2
    y = (height - text_h) // 2
    
    # Draw text shadow/outline for depth
    shadow_offset = max(3, height // 60)
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=NEUTRAL_LIGHT, font=font)
    
    # Main text in primary blue
    draw.text((x, y), text, fill=PRIMARY_BLUE, font=font)
    
    # Add a subtle accent - small checkmark above letter 'k'
    smaller_font = load_font(font_size // 3, bold=False)
    check_text = "✓"
    cb = draw.textbbox((0, 0), check_text, font=smaller_font)
    check_w = cb[2] - cb[0]
    check_h = cb[3] - cb[1]
    
    # Position checkmark above and to the right
    # Find where 'k' is
    # Approximate: after "TrustChec" - let me estimate character widths
    prefix = "TrustChec"
    pb = draw.textbbox((0, 0), prefix, font=font)
    prefix_w = pb[2] - pb[0]
    
    # Draw a subtle underline accent bar under "Trust"
    trust_text = "Trust"
    tb = draw.textbbox((0, 0), trust_text, font=font)
    trust_w = tb[2] - tb[0]
    
    bar_y = y + text_h + height // 12
    bar_thickness = max(3, height // 30)
    draw.rounded_rectangle([x, bar_y, x + trust_w, bar_y + bar_thickness], 
                          radius=bar_thickness//2, fill=ACCENT_TEAL)
    
    # Also add a small gauge dot indicator near the checkmark
    gauge_dot_cy = y + check_h // 2
    gauge_dot_cx = x + prefix_w + font_size // 3
    dot_r = max(4, height // 20)
    draw.ellipse([gauge_dot_cx - dot_r, gauge_dot_cy - dot_r, 
                  gauge_dot_cx + dot_r, gauge_dot_cy + dot_r], 
                 fill=ACCENT_GREEN)
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_wordmark.png"))
    print(f"✓ Wordmark logo saved ({width}x{height})")
    
    bg_img = Image.new("RGB", (width, height), NEUTRAL_WHITE)
    bg_img.paste(img, (0, 0), img)
    bg_img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_wordmark_bg.png"))
    
    return img


def create_combination(size=2400, height=700):
    """Variant 3: Combination mark - icon + text side by side."""
    img = Image.new("RGBA", (size, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # --- Icon portion (left side, smaller) ---
    icon_size = int(height * 0.65)
    icon_margin = size // 20
    icon_x0 = icon_margin
    icon_y0 = (height - icon_size) // 2
    cx = icon_x0 + icon_size // 2
    cy = icon_y0 + icon_size // 2
    
    # Simplified T-shield icon
    # Outer ring
    ring_r = icon_size // 2 - 2
    draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 
                 outline=PRIMARY_BLUE, width=max(3, icon_size // 20))
    
    # Inner lighter ring
    inner_r = ring_r - icon_size // 12
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                 outline=PRIMARY_LIGHT, width=max(2, icon_size // 25))
    
    # T letterform
    t_thick = icon_size // 12
    t_h = icon_size // 2
    
    # Vertical stem
    stem_x0 = cx - t_thick // 2
    stem_x1 = cx + t_thick // 2
    stem_y0 = cy - t_h // 3
    stem_y1 = cy + t_h // 3
    draw.rectangle([stem_x0, stem_y0, stem_x1, stem_y1], fill=PRIMARY_DARK)
    
    # Horizontal crossbar
    bar_y0 = cy - t_h // 3
    bar_y1 = bar_y0 + t_thick
    bar_x0 = cx - t_h // 2
    bar_x1 = cx + t_h // 2
    draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], fill=PRIMARY_DARK)
    
    # Gauge arc on icon
    for angle_deg in range(135, 337, 3):
        rad = math.radians(angle_deg)
        x = cx + ring_r * 0.82 * math.cos(rad)
        y = cy + ring_r * 0.82 * math.sin(rad)
        dot_r = max(2, icon_size // 30)
        draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=PRIMARY_BLUE)
    
    # --- Text portion (right side) ---
    text_x = icon_x0 + icon_size + size // 15
    text_y_top = height // 4
    
    # "Trust" in regular weight
    trust_font = load_font(height // 4, bold=False)
    check_font = load_font(height // 4, bold=True)
    
    trust_text = "Trust"
    check_text = "Check"
    
    tb = draw.textbbox((0, 0), trust_text, font=trust_font)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    
    draw.text((text_x, text_y_top), trust_text, fill=NEUTRAL_DARK, font=trust_font)
    
    text_x2 = text_x + tw + height // 30
    draw.text((text_x2, text_y_top), check_text, fill=PRIMARY_BLUE, font=check_font)
    
    # Tagline below
    tagline_font = load_font(height // 8, bold=False)
    tagline = "Verify with confidence"
    tag_b = draw.textbbox((0, 0), tagline, font=tagline_font)
    tag_w = tag_b[2] - tag_b[0]
    
    tag_x = text_x
    tag_y = height // 2 + height // 6
    draw.text((tag_x, tag_y), tagline, fill=NEUTRAL_GRAY, font=tagline_font)
    
    # Small underline accent bar under "TrustCheck"
    bar_width = tw + height // 30 + (draw.textbbox((0, 0), check_text, font=check_font)[2] - draw.textbbox((0, 0), check_text, font=check_font)[0])
    bar_y = text_y_top + th + height // 20
    bar_h = max(3, height // 40)
    draw.rounded_rectangle([text_x, bar_y, text_x + bar_width, bar_y + bar_h],
                          radius=bar_h//2, fill=ACCENT_TEAL)
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_combination.png"))
    print(f"✓ Combination logo saved ({size}x{height})")
    
    bg_img = Image.new("RGB", (size, height), NEUTRAL_WHITE)
    bg_img.paste(img, (0, 0), img)
    bg_img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_combination_bg.png"))
    
    return img


def create_favicons(lettermark_img):
    """Generate favicon and app icon PNGs at various sizes from the lettermark."""
    sizes = [16, 32, 48, 57, 60, 72, 76, 96, 114, 120, 144, 152, 180, 192, 256, 512]
    
    # Get just the icon center portion from the lettermark
    sz = lettermark_img.width
    margin = sz // 20
    
    for s in sizes:
        # Crop centered with some padding removed
        crop_margin = sz // 6
        cropped = lettermark_img.crop((crop_margin, crop_margin, sz - crop_margin, sz - crop_margin))
        resized = cropped.resize((s, s), Image.LANCZOS)
        
        # Create background
        bg = Image.new("RGB", (s, s), PRIMARY_BLUE)
        bg.paste(resized, (0, 0), resized)
        
        # White bg version too
        bg_white = Image.new("RGB", (s, s), NEUTRAL_WHITE)
        bg_white.paste(resized, (0, 0), resized)
        
        if s == 192:
            bg.save(os.path.join(FAVICON_DIR, "android-chrome-192x192.png"))
            bg_white.save(os.path.join(FAVICON_DIR, "android-chrome-192x192-white.png"))
        elif s == 512:
            bg.save(os.path.join(FAVICON_DIR, "android-chrome-512x512.png"))
            bg_white.save(os.path.join(FAVICON_DIR, "android-chrome-512x512-white.png"))
        elif s == 180:
            bg.save(os.path.join(FAVICON_DIR, "apple-touch-icon.png"))
            bg_white.save(os.path.join(FAVICON_DIR, "apple-touch-icon-white.png"))
        elif s == 144:
            bg.save(os.path.join(FAVICON_DIR, "msapplication-icon-144x144.png"))
        elif s in (16, 32, 48, 96):
            bg_white.save(os.path.join(FAVICON_DIR, f"favicon-{s}x{s}.png"))
        elif s in (57, 60, 72, 76, 114, 120, 152):
            pass  # Apple touch sizes, covered by 180
    
    # Create a multi-size favicon.ico approximation (PNG)
    # Most browsers support PNG favicons now, but let's make a 32x32 as default
    favicon_32 = Image.new("RGB", (32, 32), PRIMARY_BLUE)
    cropped = lettermark_img.crop((sz//6, sz//6, sz - sz//6, sz - sz//6))
    resized = cropped.resize((24, 24), Image.LANCZOS)
    favicon_32.paste(resized, (4, 4), resized)
    favicon_32.save(os.path.join(FAVICON_DIR, "favicon.png"))
    
    # Also save as favicon.ico if we can
    try:
        favicon_32.save(os.path.join(FAVICON_DIR, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
        print("✓ favicon.ico created")
    except Exception as e:
        print(f"  favicon.ico skipped ({e})")
        # Save as PNG instead
        favicon_32.save(os.path.join(FAVICON_DIR, "favicon.ico"))
    
    print(f"✓ Favicons generated ({len(sizes)} sizes)")


def create_horizontal_lockup(size=2400, height=600):
    """Horizontal lockup for headers - darker variant for light backgrounds."""
    img = Image.new("RGBA", (size, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Icon on left
    icon_size = int(height * 0.7)
    cx = icon_size // 2 + 10
    cy = height // 2
    
    ring_r = icon_size // 2 - 2
    draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 
                 outline=PRIMARY_BLUE, width=max(3, icon_size // 20))
    
    t_thick = icon_size // 12
    t_h = icon_size // 2
    stem_x0 = cx - t_thick // 2
    stem_x1 = cx + t_thick // 2
    stem_y0 = cy - t_h // 3
    stem_y1 = cy + t_h // 3
    draw.rectangle([stem_x0, stem_y0, stem_x1, stem_y1], fill=PRIMARY_BLUE)
    bar_y0 = cy - t_h // 3
    bar_y1 = bar_y0 + t_thick
    bar_x0 = cx - t_h // 2
    bar_x1 = cx + t_h // 2
    draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], fill=PRIMARY_BLUE)
    
    # "TrustCheck" text
    text_x = icon_size + height // 6
    font = load_font(height // 3, bold=True)
    text = "TrustCheck"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    draw.text((text_x, (height - th) // 2 - 5), text, fill=NEUTRAL_DARK, font=font)
    
    # Underline
    bar_y = (height - th) // 2 - 5 + th + height // 15
    bar_h = max(2, height // 50)
    draw.rounded_rectangle([text_x, bar_y, text_x + tw, bar_y + bar_h],
                          radius=bar_h//2, fill=ACCENT_TEAL)
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_horizontal_lockup.png"))
    
    bg_img = Image.new("RGB", (size, height), NEUTRAL_WHITE)
    bg_img.paste(img, (0, 0), img)
    bg_img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_horizontal_lockup_bg.png"))
    print(f"✓ Horizontal lockup saved ({size}x{height})")


def create_dark_variants():
    """Create dark-background versions of the logos."""
    
    # Lettermark on dark
    img = Image.new("RGB", (1024, 1024), NEUTRAL_DARK)
    draw = ImageDraw.Draw(img)
    cx, cy = 512, 512
    margin = 128
    
    ring_r = 512 - margin
    draw.ellipse([cx - ring_r, cy - ring_r + margin//2, cx + ring_r, cy + ring_r + margin//2], 
                 outline=PRIMARY_LIGHT, width=10)
    
    inner_r = ring_r - 25
    draw.ellipse([cx - inner_r, cy - inner_r + margin//2, cx + inner_r, cy + inner_r + margin//2],
                 outline=PRIMARY_BLUE, width=6)
    
    t_size = 350
    t_thick = 30
    stem_x0 = cx - t_thick // 2
    stem_x1 = cx + t_thick // 2
    stem_y0 = cy - t_size // 3
    stem_y1 = cy + t_size // 3
    draw.rectangle([stem_x0, stem_y0, stem_x1, stem_y1], fill=NEUTRAL_WHITE)
    bar_y0 = cy - t_size // 3
    bar_y1 = bar_y0 + t_thick
    bar_x0 = cx - t_size // 2
    bar_x1 = cx + t_size // 2
    draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], fill=NEUTRAL_WHITE)
    
    # Gauge dots on dark
    for angle_deg in range(135, 337, 3):
        rad = math.radians(angle_deg)
        x = cx + ring_r * 0.85 * math.cos(rad)
        y = cy + margin//2 + ring_r * 0.85 * math.sin(rad) + ring_r * 0.08
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=PRIMARY_LIGHT)
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_lettermark_dark.png"))
    
    # Wordmark on dark
    img2 = Image.new("RGB", (1600, 400), NEUTRAL_DARK)
    draw2 = ImageDraw.Draw(img2)
    font = load_font(120, bold=True)
    text = "TrustCheck"
    bbox = draw2.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (1600 - tw) // 2
    y = (400 - th) // 2
    draw2.text((x, y), text, fill=NEUTRAL_WHITE, font=font)
    
    trust_w = draw2.textbbox((0, 0), "Trust", font=font)[2] - draw2.textbbox((0, 0), "Trust", font=font)[0]
    bar_yy = y + th + 10
    draw2.rounded_rectangle([x, bar_yy, x + trust_w, bar_yy + 5], radius=2, fill=ACCENT_TEAL)
    
    img2.save(os.path.join(OUTPUT_DIR, "trustcheck_logo_wordmark_dark.png"))
    
    print("✓ Dark variants created")


def create_brand_pattern():
    """Create a subtle brand pattern/background texture."""
    size = 800
    img = Image.new("RGB", (size, size), NEUTRAL_WHITE)
    draw = ImageDraw.Draw(img)
    
    # Subtle grid of small T symbols
    step = 80
    for row in range(0, size, step):
        for col in range(0, size, step):
            alpha = 0.03  # very subtle
            cx, cy = col + step // 2, row + step // 2
            s = step // 4
            
            # Tiny T
            t = max(2, s // 8)
            draw.rectangle([cx - t//2, cy - s//4, cx + t//2, cy + s//4], 
                          fill=(37, 99, 235, 20))
            draw.rectangle([cx - s//2, cy - s//4, cx + s//2, cy - s//4 + t], 
                          fill=(37, 99, 235, 20))
    
    # Top-level: save at reduced opacity
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_brand_pattern.png"))
    print("✓ Brand pattern created")


def create_social_media_kit():
    """Generate social media profile images."""
    
    # Twitter/X profile (400x400)
    img = Image.new("RGB", (400, 400), PRIMARY_BLUE)
    draw = ImageDraw.Draw(img)
    cx, cy = 200, 200
    
    # White T mark
    t_size = 160
    t_thick = 18
    stem_x0 = cx - t_thick // 2
    stem_x1 = cx + t_thick // 2
    stem_y0 = cy - t_size // 3
    stem_y1 = cy + t_size // 3
    draw.rectangle([stem_x0, stem_y0, stem_x1, stem_y1], fill=NEUTRAL_WHITE)
    bar_y0 = cy - t_size // 3
    bar_y1 = bar_y0 + t_thick
    bar_x0 = cx - t_size // 2
    bar_x1 = cx + t_size // 2
    draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], fill=NEUTRAL_WHITE)
    
    # Ring
    ring_r = 140
    draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 
                 outline=(255, 255, 255, 60), width=4)
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_social_profile_twitter.png"))
    
    # Facebook/LinkedIn profile (400x400) - different angle
    img = Image.new("RGB", (400, 400), NEUTRAL_WHITE)
    draw = ImageDraw.Draw(img)
    cx, cy = 200, 200
    
    ring_r = 140
    draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 
                 outline=PRIMARY_BLUE, width=6)
    
    inner_r = 130
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                 outline=PRIMARY_LIGHT, width=3)
    
    t_size = 140
    t_thick = 16
    stem_x0 = cx - t_thick // 2
    stem_x1 = cx + t_thick // 2
    stem_y0 = cy - t_size // 3
    stem_y1 = cy + t_size // 3
    draw.rectangle([stem_x0, stem_y0, stem_x1, stem_y1], fill=PRIMARY_BLUE)
    bar_y0 = cy - t_size // 3
    bar_y1 = bar_y0 + t_thick
    bar_x0 = cx - t_size // 2
    bar_x1 = cx + t_size // 2
    draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], fill=PRIMARY_BLUE)
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_social_profile_linkedin.png"))
    
    # GitHub social preview (1280x640)
    img = Image.new("RGB", (1280, 640), NEUTRAL_DARK)
    draw = ImageDraw.Draw(img)
    
    # Left: Icon
    cx, cy = 300, 320
    ring_r = 180
    draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], 
                 outline=PRIMARY_LIGHT, width=8)
    inner_r = 165
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                 outline=PRIMARY_BLUE, width=5)
    
    t_size_big = 180
    t_thick_big = 20
    draw.rectangle([cx - t_thick_big//2, cy - t_size_big//3, cx + t_thick_big//2, cy + t_size_big//3], fill=NEUTRAL_WHITE)
    draw.rectangle([cx - t_size_big//2, cy - t_size_big//3, cx + t_size_big//2, cy - t_size_big//3 + t_thick_big], fill=NEUTRAL_WHITE)
    
    # Right: Text
    font = load_font(96, bold=True)
    text = "TrustCheck"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((520, 280 - th//2), text, fill=NEUTRAL_WHITE, font=font)
    
    tag_font = load_font(36, bold=False)
    tagline = "Privacy-first content authenticity verification"
    tb = draw.textbbox((0, 0), tagline, font=tag_font)
    tw2 = tb[2] - tb[0]
    draw.text((520, 360), tagline, fill=NEUTRAL_GRAY, font=tag_font)
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_social_preview_github.png"))
    
    print("✓ Social media kit created")


def create_color_swatches():
    """Generate color palette reference image."""
    size = 1600, 800
    img = Image.new("RGB", size, NEUTRAL_WHITE)
    draw = ImageDraw.Draw(img)
    
    colors = [
        ("Primary Blue", PRIMARY_BLUE, "#2563eb"),
        ("Primary Dark", PRIMARY_DARK, "#1d4ed8"),
        ("Primary Light", PRIMARY_LIGHT, "#60a5fa"),
        ("Accent Teal", ACCENT_TEAL, "#14b8a6"),
        ("Accent Green", ACCENT_GREEN, "#22c55e"),
        ("Accent Amber", ACCENT_AMBER, "#f59e0b"),
        ("Dark Text", NEUTRAL_DARK, "#0f172a"),
        ("Gray Text", NEUTRAL_GRAY, "#64748b"),
        ("Light BG", NEUTRAL_BG, "#f8fafc"),
    ]
    
    swatch_w = 140
    swatch_h = 140
    gap = 20
    start_x = (size[0] - (len(colors) * (swatch_w + gap) - gap)) // 2
    y = 150
    
    font = load_font(16, bold=False)
    name_font = load_font(14, bold=True)
    
    for i, (name, rgb, hex_code) in enumerate(colors):
        x = start_x + i * (swatch_w + gap)
        
        # Color swatch
        draw.rounded_rectangle([x, y, x + swatch_w, y + swatch_h], 
                              radius=12, fill=rgb)
        
        # Name
        nb = draw.textbbox((0, 0), name, font=name_font)
        nw = nb[2] - nb[0]
        draw.text((x + (swatch_w - nw) // 2, y + swatch_h + 8), name, fill=NEUTRAL_DARK, font=name_font)
        
        # Hex
        hb = draw.textbbox((0, 0), hex_code, font=font)
        hw = hb[2] - hb[0]
        draw.text((x + (swatch_w - hw) // 2, y + swatch_h + 28), hex_code, fill=NEUTRAL_GRAY, font=font)
    
    # Title
    title_font = load_font(36, bold=True)
    title = "TrustCheck Brand Color Palette"
    tb2 = draw.textbbox((0, 0), title, font=title_font)
    tw3 = tb2[2] - tb2[0]
    draw.text(((size[0] - tw3) // 2, 40), title, fill=NEUTRAL_DARK, font=title_font)
    
    # Section subtitle
    subtitle = "Primary / Accent / Neutral"
    sub_font = load_font(20, bold=False)
    sb = draw.textbbox((0, 0), subtitle, font=sub_font)
    sw = sb[2] - sb[0]
    draw.text(((size[0] - sw) // 2, 90), subtitle, fill=NEUTRAL_GRAY, font=sub_font)
    
    # Usage notes
    notes = [
        "Primary: UI elements, buttons, links, logo",
        "Accent Teal: Secondary CTAs, progress indicators, decorative elements",
        "Accent Green: Verification badges, checkmarks, success states",
        "Accent Amber: Warnings, caution indicators, trust meter mid-range",
        "Dark/Gray: Body text, labels, secondary information",
        "Light BG: Page backgrounds, card surfaces",
    ]
    note_y = y + swatch_h + 70
    for note in notes:
        draw.text((start_x, note_y), f"• {note}", fill=NEUTRAL_DARK, font=font)
        note_y += 26
    
    img.save(os.path.join(OUTPUT_DIR, "trustcheck_color_palette.png"))
    print("✓ Color palette swatches created")


# === MAIN EXECUTION ===
if __name__ == "__main__":
    print("=" * 60)
    print("  TrustCheck Brand Identity Generator")
    print("=" * 60)
    print()

    # Step 1: Lettermark
    print("[1/8] Creating Lettermark logo...")
    lettermark = create_lettermark()

    # Step 2: Wordmark
    print("[2/8] Creating Wordmark logo...")
    wordmark = create_wordmark()

    # Step 3: Combination mark
    print("[3/8] Creating Combination logo...")
    combination = create_combination()

    # Step 4: Horizontal lockup
    print("[4/8] Creating horizontal lockup...")
    create_horizontal_lockup()

    # Step 5: Favicon/App icons
    print("[5/8] Generating favicons...")
    create_favicons(lettermark)

    # Step 6: Dark variants
    print("[6/8] Creating dark background variants...")
    create_dark_variants()

    # Step 7: Brand pattern & social kit
    print("[7/8] Creating brand pattern and social media kit...")
    create_brand_pattern()
    create_social_media_kit()

    # Step 8: Color swatches
    print("[8/8] Creating color palette reference...")
    create_color_swatches()

    print()
    print("=" * 60)
    print("  ✅ All brand assets generated successfully!")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Favicons: {FAVICON_DIR}")
    print("=" * 60)