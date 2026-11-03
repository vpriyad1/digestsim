"""
DigestSim - Flask web app
A web-based tool for restriction enzyme analysis and DNA digest simulation.
"""

import os
import sqlite3
import json
from flask import Flask, render_template, request, g, redirect, url_for, abort

# ---------- App setup ----------
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.instance_path, 'digestsim.db')
app.config['SCHEMA'] = os.path.join(app.root_path, 'data', 'schema.sql')
app.config['SEED'] = os.path.join(app.root_path, 'data', 'populate_enzymes.sql')

# Make sure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)


# ---------- Database helpers ----------
def get_db():
    """Open a new DB connection per request, reuse across the request."""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close the DB connection when the request ends."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and seed enzyme data if the DB is new."""
    if os.path.exists(app.config['DATABASE']):
        return
    conn = sqlite3.connect(app.config['DATABASE'])
    with open(app.config['SCHEMA']) as f:
        conn.executescript(f.read())
    with open(app.config['SEED']) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized at", app.config['DATABASE'])


# ---------- Core analysis logic ----------
VALID_BASES = "ATGC"


def clean_sequence(raw_text):
    """Strip FASTA headers, whitespace, and non-ATGC characters."""
    cleaned = ""
    for line in raw_text.splitlines():
        if line.startswith(">"):
            continue
        for ch in line:
            upper_ch = ch.upper()
            if upper_ch in VALID_BASES:
                cleaned += upper_ch
    return cleaned


def find_cut_sites(dna, recognition, cut_offset):
    """Find all cut positions for one enzyme in a DNA sequence."""
    positions = []
    pattern_len = len(recognition)
    for i in range(len(dna) - pattern_len + 1):
        if dna[i:i + pattern_len] == recognition:
            positions.append(i + cut_offset)
    return positions


def calculate_fragments(sequence_length, cut_positions):
    """Compute fragment sizes from the full length and a list of cut positions."""
    if not cut_positions:
        return [sequence_length]
    sorted_cuts = sorted(cut_positions)
    fragments = [sorted_cuts[0]]
    for i in range(1, len(sorted_cuts)):
        fragments.append(sorted_cuts[i] - sorted_cuts[i - 1])
    fragments.append(sequence_length - sorted_cuts[-1])
    return fragments


def run_analysis(dna, enzymes):
    """Run digest analysis for a list of enzyme dicts."""
    all_cuts = []
    per_enzyme = []
    for enzyme in enzymes:
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
            all_cuts.extend(cuts)
    all_cuts.sort()
    fragments = calculate_fragments(len(dna), all_cuts)
    return {
        'per_enzyme': per_enzyme,
        'all_cuts': all_cuts,
        'fragments': fragments,
        'sequence_length': len(dna)
    }


# ---------- Routes ----------
@app.route('/')
def index():
    """Homepage with the input form."""
    db = get_db()
    enzymes = db.execute(
        "SELECT enzyme_id, enzyme_name, recognition_sequence "
        "FROM enzyme_db ORDER BY enzyme_name"
    ).fetchall()
    return render_template('index.html', enzymes=enzymes)


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process form submission, run analysis, save result."""
    submission_name = request.form.get('submission_name', '').strip() or 'Untitled submission'
    dna_input = request.form.get('dna_sequence', '')
    analysis_mode = request.form.get('analysis_mode', 'specific')
    enzyme1_id = request.form.get('enzyme1', '').strip()
    enzyme2_id = request.form.get('enzyme2', '').strip()

    dna = clean_sequence(dna_input)
    if not dna:
        return render_template('error.html', message="No valid DNA sequence found."), 400

    db = get_db()

    if analysis_mode == 'full_scan':
        enzymes = db.execute(
            "SELECT enzyme_id, enzyme_name, recognition_sequence, "
            "cut_position, overhang_type FROM enzyme_db"
        ).fetchall()
        enzyme_ids_used = 'ALL'
    else:
        enzyme_ids = [eid for eid in [enzyme1_id, enzyme2_id] if eid.isdigit()]
        if not enzyme_ids:
            return render_template('error.html', message="No enzymes selected."), 400
        placeholders = ','.join(['?'] * len(enzyme_ids))
        enzymes = db.execute(
            f"SELECT enzyme_id, enzyme_name, recognition_sequence, "
            f"cut_position, overhang_type FROM enzyme_db "
            f"WHERE enzyme_id IN ({placeholders})",
            enzyme_ids
        ).fetchall()
        enzyme_ids_used = ','.join(enzyme_ids)

    enzymes = [dict(e) for e in enzymes]
    result = run_analysis(dna, enzymes)

    # Save submission
    cursor = db.execute(
        "INSERT INTO submissions "
        "(submission_name, dna_sequence, enzyme_ids_used, analysis_mode, "
        "cut_positions, fragment_sizes) VALUES (?, ?, ?, ?, ?, ?)",
        (submission_name, dna, enzyme_ids_used, analysis_mode,
         ','.join(str(p) for p in result['all_cuts']),
         ','.join(str(f) for f in result['fragments']))
    )
    db.commit()
    submission_id = cursor.lastrowid

    return redirect(url_for('view_submission', submission_id=submission_id))


@app.route('/submission/<int:submission_id>')
def view_submission(submission_id):
    """Show results for a specific submission."""
    db = get_db()
    submission = db.execute(
        "SELECT * FROM submissions WHERE submission_id = ?",
        (submission_id,)
    ).fetchone()
    if not submission:
        abort(404)

    # Re-fetch the enzymes used
    if submission['analysis_mode'] == 'full_scan':
        enzymes = db.execute(
            "SELECT enzyme_id, enzyme_name, recognition_sequence, "
            "cut_position, overhang_type FROM enzyme_db"
        ).fetchall()
    else:
        ids = [e.strip() for e in (submission['enzyme_ids_used'] or '').split(',') if e.strip().isdigit()]
        if ids:
            placeholders = ','.join(['?'] * len(ids))
            enzymes = db.execute(
                f"SELECT enzyme_id, enzyme_name, recognition_sequence, "
                f"cut_position, overhang_type FROM enzyme_db "
                f"WHERE enzyme_id IN ({placeholders})",
                ids
            ).fetchall()
        else:
            enzymes = []

    enzymes = [dict(e) for e in enzymes]
    result = run_analysis(submission['dna_sequence'], enzymes)

    # Pre-compute per-enzyme fragments for the template
    for e in result['per_enzyme']:
        e['fragments'] = calculate_fragments(result['sequence_length'], e['cut_sites'])

    enzymes_json = json.dumps([
        {'enzyme_name': e['enzyme_name'], 'cut_sites': e['cut_sites']}
        for e in result['per_enzyme']
    ])

    return render_template(
        'results.html',
        submission=submission,
        result=result,
        enzymes_json=enzymes_json
    )


@app.route('/history')
def history():
    """List all past submissions."""
    db = get_db()
    submissions = db.execute(
        "SELECT * FROM submissions ORDER BY submission_date DESC"
    ).fetchall()

    # Resolve enzyme names for display
    all_ids = set()
    for s in submissions:
        if s['enzyme_ids_used'] and s['enzyme_ids_used'] != 'ALL':
            for e in s['enzyme_ids_used'].split(','):
                if e.strip().isdigit():
                    all_ids.add(int(e.strip()))

    name_map = {}
    if all_ids:
        placeholders = ','.join(['?'] * len(all_ids))
        rows = db.execute(
            f"SELECT enzyme_id, enzyme_name FROM enzyme_db "
            f"WHERE enzyme_id IN ({placeholders})",
            tuple(all_ids)
        ).fetchall()
        name_map = {r['enzyme_id']: r['enzyme_name'] for r in rows}

    # Enrich each submission with display fields
    enriched = []
    for s in submissions:
        s = dict(s)
        if s['analysis_mode'] == 'full_scan':
            s['enzymes_label'] = 'All enzymes'
        else:
            names = []
            if s['enzyme_ids_used']:
                for eid in s['enzyme_ids_used'].split(','):
                    if eid.strip().isdigit():
                        names.append(name_map.get(int(eid.strip()), 'Unknown'))
            s['enzymes_label'] = ', '.join(names) if names else '-'
        s['cut_count'] = len([
            p for p in (s['cut_positions'] or '').split(',') if p.strip()
        ])
        enriched.append(s)

    counts = {
        'total': len(enriched),
        'specific': sum(1 for s in enriched if s['analysis_mode'] == 'specific'),
        'full_scan': sum(1 for s in enriched if s['analysis_mode'] == 'full_scan'),
    }

    return render_template('history.html', submissions=enriched, counts=counts)

# ---------- Startup ----------

# Initialize DB immediately when the module is imported (needed for Gunicorn/Render)
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
