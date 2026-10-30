#!/usr/bin/env python3
"""One-shot external clock for GitHub news; Python 3.6+, no dependencies.

It stores only a dispatch timestamp. RSS, articles and model credentials never
leave GitHub. A separate scheduler invokes this program and it exits afterwards.
"""
import argparse
import base64
import datetime as dt
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler

REPOSITORY = "Gordoncee/morning-briefing-site"
WORKFLOW = "morning-briefing.yml"
API = "https://api.github.com/repos/" + REPOSITORY
GITHUB = "https://api.github.com"
ORIGIN = "https://gordoncee.github.io/morning-briefing-site/data/news-status.json"
PUBLIC = "https://fazhi.cc/news/"
BEIJING = dt.timezone(dt.timedelta(hours=8))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(url, token=None, payload=None):
    headers = {"User-Agent": "fazhi-news-clock/1.0", "Cache-Control": "no-cache"}
    body = None
    if token:
        if not (url.startswith(API + "/actions/") or re.fullmatch(
                r"https://api.github.com/app/installations/[0-9]+/access_tokens", url)):
            raise ValueError("credential-target-denied")
        headers.update(Authorization="Bearer " + token, Accept="application/vnd.github+json",
                       **{"X-GitHub-Api-Version": "2026-03-10"})
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    req = Request(url, data=body, headers=headers)
    # Never forward an Authorization header to a redirect destination.
    with build_opener(NoRedirect()).open(req, timeout=12) as response:
        data = response.read(1024 * 1024 + 1)
        if len(data) > 1024 * 1024:
            raise ValueError("response-too-large")
        return data.decode("utf-8")


class Metadata(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.values = {}
        self.dates = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").startswith("news-"):
            self.values[attrs["name"]] = attrs.get("content", "")
        if attrs.get("data-news-date"):
            self.dates.add(attrs["data-news-date"])


def freshness(expected, html, today):
    if expected.get("schema_version") != 1:
        return "origin-status-invalid"
    if expected.get("latest") != today:
        return "today-missing-at-origin"
    version = expected.get("archive_sha256", "")
    if not re.fullmatch(r"[a-f0-9]{64}", version):
        return "origin-version-invalid"
    page = Metadata()
    page.feed(html)
    if page.values.get("news-latest-date") != today or today not in page.dates:
        return "today-missing-on-website"
    if page.values.get("news-archive-version") != version:
        return "website-version-mismatch"
    return "current"


def active_run(runs, now):
    for row in runs.get("workflow_runs", []):
        if row.get("status") not in {"queued", "in_progress", "requested", "waiting", "pending"}:
            continue
        created = dt.datetime.strptime(row["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        age = (now - created).total_seconds()
        if created.astimezone(BEIJING).date() == now.astimezone(BEIJING).date() and 0 <= age < 3600:
            return row["id"]
    return None


def read_token(path):
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.geteuid():
            raise ValueError("token-file-must-be-owned-by-service-user-and-mode-0600")
        token = stream.read(1024).strip()
    if not token.startswith(("github_pat_", "ghs_")):
        raise ValueError("use-a-repository-scoped-fine-grained-or-app-token")
    return token


def app_installation_token(config_path, fetch=request, now=None):
    """Mint a one-hour token restricted to this repository and Actions write.

    The private App key stays in a mode-0600 file. No user login token is copied
    to the server, and no package install or resident authentication daemon is
    required. OpenSSL already present on the host signs the short-lived JWT.
    """
    config = json.loads(config_path.read_text())
    if config.get("repository") != REPOSITORY or not re.fullmatch(r"[0-9]+", str(config["installation_id"])):
        raise ValueError("app-configuration-must-target-only-news-repository")
    key = Path(config["private_key_file"])
    info = key.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.geteuid():
        raise ValueError("app-key-must-be-owned-by-service-user-and-mode-0600")
    timestamp = int((now or dt.datetime.now(dt.timezone.utc)).timestamp())
    def encode(data):
        return base64.urlsafe_b64encode(data).rstrip(b"=")
    header = encode(b'{"alg":"RS256","typ":"JWT"}')
    payload = encode(json.dumps({"iat":timestamp-60,"exp":timestamp+540,
                                 "iss":config["client_id"]}, separators=(",", ":")).encode())
    message = header + b"." + payload
    signed = subprocess.run(["/usr/bin/openssl", "dgst", "-sha256", "-sign", str(key)],
                            input=message, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            check=True, timeout=5)
    jwt = (message + b"." + encode(signed.stdout)).decode("ascii")
    data = json.loads(fetch(GITHUB + "/app/installations/" + str(config["installation_id"]) + "/access_tokens",
                            token=jwt, payload={"repositories":[REPOSITORY.split("/")[1]],
                                                "permissions":{"actions":"write"}}))
    permissions = data.get("permissions", {})
    if permissions.get("actions") != "write" or set(permissions) - {"actions", "metadata"}:
        raise ValueError("installation-token-has-unexpected-permissions")
    if not data.get("token", "").startswith("ghs_"):
        raise ValueError("invalid-installation-token")
    return data["token"]


def check(state_dir, token_file, dry_run=False, fetch=request, now=None, app_config=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    today = now.astimezone(BEIJING).date().isoformat()
    try:
        expected = json.loads(fetch(ORIGIN))
        reason = freshness(expected, fetch(PUBLIC), today)
    except (OSError, ValueError, KeyError):
        reason = "public-check-unavailable"
    result = {"date": today, "reason": reason, "dispatched": False}
    if reason == "current" or dry_run:
        return result
    # The public repository API needs no secret for this read.
    active = active_run(json.loads(fetch(API + "/actions/workflows/" + WORKFLOW + "/runs?per_page=20")), now)
    if active:
        result.update(action="wait-for-active-run", run_id=active)
        return result
    path = state_dir / "last-dispatch.json"
    if path.exists():
        previous = json.loads(path.read_text())
        if previous.get("date") == today and 0 <= now.timestamp() - previous.get("timestamp", 0) < 1200:
            result["action"] = "dispatch-cooldown"
            return result
    token = app_installation_token(app_config, fetch, now) if app_config else read_token(token_file)
    fetch(API + "/actions/workflows/" + WORKFLOW + "/dispatches", token=token,
          payload={"ref": "main", "inputs": {"date": today, "force": "false"}})
    state_dir.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"date": today, "timestamp": now.timestamp()}) + "\n")
    temporary.replace(path)
    result.update(dispatched=True, action="github-workflow-requested")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=Path("/var/lib/fazhi-news-trigger"))
    parser.add_argument("--token-file", type=Path, default=Path("/etc/fazhi-news-trigger/github-token"))
    parser.add_argument("--app-config", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = check(args.state_dir, args.token_file, args.dry_run, app_config=args.app_config)
    except HTTPError as error:
        # Never log a response body, request headers or secret contents.
        result = {"error": "github-or-public-http-error", "http_status": error.code}
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        result = {"error": type(error).__name__}
    print(json.dumps(result, ensure_ascii=False))
    return 1 if "error" in result else 0


if __name__ == "__main__":
    raise SystemExit(main())
