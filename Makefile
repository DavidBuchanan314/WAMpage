.PHONY: clean test

GENERATED = app/snapshot_blob.bin app/lib/stage1_shellcode.js app/lib/stage2_shellcode.js

all: wampage.ipk

wampage.ipk: app/* ${GENERATED}
	ares-package app/
	mv tv.rootmy.wampage_0.0.1_all.ipk $@

app/snapshot_blob.bin: build/snapshot_blob_orig.bin src/patch_snapshot.py
	python3 src/patch_snapshot.py $< $@

build/snapshot_blob_orig.bin: src/snapshot.js
	./bin/mksnapshot.sh $< --startup_blob $@

src/shellcode/%: FORCE
	make -C src/shellcode/ $(notdir $@)

clean: src/shellcode/clean
	rm -f build/* wampage.ipk ${GENERATED}

app/lib/stage2_shellcode.js: src/shellcode/python_shellcode.bin
	sh -c 'echo "var stage2_shellcode_b64 = \`\n$$(base64 $<)\`;"' > $@

app/lib/stage1_shellcode.js: src/shellcode/shellcode.bin
	python3 -c '\
		sc = open("$<", "rb").read(); \
		print("var stage1_shellcode =", [ \
			int.from_bytes(sc[i:i+4], "little") \
			for i in range(0, len(sc), 4) \
		], end=";\n")' \
	> $@

test: ${GENERATED}
	./bin/d8.sh app/lib/*.js app/wampage.js

FORCE: ;
