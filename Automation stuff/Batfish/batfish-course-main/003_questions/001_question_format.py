import sys
from pathlib import Path

# Update sys.path so we can install the utils package
sys.path.append(f"{Path(__file__).parent.parent}")

from rich import inspect

from utils.bf_setup import create_bf_session

bf = create_bf_session("001_base")

# Seeing available questions
inspect(bf.q, methods=True)

# Question format
# - Send question to Batfish and get answer
# bf.q.<question_name>().answer()

# - Send question to Batfish and get answer as a dataframe
# bf.q.<question_name>().answer().frame()
