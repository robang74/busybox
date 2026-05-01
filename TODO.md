## TODO

- [TODO](TODO): original TODO from busybox.net

---

### awk

To test against further regressions:

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

