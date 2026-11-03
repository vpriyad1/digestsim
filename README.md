# 🧬 DigestSim

> A web-based tool for restriction enzyme analysis and DNA digest simulation.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-5.7+-4479A1?logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![jQuery](https://img.shields.io/badge/jQuery-3.7-0769AD?logo=jquery&logoColor=white)
![Apache](https://img.shields.io/badge/Apache-CGI-D22128?logo=apache&logoColor=white)

![DigestSim homepage](docs/screenshots/01_homepage.png)

DigestSim lets molecular biologists plan and validate restriction enzyme digestion experiments entirely in silico. Paste any DNA sequence, choose specific enzymes (or scan all 718 in the database), and instantly see cut positions, fragment sizes, overhang types, and a visual cut map — saving time and reducing wet-lab errors before a single tube is touched.

**[Features](#features) • [Tech stack](#tech-stack) • [Screenshots](#screenshots) • [Try it yourself](#try-it-yourself) • [Installation](#installation) • [References](#references)**

> **🚀 Live demo:** currently being redeployed on public hosting. For now, see the screenshots below or clone and run locally using the installation instructions.

---

## Features

- 🔍 **Two analysis modes** — pick one or two specific enzymes for a single or double digest, or scan the entire database to find every enzyme whose recognition sequence appears in your DNA.
- 📊 **Detailed results** — cut positions, fragment sizes, overhang type (5′ sticky, 3′ sticky, blunt), and the recognition sequence with the cut site marked.
- 📈 **Visual cut map** — interactive linear DNA map with color-coded cut markers per enzyme.
- 🕓 **Submission history** — every analysis is saved and searchable; revisit and compare past results anytime.
- 🧹 **Smart input cleaning** — automatically strips FASTA headers, whitespace, numbers, and lowercase letters before analysis.
- 🗄️ **718 enzymes from REBASE** — Type II enzymes with non-degenerate recognition sequences, parsed from the official REBASE bionet file.

## Tech stack

**Backend:** Python 3 CGI programming, MySQL relational database, `mysql-connector-python`, Apache HTTP server with mod_cgi

**Frontend:** HTML5 semantic markup, CSS3 (no frameworks — handwritten), JavaScript + jQuery 3.7 for client-side interactivity

**Data:** [REBASE](http://rebase.neb.com) — The Restriction Enzyme Database (Roberts et al., 2015)

**Principles:**
- Strict content separation (no HTML in Python, no inline CSS/JS in HTML)
- Templating-based rendering (HTML templates with placeholders)
- Two-table normalized relational schema

## Screenshots

### Input page
![Input page](docs/screenshots/01_homepage.png)

### Results page with visual cut map
![Results page](docs/screenshots/02_results_page.png)

### Submission history
![History page](docs/screenshots/03_history_page.png)

## Try it yourself

Once installed, test the app with these sample inputs:

### 1. Simple EcoRI digest

- **Submission name:** `My first test`
- **DNA sequence:** `AAAGAATTCAAACCCGGGAAGCTTTTTGAATTCAA`
- **Mode:** Select specific enzymes
- **Enzyme 1:** `EcoRI`
- **Expected result:** 1 enzyme matched, 2 cut sites (at positions 4 and 28), 3 fragments of sizes 4, 24, 7

### 2. pUC19 polylinker (full scan)

- **Submission name:** `pUC19 MCS`
- **DNA sequence:** `GAATTCGAGCTCGGTACCCGGGGATCCTCTAGAGTCGACCTGCAGGCATGCAAGCTT`
- **Mode:** Scan all enzymes in database
- **Expected result:** Matches for EcoRI, SacI, KpnI, SmaI, BamHI, XbaI, SalI, PstI, SphI, HindIII, plus REBASE isoschizomers (20+ enzymes total)

### 3. FASTA input (cleaning demo)

- **DNA sequence (paste exactly, with header and lowercase):**
  ```
  >my_test_sequence
  atgctt aagctt ggat
  ccgaa ttcgta cgcta
  ```
- **Mode:** Select specific enzymes
- **Enzyme 1:** `EcoRI`
- **Enzyme 2:** `HindIII`
- **Expected result:** input cleaned to `ATGCTTAAGCTTGGATCCGAATTCGTACGCTA`, then analysis runs normally.

### 4. No cuts (empty result handling)

- **DNA sequence:** `AAAAAAAAAAAAAAAAAAAAAAAAAAAA`
- **Enzyme 1:** `EcoRI`
- **Expected result:** "No cut sites found for the selected enzymes."

## Installation

### Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB
- Apache (or any web server with CGI support)
- Python module: `mysql-connector-python`

### Steps

**1. Clone the repository into your web root**

```bash
cd /path/to/your/webroot
git clone https://github.com/vpriyad1/digestsim.git
cd digestsim
```

**2. Set up the MySQL database**

Create a MySQL database (or use an existing one with full privileges), then load the schema and data:

```bash
mysql -u your_user -p your_database < sql/create_tables.sql
mysql -u your_user -p your_database < sql/populate_enzymes.sql
```

This creates the `enzyme_db` and `submissions` tables and loads 718 Type II restriction enzymes.

**3. Create your database config** in `lib/db_config.py` (this file is gitignored for security):

```python
DB_HOST = 'localhost'
DB_USER = 'your_user'
DB_PASSWORD = 'your_password'
DB_NAME = 'your_database'
```

**4. Make CGI scripts executable**

```bash
chmod +x index.cgi cgi/*.cgi
```

**5. Access in your browser**

Navigate to your deployment URL (e.g., `http://yourserver/path/to/digestsim/index.cgi`). The homepage should load with the input form and enzyme dropdowns populated.

### Optional: Refresh enzyme data from REBASE

```bash
wget http://rebase.neb.com/rebase/link_bionet -O data/link_bionet.txt
python3 scripts/parse_rebase.py data/link_bionet.txt sql/populate_enzymes.sql
```

Then re-run step 2 to reload the data.

## Project structure

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
├── docs/
│   └── screenshots/             # README images
├── README.md
└── Final Project Proposal.pdf
```

## Database schema

Two tables:

| Table | Purpose |
|---|---|
| `enzyme_db` | Reference table of 718 Type II restriction enzymes from REBASE — name, recognition sequence, cut position, overhang type, enzyme type, commercial supplier. |
| `submissions` | Records of every analysis run through the app — submission name, DNA sequence, enzymes used, mode, cut positions, fragment sizes, timestamp. |

## References

- Roberts RJ, Vincze T, Posfai J, Macelis D. (2015). REBASE — a database for DNA restriction and modification: enzymes, genes and genomes. *Nucleic Acids Research*, 43:D298–D299. [doi:10.1093/nar/gku1046](https://doi.org/10.1093/nar/gku1046)
- Pingoud A, Wilson GG, Wende W. (2014). Type II restriction endonucleases — a historical perspective and more. *Nucleic Acids Research*, 42(12):7489–7527. [doi:10.1093/nar/gku447](https://doi.org/10.1093/nar/gku447)
- Yanisch-Perron C, Vieira J, Messing J. (1985). Improved M13 phage cloning vectors and host strains: nucleotide sequences of the M13mp18 and pUC19 vectors. *Gene*, 33(1):103–119.
- REBASE — The Restriction Enzyme Database. New England Biolabs. http://rebase.neb.com

## Acknowledgments

Built as the final project for **AS.410.712.81 — Advanced Practical Computer Concepts for Bioinformatics** at **Johns Hopkins University**, Spring 2026.

## Author

**Vedangi Priyadarshini**
M.S. Bioinformatics, Johns Hopkins University
[GitHub](https://github.com/vpriyad1)
