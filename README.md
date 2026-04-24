## BUSYBOX

**BusyBox is the Swiss army knife of embedded Linux**

BusyBox combines tiny versions of many common UNIX utilities into a single small executable.
It provides replacements for most of the utilities you usually find in GNU fileutils, shellutils, etc.

The utilities in BusyBox generally have fewer options than their full-featured GNU cousins;
however, the options that are included provide the expected functionality and behave very much like their GNU counterparts.
BusyBox provides a fairly complete environment for any small or embedded system.

BusyBox has been written with size-optimization and limited resources in mind.
It is also extremely modular so you can easily include or exclude commands (or features) at compile time.
This makes it easy to customize your embedded systems.

To create a working system, just add some device nodes in `/dev`, a few configuration files in `/etc`, and a Linux kernel.
You can find an example of boot-strapping a basic Linux embedded system (footprint 2MB) in [uchaosys cpio](https://github.com/robang74/uchaosys/tree/main/cpio) folder.

<br>

### Documentation

- [NEWS](NEWS): the changelog from busybox.net website
- [README](README): the original file from busybox.net repository
- [LICENSE](LICENSE): busybox is licenced under the GPLv2
- [AUTHORS](AUTHORS): list of authors of busybox
- [INSTALL](INSTALL): how to build & install
- [TODO](TODO): pending wishlist

<br>

### Repository

This repository is a github copy of the busybox [mirror](https://github.com/mirror/busybox) on github.
At the moment of the fork the mirror was behind the busybox master, stuck on commit [#371fe9f71](https://github.com/robang74/busybox/commit/371fe9f71)
dated 2024-07-14. After the fork, it has been integrated with the git repository
from `git.busybox.net` before it went down, at commit [#bee25205](https://github.com/robang74/busybox/commit/bee25205)
dated 2026-03-16. The change of the 'master' branch (the fork) happens on 2026-04-20,
once realised that the `git.busybox.net` crysis could have not be nor short nor temporary.

#### Legacy status

Open potentially alerts by severity/class in branch `main`:

- **security**: 103 critical, 96 high, 4 medium, **203 total**

Alerts above are related to C-language code, none otherwise.

<br>

### The fork

This repository has been created for my personal use and side projects.
Kept updated for a while by contribution collected around including the `busybox.net`
is aim to keep the BusyBox source code in safe (historical copy) and up-to-date,
possibly to continue the development, just in case. At the moment, it can be considered
a back-up and a supplementary resource.

BusyBox from last git.busybox.net master `HEAD`, saved in
[codeberg.org](https://codeberg.org/robang74/busybox) 
is providing an US/EU manually synced backup. Relevant branches: 

- [b:master](https://github.com/robang74/busybox/tree/master), [b:applets](https://github.com/robang74/busybox/tree/applets), [b:features](https://github.com/robang74/busybox/tree/features), [b:bugfixes](https://github.com/robang74/busybox/tree/bugfixes).

These branches include contribs proposed for upstreaming from which cherry-pick and
in that order merged in [b:uchaosys](https://github.com/robang74/busybox/tree/uchaosys). Which is the branch in which reliable and stable
contributes are merged and it is dedicated to my personal project
[p:uchaosys](https://github.com/robang74/uchaosys). I use it, you can use it as well.

<br>

### Maintainer

Limited to this specific fork, the maintainer is [Roberto A. Foglietta](mailto:roberto.foglietta@gmail.com)
