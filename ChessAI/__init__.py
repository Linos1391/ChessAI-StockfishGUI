"""The __init__ of package."""

from .gui import ChessAIApp
from .engine import Engine
from . import vision

__all__ = [
    "ChessAIApp",
    "Engine",
    "vision",
]

__version__ = "1.0.0rc1"
