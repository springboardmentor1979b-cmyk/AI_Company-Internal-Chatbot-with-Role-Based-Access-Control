import json
import sys

def extract_code(ipynb_path, output_path):
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, cell in enumerate(nb['cells']):
            if cell['cell_type'] == 'code':
                f.write(f"# Cell {i}\n")
                code_lines = cell['source']
                for line in code_lines:
                    if not line.startswith('!'):
                        f.write(line)
                f.write("\n\n")

if __name__ == "__main__":
    extract_code("spoonfeed.ipynb", "spoonfeed.py")
