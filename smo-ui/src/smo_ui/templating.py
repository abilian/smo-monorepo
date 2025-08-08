from pathlib import Path

from fastapi.templating import Jinja2Templates

THIS_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=THIS_DIR / "templates")
