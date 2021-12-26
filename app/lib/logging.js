function log(str) {
	print(str)
	return {
		then: function(cb) {
			if (typeof window !== "undefined") {
				window.requestAnimationFrame(cb);
			} else {
				cb();
			}
		}
	}
}
