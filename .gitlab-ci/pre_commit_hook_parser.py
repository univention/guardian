"""
Creates a SKIP filter for pre-commit hooks.
Outputs all hooks that don't match the specified filter.
For example, if you supply `backend`, you will get all pre-commit hooks for
`frontend` and `general`.

Usage:

    python3 pre_commit_hook_parser.py <PRE_COMMIT_FILE> <HOOK_FILTER>

Example:

    python3 pre_commit_hook_parser.py .pre-commit-config.yaml backend
"""
import argparse

import yaml  # type: ignore


def find(yaml_dict, tag):
    filtered_hooks = []
    for repo in yaml_dict["repos"]:
        tmp_hooks = repo["hooks"]
        filtered = filter(
            lambda hook: not hook["name"].startswith(tag),
            tmp_hooks,
        )
        filtered_hooks.extend([hook["id"] for hook in filtered])

    return list(set(filtered_hooks))


def filter_hooks(filepath: str, filter_str: str):
    with open(filepath, "r") as fp:
        content = yaml.safe_load(fp)
        return find(content, filter_str)


def format_output(hook_names: list) -> str:
    return ", ".join(hook_names)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("filter")

    args = parser.parse_args()
    filtered_hooks = filter_hooks(args.filepath, args.filter)
    print(format_output(filtered_hooks))
