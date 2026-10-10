import sys
from pathlib import Path

# let tests import our modules (settings.py, database.py) from src/spendlens
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "spendlens"))