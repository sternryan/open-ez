"""Stdlib-only client for fabric-task-request-v1.

Validates a request before it leaves the consumer repo and builds the vendored release tarball.
"""
import gzip
import hashlib
import io
import json
import pathlib
import re
import tarfile

VERSION = "1.0.0"
SCHEMA = "fabric-task-request-v1"
_SHA = re.compile(r"[0-9a-f]{64}")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_KEYS = {"schema_version", "request_id", "consumer", "source", "profile", "inputs", "parameters", "requirements",
         "limits", "outputs"}


class FabricClientError(ValueError):
    """Raised when a request fails client-side validation."""


def _check(ok: bool, message: str) -> None:
    if not ok:
        raise FabricClientError(message)


def _keys(value, keys, field: str) -> None:
    _check(isinstance(value, dict) and set(value) == set(keys), f"{field} schema is invalid")


def _sha(value, field: str) -> None:
    _check(isinstance(value, str) and _SHA.fullmatch(value) is not None, f"{field} must be a lowercase SHA-256 digest")


def _int(value, field: str, minimum: int = 0) -> None:
    _check(type(value) is int and value >= minimum, f"{field} must be an integer >= {minimum}")


def validate_request(request: dict) -> None:
    _keys(request, _KEYS, "request")
    _check(request["schema_version"] == SCHEMA, "schema_version is invalid")
    _check(isinstance(request["request_id"], str) and _UUID.fullmatch(request["request_id"]) is not None,
           "request_id must be a lowercase UUID")
    _check(isinstance(request["consumer"], str) and 0 < len(request["consumer"]) <= 64, "consumer is invalid")
    source = request["source"]
    _keys(source, {"revision", "bundle_sha256"}, "source")
    _check(isinstance(source["revision"], str) and re.fullmatch(r"[0-9a-f]{40}", source["revision"]) is not None,
           "source.revision must be a 40-hex commit")
    _sha(source["bundle_sha256"], "source.bundle_sha256")
    profile = request["profile"]
    _keys(profile, {"id", "version", "implementation_sha256"}, "profile")
    _check(profile["id"] == "cpu-test" and profile["version"] == "1", "profile is not admitted in v1.0")
    _sha(profile["implementation_sha256"], "profile.implementation_sha256")
    inputs = request["inputs"]
    _check(isinstance(inputs, list) and 1 <= len(inputs) <= 32, "inputs are invalid")
    for item in inputs:
        _keys(item, {"name", "artifact_ref", "sha256", "bytes"}, "input")
        _check(isinstance(item["name"], str) and item["name"] != "", "input.name is invalid")
        _check(isinstance(item["artifact_ref"], str) and item["artifact_ref"].startswith("approved://"),
               "input.artifact_ref is not an approved reference")
        _sha(item["sha256"], "input.sha256")
        _int(item["bytes"], "input.bytes", 1)
    parameters = request["parameters"]
    _keys(parameters, {"suite", "suite_manifest_sha256", "env_lock_sha256"}, "parameters")
    _check(isinstance(parameters["suite"], str) and parameters["suite"] != "", "parameters.suite is invalid")
    _sha(parameters["suite_manifest_sha256"], "parameters.suite_manifest_sha256")
    _sha(parameters["env_lock_sha256"], "parameters.env_lock_sha256")
    requirements = request["requirements"]
    _keys(requirements, {"capabilities", "privacy", "network", "paid_access"}, "requirements")
    capabilities = requirements["capabilities"]
    _check(isinstance(capabilities, list) and capabilities and all(isinstance(c, str) for c in capabilities),
           "requirements.capabilities is invalid")
    _check("render.gpu" not in capabilities,
           "render.gpu is not a capability; use render.metal, render.swiftshader or render.cuda")
    _check(requirements["privacy"] == "public-only" and requirements["network"] == "none"
           and requirements["paid_access"] is False, "v1 permits only public, offline, unpaid tasks")
    limits = request["limits"]
    _keys(limits, {"wall_ms", "artifact_bytes", "usd_micros", "model_tokens", "attempts"}, "limits")
    _int(limits["wall_ms"], "limits.wall_ms", 1)
    _int(limits["artifact_bytes"], "limits.artifact_bytes", 1)
    _check(limits["usd_micros"] == 0 and limits["model_tokens"] == 0 and type(limits["usd_micros"]) is int
           and type(limits["model_tokens"]) is int, "deterministic profiles require zero spend and tokens")
    _check(limits["attempts"] == 1 and type(limits["attempts"]) is int, "v1.0 permits exactly one attempt")
    outputs = request["outputs"]
    _check(isinstance(outputs, list) and 1 <= len(outputs) <= 16 and all(isinstance(o, str) for o in outputs)
           and len(set(outputs)) == len(outputs), "outputs are invalid")


_FAILURE_CODES = frozenset({
    "encoder-failed", "execution-failed", "cancelled", "validation-failed", "artifact-invalid", "runtime-unavailable",
    "lease-expired", "collection-failed", "runtime-mismatch", "network-violation", "request-conflict", "suite-collection-mismatch"})
_RESULT_KEYS = {"schema_version", "job_id", "attempt_id", "source", "profile", "status", "outputs", "execution", "failure"}
_IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
_MEDIA = re.compile(r"[a-z0-9][a-z0-9.+-]*/[a-z0-9][a-z0-9.+-]*")
_ARTIFACT = re.compile(r"approved://[A-Za-z0-9][A-Za-z0-9_-]{0,127}(?:/[A-Za-z0-9][A-Za-z0-9_-]{0,127})*")
_FLEET = (re.compile(r"(?<![\d.])\d{1,3}(\.\d{1,3}){3}(?![\d.])"), re.compile(_UUID.pattern, re.I),
          re.compile(r"(?<![a-z])(" + "|".join(("hear" + "th", "an" + "vil", "ham" + "mer", "em" + "ber", "bell" + "ows")) + r")(?![a-z])", re.I))


def _name(value, field: str) -> None:
    _check(isinstance(value, str) and _IDENT.fullmatch(value) is not None, f"{field} must be an opaque identifier")
    _check(not any(p.search(value) for p in _FLEET), f"{field} carries a fleet identifier")


def validate_result(result: dict, request: dict | None = None) -> None:
    """Validate a fabric-result-v1 projection offline. With ``request``, also check it answers that request."""
    _keys(result, _RESULT_KEYS, "result")
    _check(result["schema_version"] == "fabric-result-v1", "schema_version is invalid")
    for field in ("job_id", "attempt_id"):
        _check(isinstance(result[field], str) and _UUID.fullmatch(result[field]) is not None, f"{field} must be a lowercase UUID")
    _check(result["status"] in ("succeeded", "failed", "incomplete"), "status is invalid")
    source, profile = result["source"], result["profile"]
    _keys(source, {"revision", "bundle_sha256"}, "result.source")
    _check(isinstance(source["revision"], str) and re.fullmatch(r"[0-9a-f]{40}", source["revision"]) is not None, "revision is invalid")
    _sha(source["bundle_sha256"], "result.source.bundle_sha256")
    _check(isinstance(profile, dict) and {"id", "version", "implementation_sha256", "runtime_sha256"} <= set(profile)
           <= {"id", "version", "implementation_sha256", "runtime_sha256", "certification"}, "result.profile schema is invalid")
    _check(profile["id"] == "cpu-test" and profile["version"] == "1", "profile is not admitted in v1.0")
    _sha(profile["implementation_sha256"], "result.profile.implementation_sha256")
    _sha(profile["runtime_sha256"], "result.profile.runtime_sha256")
    _check(profile.get("certification", "attended-uncertified") in ("attended-certified", "attended-uncertified"), "certification is invalid")
    outputs = result["outputs"]
    _check(isinstance(outputs, list) and len(outputs) <= 16, "result.outputs is invalid")
    for item in outputs:
        _keys(item, {"name", "sha256", "bytes", "media_type", "artifact_ref"}, "result output")
        _name(item["name"], "result output.name")
        _sha(item["sha256"], "result output.sha256")
        _int(item["bytes"], "result output.bytes", 1)
        _check(isinstance(item["media_type"], str) and _MEDIA.fullmatch(item["media_type"]) is not None, "invalid media type")
        _check(isinstance(item["artifact_ref"], str) and _ARTIFACT.fullmatch(item["artifact_ref"]) is not None, "artifact_ref is not an approved reference")
    _check(len({o["name"] for o in outputs}) == len(outputs), "duplicate result output")
    execution = result["execution"]
    _keys(execution, {"wall_ms", "exit_status", "validation"}, "execution")
    _int(execution["wall_ms"], "execution.wall_ms")
    _check(type(execution["exit_status"]) is int, "execution.exit_status must be an integer")
    _check(isinstance(execution["validation"], list) and len(execution["validation"]) <= 32, "execution.validation is invalid")
    for check in execution["validation"]:
        _keys(check, {"name", "passed"}, "validation check")
        _check(type(check["passed"]) is bool, "validation check schema is invalid")
        _name(check["name"], "validation.name")
    failure = result["failure"]
    if failure is not None:
        _keys(failure, {"code", "detail"}, "failure")
        _check(failure["code"] in _FAILURE_CODES, "failure.code is not in the closed v1 set")
        _check(isinstance(failure["detail"], str) and 0 < len(failure["detail"]) <= 1000, "failure.detail is invalid")
    _check((result["status"] == "succeeded") == (failure is None), "status and failure disagree")
    if result["status"] == "succeeded":
        _check(outputs and execution["exit_status"] == 0 and execution["validation"]
               and all(c["passed"] for c in execution["validation"]), "successful result requires outputs and passing validation")
    if request is not None:
        validate_request(request)
        _check(source == request["source"], "result source does not match the request")
        _check(all(profile[k] == request["profile"][k] for k in ("id", "version", "implementation_sha256")), "result profile does not match the request")
        names = {o["name"] for o in outputs}
        _check(names <= set(request["outputs"]) and (result["status"] != "succeeded" or names == set(request["outputs"])), "result outputs do not match the request")
        _check(execution["wall_ms"] <= request["limits"]["wall_ms"] and sum(o["bytes"] for o in outputs) <= request["limits"]["artifact_bytes"],
               "result exceeds the request limits")


def _member(name: str, content: bytes) -> tuple[tarfile.TarInfo, io.BytesIO]:
    info = tarfile.TarInfo(name)
    info.size, info.mtime, info.uid, info.gid, info.uname, info.gname = len(content), 0, 0, 0, "", ""
    info.mode = 0o644
    return info, io.BytesIO(content)


def build_release(dest_dir) -> pathlib.Path:
    """Write the deterministic fabric-task-client-v1.0.0.tar.gz and return its path."""
    root = f"fabric-task-client-v{VERSION}"
    source = pathlib.Path(__file__).read_bytes()
    release = json.dumps({"version": VERSION, "schema": SCHEMA, "files": {
        "fabric_task_client/__init__.py": hashlib.sha256(source).hexdigest()}}, sort_keys=True, indent=1).encode()
    dest = pathlib.Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    tarball = dest / f"{root}.tar.gz"
    with tarball.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as packed, \
            tarfile.open(fileobj=packed, mode="w") as archive:
        archive.addfile(*_member(f"{root}/fabric_task_client/__init__.py", source))
        archive.addfile(*_member(f"{root}/RELEASE.json", release))
    return tarball
