#!/bin/sh

runbin=${1:-./busybox}

echo
echo "Running 'awk' test unit:"
echo "  script: $0"
echo "  binary: $runbin"

# Unit test: 3.14 ko...ko 3.14
echo
echo 'Unit test: 3.14 ko...ko 3.14'
$runbin awk 'BEGIN { OFMT="%"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%"; x=3.14; print x "" }'
$runbin awk 'BEGIN { OFMT="%"; x=3.14; print x }'
$runbin awk 'BEGIN { CONVFMT="%"; x=3.14; print x }'
echo '    ---- == 4 == -----'
$runbin awk 'BEGIN { OFMT="%nf"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%n"; x=3.14; print x "" }'
$runbin awk 'BEGIN { OFMT="%nf"; x=3.14; print x }'
$runbin awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x }'
echo '    ---- == 5 == -----'
$runbin awk 'BEGIN { OFMT="%%nf"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%%nf"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%%n"; x=3.14; print x "" }'
$runbin awk 'BEGIN { OFMT="%%nf"; x=3.14; print x }'
$runbin awk 'BEGIN { CONVFMT="%%nf"; x=3.14; print x }'
echo '    ---- == 5 == -----'

# Unit test: 3.14 ??
echo
echo 'Unit test: 3.14 ??'
echo
$runbin awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="Test PI: %.2f mf"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="Test PI: %.2f mx"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="Test PI: %.2f mm"; x=3.14; print x "" }'
echo '    ---- == 4 == -----'

# Unit test: see all-and-only the OKs, it is passed otherwise not
echo
echo 'Unit test: only 4 OKs expected'
echo
$runbin awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%.2fpi %016llx f"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="walk: %.2fpi %016llx "; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%  d"; x=3.14; print x "" }'
echo '    ---- == 4 == -----'
$runbin awk 'BEGIN { CONVFMT="%.2f OK f"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="OK pi: %.2fx"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%.2fOKpi"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%f OK p"; x=3.14; print x "" }'
echo '    ---- == 4 == -----'

# Unit test: printing an integer despite invalid format is not supported anymore
echo
echo 'Unit test: back compatibility broken/check'
echo
$runbin awk 'BEGIN { CONVFMT="%d"; x=-1.5; print x "" }'
$runbin awk 'BEGIN { CONVFMT=" % f PC?"; x=3.14; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%n"; x=314; print x "" }'
$runbin awk 'BEGIN { CONVFMT=""; x=314; print x "" }'
echo '    ---- == 4 == -----'
$runbin awk 'BEGIN { CONVFMT="%hn  f"; x=-2.5; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%ln  f"; x=-2.5; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%lln f"; x=-2.5; print x "" }'
$runbin awk 'BEGIN { CONVFMT="% n  f"; x=-2.5; print x "" }'
echo '    ---- == 4 == -----'

# Unit test: support for int 53 bits + sign and pointers added to awk
echo
echo 'Unit test: how integers and pointers display'
echo
$runbin awk 'BEGIN { CONVFMT="%d"; x=-1; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%u"; x=-1; print x "" }'
$runbin awk 'BEGIN { CONVFMT="0x%x"; x=-1; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%p"; x=-1; print x "" }'
echo '    ---- == 4 == -----'
$runbin awk 'BEGIN { CONVFMT="%p"; x=11; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%x"; x=4294967296; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%lx"; x=4294967296; print x "" }'
$runbin awk 'BEGIN { CONVFMT="%llx"; x=8589934592; print x "" }'
echo '    ---- == 4 == -----'
echo
