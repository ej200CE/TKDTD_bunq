
import sys
from time import sleep

from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.api_environment_type import ApiEnvironmentType
from bunq.sdk.context.bunq_context import BunqContext
from bunq.sdk.model.generated import endpoint

# ─────────────────────────────────────────────────────────────────────────
def main():
    # 0) read the sandbox API key
    if len(sys.argv) != 2 or not sys.argv[1].startswith("sandbox_"):
        sys.exit("Usage: python sandbox_demo.py <sandbox_api_key>")
    api_key = sys.argv[1]

    # 1) bootstrap & register context
    api_ctx = ApiContext(
        ApiEnvironmentType.SANDBOX,
        api_key,
        "python‑sandbox‑demo"
    )
    api_ctx.ensure_session_active()
    BunqContext.load_api_context(api_ctx)

    # 2) find the user and first monetary account
    user = endpoint.User.list().value[0].get_referenced_object()
    user_id = user.id_
    account = endpoint.MonetaryAccountBank.list(user_id).value[0]
    account_id = account.id_

    def balance(label):
        bal = endpoint.MonetaryAccountBank.get(user_id, account_id).value.balance
        print(f"{label}: {bal.value} {bal.currency}")

    balance("Balance before top‑up")

    # 3) request €500 from Sugar Daddy (use plain dicts)
    endpoint.RequestInquiry.create(
        amount_inquired={
            "value": "500",
            "currency": "EUR"
        },
        counterparty_alias={
            "type":  "EMAIL",
            "value": "sugardaddy@bunq.com",
            "name":  "Sugar Daddy"
        },
        description="Top‑up from sandbox_demo",
        allow_bunqme=False,
        user_id=user_id,
        monetary_account_id=account_id
    )
    print("🪄  Asked Sugar Daddy for €500 …")

    sleep(2)           # wait for auto‑accept
    balance("Balance after  top‑up")


# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()