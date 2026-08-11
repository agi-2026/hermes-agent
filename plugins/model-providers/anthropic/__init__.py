"""Native Anthropic provider profile."""

import json
import logging
import urllib.request

from hermes_cli.urllib_security import open_credentialed_url
from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)


class AnthropicProfile(ProviderProfile):
    """Native Anthropic — uses x-api-key header, not Bearer."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        """Anthropic uses x-api-key header and anthropic-version."""
        if not api_key:
            return None
        try:
            req = urllib.request.Request("https://api.anthropic.com/v1/models")
            req.add_header("x-api-key", api_key)
            req.add_header("anthropic-version", "2023-06-01")
            req.add_header("Accept", "application/json")
            with open_credentialed_url(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            return [
                m["id"]
                for m in data.get("data", [])
                if isinstance(m, dict) and "id" in m
            ]
        except Exception as exc:
            logger.debug("fetch_models(anthropic): %s", exc)
            return None


anthropic = AnthropicProfile(
    name="anthropic",
    # ``claude_subscription`` / ``claude-subscription`` are the subscription-OAuth
    # aliases: they resolve to this same profile so a user on a Claude Pro/Max plan
    # can select ``provider: claude_subscription`` (symmetric to the Codex
    # ``openai-codex`` subscription option) and get routed onto the existing
    # Anthropic OAuth path — no separate provider/transport required. The OAuth
    # credential detection, refresh, and rotation all live on this profile already
    # (see agent/anthropic_adapter.py, agent/credential_pool.py).
    aliases=(
        "claude",
        "claude-oauth",
        "claude-code",
        "claude_subscription",
        "claude-subscription",
    ),
    api_mode="anthropic_messages",
    # NOTE: ``env_vars`` is treated as *API-key* env vars by the credential
    # registry (hermes_cli/auth.py auto-extend, doctor, provider_catalog). The
    # subscription opt-in flag ``HERMES_CLAUDE_SUBSCRIPTION_AUTH`` is intentionally
    # NOT listed here — it is a boolean hint consumed by the setup flow, not a
    # secret. Adding it here would make Hermes mistake "1" for an Anthropic key.
    env_vars=("ANTHROPIC_API_KEY", "ANTHROPIC_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN"),
    base_url="https://api.anthropic.com",
    auth_type="api_key",
    default_aux_model="claude-haiku-4-5-20251001",
)

register_provider(anthropic)
