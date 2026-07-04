#!/usr/bin/env python3
"""Generate programmatic SEO pages (invoice templates by profession) + sitemap.

Usage: python3 generator/build.py [BASE_URL]
BASE_URL defaults to a placeholder; rerun with the real URL after deployment.
"""
import json
import os
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "https://invoicelark.github.io").rstrip("/")

with open(os.path.join(ROOT, "generator", "data", "professions.json")) as f:
    PROFESSIONS = json.load(f)

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="{prefix}css/style.css">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="logo" href="{prefix}">Invoice<span>Lark</span></a>
    <nav class="main">
      <a href="{prefix}invoice-generator/">Invoice Generator</a>
      <a href="{prefix}hourly-rate-calculator/">Rate Calculator</a>
      <a href="{prefix}invoice-template/">Templates</a>
    </nav>
  </div>
</header>
<main>
<div class="wrap">
"""

FOOT = """</div>
</main>
<footer class="site">
  <div class="wrap">
    <p>© 2026 InvoiceLark — free tools for freelancers. <a href="{prefix}about/">About</a> · <a href="{prefix}privacy/">Privacy</a></p>
    <p>This site provides general information, not tax, legal or financial advice.</p>
  </div>
</footer>
</body>
</html>
"""


def write(path, html):
    full = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(html)
    print("wrote", path)


def profession_page(p):
    prefix = "../../"
    name = p["name"]
    prefill = urllib.parse.quote("|".join(p["items"][:4]))
    items_rows = "\n".join(
        f'    <tr><td>{item}</td></tr>' for item in p["items"]
    )
    title = f"{name} Invoice Template — Free Example & Generator"
    desc = (
        f"Free {name.lower()} invoice template with realistic example line items, "
        f"typical rates, and billing tips. Open it in our free generator and download a PDF in a minute."
    )
    body = f"""
  <div class="crumbs"><a href="{prefix}">Home</a> › <a href="../">Invoice templates</a> › {name}</div>
  <h1>{name} Invoice Template</h1>
  <p class="subtitle">{p['intro']}</p>

  <p><a class="btn" href="{prefix}invoice-generator/?items={prefill}">Open this template in the free generator →</a></p>
  <p class="result-note">The generator pre-fills the line items below. Edit them, add your details, and download a clean PDF — free, no sign-up.</p>

  <h2>Example line items for a {name.lower()} invoice</h2>
  <table class="simple">
    <tr><th>Line item</th></tr>
{items_rows}
  </table>

  <h2>Typical {name.lower()} rates</h2>
  <p>{p['rate']}. Rates vary by market and experience — if you're unsure where you sit, run your numbers through our <a href="{prefix}hourly-rate-calculator/">hourly rate calculator</a>.</p>

  <h2>Billing tip for {name.lower()}s</h2>
  <p>{p['tips']}</p>

  <div class="reco" data-slot="affiliate-template">
    <strong>Tired of chasing payments?</strong> Put your payment terms and a late-fee clause on every invoice (our <a href="{prefix}late-fee-calculator/">late fee calculator</a> shows what an overdue balance actually costs your client), and make paying you as frictionless as possible.
  </div>

  <h2>What every {name.lower()} invoice needs</h2>
  <ol>
    <li>A unique invoice number and issue date</li>
    <li>Your business name, contact details (and tax/license ID where required)</li>
    <li>The client's name and billing details</li>
    <li>Clear line items — like the examples above — with quantities and rates</li>
    <li>Subtotal, any tax, and the total due</li>
    <li>Payment terms: due date, accepted methods, and your late-fee policy</li>
  </ol>
  <p>Ready to bill? <a href="{prefix}invoice-generator/?items={prefill}">Create your {name.lower()} invoice now</a> — it takes about a minute.</p>
"""
    head = HEAD.format(
        title=title,
        description=desc,
        canonical=f"{BASE_URL}/invoice-template/{p['slug']}/",
        prefix=prefix,
    )
    return head + body + FOOT.format(prefix=prefix)


def hub_page():
    prefix = "../"
    cards = "\n".join(
        f'    <a class="card tool-card" href="{p["slug"]}/"><h3>{p["name"]}</h3>'
        f"<p>Example line items, typical rates, and billing tips.</p></a>"
        for p in PROFESSIONS
    )
    head = HEAD.format(
        title="Free Invoice Templates by Profession — 20+ Real Examples",
        description="Free invoice templates with realistic example line items for 20+ professions: designers, developers, photographers, cleaners, trades and more. Open any of them in our free PDF generator.",
        canonical=f"{BASE_URL}/invoice-template/",
        prefix=prefix,
    )
    body = f"""
  <h1>Invoice Templates by Profession</h1>
  <p class="subtitle">Generic templates make you do the hard part — figuring out what to actually put on the invoice. Each template below comes with realistic line items, typical rates, and one hard-earned billing tip for that line of work. Open any of them in the <a href="{prefix}invoice-generator/">free invoice generator</a> and download a PDF.</p>
  <div class="grid">
{cards}
  </div>
"""
    return head + body + FOOT.format(prefix=prefix)


def sitemap():
    static = [
        "",
        "invoice-generator/",
        "hourly-rate-calculator/",
        "late-fee-calculator/",
        "freelance-quote-calculator/",
        "invoice-template/",
        "about/",
        "privacy/",
    ]
    urls = static + [f"invoice-template/{p['slug']}/" for p in PROFESSIONS]
    entries = "\n".join(
        f"  <url><loc>{BASE_URL}/{u}</loc></url>" for u in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n"
    )


def main():
    for p in PROFESSIONS:
        write(f"invoice-template/{p['slug']}/index.html", profession_page(p))
    write("invoice-template/index.html", hub_page())
    write("sitemap.xml", sitemap())
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    print(f"\nDone: {len(PROFESSIONS)} profession pages + hub + sitemap (base: {BASE_URL})")


if __name__ == "__main__":
    main()
