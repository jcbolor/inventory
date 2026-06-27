#!/usr/bin/env python3
"""
RAKS Invoicing - Branding Patch Script
Patches compiled Flutter dart.js bundles to:
  1. Change "Invoice Ninja" → "RAKS Invoicing"
  2. Remove Purchase White Label button from About modal
  3. Change Contact Us link to bizlabitsolutions.com/contact
  4. Remove Support Forum icon from sidebar
  5. Remove all social media icons from About modal
"""

import shutil
import os
import sys

PUBLIC_DIR = '/var/www/vhosts/inventory.local/web/public'

FILES_TO_PATCH = [
    'main.dart.js',
    'main.foss.dart.js',
    'main.next.dart.js',
    'main.last.dart.js',
]

def patch_file(filepath):
    if not os.path.exists(filepath):
        print(f'  SKIP (not found): {filepath}')
        return

    # Backup
    backup = filepath + '.bak'
    if not os.path.exists(backup):
        shutil.copy2(filepath, backup)
        print(f'  Backed up to: {backup}')
    else:
        print(f'  Backup already exists, skipping backup.')

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    original_content = content
    changes = []

    # ─────────────────────────────────────────────────────────
    # 1. Change "Invoice Ninja" → "RAKS Invoicing"
    #    Targets the About dialog title text widget
    # ─────────────────────────────────────────────────────────
    OLD = 'A.j("Invoice Ninja",'
    NEW = 'A.j("RAKS Invoicing",'
    count = content.count(OLD)
    if count > 0:
        content = content.replace(OLD, NEW)
        changes.append(f'[1] Replaced "Invoice Ninja" title text ({count}x)')
    else:
        changes.append('[1] WARNING: "Invoice Ninja" title text NOT FOUND')

    # Also handle the plain string version (in error messages etc.)
    OLD2 = '"Invoice Ninja"'
    NEW2 = '"RAKS Invoicing"'
    count2 = content.count(OLD2)
    if count2 > 0:
        content = content.replace(OLD2, NEW2)
        changes.append(f'[1b] Replaced plain "Invoice Ninja" string ({count2}x)')

    # ─────────────────────────────────────────────────────────
    # 2. Remove Purchase White Label / review_app button from About modal
    #    The block is: if(B.e.d6(...).a,864e8)>30){ ... m.push(new A.e2(B.rP,B.aE3,...eHI...)) }
    #    We null out the push by replacing with a no-op check
    # ─────────────────────────────────────────────────────────
    OLD_REVIEW = (
        'if(B.e.d6(new A.bz(Date.now(),0,!1).jy(A.tX(h.f.iC)).a,864e8)>30)'
        '{h=g.h(0,f)\nh.toString\nh=J.c(h,i)\nif(h==null){h=g.h(0,"en")\nh.toString\nh=J.c(h,i)\nh.toString}'
        'm.push(new A.e2(B.rP,B.aE3,h.toUpperCase(),new A.eHI(a),j,j))}'
    )
    NEW_REVIEW = '/* purchase_white_label removed */'
    if OLD_REVIEW in content:
        content = content.replace(OLD_REVIEW, NEW_REVIEW)
        changes.append('[2] Removed Purchase White Label / review_app button')
    else:
        # Try with \r\n line endings
        OLD_REVIEW2 = OLD_REVIEW.replace('\n', '\r\n')
        if OLD_REVIEW2 in content:
            content = content.replace(OLD_REVIEW2, NEW_REVIEW)
            changes.append('[2] Removed Purchase White Label / review_app button (CRLF)')
        else:
            changes.append('[2] WARNING: review_app/purchase button block NOT FOUND — trying fallback')
            # Fallback: find the eHI handler push and null it
            FALLBACK = 'm.push(new A.e2(B.rP,B.aE3,h.toUpperCase(),new A.eHI(a),j,j))'
            if FALLBACK in content:
                content = content.replace(FALLBACK, '/* purchase_white_label removed */')
                changes.append('[2b] Removed eHI (review_app) push via fallback')
            else:
                changes.append('[2b] WARNING: eHI fallback also NOT FOUND')

    # ─────────────────────────────────────────────────────────
    # 3. Change Contact Us link: slack.invoiceninja.com → bizlabitsolutions.com/contact
    #    The cST handler calls A.fJD() - we patch the URL in the cST handler block
    #    The URL is in the sidebar via cST and in eHC (About modal Slack icon)
    # ─────────────────────────────────────────────────────────
    OLD_SLACK = '"http://slack.invoiceninja.com"'
    NEW_SLACK = '"http://bizlabitsolutions.com/contact"'
    count3 = content.count(OLD_SLACK)
    if count3 > 0:
        content = content.replace(OLD_SLACK, NEW_SLACK)
        changes.append(f'[3] Changed Contact Us URL (slack → bizlab) ({count3}x)')

    OLD_SLACK_HTTPS = '"https://slack.invoiceninja.com"'
    count3b = content.count(OLD_SLACK_HTTPS)
    if count3b > 0:
        content = content.replace(OLD_SLACK_HTTPS, '"http://bizlabitsolutions.com/contact"')
        changes.append(f'[3b] Changed HTTPS slack URL ({count3b}x)')

    # ─────────────────────────────────────────────────────────
    # 4. Remove Support Forum sidebar icon
    #    The cSU handler launches https://forum.invoiceninja.com
    #    We remove the m.push() call for the support_forum item
    # ─────────────────────────────────────────────────────────
    OLD_FORUM_PUSH = (
        'k=A.aM(B.Ov,i,i,i)\n'
        'if(p){r.toString\nq=$.l().h(0,r.a)\nq.toString\nq=J.c(q,"support_forum")\nq.toString}else q=""\n'
        'm.push(A.bP(i,i,i,i,i,i,k,i,i,new A.cSU(),i,i,i,i,q,i))'
    )
    NEW_FORUM_PUSH = '/* support_forum removed */'
    if OLD_FORUM_PUSH in content:
        content = content.replace(OLD_FORUM_PUSH, NEW_FORUM_PUSH)
        changes.append('[4] Removed Support Forum sidebar icon')
    else:
        # Try alternate line endings
        OLD_FORUM_PUSH2 = OLD_FORUM_PUSH.replace('\n', '\r\n')
        if OLD_FORUM_PUSH2 in content:
            content = content.replace(OLD_FORUM_PUSH2, NEW_FORUM_PUSH)
            changes.append('[4] Removed Support Forum sidebar icon (CRLF)')
        else:
            # Fallback: just remove the cSU push
            FORUM_FALLBACK = 'm.push(A.bP(i,i,i,i,i,i,k,i,i,new A.cSU(),i,i,i,i,q,i))'
            if FORUM_FALLBACK in content:
                content = content.replace(FORUM_FALLBACK, '/* support_forum removed */')
                changes.append('[4b] Removed Support Forum push via fallback')
            else:
                changes.append('[4] WARNING: Support Forum push NOT FOUND')

    # ─────────────────────────────────────────────────────────
    # 5. Remove all social media icons from About modal
    #    Replace the full array of icon buttons with empty array []
    # ─────────────────────────────────────────────────────────
    OLD_SOCIAL = (
        'A.bP(j,j,j,j,j,j,A.aM(B.c67,j,j,j),j,j,new A.eHK(),j,j,j,j,"Twitter",j),'
        'A.bP(j,j,j,j,j,j,A.aM(B.c5E,j,j,j),j,j,new A.eHz(),j,j,j,j,"Facebook",j),'
        'A.bP(j,j,j,j,j,j,A.aM(B.c5h,j,j,j),j,j,new A.eHA(),j,j,j,j,"GitHub",j),'
        'A.bP(j,j,j,j,j,j,A.aM(B.c59,j,j,j),j,j,new A.eHB(),j,j,j,j,"YouTube",j),'
        'A.bP(j,j,j,j,j,j,A.aM(B.c5G,j,j,j),j,j,new A.eHC(),j,j,j,j,"Slack",j)'
    )
    NEW_SOCIAL = ''  # empty array, already wrapped in A.b([...])
    if OLD_SOCIAL in content:
        content = content.replace(OLD_SOCIAL, NEW_SOCIAL)
        changes.append('[5] Removed all social media icons from About modal')
    else:
        changes.append('[5] WARNING: Social icons block NOT FOUND — trying partial match')
        # Try removing each individually as fallback
        icons = [
            ('A.bP(j,j,j,j,j,j,A.aM(B.c67,j,j,j),j,j,new A.eHK(),j,j,j,j,"Twitter",j)', 'Twitter'),
            ('A.bP(j,j,j,j,j,j,A.aM(B.c5E,j,j,j),j,j,new A.eHz(),j,j,j,j,"Facebook",j)', 'Facebook'),
            ('A.bP(j,j,j,j,j,j,A.aM(B.c5h,j,j,j),j,j,new A.eHA(),j,j,j,j,"GitHub",j)', 'GitHub'),
            ('A.bP(j,j,j,j,j,j,A.aM(B.c59,j,j,j),j,j,new A.eHB(),j,j,j,j,"YouTube",j)', 'YouTube'),
            ('A.bP(j,j,j,j,j,j,A.aM(B.c5G,j,j,j),j,j,new A.eHC(),j,j,j,j,"Slack",j)', 'Slack'),
        ]
        for icon_str, name in icons:
            # Remove including potential trailing comma
            for variant in [icon_str + ',', ',' + icon_str, icon_str]:
                if variant in content:
                    content = content.replace(variant, '')
                    changes.append(f'[5b] Removed {name} icon via fallback')
                    break

    # ─────────────────────────────────────────────────────────
    # Write patched file
    # ─────────────────────────────────────────────────────────
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  ✅ PATCHED: {os.path.basename(filepath)}')
    else:
        print(f'  ⚠️  NO CHANGES made to {os.path.basename(filepath)}')

    for c in changes:
        print(f'    {c}')


if __name__ == '__main__':
    print('=== RAKS Invoicing Branding Patch ===\n')
    for fname in FILES_TO_PATCH:
        fpath = os.path.join(PUBLIC_DIR, fname)
        print(f'Processing: {fname}')
        patch_file(fpath)
        print()
    print('Done.')
