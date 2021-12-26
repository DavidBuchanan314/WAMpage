var is_d8 = typeof window === "undefined";

function log(str) {
	if (is_d8) {
		print(str);
	} else {
		document.getElementById("log").innerText += "\n" + str;
	}
	return {
		then: function(cb) {
			if (is_d8) {
				cb();
			} else {
				window.requestAnimationFrame(cb);
			}
		}
	}
}
