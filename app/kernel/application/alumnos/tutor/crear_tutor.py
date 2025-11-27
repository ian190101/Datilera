from typing import Optional
from datetime import datetime

from app.kernel.domain.alumnos.tutor_entidad import TutorEntidad
from app.kernel.domain.alumnos.ports import TutorRepositoryPort
from app.kernel.domain.alumnos.errors import TutorDuplicadoError


class CrearTutorCU:
    """Crear un nuevo tutor."""

    def __init__(self, tutor_repo: TutorRepositoryPort):
        self.tutor_repo = tutor_repo

    async def ejecutar(
        self,
        nombres: str,
        apellido_paterno: str,
        numero_documento: str,
        apellido_materno: Optional[str] = None,
        tipo_documento: str = "CI",
        telefono_principal: Optional[str] = None,
        telefono_alternativo: Optional[str] = None,
        email: Optional[str] = None,
        direccion: Optional[str] = None,
        ocupacion: Optional[str] = None,
        lugar_trabajo: Optional[str] = None,
        telefono_trabajo: Optional[str] = None,
    ) -> TutorEntidad:
        existente = await self.tutor_repo.obtener_por_documento(numero_documento)
        if existente:
            raise TutorDuplicadoError(documento=numero_documento)

        tutor = TutorEntidad(
    nombres=nombres.strip(),
    apellido_paterno=apellido_paterno.strip(),
    apellido_materno=apellido_materno.strip() if apellido_materno else None,
    tipo_documento=tipo_documento,
    numero_documento=numero_documento.strip(),
    telefono_principal=telefono_principal or "",
    telefono_alternativo=telefono_alternativo,
    email=email,
    direccion=direccion,
    ocupacion=ocupacion,
    lugar_trabajo=lugar_trabajo,
    telefono_trabajo=telefono_trabajo,
    activo=True,
    creado_en=datetime.utcnow(),
)
        return await self.tutor_repo.crear(tutor)
