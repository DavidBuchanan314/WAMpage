.PHONY: clean

all: shellcode_runner

PYTHON_SOURCE = ../devmemes.py
CC = arm-linux-gnueabi-gcc-10
AS = arm-linux-gnueabi-as
OBJCOPY = arm-linux-gnueabi-objcopy

shellcode_runner: shellcode_runner.c shellcode.bin python_shellcode.bin
	 ${CC} shellcode_runner.c -o shellcode_runner -static

shellcode.o: shellcode.s
	${AS} -k shellcode.s -o shellcode.o

python_shellcode_stub.o: python_shellcode_stub.s ${PYTHON_SOURCE}
	${AS} -k $< -o $@ --defsym SOURCELEN=$(shell stat --printf="%s" ${PYTHON_SOURCE})

python_shellcode.bin: python_shellcode_stub.bin ${PYTHON_SOURCE}
	cat $< ${PYTHON_SOURCE} > $@

%.bin: %.o
	arm-linux-gnueabi-objcopy -O binary -j .text $< $@

clean:
	rm -f *.bin *.o
