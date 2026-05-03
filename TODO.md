## TODO

- [TODO](TODO): original TODO from busybox.net

---

### awk

To test against further regressions (downstreams):

+ [20a60c8f7](https://github.com/robang74/busybox/commit/20a60c8f7) - 2026-05-03 - awk: numeric identifiers full recognition, ext. in +63b total

```sh
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2fmx"; x=3.14; print x "" }'
Test PI: 3.14mx

      19338       0       0   19338    4b8a editors/awk.o
    Fixing:                     +51
      19389       0       0   19389    4bbd editors/awk.o
    Extend:                     +12
      19401       0       0   19401    4bc9 editors/awk.o
    Total:                      +63
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

