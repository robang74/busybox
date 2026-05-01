## TODO

- [TODO](TODO): original TODO from busybox.net

---

### awk

Regression in printouts that can break tests or scripts:

+ [770fdda9b](https://github.com/robang74/busybox/commit/770fdda9b) - 2026-05-01 - awk: minimalist approach to bugfixing some awk unsupported cases

```sh
./busybox awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
3.14

awk 'BEGIN { CONVFMT="Test PI: %.2f"; x=3.14; print x "" }'
Test PI: 3.14
```

Uncovered case in `OFMT` and functional case in `CONVFMT`:

+ [428aa1e](https://github.com/robang74/busybox/commit/428aa1e) - 2026-05-01 - awk:  CONVFMT=%nf string format attack fix

```sh
./busybox awk 'BEGIN { OFMT="%nf"; x=3.14; print x }'
*** %n in writable segment detected ***
Aborted (core dumped)

./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x }'
3.14
```
