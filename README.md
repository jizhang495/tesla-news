# Tesla Dashboard

Local FastAPI app that surfaces the latest Tesla (TSLA) stock quote alongside recent community news.

## Getting Started

```bash
make install        # set up virtualenv and install dependencies
make run            # launch the dev server at http://127.0.0.1:8000
```

The homepage fetches data on each request, so leave network access enabled.

## Tooling

- `make format` runs `ruff --fix` and `black`
- `make lint` runs `ruff` and `mypy`
- `make test` runs the pytest suite with coverage
- `make check` chains format, lint, and test
