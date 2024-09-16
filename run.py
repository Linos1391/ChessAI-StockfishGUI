import os
import pathlib

PROJECT_PATH: str = pathlib.Path(__file__).parent

prompt: str = """
python ChessAI/main.py
"""

# You may add 'conda activate ..' if needed

def main():
    os.chdir(PROJECT_PATH)
    os.system(prompt)

if __name__ == '__main__':
    main()
