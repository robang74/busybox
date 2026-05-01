## TODO

- [TODO](TODO): original TODO from busybox.net

---

Uncovered case in `OFMT` and functional case in `CONVFMT`:

+ [428aa1e](https://github.com/robang74/busybox/commit/428aa1e61cbfc478aea76578830c100273e1ba86) - 2026-05-01 - awk:  CONVFMT=%nf string format attack fix

```sh
./busybox awk 'BEGIN { OFMT="%nf"; x=3.14; print x }'
*** %n in writable segment detected ***
Aborted (core dumped)

./busybox awk 'BEGIN { CONVFMT="%nf"; x=3.14; print x }'
3.14
```
