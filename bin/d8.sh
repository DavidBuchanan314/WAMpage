#!/bin/sh

BASEDIR=$(dirname "$0")
qemu-arm $BASEDIR/d8_libs/ld-2.24.so --library-path $BASEDIR/d8_libs/ $BASEDIR/d8 $@
