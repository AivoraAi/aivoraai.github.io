#!/usr/bin/env python3
"""
====================================================
  AIVORA AI — RESTORE SCRIPT
  Restores ALL files from _seo_backups/ folder
  Run this to undo all SEO script changes
====================================================
  HOW TO USE:
  1. Put this file in your repo root folder
  2. Run: python aivora_restore.py
  3. Then: git add . && git commit -m "Restore original files" && git push
====================================================
"""

import os, shutil, glob
from datetime import datetime

REPO_ROOT   = "."
BACKUP_DIR  = os.path.join(REPO_ROOT, "_seo_backups")
TODAY       = datetime.today().strftime("%Y-%m-%d %H:%M")

print("\n" + "="*52)
print("  AIVORA AI — RESTORE SCRIPT")
print(f"  Time: {TODAY}")
print("="*52 + "\n")

# Check backup folder exists
if not os.path.exists(BACKUP_DIR):
    print("❌ _seo_backups/ folder not found!")
    print("   Script may not have run, or backups were deleted.")
    print("   Try restoring from git: git checkout HEAD -- .")
    exit(1)

backup_files = glob.glob(os.path.join(BACKUP_DIR, "*.html"))

if not backup_files:
    print("❌ No backup HTML files found in _seo_backups/")
    print("   Try: git checkout HEAD -- .")
    exit(1)

print(f"📁 Found {len(backup_files)} backup files\n")
print("🔄 Restoring files...\n")

restored = 0
failed   = 0

for backup_path in backup_files:
    # Convert backup filename back to original path
    # backup name: "blog_gpt-creator-club-review-2026.html"
    # original:    "blog/gpt-creator-club-review-2026.html"
    fname = os.path.basename(backup_path)

    # Try to figure out original path from backup filename
    # Pattern: folder_filename.html → folder/filename.html
    
    original_path = None
    
    # Check common patterns
    candidates = []
    
    # blog_something.html → blog/something.html
    if fname.startswith("blog_"):
        candidates.append(os.path.join(REPO_ROOT, "blog", fname[5:]))
    
    # Root level files: index.html, blog.html, about.html etc
    candidates.append(os.path.join(REPO_ROOT, fname))
    
    # Also try replacing first _ with /
    parts = fname.split("_", 1)
    if len(parts) == 2:
        candidates.append(os.path.join(REPO_ROOT, parts[0], parts[1]))

    for candidate in candidates:
        if os.path.exists(candidate):
            original_path = candidate
            break
        # Also try even if it doesn't exist (it might have been deleted)
        if candidate.endswith(".html"):
            original_path = candidate
            break

    if not original_path:
        original_path = os.path.join(REPO_ROOT, fname)

    try:
        os.makedirs(os.path.dirname(original_path), exist_ok=True)
        shutil.copy2(backup_path, original_path)
        rel = os.path.relpath(original_path, REPO_ROOT)
        print(f"  ✅ Restored: {rel}")
        restored += 1
    except Exception as e:
        print(f"  ❌ Failed:   {backup_path} → {e}")
        failed += 1

print(f"\n{'='*52}")
print(f"  RESTORE COMPLETE")
print(f"{'='*52}")
print(f"  Restored: {restored} files")
print(f"  Failed:   {failed} files")
print()
print("  Ab yeh run karo:")
print("  git add .")
print('  git commit -m "Restore: undo SEO script changes"')
print("  git push")
print()
print("  Site 2-3 minute mein wapas normal ho jayegi!")
print()
