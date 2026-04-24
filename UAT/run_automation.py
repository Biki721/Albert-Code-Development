"""
Command-line wrapper for running Albert UAT automation modules.

This file is intentionally the single integration point used by the dashboard
backend. It keeps legacy module method-name differences out of the FastAPI app.
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


REGULAR_MODULES = {
    "Broken_Links": {
        "module": "modulebrokenlinks_phase4",
        "class": "PRP",
        "steps": ["setUp", "test_load_home_page", "test_multiple_broken", "tearDown"],
    },
    "Translation_and_Empty_Page": {
        "module": "moduletransnempty_phase4",
        "class": "PRP",
        "login_dependent": True,
        "steps": ["setUp", "parent", "tearDown"],
    },
    "New_Tab": {
        "module": "modulenewtab_phase4",
        "class": "PRP",
        "steps": ["setUp", "test_new_tab", "tearDown"],
    },
    "T_variable": {
        "module": "moduletvar_phase4",
        "class": "PRP",
        "steps": ["test_tvar_check", "tearDown"],
    },
    "External_Links": {
        "module": "Module_externallinks_validation",
        "class": "PRP",
        "steps": ["setUp", "external_url_validation", "tearDown"],
    },
    "Translation_Spelling_and_Empty_Page": {
        "module": "module_trans_spell_empt_phase4",
        "class": "PRP",
        "login_dependent": True,
        "steps": ["setUp", "parent", "tearDown"],
    },
    "Spelling_check": {
        "module": "module_spell_check_phase4",
        "class": "PRP",
        "steps": ["setUp", "test_load_home_page", "parent", "tearDown"],
    },
    "Login": {
        "module": "module_login_lang",
        "class": "PRP",
        "steps": ["setUp", "login", "tearDown"],
    },
}

DOMAIN_MODULES = {
    "PRP": {
        "module": "modulepagetree_phase4",
        "class": "PRP",
        "steps": ["setUp", "scrapecall_writetrees", "tearDown"],
    },
}

ADHOC_MODULES = {
    "Adhoc Word Search": {
        "module": "module_adhoc_word_search",
        "class": "PRP",
        "steps": ["setUp", "parent", "tearDown"],
        "attributes": {"regen_tree": True},
    },
    "Adhoc URL Search": {
        "module": "module_adhoc_link_search",
        "class": "PRP",
        "steps": ["setUp", "parent", "tearDown"],
        "attributes": {"regen_tree": True},
    },
}

ADHOC_ACCOUNT = [
    "bot.dec-d001a@hpe.com",
    "Login2PRP!",
    "NA",
    "USA",
    "English",
    "T2",
]


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
    spec = DOMAIN_MODULES[domain]
    ModuleClass = _load_class(spec["module"], spec["class"])
    instance = ModuleClass(*account)
    _run_steps(instance, spec["steps"])
    return {"type": "domain", "name": domain, "account": account[0], "status": "success"}


def run_module(module: str, account: list[str]) -> dict[str, Any]:
    spec = REGULAR_MODULES[module]
    if spec.get("login_dependent"):
        _run_login_dependent(spec, account)
    else:
        ModuleClass = _load_class(spec["module"], spec["class"])
        instance = ModuleClass(*account)
        _run_steps(instance, spec["steps"])
    return {"type": "module", "name": module, "account": account[0], "status": "success"}


def run_adhoc(adhoc_type: str) -> dict[str, Any]:
    spec = ADHOC_MODULES[adhoc_type]
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an Albert UAT automation unit")
    parser.add_argument("--kind", choices=["domain", "module", "adhoc"], required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--account-json", help="JSON account array: email,password,region,country,language,type")
    parser.add_argument("--result-json", help="Path where machine-readable result should be written")
    args = parser.parse_args()

    try:
        account = json.loads(args.account_json) if args.account_json else None
        if args.kind in {"domain", "module"}:
            if not isinstance(account, list) or len(account) != 6:
                raise ValueError("--account-json must be a six-item JSON array")
            result = run_domain(args.name, account) if args.kind == "domain" else run_module(args.name, account)
        else:
            result = run_adhoc(args.name)
        write_result(args.result_json, result)
        return 0
    except Exception as exc:
        result = {
            "type": args.kind,
            "name": args.name,
            "status": "error",
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        write_result(args.result_json, result)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
