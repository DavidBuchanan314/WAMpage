#define xstr(s) str(s)
#define str(s) #s

.text
.global _start


_start:
	adr r0, pipefd
	mov r7, #42        @ pipe
	swi #0

	ldr r0, pipewrite
	adr r1, sourcecode
	ldr r2, sourcelen
	mov r7, #4         @ write
	swi #0

	ldr r0, pipewrite
	mov r7, #6
	swi #0             @ close

	ldr r0, piperead
	mov r1, #0
	mov r7, #63        @ dup2
	swi #0

	adr r0, prog
	adr r1, argv
	str r0, [r1]
	mov r2, #0
	mov r7, #11       @ execve
	swi #0


prog: .asciz "/usr/bin/python2"
argv: .word 0, 0
pipefd:
piperead: .word 0
pipewrite: .word 0

sourcelen: .word SOURCELEN
sourcecode:
@ to be appended
