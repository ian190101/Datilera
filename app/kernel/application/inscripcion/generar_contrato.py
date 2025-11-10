from pydantic import BaseModel
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.alumnos.alumnos import AlumnoRepository
from app.infrastructure.db.repositories.seguridad.usuarios import UsuarioRepository
from app.infrastructure.db.repositories.inscripcion.contratos import ContratoRepository
from app.kernel.domain.exceptions import EntityNotFoundException
from app.infrastructure.db.models.inscripcion import Contrato


class GenerateContractResponse(BaseModel):
    pdf_url: str


class GenerateContract:
    def __init__(
        self,
        form_repo: FormularioInscripcionRepository,
        alumno_repo: AlumnoRepository,
        user_repo: UsuarioRepository,
        contract_repo: ContratoRepository,
    ):
        self.form_repo = form_repo
        self.alumno_repo = alumno_repo
        self.user_repo = user_repo
        self.contract_repo = contract_repo

    async def execute(self, form_id: int) -> GenerateContractResponse:
        formulario = await self.form_repo.get_by_id(form_id)
        if not formulario:
            raise EntityNotFoundException(f"Formulario con id {form_id} no encontrado.")

        alumno = await self.alumno_repo.get_by_id(formulario.alumno_id)
        if not alumno:
            raise EntityNotFoundException(
                f"Alumno con id {formulario.alumno_id} no encontrado."
            )

        tutor = await self.user_repo.get_by_id(alumno.tutor_id)
        if not tutor:
            raise EntityNotFoundException(
                f"Tutor con id {alumno.tutor_id} no encontrado."
            )

        # TODO: Implementar la lógica real de generación de PDF del contrato
        # Por ahora, se simula la URL del PDF
        pdf_url = f"/contratos/{form_id}/contrato_{alumno.codigo}.pdf"
        codigo_contrato = f"CONTRATO-{formulario.sede_id}-{form_id}"

        new_contract = Contrato(
            formulario_id=form_id,
            codigo_contrato=codigo_contrato,
            pdf_url=pdf_url,
            fecha_emision=datetime.now().date(),
        )
        await self.contract_repo.create(new_contract)

        return GenerateContractResponse(pdf_url=pdf_url)