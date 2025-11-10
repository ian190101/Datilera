from pydantic import BaseModel
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.inscripcion.firmas import FirmaRepository
from app.kernel.domain.exceptions import EntityNotFoundException
from app.infrastructure.db.models.inscripcion import Firma


class SaveSignatureRequest(BaseModel):
    firmante: str
    firma_url: str  # URL donde se almacena la imagen de la firma


class SaveSignature:
    def __init__(
        self,
        form_repo: FormularioInscripcionRepository,
        signature_repo: FirmaRepository,
    ):
        self.form_repo = form_repo
        self.signature_repo = signature_repo

    async def execute(self, form_id: int, request: SaveSignatureRequest) -> None:
        if not await self.form_repo.get_by_id(form_id):
            raise EntityNotFoundException(f"Formulario con id {form_id} no encontrado.")

        # TODO: Implementar la lógica real de almacenamiento de la imagen de la firma
        # Por ahora, se asume que firma_url ya contiene la URL de la imagen guardada

        new_firma = Firma(
            formulario_id=form_id,
            firmante=request.firmante,
            firma_url=request.firma_url,
        )
        await self.signature_repo.create(new_firma)