from app.config import Settings
from app.profiler import SchemaProfiler
from app.router import AdaptiveRoutePlanner
from app.schemas import Route


def test_router_sends_ambiguous_pairs_to_agentic_verify() -> None:
    profile = SchemaProfiler().profile_rows(
        "demo",
        ["amount", "sales"],
        [{"amount": "10.0", "sales": "10.0"}],
    )
    planner = AdaptiveRoutePlanner(Settings())
    route = planner.route(profile.get_column("amount"), profile.get_column("sales"), 0.55, 0.51)
    assert route == Route.AGENTIC_VERIFY


def test_router_uses_direct_for_obvious_exact_match() -> None:
    profile = SchemaProfiler().profile_rows(
        "demo",
        ["customer_email"],
        [{"customer_email": "a@example.com"}],
    )
    column = profile.get_column("customer_email")
    planner = AdaptiveRoutePlanner(Settings())
    assert planner.route(column, column, 0.99, 0.2) == Route.DIRECT

