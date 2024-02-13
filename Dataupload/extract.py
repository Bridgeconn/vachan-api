''' Python script that related to extraction of data from sql dump'''
import os
import re
import csv

def extract_table_name(line):
    match = re.search(r'COPY public\.(\w+)', line)
    if match:
        return match.group(1)
    return None

def process_sql_dump(input_file):
    output_folder = "Data New"
    os.makedirs(output_folder, exist_ok=True)
    
    current_table = None
    current_csv_file = None

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("COPY public."):
                current_table = extract_table_name(line)
                if current_table:
                    csv_file_path = os.path.join(output_folder, f"{current_table}.csv")
                    current_csv_file = open(csv_file_path, 'w', newline='', encoding='utf-8')
                    csv_writer = csv.writer(current_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    
                    # Write "COPY public." line as the first line
                    csv_writer.writerow([line.strip()])

            elif line == "\\.\n" and current_csv_file:
                current_csv_file.close()
                current_table = None
                current_csv_file = None
            elif current_csv_file:
                values = line.strip().split('\t')
                csv_writer.writerow(values)

if __name__ == "__main__":
    sql_dump_file = "vachan_prod_backup_31_01_2022.sql"
    process_sql_dump(sql_dump_file)
