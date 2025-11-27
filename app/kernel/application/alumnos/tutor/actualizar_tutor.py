from typing import Optional
from datetime import datetime

from app.kernel.domain.alumnos.tutor_entidad import TutorEntidad
from app.kernel.domain.alumnos.ports import TutorRepositoryPort
from app.kernel.domain.alumnos.errors import TutorNoEncontradoError, TutorDuplicadoError


class ActualizarTutorCU:
    """Actualizar datos de un tutor."""

    def __init__(self, tutor_repo: TutorRepositoryPort):
        self.tutor_repo = tutor_repo

    async def ejecutar(
        self,
        tutor_id: int,
        nombres: Optional[str] = None,
        apellido_paterno: Optional[str] = None,
        apellido_materno: Optional[str] = None,
        numero_documento: Optional[str] = None,
        tipo_documento: Optional[str] = None,
        telefono_principal: Optional[str] = None,
        telefono_alternativo: Optional[str] = None,
        email: Optional[str] = None,
        direccion: Optional[str] = None,
        ocupacion: Optional[str] = None,
        lugar_trabajo: Optional[str] = None,
        telefono_trabajo: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> TutorEntidad:
        tutor = await self.tutor_repo.obtener_por_id(tutor_id)
        if not tutor:
            raise TutorNoEncontradoError(tutor_id=tutor_id)

        if numero_documento and numero_documento != tutor.numero_documento:
            existente = await self.tutor_repo.obtener_por_documento(numero_documento)
            if existente and existente.id != tutor_id:
                raise TutorDuplicadoError(documento=numero_documento)

        data = tutor.model_dump()

        def set_if_not_none(field: str, value):
            if value is not None:
                data[field] = value

        set_if_not_none("nombres", nombres and nombres.strip())
        set_if_not_none("apellido_paterno", apellido_paterno and apellido_paterno.strip())
        set_if_not_none("apellido_materno", apellido_materno and apellido_materno.strip())
        set_if_not_none("numero_documento", numero_documento and numero_documento.strip())
        set_if_not_none("tipo_documento", tipo_documento)
        set_if_not_none("telefono_principal", telefono_principal)
        set_if_not_none("telefono_alternativo", telefono_alternativo)
        set_if_not_none("email", email)
        set_if_not_none("direccion", direccion)
        set_if_not_none("ocupacion", ocupacion)
        set_if_not_none("lugar_trabajo", lugar_trabajo)
        set_if_not_none("telefono_trabajo", telefono_trabajo)
        set_if_not_none("activo", activo)
        data["actualizado_en"] = datetime.utcnow()

        actualizado = TutorEntidad(**data)
        return await self.tutor_repo.actualizar(tutor_id, actualizado)
