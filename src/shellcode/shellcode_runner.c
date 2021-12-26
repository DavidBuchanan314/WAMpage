#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main(int argc, char *argv[]) {
	if (argc != 2) {
		printf("USAGE: %s shellcode.bin\n", argv[0]);
		return -1;
	}

	int fd = open(argv[1], O_RDONLY);

	if (fd < 0) {
		perror("open");
		return -1;
	}

	struct stat sb;
	fstat(fd, &sb);

	void* rwxbuf = mmap(NULL, 
			sb.st_size,
			PROT_READ | PROT_WRITE | PROT_EXEC,
			MAP_PRIVATE,
			fd,
			0);

	if(rwxbuf == MAP_FAILED) {
		perror("mmap");
		return -1;
	}

	((void(*)())rwxbuf)();

	munmap(rwxbuf, sb.st_size);
	return 0;
}
