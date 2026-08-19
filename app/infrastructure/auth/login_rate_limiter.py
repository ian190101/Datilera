from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque

from redis.asyncio import Redis

from app.config.settings import get_settings


class LoginRateLimiter:
    """Limitador distribuido con respaldo local para no desproteger el login."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        # Redis mejora la consistencia entre procesos, pero nunca debe bloquear el
        # acceso durante varios segundos si el servicio está apagado en desarrollo.
        self._redis = Redis.from_url(
            str(get_settings().REDIS_URL),
            decode_responses=True,
            socket_connect_timeout=0.20,
            socket_timeout=0.20,
            retry_on_timeout=False,
            health_check_interval=30,
        )
        self._redis_retry_at = 0.0
        self._local: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> int | None:
        if not self._redis_is_available():
            return await self._local_check(key)
        redis_key = f"datilera:auth:{key}"
        try:
            ttl = await self._redis.ttl(redis_key)
            attempts = await self._redis.get(redis_key)
            if attempts is not None and int(attempts) >= self.max_attempts:
                return max(ttl, 1)
            return None
        except Exception:
            self._mark_redis_unavailable()
            return await self._local_check(key)

    async def hit(self, key: str) -> None:
        if not self._redis_is_available():
            await self._local_hit(key)
            return
        redis_key = f"datilera:auth:{key}"
        try:
            attempts = await self._redis.incr(redis_key)
            if attempts == 1:
                await self._redis.expire(redis_key, self.window_seconds)
        except Exception:
            self._mark_redis_unavailable()
            await self._local_hit(key)

    async def reset(self, key: str) -> None:
        async with self._lock:
            self._local.pop(key, None)
        if not self._redis_is_available():
            return
        try:
            await self._redis.delete(f"datilera:auth:{key}")
        except Exception:
            self._mark_redis_unavailable()

    async def _local_hit(self, key: str) -> None:
        async with self._lock:
            now = time.monotonic()
            bucket = self._local[key]
            self._purge(bucket, now)
            bucket.append(now)

    def _redis_is_available(self) -> bool:
        return time.monotonic() >= self._redis_retry_at

    def _mark_redis_unavailable(self) -> None:
        # Reintenta periódicamente para recuperar el modo distribuido sin reiniciar.
        self._redis_retry_at = time.monotonic() + 30.0

    async def _local_check(self, key: str) -> int | None:
        async with self._lock:
            now = time.monotonic()
            bucket = self._local[key]
            self._purge(bucket, now)
            if len(bucket) < self.max_attempts:
                return None
            return max(int(self.window_seconds - (now - bucket[0])), 1)

    def _purge(self, bucket: deque[float], now: float) -> None:
        threshold = now - self.window_seconds
        while bucket and bucket[0] <= threshold:
            bucket.popleft()


login_rate_limiter = LoginRateLimiter()
