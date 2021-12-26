all: wampage.ipk

wampage.ipk: app/* app/snapshot_blob.bin
	ares-package app/
	mv tv.rootmy.wampage_0.0.1_all.ipk wampage.ipk

app/snapshot_blob.bin: app/snapshot.js
	./bin/mksnapshot.sh app/snapshot.js --startup_blob app/snapshot_blob.bin
