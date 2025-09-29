from app.strategies.momentum import Momentum
from .sma_cross import SMACross
from .breakout import Breakout
from .sma_cross_ml import SMACrossML

# Um registro central de todas as estratégias disponíveis
STRATEGY_REGISTRY = {
    "sma_cross": SMACross,
    "breakout": Breakout,
    "momentum": Momentum,
    "sma_cross_ml": SMACrossML,
}

def get_strategy(name: str):
    """
    Busca e retorna a classe da estratégia com base no nome.
    """
    strategy_class = STRATEGY_REGISTRY.get(name)
    if not strategy_class:
        raise ValueError(f"Estratégia '{name}' não encontrada. Estratégias disponíveis: {list(STRATEGY_REGISTRY.keys())}")
    return strategy_class