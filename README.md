# DigestSim

A web-based tool for restriction enzyme analysis and DNA digest simulation.

## ABOUT

DigestSim allows researchers to plan and validate restriction enzyme digestion experiments
in silico. Users paste any DNA sequence, choose specific enzymes (or scan the entire
database), and receive a detailed report including cut positions, fragment sizes,
overhang types, and a visual cut map. Every submission is stored so users can revisit
and compare past analyses through a history page.

The enzyme database is built from REBASE (Roberts et al., 2015) and contains 718
Type II restriction enzymes with non-degenerate recognition sequences.

Live deployment: http://bfx3.aap.jhu.edu/vpriyad1/digestsim/index.cgi
Source code: https://github.com/vpriyad1/final-project

## REQUIREMENTS

Server side:
- Python 3.8+
- Apache with mod_cgi (or any web server with CGI support)
- MySQL 5.7+
- python3-mysql.connector (mysql-connector-python)

Client side:
- Any modern browser with JavaScript enabled
- jQuery 3.7 (loaded from CDN)

Storage:
- Minimal. Database is < 1 MB after population.

### Installation

1. **Clone the repository**
```bash
   cd /path/to/your/webroot
   git clone https://github.com/vpriyad1/final-project.git digestsim
   cd digestsim
```

2. **Set up the MySQL database**

Create a MySQL database (or use an existing one with full privileges), then run the schema and populate scripts:

```bash
   mysql -u your_user -p < sql/create_tables.sql
   mysql -u your_user -p < sql/populate_enzymes.sql

   This creates the `enzyme_db` and `submissions` tables and loads 718 enzymes.
```

3. **Create your database config** in `lib/db_config.py` (this file is gitignored for security):
```python
   DB_HOST = 'localhost'
   DB_USER = 'your_user'
   DB_PASSWORD = 'your_password'
   DB_NAME = 'your_database'
```

4. **Make CGI scripts executable**
```bash
   chmod +x index.cgi cgi/*.cgi
```

5. **Deploy to your web root** and access via your browser URL (e.g., `http://yourserver/path/to/digestsim/index.cgi`)

### Optional: Refresh enzyme data from REBASE

The repository already includes parsed enzyme data, but if you want to fetch the latest from REBASE:

```bash
wget http://rebase.neb.com/rebase/link_bionet -O data/link_bionet.txt
python3 scripts/parse_rebase.py data/link_bionet.txt sql/populate_enzymes.sql
```

Then re-run step 2 above to reload the data.

## DETAILED USAGE

### Running an analysis

1. Visit the homepage. The form has fields for an optional submission name,
   a DNA sequence text area, an analysis mode toggle, and two enzyme dropdowns.

2. Paste a DNA sequence into the text area. The input is automatically cleaned —
   FASTA headers (lines starting with ">"), whitespace, line breaks, lowercase
   letters, and non-ATGC characters are stripped before analysis.

3. Choose an analysis mode:
   - "Select specific enzymes" lets you pick one or two enzymes for a single
      or double digest.
   - "Scan all enzymes in database" runs the sequence against all 718 enzymes
      and reports any whose recognition sequence appears in the input.

4. Click "Analyze sequence". The results page shows:
   - Summary metrics (enzymes matched, total cut sites, fragments produced,
     sequence length).
   - A table of each matching enzyme with its recognition sequence (with the
     cut site indicated by a caret), cut positions, overhang type, and the
     fragment sizes it would produce.
   - A visual cut map of the linear sequence with color-coded marks at each
     cut position.

### Browsing past submissions

Click "Submission history" in the navigation. The page lists every submission
sorted by date (newest first) with summary metrics at the top. Use the search
box to filter by submission name or enzyme, and the dropdown to filter by
analysis mode. Click "View results" on any row to revisit the full results
page for that submission.

## PROJECT STRUCTURE

```
digestsim/
├── index.cgi                    # Homepage CGI (renders input form)
├── cgi/
│   ├── analyze_sequence.cgi     # Processes form, runs analysis, saves submission
│   ├── get_history.cgi          # Renders submission history page
│   └── view_submission.cgi      # Renders a specific past submission
├── templates/                   # HTML templates (no embedded code)
│   ├── index.html
│   ├── results.html
│   └── history.html
├── css/
│   └── style.css                # All page styling (external)
├── js/                          # Client-side interactivity (external)
│   ├── main.js
│   ├── results.js
│   └── history.js
├── lib/
│   ├── db_config.py             # Database credentials (gitignored)
│   ├── db_connect.py            # MySQL connection helper
│   └── digest_logic.py          # Core analysis: cleaning, cut detection, fragments
├── sql/
│   ├── create_tables.sql        # Database schema
│   └── populate_enzymes.sql     # 718 enzyme INSERT statements (auto-generated)
├── scripts/
│   └── parse_rebase.py          # Parses REBASE bionet file into SQL
├── data/
│   └── link_bionet.txt          # Raw REBASE source data
├── README.md                    # This file
└── Final Project Proposal.pdf
```

## REFERENCES

Roberts RJ, Vincze T, Posfai J, Macelis D. (2015). REBASE — a database for DNA
    restriction and modification: enzymes, genes and genomes.
    Nucleic Acids Research, 43:D298-D299. DOI: 10.1093/nar/gku1046

REBASE — The Restriction Enzyme Database. New England Biolabs.
    http://rebase.neb.com (accessed May 2026).

## Author

**Vedangi Priyadarshini**
[GitHub](https://github.com/vpriyad1)
