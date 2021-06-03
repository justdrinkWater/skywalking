from skywalking.trace.context import get_context
from skywalking.trace.segment import _NewID


# 获取skywalking的全局tid
def get_global_trace_id():
    context = get_context()
    related_traces = context.segment.related_traces
    if len(related_traces) > 0 and isinstance(related_traces[0], _NewID):
        return related_traces[0].value
    return 'N/A'
