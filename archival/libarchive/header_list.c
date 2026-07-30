/* vi: set sw=4 ts=4: */
/*
 * Licensed under GPLv2 or later, see file LICENSE in this source tree.
 */
#include "libbb.h"
#include "bb_archive.h"

void FAST_FUNC header_list(archive_handle_t *archive_handle)
{
//TODO: cpio -vp DIR should output "DIR/NAME", not just "NAME" */

	const file_header_t *file_header = archive_handle->file_header;
	/* "tar xvOf TARFILE >OUTFILE" should use stderr for file list output: */
	FILE *fp = (archive_handle->action_data == data_extract_to_stdout) ? stderr : stdout;

	fprintf(fp, "%s\n", printable_string(file_header->name));
}
