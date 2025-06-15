# 🪙 Coinbase DCA Bot (Advanced Trade API)

This bot automates a Dollar-Cost Averaging (DCA) strategy on Coinbase using the official [`coinbase-advanced-py`](https://pypi.org/project/coinbase-advanced-py/) SDK.

It places daily limit orders to buy BTC at a 2% discount from the spot price and includes:

- ✅ Time-in-force logic: cancels stale limit orders after 24 hours
- ✅ Fallback mechanism: places a market order if 3 recent limit orders were unfilled
- ✅ Persistent order history with fill status tracking
- ✅ Environment-variable-based secrets loading using `.env`

---

## 📁 File Overview

| File                 | Purpose                                                       |
| -------------------- | ------------------------------------------------------------- |
| `dca.py`             | Main script that runs the bot logic                           |
| `.env.example`       | Sample environment variables file for API credentials         |
| `order_history.json` | Local persistent storage for tracking order status            |
| `requirements.txt`   | Python dependencies (`python-dotenv`, `coinbase-advanced-py`) |
| `.github/workflows/` | _(Optional)_ GitHub Actions automation (not included here)    |

---

## ⚙️ Prerequisites

- Python 3.9 or higher
- A Coinbase **Advanced Trade** API key with:
  - Format: `organizations/{org_id}/apiKeys/{key_id}`
  - EC Private Key in PEM format

---

## 🔐 Environment Setup

1. Duplicate `.env.example` → `.env`
2. Fill in your values:

```env
COINBASE_API_KEY=organizations/your-org-id/apiKeys/your-key-id
COINBASE_API_SECRET="-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----"
```

> ⚠️ The key must use the **ECDSA** Signature Algorithm. This may be updated in the future.

---

## 🚀 Running the Bot

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run it manually

```bash
python dca.py
```

> The bot will:
>
> - Cancel unfilled limit orders older than 24 hours
> - Check if fallback to market buy is needed
> - Place a limit order 2% below spot price
> - Track all order states in `order_history.json`

---

## 🧪 Example Output

```
✅ Limit order placed at $42834.21 for 0.00023 BTC.
```

or

```
❌ Limit order failed: {'error': 'INSUFFICIENT_FUND', ...}
```

---

## 🛠 Configuration Options

You can edit these constants in `dca.py` to customize behavior:

| Constant         | Purpose                                         | Default |
| ---------------- | ----------------------------------------------- | ------- |
| `QUOTE_AMOUNT`   | How much USD to invest per trade                | `1`     |
| `PRICE_DISCOUNT` | Limit order % below spot price (0.98 = 2%)      | `0.98`  |
| `TIF_HOURS`      | Cancel limit orders older than this             | `24`    |
| `FALLBACK_DAYS`  | Fallback to market order if unfilled for N days | `3`     |

---

## 📦 Future Improvements

- [ ] GitHub Actions or AWS Lambda deployment
- [ ] Multi-coin support (ETH, SOL, etc.)
- [ ] Alerts via email or Slack
- [ ] Integration with Supabase or Google Sheets for metrics

---

## 📄 License

MIT

---

## 🙋‍♂️ Questions?

Open an issue or ping [@vjz3qz](https://github.com/vjz3qz) if you have trouble using the bot or want help adapting it for your use case.
