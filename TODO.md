## TODO

- [TODO](TODO): original TODO from busybox.net

---

### awk

Regressions expected are those already warned about moving that part of awk
from a simpler to a more compliant way of operating regarding printf format.
The larger desktop version (cfr. .config options) supports users to debug
their awk scripts. A support usually welcomed in a transitional phase.

To test against further regressions (downstreams):

+ [patches/0008-awk-minimalist-approach-to-fix-some-unsupported-cases-v6.patch](patches/0008-awk-minimalist-approach-to-fix-some-unsupported-cases-v6.patch)

BusyBox awk seeks for the last character in format and uses it for
inferring the numeric specifier type (integer or float) despite it
sould be or not be related with the real specifier. This patch fixes
this misbehaviour thanks to previous patches: it starts from the %
and seeks a '\0' or ' ' to find the type.

- Fixing: two major issues like walking %016llx and writing %n
- Extend: support for "%fpx", keep "pi:%f" and earn "pi: %f deg"
- Testing: editors/awk_printx_tests.sh added new (only visual)

This patch disables the integer check beforehand which was probably the only
initial supported case which remained for back compatibility and moves forward
a full format support including the "%p" case. This emerging novel awk requires
no size increase (+3 bytes in total) but it breaks with the past for the better.

Acting on fmt_num() would impact on OFMT as well, just CONVFMT needs a fix
and the shortest path is to redirect the troublesome case into already %n
rejected because "Invalid format specifier"

The intrinsic limitation by "double" (IEEE 754) as type parameter remains for
integers which are going to lose precision outside the (-2^53, 2^53) range.

```
   text	   data	    bss	    dec	    hex	filename
  19352	      0	      0	  19352	   4b98	editors/awk.o
Total:                      +14

ENABLE_DESKTOP:
   text	   data	    bss	    dec	    hex	filename
  19338       0       0   19338    4b8a editors/awk.o
Fixing:                     +51
  19389       0       0   19389    4bbd editors/awk.o
Extend:                     +16
  19405	      0	      0	  19405	   4bcd	editors/awk.o
Coding:                      -2
  19403	      0	      0	  19403	   4bcb	editors/awk.o
Pointers:                   -62
  19341	      0	      0	  19341	   4b8d	editors/awk.o
Total:                       +3

Stricter:                   +38
  19379       0       0   19379    4bb3 editors/awk.o
Debugger:                   +38
  19408       0       0   19408    4bd9 editors/awk.o
Total:                      +70
```

Undefined behaviour isn't necessarily a failure (exit 1) and printing
the format as-is received by the users helps them to debug faster.
Adding a trivial prefix "E?:" helps to catch these cases immediately.

Info by Dietmar Schindler, according to:
- pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html
- pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap05.html

quoting this:
> If any character sequence in the format string begins with a '%' character,<br>
> but does not form a valid conversion specification, the behavior is unspecified

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

