#!/usr/bin/env python3
# analyze_sequence.cgi
# Reads the input form, runs the digest analysis, saves the submission,
# and shows the results page.

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
from digest_logic import clean_sequence, analyze_with_enzymes, calculate_fragments

# Print HTTP header
print("Content-Type: text/html")
print()

# ---- Get form data ----
form = cgi.FieldStorage()
submission_name = form.getvalue('submission_name', '').strip()
dna_input = form.getvalue('dna_sequence', '')
analysis_mode = form.getvalue('analysis_mode', 'specific')
enzyme1_id = form.getvalue('enzyme1', '')
enzyme2_id = form.getvalue('enzyme2', '')

if not submission_name:
    submission_name = 'Untitled submission'

# ---- Clean DNA sequence ----
dna_sequence = clean_sequence(dna_input)

if len(dna_sequence) == 0:
    print("<html><body><h1>Error: no valid DNA sequence found.</h1>"
          "<a href='../index.cgi'>Go back</a></body></html>")
    sys.exit()

# ---- Get the enzymes to use ----
conn = get_connection()
cursor = conn.cursor(dictionary=True)

if analysis_mode == 'full_scan':
    cursor.execute(
        "SELECT enzyme_id, enzyme_name, recognition_sequence, "
        "cut_position, overhang_type FROM enzyme_db"
    )
    enzymes_to_use = cursor.fetchall()
    enzyme_ids_used = 'ALL'
else:
    enzyme_ids = []
    if enzyme1_id:
        enzyme_ids.append(enzyme1_id)
    if enzyme2_id:
        enzyme_ids.append(enzyme2_id)

    if len(enzyme_ids) == 0:
        print("<html><body><h1>Error: no enzymes selected.</h1>"
              "<a href='../index.cgi'>Go back</a></body></html>")
        sys.exit()

    placeholders = ','.join(['%s'] * len(enzyme_ids))
    query = (
        "SELECT enzyme_id, enzyme_name, recognition_sequence, "
        "cut_position, overhang_type FROM enzyme_db "
        "WHERE enzyme_id IN (" + placeholders + ")"
    )
    cursor.execute(query, tuple(enzyme_ids))
    enzymes_to_use = cursor.fetchall()
    enzyme_ids_used = ','.join(enzyme_ids)

# ---- Run the analysis ----
result = analyze_with_enzymes(dna_sequence, enzymes_to_use)

# ---- Save submission to database ----
cut_positions_str = ','.join(str(p) for p in result['all_cuts'])
fragment_sizes_str = ','.join(str(f) for f in result['fragments'])

cursor.execute(
    "INSERT INTO submissions "
    "(submission_name, dna_sequence, enzyme_ids_used, analysis_mode, "
    "cut_positions, fragment_sizes) "
    "VALUES (%s, %s, %s, %s, %s, %s)",
    (submission_name, dna_sequence, enzyme_ids_used, analysis_mode,
     cut_positions_str, fragment_sizes_str)
)
conn.commit()
cursor.close()
conn.close()

# ---- Build the per-enzyme results table rows ----
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
for e in result['per_enzyme']:
    cls = overhang_classes.get(e['overhang_type'], '')
    label = overhang_labels.get(e['overhang_type'], e['overhang_type'])

    cuts_str = ', '.join(str(c) for c in e['cut_sites'])
    enz_fragments = calculate_fragments(result['sequence_length'], e['cut_sites'])
    frag_str = ', '.join(str(f) for f in enz_fragments)

    # Build display sequence with caret showing cut position
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

# Empty results message if no cuts found
if not result['per_enzyme']:
    results_rows_html = (
        '<tr><td colspan="5" style="text-align:center; color:#888; '
        'padding:20px;">No cut sites found for the selected enzymes.</td></tr>'
    )

# ---- Build JSON for the visual cut map ----
enzymes_json = json.dumps([
    {'enzyme_name': e['enzyme_name'], 'cut_sites': e['cut_sites']}
    for e in result['per_enzyme']
])
cuts_json = json.dumps(result['all_cuts'])

# ---- Read the results template ----
template_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'templates', 'results.html'
)
template_file = open(template_path, 'r')
template = template_file.read()
template_file.close()

# ---- Replace placeholders and output ----
output = template
output = output.replace('{{submission_name}}', html.escape(submission_name))
output = output.replace('{{enzymes_matched}}', str(len(result['per_enzyme'])))
output = output.replace('{{total_cut_sites}}', str(len(result['all_cuts'])))
output = output.replace('{{fragments_produced}}', str(len(result['fragments'])))
output = output.replace('{{sequence_length}}', str(result['sequence_length']))
output = output.replace('{{results_rows}}', results_rows_html)
output = output.replace('{{cuts_json}}', html.escape(cuts_json))
output = output.replace('{{enzymes_json}}', html.escape(enzymes_json))

print(output)
