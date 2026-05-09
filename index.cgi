#!/usr/bin/env python3
# index.cgi - renders the input page with the enzyme dropdown populated

import sys
import os

# Add lib directory to path so we can import db_connect
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))

from db_connect import get_connection

# Required: print HTTP header before any other output
print("Content-Type: text/html")
print()

# Read the template file
template_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates', 'index.html'
)
template_file = open(template_path, 'r')
template = template_file.read()
template_file.close()

# Get all enzymes from the database for the dropdown
conn = get_connection()
cursor = conn.cursor()
cursor.execute(
    "SELECT enzyme_id, enzyme_name, recognition_sequence "
    "FROM enzyme_db ORDER BY enzyme_name"
)
enzymes = cursor.fetchall()
cursor.close()
conn.close()

# Build the option tags for the enzyme dropdowns
options_html = ""
for enz_id, enz_name, recognition in enzymes:
    options_html = options_html + (
        '<option value="' + str(enz_id) + '">'
        + enz_name + ' (' + recognition + ')'
        + '</option>\n'
    )

# Replace the placeholder in the template and output
output = template.replace('{{enzyme_options}}', options_html)
print(output)
