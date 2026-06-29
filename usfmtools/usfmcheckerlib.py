"""
USFM Checker - Validates USFM files for marker correctness.

Checks for:
1. Paired markers opened but not explicitly closed (e.g., \\add without \\add*)
2. Unknown markers not in the USFM 3.0 specification
"""

import sys
import io
from dataclasses import dataclass
from typing import List, Tuple
from usfmtools.usfmlexer import tokenize, KNOWN_MARKERS, TOKEN_MARKER, TOKEN_MARKER_END


# All markers from the USFM 3.0 spec that require explicit closing (\marker*).
# Source: USFM 3.0 marker reference, "Open/Close pairs" group.
PAIRED_MARKERS = {
    # Footnotes and cross-reference containers
    'f', 'fe', 'x', 'ef', 'ex',
    # Alternate chapter/verse numbers
    'ca', 'va', 'vp',
    # Character styles
    'add', 'addpn', 'bk', 'dc', 'k', 'nd', 'ord', 'pn', 'png',
    'qt', 'sig', 'sls', 'tl', 'wj',
    # Formatting
    'em', 'bd', 'it', 'bdit', 'no', 'sc', 'sup',
    # Word / glossary
    'w', 'wg', 'wh', 'wa',
    # Special
    'ndx', 'fig', 'rb', 'pro',
    # Introduction
    'ior', 'iqt',
    # Poetry
    'qs', 'qac',
    # Lists
    'lik', 'litl',
    # Footnote internals
    'fdc', 'fv', 'fm',
    # Cross-reference internals
    'xot', 'xnt', 'xdc', 'xop', 'xt', 'rq',
    # Linking / other
    'jmp', 'cat', 'lit',
}

# Full legal marker set: lexer's known markers + spec markers not yet added there
ALL_LEGAL_MARKERS = KNOWN_MARKERS | {
    'ef', 'ex', 'addpn', 'dc', 'png', 'sig', 'sls', 'rb', 'pro', 'wa',
    'lik', 'litl', 'fv', 'fm', 'xot', 'xnt', 'xdc', 'xop', 'jmp', 'cat', 'lit',
}

# Structural boundaries: open paired markers must be closed before these
STRUCTURAL_BOUNDARIES = {'v', 'c', 'id'}


@dataclass
class CheckIssue:
    """A single issue found during checking."""
    filename: str
    line: int        # -1 means end of file
    issue_type: str  # 'unclosed', 'orphan_close', 'unknown_marker'
    message: str

    def __str__(self) -> str:
        loc = f"{self.filename}:{self.line}" if self.line >= 0 else f"{self.filename}:<EOF>"
        return f"{loc}: [{self.issue_type}] {self.message}"


class UsfmChecker:
    """
    Checks USFM files for marker correctness at the token level.
    """

    def __init__(self, check_unclosed: bool = True, check_unknown: bool = True):
        self.check_unclosed = check_unclosed
        self.check_unknown = check_unknown

    def check_file(self, filename: str) -> List[CheckIssue]:
        """Load and check a USFM file, returning a list of issues."""
        with open(filename, 'r', encoding='utf-8-sig') as f:
            text = f.read()
        text = text.replace('\r\n', '\n')
        return self.check_text(text, filename)

    def check_text(self, text: str, filename: str = '') -> List[CheckIssue]:
        """Check USFM text and return a list of issues."""
        # Suppress the lexer's built-in stderr warnings — checker does its own reporting
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            tokens = tokenize(text, filename)
        finally:
            sys.stderr = old_stderr

        issues: List[CheckIssue] = []
        # Stack of (marker_name, line_number) for currently open paired markers
        open_stack: List[Tuple[str, int]] = []

        def flush_open_stack(boundary: str, boundary_line: int) -> None:
            """Report any still-open paired markers before a structural boundary."""
            if self.check_unclosed:
                loc = f"line {boundary_line}" if boundary_line >= 0 else "end of file"
                for (m, l) in open_stack:
                    issues.append(CheckIssue(
                        filename=filename,
                        line=l,
                        issue_type='unclosed',
                        message=f"\\{m} not explicitly closed before \\{boundary} at {loc}"
                    ))
            open_stack.clear()

        for token in tokens:
            # Strip leading '+' to normalize nested markers (e.g., '+w' → 'w')
            raw = token.value
            norm = raw.lstrip('+')

            if token.type == TOKEN_MARKER:
                # Flush open stack at structural boundaries (verse, chapter, book)
                if norm in STRUCTURAL_BOUNDARIES:
                    flush_open_stack(norm, token.line)

                # Track open paired markers
                if self.check_unclosed and norm in PAIRED_MARKERS:
                    open_stack.append((raw, token.line))

                # Unknown marker check (skip z-prefixed custom markers)
                if self.check_unknown:
                    is_liv_variant = norm.startswith('liv') and norm[3:].isdigit()
                    if (norm not in ALL_LEGAL_MARKERS
                            and not norm.startswith('z')
                            and not is_liv_variant):
                        issues.append(CheckIssue(
                            filename=filename,
                            line=token.line,
                            issue_type='unknown_marker',
                            message=f"Unknown marker \\{raw} (not in USFM 3.0 spec)"
                        ))

            elif token.type == TOKEN_MARKER_END:
                if self.check_unclosed:
                    # Find the most recent matching open marker in the stack
                    matched_idx = None
                    for i in range(len(open_stack) - 1, -1, -1):
                        if open_stack[i][0] == raw:
                            matched_idx = i
                            break

                    if matched_idx is not None:
                        # Any markers pushed after matched_idx were never closed
                        for (m, l) in open_stack[matched_idx + 1:]:
                            issues.append(CheckIssue(
                                filename=filename,
                                line=l,
                                issue_type='unclosed',
                                message=(
                                    f"\\{m} at line {l} was not closed before "
                                    f"\\{raw}* at line {token.line}"
                                )
                            ))
                        # Remove matched marker and everything above it from stack
                        open_stack[:] = open_stack[:matched_idx]
                    elif norm in PAIRED_MARKERS:
                        # End marker with no matching open
                        issues.append(CheckIssue(
                            filename=filename,
                            line=token.line,
                            issue_type='orphan_close',
                            message=f"\\{raw}* has no matching opening \\{raw}"
                        ))

        # End of file: flush any remaining open markers
        flush_open_stack('EOF', -1)

        return issues
