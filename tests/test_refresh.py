import asyncio
from types import SimpleNamespace

from app.kernel.application.seguridad.refresh import Refresh, RefreshRequest


class FakeTokens:
    def decode_token(self, token):
        return {"type": "refresh", "sub": "9", "jti": "jti-anterior"}

    def create_access_token(self, user_id, sede_id, permisos, roles=None):
        return f"access:{user_id}:{sede_id}"

    def create_refresh_token(self, user_id, jti):
        return f"refresh:{user_id}:{jti}"


class FakeUsers:
    async def get_by_id(self, user_id):
        permiso = SimpleNamespace(nombre_completo="Finanzas:Ver")
        return SimpleNamespace(
            id=user_id,
            sede_id=2,
            activo=True,
            roles=[SimpleNamespace(nombre="ADMINISTRADOR", permisos=[permiso])],
        )


class FakeRevocados:
    def __init__(self):
        self.items = []

    async def esta_revocado(self, jti):
        return jti in self.items

    async def revocar(self, jti):
        self.items.append(jti)


class FakeSesiones:
    def __init__(self):
        self.deleted = []
        self.created = []

    async def eliminar_por_refresh(self, token):
        self.deleted.append(token)
        return True

    async def crear(self, usuario_id, refresh_token, expira_en):
        self.created.append((usuario_id, refresh_token, expira_en))


def test_rotacion_revoca_jti_anterior_y_persiste_token_nuevo():
    revocados = FakeRevocados()
    sesiones = FakeSesiones()
    use_case = Refresh(FakeUsers(), FakeTokens(), revocados, sesiones)

    result = asyncio.run(use_case.execute(RefreshRequest(refresh_token="x" * 20)))

    assert revocados.items == ["jti-anterior"]
    assert sesiones.deleted == ["x" * 20]
    assert sesiones.created[0][1] == result.refresh_token
    assert "jti-anterior" not in result.refresh_token
