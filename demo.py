from __future__ import annotations

import json
from pathlib import Path

from app.engine import TrustDIEngine


ROOT = Path(__file__).parent
SOURCE = ROOT / "data" / "samples" / "crm_orders.csv"
TARGET = ROOT / "data" / "samples" / "warehouse_sales.csv"
GOLD = {
    "customer_email": "client_email",
    "order_total": "sales_amount",
    "order_date": "purchase_date",
    "region": "sales_region",
    "product_name": "item_title",
}


def main() -> None:
    engine = TrustDIEngine()
    result = engine.match_csvs(SOURCE, TARGET, gold=GOLD)
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
