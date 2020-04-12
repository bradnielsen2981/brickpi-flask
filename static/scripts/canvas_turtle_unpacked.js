	var canvas_turtle = function (f, h) {
		var k = this;
		this.elem = document.getElementById(f);
		var m = document.createElement("canvas");
		var n;
		var o = 0;
		var p = [];
		var q = [];
		var r = new Object();
		var s = [];
		var t = [];
		var u = -1;
		var v = -1;
		var w = [];
		var y = new Object();
		var z = [];
		var A = -1;
		var B = false;
		this.conf = {
			width: 800,
			height: 600,
			on_error: null,
			turtle: "./turtle.png"
		};
		this.construct = function () {
			if (m.getContext) {
				for (var a in h) {
					this.conf[a] = h[a]
				}
				this.elem.appendChild(m);
				m.setAttribute("width", parseInt(this.conf.width) + "px");
				m.setAttribute("height", parseInt(this.conf.height) + "px");
				n = m.getContext('2d');
				n.translate(Math.round(this.conf.width / 2), Math.round(this.conf.height / 2));
				n.rotate(Math.PI);
				n.beginPath();
				n.moveTo(0, 0)
			} else if (on_error) {
				on_error()
			}
		};
		this.exec = function (a) {
			if (a.replace(/\s+/g, "") != "") {
				a = a.replace(/\\r/g, "");
				var b = a.split("\n");
				var l = b.length;
				if (l > 1) {
					for (var i = 0; i < l; i++) {
						this.exec(b[i])
					}
				} else {
					a = a.toLowerCase();
					a = E(a.replace(/\s+/g, " "));
					var c = a.split(" ");
					var d = c.splice(0, 1);
					d = d[0];
					switch (d) {
						case ";":
							break;
						case "#":
							this.startfunc.apply(this, c);
							break;
						case "return":
							this.endfunc();
							break;
						default:
							if (A >= 0) {
								y[z[A]].push(a)
							} else {
								switch (d) {
									case 'next':
										this.next();
										break;
									case 'repeat':
										this.repeat.apply(this, c);
										break;
									case 'if':
										this.ifs.apply(this, c);
										break;
									case 'else':
										this.elses();
										break;
									case 'endif':
										this.endif();
										break;
									default:
										if (u >= 0 && w[w.length - 1] == "loop") {
											s[u].arr.push(a)
										} else if (v >= 0 && w[w.length - 1] == "if") {
											if (t[v].branch) {
												t[v].arr.push(a)
											}
										} else {
											if (this[d] && this[d].apply) {
												this[d].apply(this, c)
											}
										}
								}
							}
					}
				}
			}
		};
		this.move = function (a) {
			a = C(a);
			n.moveTo(0, a);
			n.translate(0, a);
			F()
		};
		this.draw = function (a) {
			a = C(a);
			n.lineTo(0, a);
			n.stroke();
			n.beginPath();
			n.moveTo(0, a);
			n.translate(0, a);
			F()
		};
		this.right = function (a) {
			a = C(a);
			var b = (Math.PI / 180) * a;
			o += parseInt(a);
			n.rotate(b);
			F()
		};
		this.left = function (a) {
			a = C(a);
			var b = (Math.PI / 180) * (360 - a);
			o -= parseInt(a);
			n.rotate(b);
			F()
		};
		this.clear = function () {
			n.closePath();
			n.setTransform(1, 0, 0, 1, 0, 0);
			n.clearRect(0, 0, this.conf.width, this.conf.height);
			n.translate(Math.round(this.conf.width / 2), Math.round(this.conf.height / 2));
			n.rotate(Math.PI);
			n.beginPath();
			n.moveTo(0, 0);
			F()
		};
		this.home = function () {
			n.closePath();
			n.setTransform(1, 0, 0, 1, 0, 0);
			n.translate(Math.round(this.conf.width / 2), Math.round(this.conf.height / 2));
			n.rotate(Math.PI);
			n.beginPath();
			n.moveTo(0, 0);
			F()
		};
		
		this.goto = function (x,y) {
			n.moveTo(x,y);
		};
		
		this.color = function (a) {
			var c = C(a);
			c = (c == 0) ? a : c;
			n.strokeStyle = c
		};
		this.thick = function (a) {
			a = C(a);
			n.lineWidth = a
		};
		this.transparent = function (a) {
			a = C(a);
			n.globalAlpha = a / 100
		};
		this.remember = function () {
			n.save();
			p.push(w)
		};
		this.goback = function () {
			n.restore();
			n.moveTo(0, 0);
			w = p[p.length - 1];
			p.splice(p.length - 1, 1)
		};
		this.point = function (a) {
			a = C(a);
			var g = o % 360;
			this.right(a - g);
			F()
		};
		this.let = function (a) {
			var b = [];
			for (var i in arguments) {
				if (i > 0) {
					b.push(arguments[i])
				}
			}
			var c;
			if (b.length == 1 && r[b[0]]) {
				c = r[b[0]]
			} else {
				c = b.join(" ")
			}
			r[a] = c
		};
		this.repeat = function (a) {
			a = C(a);
			u = s.length;
			s[u] = new Object();
			s[u].iter = a;
			s[u].arr = [];
			w.push("loop")
		};
		this.next = function () {
			var a = s.splice(u, 1);
			a = a[0];
			u--;
			var l = a.arr.length;
			var b = a.iter;
			for (var i = 0; i < b; i++) {
				for (var j = 0; j < l; j++) {
					this.exec(a.arr[j].toString())
				}
			}
			w.pop()
		};
		this.push = function (a, b) {
			b = C(b);
			if (!q[a]) {
				q[a] = []
			}
			q[a].push(b)
		};
		this.pop = function (a, b) {
			if (!q[a]) {
				r[b] = q[a].pop()
			}
		};
		this.ifs = function (a, c, b) {
			a = C(a);
			b = C(b);
			var d;
			switch (c) {
				case "=":
					d = (a == b);
					break;
				case "==":
					d = (a == b);
					break;
				case "!=":
					d = (a != b);
					break;
				case "<>":
					d = (a != b);
					break;
				case "<":
					d = (a < b);
					break;
				case ">":
					d = (a > b);
					break;
				case "<=":
					d = (a <= b);
					break;
				case ">=":
					d = (a >= b);
					break
			}
			v = t.length;
			t[v] = new Object();
			t[v].branch = d;
			t[v].arr = [];
			w.push("if")
		};
		this.elses = function () {
			t[v].branch = !t[v].branch
		};
		this.endif = function () {
			var a = t.splice(v, 1);
			a = a[0];
			v--;
			var l = a.arr.length;
			for (var i = 0; i < l; i++) {
				this.exec(a.arr[i].toString())
			}
			w.pop()
		};
		this.startfunc = function (a) {
			A = z.length;
			z[A] = a;
			y[a] = []
		};
		this.endfunc = function () {
			z.splice(A, 1);
			A--
		};
		this.go = function (a) {
			if (y[a]) {
				var l = y[a].length;
				for (var i = 0; i < l; i++) {
					this.exec(y[a][i])
				}
			}
		};
		this.showturtle = function () {
			B = true;
			F()
		};
		this.end = function () {
			B = true;
			F()
		};
		this.hideturtle = function () {
			B = false
		};
		this.goleft = function (a, b) {
			a = C(a);
			b = C(b);
			n.quadraticCurveTo(0, a, a, b);
			n.stroke();
			n.beginPath();
			n.moveTo(a, b);
			n.translate(a, b);
			var c = Math.atan2(a, 0);
			var d = Math.atan2(b - a, a);
			var e = Math.abs(c - d);
			o -= parseInt((e * 180 / Math.PI));
			n.rotate(-e);
			F()
		};
		this.goright = function (a, b) {
			a = C(a);
			b = C(b);
			n.quadraticCurveTo(0, a, -a, b);
			n.stroke();
			n.beginPath();
			n.moveTo(-a, b);
			n.translate(-a, b);
			var c = Math.atan2(a, 0);
			var d = Math.atan2(b - a, a);
			var e = Math.abs(c - d);
			o += parseInt(e * 180 / Math.PI);
			n.rotate(e);
			F()
		};
		this.print = function () {
			var a = [];
			for (var i in arguments) {
				a.push(arguments[i])
			}
			if (a.length == 1 && r[a[0]]) {
				var b = r[a[0]]
			} else {
				var b = a.join(" ")
			}
			var g = o % 360;
			this.point(180);
			n.fillText(b, 0, 0);
			this.point(g)
		};
		this.turtleprint = function () {
			var a = [];
			for (var i in arguments) {
				a.push(arguments[i])
			}
			var b;
			if (a.length == 1 && r[a[0]]) {
				b = r[a[0]]
			} else {
				b = a.join(" ")
			}
			var c = n.measureText(b).width;
			this.right(90);
			n.textBaseline = "middle";
			n.fillText(b, 0, 0);
			n.textBaseline = "alphabetic";
			this.left(90);
			this.move(c)
		};
		this.font = function () {
			var a = [];
			for (var i in arguments) {
				a.push(arguments[i])
			}
			var b = a.join(" ");
			n.font = b
		};
		this.get = function (a, b) {
			var c;
			if (typeof b == "string" && document.getElementById(b)) {
				c = document.getElementById(b).value
			} else {
				c = prompt("Enter value")
			}
			this.let(a, c)
		};
		var C = function (a) {
			if (D(a)) {
				return parseFloat(a)
			} else if (r[a]) {
				return r[a]
			} else {
				var x = 0;
				try {
					eval("x = parseFloat(" + a + ");")
				} catch (e) {
					var b = a.split(/[\*\+\-\/%\(\)]+/);
					var l = b.length;
					var c = "";
					for (var i = 0; i < l; i++) {
						if (b[i].length > 0) {
							var d = a.slice(0, a.indexOf(b[i]) + b[i].length);
							c += d.replace(b[i], "get_val('" + b[i] + "')");
							a = a.slice(a.indexOf(b[i]) + b[i].length)
						}
					}
					try {
						eval("x = parseFloat(" + c + ");")
					} catch (e) {
						x = 0
					}
				};
				return x
			}
		};
		var D = function (a) {
			return !isNaN(parseFloat(a)) && isFinite(a)
		};
		var E = function (a) {
			return a.replace(/^\s+|\s+$/g, "")
		};
		var F = function () {
			if (B) {
				var a = new Image();
				a.src = k.conf.turtle;
				a.onload = function () {
					n.drawImage(a, -Math.round(a.width / 2), 0)
				}
			}
		};
		this.construct()
	};