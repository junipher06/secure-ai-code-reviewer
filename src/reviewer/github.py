"""Fixed GitHub API endpoints, bounded reads and no PR code execution."""

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .errors import ReviewError


class NoRedirect(HTTPRedirectHandler):
    """Do not forward bearer credentials to a redirected endpoint."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ReviewError("GitHub API redirect refused; verify the repository address.")


class GitHub:
    def __init__(self, repository: str, token: str):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or not token:
            raise ReviewError("Set valid repository name and authenticated GitHub access.")
        self.token = token
        self.base = f"https://api.github.com/repos/{repository}"

    def request(
        self,
        suffix: str,
        accept: str = "application/vnd.github+json",
        data: dict[str, Any] | None = None,
        limit: int = 2000000,
    ) -> Any:
        request = Request(
            self.base + suffix,
            data=json.dumps(data).encode() if data is not None else None,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": accept,
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
            method="POST" if data is not None else "GET",
        )
        try:
            # Host is fixed; neither model output nor PR text supplies this URL.
            with build_opener(NoRedirect()).open(request, timeout=30) as response:
                raw = response.read(limit + 1)
            if len(raw) > limit:
                raise ReviewError("GitHub response exceeds configured limit.")
            if accept == "application/vnd.github.diff":
                return raw.decode("utf-8")
            return json.loads(raw)
        except (HTTPError, URLError, OSError, UnicodeError, ValueError) as exc:
            raise ReviewError(
                "GitHub API request failed; check access, limits and PR number."
            ) from exc

    def pages(self, suffix: str) -> list[dict[str, Any]]:
        result = []
        for page in range(1, 32):
            batch = self.request(f"{suffix}?per_page=100&page={page}")
            if not isinstance(batch, list):
                raise ReviewError("Unexpected GitHub list response.")
            result.extend(batch)
            if len(batch) < 100:
                return result
        raise ReviewError("GitHub pagination limit exceeded; manual review needed.")

    def pull_request(self, number: int) -> dict[str, Any]:
        return self.request(f"/pulls/{number}")

    def collect(self, number: int, expected_sha: str) -> tuple[str, list[dict], dict]:
        pr = self.pull_request(number)
        if pr["head"]["sha"] != expected_sha or pr["state"] != "open":
            raise ReviewError("PR changed or closed; rerun for the current commit.")
        files = self.pages(f"/pulls/{number}/files")
        if len(files) != pr["changed_files"]:
            raise ReviewError("Incomplete changed-file list.")
        diff = self.request(f"/pulls/{number}", accept="application/vnd.github.diff", limit=60000)
        reviews = self.pages(f"/pulls/{number}/reviews")
        return diff, files, {"pr": pr, "reviews": reviews}

    def comment(self, number: int, body: str) -> None:
        self.request(f"/issues/{number}/comments", data={"body": body})
