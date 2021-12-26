all: wampage.ipk

wampage.ipk: app/* app/snapshot_blob.bin
	ares-package app/
	mv tv.rootmy.wampage_0.0.1_all.ipk wampage.ipk

app/snapshot_blob.bin: build/snapshot_blob_orig.bin src/patch_snapshot.py
	python3 src/patch_snapshot.py $< $@

build/snapshot_blob_orig.bin: src/snapshot.js
	./bin/mksnapshot.sh $< --startup_blob $@

clean:
	rm -f build/* app/snapshot_blob.bin wampage.ipk

test:
	./bin/d8.sh app/exploit.js
