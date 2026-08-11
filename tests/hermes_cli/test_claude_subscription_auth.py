"""Claude subscription-OAuth helpers for the Anthropic model setup flow.

Covers the issue-named deltas:
- HERMES_CLAUDE_SUBSCRIPTION_AUTH env-var opt-in detection
- the shared/multi-user "sized for individual experimentation" warning
- the `claude_subscription` provider alias resolving to `anthropic`
"""

from __future__ import annotations

import pytest

from hermes_cli.model_setup_flows import (
    _CLAUDE_SUBSCRIPTION_AUTH_ENV,
    _CLAUDE_SUBSCRIPTION_SHARED_USE_WARNING,
    _claude_subscription_auth_requested,
    _print_claude_subscription_shared_use_warning,
)


@pytest.mark.parametrize("val", ["1", "true", "TRUE", "yes", "on", " On "])
def test_flag_truthy_values(monkeypatch, val):
    monkeypatch.setenv(_CLAUDE_SUBSCRIPTION_AUTH_ENV, val)
    assert _claude_subscription_auth_requested() is True


@pytest.mark.parametrize("val", ["", "0", "false", "no", "off", "maybe"])
def test_flag_falsy_values(monkeypatch, val):
    monkeypatch.setenv(_CLAUDE_SUBSCRIPTION_AUTH_ENV, val)
    assert _claude_subscription_auth_requested() is False


def test_flag_unset(monkeypatch):
    monkeypatch.delenv(_CLAUDE_SUBSCRIPTION_AUTH_ENV, raising=False)
    assert _claude_subscription_auth_requested() is False


def test_shared_use_warning_mentions_individual_experimentation():
    # Mirrors Anthropic's stated terms: the Agent SDK credit is "sized for
    # individual experimentation".
    assert "individual experimentation" in _CLAUDE_SUBSCRIPTION_SHARED_USE_WARNING
    assert "API key" in _CLAUDE_SUBSCRIPTION_SHARED_USE_WARNING


def test_warning_printer_emits_warning(capsys):
    _print_claude_subscription_shared_use_warning()
    out = capsys.readouterr().out
    assert "individual experimentation" in out


def test_warning_contains_no_secret_material():
    # Defensive: the warning must be static copy, never echo a token.
    assert "sk-ant" not in _CLAUDE_SUBSCRIPTION_SHARED_USE_WARNING
    assert "Bearer" not in _CLAUDE_SUBSCRIPTION_SHARED_USE_WARNING


def test_claude_subscription_alias_resolves_to_anthropic():
    from providers import get_provider_profile

    assert get_provider_profile("claude_subscription").name == "anthropic"
    assert get_provider_profile("claude-subscription").name == "anthropic"
