Here you go:

---

## 📄 `README.md`

````markdown
# 🪙 Coinbase DCA Bot (Advanced Trade API)

This is an automated DCA (Dollar-Cost Averaging) bot for Coinbase using the [coinbase-advancedtrade-python](https://github.com/rhettre/coinbase-advancedtrade-python) SDK.  
It supports:

- 🔁 Daily limit buy orders at a discount (via price multiplier)
- 🕒 Time-in-force: auto-cancels stale limit orders after X hours
- 🧯 Fallback: market buy if N consecutive limit orders remain unfilled
- 🤖 Full GitHub Actions automation

---

## 🚀 Features

- Limit order at X% below spot price (e.g., 2% discount)
- Auto-cancel stale unfilled orders (default: 24h)
- After N days of failed limit orders (default: 3), fallback to market buy
- JSON-based order history tracking (can be swapped for database)
- Designed for daily GitHub Actions execution

---

## 🔧 Setup Instructions

### 1. Clone this repo

```bash
git clone https://github.com/vjz3qz/dca.git
cd dca
```
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file (or set env vars manually) using the example below.

### 4. Run locally

```bash
python dca.py
```

### 5. Or deploy via GitHub Actions

1. Go to **Repo → Settings → Secrets and Variables → Actions**
2. Add the following secrets:

   - `COINBASE_API_KEY`
   - `COINBASE_API_SECRET`

3. Push to main and GitHub Actions will run daily

---

## 🔐 Environment Variables

See [.env.example](.env.example)

- `COINBASE_API_KEY`: Your Coinbase Advanced Trade API key (e.g., `organizations/{org_id}/apiKeys/{key_id}`)
- `COINBASE_API_SECRET`: Your EC private key in PEM format

---

## ⚙️ Configuration (inside `dca.py`)

| Variable           | Description                            | Default  |
| ------------------ | -------------------------------------- | -------- |
| `PRICE_MULTIPLIER` | Limit price as % of current spot       | `"0.98"` |
| `TIF_HOURS`        | Time-in-force cancel threshold (hours) | `24`     |
| `FALLBACK_DAYS`    | Days to fallback to market buy         | `3`      |
| `BUY_AMOUNT`       | Amount in USD to invest per trade      | `"10"`   |

---

## 📁 Files

- `dca.py` — main trading logic
- `order_history.json` — local file tracking past orders
- `.github/workflows/dca.yml` — GitHub Actions automation
- `requirements.txt` — Python dependency list

---

## 📌 Notes

- This script assumes trades are made in `BTC-USDC`. You can change this in `dca.py`.
- Fallback logic checks if any limit orders were filled in last N days (basic implementation — can be upgraded to query actual fills).
- This is a basic bot — use responsibly and at your own risk.

---

## 📄 License

MIT

````

---

## 📄 `.env.example`

```dotenv
# Coinbase Advanced Trade API Key
COINBASE_API_KEY=organizations/your-org-id/apiKeys/your-key-id

# Coinbase Advanced Trade EC PRIVATE KEY
COINBASE_API_SECRET="-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----\n"
````

---
