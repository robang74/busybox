/* vi: set sw=4 ts=4: */
/*
 * Licensed under GPLv2 or later, see file LICENSE in this source tree.
 */
#include "libbb.h"
#include "bb_archive.h"

void FAST_FUNC header_list(const file_header_t *file_header)
{
//TODO: cpio -vp DIR should output "DIR/NAME", not just "NAME" */
	fputs(printable_string(file_header->name), file_header->verbose_fp);
	fputc('\n', file_header->verbose_fp);
	fflush(file_header->verbose_fp);
}
