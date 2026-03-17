import os
import pandas as pd


def parse_markdown(file_path: str) -> str:
    """
    Parse a Markdown (.md) file and return cleaned text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            return content.strip()
    except Exception as e:
        raise Exception(f"Error reading markdown file {file_path}: {str(e)}")


def parse_csv(file_path: str) -> str:
    """
    Parse a CSV file and convert it into structured text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    try:
        df = pd.read_csv(file_path)

        # Replace NaN values with empty string
        df.fillna("", inplace=True)

        # Convert dataframe to structured readable text
        text_output = []
        for _, row in df.iterrows():
            row_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
            text_output.append(row_text)

        return "\n".join(text_output)

    except Exception as e:
        raise Exception(f"Error reading CSV file {file_path}: {str(e)}")
