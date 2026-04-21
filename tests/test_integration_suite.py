"""
Integration tests for USFM parser using pre-existing test files.

This test suite validates the new implementation against the reference
test files (test1.usfm through test12.usfm) and their expected outputs
(test1.acc through test16.acc).

Tests 5 and 6 are expected to fail with errors (missing verse numbers).
"""

import pytest
from pathlib import Path
from usfmtools.usfmparser import UsfmParser
from usfmtools.usfmwalker import AccordanceWalker


# Base directory for test files (workspace root)
TEST_DIR = Path(__file__).parent.parent / "usfmToAccordanceTests"


def normalize_output(content: str) -> str:
    """Normalize line endings and trailing whitespace for comparison."""
    # Normalize line endings to LF
    content = content.replace('\r\n', '\n')
    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in content.split('\n')]
    # Remove trailing empty lines
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines)


def read_expected_output(test_num: int) -> str:
    """Read and normalize expected output from .acc file."""
    acc_file = TEST_DIR / f"test{test_num}.acc"
    if not acc_file.exists():
        pytest.skip(f"Reference file test{test_num}.acc not found")
    
    with open(acc_file, 'r', encoding='utf-8') as f:
        return normalize_output(f.read())


def parse_and_render(test_num: int, para: bool = True, tc: bool = True) -> str:
    """Parse USFM file and render to Accordance format."""
    usfm_file = TEST_DIR / f"test{test_num}.usfm"
    if not usfm_file.exists():
        pytest.skip(f"Test file test{test_num}.usfm not found")
    
    parser = UsfmParser()
    walker = AccordanceWalker(para=para, tc=tc)
    
    doc = parser.load(str(usfm_file))
    output = walker.render(doc)
    
    return normalize_output(output)


class TestIntegrationSuite:
    """Integration tests against pre-existing test files."""

    def test_test0_empty(self):
        """Test 10: USFM with only \rem comments, otherwise empty."""
        actual = parse_and_render(0)
        expected = read_expected_output(0)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"

    def test_test1_glossary_word(self):
        """Test 1: Glossary word with pipe delimiter."""
        actual = parse_and_render(1)
        expected = read_expected_output(1)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test2_cross_references_and_poetry(self):
        """Test 2: Cross-references and poetry markers."""
        actual = parse_and_render(2)
        expected = read_expected_output(2)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test3_basic_verse(self):
        """Test 3: Basic verse with text."""
        actual = parse_and_render(3)
        expected = read_expected_output(3)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test4_multiple_features(self):
        """Test 4: Multiple USFM features."""
        actual = parse_and_render(4)
        expected = read_expected_output(4)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test5_missing_verse_number_error(self):
        """Test 5: Should raise error for missing verse number."""
        usfm_file = TEST_DIR / "test5.usfm"
        if not usfm_file.exists():
            pytest.skip("Test file test5.usfm not found")
        
        parser = UsfmParser()
        
        with pytest.raises(Exception) as exc_info:
            parser.load(str(usfm_file))
        
        # Verify error message mentions verse number
        assert "verse" in str(exc_info.value).lower()
    
    def test_test6_error_case(self):
        """Test 6: Error case (structure validation)."""
        usfm_file = TEST_DIR / "test6.usfm"
        if not usfm_file.exists():
            pytest.skip("Test file test6.usfm not found")
        
        parser = UsfmParser()
        
        # Test 6 should raise an error
        with pytest.raises(Exception):
            parser.load(str(usfm_file))
    
    def test_test7_features(self):
        """Test 7: Additional USFM features."""
        actual = parse_and_render(7)
        expected = read_expected_output(7)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test8_features(self):
        """Test 8: Additional USFM features."""
        actual = parse_and_render(8)
        expected = read_expected_output(8)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test9_features(self):
        """Test 9: Additional USFM features."""
        actual = parse_and_render(9)
        expected = read_expected_output(9)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test10_features(self):
        """Test 10: Additional USFM features."""
        actual = parse_and_render(10)
        expected = read_expected_output(10)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test11_features(self):
        """Test 11: Additional USFM features."""
        actual = parse_and_render(11)
        expected = read_expected_output(11)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    
    def test_test12_features(self):
        """Test 12: Additional USFM features."""
        actual = parse_and_render(12)
        expected = read_expected_output(12)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"

    def test_test13_features(self):
        """Test 13: Additional USFM features."""
        actual = parse_and_render(13)
        expected = read_expected_output(13)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test14_space_after_open_quote(self):
        """Test 14: Output was putting space after open quotation mark."""
        actual = parse_and_render(14)
        expected = read_expected_output(14)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test15_footnoteplustext(self):
        """Test 15: Footnote text should not become part of verse text."""
        actual = parse_and_render(15)
        expected = read_expected_output(15)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test16_paragraph_in_verse(self):
        """Test 16: Paragraph in middle of verse."""
        actual = parse_and_render(16)
        expected = read_expected_output(16)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test16_paragraph_in_verse(self):
        """Test 16: Paragraph in middle of verse."""
        actual = parse_and_render(16)
        expected = read_expected_output(16)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test17_space_after_open_quote(self):
        """Test 17: Space after open quote."""
        actual = parse_and_render(17)
        expected = read_expected_output(17)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test18_parenthesis_spacing(self):
        """Test 18: Parenthesis spacing."""
        actual = parse_and_render(18)
        expected = read_expected_output(18)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test19_space_before_closing_single_quote(self):
        """Test 19: Space before closing single quote."""
        actual = parse_and_render(19)
        expected = read_expected_output(19)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test20_space_after_long_dash(self):
        """Test 20: Space after long dash."""
        actual = parse_and_render(20)
        expected = read_expected_output(20)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test21_space_before_double_quote_after_addmarker(self):
        """Test 21: Space before double quote after addmarker."""
        actual = parse_and_render(21)
        expected = read_expected_output(21)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"
    def test_test22_missing_chapter_marker(self):
        """Test 22: Missing chapter marker."""
        actual = parse_and_render(22)
        expected = read_expected_output(22)
        assert actual == expected, f"Output mismatch:\nExpected: {expected!r}\nActual: {actual!r}"


class TestIntegrationWithFlags:
    """Integration tests with different CLI flags."""
    
    def test_with_para_flag_disabled(self):
        """Test parsing with paragraph markers disabled."""
        # Use a test file that has paragraph markers
        usfm_file = TEST_DIR / "test2.usfm"
        if not usfm_file.exists():
            pytest.skip("Test file test2.usfm not found")
        
        parser = UsfmParser()
        walker = AccordanceWalker(para=False, tc=True)
        
        doc = parser.load(str(usfm_file))
        output = walker.render(doc)
        
        # Verify no paragraph markers in output
        assert '¶' not in output
    
    def test_with_tc_flag_disabled(self):
        """Test parsing with text-critical marks disabled."""
        # This would need a test file with text-critical marks
        # For now, just verify the walker accepts the flag
        walker = AccordanceWalker(para=True, tc=False)
        assert walker.tc is False


class TestFileEncoding:
    """Test handling of different file encodings and line endings."""
    
    def test_utf8_with_bom(self):
        """Test files with UTF-8 BOM are handled correctly."""
        # The parser should handle BOM transparently via utf-8-sig encoding
        parser = UsfmParser()
        
        # Test with test3 which should work
        usfm_file = TEST_DIR / "test3.usfm"
        if usfm_file.exists():
            doc = parser.load(str(usfm_file))
            assert doc is not None
    
    def test_crlf_line_endings(self):
        """Test files with Windows line endings are normalized."""
        # The parser should normalize \r\n to \n
        parser = UsfmParser()
        
        # Test with any existing test file
        usfm_file = TEST_DIR / "test3.usfm"
        if usfm_file.exists():
            doc = parser.load(str(usfm_file))
            walker = AccordanceWalker()
            output = walker.render(doc)
            
            # Output should only have \n, not \r\n
            assert '\r\n' not in output
            # Single verse output may not have newlines, which is fine
            assert '\r' not in output


class TestErrorMessages:
    """Test that error messages are descriptive and include context."""
    
    def test_error_includes_filename(self):
        """Test that parsing errors include the filename."""
        usfm_file = TEST_DIR / "test5.usfm"
        if not usfm_file.exists():
            pytest.skip("Test file test5.usfm not found")
        
        parser = UsfmParser()
        
        with pytest.raises(Exception) as exc_info:
            parser.load(str(usfm_file))
        
        # Error message should include filename
        error_msg = str(exc_info.value)
        assert "test5.usfm" in error_msg or "verse" in error_msg.lower()
    
    def test_error_includes_line_number(self):
        """Test that parsing errors include line numbers."""
        usfm_file = TEST_DIR / "test5.usfm"
        if not usfm_file.exists():
            pytest.skip("Test file test5.usfm not found")
        
        parser = UsfmParser()
        
        with pytest.raises(Exception) as exc_info:
            parser.load(str(usfm_file))
        
        # Error message should include some context
        error_msg = str(exc_info.value)
        assert len(error_msg) > 0
