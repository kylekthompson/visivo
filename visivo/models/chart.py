from typing import List, Union
from pydantic import Field
from .base_model import BaseModel, REF_REGEX
from .trace import Trace
from pydantic import constr


class Chart(BaseModel):
    """
    Charts are used to house traces and set up layout configurations (titles, axis labels, ect.).

    A chart contains 1 to many traces. This is really useful if you want to combine traces that are on different date grains, bars and lines, or even overlay big numbers over line chart to show the current value and the trend.

    The layout is where you define static labels like titles but also where you can set interactive elements like buttons and drop downs. With those interactive elements you can toggle between traces or cohorts on traces.
    ``` yaml
    chart:
      name: a-chart-name
      traces:
        - ref(a-trace-name)
      layout:
      title: 'Aggregated Fibonacci'
      yaxis:
        title: 'Widgets Sold' #Describe the data in your y axis
      xaxis:
        title: 'Week' #Describe the data in your x axis
      stack: False
    ```
    """

    traces: List[Union[constr(regex=REF_REGEX), Trace]] = Field(
        [],
        description="A list of trace either written in line in the chart called using the ref() function.",
    )
    layout: dict = Field(
        {},
        description="The layout attribute of the chart accepts any valid plotly layout configurations. You can read more about those here: [plotly layout docs](https://plotly.com/javascript/reference/layout/).",
    )

    def find_trace(self, name: str):
        return next((t for t in self.traces if t.name == name), None)

    @property
    def trace_objs(self) -> List[Trace]:
        return list(filter(Trace.is_obj, self.traces))

    @property
    def trace_refs(self) -> List[str]:
        return list(filter(Trace.is_ref, self.traces))