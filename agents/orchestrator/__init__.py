from .orchestrator import PortfolioOrchestrator

def get_orchestrator():
    """
    Factory function to provide the PortfolioOrchestrator instance.
    This satisfies the import in agents/integration.py
    """
    return PortfolioOrchestrator()

__all__ = ["get_orchestrator", "PortfolioOrchestrator"]