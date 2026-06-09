name: SEO Auto Fix — Aivora AI

# Kab chalega yeh action?
on:
  push:
    branches: [ main ]        # Jab bhi koi file push karo
  workflow_dispatch:           # Ya manually GitHub pe se button dabao
  schedule:
    - cron: '0 0 * * 1'       # Aur har Somwar raat ko automatically

jobs:
  seo-fix:
    runs-on: ubuntu-latest
    name: Fix SEO Issues Automatically

    permissions:
      contents: write           # GitHub ko files likhne ki permission

    steps:

      # Step 1: Repo download karo
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # Step 2: Python setup karo
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # Step 3: SEO fix script chalao
      - name: Run SEO Fix Script
        run: python aivora_seo_fix.py

      # Step 4: Jo bhi fix hua, woh commit aur push karo
      - name: Commit and Push fixes
        run: |
          git config user.name "Aivora SEO Bot"
          git config user.email "aivoraai@outlook.com"
          git add .
          git diff --staged --quiet || git commit -m "🤖 Auto SEO Fix: dates, canonicals, internal links, sitemap — $(date +'%Y-%m-%d')"
          git push
