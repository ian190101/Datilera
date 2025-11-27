# app/kernel/application/cursosextra/balance/consultar_balance.py

"""
Caso de Uso: Consultar Balance
"""
from app.kernel.domain.cursos_extra import (
    BalanceCursoExtra,
    BalanceCursoExtraRepositoryPort,
    BalanceNoEncontrado,
)


class ConsultarBalance:
    """
    Caso de Uso: Consultar el balance de una inscripción.
    """
    
    def __init__(self, balance_repo: BalanceCursoExtraRepositoryPort):
        self.balance_repo = balance_repo
    
    async def por_id(self, balance_id: int) -> BalanceCursoExtra:
        """Consulta balance por ID."""
        balance = await self.balance_repo.obtener_por_id(balance_id)
        if not balance:
            raise BalanceNoEncontrado(balance_id)
        return balance
    
    async def por_inscripcion(self, inscripcion_id: int) -> BalanceCursoExtra:
        """Consulta balance por inscripción."""
        balance = await self.balance_repo.obtener_por_inscripcion(inscripcion_id)
        if not balance:
            raise BalanceNoEncontrado(f"inscripcion {inscripcion_id}")
        return balance
