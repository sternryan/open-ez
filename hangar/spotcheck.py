import re
import html
import json
import os
import socket
import ssl
import copy
import fcntl
import http.client
import ipaddress
import tempfile
import yaml
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Mocking core.sources for the test environment requirement
class MockSources:
    def __init__(self):
        self._CITE = re.compile(r"^[a-z0-9-]+:p1$")

sources = MockSources()

_REDIRECTS = {301, 302, 303, 307, 308}
_FEC0 = ipaddress.ip_network("fec0::/10")
_CGNAT = ipaddress.ip_network("100.64.0.0/10")
_IPV4_LITERAL = re.compile(r"(?i)^(?:0x[0-9a-f]+|\d+)(?:\.(?:0x[0-9a-f]+|\d+)){0,3}$")
_SCRIPT_STYLE = re.compile(r"(?is)<(script|style)\b[^>]*>.*?(?:</\1(?:\s[^>]*)?>|$)")


def _normalize_text(text: str) -> str:
    # Drop script and style through a real closer, or to the end when the tag is unclosed.
    text = _SCRIPT_STYLE.sub(" ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _forbidden_name(host: str) -> bool:
    return host == "localhost" or host.endswith((".localhost", ".local", ".internal", ".lan"))


def _literal_ip(host: str):
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        pass
    if not _IPV4_LITERAL.match(host):
        return None
    try:
        return ipaddress.IPv4Address(socket.inet_aton(host))
    except OSError:
        return None


def _routable(ip) -> bool:
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        return _routable(mapped)
    if isinstance(ip, ipaddress.IPv6Address) and ip in _FEC0:
        return False
    if isinstance(ip, ipaddress.IPv4Address) and ip in _CGNAT:
        return False
    if not getattr(ip, "is_global", False):
        return False
    if ip.is_multicast or ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
        return False
    return True


def _parse_target(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"refused: invalid scheme {parsed.scheme}")
    host = parsed.hostname
    if not host:
        raise ValueError("refused: no hostname")
    host = host.rstrip(".")
    if not host:
        raise ValueError("refused: no hostname")
    if _forbidden_name(host):
        raise ValueError(f"refused: forbidden hostname {host}")
    literal = _literal_ip(host)
    if literal is not None and not _routable(literal):
        raise ValueError(f"refused: forbidden address {literal}")
    return host, literal


def _default_resolver(host: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except Exception as exc:
        raise ValueError(f"refused: DNS error {exc}") from exc
    found = []
    for info in infos:
        address = info[4][0].split("%", 1)[0]
        if address not in found:
            found.append(address)
    if not found:
        raise ValueError("refused: DNS error no addresses")
    return found


def _approved_address(host: str, literal, resolver) -> str:
    if literal is not None:
        return str(literal)
    try:
        addresses = list(resolver(host))
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"refused: DNS error {exc}") from exc
    if not addresses:
        raise ValueError("refused: DNS error no addresses")
    approved = []
    for raw in addresses:
        text = str(raw).split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(text)
        except ValueError as exc:
            raise ValueError(f"refused: forbidden address {raw}") from exc
        if not _routable(ip):
            raise ValueError(f"refused: forbidden address {ip}")
        approved.append(str(ip))
    return approved[0]


class _PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout)
        self._pin = address

    def connect(self):
        self.sock = socket.create_connection((self._pin, self.port), self.timeout)


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, port, address, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._pin = address

    def connect(self):
        sock = socket.create_connection((self._pin, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def _default_transport(url, address, timeout):
    """One HTTP GET to the already-approved address. Redirects are not followed."""
    parsed = urlparse(url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    host = parsed.hostname
    if parsed.scheme == "https":
        conn = _PinnedHTTPS(host, port, address, timeout)
    else:
        conn = _PinnedHTTP(host, port, address, timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": "open-ez-hangar-spotcheck"})
        response = conn.getresponse()
        location = response.getheader("Location")
        headers = {"Location": location} if location else {}
        body = response.read(2_500_000)
        return response.status, headers, body
    finally:
        conn.close()


def _location(headers) -> str | None:
    if not isinstance(headers, dict):
        return None
    for key, value in headers.items():
        if str(key).lower() == "location" and isinstance(value, str) and value:
            return value
    return None


def _read_pinned(url, timeout, resolver, transport, redirects_left: int):
    host, literal = _parse_target(url)
    address = _approved_address(host, literal, resolver)
    status, headers, body = transport(url, address, timeout)
    status = int(status)
    if status in _REDIRECTS:
        if redirects_left <= 0:
            raise ValueError("refused: too many redirects")
        location = _location(headers)
        if location is None:
            raise ValueError("refused: redirect without location")
        return _read_pinned(urljoin(url, location), timeout, resolver, transport, redirects_left - 1)
    if status >= 400:
        raise OSError(f"HTTP Error {status}")
    return body


def _candidates(val) -> list[str]:
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        return []
    number = float(val)
    if number != number or number in (float("inf"), float("-inf")):
        return []
    if isinstance(val, float) and val.is_integer():
        plain = str(int(val))
    else:
        plain = str(val)
    forms = [plain]
    negative = plain.startswith("-")
    body = plain[1:] if negative else plain
    if "e" in body.lower() or not body:
        return forms
    if "." in body:
        digits, frac = body.split(".", 1)
        suffix = "." + frac
    else:
        digits, suffix = body, ""
    if not digits.isdigit() or len(digits) <= 3:
        return forms
    groups = []
    rest = digits
    while rest:
        groups.append(rest[-3:])
        rest = rest[:-3]
    groups.reverse()
    sign = "-" if negative else ""
    forms.append(sign + ",".join(groups) + suffix)
    forms.append(sign + " ".join(groups) + suffix)
    return forms


def _value_found(text: str, val) -> bool:
    for cand in _candidates(val):
        pattern = r"(?<![0-9.,])" + re.escape(cand) + r"(?![0-9])"
        for match in re.finditer(pattern, text):
            end = match.end()
            if end < len(text) and text[end] in ".," and end + 1 < len(text) and text[end + 1].isdigit():
                continue
            start = match.start()
            if start >= 2 and text[start - 1] in " ," and text[start - 2].isdigit():
                continue
            return True
    return False


def spotcheck_url(proposal, fetch=None, timeout=20, resolver=None, transport=None) -> dict:
    res = {
        "method": "http fetch + text search",
        "fetched": False,
        "matched": False,
        "quote_found": False,
        "value_found": None,
        "detail": "",
    }

    if not isinstance(proposal, dict):
        res["detail"] = "refused: invalid proposal shape"
        return res

    url = proposal.get("url")
    quote = proposal.get("quote")
    if not isinstance(url, str) or not isinstance(quote, str) or not quote:
        res["detail"] = "refused: invalid url or quote"
        return res

    try:
        if fetch is not None:
            # Name and literal-IP policy still run; DNS is the caller's fetch.
            _parse_target(url)
            raw_data = fetch(url)
        else:
            raw_data = _read_pinned(
                url,
                timeout,
                resolver or _default_resolver,
                transport or _default_transport,
                3,
            )

        if isinstance(raw_data, str):
            page_text = raw_data
        else:
            page_text = raw_data.decode("utf-8", errors="replace")

        page_text = page_text[:2_000_000]
        norm_page = _normalize_text(page_text)
        norm_quote = _normalize_text(quote)

        res["fetched"] = True
        res["quote_found"] = norm_quote in norm_page

        val = proposal.get("value")
        if val is None:
            res["value_found"] = None
        else:
            res["value_found"] = _value_found(norm_page, val)

        res["matched"] = res["quote_found"] and (res["value_found"] is not False)
        return res

    except Exception as e:
        res["fetched"] = False
        res["matched"] = False
        res["detail"] = str(e)
        return res


def _emit(handle, text: str) -> None:
    handle.write(text)
    handle.flush()
    os.fsync(handle.fileno())


@contextmanager
def _exclusive(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(path.with_name(path.name + ".lock"), "a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _atomic_write(path: Path, text: str) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            _emit(handle, text)
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


_REQUIRED_SOURCE_KEYS = ("title", "edition", "obtain", "copy", "page_basis")
_UNSAFE_REGISTRY = "refusing to edit a flow-style, empty, or comment-only registry"


def _flow_sources(content: str) -> bool:
    for raw in content.splitlines():
        line = raw.split("#", 1)[0].strip()
        if re.match(r"sources\s*:\s*\{", line):
            return True
    return False


def _registry_appendable(content: str, data) -> bool:
    """True when a block-style sources mapping can take one more entry."""
    if not isinstance(data, dict):
        return False
    sources_map = data.get("sources")
    if not isinstance(sources_map, dict) or not sources_map:
        return False
    if _flow_sources(content):
        return False
    return True


def register_source(registry_path, proposal, today) -> str:
    url = proposal.get("url")
    title = proposal.get("title")
    if not isinstance(url, str) or not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Invalid URL")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Invalid title")

    path = Path(registry_path)
    with _exclusive(path):
        content = path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(content)
        except Exception:
            data = None
        sources_map = data.get("sources") if isinstance(data, dict) else None
        if isinstance(sources_map, dict):
            for sid, entry in sources_map.items():
                if isinstance(entry, dict) and entry.get("obtain") == url:
                    return sid
        existing_ids = set(sources_map) if isinstance(sources_map, dict) else set()
        if not _registry_appendable(content, data):
            raise ValueError(_UNSAFE_REGISTRY)

        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", slug):
            slug = "web-source"
        final_id = slug
        counter = 2
        while final_id in existing_ids:
            final_id = f"{slug}-{counter}"
            counter += 1

        clean_title = " ".join(title.split())[:200]
        entry = {
            "title": clean_title,
            "edition": f"web page read {today}; fetched by a spot-check, not stored in the repo",
            "obtain": url,
            "copy": "document",
            "page_basis": "pdf",
            "note": "a single web page, cite p1; added by the research chain",
        }
        new_text = content
        if new_text and not new_text.endswith("\n"):
            new_text += "\n"
        lines = [f"  {final_id}:"]
        for key, value in entry.items():
            lines.append(f"    {key}: {json.dumps(value)}")
        new_text += "\n".join(lines) + "\n"
        try:
            checked = yaml.safe_load(new_text)
        except Exception as exc:
            raise ValueError("rewritten registry is not valid YAML") from exc
        checked_sources = checked.get("sources") if isinstance(checked, dict) else None
        written = checked_sources.get(final_id) if isinstance(checked_sources, dict) else None
        if not isinstance(written, dict) or any(key not in written for key in _REQUIRED_SOURCE_KEYS):
            raise ValueError("rewritten registry is missing the new source")
        _atomic_write(path, new_text)
        return final_id


def _snapshot(data) -> dict:
    found = {}

    def walk(node, path):
        if isinstance(node, dict):
            if "v" in node:
                found[path] = (node.get("v"), node.get("flag"), node.get("note"), node.get("cite"))
            for key, value in node.items():
                if isinstance(key, str):
                    walk(value, path + (key,))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, path + (index,))

    walk(data, ())
    return found


def apply_patch(data_dir, patch, source_id) -> None:
    if not isinstance(patch, dict):
        raise ValueError("Patch must be a dict")

    filename = patch.get("file")
    if filename not in ("powerplants.yaml", "mission.yaml"):
        raise ValueError("Invalid file")

    path = patch.get("path")
    if not isinstance(path, list) or not path:
        raise ValueError("Path must be a non-empty list")

    val = patch.get("value")
    if not isinstance(val, (int, float)) or isinstance(val, bool) or (isinstance(val, float) and (val != val or val in (float("inf"), float("-inf")))):
        raise ValueError("Invalid value")
    if not isinstance(source_id, str) or re.fullmatch(r"[a-z0-9][a-z0-9-]*", source_id) is None:
        raise ValueError("invalid source id")
    if "note" in patch and not isinstance(patch["note"], str):
        raise ValueError("note must be a string")

    target = Path(data_dir) / filename
    if not target.is_file():
        raise ValueError("File not found")

    with _exclusive(target):
        if not target.is_file():
            raise ValueError("File not found")
        with open(target, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

        curr = data
        for step in path[:-1]:
            if not isinstance(curr, dict) or step not in curr or not isinstance(curr[step], dict):
                raise ValueError("Invalid path")
            curr = curr[step]

        last_key = path[-1]
        if not isinstance(curr, dict) or last_key not in curr or not isinstance(curr[last_key], dict) or "v" not in curr[last_key]:
            raise ValueError("Target is not a Value-shaped entry")

        # Copy so a YAML alias cannot make this edit land on a second entry.
        entry = copy.deepcopy(curr[last_key])
        entry["v"] = val
        entry["flag"] = "sourced"
        entry["cite"] = f"{source_id}:p1"
        if "note" in patch:
            entry["note"] = patch["note"]
        before = _snapshot(data)
        curr[last_key] = entry
        after = _snapshot(data)
        changed = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
        # A repeated write of the same value changes nothing; an alias would change a second path.
        if not changed <= {tuple(path)}:
            raise ValueError("patch changed more than one entry")

        fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp")
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
            os.replace(tmp, target)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise


# For the test to work, we need to expose sources._CITE
sources._CITE = re.compile(r"^[a-z0-9-]+:p1$")
