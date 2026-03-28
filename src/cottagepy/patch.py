from dataclasses import dataclass
from difflib import unified_diff
import re
from typing import Protocol, Self


def str2lines(s: str) -> list[str]:
    return s.splitlines(keepends=True)


@dataclass
class Editor:
    lines: list[str]
    index: int

    @classmethod
    def from_text(cls, text: str) -> Self:
        text_editor = cls(lines=text.splitlines(keepends=True), index=0)
        assert all(line.endswith("\n") for line in text_editor.lines)
        return text_editor

    def __str__(self) -> str:
        assert all(line.endswith("\n") for line in self.lines)
        return "".join(self.lines)

    def __len__(self) -> int:
        return len(self.lines)

    def at_end(self) -> bool:
        return self.index == len(self.lines)

    def num_line(self) -> int:
        return self.index + 1

    def go_to(self, num_line: int) -> None:
        index = max(0, num_line - 1)
        if index > len(self.lines):
            raise ValueError("Cannot set index past length of line array")
        self.index = index

    def advance(self) -> None:
        self.go_to(self.num_line() + 1)

    def _raise_if_at_end(self) -> None:
        if self.at_end():
            raise ValueError("Index is pointing past the lines of the text")

    def current(self) -> str:
        self._raise_if_at_end()
        return self.lines[self.index]

    def delete_line(self) -> None:
        self._raise_if_at_end()
        del self.lines[self.index]

    def insert_line(self, line: str) -> None:
        if not line.endswith("\n"):
            line += "\n"
        self.lines.insert(self.index, line)
        self.index += 1


def diff(left: str, right: str) -> str:
    return str(Editor(lines=list(unified_diff(str2lines(left), str2lines(right))), index=0))


class Error(Exception):
    pass


class HeaderError(Error):
    def __init__(self, line: str) -> None:
        super().__init__(f"Ill-formatted hunk header: {line}")
        self.line = line


@dataclass
class Subset:
    start: int
    length: int


@dataclass
class Header:
    RX = re.compile(
        r"@@ -(?P<start_left>[0-9]+)(,(?P<length_left>[0-9]+))? \+(?P<start_right>[0-9]+)(,(?P<length_right>[0-9]+))? @@"
    )
    left: Subset
    right: Subset

    @classmethod
    def parse(cls, line: str) -> Self:
        if m := cls.RX.match(line):
            return cls(
                left=Subset(
                    start=int(m.group("start_left")), length=int(m.group("length_left") or 0)
                ),
                right=Subset(
                    start=int(m.group("start_right")), length=int(m.group("length_right") or 0)
                ),
            )
        raise HeaderError(line)


class HunkError(Error):
    def __init__(self, op: str, num_hunk: int, line_expected: int, line_actual: int) -> None:
        super().__init__(
            f"After {op}ing hunk {num_hunk} of the patch, the result does not end at the same line in the text: expected {line_expected}, result is at {line_actual}"
        )
        self.op = op
        self.num_hunk = num_hunk
        self.line_expected = line_expected
        self.line_actual = line_actual


class _Operation(Protocol):
    def name(self) -> str: ...

    def handle_plus(self, editor: Editor, line: str) -> None: ...

    def handle_minus(self, editor: Editor, line: str) -> None: ...

    def select_subset(self, header: Header) -> Subset: ...


def operate(text: str, patch: str, operation: _Operation) -> str:
    lines_patch = Editor.from_text(patch).lines
    for i, (prefix_expected, line) in enumerate(zip(["---", "+++"], lines_patch)):
        if not line.startswith(prefix_expected):
            raise ParseError(i + 1, line, prefix_expected)
    editor = Editor.from_text(text)

    try:
        num_hunk = 0
        subset_current: Subset | None = None
        for line in lines_patch[2:]:
            match line[0]:
                case "@":
                    if subset_current is not None:
                        line_expected = subset_current.start + subset_current.length
                        if editor.num_line() != line_expected:
                            raise HunkError(
                                operation.name(), num_hunk, line_expected, editor.num_line()
                            )
                    subset_current = operation.select_subset(Header.parse(line))
                    num_hunk += 1
                    editor.go_to(subset_current.start)
                case " ":
                    if editor.current() != line[1:]:
                        raise ContextError(editor.num_line(), editor.current(), line[1:])
                    editor.advance()
                case "-":
                    operation.handle_minus(editor, line[1:])
                case "+":
                    operation.handle_plus(editor, line[1:])
                case _:
                    raise RuntimeError(f"Illegal line in hunk {num_hunk}: {line}")

    except StopIteration:
        pass

    return str(editor)


class ParseError(Error):
    def __init__(self, num: int, line: str, prefix: str) -> None:
        super().__init__(
            f"Expected patch line {num} to start with {prefix}, but it rather goes: {line}"
        )
        self.num_line = num
        self.line = line
        self.prefix = prefix


class ContextError(Error):
    def __init__(self, num: int, line: str, expected: str) -> None:
        super().__init__(
            f"Expected text line {num} to match [{expected}], but instead it goes: {line}"
        )
        self.num = num
        self.line = line
        self.expected = expected


def apply(text: str, patch: str) -> str:
    class Apply:
        def name(self) -> str:
            return "apply"

        def handle_plus(self, editor: Editor, line: str) -> None:
            editor.insert_line(line)

        def handle_minus(self, editor: Editor, line: str) -> None:
            editor.delete_line()

        def select_subset(self, header: Header) -> Subset:
            return header.left

    return operate(text, patch, Apply())


def revert(text: str, patch: str) -> str:
    class Revert:
        def name(self) -> str:
            return "revert"

        def handle_plus(self, editor: Editor, line: str) -> None:
            editor.delete_line()

        def handle_minus(self, editor: Editor, line: str) -> None:
            editor.insert_line(line)

        def select_subset(self, header: Header) -> Subset:
            return header.right

    return operate(text, patch, Revert())
