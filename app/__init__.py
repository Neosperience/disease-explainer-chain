from pathlib import Path
from .main import main

card_path = Path(__file__).parent.parent / "card.md"

app_name = "Disease Explainer Chain"
app_description = card_path.read_text()
app_executable = main

__all__ = ["app_name", "app_description", "app_executable"]
