#!/usr/bin/env python3
# get_history.cgi
# Reads all past submissions from the database and renders the history page.

import sys
import os
import html

# Add lib directory to path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib')
)

from db_connect import get_connection

# Print HTTP header
print("Content-Type: text/html")
print()

# ---- Connect to DB and fetch all submissions ----
conn = get_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute(
    "SELECT submission_id, submission_name, enzyme_ids_used, analysis_mode, "
    "cut_positions, fragment_sizes, submission_date "
    "FROM submissions ORDER BY submission_date DESC"
)
submissions = cursor.fetchall()

# ---- Calculate metrics ----
total = len(submissions)
specific_count = 0
full_scan_count = 0
for s in submissions:
    if s['analysis_mode'] == 'specific':
        specific_count += 1
    elif s['analysis_mode'] == 'full_scan':
        full_scan_count += 1

# ---- Look up enzyme names for "specific" submissions ----
enzyme_names_map = {}
enzyme_ids_set = set()
for s in submissions:
    if s['enzyme_ids_used'] and s['enzyme_ids_used'] != 'ALL':
        for eid in s['enzyme_ids_used'].split(','):
            eid = eid.strip()
            if eid.isdigit():
                enzyme_ids_set.add(int(eid))

if enzyme_ids_set:
    placeholders = ','.join(['%s'] * len(enzyme_ids_set))
    cursor.execute(
        "SELECT enzyme_id, enzyme_name FROM enzyme_db "
        "WHERE enzyme_id IN (" + placeholders + ")",
        tuple(enzyme_ids_set)
    )
    for row in cursor.fetchall():
        enzyme_names_map[row['enzyme_id']] = row['enzyme_name']

cursor.close()
conn.close()

# ---- Build the history table rows ----
history_rows_html = ''
for s in submissions:
    sid = s['submission_id']
    name = s['submission_name'] if s['submission_name'] else 'Untitled'
    mode = s['analysis_mode']

    # Build the enzymes label
    if mode == 'full_scan':
        enzymes_label = 'All enzymes'
    else:
        enzyme_names = []
        if s['enzyme_ids_used']:
            for eid in s['enzyme_ids_used'].split(','):
                eid = eid.strip()
                if eid.isdigit():
                    enzyme_names.append(
                        enzyme_names_map.get(int(eid), 'Unknown')
                    )
        if enzyme_names:
            enzymes_label = ', '.join(enzyme_names)
        else:
            enzymes_label = '-'

    # Count cut sites
    if s['cut_positions']:
        cut_count = len([
            p for p in s['cut_positions'].split(',') if p.strip()
        ])
    else:
        cut_count = 0

    # Date string
    if s['submission_date']:
        date_str = s['submission_date'].strftime('%b %d, %Y %H:%M')
    else:
        date_str = ''

    # Mode badge styling
    if mode == 'specific':
        mode_class = 'badge-sticky-5'
        mode_label = 'Specific enzyme'
    else:
        mode_class = 'badge-blunt'
        mode_label = 'Full scan'

    history_rows_html += (
        '<tr data-mode="' + html.escape(mode) + '">'
        '<td>' + str(sid) + '</td>'
        '<td>' + html.escape(name) + '</td>'
        '<td>' + html.escape(enzymes_label) + '</td>'
        '<td><span class="badge ' + mode_class + '">'
        + mode_label + '</span></td>'
        '<td>' + str(cut_count) + '</td>'
        '<td>' + date_str + '</td>'
        '<td><a class="view-btn" href="view_submission.cgi?id='
        + str(sid) + '">View results</a></td>'
        '</tr>\n'
    )

# Empty state
if not history_rows_html:
    history_rows_html = (
        '<tr><td colspan="7" style="text-align:center; color:#888; '
        'padding:20px;">No submissions yet. Run an analysis to see it here.</td></tr>'
    )

# ---- Read the history template ----
template_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'templates', 'history.html'
)
template_file = open(template_path, 'r')
template = template_file.read()
template_file.close()

# ---- Replace placeholders and output ----
output = template
output = output.replace('{{total_submissions}}', str(total))
output = output.replace('{{specific_count}}', str(specific_count))
output = output.replace('{{full_scan_count}}', str(full_scan_count))
output = output.replace('{{history_rows}}', history_rows_html)

print(output)
