#!/bin/sh

echo
echo "Running $0 testing script..."

# Unit test: 3.14 ko...ko 3.14
echo
echo 'Unit test: 3.14 ko...ko 3.14'
./busybox awk 'BEGIN { OFMT="%"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%"; x=3.14; print x "" }';
./busybox awk 'BEGIN { OFMT="%"; x=3.14; print x }';
./busybox awk 'BEGIN { CONVFMT="%"; x=3.14; print x }'
echo '    ---- == 4 == -----'
./busybox awk 'BEGIN { OFMT="%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%n"; x=3.14; print x "" }';
./busybox awk 'BEGIN { OFMT="%nf"; x=3.14; print x }';
./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x }'
echo '    ---- == 5 == -----'
./busybox awk 'BEGIN { OFMT="%%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%%n"; x=3.14; print x "" }';
./busybox awk 'BEGIN { OFMT="%%nf"; x=3.14; print x }';
./busybox awk 'BEGIN { CONVFMT="%%nf"; x=3.14; print x }'
echo '    ---- == 5 == -----'

# Unit test: 3.14 ??
echo
echo 'Unit test: 3.14 ??'
echo
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mf"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mx"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mm"; x=3.14; print x "" }'
echo '    ---- == 4 == -----'

# Unit test: see all-and-only the OKs, it is passed otherwise not
echo
echo 'Unit test: only 5 OKs expected'
echo
./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%.2fpi %016llx f"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="walk: %.2fpi %016llx "; x=3.14; print x "" }'
echo '    ---- == 3 == -----'
./busybox awk 'BEGIN { CONVFMT="%.2f OK f"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="OK pi: %.2fx"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="%.2fOKpi"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="%d OK"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%f OK p"; x=3.14; print x "" }';
echo '    ---- == 5 == -----'

# Unit test: printing an integer despite invalid format is not supported anymore
echo
echo 'Unit test: back compatibility broken'
echo
./busybox awk 'BEGIN { CONVFMT="%n"; x=314; print x "" }';
./busybox awk 'BEGIN { CONVFMT=""; x=314; print x "" }';
echo '    ---- == 2 == -----'

# Unit test: support for int 53 bits + sign and pointers added to awk
echo
echo 'Unit test: how integers and pointers display'
echo
./busybox awk 'BEGIN { CONVFMT="%d"; x=-1; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%u"; x=-1; print x "" }';
./busybox awk 'BEGIN { CONVFMT="0x%x"; x=-1; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%p"; x=-1; print x "" }';
echo '    ---- == 4 == -----'
./busybox awk 'BEGIN { CONVFMT="%p"; x=11; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%x"; x=4294967296; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%lx"; x=4294967296; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%llx"; x=8589934592; print x "" }';
echo '    ---- == 4 == -----'
echo
