from app.profiler import SchemaProfiler
from app.schemas import ColumnType


def test_profiler_infers_email_and_float() -> None:
    profiler = SchemaProfiler()
    profile = profiler.profile_rows(
        "orders",
        ["customer_email", "order_total"],
        [
            {"customer_email": "a@example.com", "order_total": "12.50"},
            {"customer_email": "b@example.com", "order_total": "19.00"},
        ],
    )
    assert profile.get_column("customer_email").inferred_type == ColumnType.EMAIL
    assert profile.get_column("order_total").inferred_type == ColumnType.FLOAT

