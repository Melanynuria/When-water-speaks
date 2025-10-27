# In: src/data_processing.py



import pandas as pd

def load_parquet_to_df(file_path):
    """
    Reads a Parquet file from a specified path into a pandas DataFrame.

    Args:
        file_path (str): The path to the .parquet file.

    Returns:
        pandas.DataFrame: The loaded DataFrame, or None if the file is not found.
    """
    try:
        df = pd.read_parquet(file_path)
        df = simplify_columns(df)
        return df
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
        return None
    
def simplify_columns(df):
    original_columns = df.columns.tolist()
    new_columns = [col.split('/')[0].lower() for col in original_columns]
    print(new_columns)

    df.columns = new_columns

    return df
    