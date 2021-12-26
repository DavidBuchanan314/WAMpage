all: wampage.ipk

wampage.ipk: app/* app/snapshot_blob.bin
	ares-package app/
	mv tv.rootmy.wampage_0.0.1_all.ipk wampage.ipk

app/snapshot_blob.bin: app/snapshot_blob_orig.bin app/patch_snapshot.py
	python3 app/patch_snapshot.py $< $@

app/snapshot_blob_orig.bin: app/snapshot.js
	./bin/mksnapshot.sh $< --startup_blob $@
