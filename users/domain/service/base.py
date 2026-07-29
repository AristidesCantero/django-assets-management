from abc import ABC


class BaseService(ABC):
    """
    Marker base class for all domain services.

    Inherit from this class so that the AST-based project graph
    (core/service_node.py) can automatically discover and document
    every service regardless of file name or directory convention.
    """
    pass