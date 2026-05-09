#!/usr/bin/env python3
# view_submission.cgi
# Looks up a saved submission by ID and renders its results page.

import sys
import os
import cgi
import html
import json

# Add lib directory to path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib')
)

from db_connect import get_connection
from digest_logic import find_cut_sites, calculate_fragments

# Print HTTP header
print("Content-Type: text/html")
print()
sys.stdout.flush()

# ---- Get submission ID from URL parameter ----
form = cgi.FieldStorage()
submission_id = form.getvalue('id', '')

if not submission_id or not submission_id.isdigit():
    print("<html><body><h1>Invalid submission ID.</h1>"
          "<a href='get_history.cgi'>Back to history</a></body></html>")
    sys.exit()

# ---- Fetch the submission ----
conn = get_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute(
    "SELECT * FROM submissions WHERE submission_id = %s",
    (int(submission_id),)
)
submission = cursor.fetchone()

if not submission:
    print("<html><body><h1>Submission not found.</h1>"
          "<a href='get_history.cgi'>Back to history</a></body></html>")
    sys.exit()

# ---- Get enzymes used in this submission ----
if submission['analysis_mode'] == 'full_scan':
    cursor.execute(
        "SELECT enzyme_id, enzyme_name, recognition_sequence, "
        "cut_position, overhang_type FROM enzyme_db"
    )
    enzymes_to_use = cursor.fetchall()
else:
    enzyme_ids = []
    if submission['enzyme_ids_used']:
        for e in submission['enzyme_ids_used'].split(','):
            e = e.strip()
            if e.isdigit():
                enzyme_ids.append(int(e))

    if enzyme_ids:
        placeholders = ','.join(['%s'] * len(enzyme_ids))
        cursor.execute(
            "SELECT enzyme_id, enzyme_name, recognition_sequence, "
            "cut_position, overhang_type FROM enzyme_db "
            "WHERE enzyme_id IN (" + placeholders + ")",
            tuple(enzyme_ids)
        )
        enzymes_to_use = cursor.fetchall()
    else:
        enzymes_to_use = []

cursor.close()
conn.close()

# ---- Re-run analysis to get per-enzyme breakdown ----
dna = submission['dna_sequence']
sequence_length = len(dna)

per_enzyme = []
all_cuts = []
for enzyme in enzymes_to_use:
    cuts = find_cut_sites(
        dna, enzyme['recognition_sequence'], enzyme['cut_position']
    )
    if cuts:
        per_enzyme.append({
            'enzyme_name': enzyme['enzyme_name'],
            'recognition_sequence': enzyme['recognition_sequence'],
            'cut_position': enzyme['cut_position'],
            'overhang_type': enzyme['overhang_type'],
            'cut_sites': cuts
        })
        all_cuts = all_cuts + cuts

all_cuts.sort()
fragments = calculate_fragments(sequence_length, all_cuts)

# ---- Build results table rows ----
overhang_classes = {
    '5_prime_sticky': 'badge-sticky-5',
    '3_prime_sticky': 'badge-sticky-3',
    'blunt': 'badge-blunt'
}
overhang_labels = {
    '5_prime_sticky': "5' sticky",
    '3_prime_sticky': "3' sticky",
    'blunt': "blunt"
}

results_rows_html = ''
for e in per_enzyme:
    cls = overhang_classes.get(e['overhang_type'], '')
    label = overhang_labels.get(e['overhang_type'], e['overhang_type'])

    cuts_str = ', '.join(str(c) for c in e['cut_sites'])
    enz_fragments = calculate_fragments(sequence_length, e['cut_sites'])
    frag_str = ', '.join(str(f) for f in enz_fragments)

    seq = e['recognition_sequence']
    pos = e['cut_position']
    display_seq = seq[:pos] + '^' + seq[pos:]

    results_rows_html += (
        '<tr>'
        '<td>' + html.escape(e['enzyme_name']) + '</td>'
        '<td>' + html.escape(display_seq) + '</td>'
        '<td>' + html.escape(cuts_str) + '</td>'
        '<td><span class="badge ' + cls + '">' + label + '</span></td>'
        '<td>' + html.escape(frag_str) + '</td>'
        '</tr>\n'
    )

if not per_enzyme:
    results_rows_html = (
        '<tr><td colspan="5" style="text-align:center; color:#888; '
        'padding:20px;">No cut sites found.</td></tr>'
    )

# ---- Build JSON for visual cut map ----
enzymes_json = json.dumps([
    {'enzyme_name': e['enzyme_name'], 'cut_sites': e['cut_sites']}
    for e in per_enzyme
])
cuts_json = json.dumps(all_cuts)

# ---- Read template ----
template_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'templates', 'results.html'
)
template_file = open(template_path, 'r')
template = template_file.read()
template_file.close()

# ---- Replace placeholders and output ----
sub_name = submission['submission_name'] if submission['submission_name'] else 'Untitled'

output = template
output = output.replace('{{submission_name}}', html.escape(sub_name))
output = output.replace('{{enzymes_matched}}', str(len(per_enzyme)))
output = output.replace('{{total_cut_sites}}', str(len(all_cuts)))
output = output.replace('{{fragments_produced}}', str(len(fragments)))
output = output.replace('{{sequence_length}}', str(sequence_length))
output = output.replace('{{results_rows}}', results_rows_html)
output = output.replace('{{cuts_json}}', html.escape(cuts_json))
output = output.replace('{{enzymes_json}}', html.escape(enzymes_json))

print(output)
