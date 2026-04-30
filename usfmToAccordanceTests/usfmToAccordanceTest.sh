#!/bin/sh -v

# Run some test files and produce output to compare to known good

# Remember to start the Python environment
# with source ../.usfmparse/bin/activate

rm -rf *.tmp

#SCRIPT='python3 ../usfmToAccordance.py'
SCRIPT='python3 -m usfmtools.usfmToAccordance'

$SCRIPT test1.usfm > test1.tmp
diff test1.acc test1.tmp
$SCRIPT test2.usfm > test2.tmp
diff test2.acc test2.tmp
$SCRIPT test3.usfm > test3.tmp
diff test3.acc test3.tmp
$SCRIPT test4.usfm > test4.tmp
diff test4.acc test4.tmp
# Test if verse number is missing. Should say
# ERROR: Missing verse number in test5.usfm:3
$SCRIPT test5.usfm > test5.tmp
diff test5.acc test5.tmp
# Test if chapter number is missing. Should say
# ERROR: Missing chapter number in test6.usfm:2
$SCRIPT test6.usfm > test6.tmp
diff test6.acc test6.tmp
$SCRIPT test7.usfm > test7.tmp
diff test7.acc test7.tmp
$SCRIPT test8.usfm > test8.tmp
diff test8.acc test8.tmp
$SCRIPT test9.usfm > test9.tmp
diff test9.acc test9.tmp
# Problem with simple footnotes - must eliminate
$SCRIPT test10.usfm > test10.tmp
diff test10.acc test10.tmp
# Problem with complex glossary entries with strong number attributes must eliminate
$SCRIPT test11.usfm > test11.tmp
diff test11.acc test11.tmp
# More problems with glossary \w and footnotes
$SCRIPT test12.usfm > test12.tmp
diff test12.acc test12.tmp
$SCRIPT test13.usfm > test13.tmp
diff test13.acc test13.tmp
$SCRIPT test14.usfm > test14.tmp
diff test14.acc test14.tmp
$SCRIPT test15.usfm > test15.tmp
diff test15.acc test15.tmp
$SCRIPT test16.usfm > test16.tmp
diff test16.acc test16.tmp

$SCRIPT test17.usfm > test17.tmp
diff test17.acc test17.tmp
$SCRIPT test18.usfm > test18.tmp
diff test18.acc test18.tmp
$SCRIPT test19.usfm > test19.tmp
diff test19.acc test19.tmp
$SCRIPT test20.usfm > test20.tmp
diff test20.acc test20.tmp
$SCRIPT test21.usfm > test21.tmp
diff test21.acc test21.tmp
$SCRIPT test22.usfm > test22.tmp
diff test22.acc test22.tmp
$SCRIPT test23.usfm > test23.tmp
diff test23.acc test23.tmp
$SCRIPT test24.usfm > test24.tmp
diff test24.acc test24.tmp
$SCRIPT --separate-quotes test25.usfm > test25.tmp
diff test25.acc test25.tmp
$SCRIPT test26.usfm > test26.tmp
diff test26.acc test26.tmp
