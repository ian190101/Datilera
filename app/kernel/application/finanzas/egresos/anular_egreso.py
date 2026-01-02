# app/application/use_cases/finanzas/anular_egreso.py
"""
Caso de uso: Anular un egreso existente.
Arquitectura hexagonal - Solo usa puertos, no implementaciones concretas.
"""
from datetime import datetime

from app.kernel.domain.finanzas.egreso_entidad import EgresoAnular
from app.kernel.domain.finanzas.ports import (
    IEgresoRepository,
    ILibroCajaRepository,
)
from app.kernel.domain.finanzas.errors import (
    EgresoNoEncontradoError,
    EgresoYaAnuladoError,
    EgresoError,
)


class AnularEgresoUC:
    """
    Caso de uso: Anular un egreso existente.
    
    Flujo:
    1. Obtener egreso usando puerto
    2. Validar que existe y no está anulado
    3. Anular el egreso usando puerto
    4. Registrar anulación en libro de caja (como ingreso de reversión)
    5. Retornar confirmación
    """

    def __init__(
        self,
        egreso_repo: IEgresoRepository,
        libro_caja_repo: ILibroCajaRepository
    ):
        """
        Constructor con inyección de dependencias por puertos.
        
        Args:
            egreso_repo: Puerto del repositorio de egresos
            libro_caja_repo: Puerto del repositorio de libro de caja
        """
        self._egreso_repo = egreso_repo
        self._libro_caja_repo = libro_caja_repo

    async def execute(
        self,
        egreso_id: int,
        datos: EgresoAnular
    ) -> bool:
        """
        Anula un egreso existente.
        
        Args:
            egreso_id: ID del egreso a anular
            datos: Schema Pydantic con motivo y usuario (ya validados)
            
        Returns:
            True si se anuló correctamente
            
        Raises:
            EgresoNoEncontradoError: Si el egreso no existe
            EgresoYaAnuladoError: Si el egreso ya está anulado
            EgresoError: Para otros errores de negocio
        """
        # ✅ 1. Pydantic ya validó motivo (>=10 caracteres) y anulado_por (>0)
        
        # ✅ 2. Obtener egreso usando el puerto
        egreso_dict = await self._egreso_repo.obtener_por_id(egreso_id)
        
        if not egreso_dict:
            raise EgresoNoEncontradoError(
                f"Egreso con ID {egreso_id} no encontrado"
            )
        
        # ✅ 3. Validar que no esté anulado
        if egreso_dict.get('anulado', False):
            raise EgresoYaAnuladoError(
                f"El egreso {egreso_id} ya está anulado"
            )
        
        # ✅ 4. Obtener datos del egreso
        monto = egreso_dict.get('monto')
        sede_id = egreso_dict.get('sede_id')
        
        if not monto or monto <= 0:
            raise EgresoError(
                f"Egreso {egreso_id} tiene monto inválido: {monto}"
            )
        
        # ✅ 5. Anular el egreso usando el puerto
        try:
            success = await self._egreso_repo.anular(
                egreso_id=egreso_id,
                anulado_por_id=datos.anulado_por,
                motivo=datos.motivo_anulacion
            )
            
            if not success:
                raise EgresoError(f"No se pudo anular el egreso {egreso_id}")
                
        except Exception as e:
            raise EgresoError(f"Error al anular el egreso: {str(e)}")
        
        # ✅ 6. Registrar anulación en libro de caja (como ingreso de reversión)
        try:
            await self._libro_caja_repo.registrar_ingreso(
                monto=monto,
                fecha=datetime.utcnow(),
                registrado_por_id=datos.anulado_por,
                observaciones=f"Anulación de egreso ID {egreso_id}. Motivo: {datos.motivo_anulacion}",
                pago_id=None,
                sede_id=sede_id
            )
        except Exception as e:
            # El egreso ya se anuló, pero falló el libro de caja
            # Podrías implementar compensación o logging
            raise EgresoError(
                f"Egreso {egreso_id} anulado pero falló registro en libro de caja: {str(e)}"
            )
        
        return True
