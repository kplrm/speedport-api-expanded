# Local development

Run commands from the repository root. This fork's changes require a local
checkout; installing the upstream PyPI package will not include them.

## Envirnonment

```sh
cp .env.example .env
chmod 600 .env
```

(Optional) Edit `.env` with your router's web interface password and host (no URL scheme).
The router uses a password only, with no username.

The CLI reads `SPEEDPORT_HOST` and `SPEEDPORT_PASSWORD` from the environment;
explicit `--host` / `--password` options take precedence. Without a password it
prompts securely. Prefer the prompt or environment over `--password`, which can
expose the password in shell history and process listings.

## Docker (Python 3.14 slim)

```sh
docker build -f docs/Dockerfile -t speedport-dev .
docker run --rm -it --env-file .env \
  --mount type=bind,src="$PWD",dst=/app speedport-dev
```

The image uses the [official Python 3.14 slim image](https://github.com/docker-library/python/tree/master/3.14/slim-trixie).
Inside the container, source changes are available immediately:

```sh
python -m speedport ip-info
```

The container must reach the router on your LAN. Use its IP address if
`speedport.ip` does not resolve. On Linux, add `--network host` to `docker run`
if bridge networking cannot reach the router. No ports need publishing.
Keep `.env` values unquoted for Docker's `--env-file` parser.

## Without Docker

```sh
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install -e . -r requirements_dev.txt
python -m speedport --host 192.168.2.1 ip-info
```

This prompts for the password. The CLI does not automatically load `.env`;
Docker loads it with `--env-file`. For local scripts, supply environment variables
through your shell or IDE's environment settings.

## Adding router functionality

1. Open your router's web interface and your browser's Network developer tools.
   Perform the action or open the relevant page; note the JSON endpoint, request
   method, fields, and referring HTML page. Captures can contain secrets.
2. Add a method in `speedport/api.py`. Reuse `self.api.get()` / `post()`;
   `speedport/connection.py` already handles encryption, sessions, and page
   tokens. Use `@need_auth` and `auth=True` for authenticated GET responses, and
   pass the page's `referer` when needed. Avoid duplicating authentication logic.
3. Expose the operation through `Speedport` in `speedport/speedport.py`.
   Follow the existing async methods/properties and context manager so sessions
   are closed. Optionally add a command in `speedport/__main__.py`.
4. Add mocked tests using sanitized responses, document the API/CLI usage, and
   run the checks below. Confirm behavior on your router and report its model
   and firmware in the pull request.

For example, IP information uses `data/IPData.json` with the referring page
`html/content/internet/con_ipdata.html`. `await router.ip_info` refreshes the
cached fields and returns the router's field names and values. It propagates
authentication and connection errors rather than returning stale data.
