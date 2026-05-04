## TODO

- [TODO](TODO): original TODO from busybox.net

---

### awk

To test against further regressions (downstreams):
+ [8b52c08a4](https://github.com/robang74/busybox/commit/8b52c08a4) - 2026-05-04 - awk: numeric identifiers full recognition, fixed in +65b total

Fixing: two major issues like walking %016llx and writing %n
Extend: support for "%fpx", keep "pi:%f" and earn "pi: %f deg"
Testing: editors/awk_printx_tests.sh added new (only visual)
Advantage: see all-and-only-the-OKs approach when viable (3 OKs)
- `test $(./run_3oks_test 2>&1 | grep OK | wc -l) -eq 3`

```sh 
./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%.2f OK f"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="%.2fpi %016llx f"; x=3.14; print x "" }';
./busybox awk 'BEGIN { CONVFMT="walk: %.2fpi %016llx "; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="OK pi: %.2fx"; x=3.14; print x "" }'
./busybox awk 'BEGIN { CONVFMT="%.2fOKpi"; x=3.14; print x "" }'

   text    data     bss     dec     hex filename
  19338       0       0   19338    4b8a editors/awk.o
Fixing:                     +51
  19389       0       0   19389    4bbd editors/awk.o
Extend:                     +16
  19405       0       0   19405    4bcd editors/awk.o
Coding:                      -2
  19403       0       0   19403    4bcb editors/awk.o
```



+ [70172e793](https://github.com/robang74/busybox/commit/70172e793) - 2026-05-03 - awk: proper numeric specifier type reading, bugfix

busybox awk seek for the last character in format and uses it for
infering the numeric specifier type (interger or float) despite it
sould be or not be related with the real specifier. This patch fixes
this behaviour thanks to previous patches: it starts from the % and
seek a '\0' or ' ' to find the type. Zero bytes footprint increase.

before:
```sh
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mf"; x=3.14; print x "" }'
Test PI: 3.14 mf
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mx"; x=3.14; print x "" }'
Test PI: 0.00 mx
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mm"; x=3.14; print x "" }'
awk: cmd. line:1: Invalid format specifier
```

after:
```sh
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f mx"; x=3.14; print x "" }'
Test PI: 3.14 mx
```

+ [75e5e57cf](https://github.com/robang74/busybox/commit/75e5e57cf) - 2026-05-01 - awk: minimalist approach to bugfixing some awk unsupported cases, p.2

```sh
+:git-shell:uchaosys:busybox> size editors/awk.o
   text    data     bss     dec     hex filename
  19338	      0	      0	  19338	   4b8a	editors/awk.o
  19389       0       0   19389    4bbd editors/awk.o
Difference:                 +51

./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
Test PI: 3.14
```

Regression in printouts that can break tests or scripts:

+ [770fdda9b](https://github.com/robang74/busybox/commit/770fdda9b) - 2026-05-01 - awk: minimalist approach to bugfixing some awk unsupported cases

```sh
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
3.14

awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
Test PI: 3.14
```

Uncovered case in `OFMT` and functional case in `CONVFMT`:

+ [428aa1e6](https://github.com/robang74/busybox/commit/428aa1e6) - 2026-05-01 - awk:  CONVFMT=%nf string format attack fix

```sh
./busybox awk 'BEGIN { OFMT="%nf"; x=3.14; print x }'
*** %n in writable segment detected ***
Aborted (core dumped)

./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x }'
3.14
```

---

### top

This 9aa599d (2011-01-25) is exactly the cause of >100% ram displaying described also by sertonix which reported the commit:

```diff
- "  PID  PPID USER     STAT   VSZ %MEM"
+ "  PID  PPID USER     STAT   VSZ %VSZ"
```

The users might expect to see MEM %MEM and not VSZ %VSZ which is "virtual" value but on constrained systems is the physical RAM to be the most relevant.

The value is so obscenely inflated that destroy the column alignment:

```
CPU:   0% usr   0% sys   0% nic  98% idle   0% io   0% irq   0% sirq
Load average: 0.24 0.43 0.52 1/1037 731380
  PID  PPID USER     STAT   VSZ %VSZ %CPU COMMAND
10114  9920 roberto  S    5544m  32%   0% /usr/bin/gnome-shell
 1488     1 root     S    3685m  22%   0% /bin/warp-svc
16232 10114 roberto  S    49.6g 298%   0% /opt/google/chrome/chrome
45259 16253 roberto  S    1392g8356%   0% /opt/google/chrome/chrome

731370730294 roberto  R     2524   0%   0% busybox top
```

And it is not the only displaying bug but also PID has longer values and breaks the vertical alignment. Despite the uptime being less than 1 day. Fortunately, `busybox top` never has been anything else than a gadget and rarely a last-resort or first-sight system debug tool.

**Conclusion**: busybox top is obsolete as a tool, rather than broken or worse designed. The "campaign" to keep bring back to life started a few years ago 294881d2e (2022-05-10) and did not receive a lot of attention.

