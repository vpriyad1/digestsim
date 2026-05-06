-- DigestSim Database Schema
-- Two tables: enzyme_db (reference) and submissions (user history)

-- =============================================
-- Table 1: enzyme_db
-- Stores restriction enzyme reference data sourced from REBASE
-- =============================================
CREATE TABLE IF NOT EXISTS enzyme_db (
    enzyme_id INT AUTO_INCREMENT PRIMARY KEY,
    enzyme_name VARCHAR(50) NOT NULL,
    recognition_sequence VARCHAR(50) NOT NULL,
    cut_position INT NOT NULL,
    overhang_type ENUM('5_prime_sticky', '3_prime_sticky', 'blunt') NOT NULL,
    enzyme_type ENUM('Type I', 'Type II', 'Type III') NOT NULL,
    commercial_supplier VARCHAR(100) DEFAULT NULL
);

-- =============================================
-- Table 2: submissions
-- Stores user-submitted analyses and their results
-- =============================================
CREATE TABLE IF NOT EXISTS submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    submission_name VARCHAR(255) DEFAULT NULL,
    dna_sequence TEXT NOT NULL,
    enzyme_ids_used VARCHAR(255) DEFAULT NULL,
    analysis_mode ENUM('specific', 'full_scan') NOT NULL,
    cut_positions TEXT DEFAULT NULL,
    fragment_sizes TEXT DEFAULT NULL,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
