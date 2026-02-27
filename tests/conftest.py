import sys
from pathlib import Path

# добавляем src в PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))