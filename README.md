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

- [README.md](https://github.com/robang74/busybox/README.md): this page for presenting the fork
- [FORK.md](FORK.md): vda-linux account hijacked crysis (**!!!**)
- [TODO.md](TODO.md): extension of TODO list w/o altering original
- [NEWS](NEWS): the changelog from busybox.net website

Already present in the original git repository:

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

- **addressed**: 44, class: potentially dangerous function use

#### Patches folder

This fork is offering `patches` folder collection for supporting downstream testing:

- [patches](https://github.com/robang74/busybox/tree/master/patches): for collecting patchsets, each in a single file.

All patches are independently based on `master`branch, and collisions might be happen.

Note that patches numeric indexing is made for chronologic order by lexicographic order.

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

- [b:master](https://github.com/robang74/busybox/tree/master), [b:applets](https://github.com/robang74/busybox/tree/applets), [b:features](https://github.com/robang74/busybox/tree/features), [b:bugfixes](https://github.com/robang74/busybox/tree/bugfixes), [b:devel](https://github.com/robang74/busybox/tree/devel), [b:bbox](https://github.com/robang74/busybox/tree/bboxnet).

These branches include contribs proposed for upstreaming from which cherry-pick and
in that order merged in [b:uchaosys](https://github.com/robang74/busybox/tree/uchaosys). Which is the branch in which reliable and stable
contributes are merged and it is dedicated to my personal project
[p:uchaosys](https://github.com/robang74/uchaosys). I use it, you can use it as well.

#### Repo evolution

The development on `busybox.net` started (2026-09-21) after months of impasse (2026-03-16), mainly for bug fixing and refactoring, typical activities after a maintainer change (despite the e-mail address remaining the same *vda.linux*). Therefore [b:bboxnet](https://github.com/robang74/busybox/tree/bboxnet) contains a copy 1:1 of the "community" development while the [b:devel](https://github.com/robang74/busybox/tree/devel) aims to integrated the fork with codebase.

#### Relevant changes

This fork contains some changes that did not go "upstream", and the most relevant are:

- The `$RANDOM` generation which busybox fails to pass the fist stage of PractRand stdin32 test and it is **not** even a good white-noise (minimum viable for uniformity) output.
- The `gunzip` (or `zcat`) speed which is basically fair, just 1.5x slower than the GNU `gzip` delivered by almost all Linux distributions, while it could be 1.75x faster.
- The `CRC32` computed via a 4KB static table which improves the speed by 3x times and this improvement has a quite impact on applets that make use of it, like `gzip` et company.
- The `DES` legacy password is confined into pre-`SuSv3` config section, not so much code but makes a sort of approach difference, expecially after the SSHole vulnerability.
- New applets like `unbuffer` to unbuffer applications `stdout`/`err`, or `shuf` random non-uniformity fixed, `unxz` with ARM64 and RISC-V BCJ filters, `awk` debug friendly, etc.

By rule of thumb, the sync of this fork with the "*community*" codebase happens when a relevant distribution like [Ubuntu](https://launchpad.net/ubuntu/+source/busybox), accepts and distributes it. The `devel` branch serves to speed-up the sync, spreading activities over the overall period of time between two releases.

<br>

### Maintainer

Limited to this fork, the maintainer is [Roberto A. Foglietta](mailto:roberto.foglietta@gmail.com)
