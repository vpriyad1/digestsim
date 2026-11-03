-- DigestSim SQLite schema
-- Converted from MySQL for portable deployment

-- Reference table of restriction enzymes (populated from REBASE)
CREATE TABLE IF NOT EXISTS enzyme_db (
    enzyme_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enzyme_name TEXT NOT NULL,
    recognition_sequence TEXT NOT NULL,
    cut_position INTEGER NOT NULL,
    overhang_type TEXT NOT NULL CHECK (overhang_type IN ('5_prime_sticky', '3_prime_sticky', 'blunt')),
    enzyme_type TEXT NOT NULL CHECK (enzyme_type IN ('Type I', 'Type II', 'Type III')),
    commercial_supplier TEXT
);

-- Records of every user analysis
CREATE TABLE IF NOT EXISTS submissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_name TEXT,
    dna_sequence TEXT NOT NULL,
    enzyme_ids_used TEXT,
    analysis_mode TEXT NOT NULL CHECK (analysis_mode IN ('specific', 'full_scan')),
    cut_positions TEXT,
    fragment_sizes TEXT,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_enzyme_name ON enzyme_db(enzyme_name);
CREATE INDEX IF NOT EXISTS idx_submission_date ON submissions(submission_date DESC);
