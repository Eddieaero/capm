# import pandas as pd

# # Read the Excel file
# df = pd.read_excel('US_companies_251030_AH.xlsx')

# # Save as CSV
# df.to_csv('US_companies_251030_AH.csv', index=False)

import pandas as pd
import os


# second version: convert each sheet to a separate CSV file

def convert_excel_to_multiple_csv(excel_file_path):
    """
    Converts each sheet in an Excel file to a separate CSV file.
    
    Args:
        excel_file_path (str): The path to your Excel file (e.g., 'data.xlsx').
    """
    # 1. Read all sheets into a dictionary of DataFrames
    # sheet_name=None reads all sheets
    try:
        all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
    except FileNotFoundError:
        print(f"Error: The file '{excel_file_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return

    # Extract the base name for the output files
    base_name = os.path.splitext(os.path.basename(excel_file_path))[0]
    
    print(f"Found {len(all_sheets)} sheets in '{excel_file_path}'.")
    
    # 2. Loop through the dictionary and save each sheet as a CSV
    for sheet_name, df in all_sheets.items():
        # Create a clean, descriptive filename
        # Replaces any special characters in the sheet name with an underscore
        safe_sheet_name = "".join(c if c.isalnum() else "_" for c in sheet_name)
        csv_filename = f"{base_name}_{safe_sheet_name}.csv"
        
        # Save the DataFrame to a CSV file (index=False prevents writing the DataFrame index)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"-> Successfully saved sheet '{sheet_name}' to {csv_filename}")

# --- Set your Excel file name here ---
excel_filename = 'Swedish_companies_251030_AH.xlsx'
convert_excel_to_multiple_csv(excel_filename)

# third version: combine all sheets into a single CSV file

# import pandas as pd
# import os

# def combine_excel_sheets_to_single_csv(excel_file_path, output_csv_path):
#     """
#     Reads all sheets from an Excel file, combines them, and saves to a single CSV.
    
#     Args:
#         excel_file_path (str): Path to your Excel file.
#         output_csv_path (str): Desired path for the combined CSV file.
#     """
#     try:
#         # Read all sheets into a dictionary of DataFrames
#         all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
#     except FileNotFoundError:
#         print(f"Error: The file '{excel_file_path}' was not found.")
#         return
    
#     # Concatenate all DataFrames in the dictionary into a single DataFrame
#     # ignore_index=True resets the index for the combined data
#     combined_df = pd.concat(all_sheets.values(), ignore_index=True)
    
#     # Save the combined DataFrame to the output CSV file
#     combined_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    
#     print(f"Successfully combined {len(all_sheets)} sheets into one file: {output_csv_path}")

# # --- Set your file names here ---
# excel_filename = 'US_companies_251030_AH.xlsx'
# output_filename = 'US_companies_251030_AH.csv'

# combine_excel_sheets_to_single_csv(excel_filename, output_filename)