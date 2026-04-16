import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")


def get_balance():
    if not BINANCE_API_KEY or not BINANCE_SECRET:
        print("❌ ERROR: BINANCE_API_KEY or BINANCE_SECRET not set in .env")
        return

    try:
        client = Client(BINANCE_API_KEY, BINANCE_SECRET)
        account = client.get_account()

        print("\n💰 BINANCE BALANCE")
        print("=" * 35)

        total_usdt = 0.0
        has_balance = False

        for asset in account["balances"]:
            free = float(asset["free"])
            locked = float(asset["locked"])
            total = free + locked

            if total > 0:
                has_balance = True
                print(
                    f"  {asset['asset']:<8} Free: {free:<15.6f}  Locked: {locked:.6f}"
                )

                # Estimate USDT value
                if asset["asset"] == "USDT":
                    total_usdt += total
                else:
                    try:
                        ticker = client.get_symbol_ticker(
                            symbol=f"{asset['asset']}USDT"
                        )
                        price = float(ticker["price"])
                        usdt_val = total * price
                        total_usdt += usdt_val
                        print(f"           ≈ ${usdt_val:.2f} USDT  (@ ${price:.4f})")
                    except Exception:
                        pass  # pair might not exist vs USDT

        if not has_balance:
            print("  No assets with balance found.")

        print("=" * 35)
        print(f"  📊 Est. Total Value: ${total_usdt:.2f} USDT")
        print("=" * 35)
        print()

    except BinanceAPIException as e:
        print(f"❌ Binance API Error: {e.message}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    get_balance()
