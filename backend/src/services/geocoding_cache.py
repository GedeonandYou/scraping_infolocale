"""Redis-backed cache for geocoding results."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Optional, Dict, Any

from loguru import logger

from src.config.settings import get_settings

try:
    import redis.asyncio as redis
except Exception:  # pragma: no cover - optional dependency
    redis = None

settings = get_settings()


class GeocodingCache:
    """Async Redis cache for geocoding results."""

    def __init__(self) -> None:
        self.enabled = settings.GEOCODING_CACHE_ENABLED
        self.ttl = settings.GEOCODING_CACHE_TTL
        self.negative_ttl = settings.GEOCODING_CACHE_NEGATIVE_TTL
        self.redis = None

        if not self.enabled:
            logger.info("Geocoding cache disabled")
            return
        if redis is None:
            logger.warning("redis package not installed; geocoding cache disabled")
            self.enabled = False
            return

        redis_url = settings.redis_url
        if not redis_url:
            logger.warning("Redis URL not configured; geocoding cache disabled")
            self.enabled = False
            return

        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            logger.info("Geocoding cache enabled (Redis)")
        except Exception as exc:  # pragma: no cover - connection failure
            logger.warning(f"Failed to initialize Redis cache: {exc}")
            self.enabled = False

    @staticmethod
    def _normalize_text(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"\s+", " ", value)
        return value

    def _cache_key(
        self,
        address: Optional[str],
        city: Optional[str],
        zipcode: Optional[str],
        country: Optional[str],
    ) -> Optional[str]:
        parts = [p for p in [address, zipcode, city, country] if p]
        if not parts:
            return None
        normalized = self._normalize_text("|".join(parts))
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        return f"geocode:{digest}"

    async def get(
        self,
        address: Optional[str],
        city: Optional[str],
        zipcode: Optional[str],
        country: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        if not self.redis:
            return None

        key = self._cache_key(address, city, zipcode, country)
        if not key:
            return None

        try:
            payload = await self.redis.get(key)
            if not payload:
                return None
            data = json.loads(payload)
            if data.get("_not_found"):
                return None
            return data
        except Exception as exc:
            logger.debug(f"Redis cache get failed: {exc}")
            return None

    async def set(
        self,
        address: Optional[str],
        city: Optional[str],
        zipcode: Optional[str],
        country: Optional[str],
        data: Dict[str, Any],
    ) -> None:
        if not self.redis:
            return

        key = self._cache_key(address, city, zipcode, country)
        if not key:
            return

        try:
            payload = json.dumps(data)
            await self.redis.set(key, payload, ex=self.ttl)
        except Exception as exc:
            logger.debug(f"Redis cache set failed: {exc}")

    async def set_not_found(
        self,
        address: Optional[str],
        city: Optional[str],
        zipcode: Optional[str],
        country: Optional[str],
    ) -> None:
        if not self.redis:
            return

        key = self._cache_key(address, city, zipcode, country)
        if not key:
            return

        try:
            payload = json.dumps({"_not_found": True})
            await self.redis.set(key, payload, ex=self.negative_ttl)
        except Exception as exc:
            logger.debug(f"Redis cache set_not_found failed: {exc}")

    async def close(self) -> None:
        if not self.redis:
            return
        try:
            await self.redis.close()
        except Exception:
            pass
