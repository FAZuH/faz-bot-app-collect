from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

try:
    __version__ = version("faz-bot-app-collect")
except PackageNotFoundError:
    __version__ = "development"
