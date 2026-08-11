# Claude subscription auth (Pro / Max) via OAuth

Hermes can use **Claude as the model backend on your Claude subscription** (Pro,
Max, Team, or Enterprise) via OAuth, instead of a Developer Platform API key that
bills per token on top of your plan. This routes usage into Anthropic's Agent SDK
subscription credit rather than a separate metered API key.

This is provided by the existing `anthropic` provider profile — there is **no
separate `claude-agent-sdk` provider or transport**. The subscription-OAuth path
is the same Anthropic Messages API surface used for API keys, with OAuth
credentials swapped in. (Wrapping the Claude Agent SDK's own agent loop was
considered and rejected: Hermes is already an agent, and running both loops would
fight for control of tool use and context.)

## How to enable

Pick whichever is convenient — all three resolve to the same `anthropic` profile:

1. **`hermes model` → Anthropic → option 1 (Claude Pro/Max subscription)** — runs
   the OAuth login flow and stores the credentials.
2. **Auto-detect Claude Code credentials.** If you already ran `claude
   setup-token` (credentials at `~/.claude/.credentials.json`) and no Anthropic
   API key is set, Hermes detects and uses them automatically.
3. **`HERMES_CLAUDE_SUBSCRIPTION_AUTH=1`.** Set this env var to bias the setup
   flow toward the subscription-OAuth path (Enter defaults to option 1 instead of
   cancelling). This is the explicit opt-in equivalent of auto-detection.

You can also select the provider by its subscription alias in config or on the
CLI:

```yaml
model:
  provider: claude_subscription   # alias of `anthropic`; uses the OAuth path
  default: claude-sonnet-4-20250514
```

`claude_subscription` (and `claude-subscription`) are aliases of the `anthropic`
provider, symmetric to how `openai-codex` surfaces the ChatGPT/Codex
subscription option.

## ⚠ Shared / multi-user deployments

Per Anthropic, the Agent SDK subscription credit is **"sized for individual
experimentation."** For shared or multi-user deployments — production services,
multi-tenant automation, CI fleets — use an **Anthropic API key** instead.
Routing many users through a single subscription may exceed the plan's Agent SDK
credit and can violate Anthropic's terms.

Hermes prints this warning when you choose the subscription-OAuth path in
`hermes model`.

## Credential handling

OAuth tokens are secrets. Hermes:

- reads Claude Code credentials from `~/.claude/.credentials.json` and Hermes'
  own PKCE store at `~/.hermes/.anthropic_oauth.json`;
- refreshes / rotates them through the shared credential-pool plumbing (the same
  machinery used for the Codex OAuth pool);
- never deletes the external Claude Code credential file on `auth remove` (it
  only suppresses the pool seed);
- masks/truncates tokens when displaying them.

## References

- [Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
