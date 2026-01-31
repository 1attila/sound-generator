from typing import Dict, List, Set
from dataclasses import dataclass, field
from pathlib import Path
import argparse
import keyword
import re


DEFAULT_MC_VERSION = "1.21.10"
DEFAULT_JAVA_FILE = "SoundEvents.java"
DEFAULT_OUTPUT_PATH = "sounds"
FILE_HEAD = """\
# =============================
# Created by 1attla's generator
# ============================="""
REGISTER_RE = re.compile(
    r'register(?:ForHolder)?\(\s*"([^"]+)"\s*\)'
)


@dataclass
class Node:
    children: Dict[str, "Node"] = field(default_factory=dict)
    sounds: Set[str] = field(default_factory=set)


def patch_name(name: str) -> str:

    if keyword.iskeyword(name):
        name += "_"

    if name[0].isdigit():
        name = "_" + name

    return name


def parse_java_sounds(java_file: Path) -> List[str]:

    sounds: List[str] = []

    with java_file.open(encoding="utf-8") as f:
        for line in f:
            match = REGISTER_RE.search(line)
            if match and match.group(1) != "intentionally_empty":
                sounds.append(match.group(1))

    return sounds


def build_tree(sound_ids: List[str]) -> Node:

    root = Node()

    for sound in sound_ids:

        parts = sound.split(".")
        node = root

        for part in parts[:-1]:
            node = node.children.setdefault(part, Node())

        node.sounds.add(parts[-1])

    return root


def add_goat_horn_sounds(root: Node) -> None:

    node = (
        root.children
            .setdefault("item", Node())
            .children
            .setdefault("goat_horn", Node())
            .children
            .setdefault("sound", Node())
    )

    node.sounds.update(str(i) for i in range(8))


def add_wolf_sounds(root: Node) -> None:

    wolf = (
        root.children
            .setdefault("entity", Node())
            .children
            .setdefault("wolf", Node())
    )

    wolf.sounds.update(
        ["ambient", "death", "growl", "hurt", "pant", "whine"]
    )


def emit_node(
    lines: List[str],
    node: Node,
    path: List[str],
    indent: int = 0
) -> None:

    pad = " " * indent
    namespace = ".".join(path)


    for sound in sorted(node.sounds):

        if sound not in node.children:
            lines.append(
                f'{pad}{patch_name(sound)} = "{namespace}.{sound}"'
            )

    if node.sounds and node.children:
        lines.append("")

    for name, child in sorted(node.children.items()):

        patched = patch_name(name)
        conflict = name in node.sounds

        if conflict:
            lines.append(
                f'{pad}class _{patched}:'
                f'\n{pad}    """'
                f'\n{pad}    NOTE: you can use this directly as:'
                f'\n{pad}    sounds.{".".join(path + [name])}'
                f'\n{pad}    """'
                f'\n\n{pad}    def __repr__(self) -> str:'
                f'\n{pad}        return "{namespace}.{name}"\n'
            )
            class_name = f"_{patched}"
        else:
            lines.append(f"{pad}class {patched}:")

            class_name = patched

        emit_node(
            lines,
            child,
            path + [name],
            indent + 4
        )

        if conflict:
            lines.append(f"\n{pad}{patched} = {class_name}()")

        lines.append("")


def generate_modules(
    root: Node,
    output_dir: Path,
    mc_version: str
) -> None:

    output_dir.mkdir(exist_ok=True)

    init_imports: List[str] = []

    for namespace, node in sorted(root.children.items()):

        init_imports.append(namespace)

        file = output_dir / f"{namespace}.py"
        lines: List[str] = [FILE_HEAD, ""]

        emit_node(lines, node, [namespace])

        while lines and not lines[-1].strip():
            lines.pop()

        file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    init_lines = (
        FILE_HEAD
        + "\n\n"
        + f'"""\n## Sound completer by 1attila\n\nLatest version supported: `{mc_version}`\n"""\n\n'
    )

    for mod in init_imports:
        init_lines += f"from . import {mod} as {mod}\n"

    init_lines += "\n\n__all__ = [\n"

    for i, mod in enumerate(init_imports):
        init_lines += f'    "{mod}"'
        init_lines += "," if i < len(init_imports) - 1 else ""
        init_lines += "\n"

    init_lines += "]"

    (output_dir / "__init__.py").write_text(init_lines, encoding="utf-8")


def generate(
    input_path: Path,
    mc_version: str,
    output_dir: Path
) -> None:

    if not input_path.exists():
        raise FileNotFoundError(input_path.name)

    sounds = parse_java_sounds(input_path)
    root = build_tree(sounds)

    add_goat_horn_sounds(root)
    add_wolf_sounds(root)

    generate_modules(root, output_dir, mc_version)

    print(f"Generated {len(sounds)} sounds")


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument("-version", "-v", help="latest version supported", default=DEFAULT_MC_VERSION)
    parser.add_argument("-input", "-i", help="SoundEvents.java path", default=DEFAULT_JAVA_FILE)
    parser.add_argument("-output", "-o", help="directory where the package should be created", default=DEFAULT_OUTPUT_PATH)

    args = parser.parse_args()
    generate(
        Path(args.input),
        args.version,
        Path(args.output)
    )


if __name__ == "__main__":
    main()