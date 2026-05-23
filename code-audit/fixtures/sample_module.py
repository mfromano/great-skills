"""Sample module with a known call graph for testing audit_call_graph.py.

Expected call graph:
    main -> process_data -> validate_input
    main -> format_output
    DataProcessor.__init__ (entry point)
    DataProcessor.run -> DataProcessor._transform -> DataProcessor._validate
    DataProcessor.run -> DataProcessor._format
    helper (entry point, calls nothing)
    recursive_func -> recursive_func (cycle)

Expected entry points:
    main, DataProcessor.__init__, DataProcessor.run, helper, recursive_func

Expected complexity:
    main: 1 (no branches)
    process_data: 3 (if + for)
    validate_input: 2 (if)
    format_output: 1
    DataProcessor.__init__: 1
    DataProcessor.run: 2 (if)
    DataProcessor._transform: 3 (for + if)
    DataProcessor._validate: 2 (if)
    DataProcessor._format: 1
    helper: 1
    recursive_func: 2 (if)
"""


def main():
    data = process_data([1, 2, 3])
    return format_output(data)


def process_data(items):
    if not items:
        return []
    results = []
    for item in items:
        results.append(validate_input(item))
    return results


def validate_input(value):
    if value < 0:
        raise ValueError("negative")
    return value


def format_output(data):
    return str(data)


class DataProcessor:
    def __init__(self, config):
        self.config = config

    def run(self, data):
        if not data:
            return None
        transformed = self._transform(data)
        return self._format(transformed)

    def _transform(self, data):
        results = []
        for item in data:
            if self._validate(item):
                results.append(item * 2)
        return results

    def _validate(self, item):
        if item is None:
            return False
        return True

    def _format(self, data):
        return {"result": data}


def helper():
    return 42


def recursive_func(n):
    if n <= 0:
        return 1
    return n * recursive_func(n - 1)
