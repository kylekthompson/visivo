from visivo.models.dashboard import Dashboard
from ..factories.model_factories import DashboardFactory

from pydantic import ValidationError


def test_Dashboard_simple_data():
    data = {"name": "development"}
    dashboard = Dashboard(**data)
    assert dashboard.name == "development"


def test_Dashboard_missing_data():
    try:
        Dashboard()
    except ValidationError as e:
        error = e.errors()[0]
        assert error["msg"] == "field required"
        assert error["type"] == "value_error.missing"


def test_Dashboard_find_trace():
    dashboard = Dashboard()
    assert dashboard.find_trace(name="trace") == None

    dashboard = DashboardFactory()
    trace = dashboard.rows[0].items[0].chart.traces[0]
    assert dashboard.find_trace(name=trace.name) == trace

    dashboard = DashboardFactory(table_item=True)
    trace = dashboard.rows[0].items[0].table.trace
    assert dashboard.find_trace(name=trace.name) == trace


def test_Dashboard_all_tables():
    dashboard = DashboardFactory(table_item=True)
    table = dashboard.rows[0].items[0].table
    assert dashboard.all_tables == [table]


def test_Dashboard_all_charts():
    dashboard = DashboardFactory()
    chart = dashboard.rows[0].items[0].chart
    assert dashboard.all_charts == [chart]