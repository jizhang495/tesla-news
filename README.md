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

## Deploying to Vercel

The repository includes a `vercel.json` configuration and a serverless entrypoint at `api/index.py`
that expose the FastAPI app via Vercel's Python runtime.

1. Install the Vercel CLI (`npm install -g vercel`) and authenticate with `vercel login`.
2. From the project root, run `vercel` to create and link a project; accept the defaults for
   framework detection (choose “Other” if prompted) and keep the root directory as `.`.
3. Once the preview deploy succeeds, promote it with `vercel --prod` or enable Git integration in
   the Vercel dashboard so pushes to your main branch build automatically.

Vercel will install the dependencies from `requirements.txt`, load the FastAPI application through
`api/index.py`, and route all incoming traffic to the ASGI app defined in `src/app/main.py`.
