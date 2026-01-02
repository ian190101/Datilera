# app/infrastructure/queues/broker.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Protocol

from redis import Redis
from rq import Queue
from rq.job import Job
from app.config.settings import get_settings


class JobBroker(Protocol):
    def enqueue(
        self,
        task_name: str,
        *,
        args: list[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        queue_name: str = "default",
    ) -> str: ...

    def enqueue_at(
        self,
        task_name: str,
        run_at: datetime,
        *,
        args: list[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        queue_name: str = "default",
    ) -> str: ...

    def enqueue_in(
        self,
        task_name: str,
        delay: timedelta,
        *,
        args: list[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        queue_name: str = "default",
    ) -> str: ...


class RQJobBroker:
    def __init__(self, redis_url: str | None = None) -> None:
        settings = get_settings()
        url = redis_url or str(settings.REDIS_URL)
        self._redis = Redis.from_url(url)
        self._queues: dict[str, Queue] = {
            "default": Queue("default", connection=self._redis),
            "low": Queue("low", connection=self._redis),
            "high": Queue("high", connection=self._redis),
        }

    def _get_queue(self, name: str) -> Queue:
        return self._queues.get(name) or self._queues["default"]

    def enqueue(
        self,
        task_name: str,
        *,
        args: list[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        queue_name: str = "default",
    ) -> str:
        queue = self._get_queue(queue_name)
        job: Job = queue.enqueue(
            task_name,
            *(args or []),
            **(kwargs or {}),
        )
        return job.id

    def enqueue_at(
        self,
        task_name: str,
        run_at: datetime,
        *,
        args: list[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        queue_name: str = "default",
    ) -> str:
        # Asegurar timezone-aware para RQ
        if run_at.tzinfo is None:
            run_at = run_at.replace(tzinfo=timezone.utc)

        queue = self._get_queue(queue_name)
        job: Job = queue.enqueue_at(
            run_at,
            task_name,
            *(args or []),
            **(kwargs or {}),
        )
        return job.id

    def enqueue_in(
        self,
        task_name: str,
        delay: timedelta,
        *,
        args: list[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        queue_name: str = "default",
    ) -> str:
        queue = self._get_queue(queue_name)
        job: Job = queue.enqueue_in(
            delay,
            task_name,
            *(args or []),
            **(kwargs or {}),
        )
        return job.id


# Instancia global que usará JobQueueService
broker: JobBroker = RQJobBroker()
