# Local development

Run commands from the repository root. The fork's PyPI package is
`speedport-api-expanded`; its Python import remains `speedport`.

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

## Checks and releases

```sh
python -m unittest discover -s tests -v
python -m black speedport tests setup.py --check
python -m flake8 speedport tests setup.py --select=E9,F63,F7,F82
```

CI installs the package and runs compatibility tests on Python 3.8–3.14 without
router access. Pushes and pull requests to `main` run these checks automatically.

To release, update `version` in `setup.py`, push to `main`, then run **Actions →
Release Python Package → Run workflow** on `main`. Only `kplrm` can execute the
release pipeline, including reruns. After all checks pass, the workflow builds
and validates the wheel/source archive, publishes it to PyPI, then creates a
GitHub release with the same files at the tested commit. An existing `v<version>`
tag skips publishing and release creation; bump the version for a new
release. Releases are serialized to avoid duplicate runs publishing concurrently.
GitHub release creation uses GitHub's built-in token. PyPI publishing uses OIDC
Trusted Publishing, with no PyPI password or API token stored in the repository.
Build, PyPI publish, and GitHub release jobs have separate permissions.

## One-time PyPI setup

Creating an account does not grant access to the upstream `speedport-api` project.
This fork publishes as `speedport-api-expanded`.

1. In GitHub, open this repository's **Settings → Environments**, create `pypi`,
   and restrict its deployment branches to `main`.
2. In PyPI, open [your account's Publishing page](https://pypi.org/manage/account/publishing/)
   and add a pending GitHub publisher with these exact values:

   | Field | Value |
   | --- | --- |
   | PyPI project name | `speedport-api-expanded` |
   | Owner | `kplrm` |
   | Repository | `speedport-api-expanded` |
   | Workflow filename | `python-publish.yml` |
   | Environment | `pypi` |

3. Push these changes to `main`, then manually run **Release Python Package**.
   The first successful upload creates the PyPI project. Subsequent uploads use
   the same publisher. If the package already exists under your account, configure
   its publisher under **Manage project → Publishing** instead.

See [PyPI's pending publisher guide](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
The pending publisher does not reserve the package name. Published versions
cannot be replaced; bump `setup.py` for each new release. If PyPI publishing
succeeds but GitHub release creation fails, use **Re-run failed jobs** to retry
the GitHub job without uploading the package again.

## Container image

Run **Actions → Publish Container Image → Run workflow** on `main` as `kplrm`.
This independent workflow builds the root `Dockerfile` using the latest published
PyPI package version. It publishes to GitHub Container Registry, tagged with the
package version and `latest`:

```sh
docker pull ghcr.io/kplrm/speedport-api-expanded:latest
docker run --rm ghcr.io/kplrm/speedport-api-expanded:latest speedport --help
```
