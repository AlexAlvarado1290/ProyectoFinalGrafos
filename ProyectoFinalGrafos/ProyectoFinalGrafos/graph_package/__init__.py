from .graph import ManualGraph
from .algorithms import GraphTraversal
from .file_io import GraphFileIO
from .graph_model import GraphModel, GraphCompatibilityWrapper
from .config import DEFAULT_CSV, SAMPLE_EDGES

try:
    from .gui import GraphApp
    GUI_AVAILABLE = True
except ImportError as e:
    GraphApp = None
    GUI_AVAILABLE = False
    print("Instale las dependencias: pip install matplotlib networkx")
__all__ = [
    'ManualGraph',
    'GraphTraversal', 
    'GraphFileIO',
    'GraphModel',
    'GraphCompatibilityWrapper',
    'GraphApp',
    'DEFAULT_CSV',
    'SAMPLE_EDGES',
    'GUI_AVAILABLE'
]