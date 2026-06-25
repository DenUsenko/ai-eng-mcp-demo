# Finnhub MCP Server

MCP-сервер, який підключає Claude Desktop до real-time даних фондового ринку через [Finnhub](https://finnhub.io/).

## Що всередині

| Тип | Назва | Аргументи | Що робить |
|-----|-------|-----------|-----------|
| 🔧 Tool | `get_company_profile` | `symbol` | Профіль компанії: назва, країна, біржа, market cap, IPO |
| 🔧 Tool | `get_stock_quote` | `symbol` · `[include_52w]` | Real-time котирування; з `include_52w=True` — додає 52-тижневий діапазон |
| 🔧 Tool | `get_market_news` | `[category]` | Останні 5 headlines: `general` / `forex` / `merger` / `crypto` |
| 📄 Resource | `watchlist://my-tickers` | — | Персональний watchlist — список тікерів |
| 💬 Prompt | `watchlist-snapshot` | — | Аналізує watchlist і підсвічує потенційні покупки |

---

## Швидкий старт

### 1. Отримай Finnhub API key

Безкоштовно на [finnhub.io](https://finnhub.io/) — реєстрація займає хвилину.

### 2. Додай сервер у Claude Desktop

Відкрий `claude_desktop_config.json` і додай блок нижче:

```json
{
  "mcpServers": {
    "finnhub": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/DenUsenko/ai-eng-mcp-demo", "finnhub-mcp"],
      "env": {
        "FINNHUB_API_KEY": "your_key_here"
      }
    }
  }
}
```

Розташування конфігу:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Клонувати репозиторій і встановлювати залежності вручну не потрібно — `uvx` зробить це автоматично при першому запуску.

### 3. Перезапусти Claude Desktop

Після перезапуску в інтерфейсі з'являться нові tools.

**Потрібно мати:** [uv](https://docs.astral.sh/uv/getting-started/installation/) та Python 3.12+.

---

## Watchlist

За замовчуванням у watchlist — акції MAG7 мінус Google/Amazon плюс Micron:

```python
WATCHLIST = ["MSFT", "META", "MU", "BRK.B", "NVDA"]
```

Щоб змінити список — зроби fork репозиторію, відредагуй `WATCHLIST` у `server.py` і вкажи свій репозиторій у `claude_desktop_config.json`.

---

## Example Conversations

### 1 — Market News via `get_market_news`

> **User:** Give me the latest news on crypto.

**Claude:**

Here's what's moving in crypto right now:

**Bitcoin under pressure** — BTC has dropped to the $58K range, with multiple analysts framing the $58K level as "normal" under power-law models, but options traders are actively hedging downside as uncertainty lingers. Some bears are eyeing sub-$50K as a next target if support doesn't hold. ([Cointelegraph](https://cointelegraph.com/markets/key-bitcoin-price-levels-after-btc-power-law-says-58k-is-normal))

**Coinbase Base outage** — Coinbase's Base L2 blockchain suffered a two-hour outage earlier today before resuming. No details yet on the root cause, but it's a notable reliability event for one of the more actively used L2 networks. ([CoinDesk](https://www.coindesk.com/tech/2026/06/25/coinbase-s-base-blockchain-resumes-after-two-hour-outage-disrupted-network))

**Crypto "invisible" to UK wealth advisers** — A CoinShares survey found that half of UK wealth advisers have no visibility into their clients' crypto holdings, pointing to a structural gap in portfolio oversight as adoption grows. ([Cointelegraph](https://cointelegraph.com/news/uk-wealth-advisors-clients-crypto-invisible-survey))

The dominant theme is BTC sentiment — the market's watching whether $58K holds or if there's more downside ahead.

---

### 2 — Company Profile via `get_company_profile` + `get_stock_quote`

> **User:** Give me a short company profile on SOFI.

**Claude:**

**SoFi Technologies (SOFI)** · NASDAQ · Financial Services

Trading at **$17.30** today (nearly flat, –0.06%), with a market cap of ~**$22.2B**. Notable: it's sitting **–47.1% below its 52-week high** of $32.73 — well past the 20% flag threshold.

**What they do:** SoFi is a digital-first financial services company targeting "HENRYs" (high earners, not rich yet) — young professionals refinancing student loans or looking for a one-stop-shop bank. Their product stack covers personal loans, student loan refinancing, home loans, a cash management account, investing, and credit cards. They secured a full bank charter in early 2022, a significant milestone that lets them hold deposits and fund loans directly.

**The infrastructure play:** SoFi also owns Galileo (acquired 2020) and Technisys (acquired 2022) — B2B fintech infrastructure businesses that power card issuing and banking platforms for other fintechs. This gives them a revenue stream beyond consumer finance and makes them something of a picks-and-shovels play on fintech broadly.

**Things to watch:** Growth has been strong but profitability has been a moving target. The student loan environment (government policy on repayments) has historically been a headwind or tailwind depending on the cycle. At –47% from peak, it's deeply discounted — but worth a closer look at net interest margin and loan quality trends before forming a view.

---

### 3 — Watchlist Snapshot via `watchlist-snapshot` prompt

> **User:** *(selected the `watchlist-snapshot` prompt and `watchlist://my-tickers` resource from the Claude chat UI)*

**Claude:**

Got the tools. Now let me pull quotes with 52-week data for all 5 tickers simultaneously... All quotes in. Now let me grab the MSFT profile — it's the one furthest off its peak... Here's the full picture. A few key takeaways:

**Potential buys (>20% below 52-week peak):**

MSFT is the standout at **–36.5%** off its high of $555.45 — the largest drawdown in the watchlist by a meaningful margin. That's a significant pullback for a company of its quality and suggests the market has repriced it substantially, though a drop of that magnitude warrants understanding the catalyst (macro rates, valuation compression, Azure growth deceleration) before treating it as a simple entry.

META is also flagged at **–31.8%** off $796.25, down another 2.65% today. Still generating massive FCF and expanding its AI/advertising stack, so this is worth watching closely.

**Not triggered:**

NVDA is just under the threshold at –17.2%, trading at $195.74 vs. its $236.54 peak. Close, but not quite there by the 20% rule.

MU is on an absolute tear — up 15.7% today alone and sitting right at its 52-week high of $1,213.56.

**BRK.B caveat:** Finnhub's 52-week data for BRK.B came back clearly wrong (returning BRK.A Class A figures near $775K). The current price of $487.81 looks plausible for BRK.B, but I excluded it from the peak-distance analysis entirely rather than surface bad numbers. Worth checking a second source on that one.

*Not financial advice.*

---

## Обмеження

- **Rate limit:** Finnhub free tier — 60 запитів/хв. Watchlist snapshot робить 1–2 запити на тікер.
- **Market hours:** поза торговою сесією повертається ціна закриття без позначки "ринок закритий".
- **Watchlist статичний:** зміни потребують fork і редагування `server.py`.
- **US-centric:** free tier має обмежені дані для не-американських бірж.
- **52-week дані:** для ETF та маловідомих символів поле може повернути `0`.
