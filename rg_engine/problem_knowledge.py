"""Stan wiedzy bohatera o Zagrożeniach.

Implementacja znajduje się w :mod:`rg_engine.threats`; ten moduł zachowuje
stabilne importy używane przez istniejący kod i testy.
"""

from rg_engine.threats import (
    PROBLEM_INVESTIGATION_ACTION_COST,
    can_investigate_problem,
    clear_problem_knowledge,
    investigate_problem,
    problem_investigated,
    problem_knowledge_view,
    problem_methods_for_player,
)

__all__ = [
    "PROBLEM_INVESTIGATION_ACTION_COST",
    "can_investigate_problem",
    "clear_problem_knowledge",
    "investigate_problem",
    "problem_investigated",
    "problem_knowledge_view",
    "problem_methods_for_player",
]
