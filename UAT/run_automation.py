"""
Command-line wrapper for running Albert UAT automation modules.

This file is intentionally the single integration point used by the dashboard
backend. It keeps legacy module method-name differences out of the FastAPI app.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from registry import ADHOC_ACCOUNT, get_spec

JOBS_DIR = BASE_DIR / "jobs"


def _load_class(module_name: str, class_name: str):
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)


def _run_steps(instance: Any, steps: list[str]) -> None:
    teardown = getattr(instance, "tearDown", None)
    teardown_called = False
    try:
        for step in steps:
            method = getattr(instance, step)
            method()
            if step == "tearDown":
                teardown_called = True
    finally:
        if teardown and not teardown_called:
            try:
                teardown()
            except Exception:
                print("Warning: tearDown failed during cleanup", file=sys.stderr)
                traceback.print_exc()


def _run_login_dependent(spec: dict[str, Any], account: list[str]) -> None:
    LoginClass = _load_class("module_login_lang", "PRP")
    ModuleClass = _load_class(spec["module"], spec["class"])

    login_instance = LoginClass(*account)
    main_instance = None
    try:
        login_instance.setUp()
        login_success = login_instance.login()
        if not login_success:
            raise RuntimeError("Login failed")

        main_instance = ModuleClass(
            *account,
            playwright=login_instance.playwright,
            browser=login_instance.browser,
            page=login_instance.page,
        )
        _run_steps(main_instance, spec["steps"])
    finally:
        if main_instance is None:
            try:
                login_instance.tearDown()
            except Exception:
                pass


def run_domain(domain: str, account: list[str]) -> dict[str, Any]:
    spec = get_spec("domain", domain)
    ModuleClass = _load_class(spec["module"], spec["class"])
    instance = ModuleClass(*account)
    _run_steps(instance, spec["steps"])
    return {"type": "domain", "name": domain, "account": account[0], "status": "success"}


def run_module(module: str, account: list[str]) -> dict[str, Any]:
    spec = get_spec("module", module)
    if spec.get("login_dependent"):
        _run_login_dependent(spec, account)
    else:
        ModuleClass = _load_class(spec["module"], spec["class"])
        instance = ModuleClass(*account)
        _run_steps(instance, spec["steps"])
    return {"type": "module", "name": module, "account": account[0], "status": "success"}


def run_adhoc(adhoc_type: str) -> dict[str, Any]:
    spec = get_spec("adhoc", adhoc_type)
    ModuleClass = _load_class(spec["module"], spec["class"])
    instance = ModuleClass(*ADHOC_ACCOUNT)
    for attr, value in spec.get("attributes", {}).items():
        setattr(instance, attr, value)
    _run_steps(instance, spec["steps"])
    return {"type": "adhoc", "name": adhoc_type, "account": ADHOC_ACCOUNT[0], "status": "success"}


def write_result(path: str | None, result: dict[str, Any]) -> None:
    if not path:
        print(json.dumps(result, ensure_ascii=False))
        return
    Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize_account(account: Any) -> list[str] | None:
    if account is None:
        return None
    if isinstance(account, list):
        parts = account
    elif isinstance(account, str):
        parts = account.split("|")
    elif isinstance(account, dict):
        parts = [
            account.get("email"),
            account.get("password"),
            account.get("region"),
            account.get("country"),
            account.get("language"),
            account.get("account_type"),
        ]
    else:
        raise TypeError("account must be a list, pipe-delimited string, or object")

    if len(parts) != 6 or any(part in (None, "") for part in parts):
        raise ValueError("account must include email, password, region, country, language, and account_type")
    return [str(part) for part in parts]


def run_unit(kind: str, name: str, account: Any = None) -> dict[str, Any]:
    normalized_account = _normalize_account(account)
    if kind in {"domain", "module"}:
        if normalized_account is None:
            raise ValueError(f"{kind} automation requires an account")
        return run_domain(name, normalized_account) if kind == "domain" else run_module(name, normalized_account)
    if kind == "adhoc":
        return run_adhoc(name)
    raise ValueError(f"Unsupported automation kind: {kind}")


def load_job_input(path: str) -> dict[str, Any]:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError("job input must be a JSON object")
    return payload


def ensure_job_dir(job_id: str | None, job_dir: str | None) -> Path:
    if job_dir:
        path = Path(job_dir)
    else:
        path = JOBS_DIR / (job_id or "manual")
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    kind = payload.get("kind")
    name = payload.get("name")
    if not kind or not name:
        raise ValueError("job input requires kind and name")
    result = run_unit(kind, name, payload.get("account"))
    if payload.get("job_id"):
        result["job_id"] = payload["job_id"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an Albert UAT automation unit")
    parser.add_argument("--input", help="Path to a JSON job input file")
    parser.add_argument("--job-id", help="Dashboard job id for job-folder output")
    parser.add_argument("--job-dir", help="Explicit job folder path")
    parser.add_argument("--kind", choices=["domain", "module", "adhoc"])
    parser.add_argument("--name")
    parser.add_argument("--account-json", help="JSON account array: email,password,region,country,language,type")
    parser.add_argument("--result-json", help="Path where machine-readable result should be written")
    args = parser.parse_args()

    job_dir = None
    attempted_kind = args.kind
    attempted_name = args.name
    try:
        if args.input:
            payload = load_job_input(args.input)
            attempted_kind = payload.get("kind")
            attempted_name = payload.get("name")
            job_dir = ensure_job_dir(payload.get("job_id") or args.job_id, args.job_dir)
            job_input_copy = job_dir / "input.json"
            if Path(args.input).resolve() != job_input_copy.resolve():
                job_input_copy.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            result = run_from_payload(payload)
        else:
            if not args.kind or not args.name:
                raise ValueError("--kind and --name are required when --input is not provided")
            account = json.loads(args.account_json) if args.account_json else None
            payload = {
                "job_id": args.job_id,
                "kind": args.kind,
                "name": args.name,
                "account": account,
            }
            job_dir = ensure_job_dir(args.job_id, args.job_dir) if args.job_id or args.job_dir else None
            result = run_from_payload(payload)

        result_path = args.result_json or (str(job_dir / "result.json") if job_dir else None)
        if job_dir:
            result["job_dir"] = str(job_dir)
            result["pid"] = os.getpid()
        write_result(result_path, result)
        return 0
    except Exception as exc:
        result = {
            "type": attempted_kind,
            "name": attempted_name,
            "status": "error",
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        result_path = args.result_json or (str(job_dir / "result.json") if job_dir else None)
        write_result(result_path, result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
