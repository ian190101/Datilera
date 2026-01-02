# app/application/use_cases/finanzas/registrar_egreso.py
"""
Caso de uso: Registrar un egreso (gasto).
Arquitectura hexagonal - Solo usa puertos, no implementaciones concretas.
"""
from datetime import datetime
from typing import Optional

from app.kernel.domain.finanzas.egreso_entidad import EgresoCreate
from app.kernel.domain.finanzas.ports import (
    IEgresoRepository,
    ILibroCajaRepository,
)
from app.kernel.domain.finanzas.errors import (
    ComprobantePagoYaExisteError,
    EgresoError,
)


class RegistrarEgresoUC:
    """
    Caso de uso: Registrar un egreso (gasto).
    
    Flujo:
    1. Validar duplicidad de comprobante (si aplica)
    2. Crear registro de egreso usando puerto
    3. Registrar movimiento en libro de caja usando puerto
    4. Retornar ID del egreso creado
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
        datos: EgresoCreate
    ) -> int:
        """
        Registra un nuevo egreso.
        
        Args:
            datos: Schema Pydantic con los datos del egreso (ya validados)
            
        Returns:
            ID del egreso creado
            
        Raises:
            ComprobanteYaExisteError: Si el comprobante está duplicado
            EgresoError: Para otros errores de negocio
        """
        # ✅ 1. Pydantic ya validó monto (>0) y descripción (>=5 caracteres)
        
        # ✅ 2. Verificar duplicidad de comprobante
        if datos.numero_comprobante:
            existe = await self._egreso_repo.verificar_duplicado_comprobante(
                datos.numero_comprobante
            )
            if existe:
                raise ComprobantePagoYaExisteError(
                    f"Ya existe un egreso con el comprobante '{datos.numero_comprobante}'"
                )
        
        # ✅ 3. Crear egreso usando el puerto
        try:
            egreso_id = await self._egreso_repo.crear(
                sede_id=datos.sede_id,
                monto=datos.monto,
                categoria_egreso_id=datos.categoria_egreso_id,
                descripcion=datos.descripcion,
                fecha_egreso=datos.fecha_egreso,
                numero_comprobante=datos.numero_comprobante,
                observaciones=datos.observaciones,
                registrado_por=datos.registrado_por
            )
        except Exception as e:
            raise EgresoError(f"Error al crear el egreso: {str(e)}")
        
        # ✅ 4. Registrar en libro de caja usando el puerto
        try:
            await self._libro_caja_repo.registrar_egreso(
                monto=datos.monto,
                fecha=datos.fecha_egreso,
                registrado_por_id=datos.registrado_por,
                observaciones=datos.descripcion,
                egreso_id=egreso_id,
                sede_id=datos.sede_id
            )
        except Exception as e:
            # Si falla el libro de caja, el egreso ya se creó
            # Aquí podrías implementar compensación o logging
            raise EgresoError(
                f"Egreso creado (ID: {egreso_id}) pero falló registro en libro de caja: {str(e)}"
            )
        
        return egreso_id
