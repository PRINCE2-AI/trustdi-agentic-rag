from app.config import Settings
from app.engine import TrustDIEngine
from app.profiler import SchemaProfiler
from app.schemas import Decision


def test_agentic_matcher_maps_sample_schema() -> None:
    profiler = SchemaProfiler()
    source = profiler.profile_rows(
        "crm",
        ["customer_email", "order_total", "order_date"],
        [
            {"customer_email": "a@example.com", "order_total": "12.50", "order_date": "2026-07-01"},
            {"customer_email": "b@example.com", "order_total": "20.00", "order_date": "2026-07-02"},
        ],
    )
    target = profiler.profile_rows(
        "warehouse",
        ["client_email", "sales_amount", "purchase_date"],
        [
            {"client_email": "a@example.com", "sales_amount": "12.50", "purchase_date": "2026-07-01"},
            {"client_email": "b@example.com", "sales_amount": "20.00", "purchase_date": "2026-07-02"},
        ],
    )
    result = TrustDIEngine(Settings()).match_profiles(
        source,
        target,
        gold={
            "customer_email": "client_email",
            "order_total": "sales_amount",
            "order_date": "purchase_date",
        },
    )
    predicted = {match.source_column: match.target_column for match in result.matches}
    assert predicted["customer_email"] == "client_email"
    assert predicted["order_total"] == "sales_amount"
    assert result.metrics["recall"] >= 0.66
    assert any(match.decision in {Decision.MATCH, Decision.POSSIBLE_MATCH} for match in result.matches)

