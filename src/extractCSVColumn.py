import csv

# Define input and output file paths
input_file = './input/dayAhead2023.csv'
output_file = './input/prices.csv'

# Open the input and output files
with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    # Create CSV reader with semicolon as delimiter
    reader = csv.reader(infile, delimiter=';')
    
    # Iterate over each row in the input file
    for row in reader:
        if len(row) >= 2:
            outfile.write(row[2].replace(",", ".")+'\n')
        else:
            # Handle rows that don't have at least 5 columns
            outfile.write('\n')
