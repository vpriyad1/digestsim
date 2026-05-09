# digest_logic.py
# Core analysis functions for DigestSim:
#   - clean DNA input from the user
#   - find restriction enzyme cut sites
#   - compute fragment sizes from cut positions
#   - run an analysis for one or many enzymes

VALID_BASES = "ATGC"


def clean_sequence(raw_text):
    # Remove whitespace, numbers, FASTA headers, etc.
    # Returns an uppercase DNA string with only A, T, G, C.
    cleaned = ""
    for line in raw_text.splitlines():
        if line.startswith(">"):
            continue  # skip FASTA header lines
        for ch in line:
            upper_ch = ch.upper()
            if upper_ch in VALID_BASES:
                cleaned = cleaned + upper_ch
    return cleaned


def find_cut_sites(dna, recognition, cut_offset):
    # Find all cut positions for one enzyme in a DNA sequence.
    # Example: EcoRI recognition is "GAATTC" and cut_offset is 1.
    # Every time GAATTC appears at position i, the cut happens at (i + 1).
    positions = []
    pattern_len = len(recognition)

    for i in range(len(dna) - pattern_len + 1):
        if dna[i:i + pattern_len] == recognition:
            cut = i + cut_offset
            positions.append(cut)

    return positions


def calculate_fragments(sequence_length, cut_positions):
    # Given the full sequence length and a list of cut positions,
    # return the lengths of the fragments produced.
    if len(cut_positions) == 0:
        return [sequence_length]

    sorted_cuts = sorted(cut_positions)
    fragments = []

    # First fragment: from start of sequence to first cut
    fragments.append(sorted_cuts[0])

    # Middle fragments: between consecutive cuts
    for i in range(1, len(sorted_cuts)):
        fragments.append(sorted_cuts[i] - sorted_cuts[i - 1])

    # Last fragment: from last cut to end of sequence
    fragments.append(sequence_length - sorted_cuts[-1])

    return fragments


def analyze_with_enzymes(dna, enzymes):
    # Run the full analysis with a list of enzyme dicts.
    # Each enzyme dict needs: enzyme_name, recognition_sequence, cut_position.
    # Returns a dict with per-enzyme details, combined cut sites, and fragments.
    all_cuts = []
    per_enzyme = []

    for enzyme in enzymes:
        cut_sites = find_cut_sites(
            dna,
            enzyme['recognition_sequence'],
            enzyme['cut_position']
        )
        if len(cut_sites) > 0:
            per_enzyme.append({
                'enzyme_name': enzyme['enzyme_name'],
                'recognition_sequence': enzyme['recognition_sequence'],
                'cut_position': enzyme['cut_position'],
                'overhang_type': enzyme.get('overhang_type', ''),
                'cut_sites': cut_sites
            })
            all_cuts = all_cuts + cut_sites

    fragments = calculate_fragments(len(dna), all_cuts)

    return {
        'per_enzyme': per_enzyme,
        'all_cuts': sorted(all_cuts),
        'fragments': fragments,
        'sequence_length': len(dna)
    }
