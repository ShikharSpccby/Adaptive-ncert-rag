import copy
from pathlib import Path

import yaml

DEFAULT_PATH = Path(__file__).parent / "config.yaml"


def deep_update(base: dict, new: dict) -> dict:
    for k, v in new.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path=None, overrides: dict | None = None) -> dict:
    with open(path or DEFAULT_PATH) as f:
        cfg = yaml.safe_load(f)
    if overrides:
        cfg = deep_update(copy.deepcopy(cfg), overrides)
    return cfg


def parse_set_args(pairs: list[str]) -> dict:
    """['chunking.strategy=sentence', 'retrieval.top_k=8'] -> nested override dict."""
    out: dict = {}
    for pair in pairs or []:
        key, _, raw = pair.partition("=")
        value = yaml.safe_load(raw)  # so '8' -> int, '{class_level: 10}' -> dict
        node = out
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = value
    return out
