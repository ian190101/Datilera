from pathlib import Path
from types import SimpleNamespace

from app.kernel.application.services.tutor_existing_registration import (
    actualizar_perfil_tutor_existente,
)

ROOT = Path(__file__).resolve().parents[1]


class Formulario(dict):
    def getlist(self, clave: str) -> list[str]:
        valor = self.get(clave, [])
        return valor if isinstance(valor, list) else [valor]


def test_actualizar_tutor_existente_no_cambia_identidad_ni_cuenta() -> None:
    tutor = SimpleNamespace(
        nombres="María",
        apellidos="Pérez",
        ci_numero="123",
        ci_expedido="CBBA",
        profesion=None,
        lugar_trabajo=None,
        direccion_trabajo=None,
        celular="70000000",
        email=None,
        usuario_id=17,
    )
    formulario = Formulario(
        tutor1_nombres="Nombre manipulado",
        tutor1_ci="456",
        tutor1_celular="71111111",
        tutor1_email="maria@example.com",
    )

    actualizar_perfil_tutor_existente(tutor, formulario)

    assert tutor.nombres == "María"
    assert tutor.apellidos == "Pérez"
    assert tutor.usuario_id == 17
    assert tutor.celular == "71111111"


def test_interfaz_preinscribe_hermano_con_color_primario_e_icono() -> None:
    javascript = (ROOT / "app/interfaces/web/static/js/inscripciones-list.js").read_text(
        encoding="utf-8"
    )
    plantilla = (ROOT / "app/interfaces/web/templates/inscripciones/list.html").read_text(
        encoding="utf-8"
    )

    assert 'title="Preinscribir hermano"' in javascript
    assert 'class="fas fa-children"' in javascript
    assert 'id="modal-preinscribir-hermano"' in plantilla
    assert 'class="bg-primary-600 px-6 py-5 text-white"' in plantilla


def test_flujo_tutor_existente_no_envia_credenciales() -> None:
    javascript = (ROOT / "app/interfaces/web/static/js/registro-tutores.js").read_text(
        encoding="utf-8"
    )
    rutas = (ROOT / "app/interfaces/web/routes.py").read_text(encoding="utf-8")

    assert "completar-inscripcion-existente" in javascript
    assert "control.disabled = true" in javascript
    assert '"/api/v1/tutor/inscripciones-pendientes"' in rutas
    assert 'tipo="completar_inscripcion_hermano"' in rutas


def test_listado_inscripciones_no_carga_usuario_tutor_de_forma_perezosa() -> None:
    rutas = (ROOT / "app/interfaces/web/routes.py").read_text(encoding="utf-8")
    inicio = rutas.index("async def listar_inscripciones_endpoint")
    fin = rutas.index("#Lista simple de alumnos", inicio)
    listado = rutas[inicio:fin]

    assert "usuarios_tutores_activos" in listado
    assert "tutor.usuario and tutor.usuario.activo" not in listado
