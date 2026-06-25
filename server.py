import os, json, sys
from dotenv import load_dotenv
import finnhub
from mcp.server.fastmcp import FastMCP
from pydantic import Field

load_dotenv()

api_key = os.environ.get("FINNHUB_API_KEY")
if not api_key:
    raise EnvironmentError("FINNHUB_API_KEY is not set. Pass it via claude_desktop_config.json env block.")

mcp = FastMCP("finnhub")
client = finnhub.Client(api_key=api_key)

WATCHLIST = ["MSFT", "META", "MU", "BRK.B", "NVDA"]


@mcp.resource("watchlist://my-tickers")
def get_watchlist() -> str:
    return json.dumps(WATCHLIST)


@mcp.tool(
    name="get_company_profile",
    description="Return company metadata for a stock ticker: name, country, exchange, industry, market cap, IPO date, and website."
)
def get_company_profile(
    symbol: str = Field(description="Stock ticker symbol, e.g. AAPL or NVDA")
) -> dict:
    try:
        data = client.company_profile2(symbol=symbol)
        if not data:
            return {"error": f"Company profile not found for {symbol}"}
        return {
            "name":                 data.get("name"),
            "ticker":               data.get("ticker"),
            "country":              data.get("country"),
            "exchange":             data.get("exchange"),
            "currency":             data.get("currency"),
            "finnhubIndustry":      data.get("finnhubIndustry"),
            "marketCapitalization": data.get("marketCapitalization"),
            "ipo":                  data.get("ipo"),
            "weburl":               data.get("weburl"),
        }
    except Exception as e:
        print(f"[get_company_profile] error: {e}", file=sys.stderr)
        return {"error": str(e)}


@mcp.tool(
    name="get_stock_quote",
    description="Return a real-time stock quote. Optionally includes 52-week high and low fetched from basic financials."
)
def get_stock_quote(
    symbol: str = Field(description="Stock ticker symbol, e.g. AAPL or TSLA"),
    include_52w: bool = Field(default=False, description="If true, adds 52-week high and low to the response")
) -> dict:
    try:
        q = client.quote(symbol)
        if not q or q.get("c", 0) == 0:
            return {"error": f"Quote not available for {symbol}"}
        result = {
            "symbol":        symbol,
            "current_price": q["c"],
            "change":        q["d"],
            "change_pct":    q["dp"],
            "high_today":    q["h"],
            "low_today":     q["l"],
        }
        if include_52w:
            fin = client.company_basic_financials(symbol, "all")
            metric = fin.get("metric", {})
            result["52w_high"] = metric.get("52WeekHigh")
            result["52w_low"]  = metric.get("52WeekLow")
        return result
    except Exception as e:
        print(f"[get_stock_quote] error: {e}", file=sys.stderr)
        return {"error": str(e)}


@mcp.tool(
    name="get_market_news",
    description="Return the latest 5 market news headlines for a given category."
)
def get_market_news(
    category: str = Field(default="general", description="News category: general, forex, merger, or crypto")
) -> list:
    try:
        articles = client.general_news(category, min_id=0)
        return [
            {
                "headline": a["headline"],
                "source":   a["source"],
                "url":      a["url"],
                "datetime": a["datetime"],
            }
            for a in articles[:5]
        ]
    except Exception as e:
        print(f"[get_market_news] error: {e}", file=sys.stderr)
        return [{"error": str(e)}]


@mcp.prompt()
def watchlist_snapshot() -> str:
    return """
Please review my stock watchlist (watchlist://my-tickers) and help me identify buying opportunities.
For each stock, I'd like to know the current price and how far it sits from its 52-week high.
If any are more than 20% below their yearly peak, flag them as potential buys —
and for the one furthest below its own 52-week high, give me a short company overview.
""".strip()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
