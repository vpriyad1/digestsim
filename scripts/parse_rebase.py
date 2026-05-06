#!/usr/bin/env python3
# parse_rebase.py
# Reads the REBASE bionet file and creates SQL INSERT statements
# for the enzyme_db table.
#
# Usage: python3 scripts/parse_rebase.py data/link_bionet.txt sql/populate_enzymes.sql

import sys

# Bases we accept (skip degenerate codes like N, R, Y, etc.)
VALID_BASES = "ATGC"


def get_overhang(cut_pos, seq_length):
    # If the cut is exactly at the middle = blunt
    # If before the middle = 5' sticky
    # If after the middle = 3' sticky
    middle = seq_length / 2
    if cut_pos == middle:
        return "blunt"
    elif cut_pos < middle:
        return "5_prime_sticky"
    else:
        return "3_prime_sticky"


def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    enzymes = []
    seen_names = []

    infile = open(input_file, "r")
    for line in infile:
        line = line.strip()

        # Skip empty lines and headers
        if line == "":
            continue
        if "REBASE" in line or "Rich Roberts" in line:
            continue

        # Split into name part + recognition sequence
        # Lines look like: "EcoRI                             G^AATTC"
        parts = line.split()
        if len(parts) < 2:
            continue

        # Recognition sequence is always the last part
        seq_with_cut = parts[-1]

        # Enzyme name is the first part (drop any "(prototype)" reference)
        name = parts[0]

        # Skip if no cut site marked
        if "^" not in seq_with_cut:
            continue

        # Find where the cut goes
        cut_pos = seq_with_cut.index("^")
        recognition = seq_with_cut.replace("^", "")

        # Skip if cut is at start or end (Type IIS enzymes)
        if cut_pos == 0 or cut_pos == len(recognition):
            continue

        # Skip if any degenerate bases
        is_valid = True
        for base in recognition:
            if base not in VALID_BASES:
                is_valid = False
                break
        if not is_valid:
            continue

        # Skip duplicates
        if name in seen_names:
            continue
        seen_names.append(name)

        # Skip if too short or too long
        if len(recognition) < 4 or len(recognition) > 12:
            continue

        # Figure out overhang type from cut position
        overhang = get_overhang(cut_pos, len(recognition))

        enzymes.append([name, recognition, cut_pos, overhang])

    infile.close()

    # Write the SQL file
    outfile = open(output_file, "w")
    outfile.write("-- Generated from REBASE link_bionet\n")
    outfile.write("-- Total enzymes: " + str(len(enzymes)) + "\n\n")
    outfile.write("INSERT INTO enzyme_db (enzyme_name, recognition_sequence, ")
    outfile.write("cut_position, overhang_type, enzyme_type, commercial_supplier) VALUES\n")

    rows = []
    for enz in enzymes:
        name = enz[0]
        seq = enz[1]
        pos = enz[2]
        overhang = enz[3]
        row = "    ('" + name + "', '" + seq + "', " + str(pos) + ", '" + overhang + "', 'Type II', NULL)"
        rows.append(row)

    outfile.write(",\n".join(rows) + ";\n")
    outfile.close()

    print("Parsed " + str(len(enzymes)) + " enzymes")
    print("SQL written to " + output_file)


main()
