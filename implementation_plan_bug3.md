# Fix Spacing Bugs After Inline `\add` Markers

The USFM specification requires a space after `\add*` closing markers (to avoid ambiguity like `\add*"`). This markup-artifact space is being preserved in the Accordance output as an unwanted content space in three specific cases.

## Root Cause Analysis

The three failing tests each expose a different aspect of the same underlying issue—the walker's `visit_text` spacing logic doesn't account for USFM inline marker boundaries:

| Test | USFM Source | Expected Output | Actual Output | Bug |
|------|-------------|-----------------|---------------|-----|
| 19 | `\add while\add* '?` | `while'?` | `while '?` | Space before ASCII `'` (closing quote) after span |
| 20 | `world— \add about\add*` | `world—about` | `world— about` | Space after em-dash `—` before span content |
| 21 | `\add Him.\add* "` | `Him."` | `Him. "` | Space before ASCII `"` (closing quote) after span |

## Proposed Changes

### [MODIFY] [usfmwalker.py](file:///home/postiffm/Dropbox/AndroidApps/usfmparse/usfmtools/usfmwalker.py)

Two targeted changes to `AccordanceWalker`:

#### Change 1: Em-dash suppresses trailing space (fixes test 20)

In `visit_text`, after rendering text that ends with `—` (U+2014 em-dash), set `suppressNextSpace = True`. This prevents a space being added before the next word, whether it's inside an inline span or not.

```python
# At the end of visit_text, add:
if text and text[-1] == '\u2014':  # em-dash
    self.suppressNextSpace = True
```

#### Change 2: Track post-inline-span context + closing punctuation heuristic (fixes tests 19 & 21)

Add an `after_inline_span` flag that `visit_inlinespan` sets to `True` after rendering. In `visit_text`, when this flag is set and the text is "closing punctuation" (standalone ASCII `"` or ASCII `'` followed by non-alpha), suppress the leading space.

The heuristic distinguishes:
- ✅ `'?` after span → closing quote+punctuation → no space (test 19)
- ✅ `"` after span → closing quote → no space (test 21)  
- ✅ `"` NOT after span → opening quote → keeps space (test 14)
- ✅ `'Whoever` → opening quote+word → keeps space (test 14)

```python
# In visit_text, add after the existing punctuation check:
if self.after_inline_span and text:
    if text[0] in ('"', "'") and (len(text) == 1 or not text[1].isalpha()):
        self.after_inline_span = False
        return text  # No leading space for closing punctuation after inline span

# In visit_inlinespan, add at end:
self.after_inline_span = True
```

#### Change 3: Apply same fixes to `SimplifyWalker`

Mirror the changes in `SimplifyWalker` for consistency.

## Verification Plan

### Automated Tests
- Run `python3 -m pytest tests/test_integration_suite.py -v` — all tests 0-22 should pass
- Specifically verify tests 19, 20, 21 now pass
- Verify tests 14, 17 still pass (the most similar existing tests with inline spans and quotes)
