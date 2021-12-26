#!/bin/sh

BASEDIR=$(dirname "$0")
qemu-i386 $BASEDIR/mksnapshot_libs/ld-2.31.so --library-path $BASEDIR/mksnapshot_libs/ $BASEDIR/mksnapshot $@
