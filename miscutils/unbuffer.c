/*
 * (c) 2026, Roberto A. Foglietta <roberto.foglietta@gmail.com>, GPLv2 license
 */

//config:config UNBUFFER
//config:	bool "unbuffer (0.7kb)"
//config:	default n
//config:	help
//config:	  Run a command in a PTY to disable buffering.

//applet:IF_UNBUFFER(APPLET(unbuffer, BB_DIR_USR_BIN, BB_SUID_DROP))

//kbuild:lib-$(CONFIG_UNBUFFER) += unbuffer.o
//kbuild:ldflags-$(CONFIG_UNBUFFER) += -lutil

//usage:#define unbuffer_trivial_usage
//usage: "CMD [ARGS]"
//usage:#define unbuffer_full_usage "\n\n"
//usage: "Run a command in a PTY to disable buffering."

/*
  size check: before vs after:
     text	   data	    bss	    dec	    hex	filename
  1096595	  16691	   1656	1114942	 11033e	busybox
     text	   data	    bss	    dec	    hex	filename
  1097296	  16711	   1656	1115663	 11060f	busybox

  how to apply:
  copy this file into in miscutils/unbuffer.c

  how to activate:
  make oldconfig && sed "s/^# *\(CONFIG_UNBUFFER\).*/\\1=y/" -i .config
*/

#include "libbb.h"
#include <termios.h>
#include <unistd.h>
#include <utmp.h>
#include <pty.h>

static int ptyfd = -1;

static void sigwinch_handler(int sig UNUSED_PARAM)
{
    struct winsize ws;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0)
        ioctl(ptyfd, TIOCSWINSZ, &ws);
}

int unbuffer_main(int argc, char **argv) MAIN_EXTERNALLY_VISIBLE;
int unbuffer_main(int argc, char **argv)
{
    int n, fd;
    pid_t pid;
    struct termios tios;
    sigset_t set, oldset;
    char ch;

    if (!(argc >> 1)) bb_show_usage();

    setvbuf(stdout, NULL, _IONBF, 0);

    sigfillset(&set);
    sigprocmask(SIG_BLOCK, &set, &oldset);

    bb_signals(SIG_BLOCK, NULL);
    signal(SIGWINCH, sigwinch_handler);
    signal(SIGCHLD, SIG_DFL);

    if((pid = forkpty(&fd, NULL, NULL, NULL)) < 0)
        bb_perror_msg_and_die("forkpty");

    if (pid == 0) { // child proccess
        sigprocmask(SIG_SETMASK, &oldset, NULL);
        BB_EXECVP_or_die(argv + 1);
    } // parent process
    ptyfd = fd;

    bb_signals((1<<SIGINT)|(1<<SIGTERM)|(1<<SIGHUP)|(1<<SIGQUIT), SIG_IGN);
    sigprocmask(SIG_SETMASK, &oldset, NULL);
    sigwinch_handler(0);

    if (tcgetattr(ptyfd, &tios) == 0) {
        cfmakeraw(&tios);
        tios.c_oflag |= ONLCR;
        tcsetattr(ptyfd, TCSANOW, &tios);
    }

    while ((n = read(ptyfd, &ch, 1)) == 1) {
        if(full_write(STDOUT_FILENO, &ch, 1) != 1) {
            bb_simple_perror_msg("write");
            break;
        }
    }
    if (n < 0 && errno != EIO)
        bb_simple_perror_msg("read");

    close(ptyfd);

    return wait_for_exitstatus(pid);
}
