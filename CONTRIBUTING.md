# Contributing

AutoBalance is a falsifiable transport-control experiment. Improvements must make the result easier to inspect, reproduce, or disprove.

Use SI units at the model boundary. Keep plant assumptions separate from policy assumptions. Every comparator must see the same disturbance and obey the stated hardware constraints. Choose parameters on training scenarios only, then freeze them before evaluation.

Write short functions with descriptive names. Add comments for physical reasoning, units, and non-obvious numerical choices. Avoid comments that merely repeat the code. Prefer direct equations to elaborate abstractions.

Before submitting:

```sh
python -m pip install -e ".[test]"
python -m pytest -q
python -m ruff check src tests experiments app
python -m ruff format --check src tests experiments app
```

For model changes, regenerate the benchmark and include its manifest. Report negative results. Never replace a held-out result with a better seed after seeing its score. Claims about real materials need primary sources and matching experimental conditions.

An issue should state the assumption being questioned, a reproducible example, and what result would change the conclusion. A proposed feature should explain which scientific uncertainty it resolves.
