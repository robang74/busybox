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
echo
./busybox awk 'BEGIN { OFMT="%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%n"; x=3.14; print x "" }';
./busybox awk 'BEGIN { OFMT="%nf"; x=3.14; print x }';
./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x }'
echo
./busybox awk 'BEGIN { OFMT="%%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%%n"; x=3.14; print x "" }';
./busybox awk 'BEGIN { OFMT="%%nf"; x=3.14; print x }';
./busybox awk 'BEGIN { CONVFMT="%%nf"; x=3.14; print x }'

# Unit test: 3.14 ??
echo
echo 'Unit test: 3.14 ??'
echo
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mf"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mx"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mm"; x=3.14; print x "" }'

# Unit test: see all-and-only the OKs, it is passed otherwise not
echo
echo 'Unit test: 3 OKs expected'
echo
./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%.2f OK f"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%.2fpi %016llx f"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="walk: %.2fpi %016llx "; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="OK pi: %.2fx"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="%.2fOKpi"; x=3.14; print x "" }'

# 3 OKs expected then test $(./run_3oks_test 2>&1 | grep OK | wc -l) -eq 3
echo
