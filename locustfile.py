from locust import HttpUser, task, between



class DatileraUser(HttpUser):
    wait_time = between(1, 4)

    # Opcional: headers base (útil con Cloudflare)
    def _base_headers(self):
        # Host a veces ayuda cuando hay proxy/tunnel
        host = self.host.replace("https://", "").replace("http://", "").rstrip("/")
        return {
            "User-Agent": "locust",
            "Accept": "application/json",
            "Host": host,
        }

    def on_start(self):
        self.client.verify = False
        headers = self._base_headers()
        headers["Content-Type"] = "application/json"

        import random, time
        time.sleep(random.uniform(0, 10))
        with self.client.post(
            "/api/v1/auth/login",
            json={"username": "ian", "password": "a1b2c3d4e5@"},
            headers=headers,
            catch_response=True,
            allow_redirects=False,
            # verify=True por defecto; con Cloudflare no necesitas verify=False
        ) as r:
            if r.status_code != 200:
                r.failure(f"Login failed {r.status_code}: {r.text[:200]}")
                return

        # Cookie real que tu backend setea
        if "accesstoken" not in self.client.cookies:
            # Esto NO revienta el usuario; queda registrado en "Failures"
            with self.client.get("/health", catch_response=True, name="NO_COOKIE") as rr:
                rr.failure(f"No llegó accesstoken. cookies={self.client.cookies}")
            return

        # Smoke test del perfil
        with self.client.get(
            "/api/v1/usuarios/me",
            headers=self._base_headers(),
            catch_response=True,
            allow_redirects=False,
        ) as r:
            if r.status_code != 200:
                r.failure(f"/usuarios/me failed {r.status_code}: {r.text[:200]}")

    @task(3)
    def ver_dashboard(self):
        self.client.get(
            "/api/v1/reportes/dashboard/metricas?period=month",
            headers=self._base_headers(),
            name="/api/v1/reportes/dashboard/metricas",
        )

    @task(2)
    def listar_inscripciones(self):
        self.client.get(
            "/api/v1/inscripciones?page=1",
            headers=self._base_headers(),
            name="/api/v1/inscripciones",
        )

    @task(1)
    def verificar_perfil(self):
        self.client.get(
            "/api/v1/usuarios/me",
            headers=self._base_headers(),
            name="/api/v1/usuarios/me",
        )
