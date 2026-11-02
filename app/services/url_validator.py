"""Reusable URL validation and sanitization service."""

import re
import time
from typing import Any
from urllib.parse import urlparse, urlunparse
import httpx

from app.core.cache import InMemoryTTLCache, service_cache
from app.core.logging import get_logger

logger = get_logger("services.url_validator")

# Safe schemes allowed
SAFE_SCHEMES = {"http", "https"}

# Regex for basic domain validation
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)


class UrlValidationResult:
    """Represents the outcome of external URL validation."""

    def __init__(
        self,
        original_url: str,
        normalized_url: str | None = None,
        is_valid_format: bool = False,
        status: str = "UNVERIFIED",
        status_code: int | None = None,
        final_url: str | None = None,
        error_detail: str | None = None,
        checked_at: str | None = None,
    ):
        self.original_url = original_url
        self.normalized_url = normalized_url
        self.is_valid_format = is_valid_format
        self.status = status  # VERIFIED, UNVERIFIED_CHALLENGE, UNREACHABLE, TIMEOUT, INVALID_FORMAT
        self.status_code = status_code
        self.final_url = final_url
        self.error_detail = error_detail
        self.checked_at = checked_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_url": self.original_url,
            "normalized_url": self.normalized_url,
            "is_valid_format": self.is_valid_format,
            "status": self.status,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "error_detail": self.error_detail,
            "checked_at": self.checked_at,
        }


class UrlValidatorService:
    """Service validating external web links with redirect handling and anti-block resilience."""

    def __init__(self, cache: InMemoryTTLCache | None = service_cache) -> None:
        self.cache = cache

    @staticmethod
    def normalize_url(raw_url: str | None) -> str | None:
        """Safely normalize URL, ensure protocol, and reject malicious schemes."""
        if not raw_url or not isinstance(raw_url, str):
            return None

        clean = raw_url.strip()
        if not clean or clean.lower() in ("nan", "null", "none", "#"):
            return None

        # Reject unsafe schemes immediately
        lower_raw = clean.lower()
        if lower_raw.startswith(("javascript:", "data:", "vbscript:", "file:")):
            return None

        # Add https:// if protocol missing
        if not lower_raw.startswith(("http://", "https://")):
            clean = "https://" + clean

        try:
            parsed = urlparse(clean)
            if parsed.scheme.lower() not in SAFE_SCHEMES:
                return None
            if not parsed.netloc:
                return None

            # Reconstruct clean url
            normalized = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path or "/",
                parsed.params,
                parsed.query,
                ""  # Strip fragment tracking
            ))
            return normalized
        except Exception:
            return None

    @staticmethod
    def is_syntax_valid(normalized_url: str | None) -> bool:
        """Check if normalized URL syntax and host are valid."""
        if not normalized_url:
            return False
        try:
            parsed = urlparse(normalized_url)
            host = parsed.netloc.split(":")[0]
            if not host:
                return False
            # Check for domain or localhost
            return bool(DOMAIN_REGEX.match(host) or host in ("localhost", "127.0.0.1"))
        except Exception:
            return False

    async def validate_url_async(
        self,
        raw_url: str | None,
        timeout_seconds: float = 3.5,
    ) -> UrlValidationResult:
        """Check URL syntax and perform non-blocking HTTP verification with redirect resolution."""
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        normalized = self.normalize_url(raw_url)
        if not normalized or not self.is_syntax_valid(normalized):
            return UrlValidationResult(
                original_url=raw_url or "",
                normalized_url=normalized,
                is_valid_format=False,
                status="INVALID_FORMAT",
                error_detail="Invalid URL syntax or disallowed scheme",
                checked_at=now_iso,
            )

        # Check cache
        cache_key = f"url_valid:{normalized}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached and isinstance(cached, dict):
                return UrlValidationResult(**cached)

        # Non-blocking probe
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36 UrbanLens/1.0"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        result_status = "UNVERIFIED"
        status_code = None
        final_url = normalized
        error_detail = None

        try:
            async with httpx.AsyncClient(
                timeout=timeout_seconds,
                follow_redirects=True,
                headers=headers,
                verify=False,  # Tolerate self-signed/expired certs on municipal sites without marking broken
            ) as client:
                try:
                    resp = await client.head(normalized)
                    status_code = resp.status_code
                    final_url = str(resp.url)
                    if status_code in (404, 410):
                        result_status = "UNREACHABLE"
                    elif status_code in (403, 429, 503):
                        # WAF / Bot protection: Do NOT mark as broken
                        result_status = "UNVERIFIED_CHALLENGE"
                    elif 200 <= status_code < 400:
                        result_status = "VERIFIED"
                    else:
                        result_status = "VERIFIED"
                except (httpx.RequestError, httpx.HTTPStatusError):
                    # Fallback to GET with 1-byte range
                    resp = await client.get(normalized, headers={"Range": "bytes=0-100"})
                    status_code = resp.status_code
                    final_url = str(resp.url)
                    if status_code in (404, 410):
                        result_status = "UNREACHABLE"
                    elif status_code in (403, 429, 503):
                        result_status = "UNVERIFIED_CHALLENGE"
                    elif 200 <= status_code < 400:
                        result_status = "VERIFIED"
                    else:
                        result_status = "VERIFIED"
        except httpx.TimeoutException:
            result_status = "TIMEOUT"
            error_detail = "Verification request timed out"
        except httpx.ConnectError as ce:
            result_status = "UNREACHABLE"
            error_detail = f"DNS or connection failure: {str(ce)[:80]}"
        except Exception as exc:
            result_status = "UNVERIFIED_CHALLENGE"
            error_detail = str(exc)[:80]

        res = UrlValidationResult(
            original_url=raw_url or "",
            normalized_url=normalized,
            is_valid_format=True,
            status=result_status,
            status_code=status_code,
            final_url=final_url,
            error_detail=error_detail,
            checked_at=now_iso,
        )

        if self.cache:
            self.cache.set(cache_key, res.to_dict(), ttl_seconds=3600)

        return res
