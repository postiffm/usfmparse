# USFM Parser Tools — Architecture

The toolkit is a small Python compiler for USFM (Unified Standard Format Markers) following a three-stage design: **Lexer → Parser → Walker**.

## High-level pipeline

```mermaid
flowchart LR
    subgraph Input
        USFM[".usfm files / strings"]
    end

    subgraph Stage1["Stage 1: Lexer"]
        Lex["usfmlexer.py"]
        Tok["UsfmToken stream\nMARKER | MARKER_END | TEXT"]
    end

    subgraph Stage2["Stage 2: Parser"]
        Par["usfmparser.py\nUsfmParser"]
        AST["AST (UsfmNode tree)"]
    end

    subgraph Stage3["Stage 3: Walker"]
        Walk["usfmwalker.py\nUsfmWalker + subclasses"]
        Out["Output formats"]
    end

    USFM --> Lex
    Lex --> Tok
    Tok --> Par
    Par --> AST
    AST --> Walk
    Walk --> Out

    Out --> ACC["Accordance .acc"]
    Out --> TXT["Plain / simplified text"]
    Out --> PARA["Paragraph extract/apply"]
```

## Package structure and entry points

```mermaid
flowchart TB
    subgraph CLI
        CLIEntry["usfmToAccordance.py\n(click CLI)"]
    end

    subgraph Core["usfmtools/"]
        Lexer["usfmlexer.py\ntokenize(), UsfmToken"]
        Parser["usfmparser.py\nUsfmParser + AST nodes"]
        Walker["usfmwalker.py\nvisitor walkers"]
    end

    subgraph Consumers
        Examples["examples/\nexample_simplify.py\nexample_paragraphs.py"]
        Tests["tests/\ntest_lexer, test_parser,\ntest_walker, test_cli,\ntest_integration_suite"]
        Fixtures["usfmToAccordanceTests/\n*.usfm + *.acc golden files"]
    end

    CLIEntry --> Parser
    CLIEntry --> Walker
    Examples --> Parser
    Examples --> Walker
    Tests --> Lexer
    Tests --> Parser
    Tests --> Walker
    Tests --> Fixtures
    CLIEntry --> Fixtures

    Lexer --> Parser
    Parser --> Walker
```

## AST hierarchy

The parser builds a tree rooted at `Document`:

```mermaid
classDiagram
    class UsfmNode {
        <<abstract>>
    }

    UsfmNode <|-- Document
    UsfmNode <|-- Book
    UsfmNode <|-- Chapter
    UsfmNode <|-- Verse
    UsfmNode <|-- Paragraph
    UsfmNode <|-- Heading
    UsfmNode <|-- Footnote
    UsfmNode <|-- CrossRef
    UsfmNode <|-- GlossaryWord
    UsfmNode <|-- InlineSpan
    UsfmNode <|-- Text
    UsfmNode <|-- Unknown
    UsfmNode <|-- Table
    UsfmNode <|-- TableRow
    UsfmNode <|-- TableCell

    Document "1" --> "*" Book : books
    Book "1" --> "*" UsfmNode : children
    Chapter "1" --> "*" UsfmNode : children
    Verse "1" --> "*" UsfmNode : children
    Paragraph "1" --> "*" UsfmNode : children
    Table "1" --> "*" TableRow
    TableRow "1" --> "*" TableCell
```

## Walker pattern (visitor dispatch)

Walkers traverse the AST via `render()` → `visit_<nodetype>()`:

```mermaid
flowchart TB
    Base["UsfmWalker\nrender() dispatches by node class"]

    Base --> AW["AccordanceWalker\n→ Accordance import format"]
    Base --> SW["SimplifyWalker\n→ plain text for AI/training"]
    Base --> PEW["ParagraphExtractWalker\n→ extract ¶ markers"]
    Base --> PAW["ParagraphApplyWalker\n→ re-apply paragraph info"]

    AW --> CLI["CLI: usfmToAccordance"]
    SW --> Ex1["examples/example_simplify.py"]
    PEW --> Ex2["examples/example_paragraphs.py"]
    PAW --> Ex2
```

## Data flow (one conversion)

```mermaid
sequenceDiagram
    participant User
    participant CLI as usfmToAccordance
    participant Lex as tokenize()
    participant Par as UsfmParser
    participant AST as Document tree
    participant W as AccordanceWalker

    User->>CLI: .usfm file(s) + flags
    CLI->>Par: load() / loads()
    Par->>Lex: tokenize(usfm_text)
    Lex-->>Par: List[UsfmToken]
    Par-->>CLI: Document
    CLI->>W: render(document)
    W-->>CLI: formatted string
    CLI-->>User: stdout (.acc)
```

## Repo layout

| Path | Role |
|------|------|
| `usfmtools/usfmlexer.py` | Tokenization (`\markers`, text, line numbers) |
| `usfmtools/usfmparser.py` | AST + `UsfmParser` |
| `usfmtools/usfmwalker.py` | Output walkers (Accordance, simplify, paragraphs) |
| `usfmtools/usfmToAccordance.py` | CLI entry (`python -m usfmtools.usfmToAccordance`) |
| `tests/` | Unit + integration pytest |
| `usfmToAccordanceTests/` | Golden USFM ↔ `.acc` pairs |
| `examples/` | Programmatic usage demos |

## Design takeaway

Lexer, parser, and walker are separate so you can add markers or output formats without touching the other stages. The CLI is a thin layer over `UsfmParser` + `AccordanceWalker`; tests and golden files validate the full pipeline end to end.

For more detail on supported markers and usage, see [README.md](../README.md).
