import pandas as pd
import os

def save_to_excel(data_list, output_path):
    """
    Saves a list of dictionaries to an Excel file.
    """
    if not data_list:
        print("No data to save.")
        return

    try:
        df = pd.DataFrame(data_list)
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Successfully saved {len(data_list)} records to {output_path}")
        
    except Exception as e:
        print(f"Error saving to Excel: {e}")
