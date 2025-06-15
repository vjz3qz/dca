# 🪙 Coinbase DCA Bot (Advanced Trade API)

This bot automates a Dollar-Cost Averaging (DCA) strategy on Coinbase using the official [`coinbase-advanced-py`](https://pypi.org/project/coinbase-advanced-py/) SDK.

It places daily limit orders to buy BTC at a 2% discount from the spot price and includes:

- ✅ Time-in-force logic: cancels stale limit orders after 24 hours
- ✅ Fallback mechanism: places a market order if 3 recent limit orders were unfilled
- ✅ Persistent order history with fill status tracking
- ✅ Track all order states in `order_history.json` (if running locally)

---

## 📁 File Overview

| File                        | Purpose                                                       |
| --------------------------- | ------------------------------------------------------------- |
| `dca.py`                    | Main script that runs the bot logic                           |
| `.env.example`              | Sample environment variables file for API credentials         |
| `order_history.json`        | Local persistent storage for tracking order status            |
| `requirements.txt`          | Python dependencies (`python-dotenv`, `coinbase-advanced-py`) |
| `.github/workflows/dca.yml` | GitHub Actions automation script for scheduled runs           |

---

## ⚙️ Prerequisites

- Python 3.9 or higher
- A Coinbase **Advanced Trade** API key with:
  - Format: `organizations/{org_id}/apiKeys/{key_id}`
  - EC Private Key in PEM format

---

## 🔐 Environment Setup (Local)

1. Duplicate `.env.example` → `.env`
2. Fill in your values:

```env
COINBASE_API_KEY=organizations/your-org-id/apiKeys/your-key-id
COINBASE_API_SECRET="-----BEGIN EC PRIVATE KEY-----\n...\n-----END EC PRIVATE KEY-----"
```

> ⚠️ The key must use the **ECDSA** Signature Algorithm. This may be updated in the future.

---

## 🚀 Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the bot

```bash
python dca.py
```

---

## ☁️ Deploy as a GitHub Actions Scheduled Job

### 1. Add GitHub Secrets

In your repo:

- Go to **Settings → Secrets and Variables → Actions**
- Add the following secrets:

  - `COINBASE_API_KEY`
  - `COINBASE_API_SECRET`

### 2. Create workflow file: `.github/workflows/dca.yml`

```yaml
name: Coinbase DCA Bot

on:
  schedule:
    - cron: "0 13 * * *" # Daily at 9 AM Eastern
  workflow_dispatch:

jobs:
  run-dca:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run DCA bot
        env:
          COINBASE_API_KEY: ${{ secrets.COINBASE_API_KEY }}
          COINBASE_API_SECRET: ${{ secrets.COINBASE_API_SECRET }}
        run: python dca.py
```

### 3. Push your changes

```bash
git add .
git commit -m "Add GitHub Actions workflow"
git push origin main
```

### 4. Trigger manually or wait for daily run

Go to the **Actions tab** in GitHub and either wait for the scheduled time or click **“Run workflow”** to test.

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

## 🛠 Configuration Options (inside `dca.py`)

You can edit these constants in `dca.py` to customize behavior:

| Constant         | Purpose                                         | Default |
| ---------------- | ----------------------------------------------- | ------- |
| `QUOTE_AMOUNT`   | How much USD to invest per trade                | `1`     |
| `PRICE_DISCOUNT` | Limit order % below spot price (0.98 = 2%)      | `0.98`  |
| `TIF_HOURS`      | Cancel limit orders older than this             | `24`    |
| `FALLBACK_DAYS`  | Fallback to market order if unfilled for N days | `3`     |

---

## 📦 Future Improvements

- [ ] Multi-coin support (ETH, SOL, etc.)
- [ ] Slack/email notifications on fallback
- [ ] Logging to Google Sheets or Supabase

---

## 📄 License

MIT

---

## 🙋‍♂️ Questions?

Open an issue or ping [@vjz3qz](https://github.com/vjz3qz) if you have trouble using the bot or want help adapting it for your use case.
