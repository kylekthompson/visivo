import re
from typing import List, Optional, Union
from .dashboard import Dashboard
from .chart import Chart
from .trace import Trace
from .target import Target
from .table import Table
from .alert import EmailAlert, SlackAlert, ConsoleAlert
from .defaults import Defaults
from typing import List
from .base_model import BaseModel
from pydantic import root_validator, Field
from typing_extensions import Annotated

Alert = Annotated[
    Union[SlackAlert, EmailAlert, ConsoleAlert], Field(discriminator="type")
]


class Project(BaseModel):
    defaults: Optional[Defaults]
    targets: List[Target] = []
    alerts: List[Alert] = []
    dashboards: List[Dashboard] = []
    charts: List[Chart] = []
    tables: List[Table] = []
    traces: List[Trace] = []

    @property
    def trace_objs(self) -> List[Trace]:
        return list(filter(Trace.is_obj, self.__all_traces()))

    @property
    def trace_refs(self) -> List[str]:
        return list(filter(Trace.is_ref, self.__all_traces()))

    @property
    def chart_objs(self) -> List[Chart]:
        return list(filter(Chart.is_obj, self.__all_charts()))

    @property
    def chart_refs(self) -> List[str]:
        return list(filter(Chart.is_ref, self.__all_charts()))

    @property
    def table_objs(self) -> List[Chart]:
        return list(filter(Table.is_obj, self.__all_tables()))

    @property
    def table_refs(self) -> List[str]:
        return list(filter(Table.is_ref, self.__all_tables()))

    def filter_traces(self, pattern) -> List[Trace]:
        def name_match(trace):
            return re.search(pattern, trace.name)

        return list(filter(name_match, self.trace_objs))

    def find_trace(self, name: str) -> Trace:
        return next((t for t in self.trace_objs if t.name == name), None)

    def find_target(self, name: str) -> Target:
        return next((t for t in self.targets if t.name == name), None)

    def find_chart(self, name: str) -> Chart:
        return next((c for c in self.chart_objs if c.name == name), None)

    def find_table(self, name: str) -> Chart:
        return next((t for t in self.table_objs if t.name == name), None)

    def find_alert(self, name: str) -> Alert:
        return next((a for a in self.alerts if a.name == name), None)

    @root_validator
    def validate_default_names(cls, values):
        targets, alerts = (values.get("targets"), values.get("alerts"))
        target_names = [target.name for target in targets]
        alert_names = [alert.name for alert in alerts]
        defaults = values.get("defaults")
        if not defaults:
            return values

        if defaults.target_name and defaults.target_name not in target_names:
            raise ValueError(f"default target '{defaults.target_name}' does not exist")

        if defaults.alert_name and defaults.alert_name not in alert_names:
            raise ValueError(f"default alert '{defaults.alert_name}' does not exist")

        return values

    @root_validator
    def validate_trace_refs(cls, values):
        traces, dashboards, charts = (
            values.get("traces"),
            values.get("dashboards"),
            values.get("charts"),
        )
        trace_names = []
        trace_refs = []

        def append_values(obj_with_traces):
            for trace in obj_with_traces.trace_objs:
                cls.__append_name(trace, trace_names, "trace")
            for trace_ref in obj_with_traces.trace_refs:
                trace_refs.append(Trace.get_name(obj=trace_ref))

        [cls.__append_name(trace, trace_names, "trace") for trace in traces]
        [append_values(dashboard) for dashboard in dashboards]
        [append_values(chart) for chart in charts]

        for trace_ref in trace_refs:
            if trace_ref not in trace_names:
                raise ValueError(f"trace 'ref({trace_ref})' does not reference a trace")
        return values

    @root_validator
    def validate_chart_refs(cls, values):
        dashboards, charts = (
            values.get("dashboards"),
            values.get("charts"),
        )
        chart_names = []
        chart_refs = []

        [cls.__append_name(chart, chart_names, "chart") for chart in charts]

        for dashboard in dashboards:
            for chart in dashboard.chart_objs:
                cls.__append_name(chart, chart_names, "chart")
            for chart_ref in dashboard.chart_refs:
                chart_refs.append(Chart.get_name(obj=chart_ref))

        for chart_ref in chart_refs:
            if chart_ref not in chart_names:
                raise ValueError(f"chart 'ref({chart_ref})' does not reference a chart")
        return values

    @root_validator
    def validate_dashboard_names(cls, values):
        dashboard_names = []
        for dashboard in values.get("dashboards"):
            cls.__append_name(dashboard, dashboard_names, "dashboard")

        return values

    @classmethod
    def __append_name(cls, obj, names, type):
        name = BaseModel.get_name(obj=obj)
        if name in names:
            raise ValueError(f"{type} name '{name}' is not unique in the project")
        names.append(name)

    def __all_traces(self):
        traces = []
        traces += self.traces
        for table in self.tables:
            traces += [table.trace]
        for chart in self.charts:
            traces += chart.traces
        for dashboard in self.dashboards:
            traces += dashboard.all_traces
        return traces

    def __all_charts(self):
        charts = []
        charts += self.charts
        for dashboard in self.dashboards:
            charts += dashboard.all_charts
        return charts

    def __all_tables(self):
        tables = []
        tables += self.tables
        for dashboard in self.dashboards:
            tables += dashboard.all_tables
        return tables