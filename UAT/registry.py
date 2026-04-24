"""
Approved UAT automation registry for dashboard-driven runs.

Keep dashboard-visible module names mapped here instead of spreading legacy
method-call knowledge across the backend.
"""

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


def get_spec(kind: str, name: str) -> dict:
    registries = {
        "domain": DOMAIN_MODULES,
        "module": REGULAR_MODULES,
        "adhoc": ADHOC_MODULES,
    }
    try:
        return registries[kind][name]
    except KeyError as exc:
        raise KeyError(f"Unsupported UAT automation: {kind} {name}") from exc
