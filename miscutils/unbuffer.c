/*
 * (c) 2026, Roberto A. Foglietta <roberto.foglietta@gmail.com>, GPLv2 license
 */

//config:config UNBUFFER
//config:	bool "unbuffer (0.5kb)"
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
  size check: before vs after
     text	   data	    bss	    dec	    hex	filename
  1096595	  16691	   1656	1114942	 11033e	busybox
     text	   data	    bss	    dec	    hex	filename
  1097217	  16711	   1656	1115584	 1105c0	busybox

  function                                             old     new   delta
  unbuffer_main                                          -     370    +370
  sigwinch_handler                                      15      98     +83
  packed_usage                                       35565   35602     +37
  applet_names                                        2817    2826      +9
  applet_main                                         3264    3272      +8
  .rodata                                           103410  103418      +8
  ptyfd                                                  -       4      +4
  applet_suid                                          102     103      +1
  applet_install_loc                                   204     205      +1
  ------------------------------------------------------------------------------
  (add/remove: 3/0 grow/shrink: 7/0 up/down: 521/0)             Total: 521 bytes
*/

#include "libbb.h"
#include <termios.h>
#include <unistd.h>
#include <utmp.h>
#include <pty.h>

static int ptyfd = -1;

static inline void sigwinch_handler(int sig UNUSED_PARAM)
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
    char ch;
    
    if (!argv[1]) bb_show_usage();
    
    setvbuf(stdout, NULL, _IONBF, 0);

    if((pid = forkpty(&fd, NULL, NULL, NULL)) < 0)
        bb_perror_msg_and_die("forkpty");
    if (pid == 0) { // child proccess
        BB_EXECVP_or_die(argv + 1);
    } // parent process
    ptyfd = fd;

    signal(SIGINT, SIG_IGN);
    signal(SIGTERM, SIG_IGN);
    bb_signals(1 << SIGWINCH, sigwinch_handler);
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
