# USFM Parser Tools

A clean, modular USFM (Unified Standard Format Markers) parser following a three-stage compiler architecture: Lexer → Parser → Walker. This toolkit processes Bible text files in USFM format and supports multiple output formats including Accordance import format and simplified plain text for AI training.

## Features

- **Modular Architecture**: Separate lexer, parser, and walker components for maintainability
- **Multiple Output Formats**: Accordance format, simplified text, and extensible walker pattern
- **Robust Error Handling**: Descriptive error messages with filename and line number context
- **Unicode Support**: Full Unicode preservation with BOM handling
- **Cross-Platform**: Works on Ubuntu, WSL2, and other Unix-like environments

## Installation

No external dependencies required beyond Python 3.7+ standard library (except `click` for CLI).

```bash
# Install dependency click for CLI usage and set up to be an editable module
python3 -m venv .usfmparse
source .usfmparse/bin/activate
pip install -r requirements.txt 
```

## Command-Line Usage

### Basic Usage

Convert USFM files to Accordance format:

```bash
python -m usfmtools.usfmToAccordance input.usfm > output.acc
```

### Multiple Files

Process multiple USFM files into a single output:

```bash
python -m usfmtools.usfmToAccordance book1.usfm book2.usfm book3.usfm > combined.acc
```

### Command-Line Options

```bash
# Disable paragraph markers (¶)
python -m usfmtools.usfmToAccordance --no-para input.usfm > output.acc

# Disable text-critical marks (⸂ and ⸃)
python -m usfmtools.usfmToAccordance --no-tc input.usfm > output.acc

# Enable debug output
python -m usfmtools.usfmToAccordance --debug input.usfm > output.acc

# Combine options
python -m usfmtools.usfmToAccordance --no-para --no-tc input.usfm > output.acc
```

## Programmatic Usage

### Basic Parsing

```python
from usfmtools.usfmparser import UsfmParser

# Parse a USFM file
parser = UsfmParser()
document = parser.load('input.usfm')

# Parse a USFM string
usfm_text = r"""
\id MAT
\c 1
\v 1 In the beginning...
"""
document = parser.loads(usfm_text)
```

### AccordanceWalker - Generate Accordance Format

```python
from usfmtools.usfmparser import UsfmParser
from usfmtools.usfmwalker import AccordanceWalker

# Parse and render to Accordance format
parser = UsfmParser()
document = parser.load('matthew.usfm')

walker = AccordanceWalker(para=True, tc=True)
output = walker.render(document)
print(output)

# Output format:
# Matt. 1:1 In the beginning...
# Matt. 1:2 ¶ And it came to pass...
```

### SimplifyWalker - Generate Plain Text

```python
from usfmtools.usfmparser import UsfmParser
from usfmtools.usfmwalker import SimplifyWalker

# Parse and render to simplified text (no verse references)
parser = UsfmParser()
document = parser.load('matthew.usfm')

walker = SimplifyWalker()
output = walker.render(document)
print(output)

# Output format:
# In the beginning... And it came to pass...
```

### ParagraphExtractWalker - Extract Paragraph Locations

```python
from usfmtools.usfmparser import UsfmParser
from usfmtools.usfmwalker import ParagraphExtractWalker

# Extract paragraph marker locations
parser = UsfmParser()
document = parser.load('matthew.usfm')

walker = ParagraphExtractWalker()
paragraph_map = walker.extract(document)

# paragraph_map is a dict: {"MAT 1:2": True, "MAT 2:1": True, ...}
for verse_ref in paragraph_map:
    print(f"Paragraph at {verse_ref}")
```

### ParagraphApplyWalker - Insert Paragraph Markers

```python
from usfmtools.usfmparser import UsfmParser
from usfmtools.usfmwalker import ParagraphApplyWalker, AccordanceWalker

# Apply paragraph markers from a map
parser = UsfmParser()
document = parser.load('matthew.usfm')

paragraph_map = {
    "MAT 1:2": True,
    "MAT 2:1": True,
}

walker = ParagraphApplyWalker(paragraph_map)
modified_document = walker.apply(document)

# Render with paragraph markers
output_walker = AccordanceWalker(para=True)
output = output_walker.render(modified_document)
```

### Lexer - Direct Tokenization

```python
from usfmtools.usfmlexer import tokenize

# Tokenize USFM text
usfm_text = r"\id MAT\c 1\v 1 In the beginning"
tokens = tokenize(usfm_text, filename='matthew.usfm')

for token in tokens:
    print(f"{token.type}: {token.value} (line {token.line})")

# Output:
# MARKER: id (line 1)
# TEXT: MAT (line 1)
# MARKER: c (line 1)
# TEXT: 1 (line 1)
# MARKER: v (line 1)
# TEXT: 1 (line 1)
# TEXT: In (line 1)
# TEXT: the (line 1)
# TEXT: beginning (line 1)
```

### Custom Walker - Create Your Own Output Format

```python
from usfmtools.usfmwalker import UsfmWalker
from usfmtools.usfmparser import UsfmParser

class MyCustomWalker(UsfmWalker):
    """Custom walker for your specific output format"""
    
    def __init__(self):
        self.verse_count = 0
    
    def visit_verse(self, node):
        self.verse_count += 1
        content = ''.join(self.render(child) for child in node.children)
        return f"[Verse {self.verse_count}] {content}\n"
    
    def visit_text(self, node):
        return node.value + " "

# Use your custom walker
parser = UsfmParser()
document = parser.load('matthew.usfm')

walker = MyCustomWalker()
output = walker.render(document)
print(output)
```

## Error Handling

The parser provides descriptive error messages with context:

```python
from usfmtools.usfmparser import UsfmParser

parser = UsfmParser()

try:
    document = parser.load('invalid.usfm')
except Exception as e:
    print(f"Parse error: {e}")
    # Output: Parse error: Missing verse number in invalid.usfm:15
```

Unknown markers generate warnings but don't stop processing:

```python
# USFM with unknown marker \xyz
# Output to stderr: Warning: Unknown marker '\xyz' at line 10
# Processing continues, content is preserved
```

## Architecture

The toolkit follows a three-stage compiler design:

1. **Lexer** (`usfmlexer.py`): Tokenizes raw USFM text into a stream of tokens
2. **Parser** (`usfmparser.py`): Converts tokens into an Abstract Syntax Tree (AST)
3. **Walker** (`usfmwalker.py`): Traverses the AST to generate output in various formats

This separation of concerns makes the code maintainable and extensible.

## Supported USFM Markers

- **Identification**: `\id`, `\rem`, `\h`, `\toc1`, `\toc2`, `\toc3`
- **Titles**: `\mt`, `\mt1`, `\mt2`, `\mt3`, `\ms`, `\imt1`, `\imt2`
- **Introductions**: `\is`, `\ip`, `\ipr`, `\imq`, `\iot`, `\io1`, `\io2`, `\io3`, `\ior`, `\ie`, `\ili`
- **Headings**: `\s`, `\s1`, `\s2`, `\s3`, `\r`, `\mr`, `\d`, `\qa`
- **Chapter/Verse**: `\c`, `\v`
- **Paragraphs**: `\p`, `\m`, `\mi`, `\nb`, `\b`, `\pi`, `\pi2`, `\pmo`
- **Poetry**: `\q`, `\q1`, `\q2`, `\q3`, `\q4`, `\qc`, `\qs`
- **Lists**: `\li`, `\li1`, `\li2`
- **Footnotes**: `\f`, `\fr`, `\fk`, `\ft`, `\fw`, `\fp`, `\f*`
- **Cross-references**: `\x`, `\xo`, `\xt`, `\x*`
- **Character styles**: `\w`, `\nd`, `\add`, `\qt`, `\tl`, `\rq`, `\k` (with end markers)
- **Tables**: `\tr`, `\th1`, `\th2`, `\th3`, `\tc1`, `\tc2`, `\tc3`
- **Special**: `\periph`, `\+w`

## Testing

Run the test suite with pytest:

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_lexer.py
pytest tests/test_parser.py
pytest tests/test_walker.py

# Run with verbose output
pytest -v

# Run integration tests
pytest tests/test_integration_suite.py
```

## Examples

See the `examples/` directory for complete working examples:

- `example_simplify.py`: Using SimplifyWalker for plain text output
- `example_paragraphs.py`: Extracting and applying paragraph markers

## Requirements

- Python 3.7+ (for dataclasses)
- `click` library (for CLI only, optional for programmatic usage)

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting pull requests.

## Documentation

For detailed design documentation, see `.kiro/specs/usfm-parser-refactor/design.md`.

## Guidance for bug fixes for Antigravity
### Bug 1
In the usfmparser.py, there is a bug exposed in test_integration_suite.py::test_test16_paragraph_in_verse. What is happening is that the paragraph marker \p is not handled correctly when it is inside a verse (\v marker). Instead, the paragraph marker is "postponed" and printed at the beginning of the next verse, which is an error. 

A possible solution si that the verse container should be able to hold  paragraph markers in addition to all the other content that it can hold. Also, if a paragraph marker is between two verses (right before a \v marker) then the chapter container should be able to hold it as well. Can you suggest a fix for this problem while keeping all the other tests working?

One clue that might help solve this problem is that there is a lookahead hack around usfmparser.py:341. I am thinking that this should not be necessary.

### Bug 2
In the usfmwalker, there are two more little bugs in usfmToAccordanceTests/test17.usfm and usfmToAccordanceTests/test18.usfm which result in extra spaces either after an opening double quotation mark or before a closing parenthesis. These two failing tests are also integrated into test_integration_suite.py. Can you find the cause of this and fix it while keeping all the other tests working?

### Bug 3
In the usfmwalker, there are three more spacing bugs exposed by usfmToAccordanceTests/test19.usfm, usfmToAccordanceTests/test20.usfm, and usfmToAccordanceTests/test21.usfm which result in extra spaces in the output. These bugs are related to the presence of inline \add markers in the usfm inputs. The failing tests are integrated into the pytest tests in tests/test_integration_suite.py. Can you find the cause of this and suggestion a fix while keeping all the other tests working?

Antigravity = Claude Opus 4.6 fixed this bug after a lot of thinking. 

### Bug 4
The fourth bug in usfmToAccordanceTests/test22.usfm is a shortcoming in error reporting. test21.usfm is missing a chapter number, which is required. But the output is empty. Instead, it should indicate the error about the missing chapter number to alert the user to fix the input.

Although test22.acc lists the correct output as text, I really want the error message raised as an exception and reported to the user.

I fixed this myself when I ran out of credits on the models in Antigravity (!). In parse_book, there were two places where the parser simply dropped text. That is not permitted. So I added:

raise RuntimeError(f"Unexpected marker at book level (missing chapter?): {token.value} on line {token.line}")
and
raise RuntimeError(f"Invalid text or endmarker token at book level: {token.value} on line {token.line}")

### Bug 5
The parser does not handle A0 front matter or other USFM files whose names usually begin with an A or a B (like A0FRT or B0TDX). Although I do not want the contents of those files printed by the AccordanceWalker, the contents do need to be parsed and stored in the AST so that they can be used by other walkers in the future. These files should not cause a parse error because they are valid USFM. See usfmToAccordanceTests/test23.usfm and the expected result file test23.acc for what I am after.

### Bug 6
In usfmToAccordanceTests/test24.usfm, there is another spacing bug in the output. usfmToAccrdanceTests/test24.acc has the correct output. This time the bug is a single quotation mark that is followed by an \add marker. In the output, it is rendered with a space after it, but there should be no space. We have seen this bug before, but I think it was a double quotation mark.

### Bug 7 
usfmToAccordanceTests/test25.usfm demonstrates the need for a new commnad-line parameter --separate-quotes. When this is true, usfmToAccrdanceTests/test25.acc has the correct output. Namely, when there are two or more closing quotation marks in a row, there should be a space between them, like this: " ', or " ' ", not " '" which lacks the space between the final two marks.

--separate-quotes should default to False and in that case the output should be "'". When --separate-quotes is set True by the user issuing the command-line flag, then the output should be " ' ".

The initial fix for test25 does not work quite right. I have added usfmToAccordanceTests/test26.usfm which is the same as test25 except that --separate-quotes is false. When false, all the closing quotes should print without any spaces. With --separate-quotes=true, there should be spaces between the two closing quotes. The tests currently compare the output to the expected results in the .acc files. So when you run pytest, you will see the failures for the two tests.

### Bug 8
usfmToAccordanceTests/test27.usfm contains tables, which are valid in USFM but not currently handled by the USFM parser. I would like to fix this and add support for tables. tests/test_integration_suite.py demonstrates this bug.  The correct output from the AccordanceWalker is empty, but there should be no errors and the AST should be correctly populated with teh table. test27.acc has the correct output. I started the implementation with a call to _parse_table but please suggest if this is the right high-level approach and then if it is, implement _parse_table so that it returns a UsfmTable node and add the appropriate AST node definitions.

After you implemented this change, table support is partially working. It is unclear to me why test27.usfm complains about unknown markers th4, tc4, and tc5. They are listed in TABLE_MARKERS  in usfmparser.py.

### Bug 9
In usfmToAccordanceTests/test28.usfm, the parser complains about the \s1 marker at book level, but it is actually correct according to the USFM language specification. Similarly, test29.usfm demonstrates a paring error at the \xt marker. This too should be allowed. In both cases, the parser should parse these and include them in the AST for future walkers to access; but for the AccordanceWalker, there will be no output since these tests occur in books that begin with an A or a B, like A7 or B0. These are not Bible books, but front and backmatter books that are somewhat special cases. The parser should not complain about \s1 and \xt markers in this context. Try running `pytest tests/test_integration_suite.py` to see what happens.

### Bug 10
Various markers are not processed correctly by the code. For example: \im, \+xt, \+xt*. There is also a custom marker \zhash and \zhash* used in one input data set that we must handle also. Regarding the markers that start with a + sign in front of the marker, that means that the marker is nested within another marker. These are so-called "inline" markers for character styles, or cross-references, etc. 
usfmToAccordanceTests/test30.usfm and the integration suite demonstrate the errors. The output once again should be error free, and the parser needs to be updated to parse these markers and include them in the AST.

### Bug 11
test31.usfm and test32.usfm show examples of more markers that we need to support. \imt1, \imi, \ib, \is1, \fdc, \fq, \fig, \fig*, \bk, \bk*, \iqt, \iqt*. All of these must be supported. Markers in a \rem line should never be consumed as markers. The \rem changes the entire line to a comment which should be consumed as plain text and all with the \rem in the AST. A \rem line may even contain a marker that is not supported, but that is fine since it is in a comment (\rem is short for \remark, a comment line).

There are many markers in test33.usfm that should be supported. I will not list them here, but you will see them when you run the test_integration_suite.py with test31, test32, and test33.

### Bug 12
More markers need to be supported: \imt3, \imt4, \fe, \fe*. See test34 and test35 in usfmToAccordanceTests/ and test_integration_suite.py.

### Bug 13
More markers need to be supported: \ms1, \ms2, \zpa-xb, \zpa-xc, \zpa-xv and their final versions that end in *, like \zpa-xb*. See test36.usfm. In fact, all markers that start with \z are accepted by the language standard, and it would be nice to support all of them in this update to the code. They are all valid markers and should be included in the AST.

### Bug 14
Can you explain why test37.usfm fails with a message about an unexpected \rq marker? Visual inspection of the input file does not show why there must be a failure. It may be because you are expecting an ending marker \qt*, but that is not absolutely required by a loose interpretation of the language. Ideally every input file would have a \qt* to end every \qt opening marker, but that is not how people use USFM. I think the idea is that if a line ends, then the \qt is implicitly closed.

### Bug 15
Extra text on an \id line until the end of that line should not issue any warning or error message. It should not appear in the AccordanceWalker output. Treat it as a comment include as extra information in the id marker in the AST. See usfmToAccordanceTests/test38.usfm and the test integration suite.

### Bug 16
Why is it that when I run 
cd usfmToAccordanceTests ; python3 -m usfmtools.usfmToAccordance test39.usfm test40.usfm  > test39.acc 2>&1
that the AccordanceWalker outputs the string "Warning: Unknown Unknown" twice as well as several messages about "Skipping:" It only happens when I process the two files together, not separate, and I cannot figure out how to shorten the second file while still retaining the error. I need help identifying the bug and shortening test39.usfm and test40.usfm