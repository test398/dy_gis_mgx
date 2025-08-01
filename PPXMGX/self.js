self.onerror = function() {
    console.error('An error occurred while parsing the WebWorker bundle. This is most likely due to improper transpilation by Babel; please see https://docs.sgmap.com/sgmap-js/guides/install/#transpiling');
}
;
var sharedChunk = {};
(function(t) {
    "use strict";
    var e = "undefined" != typeof self ? self : {}
      , r = n;
    function n(t, e, r, n) {
        this.cx = 3 * t,
        this.bx = 3 * (r - t) - this.cx,
        this.ax = 1 - this.cx - this.bx,
        this.cy = 3 * e,
        this.by = 3 * (n - e) - this.cy,
        this.ay = 1 - this.cy - this.by,
        this.p1x = t,
        this.p1y = n,
        this.p2x = r,
        this.p2y = n;
    }
    n.prototype.sampleCurveX = function(t) {
        return ((this.ax * t + this.bx) * t + this.cx) * t
    }
    ,
    n.prototype.sampleCurveY = function(t) {
        return ((this.ay * t + this.by) * t + this.cy) * t
    }
    ,
    n.prototype.sampleCurveDerivativeX = function(t) {
        return (3 * this.ax * t + 2 * this.bx) * t + this.cx
    }
    ,
    n.prototype.solveCurveX = function(t, e) {
        var r, n, i, s, a;
        for (void 0 === e && (e = 1e-6),
        i = t,
        a = 0; a < 8; a++) {
            if (s = this.sampleCurveX(i) - t,
            Math.abs(s) < e)
                return i;
            var o = this.sampleCurveDerivativeX(i);
            if (Math.abs(o) < 1e-6)
                break;
            i -= s / o;
        }
        if ((i = t) < (r = 0))
            return r;
        if (i > (n = 1))
            return n;
        for (; r < n; ) {
            if (s = this.sampleCurveX(i),
            Math.abs(s - t) < e)
                return i;
            t > s ? r = i : n = i,
            i = .5 * (n - r) + r;
        }
        return i
    }
    ,
    n.prototype.solve = function(t, e) {
        return this.sampleCurveY(this.solveCurveX(t, e))
    }
    ;
    var i = s;
    function s(t, e) {
        this.x = t,
        this.y = e;
    }
    s.prototype = {
        clone: function() {
            return new s(this.x,this.y)
        },
        add: function(t) {
            return this.clone()._add(t)
        },
        sub: function(t) {
            return this.clone()._sub(t)
        },
        multByPoint: function(t) {
            return this.clone()._multByPoint(t)
        },
        divByPoint: function(t) {
            return this.clone()._divByPoint(t)
        },
        mult: function(t) {
            return this.clone()._mult(t)
        },
        div: function(t) {
            return this.clone()._div(t)
        },
        rotate: function(t) {
            return this.clone()._rotate(t)
        },
        rotateAround: function(t, e) {
            return this.clone()._rotateAround(t, e)
        },
        matMult: function(t) {
            return this.clone()._matMult(t)
        },
        unit: function() {
            return this.clone()._unit()
        },
        perp: function() {
            return this.clone()._perp()
        },
        round: function() {
            return this.clone()._round()
        },
        mag: function() {
            return Math.sqrt(this.x * this.x + this.y * this.y)
        },
        equals: function(t) {
            return this.x === t.x && this.y === t.y
        },
        dist: function(t) {
            return Math.sqrt(this.distSqr(t))
        },
        distSqr: function(t) {
            var e = t.x - this.x
              , r = t.y - this.y;
            return e * e + r * r
        },
        angle: function() {
            return Math.atan2(this.y, this.x)
        },
        angleTo: function(t) {
            return Math.atan2(this.y - t.y, this.x - t.x)
        },
        angleWith: function(t) {
            return this.angleWithSep(t.x, t.y)
        },
        angleWithSep: function(t, e) {
            return Math.atan2(this.x * e - this.y * t, this.x * t + this.y * e)
        },
        _matMult: function(t) {
            var e = t[2] * this.x + t[3] * this.y;
            return this.x = t[0] * this.x + t[1] * this.y,
            this.y = e,
            this
        },
        _add: function(t) {
            return this.x += t.x,
            this.y += t.y,
            this
        },
        _sub: function(t) {
            return this.x -= t.x,
            this.y -= t.y,
            this
        },
        _mult: function(t) {
            return this.x *= t,
            this.y *= t,
            this
        },
        _div: function(t) {
            return this.x /= t,
            this.y /= t,
            this
        },
        _multByPoint: function(t) {
            return this.x *= t.x,
            this.y *= t.y,
            this
        },
        _divByPoint: function(t) {
            return this.x /= t.x,
            this.y /= t.y,
            this
        },
        _unit: function() {
            return this._div(this.mag()),
            this
        },
        _perp: function() {
            var t = this.y;
            return this.y = this.x,
            this.x = -t,
            this
        },
        _rotate: function(t) {
            var e = Math.cos(t)
              , r = Math.sin(t)
              , n = r * this.x + e * this.y;
            return this.x = e * this.x - r * this.y,
            this.y = n,
            this
        },
        _rotateAround: function(t, e) {
            var r = Math.cos(t)
              , n = Math.sin(t)
              , i = e.y + n * (this.x - e.x) + r * (this.y - e.y);
            return this.x = e.x + r * (this.x - e.x) - n * (this.y - e.y),
            this.y = i,
            this
        },
        _round: function() {
            return this.x = Math.round(this.x),
            this.y = Math.round(this.y),
            this
        }
    },
    s.convert = function(t) {
        return t instanceof s ? t : Array.isArray(t) ? new s(t[0],t[1]) : t
    }
    ;
    const a = Math.PI / 180
      , o = 180 / Math.PI;
    function l(t) {
        return t * a
    }
    function u(t) {
        return t * o
    }
    const c = [[0, 0], [1, 0], [1, 1], [0, 1]];
    function h(t) {
        if (t <= 0)
            return 0;
        if (t >= 1)
            return 1;
        const e = t * t
          , r = e * t;
        return 4 * (t < .5 ? r : 3 * (t - e) + r - .75)
    }
    function p(t, e, n, i) {
        const s = new r(t,e,n,i);
        return function(t) {
            return s.solve(t)
        }
    }
    const f = p(.25, .1, .25, 1);
    function d(t, e, r) {
        return Math.min(r, Math.max(e, t))
    }
    function y(t, e, r) {
        return (r = d((r - t) / (e - t), 0, 1)) * r * (3 - 2 * r)
    }
    function m(t, e, r) {
        const n = r - e
          , i = ((t - e) % n + n) % n + e;
        return i === e ? r : i
    }
    function g(t, e, r) {
        if (!t.length)
            return r(null, []);
        let n = t.length;
        const i = new Array(t.length);
        let s = null;
        t.forEach(((t,a)=>{
            e(t, ((t,e)=>{
                t && (s = t),
                i[a] = e,
                0 == --n && r(s, i);
            }
            ));
        }
        ));
    }
    function x(t) {
        const e = [];
        for (const r in t)
            e.push(t[r]);
        return e
    }
    function v(t, ...e) {
        for (const r of e)
            for (const e in r)
                t[e] = r[e];
        return t
    }
    let b = 1;
    function w() {
        return b++
    }
    function A(t) {
        return t <= 1 ? 1 : Math.pow(2, Math.ceil(Math.log(t) / Math.LN2))
    }
    function k(t, e) {
        t.forEach((t=>{
            e[t] && (e[t] = e[t].bind(e));
        }
        ));
    }
    function z(t, e) {
        return -1 !== t.indexOf(e, t.length - e.length)
    }
    function S(t, e, r) {
        const n = {};
        for (const i in t)
            n[i] = e.call(r || this, t[i], i, t);
        return n
    }
    function M(t, e, r) {
        const n = {};
        for (const i in t)
            e.call(r || this, t[i], i, t) && (n[i] = t[i]);
        return n
    }
    function I(t) {
        return Array.isArray(t) ? t.map(I) : "object" == typeof t && t ? S(t, I) : t
    }
    const T = {};
    function B(t) {
        T[t] || ("undefined" != typeof console && console.warn(t),
        T[t] = !0);
    }
    function C(t, e, r) {
        return (r.y - t.y) * (e.x - t.x) > (e.y - t.y) * (r.x - t.x)
    }
    function V(t) {
        let e = 0;
        for (let r, n, i = 0, s = t.length, a = s - 1; i < s; a = i++)
            r = t[i],
            n = t[a],
            e += (n.x - r.x) * (r.y + n.y);
        return e
    }
    function P() {
        return "undefined" != typeof WorkerGlobalScope && "undefined" != typeof self && self instanceof WorkerGlobalScope
    }
    function D(t) {
        const e = {};
        if (t.replace(/(?:^|(?:\s*\,\s*))([^\x00-\x20\(\)<>@\,;\:\\"\/\[\]\?\=\{\}\x7F]+)(?:\=(?:([^\x00-\x20\(\)<>@\,;\:\\"\/\[\]\?\=\{\}\x7F]+)|(?:\"((?:[^"\\]|\\.)*)\")))?/g, ((t,r,n,i)=>{
            const s = n || i;
            return e[r] = !s || s.toLowerCase(),
            ""
        }
        )),
        e["max-age"]) {
            const t = parseInt(e["max-age"], 10);
            isNaN(t) ? delete e["max-age"] : e["max-age"] = t;
        }
        return e
    }
    let E = null;
    function F(t) {
        if (null == E) {
            const e = t.navigator ? t.navigator.userAgent : null;
            E = !!t.safari || !(!e || !(/\b(iPad|iPhone|iPod)\b/.test(e) || e.match("Safari") && !e.match("Chrome")));
        }
        return E
    }
    function L(t, e) {
        return [t[4 * e], t[4 * e + 1], t[4 * e + 2], t[4 * e + 3]]
    }
    const R = e.performance;
    function j(t) {
        if (!R)
            return;
        const e = t ? t.url.toString() : void 0;
        return R.getEntriesByName(e)
    }
    let U, O, $, q;
    const N = {
        now: ()=>void 0 !== $ ? $ : e.performance.now(),
        setNow(t) {
            $ = t;
        },
        restoreNow() {
            $ = void 0;
        },
        frame(t) {
            const r = e.requestAnimationFrame(t);
            return {
                cancel: ()=>e.cancelAnimationFrame(r)
            }
        },
        getImageData(t, r=0) {
            const {width: n, height: i} = t;
            q || (q = e.document.createElement("canvas"));
            const s = q.getContext("2d", {
                willReadFrequently: !0
            });
            if (!s)
                throw new Error("failed to create canvas 2d context");
            return (n > q.width || i > q.height) && (q.width = n,
            q.height = i),
            s.clearRect(-r, -r, n + 2 * r, i + 2 * r),
            s.drawImage(t, 0, 0, n, i),
            s.getImageData(-r, -r, n + 2 * r, i + 2 * r)
        },
        resolveURL: t=>(U || (U = e.document.createElement("a")),
        U.href = t,
        U.href),
        get devicePixelRatio() {
            return e.devicePixelRatio
        },
        get prefersReducedMotion() {
            return !!e.matchMedia && (null == O && (O = e.matchMedia("(prefers-reduced-motion: reduce)")),
            O.matches)
        }
    }
      , Z = {
        API_URL: "",
        ACCESS_TOKEN: null,
        MAX_PARALLEL_IMAGE_REQUESTS: 16
    }
      , G = {
        supported: !1,
        testSupport: function(t) {
            !H && Y && (K ? J(t) : X = t);
        }
    };
    let X, Y, H = !1, K = !1;
    function J(t) {
        const e = t.createTexture();
        t.bindTexture(t.TEXTURE_2D, e);
        try {
            if (t.texImage2D(t.TEXTURE_2D, 0, t.RGBA, t.RGBA, t.UNSIGNED_BYTE, Y),
            t.isContextLost())
                return;
            G.supported = !0;
        } catch (t) {}
        t.deleteTexture(e),
        H = !0;
    }
    e.document && (Y = e.document.createElement("img"),
    Y.onload = function() {
        X && J(X),
        X = null,
        K = !0;
    }
    ,
    Y.onerror = function() {
        H = !0,
        X = null;
    }
    ,
    Y.src = "data:image/webp;base64,UklGRh4AAABXRUJQVlA4TBEAAAAvAQAAAAfQ//73v/+BiOh/AAA=");
    const W = "01";
    function Q(t) {
        return 0 === t.indexOf("aegis:") || /aegis\./
    }
    const tt = /^((https?:)?\/\/)?([^\/]+\.)?(epgis|sgcc)\.c(n|om)(\.cn)?|^aegis:\/\//i;
    function et(t) {
        return tt.test(t)
    }
    function rt(t) {
        for (const e of t) {
            const t = e.match(/^access_token=(.*)$/);
            if (t)
                return t[1]
        }
        return null
    }
    const nt = /^(\w+):\/\/([^/?]*)(\/[^?]+)?\??(.+)?/;
    function it(t) {
        const e = t.match(nt);
        if (!e)
            throw new Error("Unable to parse URL object");
        return {
            protocol: e[1],
            authority: e[2],
            path: e[3] || "/",
            params: e[4] ? e[4].split("&") : []
        }
    }
    function st(t) {
        const e = t.params.length ? `?${t.params.join("&")}` : "";
        return `${t.protocol}://${t.authority}${t.path}${e}`
    }
    let at, ot = 500, lt = 50, ut = {};
    function ct(t) {
        const e = ft(t);
        let r, n;
        e && e.forEach((t=>{
            const e = t.split("=");
            "language" === e[0] ? r = e[1] : "worldview" === e[0] && (n = e[1]);
        }
        ));
        let i = "sgmap-tiles";
        return r && (i += `-${r}`),
        n && (i += `-${n}`),
        i
    }
    function ht() {
        try {
            return e.caches
        } catch (t) {}
    }
    function pt(t) {
        const e = ht();
        e && !ut[t] && (ut[t] = e.open(t));
    }
    function ft(t) {
        const e = t.indexOf("?");
        return e > 0 ? t.slice(e + 1).split("&") : []
    }
    function dt(t) {
        const e = t.indexOf("?");
        if (e < 0)
            return t;
        const r = ft(t).filter((t=>{
            const e = t.split("=");
            return "language" === e[0] || "worldview" === e[0]
        }
        ));
        return r.length ? `${t.slice(0, e)}?${r.join("&")}` : t.slice(0, e)
    }
    let yt = 1 / 0;
    !function() {
        for (var t = [], e = 0; e < 256; ++e)
            t.push("%" + ((e < 16 ? "0" : "") + e.toString(16)).toUpperCase());
    }();
    const mt = (t,e)=>{
        let r, n, i, s = t.z % 8, a = t.x % 8, o = t.y % 8, l = e, u = l.byteLength - s - a - o, c = Math.floor(u / 3), h = Math.floor(u / 3), p = u - c - h;
        o <= a && a <= s && o <= s ? (i = new Uint8Array(l.slice(o, p + o)),
        n = new Uint8Array(l.slice(p + a + o, p + h + a + o)),
        r = new Uint8Array(l.slice(p + h + a + o + s, u + s + a + o))) : o <= a && s <= a && o <= s ? (i = new Uint8Array(l.slice(o, p + o)),
        r = new Uint8Array(l.slice(p + s + o, p + c + s + o)),
        n = new Uint8Array(l.slice(p + c + s + o + a, u + s + a + o))) : a <= o && o <= s && a <= s ? (n = new Uint8Array(l.slice(a, h + a)),
        i = new Uint8Array(l.slice(h + a + o, p + h + a + o)),
        r = new Uint8Array(l.slice(p + h + s + o + a, u + s + a + o))) : a <= s && s <= o && a <= o ? (n = new Uint8Array(l.slice(a, h + a)),
        r = new Uint8Array(l.slice(h + a + s, h + c + a + s)),
        i = new Uint8Array(l.slice(h + c + s + o + a, u + s + a + o))) : s <= o && o <= a && s <= a ? (r = new Uint8Array(l.slice(s, c + s)),
        i = new Uint8Array(l.slice(c + s + o, p + c + s + o)),
        n = new Uint8Array(l.slice(p + c + s + o + a, u + s + a + o))) : s <= a && a <= o && s <= o && (r = new Uint8Array(l.slice(s, c + s)),
        n = new Uint8Array(l.slice(c + s + a, c + h + s + a)),
        i = new Uint8Array(l.slice(c + h + s + o + a, u + s + a + o)));
        let f = new Uint8Array(u);
        return f.set(r, 0),
        f.set(n, c),
        f.set(i, h + c),
        function() {
            const t = navigator.userAgent;
            return t.indexOf("Trident") > -1 && t.indexOf("rv:11.0") > -1
        }() ? [].slice.call(f) : f.buffer
    }
      , gt = ({url: t, params: e})=>{
        if (!e || 0 === Object.keys(e).length)
            return t;
        const r = -1 !== t.indexOf("?");
        return `${t}${r ? "&" : "?"}${(t=>{
            var e = [];
            for (var r in t)
                e.push(null === t[r] ? r : r + "=" + t[r]);
            return e.join("&")
        }
        )(e)}`
    }
      , xt = t=>{
        const e = {};
        if (-1 !== t.indexOf("?")) {
            const r = t.split("?");
            e.url = r[0],
            e.params = (t=>{
                var e = t.split("&")
                  , r = {};
                for (let t = 0; t < e.length; t++)
                    if (e[t].indexOf("=") >= 0) {
                        let n = e[t].split("=");
                        r[n[0]] = n[1];
                    } else
                        r[e[t]] = null;
                return r
            }
            )(r[1]);
        } else
            e.url = t,
            e.params = {};
        return e
    }
      , vt = t=>{
        window.__MAP_ISDEV && console.log(t);
    }
      , bt = {
        _Jm(t, e) {
            for (var r, n = [], i = [0, 0], s = 0, a = bt._w(t); s < a; ++s)
                r = e ? e(t[s]) : t[s],
                bt._zh(r[0] - i[0], n),
                bt._zh(r[1] - i[1], n),
                i = r;
            return n.join("")
        },
        _zh: (t,e)=>bt._Km(0 > t ? ~(t << 1) : t << 1, e),
        _Km(t, e) {
            for (; 32 <= t; )
                e.push(String.fromCharCode(63 + (32 | 31 & t))),
                t >>= 5;
            return e.push(String.fromCharCode(t + 63)),
            e
        },
        _w: t=>t ? t.length : 0,
        _F(t, e, r) {
            if (t && (void 0 !== t.lat || void 0 !== t.lng))
                try {
                    Ac(t),
                    e = t.lng,
                    t = t.lat,
                    r = !1;
                } catch (t) {
                    _.oc(t);
                }
            return t -= 0,
            e -= 0,
            r || (t = bt._fb(t, -90, 90),
            180 != e && (e = bt._gb(e, -180, 180))),
            t || e
        },
        _fb: (t,e,r)=>(null != e && (t = Math.max(t, e)),
        null != r && (t = Math.min(t, r)),
        t),
        _gb: (t,e,r)=>((t - e) % (r -= e) + r) % r + e
    }
      , _t = function(t) {
        if ("string" == typeof t)
            return (t=>{
                for (var e = [], r = bt._w(t), n = Array(Math.floor(t.length / 2)), i = 0, s = 0, a = 0, o = 0; i < r; ++o) {
                    var l = 1
                      , u = 0;
                    do {
                        var c = t.charCodeAt(i++) - 63 - 1;
                        l += c << u,
                        u += 5;
                    } while (31 <= c);
                    s += 1 & l ? ~(l >> 1) : l >> 1,
                    l = 1,
                    u = 0;
                    do {
                        l += (c = t.charCodeAt(i++) - 63 - 1) << u,
                        u += 5;
                    } while (31 <= c);
                    n[o] = bt._F(1e-5 * s, 1e-5 * (a += 1 & l ? ~(l >> 1) : l >> 1), !0),
                    e.push([1e-5 * a, 1e-5 * s]);
                }
                return n.length = o,
                e.length > 1 ? e : e[0]
            }
            )(t);
        if (Array.isArray(t))
            return t.map((t=>_t(t)));
        throw new Error("shape.coordinates参数格不正确")
    }
      , wt = (t,e,r,n)=>{
        if (!n || !e || null == r || null == r)
            return t || {};
        var i = t.styleid
          , s = t.shieldType
          , a = 0;
        if (!i && !s)
            return t || {};
        if (!e[i] && !e["40001:" + s])
            return null;
        var o = r + 1;
        if (o = o <= 3 ? 3 : o >= 20 ? 20 : o,
        i && e[i]) {
            let r = Object.keys(e[i]);
            for (let n = 0; n < r.length; n++) {
                let s = r[n];
                if ("type" != s && (s = s.split(","),
                s.indexOf(o) >= 0 || s.indexOf(String(o)) >= 0)) {
                    a = 1,
                    t = v(t, e[i][r[n]]);
                    break
                }
            }
        }
        if (s && e["40001:" + s]) {
            let r = Object.keys(e["40001:" + s]);
            for (let n = 0; n < r.length; n++) {
                let i = r[n];
                if ("type" != i && (i = i.split(","),
                i.indexOf(o) >= 0 || i.indexOf(String(o)) >= 0)) {
                    a = 1,
                    t = v(t, e["40001:" + s][r[n]]);
                    break
                }
            }
        }
        return 0 == a ? null : t
    }
    ;
    let At = [];
    const kt = function(t) {
        return At.indexOf(t) >= 0
    }
      , zt = {
        Unknown: "Unknown",
        Style: "Style",
        Source: "Source",
        Tile: "Tile",
        Glyphs: "Glyphs",
        SpriteImage: "SpriteImage",
        SpriteJSON: "SpriteJSON",
        Image: "Image"
    };
    "function" == typeof Object.freeze && Object.freeze(zt);
    class St extends Error {
        constructor(t, e, r) {
            401 === e && et(r) && (t += ": you may have provided an invalid sgmap access token. See https://map.sgcc.com.cn/products/js-sdk/v3/#"),
            super(t),
            this.status = e,
            this.url = r;
        }
        toString() {
            return `${this.name}: ${this.message} (${this.status}): ${this.url}`
        }
    }
    const Mt = P() ? ()=>self.worker && self.worker.referrer : ()=>("blob:" === e.location.protocol ? e.parent : e).location.href
      , It = t=>/^file:/.test(t) || /^file:/.test(Mt()) && !/^\w+:/.test(t);
    function Tt(t, r) {
        const n = new e.AbortController
          , i = new e.Request(t.url,{
            method: t.method || "GET",
            body: t.body,
            credentials: t.credentials,
            headers: t.headers,
            referrer: Mt(),
            signal: n.signal
        });
        let s = !1
          , a = !1;
        const o = (l = i.url).indexOf("sku=") > 0 && et(l);
        var l;
        "json" === t.type && i.headers.set("Accept", "application/json");
        const u = (n,s,l)=>{
            if (a)
                return;
            if (n && "SecurityError" !== n.message && B(n),
            s && l)
                return c(s);
            const u = Date.now();
            e.fetch(i).then((e=>{
                if (e.ok) {
                    const t = o ? e.clone() : null;
                    return c(e, t, u)
                }
                return r(new St(e.statusText,e.status,t.url))
            }
            )).catch((t=>{
                20 !== t.code && r(new Error(t.message));
            }
            ));
        }
          , c = (n,o,l)=>{
            ("arrayBuffer" === t.type ? n.arrayBuffer() : "json" === t.type ? n.json() : n.text()).then((t=>{
                a || (o && l && function(t, r, n) {
                    const i = ct(t.url);
                    if (pt(i),
                    !ut[i])
                        return;
                    const s = {
                        status: r.status,
                        statusText: r.statusText,
                        headers: new e.Headers
                    };
                    r.headers.forEach(((t,e)=>s.headers.set(e, t)));
                    const a = D(r.headers.get("Cache-Control") || "");
                    if (a["no-store"])
                        return;
                    a["max-age"] && s.headers.set("Expires", new Date(n + 1e3 * a["max-age"]).toUTCString());
                    const o = s.headers.get("Expires");
                    o && (new Date(o).getTime() - n < 42e4 || function(t, e) {
                        if (void 0 === at)
                            try {
                                new Response(new ReadableStream),
                                at = !0;
                            } catch (t) {
                                at = !1;
                            }
                        at ? e(t.body) : t.blob().then(e);
                    }(r, (r=>{
                        const n = new e.Response(r,s);
                        pt(i),
                        ut[i] && ut[i].then((e=>e.put(dt(t.url), n))).catch((t=>B(t.message)));
                    }
                    )));
                }(i, o, l),
                s = !0,
                r(null, t, n.headers.get("Cache-Control"), n.headers.get("Expires")));
            }
            )).catch((t=>{
                a || r(new Error(t.message));
            }
            ));
        }
        ;
        return o ? function(t, e) {
            const r = ct(t.url);
            if (pt(r),
            !ut[r])
                return e(null);
            const n = dt(t.url);
            ut[r].then((t=>{
                t.match(n).then((r=>{
                    const i = function(t) {
                        if (!t)
                            return !1;
                        const e = new Date(t.headers.get("Expires") || 0)
                          , r = D(t.headers.get("Cache-Control") || "");
                        return e > Date.now() && !r["no-cache"]
                    }(r);
                    t.delete(n),
                    i && t.put(n, r.clone()),
                    e(null, r, i);
                }
                )).catch(e);
            }
            )).catch(e);
        }(i, u) : u(null, null),
        {
            cancel: ()=>{
                a = !0,
                s || n.abort();
            }
        }
    }
    function Bt(t, r) {
        const n = new e.XMLHttpRequest;
        n.open(t.method || "GET", t.url, !0),
        "arrayBuffer" === t.type && (n.responseType = "arraybuffer");
        for (const e in t.headers)
            n.setRequestHeader(e, t.headers[e]);
        return "json" === t.type && (n.responseType = "text",
        n.setRequestHeader("Accept", "application/json")),
        n.withCredentials = "include" === t.credentials,
        n.onerror = ()=>{
            r(new Error(n.statusText));
        }
        ,
        n.onload = ()=>{
            if ((n.status >= 200 && n.status < 300 || 0 === n.status) && null !== n.response) {
                let e = n.response;
                if ("json" === t.type)
                    try {
                        e = JSON.parse(n.response);
                    } catch (t) {
                        return r(t)
                    }
                r(null, e, n.getResponseHeader("Cache-Control"), n.getResponseHeader("Expires"));
            } else
                r(new St(n.statusText,n.status,t.url));
        }
        ,
        n.send(t.body),
        {
            cancel: ()=>n.abort()
        }
    }
    const Ct = function(t, r) {
        const n = xt(t.url)
          , {access_token: i} = n.params;
        if (void 0 === t.cache && (t.cache = !0),
        i && (delete n.params.access_token,
        t.headers || (t.headers = {}),
        t.headers.Authorization = i),
        t.url = gt(n),
        !It(t.url)) {
            if (e.fetch && e.Request && e.AbortController && e.Request.prototype.hasOwnProperty("signal"))
                return Tt(t, r);
            if (P() && self.worker && self.worker.actor)
                return self.worker.actor.send("getResource", t, r, void 0, !0)
        }
        return Bt(t, r)
    }
      , Vt = function(t, e) {
        const {tilesecurity: r, zxy: n} = t;
        return delete t.zxy,
        delete t.tilesecurity,
        Ct(v(t, {
            type: "arrayBuffer"
        }), ((t,i,s,a)=>{
            !t && i && r && (i = mt(n, i)),
            e(t, i, s, a);
        }
        ))
    };
    function Pt(t) {
        const r = e.document.createElement("a");
        return r.href = t,
        r.protocol === e.document.location.protocol && r.host === e.document.location.host
    }
    const Dt = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQYV2NgAAIAAAUAAarVyFEAAAAASUVORK5CYII=";
    let Et, Ft;
    Et = [],
    Ft = 0;
    const Lt = function(t, r) {
        if (G.supported && (t.headers || (t.headers = {}),
        t.headers.accept = "image/webp,*/*"),
        Ft >= Z.MAX_PARALLEL_IMAGE_REQUESTS) {
            const e = {
                requestParameters: t,
                callback: r,
                cancelled: !1,
                cancel() {
                    this.cancelled = !0;
                }
            };
            return Et.push(e),
            e
        }
        Ft++;
        let n = !1;
        const i = ()=>{
            if (!n)
                for (n = !0,
                Ft--; Et.length && Ft < Z.MAX_PARALLEL_IMAGE_REQUESTS; ) {
                    const t = Et.shift()
                      , {requestParameters: e, callback: r, cancelled: n} = t;
                    n || (t.cancel = Lt(e, r).cancel);
                }
        }
          , s = Vt(t, ((t,n,s,a)=>{
            i(),
            t ? r(t) : n && (e.createImageBitmap ? function(t, r) {
                const n = new e.Blob([new Uint8Array(t)],{
                    type: "image/png"
                });
                e.createImageBitmap(n).then((t=>{
                    r(null, t);
                }
                )).catch((t=>{
                    r(new Error(`Could not load image because of ${t.message}. Please make sure to use a supported image type such as PNG or JPEG. Note that SVGs are not supported.`));
                }
                ));
            }(n, ((t,e)=>r(t, e, s, a))) : function(t, r) {
                const n = new e.Image
                  , i = e.URL;
                n.onload = ()=>{
                    r(null, n),
                    i.revokeObjectURL(n.src),
                    n.onload = null,
                    e.requestAnimationFrame((()=>{
                        n.src = Dt;
                    }
                    ));
                }
                ,
                n.onerror = ()=>r(new Error("Could not load image. Please make sure to use a supported image type such as PNG or JPEG. Note that SVGs are not supported."));
                const s = new e.Blob([new Uint8Array(t)],{
                    type: "image/png"
                });
                n.src = t.byteLength ? i.createObjectURL(s) : Dt;
            }(n, ((t,e)=>r(t, e, s, a))));
        }
        ));
        return {
            cancel: ()=>{
                s.cancel(),
                i();
            }
        }
    };
    function Rt(t, e, r) {
        r[t] && -1 !== r[t].indexOf(e) || (r[t] = r[t] || [],
        r[t].push(e));
    }
    function jt(t, e, r) {
        if (r && r[t]) {
            const n = r[t].indexOf(e);
            -1 !== n && r[t].splice(n, 1);
        }
    }
    class Ut {
        constructor(t, e={}) {
            v(this, e),
            this.type = t;
        }
    }
    class Ot extends Ut {
        constructor(t, e={}) {
            super("error", v({
                error: t
            }, e));
        }
    }
    class $t {
        on(t, e) {
            return this._listeners = this._listeners || {},
            Rt(t, e, this._listeners),
            this
        }
        off(t, e) {
            return jt(t, e, this._listeners),
            jt(t, e, this._oneTimeListeners),
            this
        }
        once(t, e) {
            return e ? (this._oneTimeListeners = this._oneTimeListeners || {},
            Rt(t, e, this._oneTimeListeners),
            this) : new Promise((e=>this.once(t, e)))
        }
        fire(t, e) {
            "string" == typeof t && (t = new Ut(t,e || {}));
            const r = t.type;
            if (this.listens(r)) {
                t.target = this;
                const e = this._listeners && this._listeners[r] ? this._listeners[r].slice() : [];
                for (const r of e)
                    r.call(this, t);
                const n = this._oneTimeListeners && this._oneTimeListeners[r] ? this._oneTimeListeners[r].slice() : [];
                for (const e of n)
                    jt(r, e, this._oneTimeListeners),
                    e.call(this, t);
                const i = this._eventedParent;
                i && (v(t, "function" == typeof this._eventedParentData ? this._eventedParentData() : this._eventedParentData),
                i.fire(t));
            } else
                t instanceof Ot && console.error(t.error);
            return this
        }
        listens(t) {
            return !!(this._listeners && this._listeners[t] && this._listeners[t].length > 0 || this._oneTimeListeners && this._oneTimeListeners[t] && this._oneTimeListeners[t].length > 0 || this._eventedParent && this._eventedParent.listens(t))
        }
        setEventedParent(t, e) {
            return this._eventedParent = t,
            this._eventedParentData = e,
            this
        }
    }
    var qt = JSON.parse('{"$version":8,"$root":{"version":{"required":true,"type":"enum","values":[8]},"name":{"type":"string"},"metadata":{"type":"*"},"center":{"type":"array","value":"number"},"zoom":{"type":"number"},"bearing":{"type":"number","default":0,"period":360,"units":"degrees"},"pitch":{"type":"number","default":0,"units":"degrees"},"light":{"type":"light"},"terrain":{"type":"terrain"},"fog":{"type":"fog"},"sources":{"required":true,"type":"sources"},"sprite":{"type":"string"},"glyphs":{"type":"string"},"transition":{"type":"transition"},"projection":{"type":"projection"},"layers":{"required":true,"type":"array","value":"layer"}},"sources":{"*":{"type":"source"}},"source":["source_vector","source_raster","source_raster_dem","source_geojson","source_video","source_image"],"source_vector":{"type":{"required":true,"type":"enum","values":{"vector":{}}},"url":{"type":"string"},"tiles":{"type":"array","value":"string"},"bounds":{"type":"array","value":"number","length":4,"default":[-180,-85.051129,180,85.051129]},"scheme":{"type":"enum","values":{"xyz":{},"tms":{}},"default":"xyz"},"minzoom":{"type":"number","default":0},"maxzoom":{"type":"number","default":22},"attribution":{"type":"string"},"promoteId":{"type":"promoteId"},"volatile":{"type":"boolean","default":false},"*":{"type":"*"}},"source_raster":{"type":{"required":true,"type":"enum","values":{"raster":{}}},"url":{"type":"string"},"tiles":{"type":"array","value":"string"},"bounds":{"type":"array","value":"number","length":4,"default":[-180,-85.051129,180,85.051129]},"minzoom":{"type":"number","default":0},"maxzoom":{"type":"number","default":22},"tileSize":{"type":"number","default":512,"units":"pixels"},"scheme":{"type":"enum","values":{"xyz":{},"tms":{}},"default":"xyz"},"attribution":{"type":"string"},"volatile":{"type":"boolean","default":false},"*":{"type":"*"}},"source_raster_dem":{"type":{"required":true,"type":"enum","values":{"raster-dem":{}}},"url":{"type":"string"},"tiles":{"type":"array","value":"string"},"bounds":{"type":"array","value":"number","length":4,"default":[-180,-85.051129,180,85.051129]},"minzoom":{"type":"number","default":0},"maxzoom":{"type":"number","default":22},"tileSize":{"type":"number","default":512,"units":"pixels"},"attribution":{"type":"string"},"encoding":{"type":"enum","values":{"terrarium":{},"sgmap":{},"epgis":{}},"default":"epgis"},"volatile":{"type":"boolean","default":false},"*":{"type":"*"}},"source_geojson":{"type":{"required":true,"type":"enum","values":{"geojson":{}}},"data":{"type":"*"},"maxzoom":{"type":"number","default":18},"attribution":{"type":"string"},"buffer":{"type":"number","default":128,"maximum":512,"minimum":0},"filter":{"type":"*"},"tolerance":{"type":"number","default":0.375},"cluster":{"type":"boolean","default":false},"clusterRadius":{"type":"number","default":50,"minimum":0},"clusterMaxZoom":{"type":"number"},"clusterMinPoints":{"type":"number"},"clusterProperties":{"type":"*"},"lineMetrics":{"type":"boolean","default":false},"generateId":{"type":"boolean","default":false},"promoteId":{"type":"promoteId"}},"source_video":{"type":{"required":true,"type":"enum","values":{"video":{}}},"urls":{"required":true,"type":"array","value":"string"},"coordinates":{"required":true,"type":"array","length":4,"value":{"type":"array","length":2,"value":"number"}}},"source_image":{"type":{"required":true,"type":"enum","values":{"image":{}}},"url":{"required":true,"type":"string"},"coordinates":{"required":true,"type":"array","length":4,"value":{"type":"array","length":2,"value":"number"}}},"layer":{"id":{"type":"string","required":true},"type":{"type":"enum","values":{"fill":{},"line":{},"symbol":{},"circle":{},"esymbol":{},"eline":{},"heatmap":{},"fill-extrusion":{},"raster":{},"hillshade":{},"background":{},"sky":{}},"required":true},"metadata":{"type":"*"},"source":{"type":"string"},"source-layer":{"type":"string"},"minzoom":{"type":"number","minimum":0,"maximum":24},"maxzoom":{"type":"number","minimum":0,"maximum":24},"filter":{"type":"filter"},"layout":{"type":"layout"},"paint":{"type":"paint"}},"layout":["layout_fill","layout_line","layout_circle","layout_heatmap","layout_fill-extrusion","layout_symbol","layout_raster","layout_hillshade","layout_background","layout_sky","layout_esymbol"],"layout_background":{"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_sky":{"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_fill":{"fill-sort-key":{"type":"number","expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_circle":{"circle-sort-key":{"type":"number","expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_heatmap":{"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_fill-extrusion":{"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"},"fill-extrusion-edge-radius":{"type":"number","private":true,"default":0,"minimum":0,"maximum":1,"property-type":"constant"}},"layout_line":{"esymbol-id":{"type":"string","tokens":true,"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"line-cap":{"type":"enum","values":{"butt":{},"round":{},"square":{}},"default":"butt","expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"line-join":{"type":"enum","values":{"bevel":{},"round":{},"miter":{}},"default":"miter","expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"line-miter-limit":{"type":"number","default":2,"requires":[{"line-join":"miter"}],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"line-round-limit":{"type":"number","default":1.05,"requires":[{"line-join":"round"}],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"line-sort-key":{"type":"number","expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_symbol":{"symbol-scaleable":{"type":"boolean","default":false,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"symbol-placement":{"type":"enum","values":{"point":{},"line":{},"line-center":{}},"default":"point","expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"symbol-spacing":{"type":"number","default":250,"minimum":1,"units":"pixels","requires":[{"symbol-placement":"line"}],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"symbol-avoid-edges":{"type":"boolean","default":false,"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"symbol-sort-key":{"type":"number","expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"symbol-z-order":{"type":"enum","values":{"auto":{},"viewport-y":{},"source":{}},"default":"auto","expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"icon-allow-overlap":{"type":"boolean","default":false,"requires":["icon-image"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"icon-ignore-placement":{"type":"boolean","default":false,"requires":["icon-image"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"icon-optional":{"type":"boolean","default":false,"requires":["icon-image","text-field"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"icon-rotation-alignment":{"type":"enum","values":{"map":{},"viewport":{},"auto":{}},"default":"auto","requires":["icon-image"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"icon-size":{"type":"number","default":1,"minimum":0,"units":"factor of the original icon size","requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"icon-text-fit":{"type":"enum","values":{"none":{},"width":{},"height":{},"both":{}},"default":"none","requires":["icon-image","text-field"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"icon-text-fit-padding":{"type":"array","value":"number","length":4,"default":[0,0,0,0],"units":"pixels","requires":["icon-image","text-field",{"icon-text-fit":["both","width","height"]}],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"icon-image":{"type":"resolvedImage","tokens":true,"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"icon-rotate":{"type":"number","default":0,"period":360,"units":"degrees","requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"icon-padding":{"type":"number","default":2,"minimum":0,"units":"pixels","requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"icon-keep-upright":{"type":"boolean","default":false,"requires":["icon-image",{"icon-rotation-alignment":"map"},{"symbol-placement":["line","line-center"]}],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"icon-offset":{"type":"array","value":"number","length":2,"default":[0,0],"requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"icon-anchor":{"type":"enum","values":{"center":{},"left":{},"right":{},"top":{},"bottom":{},"top-left":{},"top-right":{},"bottom-left":{},"bottom-right":{}},"default":"center","requires":["icon-image"],"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"icon-pitch-alignment":{"type":"enum","values":{"map":{},"viewport":{},"auto":{}},"default":"auto","requires":["icon-image"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-pitch-alignment":{"type":"enum","values":{"map":{},"viewport":{},"auto":{}},"default":"auto","requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-rotation-alignment":{"type":"enum","values":{"map":{},"viewport":{},"auto":{}},"default":"auto","requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-field":{"type":"formatted","default":"","tokens":true,"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-font":{"type":"array","value":"string","default":["Microsoft YaHei Regular"],"requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-size":{"type":"number","default":16,"minimum":0,"units":"pixels","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-max-width":{"type":"number","default":10,"minimum":0,"units":"ems","requires":["text-field",{"symbol-placement":["point"]}],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-line-height":{"type":"number","default":1.2,"units":"ems","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-letter-spacing":{"type":"number","default":0,"units":"ems","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-justify":{"type":"enum","values":{"auto":{},"left":{},"center":{},"right":{}},"default":"center","requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-radial-offset":{"type":"number","units":"ems","default":0,"requires":["text-field"],"property-type":"data-driven","expression":{"interpolated":true,"parameters":["zoom","feature"]}},"text-variable-anchor":{"type":"array","value":"enum","values":{"center":{},"left":{},"right":{},"top":{},"bottom":{},"top-left":{},"top-right":{},"bottom-left":{},"bottom-right":{}},"requires":["text-field",{"symbol-placement":["point"]}],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-anchor":{"type":"enum","values":{"center":{},"left":{},"right":{},"top":{},"bottom":{},"top-left":{},"top-right":{},"bottom-left":{},"bottom-right":{}},"default":"center","requires":["text-field",{"!":"text-variable-anchor"}],"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-max-angle":{"type":"number","default":45,"units":"degrees","requires":["text-field",{"symbol-placement":["line","line-center"]}],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"text-writing-mode":{"type":"array","value":"enum","values":{"horizontal":{},"vertical":{}},"requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-rotate":{"type":"number","default":0,"period":360,"units":"degrees","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-padding":{"type":"number","default":2,"minimum":0,"units":"pixels","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"text-keep-upright":{"type":"boolean","default":true,"requires":["text-field",{"text-rotation-alignment":"map"},{"symbol-placement":["line","line-center"]}],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-transform":{"type":"enum","values":{"none":{},"uppercase":{},"lowercase":{}},"default":"none","requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-offset":{"type":"array","value":"number","units":"ems","length":2,"default":[0,0],"requires":["text-field",{"!":"text-radial-offset"}],"expression":{"interpolated":true,"parameters":["zoom","feature"]},"property-type":"data-driven"},"text-allow-overlap":{"type":"boolean","default":false,"requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-ignore-placement":{"type":"boolean","default":false,"requires":["text-field"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-optional":{"type":"boolean","default":false,"requires":["text-field","icon-image"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_esymbol":{"esymbol-scaleable":{"type":"boolean","default":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-size":{"type":"number","default":1,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-rotate":{"type":"number","default":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-id":{"type":"string","tokens":true,"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"esymbol-sort-key":{"type":"number","expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"data-driven"},"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_raster":{"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"layout_hillshade":{"visibility":{"type":"enum","values":{"visible":{},"none":{}},"default":"visible","property-type":"constant"}},"filter":{"type":"array","value":"*"},"filter_symbol":{"type":"boolean","default":false,"transition":false,"property-type":"data-driven","expression":{"interpolated":false,"parameters":["zoom","feature","pitch","distance-from-center"]}},"filter_fill":{"type":"boolean","default":false,"transition":false,"property-type":"data-driven","expression":{"interpolated":false,"parameters":["zoom","feature"]}},"filter_line":{"type":"boolean","default":false,"transition":false,"property-type":"data-driven","expression":{"interpolated":false,"parameters":["zoom","feature"]}},"filter_circle":{"type":"boolean","default":false,"transition":false,"property-type":"data-driven","expression":{"interpolated":false,"parameters":["zoom","feature"]}},"filter_fill-extrusion":{"type":"boolean","default":false,"transition":false,"property-type":"data-driven","expression":{"interpolated":false,"parameters":["zoom","feature"]}},"filter_heatmap":{"type":"boolean","default":false,"transition":false,"property-type":"data-driven","expression":{"interpolated":false,"parameters":["zoom","feature"]}},"filter_operator":{"type":"enum","values":{"==":{},"!=":{},">":{},">=":{},"<":{},"<=":{},"in":{},"!in":{},"all":{},"any":{},"none":{},"has":{},"!has":{},"within":{}}},"geometry_type":{"type":"enum","values":{"Point":{},"LineString":{},"Polygon":{}}},"function":{"expression":{"type":"expression"},"stops":{"type":"array","value":"function_stop"},"base":{"type":"number","default":1,"minimum":0},"property":{"type":"string","default":"$zoom"},"type":{"type":"enum","values":{"identity":{},"exponential":{},"interval":{},"categorical":{}},"default":"exponential"},"colorSpace":{"type":"enum","values":{"rgb":{},"lab":{},"hcl":{}},"default":"rgb"},"default":{"type":"*","required":false}},"function_stop":{"type":"array","minimum":0,"maximum":24,"value":["number","color"],"length":2},"expression":{"type":"array","value":"*","minimum":1},"fog":{"range":{"type":"array","default":[0.5,10],"minimum":-20,"maximum":20,"length":2,"value":"number","property-type":"data-constant","transition":true,"expression":{"interpolated":true,"parameters":["zoom"]}},"color":{"type":"color","property-type":"data-constant","default":"#ffffff","expression":{"interpolated":true,"parameters":["zoom"]},"transition":true},"high-color":{"type":"color","property-type":"data-constant","default":"#245cdf","expression":{"interpolated":true,"parameters":["zoom"]},"transition":true},"space-color":{"type":"color","property-type":"data-constant","default":["interpolate",["linear"],["zoom"],4,"#010b19",7,"#367ab9"],"expression":{"interpolated":true,"parameters":["zoom"]},"transition":true},"horizon-blend":{"type":"number","property-type":"data-constant","default":["interpolate",["linear"],["zoom"],4,0.2,7,0.1],"minimum":0,"maximum":1,"expression":{"interpolated":true,"parameters":["zoom"]},"transition":true},"star-intensity":{"type":"number","property-type":"data-constant","default":["interpolate",["linear"],["zoom"],5,0.35,6,0],"minimum":0,"maximum":1,"expression":{"interpolated":true,"parameters":["zoom"]},"transition":true}},"light":{"anchor":{"type":"enum","default":"viewport","values":{"map":{},"viewport":{}},"property-type":"data-constant","transition":false,"expression":{"interpolated":false,"parameters":["zoom"]}},"position":{"type":"array","default":[1.15,210,30],"length":3,"value":"number","property-type":"data-constant","transition":true,"expression":{"interpolated":true,"parameters":["zoom"]}},"color":{"type":"color","property-type":"data-constant","default":"#ffffff","expression":{"interpolated":true,"parameters":["zoom"]},"transition":true},"intensity":{"type":"number","property-type":"data-constant","default":0.5,"minimum":0,"maximum":1,"expression":{"interpolated":true,"parameters":["zoom"]},"transition":true}},"projection":{"name":{"type":"enum","values":{"albers":{},"equalEarth":{},"equirectangular":{},"lambertConformalConic":{},"mercator":{},"naturalEarth":{},"winkelTripel":{},"globe":{}},"default":"mercator","required":true},"center":{"type":"array","length":2,"value":"number","property-type":"data-constant","minimum":[-180,-90],"maximum":[180,90],"transition":false,"requires":[{"name":["albers","lambertConformalConic"]}]},"parallels":{"type":"array","length":2,"value":"number","property-type":"data-constant","minimum":[-90,-90],"maximum":[90,90],"transition":false,"requires":[{"name":["albers","lambertConformalConic"]}]}},"terrain":{"source":{"type":"string","required":true},"exaggeration":{"type":"number","property-type":"data-constant","default":1,"minimum":0,"maximum":1000,"expression":{"interpolated":true,"parameters":["zoom"]},"transition":true,"requires":["source"]}},"paint":["paint_fill","paint_line","paint_circle","paint_heatmap","paint_fill-extrusion","paint_symbol","paint_raster","paint_hillshade","paint_background","paint_sky","paint_esymbol"],"paint_fill":{"fill-minzoom":{"type":"number","default":0,"minimum":0,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-maxzoom":{"type":"number","default":24,"minimum":1,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-antialias":{"type":"boolean","default":true,"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"fill-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-color":{"type":"color","default":"#000000","transition":true,"requires":[{"!":"fill-pattern"}],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-outline-color":{"type":"color","transition":true,"requires":[{"!":"fill-pattern"},{"fill-antialias":true}],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-translate":{"type":"array","value":"number","length":2,"default":[0,0],"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"fill-translate-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","requires":["fill-translate"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"fill-pattern":{"type":"resolvedImage","transition":true,"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"cross-faded-data-driven"}},"paint_fill-extrusion":{"fill-extrusion-minzoom":{"type":"number","default":0,"minimum":0,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-extrusion-maxzoom":{"type":"number","default":24,"minimum":1,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-extrusion-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"fill-extrusion-color":{"type":"color","default":"#000000","transition":true,"requires":[{"!":"fill-extrusion-pattern"}],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-extrusion-topcolor":{"type":"color","default":"rgba(0,0,0,0)","transition":true,"requires":[{"!":"fill-extrusion-pattern"}],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-extrusion-translate":{"type":"array","value":"number","length":2,"default":[0,0],"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"fill-extrusion-translate-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","requires":["fill-extrusion-translate"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"fill-extrusion-pattern":{"type":"resolvedImage","transition":true,"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"cross-faded-data-driven"},"fill-extrusion-height":{"type":"number","default":0,"minimum":0,"units":"meters","transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-extrusion-base":{"type":"number","default":0,"minimum":0,"units":"meters","transition":true,"requires":["fill-extrusion-height"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"fill-extrusion-vertical-gradient":{"type":"boolean","default":true,"transition":false,"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"fill-extrusion-ambient-occlusion-intensity":{"property-type":"data-constant","type":"number","private":true,"default":0,"minimum":0,"maximum":1,"expression":{"interpolated":true,"parameters":["zoom"]},"transition":true},"fill-extrusion-ambient-occlusion-radius":{"property-type":"data-constant","type":"number","private":true,"default":3,"minimum":0,"expression":{"interpolated":true,"parameters":["zoom"]},"transition":true}},"paint_line":{"line-minzoom":{"type":"number","default":0,"minimum":0,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-maxzoom":{"type":"number","default":24,"minimum":1,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-color":{"type":"color","default":"#000000","transition":true,"requires":[{"!":"line-pattern"}],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-outline-color":{"type":"color","default":"#000000","transition":true,"requires":[{"!":"line-pattern"}],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-translate":{"type":"array","value":"number","length":2,"default":[0,0],"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"line-translate-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","requires":["line-translate"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"line-width":{"type":"number","default":1,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-outline-width":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-gap-width":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-offset":{"type":"number","default":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-blur":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"line-dasharray":{"type":"array","value":"number","minimum":0,"transition":true,"units":"line widths","requires":[{"!":"line-pattern"}],"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"cross-faded-data-driven"},"line-outline-dasharray":{"type":"array","value":"number","minimum":0,"transition":true,"units":"line widths","requires":[{"!":"line-pattern"}],"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"cross-faded-data-driven"},"line-pattern":{"type":"resolvedImage","transition":true,"expression":{"interpolated":false,"parameters":["zoom","feature"]},"property-type":"cross-faded-data-driven"},"line-pattern-color":{"type":"boolean","default":false,"requires":["line-pattern","line-color"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"line-gradient":{"type":"color","transition":false,"requires":[{"!":"line-pattern"},{"source":"geojson","has":{"lineMetrics":true}}],"expression":{"interpolated":true,"parameters":["line-progress"]},"property-type":"color-ramp"},"line-trim-offset":{"type":"array","value":"number","length":2,"default":[0,0],"minimum":[0,0],"maximum":[1,1],"transition":false,"requires":[{"source":"geojson","has":{"lineMetrics":true}}],"property-type":"constant"}},"paint_circle":{"circle-minzoom":{"type":"number","default":0,"minimum":0,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-maxzoom":{"type":"number","default":24,"minimum":1,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-radius":{"type":"number","default":5,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-color":{"type":"color","default":"#000000","transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-blur":{"type":"number","default":0,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-translate":{"type":"array","value":"number","length":2,"default":[0,0],"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"circle-translate-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","requires":["circle-translate"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"circle-pitch-scale":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"circle-pitch-alignment":{"type":"enum","values":{"map":{},"viewport":{}},"default":"viewport","expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"circle-stroke-width":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-stroke-color":{"type":"color","default":"#000000","transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"circle-stroke-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"}},"paint_esymbol":{"esymbol-minzoom":{"type":"number","default":0,"minimum":0,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-maxzoom":{"type":"number","default":24,"minimum":1,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-radius":{"type":"number","default":40,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-color":{"type":"color","default":"#b84842","transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-blur":{"type":"number","default":0,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-translate":{"type":"array","value":"number","length":2,"default":[0,0],"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"esymbol-translate-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","requires":["circle-translate"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"esymbol-stroke-width":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-stroke-color":{"type":"color","default":"#000000","transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"esymbol-stroke-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"}},"paint_heatmap":{"heatmap-radius":{"type":"number","default":30,"minimum":1,"transition":true,"units":"pixels","expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"heatmap-weight":{"type":"number","default":1,"minimum":0,"transition":false,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"heatmap-intensity":{"type":"number","default":1,"minimum":0,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"heatmap-color":{"type":"color","default":["interpolate",["linear"],["heatmap-density"],0,"rgba(0, 0, 255, 0)",0.1,"royalblue",0.3,"cyan",0.5,"lime",0.7,"yellow",1,"red"],"transition":false,"expression":{"interpolated":true,"parameters":["heatmap-density"]},"property-type":"color-ramp"},"heatmap-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"}},"paint_symbol":{"symbol-minzoom":{"type":"number","default":0,"minimum":0,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"symbol-maxzoom":{"type":"number","default":24,"minimum":1,"maximum":24,"transition":true,"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"icon-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"icon-color":{"type":"color","default":"#000000","transition":true,"requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"icon-halo-color":{"type":"color","default":"rgba(0, 0, 0, 0)","transition":true,"requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"icon-halo-width":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"icon-halo-blur":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"icon-translate":{"type":"array","value":"number","length":2,"default":[0,0],"transition":true,"units":"pixels","requires":["icon-image"],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"icon-translate-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","requires":["icon-image","icon-translate"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"text-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"text-color":{"type":"color","default":"#000000","transition":true,"overridable":true,"requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"text-halo-color":{"type":"color","default":"rgba(0, 0, 0, 0)","transition":true,"requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"text-halo-width":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"text-halo-blur":{"type":"number","default":0,"minimum":0,"transition":true,"units":"pixels","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom","feature","feature-state"]},"property-type":"data-driven"},"text-translate":{"type":"array","value":"number","length":2,"default":[0,0],"transition":true,"units":"pixels","requires":["text-field"],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"text-translate-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"map","requires":["text-field","text-translate"],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"}},"paint_raster":{"raster-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"raster-hue-rotate":{"type":"number","default":0,"period":360,"transition":true,"units":"degrees","expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"raster-brightness-min":{"type":"number","default":0,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"raster-brightness-max":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"raster-saturation":{"type":"number","default":0,"minimum":-1,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"raster-contrast":{"type":"number","default":0,"minimum":-1,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"raster-resampling":{"type":"enum","values":{"linear":{},"nearest":{}},"default":"linear","expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"raster-fade-duration":{"type":"number","default":300,"minimum":0,"transition":false,"units":"milliseconds","expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"}},"paint_hillshade":{"hillshade-illumination-direction":{"type":"number","default":335,"minimum":0,"maximum":359,"transition":false,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"hillshade-illumination-anchor":{"type":"enum","values":{"map":{},"viewport":{}},"default":"viewport","expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"hillshade-exaggeration":{"type":"number","default":0.5,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"hillshade-shadow-color":{"type":"color","default":"#000000","transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"hillshade-highlight-color":{"type":"color","default":"#FFFFFF","transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"hillshade-accent-color":{"type":"color","default":"#000000","transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"}},"paint_background":{"background-color":{"type":"color","default":"#000000","transition":true,"requires":[{"!":"background-pattern"}],"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"},"background-pattern":{"type":"resolvedImage","transition":true,"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"cross-faded"},"background-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"}},"paint_sky":{"sky-type":{"type":"enum","values":{"gradient":{},"atmosphere":{}},"default":"atmosphere","expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"sky-atmosphere-sun":{"type":"array","value":"number","length":2,"units":"degrees","minimum":[0,0],"maximum":[360,180],"transition":false,"requires":[{"sky-type":"atmosphere"}],"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"sky-atmosphere-sun-intensity":{"type":"number","requires":[{"sky-type":"atmosphere"}],"default":10,"minimum":0,"maximum":100,"transition":false,"property-type":"data-constant"},"sky-gradient-center":{"type":"array","requires":[{"sky-type":"gradient"}],"value":"number","default":[0,0],"length":2,"units":"degrees","minimum":[0,0],"maximum":[360,180],"transition":false,"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"sky-gradient-radius":{"type":"number","requires":[{"sky-type":"gradient"}],"default":90,"minimum":0,"maximum":180,"transition":false,"expression":{"interpolated":false,"parameters":["zoom"]},"property-type":"data-constant"},"sky-gradient":{"type":"color","default":["interpolate",["linear"],["sky-radial-progress"],0.8,"#87ceeb",1,"white"],"transition":false,"requires":[{"sky-type":"gradient"}],"expression":{"interpolated":true,"parameters":["sky-radial-progress"]},"property-type":"color-ramp"},"sky-atmosphere-halo-color":{"type":"color","default":"white","transition":false,"requires":[{"sky-type":"atmosphere"}],"property-type":"data-constant"},"sky-atmosphere-color":{"type":"color","default":"white","transition":false,"requires":[{"sky-type":"atmosphere"}],"property-type":"data-constant"},"sky-opacity":{"type":"number","default":1,"minimum":0,"maximum":1,"transition":true,"expression":{"interpolated":true,"parameters":["zoom"]},"property-type":"data-constant"}},"transition":{"duration":{"type":"number","default":300,"minimum":0,"units":"milliseconds"},"delay":{"type":"number","default":0,"minimum":0,"units":"milliseconds"}},"property-type":{"data-driven":{"type":"property-type"},"cross-faded":{"type":"property-type"},"cross-faded-data-driven":{"type":"property-type"},"color-ramp":{"type":"property-type"},"data-constant":{"type":"property-type"},"constant":{"type":"property-type"}},"promoteId":{"*":{"type":"string"}}}');
    function Nt(t, ...e) {
        for (const r of e)
            for (const e in r)
                t[e] = r[e];
        return t
    }
    function Zt(t) {
        return t instanceof Number || t instanceof String || t instanceof Boolean ? t.valueOf() : t
    }
    function Gt(t) {
        if (Array.isArray(t))
            return t.map(Gt);
        if (t instanceof Object && !(t instanceof Number || t instanceof String || t instanceof Boolean)) {
            const e = {};
            for (const r in t)
                e[r] = Gt(t[r]);
            return e
        }
        return Zt(t)
    }
    class Xt extends Error {
        constructor(t, e) {
            super(e),
            this.message = e,
            this.key = t;
        }
    }
    var Yt = Xt;
    class Ht {
        constructor(t, e=[]) {
            this.parent = t,
            this.bindings = {};
            for (const [t,r] of e)
                this.bindings[t] = r;
        }
        concat(t) {
            return new Ht(this,t)
        }
        get(t) {
            if (this.bindings[t])
                return this.bindings[t];
            if (this.parent)
                return this.parent.get(t);
            throw new Error(`${t} not found in scope.`)
        }
        has(t) {
            return !!this.bindings[t] || !!this.parent && this.parent.has(t)
        }
    }
    var Kt = Ht;
    const Jt = {
        kind: "null"
    }
      , Wt = {
        kind: "number"
    }
      , Qt = {
        kind: "string"
    }
      , te = {
        kind: "boolean"
    }
      , ee = {
        kind: "color"
    }
      , re = {
        kind: "object"
    }
      , ne = {
        kind: "value"
    }
      , ie = {
        kind: "collator"
    }
      , se = {
        kind: "formatted"
    }
      , ae = {
        kind: "resolvedImage"
    };
    function oe(t, e) {
        return {
            kind: "array",
            itemType: t,
            N: e
        }
    }
    function le(t) {
        if ("array" === t.kind) {
            const e = le(t.itemType);
            return "number" == typeof t.N ? `array<${e}, ${t.N}>` : "value" === t.itemType.kind ? "array" : `array<${e}>`
        }
        return t.kind
    }
    const ue = [Jt, Wt, Qt, te, ee, se, re, oe(ne), ae];
    function ce(t, e) {
        if ("error" === e.kind)
            return null;
        if ("array" === t.kind) {
            if ("array" === e.kind && (0 === e.N && "value" === e.itemType.kind || !ce(t.itemType, e.itemType)) && ("number" != typeof t.N || t.N === e.N))
                return null
        } else {
            if (t.kind === e.kind)
                return null;
            if ("value" === t.kind)
                for (const t of ue)
                    if (!ce(t, e))
                        return null
        }
        return `Expected ${le(t)} but found ${le(e)} instead.`
    }
    function he(t, e) {
        return e.some((e=>e.kind === t.kind))
    }
    function pe(t, e) {
        return e.some((e=>"null" === e ? null === t : "array" === e ? Array.isArray(t) : "object" === e ? t && !Array.isArray(t) && "object" == typeof t : e === typeof t))
    }
    function fe(t) {
        var e = {
            exports: {}
        };
        return t(e, e.exports),
        e.exports
    }
    var de = fe((function(t, e) {
        var r = {
            transparent: [0, 0, 0, 0],
            aliceblue: [240, 248, 255, 1],
            antiquewhite: [250, 235, 215, 1],
            aqua: [0, 255, 255, 1],
            aquamarine: [127, 255, 212, 1],
            azure: [240, 255, 255, 1],
            beige: [245, 245, 220, 1],
            bisque: [255, 228, 196, 1],
            black: [0, 0, 0, 1],
            blanchedalmond: [255, 235, 205, 1],
            blue: [0, 0, 255, 1],
            blueviolet: [138, 43, 226, 1],
            brown: [165, 42, 42, 1],
            burlywood: [222, 184, 135, 1],
            cadetblue: [95, 158, 160, 1],
            chartreuse: [127, 255, 0, 1],
            chocolate: [210, 105, 30, 1],
            coral: [255, 127, 80, 1],
            cornflowerblue: [100, 149, 237, 1],
            cornsilk: [255, 248, 220, 1],
            crimson: [220, 20, 60, 1],
            cyan: [0, 255, 255, 1],
            darkblue: [0, 0, 139, 1],
            darkcyan: [0, 139, 139, 1],
            darkgoldenrod: [184, 134, 11, 1],
            darkgray: [169, 169, 169, 1],
            darkgreen: [0, 100, 0, 1],
            darkgrey: [169, 169, 169, 1],
            darkkhaki: [189, 183, 107, 1],
            darkmagenta: [139, 0, 139, 1],
            darkolivegreen: [85, 107, 47, 1],
            darkorange: [255, 140, 0, 1],
            darkorchid: [153, 50, 204, 1],
            darkred: [139, 0, 0, 1],
            darksalmon: [233, 150, 122, 1],
            darkseagreen: [143, 188, 143, 1],
            darkslateblue: [72, 61, 139, 1],
            darkslategray: [47, 79, 79, 1],
            darkslategrey: [47, 79, 79, 1],
            darkturquoise: [0, 206, 209, 1],
            darkviolet: [148, 0, 211, 1],
            deeppink: [255, 20, 147, 1],
            deepskyblue: [0, 191, 255, 1],
            dimgray: [105, 105, 105, 1],
            dimgrey: [105, 105, 105, 1],
            dodgerblue: [30, 144, 255, 1],
            firebrick: [178, 34, 34, 1],
            floralwhite: [255, 250, 240, 1],
            forestgreen: [34, 139, 34, 1],
            fuchsia: [255, 0, 255, 1],
            gainsboro: [220, 220, 220, 1],
            ghostwhite: [248, 248, 255, 1],
            gold: [255, 215, 0, 1],
            goldenrod: [218, 165, 32, 1],
            gray: [128, 128, 128, 1],
            green: [0, 128, 0, 1],
            greenyellow: [173, 255, 47, 1],
            grey: [128, 128, 128, 1],
            honeydew: [240, 255, 240, 1],
            hotpink: [255, 105, 180, 1],
            indianred: [205, 92, 92, 1],
            indigo: [75, 0, 130, 1],
            ivory: [255, 255, 240, 1],
            khaki: [240, 230, 140, 1],
            lavender: [230, 230, 250, 1],
            lavenderblush: [255, 240, 245, 1],
            lawngreen: [124, 252, 0, 1],
            lemonchiffon: [255, 250, 205, 1],
            lightblue: [173, 216, 230, 1],
            lightcoral: [240, 128, 128, 1],
            lightcyan: [224, 255, 255, 1],
            lightgoldenrodyellow: [250, 250, 210, 1],
            lightgray: [211, 211, 211, 1],
            lightgreen: [144, 238, 144, 1],
            lightgrey: [211, 211, 211, 1],
            lightpink: [255, 182, 193, 1],
            lightsalmon: [255, 160, 122, 1],
            lightseagreen: [32, 178, 170, 1],
            lightskyblue: [135, 206, 250, 1],
            lightslategray: [119, 136, 153, 1],
            lightslategrey: [119, 136, 153, 1],
            lightsteelblue: [176, 196, 222, 1],
            lightyellow: [255, 255, 224, 1],
            lime: [0, 255, 0, 1],
            limegreen: [50, 205, 50, 1],
            linen: [250, 240, 230, 1],
            magenta: [255, 0, 255, 1],
            maroon: [128, 0, 0, 1],
            mediumaquamarine: [102, 205, 170, 1],
            mediumblue: [0, 0, 205, 1],
            mediumorchid: [186, 85, 211, 1],
            mediumpurple: [147, 112, 219, 1],
            mediumseagreen: [60, 179, 113, 1],
            mediumslateblue: [123, 104, 238, 1],
            mediumspringgreen: [0, 250, 154, 1],
            mediumturquoise: [72, 209, 204, 1],
            mediumvioletred: [199, 21, 133, 1],
            midnightblue: [25, 25, 112, 1],
            mintcream: [245, 255, 250, 1],
            mistyrose: [255, 228, 225, 1],
            moccasin: [255, 228, 181, 1],
            navajowhite: [255, 222, 173, 1],
            navy: [0, 0, 128, 1],
            oldlace: [253, 245, 230, 1],
            olive: [128, 128, 0, 1],
            olivedrab: [107, 142, 35, 1],
            orange: [255, 165, 0, 1],
            orangered: [255, 69, 0, 1],
            orchid: [218, 112, 214, 1],
            palegoldenrod: [238, 232, 170, 1],
            palegreen: [152, 251, 152, 1],
            paleturquoise: [175, 238, 238, 1],
            palevioletred: [219, 112, 147, 1],
            papayawhip: [255, 239, 213, 1],
            peachpuff: [255, 218, 185, 1],
            peru: [205, 133, 63, 1],
            pink: [255, 192, 203, 1],
            plum: [221, 160, 221, 1],
            powderblue: [176, 224, 230, 1],
            purple: [128, 0, 128, 1],
            rebeccapurple: [102, 51, 153, 1],
            red: [255, 0, 0, 1],
            rosybrown: [188, 143, 143, 1],
            royalblue: [65, 105, 225, 1],
            saddlebrown: [139, 69, 19, 1],
            salmon: [250, 128, 114, 1],
            sandybrown: [244, 164, 96, 1],
            seagreen: [46, 139, 87, 1],
            seashell: [255, 245, 238, 1],
            sienna: [160, 82, 45, 1],
            silver: [192, 192, 192, 1],
            skyblue: [135, 206, 235, 1],
            slateblue: [106, 90, 205, 1],
            slategray: [112, 128, 144, 1],
            slategrey: [112, 128, 144, 1],
            snow: [255, 250, 250, 1],
            springgreen: [0, 255, 127, 1],
            steelblue: [70, 130, 180, 1],
            tan: [210, 180, 140, 1],
            teal: [0, 128, 128, 1],
            thistle: [216, 191, 216, 1],
            tomato: [255, 99, 71, 1],
            turquoise: [64, 224, 208, 1],
            violet: [238, 130, 238, 1],
            wheat: [245, 222, 179, 1],
            white: [255, 255, 255, 1],
            whitesmoke: [245, 245, 245, 1],
            yellow: [255, 255, 0, 1],
            yellowgreen: [154, 205, 50, 1]
        };
        function n(t) {
            return (t = Math.round(t)) < 0 ? 0 : t > 255 ? 255 : t
        }
        function i(t) {
            return n("%" === t[t.length - 1] ? parseFloat(t) / 100 * 255 : parseInt(t))
        }
        function s(t) {
            return (e = "%" === t[t.length - 1] ? parseFloat(t) / 100 : parseFloat(t)) < 0 ? 0 : e > 1 ? 1 : e;
            var e;
        }
        function a(t, e, r) {
            return r < 0 ? r += 1 : r > 1 && (r -= 1),
            6 * r < 1 ? t + (e - t) * r * 6 : 2 * r < 1 ? e : 3 * r < 2 ? t + (e - t) * (2 / 3 - r) * 6 : t
        }
        try {
            e.parseCSSColor = function(t) {
                var e, o = t.replace(/ /g, "").toLowerCase();
                if (o in r)
                    return r[o].slice();
                if ("#" === o[0])
                    return 4 === o.length ? (e = parseInt(o.substr(1), 16)) >= 0 && e <= 4095 ? [(3840 & e) >> 4 | (3840 & e) >> 8, 240 & e | (240 & e) >> 4, 15 & e | (15 & e) << 4, 1] : null : 7 === o.length && (e = parseInt(o.substr(1), 16)) >= 0 && e <= 16777215 ? [(16711680 & e) >> 16, (65280 & e) >> 8, 255 & e, 1] : null;
                var l = o.indexOf("(")
                  , u = o.indexOf(")");
                if (-1 !== l && u + 1 === o.length) {
                    var c = o.substr(0, l)
                      , h = o.substr(l + 1, u - (l + 1)).split(",")
                      , p = 1;
                    switch (c) {
                    case "rgba":
                        if (4 !== h.length)
                            return null;
                        p = s(h.pop());
                    case "rgb":
                        return 3 !== h.length ? null : [i(h[0]), i(h[1]), i(h[2]), p];
                    case "hsla":
                        if (4 !== h.length)
                            return null;
                        p = s(h.pop());
                    case "hsl":
                        if (3 !== h.length)
                            return null;
                        var f = (parseFloat(h[0]) % 360 + 360) % 360 / 360
                          , d = s(h[1])
                          , y = s(h[2])
                          , m = y <= .5 ? y * (d + 1) : y + d - y * d
                          , g = 2 * y - m;
                        return [n(255 * a(g, m, f + 1 / 3)), n(255 * a(g, m, f)), n(255 * a(g, m, f - 1 / 3)), p];
                    default:
                        return null
                    }
                }
                return null
            }
            ;
        } catch (t) {}
    }
    ));
    class ye {
        constructor(t, e, r, n=1) {
            this.r = t,
            this.g = e,
            this.b = r,
            this.a = n;
        }
        static parse(t) {
            if (!t)
                return;
            if (t instanceof ye)
                return t;
            if ("string" != typeof t)
                return;
            const e = de.parseCSSColor(t);
            return e ? new ye(e[0] / 255 * e[3],e[1] / 255 * e[3],e[2] / 255 * e[3],e[3]) : void 0
        }
        toString() {
            const [t,e,r,n] = this.toArray();
            return `rgba(${Math.round(t)},${Math.round(e)},${Math.round(r)},${n})`
        }
        toArray() {
            const {r: t, g: e, b: r, a: n} = this;
            return 0 === n ? [0, 0, 0, 0] : [255 * t / n, 255 * e / n, 255 * r / n, n]
        }
        toArray01() {
            const {r: t, g: e, b: r, a: n} = this;
            return 0 === n ? [0, 0, 0, 0] : [t / n, e / n, r / n, n]
        }
        toArray01PremultipliedAlpha() {
            const {r: t, g: e, b: r, a: n} = this;
            return [t, e, r, n]
        }
    }
    ye.black = new ye(0,0,0,1),
    ye.white = new ye(1,1,1,1),
    ye.transparent = new ye(0,0,0,0),
    ye.red = new ye(1,0,0,1),
    ye.blue = new ye(0,0,1,1);
    var me = ye;
    class ge {
        constructor(t, e, r) {
            this.sensitivity = t ? e ? "variant" : "case" : e ? "accent" : "base",
            this.locale = r,
            this.collator = new Intl.Collator(this.locale ? this.locale : [],{
                sensitivity: this.sensitivity,
                usage: "search"
            });
        }
        compare(t, e) {
            return this.collator.compare(t, e)
        }
        resolvedLocale() {
            return new Intl.Collator(this.locale ? this.locale : []).resolvedOptions().locale
        }
    }
    class xe {
        constructor(t, e, r, n, i) {
            this.text = t.normalize ? t.normalize() : t,
            this.image = e,
            this.scale = r,
            this.fontStack = n,
            this.textColor = i;
        }
    }
    class ve {
        constructor(t) {
            this.sections = t;
        }
        static fromString(t) {
            return new ve([new xe(t,null,null,null,null)])
        }
        isEmpty() {
            return 0 === this.sections.length || !this.sections.some((t=>0 !== t.text.length || t.image && 0 !== t.image.name.length))
        }
        static factory(t) {
            return t instanceof ve ? t : ve.fromString(t)
        }
        toString() {
            return 0 === this.sections.length ? "" : this.sections.map((t=>t.text)).join("")
        }
        serialize() {
            const t = ["format"];
            for (const e of this.sections) {
                if (e.image) {
                    t.push(["image", e.image.name]);
                    continue
                }
                t.push(e.text);
                const r = {};
                e.fontStack && (r["text-font"] = ["literal", e.fontStack.split(",")]),
                e.scale && (r["font-scale"] = e.scale),
                e.textColor && (r["text-color"] = ["rgba"].concat(e.textColor.toArray())),
                t.push(r);
            }
            return t
        }
    }
    class be {
        constructor(t) {
            this.name = t.name,
            this.available = t.available;
        }
        toString() {
            return this.name
        }
        static fromString(t) {
            return t ? new be({
                name: t,
                available: !1
            }) : null
        }
        serialize() {
            return ["image", this.name]
        }
    }
    function _e(t, e, r, n) {
        return "number" == typeof t && t >= 0 && t <= 255 && "number" == typeof e && e >= 0 && e <= 255 && "number" == typeof r && r >= 0 && r <= 255 ? void 0 === n || "number" == typeof n && n >= 0 && n <= 1 ? null : `Invalid rgba value [${[t, e, r, n].join(", ")}]: 'a' must be between 0 and 1.` : `Invalid rgba value [${("number" == typeof n ? [t, e, r, n] : [t, e, r]).join(", ")}]: 'r', 'g', and 'b' must be between 0 and 255.`
    }
    function we(t) {
        if (null === t)
            return !0;
        if ("string" == typeof t)
            return !0;
        if ("boolean" == typeof t)
            return !0;
        if ("number" == typeof t)
            return !0;
        if (t instanceof me)
            return !0;
        if (t instanceof ge)
            return !0;
        if (t instanceof ve)
            return !0;
        if (t instanceof be)
            return !0;
        if (Array.isArray(t)) {
            for (const e of t)
                if (!we(e))
                    return !1;
            return !0
        }
        if ("object" == typeof t) {
            for (const e in t)
                if (!we(t[e]))
                    return !1;
            return !0
        }
        return !1
    }
    function Ae(t) {
        if (null === t)
            return Jt;
        if ("string" == typeof t)
            return Qt;
        if ("boolean" == typeof t)
            return te;
        if ("number" == typeof t)
            return Wt;
        if (t instanceof me)
            return ee;
        if (t instanceof ge)
            return ie;
        if (t instanceof ve)
            return se;
        if (t instanceof be)
            return ae;
        if (Array.isArray(t)) {
            const e = t.length;
            let r;
            for (const e of t) {
                const t = Ae(e);
                if (r) {
                    if (r === t)
                        continue;
                    r = ne;
                    break
                }
                r = t;
            }
            return oe(r || ne, e)
        }
        return re
    }
    function ke(t) {
        const e = typeof t;
        return null === t ? "" : "string" === e || "number" === e || "boolean" === e ? String(t) : t instanceof me || t instanceof ve || t instanceof be ? t.toString() : JSON.stringify(t)
    }
    class ze {
        constructor(t, e) {
            this.type = t,
            this.value = e;
        }
        static parse(t, e) {
            if (2 !== t.length)
                return e.error(`'literal' expression requires exactly one argument, but found ${t.length - 1} instead.`);
            if (!we(t[1]))
                return e.error("invalid value");
            const r = t[1];
            let n = Ae(r);
            const i = e.expectedType;
            return "array" !== n.kind || 0 !== n.N || !i || "array" !== i.kind || "number" == typeof i.N && 0 !== i.N || (n = i),
            new ze(n,r)
        }
        evaluate() {
            return this.value
        }
        eachChild() {}
        outputDefined() {
            return !0
        }
        serialize() {
            return "array" === this.type.kind || "object" === this.type.kind ? ["literal", this.value] : this.value instanceof me ? ["rgba"].concat(this.value.toArray()) : this.value instanceof ve ? this.value.serialize() : this.value
        }
    }
    var Se = ze
      , Me = class {
        constructor(t) {
            this.name = "ExpressionEvaluationError",
            this.message = t;
        }
        toJSON() {
            return this.message
        }
    }
    ;
    const Ie = {
        string: Qt,
        number: Wt,
        boolean: te,
        object: re
    };
    class Te {
        constructor(t, e) {
            this.type = t,
            this.args = e;
        }
        static parse(t, e) {
            if (t.length < 2)
                return e.error("Expected at least one argument.");
            let r, n = 1;
            const i = t[0];
            if ("array" === i) {
                let i, s;
                if (t.length > 2) {
                    const r = t[1];
                    if ("string" != typeof r || !(r in Ie) || "object" === r)
                        return e.error('The item type argument of "array" must be one of string, number, boolean', 1);
                    i = Ie[r],
                    n++;
                } else
                    i = ne;
                if (t.length > 3) {
                    if (null !== t[2] && ("number" != typeof t[2] || t[2] < 0 || t[2] !== Math.floor(t[2])))
                        return e.error('The length argument to "array" must be a positive integer literal', 2);
                    s = t[2],
                    n++;
                }
                r = oe(i, s);
            } else
                r = Ie[i];
            const s = [];
            for (; n < t.length; n++) {
                const r = e.parse(t[n], n, ne);
                if (!r)
                    return null;
                s.push(r);
            }
            return new Te(r,s)
        }
        evaluate(t) {
            for (let e = 0; e < this.args.length; e++) {
                const r = this.args[e].evaluate(t);
                if (!ce(this.type, Ae(r)))
                    return r;
                if (e === this.args.length - 1)
                    throw new Me(`Expected value to be of type ${le(this.type)}, but found ${le(Ae(r))} instead.`)
            }
            return null
        }
        eachChild(t) {
            this.args.forEach(t);
        }
        outputDefined() {
            return this.args.every((t=>t.outputDefined()))
        }
        serialize() {
            const t = this.type
              , e = [t.kind];
            if ("array" === t.kind) {
                const r = t.itemType;
                if ("string" === r.kind || "number" === r.kind || "boolean" === r.kind) {
                    e.push(r.kind);
                    const n = t.N;
                    ("number" == typeof n || this.args.length > 1) && e.push(n);
                }
            }
            return e.concat(this.args.map((t=>t.serialize())))
        }
    }
    var Be = Te;
    class Ce {
        constructor(t) {
            this.type = se,
            this.sections = t;
        }
        static parse(t, e) {
            if (t.length < 2)
                return e.error("Expected at least one argument.");
            const r = t[1];
            if (!Array.isArray(r) && "object" == typeof r)
                return e.error("First argument must be an image or text section.");
            const n = [];
            let i = !1;
            for (let r = 1; r <= t.length - 1; ++r) {
                const s = t[r];
                if (i && "object" == typeof s && !Array.isArray(s)) {
                    i = !1;
                    let t = null;
                    if (s["font-scale"] && (t = e.parse(s["font-scale"], 1, Wt),
                    !t))
                        return null;
                    let r = null;
                    if (s["text-font"] && (r = e.parse(s["text-font"], 1, oe(Qt)),
                    !r))
                        return null;
                    let a = null;
                    if (s["text-color"] && (a = e.parse(s["text-color"], 1, ee),
                    !a))
                        return null;
                    const o = n[n.length - 1];
                    o.scale = t,
                    o.font = r,
                    o.textColor = a;
                } else {
                    const s = e.parse(t[r], 1, ne);
                    if (!s)
                        return null;
                    const a = s.type.kind;
                    if ("string" !== a && "value" !== a && "null" !== a && "resolvedImage" !== a)
                        return e.error("Formatted text type must be 'string', 'value', 'image' or 'null'.");
                    i = !0,
                    n.push({
                        content: s,
                        scale: null,
                        font: null,
                        textColor: null
                    });
                }
            }
            return new Ce(n)
        }
        evaluate(t) {
            return new ve(this.sections.map((e=>{
                const r = e.content.evaluate(t);
                return Ae(r) === ae ? new xe("",r,null,null,null) : new xe(ke(r),null,e.scale ? e.scale.evaluate(t) : null,e.font ? e.font.evaluate(t).join(",") : null,e.textColor ? e.textColor.evaluate(t) : null)
            }
            )))
        }
        eachChild(t) {
            for (const e of this.sections)
                t(e.content),
                e.scale && t(e.scale),
                e.font && t(e.font),
                e.textColor && t(e.textColor);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            const t = ["format"];
            for (const e of this.sections) {
                t.push(e.content.serialize());
                const r = {};
                e.scale && (r["font-scale"] = e.scale.serialize()),
                e.font && (r["text-font"] = e.font.serialize()),
                e.textColor && (r["text-color"] = e.textColor.serialize()),
                t.push(r);
            }
            return t
        }
    }
    class Ve {
        constructor(t) {
            this.type = ae,
            this.input = t;
        }
        static parse(t, e) {
            if (2 !== t.length)
                return e.error("Expected two arguments.");
            const r = e.parse(t[1], 1, Qt);
            return r ? new Ve(r) : e.error("No image name provided.")
        }
        evaluate(t) {
            const e = this.input.evaluate(t)
              , r = be.fromString(e);
            return r && t.availableImages && (r.available = t.availableImages.indexOf(e) > -1),
            r
        }
        eachChild(t) {
            t(this.input);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            return ["image", this.input.serialize()]
        }
    }
    const Pe = {
        "to-boolean": te,
        "to-color": ee,
        "to-number": Wt,
        "to-string": Qt
    };
    class De {
        constructor(t, e) {
            this.type = t,
            this.args = e;
        }
        static parse(t, e) {
            if (t.length < 2)
                return e.error("Expected at least one argument.");
            const r = t[0];
            if (("to-boolean" === r || "to-string" === r) && 2 !== t.length)
                return e.error("Expected one argument.");
            const n = Pe[r]
              , i = [];
            for (let r = 1; r < t.length; r++) {
                const n = e.parse(t[r], r, ne);
                if (!n)
                    return null;
                i.push(n);
            }
            return new De(n,i)
        }
        evaluate(t) {
            if ("boolean" === this.type.kind)
                return Boolean(this.args[0].evaluate(t));
            if ("color" === this.type.kind) {
                let e, r;
                for (const n of this.args) {
                    if (e = n.evaluate(t),
                    r = null,
                    e instanceof me)
                        return e;
                    if ("string" == typeof e) {
                        const r = t.parseColor(e);
                        if (r)
                            return r
                    } else if (Array.isArray(e) && (r = e.length < 3 || e.length > 4 ? `Invalid rbga value ${JSON.stringify(e)}: expected an array containing either three or four numeric values.` : _e(e[0], e[1], e[2], e[3]),
                    !r))
                        return new me(e[0] / 255,e[1] / 255,e[2] / 255,e[3])
                }
                throw new Me(r || `Could not parse color from value '${"string" == typeof e ? e : String(JSON.stringify(e))}'`)
            }
            if ("number" === this.type.kind) {
                let e = null;
                for (const r of this.args) {
                    if (e = r.evaluate(t),
                    null === e)
                        return 0;
                    const n = Number(e);
                    if (!isNaN(n))
                        return n
                }
                throw new Me(`Could not convert ${JSON.stringify(e)} to number.`)
            }
            return "formatted" === this.type.kind ? ve.fromString(ke(this.args[0].evaluate(t))) : "resolvedImage" === this.type.kind ? be.fromString(ke(this.args[0].evaluate(t))) : ke(this.args[0].evaluate(t))
        }
        eachChild(t) {
            this.args.forEach(t);
        }
        outputDefined() {
            return this.args.every((t=>t.outputDefined()))
        }
        serialize() {
            if ("formatted" === this.type.kind)
                return new Ce([{
                    content: this.args[0],
                    scale: null,
                    font: null,
                    textColor: null
                }]).serialize();
            if ("resolvedImage" === this.type.kind)
                return new Ve(this.args[0]).serialize();
            const t = [`to-${this.type.kind}`];
            return this.eachChild((e=>{
                t.push(e.serialize());
            }
            )),
            t
        }
    }
    var Ee = De;
    const Fe = ["Unknown", "Point", "LineString", "Polygon"];
    var Le = class {
        constructor() {
            this.globals = null,
            this.feature = null,
            this.featureState = null,
            this.formattedSection = null,
            this._parseColorCache = {},
            this.availableImages = null,
            this.canonical = null,
            this.featureTileCoord = null,
            this.featureDistanceData = null;
        }
        id() {
            return this.feature && void 0 !== this.feature.id ? this.feature.id : null
        }
        geometryType() {
            return this.feature ? "number" == typeof this.feature.type ? Fe[this.feature.type] : this.feature.type : null
        }
        geometry() {
            return this.feature && "geometry"in this.feature ? this.feature.geometry : null
        }
        canonicalID() {
            return this.canonical
        }
        properties() {
            return this.feature && this.feature.properties || {}
        }
        distanceFromCenter() {
            if (this.featureTileCoord && this.featureDistanceData) {
                const t = this.featureDistanceData.center
                  , e = this.featureDistanceData.scale
                  , {x: r, y: n} = this.featureTileCoord;
                return this.featureDistanceData.bearing[0] * (r * e - t[0]) + this.featureDistanceData.bearing[1] * (n * e - t[1])
            }
            return 0
        }
        parseColor(t) {
            let e = this._parseColorCache[t];
            return e || (e = this._parseColorCache[t] = me.parse(t)),
            e
        }
    }
    ;
    class Re {
        constructor(t, e, r, n) {
            this.name = t,
            this.type = e,
            this._evaluate = r,
            this.args = n;
        }
        evaluate(t) {
            return this._evaluate(t, this.args)
        }
        eachChild(t) {
            this.args.forEach(t);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            return [this.name].concat(this.args.map((t=>t.serialize())))
        }
        static parse(t, e) {
            const r = t[0]
              , n = Re.definitions[r];
            if (!n)
                return e.error(`Unknown expression "${r}". If you wanted a literal array, use ["literal", [...]].`, 0);
            const i = Array.isArray(n) ? n[0] : n.type
              , s = Array.isArray(n) ? [[n[1], n[2]]] : n.overloads
              , a = s.filter((([e])=>!Array.isArray(e) || e.length === t.length - 1));
            let o = null;
            for (const [n,s] of a) {
                o = new hr(e.registry,e.path,null,e.scope);
                const a = [];
                let l = !1;
                for (let e = 1; e < t.length; e++) {
                    const r = t[e]
                      , i = Array.isArray(n) ? n[e - 1] : n.type
                      , s = o.parse(r, 1 + a.length, i);
                    if (!s) {
                        l = !0;
                        break
                    }
                    a.push(s);
                }
                if (!l)
                    if (Array.isArray(n) && n.length !== a.length)
                        o.error(`Expected ${n.length} arguments, but found ${a.length} instead.`);
                    else {
                        for (let t = 0; t < a.length; t++) {
                            const e = Array.isArray(n) ? n[t] : n.type
                              , r = a[t];
                            o.concat(t + 1).checkSubtype(e, r.type);
                        }
                        if (0 === o.errors.length)
                            return new Re(r,i,s,a)
                    }
            }
            if (1 === a.length)
                e.errors.push(...o.errors);
            else {
                const r = (a.length ? a : s).map((([t])=>{
                    return e = t,
                    Array.isArray(e) ? `(${e.map(le).join(", ")})` : `(${le(e.type)}...)`;
                    var e;
                }
                )).join(" | ")
                  , n = [];
                for (let r = 1; r < t.length; r++) {
                    const i = e.parse(t[r], 1 + n.length);
                    if (!i)
                        return null;
                    n.push(le(i.type));
                }
                e.error(`Expected arguments of type ${r}, but found (${n.join(", ")}) instead.`);
            }
            return null
        }
        static register(t, e) {
            Re.definitions = e;
            for (const r in e)
                t[r] = Re;
        }
    }
    var je = Re;
    class Ue {
        constructor(t, e, r) {
            this.type = ie,
            this.locale = r,
            this.caseSensitive = t,
            this.diacriticSensitive = e;
        }
        static parse(t, e) {
            if (2 !== t.length)
                return e.error("Expected one argument.");
            const r = t[1];
            if ("object" != typeof r || Array.isArray(r))
                return e.error("Collator options argument must be an object.");
            const n = e.parse(void 0 !== r["case-sensitive"] && r["case-sensitive"], 1, te);
            if (!n)
                return null;
            const i = e.parse(void 0 !== r["diacritic-sensitive"] && r["diacritic-sensitive"], 1, te);
            if (!i)
                return null;
            let s = null;
            return r.locale && (s = e.parse(r.locale, 1, Qt),
            !s) ? null : new Ue(n,i,s)
        }
        evaluate(t) {
            return new ge(this.caseSensitive.evaluate(t),this.diacriticSensitive.evaluate(t),this.locale ? this.locale.evaluate(t) : null)
        }
        eachChild(t) {
            t(this.caseSensitive),
            t(this.diacriticSensitive),
            this.locale && t(this.locale);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            const t = {};
            return t["case-sensitive"] = this.caseSensitive.serialize(),
            t["diacritic-sensitive"] = this.diacriticSensitive.serialize(),
            this.locale && (t.locale = this.locale.serialize()),
            ["collator", t]
        }
    }
    const Oe = 8192;
    function $e(t, e) {
        t[0] = Math.min(t[0], e[0]),
        t[1] = Math.min(t[1], e[1]),
        t[2] = Math.max(t[2], e[0]),
        t[3] = Math.max(t[3], e[1]);
    }
    function qe(t, e) {
        return !(t[0] <= e[0] || t[2] >= e[2] || t[1] <= e[1] || t[3] >= e[3])
    }
    function Ne(t, e) {
        const r = (180 + t[0]) / 360
          , n = (180 - 180 / Math.PI * Math.log(Math.tan(Math.PI / 4 + t[1] * Math.PI / 360))) / 360
          , i = Math.pow(2, e.z);
        return [Math.round(r * i * Oe), Math.round(n * i * Oe)]
    }
    function Ze(t, e, r) {
        const n = t[0] - e[0]
          , i = t[1] - e[1]
          , s = t[0] - r[0]
          , a = t[1] - r[1];
        return n * a - s * i == 0 && n * s <= 0 && i * a <= 0
    }
    function Ge(t, e) {
        let r = !1;
        for (let a = 0, o = e.length; a < o; a++) {
            const o = e[a];
            for (let e = 0, a = o.length; e < a - 1; e++) {
                if (Ze(t, o[e], o[e + 1]))
                    return !1;
                (i = o[e])[1] > (n = t)[1] != (s = o[e + 1])[1] > n[1] && n[0] < (s[0] - i[0]) * (n[1] - i[1]) / (s[1] - i[1]) + i[0] && (r = !r);
            }
        }
        var n, i, s;
        return r
    }
    function Xe(t, e) {
        for (let r = 0; r < e.length; r++)
            if (Ge(t, e[r]))
                return !0;
        return !1
    }
    function Ye(t, e, r, n) {
        const i = n[0] - r[0]
          , s = n[1] - r[1]
          , a = (t[0] - r[0]) * s - i * (t[1] - r[1])
          , o = (e[0] - r[0]) * s - i * (e[1] - r[1]);
        return a > 0 && o < 0 || a < 0 && o > 0
    }
    function He(t, e, r) {
        for (const u of r)
            for (let r = 0; r < u.length - 1; ++r)
                if (0 != (o = [(a = u[r + 1])[0] - (s = u[r])[0], a[1] - s[1]])[0] * (l = [(i = e)[0] - (n = t)[0], i[1] - n[1]])[1] - o[1] * l[0] && Ye(n, i, s, a) && Ye(s, a, n, i))
                    return !0;
        var n, i, s, a, o, l;
        return !1
    }
    function Ke(t, e) {
        for (let r = 0; r < t.length; ++r)
            if (!Ge(t[r], e))
                return !1;
        for (let r = 0; r < t.length - 1; ++r)
            if (He(t[r], t[r + 1], e))
                return !1;
        return !0
    }
    function Je(t, e) {
        for (let r = 0; r < e.length; r++)
            if (Ke(t, e[r]))
                return !0;
        return !1
    }
    function We(t, e, r) {
        const n = [];
        for (let i = 0; i < t.length; i++) {
            const s = [];
            for (let n = 0; n < t[i].length; n++) {
                const a = Ne(t[i][n], r);
                $e(e, a),
                s.push(a);
            }
            n.push(s);
        }
        return n
    }
    function Qe(t, e, r) {
        const n = [];
        for (let i = 0; i < t.length; i++) {
            const s = We(t[i], e, r);
            n.push(s);
        }
        return n
    }
    function tr(t, e, r, n) {
        if (t[0] < r[0] || t[0] > r[2]) {
            const e = .5 * n;
            let i = t[0] - r[0] > e ? -n : r[0] - t[0] > e ? n : 0;
            0 === i && (i = t[0] - r[2] > e ? -n : r[2] - t[0] > e ? n : 0),
            t[0] += i;
        }
        $e(e, t);
    }
    function er(t, e, r, n) {
        const i = Math.pow(2, n.z) * Oe
          , s = [n.x * Oe, n.y * Oe]
          , a = [];
        if (!t)
            return a;
        for (const n of t)
            for (const t of n) {
                const n = [t.x + s[0], t.y + s[1]];
                tr(n, e, r, i),
                a.push(n);
            }
        return a
    }
    function rr(t, e, r, n) {
        const i = Math.pow(2, n.z) * Oe
          , s = [n.x * Oe, n.y * Oe]
          , a = [];
        if (!t)
            return a;
        for (const r of t) {
            const t = [];
            for (const n of r) {
                const r = [n.x + s[0], n.y + s[1]];
                $e(e, r),
                t.push(r);
            }
            a.push(t);
        }
        if (e[2] - e[0] <= i / 2) {
            (o = e)[0] = o[1] = 1 / 0,
            o[2] = o[3] = -1 / 0;
            for (const t of a)
                for (const n of t)
                    tr(n, e, r, i);
        }
        var o;
        return a
    }
    class nr {
        constructor(t, e) {
            this.type = te,
            this.geojson = t,
            this.geometries = e;
        }
        static parse(t, e) {
            if (2 !== t.length)
                return e.error(`'within' expression requires exactly one argument, but found ${t.length - 1} instead.`);
            if (we(t[1])) {
                const e = t[1];
                if ("FeatureCollection" === e.type)
                    for (let t = 0; t < e.features.length; ++t) {
                        const r = e.features[t].geometry.type;
                        if ("Polygon" === r || "MultiPolygon" === r)
                            return new nr(e,e.features[t].geometry)
                    }
                else if ("Feature" === e.type) {
                    const t = e.geometry.type;
                    if ("Polygon" === t || "MultiPolygon" === t)
                        return new nr(e,e.geometry)
                } else if ("Polygon" === e.type || "MultiPolygon" === e.type)
                    return new nr(e,e)
            }
            return e.error("'within' expression requires valid geojson object that contains polygon geometry type.")
        }
        evaluate(t) {
            if (null != t.geometry() && null != t.canonicalID()) {
                if ("Point" === t.geometryType())
                    return function(t, e) {
                        const r = [1 / 0, 1 / 0, -1 / 0, -1 / 0]
                          , n = [1 / 0, 1 / 0, -1 / 0, -1 / 0]
                          , i = t.canonicalID();
                        if (!i)
                            return !1;
                        if ("Polygon" === e.type) {
                            const s = We(e.coordinates, n, i)
                              , a = er(t.geometry(), r, n, i);
                            if (!qe(r, n))
                                return !1;
                            for (const t of a)
                                if (!Ge(t, s))
                                    return !1
                        }
                        if ("MultiPolygon" === e.type) {
                            const s = Qe(e.coordinates, n, i)
                              , a = er(t.geometry(), r, n, i);
                            if (!qe(r, n))
                                return !1;
                            for (const t of a)
                                if (!Xe(t, s))
                                    return !1
                        }
                        return !0
                    }(t, this.geometries);
                if ("LineString" === t.geometryType())
                    return function(t, e) {
                        const r = [1 / 0, 1 / 0, -1 / 0, -1 / 0]
                          , n = [1 / 0, 1 / 0, -1 / 0, -1 / 0]
                          , i = t.canonicalID();
                        if (!i)
                            return !1;
                        if ("Polygon" === e.type) {
                            const s = We(e.coordinates, n, i)
                              , a = rr(t.geometry(), r, n, i);
                            if (!qe(r, n))
                                return !1;
                            for (const t of a)
                                if (!Ke(t, s))
                                    return !1
                        }
                        if ("MultiPolygon" === e.type) {
                            const s = Qe(e.coordinates, n, i)
                              , a = rr(t.geometry(), r, n, i);
                            if (!qe(r, n))
                                return !1;
                            for (const t of a)
                                if (!Je(t, s))
                                    return !1
                        }
                        return !0
                    }(t, this.geometries)
            }
            return !1
        }
        eachChild() {}
        outputDefined() {
            return !0
        }
        serialize() {
            return ["within", this.geojson]
        }
    }
    var ir = nr;
    function sr(t) {
        if (t instanceof je) {
            if ("get" === t.name && 1 === t.args.length)
                return !1;
            if ("feature-state" === t.name)
                return !1;
            if ("has" === t.name && 1 === t.args.length)
                return !1;
            if ("properties" === t.name || "geometry-type" === t.name || "id" === t.name)
                return !1;
            if (/^filter-/.test(t.name))
                return !1
        }
        if (t instanceof ir)
            return !1;
        let e = !0;
        return t.eachChild((t=>{
            e && !sr(t) && (e = !1);
        }
        )),
        e
    }
    function ar(t) {
        if (t instanceof je && "feature-state" === t.name)
            return !1;
        let e = !0;
        return t.eachChild((t=>{
            e && !ar(t) && (e = !1);
        }
        )),
        e
    }
    function or(t, e) {
        if (t instanceof je && e.indexOf(t.name) >= 0)
            return !1;
        let r = !0;
        return t.eachChild((t=>{
            r && !or(t, e) && (r = !1);
        }
        )),
        r
    }
    class lr {
        constructor(t, e) {
            this.type = e.type,
            this.name = t,
            this.boundExpression = e;
        }
        static parse(t, e) {
            if (2 !== t.length || "string" != typeof t[1])
                return e.error("'var' expression requires exactly one string literal argument.");
            const r = t[1];
            return e.scope.has(r) ? new lr(r,e.scope.get(r)) : e.error(`Unknown variable "${r}". Make sure "${r}" has been bound in an enclosing "let" expression before using it.`, 1)
        }
        evaluate(t) {
            return this.boundExpression.evaluate(t)
        }
        eachChild() {}
        outputDefined() {
            return !1
        }
        serialize() {
            return ["var", this.name]
        }
    }
    var ur = lr;
    class cr {
        constructor(t, e=[], r, n=new Kt, i=[]) {
            this.registry = t,
            this.path = e,
            this.key = e.map((t=>`[${t}]`)).join(""),
            this.scope = n,
            this.errors = i,
            this.expectedType = r;
        }
        parse(t, e, r, n, i={}) {
            return e ? this.concat(e, r, n)._parse(t, i) : this._parse(t, i)
        }
        _parse(t, e) {
            function r(t, e, r) {
                return "assert" === r ? new Be(e,[t]) : "coerce" === r ? new Ee(e,[t]) : t
            }
            if (null !== t && "string" != typeof t && "boolean" != typeof t && "number" != typeof t || (t = ["literal", t]),
            Array.isArray(t)) {
                if (0 === t.length)
                    return this.error('Expected an array with at least one element. If you wanted a literal array, use ["literal", []].');
                const n = t[0];
                if ("string" != typeof n)
                    return this.error(`Expression name must be a string, but found ${typeof n} instead. If you wanted a literal array, use ["literal", [...]].`, 0),
                    null;
                const i = this.registry[n];
                if (i) {
                    let n = i.parse(t, this);
                    if (!n)
                        return null;
                    if (this.expectedType) {
                        const t = this.expectedType
                          , i = n.type;
                        if ("string" !== t.kind && "number" !== t.kind && "boolean" !== t.kind && "object" !== t.kind && "array" !== t.kind || "value" !== i.kind)
                            if ("color" !== t.kind && "formatted" !== t.kind && "resolvedImage" !== t.kind || "value" !== i.kind && "string" !== i.kind) {
                                if (this.checkSubtype(t, i))
                                    return null
                            } else
                                n = r(n, t, e.typeAnnotation || "coerce");
                        else
                            n = r(n, t, e.typeAnnotation || "assert");
                    }
                    if (!(n instanceof Se) && "resolvedImage" !== n.type.kind && pr(n)) {
                        const t = new Le;
                        try {
                            n = new Se(n.type,n.evaluate(t));
                        } catch (t) {
                            return this.error(t.message),
                            null
                        }
                    }
                    return n
                }
                return this.error(`Unknown expression "${n}". If you wanted a literal array, use ["literal", [...]].`, 0)
            }
            return this.error(void 0 === t ? "'undefined' value invalid. Use null instead." : "object" == typeof t ? 'Bare objects invalid. Use ["literal", {...}] instead.' : `Expected an array, but found ${typeof t} instead.`)
        }
        concat(t, e, r) {
            const n = "number" == typeof t ? this.path.concat(t) : this.path
              , i = r ? this.scope.concat(r) : this.scope;
            return new cr(this.registry,n,e || null,i,this.errors)
        }
        error(t, ...e) {
            const r = `${this.key}${e.map((t=>`[${t}]`)).join("")}`;
            this.errors.push(new Yt(r,t));
        }
        checkSubtype(t, e) {
            const r = ce(t, e);
            return r && this.error(r),
            r
        }
    }
    var hr = cr;
    function pr(t) {
        if (t instanceof ur)
            return pr(t.boundExpression);
        if (t instanceof je && "error" === t.name)
            return !1;
        if (t instanceof Ue)
            return !1;
        if (t instanceof ir)
            return !1;
        const e = t instanceof Ee || t instanceof Be;
        let r = !0;
        return t.eachChild((t=>{
            r = e ? r && pr(t) : r && t instanceof Se;
        }
        )),
        !!r && sr(t) && or(t, ["zoom", "heatmap-density", "line-progress", "sky-radial-progress", "accumulated", "is-supported-script", "pitch", "distance-from-center"])
    }
    function fr(t, e) {
        const r = t.length - 1;
        let n, i, s = 0, a = r, o = 0;
        for (; s <= a; )
            if (o = Math.floor((s + a) / 2),
            n = t[o],
            i = t[o + 1],
            n <= e) {
                if (o === r || e < i)
                    return o;
                s = o + 1;
            } else {
                if (!(n > e))
                    throw new Me("Input is not a number.");
                a = o - 1;
            }
        return 0
    }
    class dr {
        constructor(t, e, r) {
            this.type = t,
            this.input = e,
            this.labels = [],
            this.outputs = [];
            for (const [t,e] of r)
                this.labels.push(t),
                this.outputs.push(e);
        }
        static parse(t, e) {
            if (t.length - 1 < 4)
                return e.error(`Expected at least 4 arguments, but found only ${t.length - 1}.`);
            if ((t.length - 1) % 2 != 0)
                return e.error("Expected an even number of arguments.");
            const r = e.parse(t[1], 1, Wt);
            if (!r)
                return null;
            const n = [];
            let i = null;
            e.expectedType && "value" !== e.expectedType.kind && (i = e.expectedType);
            for (let r = 1; r < t.length; r += 2) {
                const s = 1 === r ? -1 / 0 : t[r]
                  , a = t[r + 1]
                  , o = r
                  , l = r + 1;
                if ("number" != typeof s)
                    return e.error('Input/output pairs for "step" expressions must be defined using literal numeric values (not computed expressions) for the input values.', o);
                if (n.length && n[n.length - 1][0] >= s)
                    return e.error('Input/output pairs for "step" expressions must be arranged with input values in strictly ascending order.', o);
                const u = e.parse(a, l, i);
                if (!u)
                    return null;
                i = i || u.type,
                n.push([s, u]);
            }
            return new dr(i,r,n)
        }
        evaluate(t) {
            const e = this.labels
              , r = this.outputs;
            if (1 === e.length)
                return r[0].evaluate(t);
            const n = this.input.evaluate(t);
            if (n <= e[0])
                return r[0].evaluate(t);
            const i = e.length;
            return n >= e[i - 1] ? r[i - 1].evaluate(t) : r[fr(e, n)].evaluate(t)
        }
        eachChild(t) {
            t(this.input);
            for (const e of this.outputs)
                t(e);
        }
        outputDefined() {
            return this.outputs.every((t=>t.outputDefined()))
        }
        serialize() {
            const t = ["step", this.input.serialize()];
            for (let e = 0; e < this.labels.length; e++)
                e > 0 && t.push(this.labels[e]),
                t.push(this.outputs[e].serialize());
            return t
        }
    }
    var yr = dr;
    function mr(t, e, r) {
        return t * (1 - r) + e * r
    }
    var gr = Object.freeze({
        __proto__: null,
        number: mr,
        color: function(t, e, r) {
            return new me(mr(t.r, e.r, r),mr(t.g, e.g, r),mr(t.b, e.b, r),mr(t.a, e.a, r))
        },
        array: function(t, e, r) {
            return t.map(((t,n)=>mr(t, e[n], r)))
        }
    });
    const xr = .95047
      , vr = 1.08883
      , br = 4 / 29
      , _r = 6 / 29
      , wr = 3 * _r * _r
      , Ar = Math.PI / 180
      , kr = 180 / Math.PI;
    function zr(t) {
        return t > .008856451679035631 ? Math.pow(t, 1 / 3) : t / wr + br
    }
    function Sr(t) {
        return t > _r ? t * t * t : wr * (t - br)
    }
    function Mr(t) {
        return 255 * (t <= .0031308 ? 12.92 * t : 1.055 * Math.pow(t, 1 / 2.4) - .055)
    }
    function Ir(t) {
        return (t /= 255) <= .04045 ? t / 12.92 : Math.pow((t + .055) / 1.055, 2.4)
    }
    function Tr(t) {
        const e = Ir(t.r)
          , r = Ir(t.g)
          , n = Ir(t.b)
          , i = zr((.4124564 * e + .3575761 * r + .1804375 * n) / xr)
          , s = zr((.2126729 * e + .7151522 * r + .072175 * n) / 1);
        return {
            l: 116 * s - 16,
            a: 500 * (i - s),
            b: 200 * (s - zr((.0193339 * e + .119192 * r + .9503041 * n) / vr)),
            alpha: t.a
        }
    }
    function Br(t) {
        let e = (t.l + 16) / 116
          , r = isNaN(t.a) ? e : e + t.a / 500
          , n = isNaN(t.b) ? e : e - t.b / 200;
        return e = 1 * Sr(e),
        r = xr * Sr(r),
        n = vr * Sr(n),
        new me(Mr(3.2404542 * r - 1.5371385 * e - .4985314 * n),Mr(-.969266 * r + 1.8760108 * e + .041556 * n),Mr(.0556434 * r - .2040259 * e + 1.0572252 * n),t.alpha)
    }
    function Cr(t, e, r) {
        const n = e - t;
        return t + r * (n > 180 || n < -180 ? n - 360 * Math.round(n / 360) : n)
    }
    const Vr = {
        forward: Tr,
        reverse: Br,
        interpolate: function(t, e, r) {
            return {
                l: mr(t.l, e.l, r),
                a: mr(t.a, e.a, r),
                b: mr(t.b, e.b, r),
                alpha: mr(t.alpha, e.alpha, r)
            }
        }
    }
      , Pr = {
        forward: function(t) {
            const {l: e, a: r, b: n} = Tr(t)
              , i = Math.atan2(n, r) * kr;
            return {
                h: i < 0 ? i + 360 : i,
                c: Math.sqrt(r * r + n * n),
                l: e,
                alpha: t.a
            }
        },
        reverse: function(t) {
            const e = t.h * Ar
              , r = t.c;
            return Br({
                l: t.l,
                a: Math.cos(e) * r,
                b: Math.sin(e) * r,
                alpha: t.alpha
            })
        },
        interpolate: function(t, e, r) {
            return {
                h: Cr(t.h, e.h, r),
                c: mr(t.c, e.c, r),
                l: mr(t.l, e.l, r),
                alpha: mr(t.alpha, e.alpha, r)
            }
        }
    };
    var Dr = Object.freeze({
        __proto__: null,
        lab: Vr,
        hcl: Pr
    });
    class Er {
        constructor(t, e, r, n, i) {
            this.type = t,
            this.operator = e,
            this.interpolation = r,
            this.input = n,
            this.labels = [],
            this.outputs = [];
            for (const [t,e] of i)
                this.labels.push(t),
                this.outputs.push(e);
        }
        static interpolationFactor(t, e, n, i) {
            let s = 0;
            if ("exponential" === t.name)
                s = Fr(e, t.base, n, i);
            else if ("linear" === t.name)
                s = Fr(e, 1, n, i);
            else if ("cubic-bezier" === t.name) {
                const a = t.controlPoints;
                s = new r(a[0],a[1],a[2],a[3]).solve(Fr(e, 1, n, i));
            }
            return s
        }
        static parse(t, e) {
            let[r,n,i,...s] = t;
            if (!Array.isArray(n) || 0 === n.length)
                return e.error("Expected an interpolation type expression.", 1);
            if ("linear" === n[0])
                n = {
                    name: "linear"
                };
            else if ("exponential" === n[0]) {
                const t = n[1];
                if ("number" != typeof t)
                    return e.error("Exponential interpolation requires a numeric base.", 1, 1);
                n = {
                    name: "exponential",
                    base: t
                };
            } else {
                if ("cubic-bezier" !== n[0])
                    return e.error(`Unknown interpolation type ${String(n[0])}`, 1, 0);
                {
                    const t = n.slice(1);
                    if (4 !== t.length || t.some((t=>"number" != typeof t || t < 0 || t > 1)))
                        return e.error("Cubic bezier interpolation requires four numeric arguments with values between 0 and 1.", 1);
                    n = {
                        name: "cubic-bezier",
                        controlPoints: t
                    };
                }
            }
            if (t.length - 1 < 4)
                return e.error(`Expected at least 4 arguments, but found only ${t.length - 1}.`);
            if ((t.length - 1) % 2 != 0)
                return e.error("Expected an even number of arguments.");
            if (i = e.parse(i, 2, Wt),
            !i)
                return null;
            const a = [];
            let o = null;
            "interpolate-hcl" === r || "interpolate-lab" === r ? o = ee : e.expectedType && "value" !== e.expectedType.kind && (o = e.expectedType);
            for (let t = 0; t < s.length; t += 2) {
                const r = s[t]
                  , n = s[t + 1]
                  , i = t + 3
                  , l = t + 4;
                if ("number" != typeof r)
                    return e.error('Input/output pairs for "interpolate" expressions must be defined using literal numeric values (not computed expressions) for the input values.', i);
                if (a.length && a[a.length - 1][0] >= r)
                    return e.error('Input/output pairs for "interpolate" expressions must be arranged with input values in strictly ascending order.', i);
                const u = e.parse(n, l, o);
                if (!u)
                    return null;
                o = o || u.type,
                a.push([r, u]);
            }
            return "number" === o.kind || "color" === o.kind || "array" === o.kind && "number" === o.itemType.kind && "number" == typeof o.N ? new Er(o,r,n,i,a) : e.error(`Type ${le(o)} is not interpolatable.`)
        }
        evaluate(t) {
            const e = this.labels
              , r = this.outputs;
            if (1 === e.length)
                return r[0].evaluate(t);
            const n = this.input.evaluate(t);
            if (n <= e[0])
                return r[0].evaluate(t);
            const i = e.length;
            if (n >= e[i - 1])
                return r[i - 1].evaluate(t);
            const s = fr(e, n)
              , a = Er.interpolationFactor(this.interpolation, n, e[s], e[s + 1])
              , o = r[s].evaluate(t)
              , l = r[s + 1].evaluate(t);
            return "interpolate" === this.operator ? gr[this.type.kind.toLowerCase()](o, l, a) : "interpolate-hcl" === this.operator ? Pr.reverse(Pr.interpolate(Pr.forward(o), Pr.forward(l), a)) : Vr.reverse(Vr.interpolate(Vr.forward(o), Vr.forward(l), a))
        }
        eachChild(t) {
            t(this.input);
            for (const e of this.outputs)
                t(e);
        }
        outputDefined() {
            return this.outputs.every((t=>t.outputDefined()))
        }
        serialize() {
            let t;
            t = "linear" === this.interpolation.name ? ["linear"] : "exponential" === this.interpolation.name ? 1 === this.interpolation.base ? ["linear"] : ["exponential", this.interpolation.base] : ["cubic-bezier"].concat(this.interpolation.controlPoints);
            const e = [this.operator, t, this.input.serialize()];
            for (let t = 0; t < this.labels.length; t++)
                e.push(this.labels[t], this.outputs[t].serialize());
            return e
        }
    }
    function Fr(t, e, r, n) {
        const i = n - r
          , s = t - r;
        return 0 === i ? 0 : 1 === e ? s / i : (Math.pow(e, s) - 1) / (Math.pow(e, i) - 1)
    }
    var Lr = Er;
    class Rr {
        constructor(t, e) {
            this.type = t,
            this.args = e;
        }
        static parse(t, e) {
            if (t.length < 2)
                return e.error("Expectected at least one argument.");
            let r = null;
            const n = e.expectedType;
            n && "value" !== n.kind && (r = n);
            const i = [];
            for (const n of t.slice(1)) {
                const t = e.parse(n, 1 + i.length, r, void 0, {
                    typeAnnotation: "omit"
                });
                if (!t)
                    return null;
                r = r || t.type,
                i.push(t);
            }
            const s = n && i.some((t=>ce(n, t.type)));
            return new Rr(s ? ne : r,i)
        }
        evaluate(t) {
            let e, r = null, n = 0;
            for (const i of this.args) {
                if (n++,
                r = i.evaluate(t),
                r && r instanceof be && !r.available && (e || (e = r),
                r = null,
                n === this.args.length))
                    return e;
                if (null !== r)
                    break
            }
            return r
        }
        eachChild(t) {
            this.args.forEach(t);
        }
        outputDefined() {
            return this.args.every((t=>t.outputDefined()))
        }
        serialize() {
            const t = ["coalesce"];
            return this.eachChild((e=>{
                t.push(e.serialize());
            }
            )),
            t
        }
    }
    var jr = Rr;
    class Ur {
        constructor(t, e) {
            this.type = e.type,
            this.bindings = [].concat(t),
            this.result = e;
        }
        evaluate(t) {
            return this.result.evaluate(t)
        }
        eachChild(t) {
            for (const e of this.bindings)
                t(e[1]);
            t(this.result);
        }
        static parse(t, e) {
            if (t.length < 4)
                return e.error(`Expected at least 3 arguments, but found ${t.length - 1} instead.`);
            const r = [];
            for (let n = 1; n < t.length - 1; n += 2) {
                const i = t[n];
                if ("string" != typeof i)
                    return e.error(`Expected string, but found ${typeof i} instead.`, n);
                if (/[^a-zA-Z0-9_]/.test(i))
                    return e.error("Variable names must contain only alphanumeric characters or '_'.", n);
                const s = e.parse(t[n + 1], n + 1);
                if (!s)
                    return null;
                r.push([i, s]);
            }
            const n = e.parse(t[t.length - 1], t.length - 1, e.expectedType, r);
            return n ? new Ur(r,n) : null
        }
        outputDefined() {
            return this.result.outputDefined()
        }
        serialize() {
            const t = ["let"];
            for (const [e,r] of this.bindings)
                t.push(e, r.serialize());
            return t.push(this.result.serialize()),
            t
        }
    }
    var Or = Ur;
    class $r {
        constructor(t, e, r) {
            this.type = t,
            this.index = e,
            this.input = r;
        }
        static parse(t, e) {
            if (3 !== t.length)
                return e.error(`Expected 2 arguments, but found ${t.length - 1} instead.`);
            const r = e.parse(t[1], 1, Wt)
              , n = e.parse(t[2], 2, oe(e.expectedType || ne));
            return r && n ? new $r(n.type.itemType,r,n) : null
        }
        evaluate(t) {
            const e = this.index.evaluate(t)
              , r = this.input.evaluate(t);
            if (e < 0)
                throw new Me(`Array index out of bounds: ${e} < 0.`);
            if (e >= r.length)
                throw new Me(`Array index out of bounds: ${e} > ${r.length - 1}.`);
            if (e !== Math.floor(e))
                throw new Me(`Array index must be an integer, but found ${e} instead.`);
            return r[e]
        }
        eachChild(t) {
            t(this.index),
            t(this.input);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            return ["at", this.index.serialize(), this.input.serialize()]
        }
    }
    var qr = $r;
    class Nr {
        constructor(t, e) {
            this.type = te,
            this.needle = t,
            this.haystack = e;
        }
        static parse(t, e) {
            if (3 !== t.length)
                return e.error(`Expected 2 arguments, but found ${t.length - 1} instead.`);
            const r = e.parse(t[1], 1, ne)
              , n = e.parse(t[2], 2, ne);
            return r && n ? he(r.type, [te, Qt, Wt, Jt, ne]) ? new Nr(r,n) : e.error(`Expected first argument to be of type boolean, string, number or null, but found ${le(r.type)} instead`) : null
        }
        evaluate(t) {
            const e = this.needle.evaluate(t)
              , r = this.haystack.evaluate(t);
            if (null == r)
                return !1;
            if (!pe(e, ["boolean", "string", "number", "null"]))
                throw new Me(`Expected first argument to be of type boolean, string, number or null, but found ${le(Ae(e))} instead.`);
            if (!pe(r, ["string", "array"]))
                throw new Me(`Expected second argument to be of type array or string, but found ${le(Ae(r))} instead.`);
            return r.indexOf(e) >= 0
        }
        eachChild(t) {
            t(this.needle),
            t(this.haystack);
        }
        outputDefined() {
            return !0
        }
        serialize() {
            return ["in", this.needle.serialize(), this.haystack.serialize()]
        }
    }
    var Zr = Nr;
    class Gr {
        constructor(t, e, r) {
            this.type = Wt,
            this.needle = t,
            this.haystack = e,
            this.fromIndex = r;
        }
        static parse(t, e) {
            if (t.length <= 2 || t.length >= 5)
                return e.error(`Expected 3 or 4 arguments, but found ${t.length - 1} instead.`);
            const r = e.parse(t[1], 1, ne)
              , n = e.parse(t[2], 2, ne);
            if (!r || !n)
                return null;
            if (!he(r.type, [te, Qt, Wt, Jt, ne]))
                return e.error(`Expected first argument to be of type boolean, string, number or null, but found ${le(r.type)} instead`);
            if (4 === t.length) {
                const i = e.parse(t[3], 3, Wt);
                return i ? new Gr(r,n,i) : null
            }
            return new Gr(r,n)
        }
        evaluate(t) {
            const e = this.needle.evaluate(t)
              , r = this.haystack.evaluate(t);
            if (!pe(e, ["boolean", "string", "number", "null"]))
                throw new Me(`Expected first argument to be of type boolean, string, number or null, but found ${le(Ae(e))} instead.`);
            if (!pe(r, ["string", "array"]))
                throw new Me(`Expected second argument to be of type array or string, but found ${le(Ae(r))} instead.`);
            if (this.fromIndex) {
                const n = this.fromIndex.evaluate(t);
                return r.indexOf(e, n)
            }
            return r.indexOf(e)
        }
        eachChild(t) {
            t(this.needle),
            t(this.haystack),
            this.fromIndex && t(this.fromIndex);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            if (null != this.fromIndex && void 0 !== this.fromIndex) {
                const t = this.fromIndex.serialize();
                return ["index-of", this.needle.serialize(), this.haystack.serialize(), t]
            }
            return ["index-of", this.needle.serialize(), this.haystack.serialize()]
        }
    }
    var Xr = Gr;
    class Yr {
        constructor(t, e, r, n, i, s) {
            this.inputType = t,
            this.type = e,
            this.input = r,
            this.cases = n,
            this.outputs = i,
            this.otherwise = s;
        }
        static parse(t, e) {
            if (t.length < 5)
                return e.error(`Expected at least 4 arguments, but found only ${t.length - 1}.`);
            if (t.length % 2 != 1)
                return e.error("Expected an even number of arguments.");
            let r, n;
            e.expectedType && "value" !== e.expectedType.kind && (n = e.expectedType);
            const i = {}
              , s = [];
            for (let a = 2; a < t.length - 1; a += 2) {
                let o = t[a];
                const l = t[a + 1];
                Array.isArray(o) || (o = [o]);
                const u = e.concat(a);
                if (0 === o.length)
                    return u.error("Expected at least one branch label.");
                for (const t of o) {
                    if ("number" != typeof t && "string" != typeof t)
                        return u.error("Branch labels must be numbers or strings.");
                    if ("number" == typeof t && Math.abs(t) > Number.MAX_SAFE_INTEGER)
                        return u.error(`Branch labels must be integers no larger than ${Number.MAX_SAFE_INTEGER}.`);
                    if ("number" == typeof t && Math.floor(t) !== t)
                        return u.error("Numeric branch labels must be integer values.");
                    if (r) {
                        if (u.checkSubtype(r, Ae(t)))
                            return null
                    } else
                        r = Ae(t);
                    if (void 0 !== i[String(t)])
                        return u.error("Branch labels must be unique.");
                    i[String(t)] = s.length;
                }
                const c = e.parse(l, a, n);
                if (!c)
                    return null;
                n = n || c.type,
                s.push(c);
            }
            const a = e.parse(t[1], 1, ne);
            if (!a)
                return null;
            const o = e.parse(t[t.length - 1], t.length - 1, n);
            return o ? "value" !== a.type.kind && e.concat(1).checkSubtype(r, a.type) ? null : new Yr(r,n,a,i,s,o) : null
        }
        evaluate(t) {
            const e = this.input.evaluate(t);
            return (Ae(e) === this.inputType && this.outputs[this.cases[e]] || this.otherwise).evaluate(t)
        }
        eachChild(t) {
            t(this.input),
            this.outputs.forEach(t),
            t(this.otherwise);
        }
        outputDefined() {
            return this.outputs.every((t=>t.outputDefined())) && this.otherwise.outputDefined()
        }
        serialize() {
            const t = ["match", this.input.serialize()]
              , e = Object.keys(this.cases).sort()
              , r = []
              , n = {};
            for (const t of e) {
                const e = n[this.cases[t]];
                void 0 === e ? (n[this.cases[t]] = r.length,
                r.push([this.cases[t], [t]])) : r[e][1].push(t);
            }
            const i = t=>"number" === this.inputType.kind ? Number(t) : t;
            for (const [e,n] of r)
                t.push(1 === n.length ? i(n[0]) : n.map(i)),
                t.push(this.outputs[e].serialize());
            return t.push(this.otherwise.serialize()),
            t
        }
    }
    var Hr = Yr;
    class Kr {
        constructor(t, e, r) {
            this.type = t,
            this.branches = e,
            this.otherwise = r;
        }
        static parse(t, e) {
            if (t.length < 4)
                return e.error(`Expected at least 3 arguments, but found only ${t.length - 1}.`);
            if (t.length % 2 != 0)
                return e.error("Expected an odd number of arguments.");
            let r;
            e.expectedType && "value" !== e.expectedType.kind && (r = e.expectedType);
            const n = [];
            for (let i = 1; i < t.length - 1; i += 2) {
                const s = e.parse(t[i], i, te);
                if (!s)
                    return null;
                const a = e.parse(t[i + 1], i + 1, r);
                if (!a)
                    return null;
                n.push([s, a]),
                r = r || a.type;
            }
            const i = e.parse(t[t.length - 1], t.length - 1, r);
            return i ? new Kr(r,n,i) : null
        }
        evaluate(t) {
            for (const [e,r] of this.branches)
                if (e.evaluate(t))
                    return r.evaluate(t);
            return this.otherwise.evaluate(t)
        }
        eachChild(t) {
            for (const [e,r] of this.branches)
                t(e),
                t(r);
            t(this.otherwise);
        }
        outputDefined() {
            return this.branches.every((([t,e])=>e.outputDefined())) && this.otherwise.outputDefined()
        }
        serialize() {
            const t = ["case"];
            return this.eachChild((e=>{
                t.push(e.serialize());
            }
            )),
            t
        }
    }
    var Jr = Kr;
    class Wr {
        constructor(t, e, r, n) {
            this.type = t,
            this.input = e,
            this.beginIndex = r,
            this.endIndex = n;
        }
        static parse(t, e) {
            if (t.length <= 2 || t.length >= 5)
                return e.error(`Expected 3 or 4 arguments, but found ${t.length - 1} instead.`);
            const r = e.parse(t[1], 1, ne)
              , n = e.parse(t[2], 2, Wt);
            if (!r || !n)
                return null;
            if (!he(r.type, [oe(ne), Qt, ne]))
                return e.error(`Expected first argument to be of type array or string, but found ${le(r.type)} instead`);
            if (4 === t.length) {
                const i = e.parse(t[3], 3, Wt);
                return i ? new Wr(r.type,r,n,i) : null
            }
            return new Wr(r.type,r,n)
        }
        evaluate(t) {
            const e = this.input.evaluate(t)
              , r = this.beginIndex.evaluate(t);
            if (!pe(e, ["string", "array"]))
                throw new Me(`Expected first argument to be of type array or string, but found ${le(Ae(e))} instead.`);
            if (this.endIndex) {
                const n = this.endIndex.evaluate(t);
                return e.slice(r, n)
            }
            return e.slice(r)
        }
        eachChild(t) {
            t(this.input),
            t(this.beginIndex),
            this.endIndex && t(this.endIndex);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            if (null != this.endIndex && void 0 !== this.endIndex) {
                const t = this.endIndex.serialize();
                return ["slice", this.input.serialize(), this.beginIndex.serialize(), t]
            }
            return ["slice", this.input.serialize(), this.beginIndex.serialize()]
        }
    }
    var Qr = Wr;
    function tn(t, e) {
        return "==" === t || "!=" === t ? "boolean" === e.kind || "string" === e.kind || "number" === e.kind || "null" === e.kind || "value" === e.kind : "string" === e.kind || "number" === e.kind || "value" === e.kind
    }
    function en(t, e, r, n) {
        return 0 === n.compare(e, r)
    }
    function rn(t, e, r) {
        const n = "==" !== t && "!=" !== t;
        return class i {
            constructor(t, e, r) {
                this.type = te,
                this.lhs = t,
                this.rhs = e,
                this.collator = r,
                this.hasUntypedArgument = "value" === t.type.kind || "value" === e.type.kind;
            }
            static parse(t, e) {
                if (3 !== t.length && 4 !== t.length)
                    return e.error("Expected two or three arguments.");
                const r = t[0];
                let s = e.parse(t[1], 1, ne);
                if (!s)
                    return null;
                if (!tn(r, s.type))
                    return e.concat(1).error(`"${r}" comparisons are not supported for type '${le(s.type)}'.`);
                let a = e.parse(t[2], 2, ne);
                if (!a)
                    return null;
                if (!tn(r, a.type))
                    return e.concat(2).error(`"${r}" comparisons are not supported for type '${le(a.type)}'.`);
                if (s.type.kind !== a.type.kind && "value" !== s.type.kind && "value" !== a.type.kind)
                    return e.error(`Cannot compare types '${le(s.type)}' and '${le(a.type)}'.`);
                n && ("value" === s.type.kind && "value" !== a.type.kind ? s = new Be(a.type,[s]) : "value" !== s.type.kind && "value" === a.type.kind && (a = new Be(s.type,[a])));
                let o = null;
                if (4 === t.length) {
                    if ("string" !== s.type.kind && "string" !== a.type.kind && "value" !== s.type.kind && "value" !== a.type.kind)
                        return e.error("Cannot use collator to compare non-string types.");
                    if (o = e.parse(t[3], 3, ie),
                    !o)
                        return null
                }
                return new i(s,a,o)
            }
            evaluate(i) {
                const s = this.lhs.evaluate(i)
                  , a = this.rhs.evaluate(i);
                if (n && this.hasUntypedArgument) {
                    const e = Ae(s)
                      , r = Ae(a);
                    if (e.kind !== r.kind || "string" !== e.kind && "number" !== e.kind)
                        throw new Me(`Expected arguments for "${t}" to be (string, string) or (number, number), but found (${e.kind}, ${r.kind}) instead.`)
                }
                if (this.collator && !n && this.hasUntypedArgument) {
                    const t = Ae(s)
                      , r = Ae(a);
                    if ("string" !== t.kind || "string" !== r.kind)
                        return e(i, s, a)
                }
                return this.collator ? r(i, s, a, this.collator.evaluate(i)) : e(i, s, a)
            }
            eachChild(t) {
                t(this.lhs),
                t(this.rhs),
                this.collator && t(this.collator);
            }
            outputDefined() {
                return !0
            }
            serialize() {
                const e = [t];
                return this.eachChild((t=>{
                    e.push(t.serialize());
                }
                )),
                e
            }
        }
    }
    const nn = rn("==", (function(t, e, r) {
        return e === r
    }
    ), en)
      , sn = rn("!=", (function(t, e, r) {
        return e !== r
    }
    ), (function(t, e, r, n) {
        return !en(0, e, r, n)
    }
    ))
      , an = rn("<", (function(t, e, r) {
        return e < r
    }
    ), (function(t, e, r, n) {
        return n.compare(e, r) < 0
    }
    ))
      , on = rn(">", (function(t, e, r) {
        return e > r
    }
    ), (function(t, e, r, n) {
        return n.compare(e, r) > 0
    }
    ))
      , ln = rn("<=", (function(t, e, r) {
        return e <= r
    }
    ), (function(t, e, r, n) {
        return n.compare(e, r) <= 0
    }
    ))
      , un = rn(">=", (function(t, e, r) {
        return e >= r
    }
    ), (function(t, e, r, n) {
        return n.compare(e, r) >= 0
    }
    ));
    class cn {
        constructor(t, e, r, n, i, s) {
            this.type = Qt,
            this.number = t,
            this.locale = e,
            this.currency = r,
            this.unit = n,
            this.minFractionDigits = i,
            this.maxFractionDigits = s;
        }
        static parse(t, e) {
            if (3 !== t.length)
                return e.error("Expected two arguments.");
            const r = e.parse(t[1], 1, Wt);
            if (!r)
                return null;
            const n = t[2];
            if ("object" != typeof n || Array.isArray(n))
                return e.error("NumberFormat options argument must be an object.");
            let i = null;
            if (n.locale && (i = e.parse(n.locale, 1, Qt),
            !i))
                return null;
            let s = null;
            if (n.currency && (s = e.parse(n.currency, 1, Qt),
            !s))
                return null;
            let a = null;
            if (n.unit && (a = e.parse(n.unit, 1, Qt),
            !a))
                return null;
            let o = null;
            if (n["min-fraction-digits"] && (o = e.parse(n["min-fraction-digits"], 1, Wt),
            !o))
                return null;
            let l = null;
            return n["max-fraction-digits"] && (l = e.parse(n["max-fraction-digits"], 1, Wt),
            !l) ? null : new cn(r,i,s,a,o,l)
        }
        evaluate(t) {
            return new Intl.NumberFormat(this.locale ? this.locale.evaluate(t) : [],{
                style: (this.currency ? "currency" : this.unit && "unit") || "decimal",
                currency: this.currency ? this.currency.evaluate(t) : void 0,
                unit: this.unit ? this.unit.evaluate(t) : void 0,
                minimumFractionDigits: this.minFractionDigits ? this.minFractionDigits.evaluate(t) : void 0,
                maximumFractionDigits: this.maxFractionDigits ? this.maxFractionDigits.evaluate(t) : void 0
            }).format(this.number.evaluate(t))
        }
        eachChild(t) {
            t(this.number),
            this.locale && t(this.locale),
            this.currency && t(this.currency),
            this.unit && t(this.unit),
            this.minFractionDigits && t(this.minFractionDigits),
            this.maxFractionDigits && t(this.maxFractionDigits);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            const t = {};
            return this.locale && (t.locale = this.locale.serialize()),
            this.currency && (t.currency = this.currency.serialize()),
            this.unit && (t.unit = this.unit.serialize()),
            this.minFractionDigits && (t["min-fraction-digits"] = this.minFractionDigits.serialize()),
            this.maxFractionDigits && (t["max-fraction-digits"] = this.maxFractionDigits.serialize()),
            ["number-format", this.number.serialize(), t]
        }
    }
    class hn {
        constructor(t) {
            this.type = Wt,
            this.input = t;
        }
        static parse(t, e) {
            if (2 !== t.length)
                return e.error(`Expected 1 argument, but found ${t.length - 1} instead.`);
            const r = e.parse(t[1], 1);
            return r ? "array" !== r.type.kind && "string" !== r.type.kind && "value" !== r.type.kind ? e.error(`Expected argument of type string or array, but found ${le(r.type)} instead.`) : new hn(r) : null
        }
        evaluate(t) {
            const e = this.input.evaluate(t);
            if ("string" == typeof e)
                return e.length;
            if (Array.isArray(e))
                return e.length;
            throw new Me(`Expected value to be of type string or array, but found ${le(Ae(e))} instead.`)
        }
        eachChild(t) {
            t(this.input);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            const t = ["length"];
            return this.eachChild((e=>{
                t.push(e.serialize());
            }
            )),
            t
        }
    }
    const pn = {
        "==": nn,
        "!=": sn,
        ">": on,
        "<": an,
        ">=": un,
        "<=": ln,
        array: Be,
        at: qr,
        boolean: Be,
        case: Jr,
        coalesce: jr,
        collator: Ue,
        format: Ce,
        image: Ve,
        in: Zr,
        "index-of": Xr,
        interpolate: Lr,
        "interpolate-hcl": Lr,
        "interpolate-lab": Lr,
        length: hn,
        let: Or,
        literal: Se,
        match: Hr,
        number: Be,
        "number-format": cn,
        object: Be,
        slice: Qr,
        step: yr,
        string: Be,
        "to-boolean": Ee,
        "to-color": Ee,
        "to-number": Ee,
        "to-string": Ee,
        var: ur,
        within: ir
    };
    function fn(t, [e,r,n,i]) {
        e = e.evaluate(t),
        r = r.evaluate(t),
        n = n.evaluate(t);
        const s = i ? i.evaluate(t) : 1
          , a = _e(e, r, n, s);
        if (a)
            throw new Me(a);
        return new me(e / 255 * s,r / 255 * s,n / 255 * s,s)
    }
    function dn(t, e) {
        return t in e
    }
    function yn(t, e) {
        const r = e[t];
        return void 0 === r ? null : r
    }
    function mn(t) {
        return {
            type: t
        }
    }
    je.register(pn, {
        error: [{
            kind: "error"
        }, [Qt], (t,[e])=>{
            throw new Me(e.evaluate(t))
        }
        ],
        typeof: [Qt, [ne], (t,[e])=>le(Ae(e.evaluate(t)))],
        "to-rgba": [oe(Wt, 4), [ee], (t,[e])=>e.evaluate(t).toArray()],
        rgb: [ee, [Wt, Wt, Wt], fn],
        rgba: [ee, [Wt, Wt, Wt, Wt], fn],
        has: {
            type: te,
            overloads: [[[Qt], (t,[e])=>dn(e.evaluate(t), t.properties())], [[Qt, re], (t,[e,r])=>dn(e.evaluate(t), r.evaluate(t))]]
        },
        get: {
            type: ne,
            overloads: [[[Qt], (t,[e])=>yn(e.evaluate(t), t.properties())], [[Qt, re], (t,[e,r])=>yn(e.evaluate(t), r.evaluate(t))]]
        },
        "feature-state": [ne, [Qt], (t,[e])=>yn(e.evaluate(t), t.featureState || {})],
        properties: [re, [], t=>t.properties()],
        "geometry-type": [Qt, [], t=>t.geometryType()],
        id: [ne, [], t=>t.id()],
        zoom: [Wt, [], t=>t.globals.zoom],
        pitch: [Wt, [], t=>t.globals.pitch || 0],
        "distance-from-center": [Wt, [], t=>t.distanceFromCenter()],
        "heatmap-density": [Wt, [], t=>t.globals.heatmapDensity || 0],
        "line-progress": [Wt, [], t=>t.globals.lineProgress || 0],
        "sky-radial-progress": [Wt, [], t=>t.globals.skyRadialProgress || 0],
        accumulated: [ne, [], t=>void 0 === t.globals.accumulated ? null : t.globals.accumulated],
        "+": [Wt, mn(Wt), (t,e)=>{
            let r = 0;
            for (const n of e)
                r += n.evaluate(t);
            return r
        }
        ],
        "*": [Wt, mn(Wt), (t,e)=>{
            let r = 1;
            for (const n of e)
                r *= n.evaluate(t);
            return r
        }
        ],
        "-": {
            type: Wt,
            overloads: [[[Wt, Wt], (t,[e,r])=>e.evaluate(t) - r.evaluate(t)], [[Wt], (t,[e])=>-e.evaluate(t)]]
        },
        "/": [Wt, [Wt, Wt], (t,[e,r])=>e.evaluate(t) / r.evaluate(t)],
        "%": [Wt, [Wt, Wt], (t,[e,r])=>e.evaluate(t) % r.evaluate(t)],
        ln2: [Wt, [], ()=>Math.LN2],
        pi: [Wt, [], ()=>Math.PI],
        e: [Wt, [], ()=>Math.E],
        "^": [Wt, [Wt, Wt], (t,[e,r])=>Math.pow(e.evaluate(t), r.evaluate(t))],
        sqrt: [Wt, [Wt], (t,[e])=>Math.sqrt(e.evaluate(t))],
        log10: [Wt, [Wt], (t,[e])=>Math.log(e.evaluate(t)) / Math.LN10],
        ln: [Wt, [Wt], (t,[e])=>Math.log(e.evaluate(t))],
        log2: [Wt, [Wt], (t,[e])=>Math.log(e.evaluate(t)) / Math.LN2],
        sin: [Wt, [Wt], (t,[e])=>Math.sin(e.evaluate(t))],
        cos: [Wt, [Wt], (t,[e])=>Math.cos(e.evaluate(t))],
        tan: [Wt, [Wt], (t,[e])=>Math.tan(e.evaluate(t))],
        asin: [Wt, [Wt], (t,[e])=>Math.asin(e.evaluate(t))],
        acos: [Wt, [Wt], (t,[e])=>Math.acos(e.evaluate(t))],
        atan: [Wt, [Wt], (t,[e])=>Math.atan(e.evaluate(t))],
        min: [Wt, mn(Wt), (t,e)=>Math.min(...e.map((e=>e.evaluate(t))))],
        max: [Wt, mn(Wt), (t,e)=>Math.max(...e.map((e=>e.evaluate(t))))],
        abs: [Wt, [Wt], (t,[e])=>Math.abs(e.evaluate(t))],
        round: [Wt, [Wt], (t,[e])=>{
            const r = e.evaluate(t);
            return r < 0 ? -Math.round(-r) : Math.round(r)
        }
        ],
        floor: [Wt, [Wt], (t,[e])=>Math.floor(e.evaluate(t))],
        ceil: [Wt, [Wt], (t,[e])=>Math.ceil(e.evaluate(t))],
        "filter-==": [te, [Qt, ne], (t,[e,r])=>t.properties()[e.value] === r.value],
        "filter-id-==": [te, [ne], (t,[e])=>t.id() === e.value],
        "filter-type-==": [te, [Qt], (t,[e])=>t.geometryType() === e.value],
        "filter-<": [te, [Qt, ne], (t,[e,r])=>{
            const n = t.properties()[e.value]
              , i = r.value;
            return typeof n == typeof i && n < i
        }
        ],
        "filter-id-<": [te, [ne], (t,[e])=>{
            const r = t.id()
              , n = e.value;
            return typeof r == typeof n && r < n
        }
        ],
        "filter->": [te, [Qt, ne], (t,[e,r])=>{
            const n = t.properties()[e.value]
              , i = r.value;
            return typeof n == typeof i && n > i
        }
        ],
        "filter-id->": [te, [ne], (t,[e])=>{
            const r = t.id()
              , n = e.value;
            return typeof r == typeof n && r > n
        }
        ],
        "filter-<=": [te, [Qt, ne], (t,[e,r])=>{
            const n = t.properties()[e.value]
              , i = r.value;
            return typeof n == typeof i && n <= i
        }
        ],
        "filter-id-<=": [te, [ne], (t,[e])=>{
            const r = t.id()
              , n = e.value;
            return typeof r == typeof n && r <= n
        }
        ],
        "filter->=": [te, [Qt, ne], (t,[e,r])=>{
            const n = t.properties()[e.value]
              , i = r.value;
            return typeof n == typeof i && n >= i
        }
        ],
        "filter-id->=": [te, [ne], (t,[e])=>{
            const r = t.id()
              , n = e.value;
            return typeof r == typeof n && r >= n
        }
        ],
        "filter-has": [te, [ne], (t,[e])=>e.value in t.properties()],
        "filter-has-id": [te, [], t=>null !== t.id() && void 0 !== t.id()],
        "filter-type-in": [te, [oe(Qt)], (t,[e])=>e.value.indexOf(t.geometryType()) >= 0],
        "filter-id-in": [te, [oe(ne)], (t,[e])=>e.value.indexOf(t.id()) >= 0],
        "filter-in-small": [te, [Qt, oe(ne)], (t,[e,r])=>r.value.indexOf(t.properties()[e.value]) >= 0],
        "filter-in-large": [te, [Qt, oe(ne)], (t,[e,r])=>function(t, e, r, n) {
            for (; r <= n; ) {
                const i = r + n >> 1;
                if (e[i] === t)
                    return !0;
                e[i] > t ? n = i - 1 : r = i + 1;
            }
            return !1
        }(t.properties()[e.value], r.value, 0, r.value.length - 1)],
        all: {
            type: te,
            overloads: [[[te, te], (t,[e,r])=>e.evaluate(t) && r.evaluate(t)], [mn(te), (t,e)=>{
                for (const r of e)
                    if (!r.evaluate(t))
                        return !1;
                return !0
            }
            ]]
        },
        any: {
            type: te,
            overloads: [[[te, te], (t,[e,r])=>e.evaluate(t) || r.evaluate(t)], [mn(te), (t,e)=>{
                for (const r of e)
                    if (r.evaluate(t))
                        return !0;
                return !1
            }
            ]]
        },
        "!": [te, [te], (t,[e])=>!e.evaluate(t)],
        "is-supported-script": [te, [Qt], (t,[e])=>{
            const r = t.globals && t.globals.isSupportedScript;
            return !r || r(e.evaluate(t))
        }
        ],
        upcase: [Qt, [Qt], (t,[e])=>e.evaluate(t).toUpperCase()],
        downcase: [Qt, [Qt], (t,[e])=>e.evaluate(t).toLowerCase()],
        concat: [Qt, mn(ne), (t,e)=>e.map((e=>ke(e.evaluate(t)))).join("")],
        "resolved-locale": [Qt, [ie], (t,[e])=>e.evaluate(t).resolvedLocale()]
    });
    var gn = pn;
    function xn(t) {
        return {
            result: "success",
            value: t
        }
    }
    function vn(t) {
        return {
            result: "error",
            value: t
        }
    }
    function bn(t) {
        return "data-driven" === t["property-type"] || "cross-faded-data-driven" === t["property-type"]
    }
    function _n(t) {
        return !!t.expression && t.expression.parameters.indexOf("zoom") > -1
    }
    function wn(t) {
        return !!t.expression && t.expression.interpolated
    }
    function An(t) {
        return t instanceof Number ? "number" : t instanceof String ? "string" : t instanceof Boolean ? "boolean" : Array.isArray(t) ? "array" : null === t ? "null" : typeof t
    }
    function kn(t) {
        return "object" == typeof t && null !== t && !Array.isArray(t)
    }
    function zn(t) {
        return t
    }
    function Sn(t, e) {
        const r = "color" === e.type
          , n = t.stops && "object" == typeof t.stops[0][0]
          , i = n || !(n || void 0 !== t.property)
          , s = t.type || (wn(e) ? "exponential" : "interval");
        if (r && ((t = Nt({}, t)).stops && (t.stops = t.stops.map((t=>[t[0], me.parse(t[1])]))),
        t.default = me.parse(t.default ? t.default : e.default)),
        t.colorSpace && "rgb" !== t.colorSpace && !Dr[t.colorSpace])
            throw new Error(`Unknown color space: ${t.colorSpace}`);
        let a, o, l;
        if ("exponential" === s)
            a = Bn;
        else if ("interval" === s)
            a = Tn;
        else if ("categorical" === s) {
            a = In,
            o = Object.create(null);
            for (const e of t.stops)
                o[e[0]] = e[1];
            l = typeof t.stops[0][0];
        } else {
            if ("identity" !== s)
                throw new Error(`Unknown function type "${s}"`);
            a = Cn;
        }
        if (n) {
            const r = {}
              , n = [];
            for (let e = 0; e < t.stops.length; e++) {
                const i = t.stops[e]
                  , s = i[0].zoom;
                void 0 === r[s] && (r[s] = {
                    zoom: s,
                    type: t.type,
                    property: t.property,
                    default: t.default,
                    stops: []
                },
                n.push(s)),
                r[s].stops.push([i[0].value, i[1]]);
            }
            const i = [];
            for (const t of n)
                i.push([r[t].zoom, Sn(r[t], e)]);
            const s = {
                name: "linear"
            };
            return {
                kind: "composite",
                interpolationType: s,
                interpolationFactor: Lr.interpolationFactor.bind(void 0, s),
                zoomStops: i.map((t=>t[0])),
                evaluate: ({zoom: r},n)=>Bn({
                    stops: i,
                    base: t.base
                }, e, r).evaluate(r, n)
            }
        }
        if (i) {
            const r = "exponential" === s ? {
                name: "exponential",
                base: void 0 !== t.base ? t.base : 1
            } : null;
            return {
                kind: "camera",
                interpolationType: r,
                interpolationFactor: Lr.interpolationFactor.bind(void 0, r),
                zoomStops: t.stops.map((t=>t[0])),
                evaluate: ({zoom: r})=>a(t, e, r, o, l)
            }
        }
        return {
            kind: "source",
            evaluate(r, n) {
                const i = n && n.properties ? n.properties[t.property] : void 0;
                return void 0 === i ? Mn(t.default, e.default) : a(t, e, i, o, l)
            }
        }
    }
    function Mn(t, e, r) {
        return void 0 !== t ? t : void 0 !== e ? e : void 0 !== r ? r : void 0
    }
    function In(t, e, r, n, i) {
        return Mn(typeof r === i ? n[r] : void 0, t.default, e.default)
    }
    function Tn(t, e, r) {
        if ("number" !== An(r))
            return Mn(t.default, e.default);
        const n = t.stops.length;
        if (1 === n)
            return t.stops[0][1];
        if (r <= t.stops[0][0])
            return t.stops[0][1];
        if (r >= t.stops[n - 1][0])
            return t.stops[n - 1][1];
        const i = fr(t.stops.map((t=>t[0])), r);
        return t.stops[i][1]
    }
    function Bn(t, e, r) {
        const n = void 0 !== t.base ? t.base : 1;
        if ("number" !== An(r))
            return Mn(t.default, e.default);
        const i = t.stops.length;
        if (1 === i)
            return t.stops[0][1];
        if (r <= t.stops[0][0])
            return t.stops[0][1];
        if (r >= t.stops[i - 1][0])
            return t.stops[i - 1][1];
        const s = fr(t.stops.map((t=>t[0])), r)
          , a = function(t, e, r, n) {
            const i = n - r
              , s = t - r;
            return 0 === i ? 0 : 1 === e ? s / i : (Math.pow(e, s) - 1) / (Math.pow(e, i) - 1)
        }(r, n, t.stops[s][0], t.stops[s + 1][0])
          , o = t.stops[s][1]
          , l = t.stops[s + 1][1];
        let u = gr[e.type] || zn;
        if (t.colorSpace && "rgb" !== t.colorSpace) {
            const e = Dr[t.colorSpace];
            u = (t,r)=>e.reverse(e.interpolate(e.forward(t), e.forward(r), a));
        }
        return "function" == typeof o.evaluate ? {
            evaluate(...t) {
                const e = o.evaluate.apply(void 0, t)
                  , r = l.evaluate.apply(void 0, t);
                if (void 0 !== e && void 0 !== r)
                    return u(e, r, a)
            }
        } : u(o, l, a)
    }
    function Cn(t, e, r) {
        return "color" === e.type ? r = me.parse(r) : "formatted" === e.type ? r = ve.fromString(r.toString()) : "resolvedImage" === e.type ? r = be.fromString(r.toString()) : An(r) === e.type || "enum" === e.type && e.values[r] || (r = void 0),
        Mn(r, t.default, e.default)
    }
    class Vn {
        constructor(t, e) {
            this.expression = t,
            this._warningHistory = {},
            this._evaluator = new Le,
            this._defaultValue = e ? function(t) {
                return "color" === t.type && (kn(t.default) || Array.isArray(t.default)) ? new me(0,0,0,0) : "color" === t.type ? me.parse(t.default) || null : void 0 === t.default ? null : t.default
            }(e) : null,
            this._enumValues = e && "enum" === e.type ? e.values : null;
        }
        evaluateWithoutErrorHandling(t, e, r, n, i, s, a, o) {
            return this._evaluator.globals = t,
            this._evaluator.feature = e,
            this._evaluator.featureState = r,
            this._evaluator.canonical = n || null,
            this._evaluator.availableImages = i || null,
            this._evaluator.formattedSection = s,
            this._evaluator.featureTileCoord = a || null,
            this._evaluator.featureDistanceData = o || null,
            this.expression.evaluate(this._evaluator)
        }
        evaluate(t, e, r, n, i, s, a, o) {
            this._evaluator.globals = t,
            this._evaluator.feature = e || null,
            this._evaluator.featureState = r || null,
            this._evaluator.canonical = n || null,
            this._evaluator.availableImages = i || null,
            this._evaluator.formattedSection = s || null,
            this._evaluator.featureTileCoord = a || null,
            this._evaluator.featureDistanceData = o || null;
            try {
                const t = this.expression.evaluate(this._evaluator);
                if (null == t || "number" == typeof t && t != t)
                    return this._defaultValue;
                if (this._enumValues && !(t in this._enumValues))
                    throw new Me(`Expected value to be one of ${Object.keys(this._enumValues).map((t=>JSON.stringify(t))).join(", ")}, but found ${JSON.stringify(t)} instead.`);
                return t
            } catch (t) {
                return this._warningHistory[t.message] || (this._warningHistory[t.message] = !0,
                "undefined" != typeof console && console.warn(t.message)),
                this._defaultValue
            }
        }
    }
    function Pn(t) {
        return Array.isArray(t) && t.length > 0 && "string" == typeof t[0] && t[0]in gn
    }
    function Dn(t, e) {
        const r = new hr(gn,[],e ? function(t) {
            const e = {
                color: ee,
                string: Qt,
                number: Wt,
                enum: Qt,
                boolean: te,
                formatted: se,
                resolvedImage: ae
            };
            return "array" === t.type ? oe(e[t.value] || ne, t.length) : e[t.type]
        }(e) : void 0)
          , n = r.parse(t, void 0, void 0, void 0, e && "string" === e.type ? {
            typeAnnotation: "coerce"
        } : void 0);
        return n ? xn(new Vn(n,e)) : vn(r.errors)
    }
    class En {
        constructor(t, e) {
            this.kind = t,
            this._styleExpression = e,
            this.isStateDependent = "constant" !== t && !ar(e.expression);
        }
        evaluateWithoutErrorHandling(t, e, r, n, i, s) {
            return this._styleExpression.evaluateWithoutErrorHandling(t, e, r, n, i, s)
        }
        evaluate(t, e, r, n, i, s) {
            return this._styleExpression.evaluate(t, e, r, n, i, s)
        }
    }
    class Fn {
        constructor(t, e, r, n) {
            this.kind = t,
            this.zoomStops = r,
            this._styleExpression = e,
            this.isStateDependent = "camera" !== t && !ar(e.expression),
            this.interpolationType = n;
        }
        evaluateWithoutErrorHandling(t, e, r, n, i, s) {
            return this._styleExpression.evaluateWithoutErrorHandling(t, e, r, n, i, s)
        }
        evaluate(t, e, r, n, i, s) {
            return this._styleExpression.evaluate(t, e, r, n, i, s)
        }
        interpolationFactor(t, e, r) {
            return this.interpolationType ? Lr.interpolationFactor(this.interpolationType, t, e, r) : 0
        }
    }
    function Ln(t, e) {
        if ("error" === (t = Dn(t, e)).result)
            return t;
        const r = t.value.expression
          , n = sr(r);
        if (!n && !bn(e))
            return vn([new Yt("","data expressions not supported")]);
        const i = or(r, ["zoom", "pitch", "distance-from-center"]);
        if (!i && !_n(e))
            return vn([new Yt("","zoom expressions not supported")]);
        const s = jn(r);
        return s || i ? s instanceof Yt ? vn([s]) : s instanceof Lr && !wn(e) ? vn([new Yt("",'"interpolate" expressions cannot be used with this property')]) : xn(s ? new Fn(n ? "camera" : "composite",t.value,s.labels,s instanceof Lr ? s.interpolation : void 0) : new En(n ? "constant" : "source",t.value)) : vn([new Yt("",'"zoom" expression may only be used as input to a top-level "step" or "interpolate" expression.')])
    }
    class Rn {
        constructor(t, e) {
            this._parameters = t,
            this._specification = e,
            Nt(this, Sn(this._parameters, this._specification));
        }
        static deserialize(t) {
            return new Rn(t._parameters,t._specification)
        }
        static serialize(t) {
            return {
                _parameters: t._parameters,
                _specification: t._specification
            }
        }
    }
    function jn(t) {
        let e = null;
        if (t instanceof Or)
            e = jn(t.result);
        else if (t instanceof jr) {
            for (const r of t.args)
                if (e = jn(r),
                e)
                    break
        } else
            (t instanceof yr || t instanceof Lr) && t.input instanceof je && "zoom" === t.input.name && (e = t);
        return e instanceof Yt || t.eachChild((t=>{
            const r = jn(t);
            r instanceof Yt ? e = r : !e && r ? e = new Yt("",'"zoom" expression may only be used as input to a top-level "step" or "interpolate" expression.') : e && r && e !== r && (e = new Yt("",'Only one zoom-based "step" or "interpolate" subexpression may be used in an expression.'));
        }
        )),
        e
    }
    class Un {
        constructor(t, e, r, n) {
            this.message = (t ? `${t}: ` : "") + r,
            n && (this.identifier = n),
            null != e && e.__line__ && (this.line = e.__line__);
        }
    }
    function On(t) {
        const e = t.key
          , r = t.value
          , n = t.valueSpec || {}
          , i = t.objectElementValidators || {}
          , s = t.style
          , a = t.styleSpec;
        let o = [];
        const l = An(r);
        if ("object" !== l)
            return [new Un(e,r,`object expected, ${l} found`)];
        for (const t in r) {
            const l = t.split(".")[0]
              , u = n[l] || n["*"];
            let c;
            i[l] ? c = i[l] : n[l] ? c = bi : i["*"] ? c = i["*"] : n["*"] && (c = bi),
            c ? o = o.concat(c({
                key: (e ? `${e}.` : e) + t,
                value: r[t],
                valueSpec: u,
                style: s,
                styleSpec: a,
                object: r,
                objectKey: t
            }, r)) : o.push(new Un(e,r[t],`unknown property "${t}"`));
        }
        for (const t in n)
            i[t] || n[t].required && void 0 === n[t].default && void 0 === r[t] && o.push(new Un(e,r,`missing required property "${t}"`));
        return o
    }
    function $n(t) {
        const e = t.value
          , r = t.valueSpec
          , n = t.style
          , i = t.styleSpec
          , s = t.key
          , a = t.arrayElementValidator || bi;
        if ("array" !== An(e))
            return [new Un(s,e,`array expected, ${An(e)} found`)];
        if (r.length && e.length !== r.length)
            return [new Un(s,e,`array length ${r.length} expected, length ${e.length} found`)];
        if (r["min-length"] && e.length < r["min-length"])
            return [new Un(s,e,`array length at least ${r["min-length"]} expected, length ${e.length} found`)];
        let o = {
            type: r.value,
            values: r.values,
            minimum: r.minimum,
            maximum: r.maximum,
            function: void 0
        };
        i.$version < 7 && (o.function = r.function),
        "object" === An(r.value) && (o = r.value);
        let l = [];
        for (let t = 0; t < e.length; t++)
            l = l.concat(a({
                array: e,
                arrayIndex: t,
                value: e[t],
                valueSpec: o,
                style: n,
                styleSpec: i,
                key: `${s}[${t}]`
            }));
        return l
    }
    function qn(t) {
        const e = t.key
          , r = t.value
          , n = t.valueSpec;
        let i = An(r);
        if ("number" === i && r != r && (i = "NaN"),
        "number" !== i)
            return [new Un(e,r,`number expected, ${i} found`)];
        if ("minimum"in n) {
            let i = n.minimum;
            if ("array" === An(n.minimum) && (i = n.minimum[t.arrayIndex]),
            r < i)
                return [new Un(e,r,`${r} is less than the minimum value ${i}`)]
        }
        if ("maximum"in n) {
            let i = n.maximum;
            if ("array" === An(n.maximum) && (i = n.maximum[t.arrayIndex]),
            r > i)
                return [new Un(e,r,`${r} is greater than the maximum value ${i}`)]
        }
        return []
    }
    function Nn(t) {
        const e = t.valueSpec
          , r = Zt(t.value.type);
        let n, i, s, a = {};
        const o = "categorical" !== r && void 0 === t.value.property
          , l = !o
          , u = "array" === An(t.value.stops) && "array" === An(t.value.stops[0]) && "object" === An(t.value.stops[0][0])
          , c = On({
            key: t.key,
            value: t.value,
            valueSpec: t.styleSpec.function,
            style: t.style,
            styleSpec: t.styleSpec,
            objectElementValidators: {
                stops: function(t) {
                    if ("identity" === r)
                        return [new Un(t.key,t.value,'identity function may not have a "stops" property')];
                    let e = [];
                    const n = t.value;
                    return e = e.concat($n({
                        key: t.key,
                        value: n,
                        valueSpec: t.valueSpec,
                        style: t.style,
                        styleSpec: t.styleSpec,
                        arrayElementValidator: h
                    })),
                    "array" === An(n) && 0 === n.length && e.push(new Un(t.key,n,"array must have at least one stop")),
                    e
                },
                default: function(t) {
                    return bi({
                        key: t.key,
                        value: t.value,
                        valueSpec: e,
                        style: t.style,
                        styleSpec: t.styleSpec
                    })
                }
            }
        });
        return "identity" === r && o && c.push(new Un(t.key,t.value,'missing required property "property"')),
        "identity" === r || t.value.stops || c.push(new Un(t.key,t.value,'missing required property "stops"')),
        "exponential" === r && t.valueSpec.expression && !wn(t.valueSpec) && c.push(new Un(t.key,t.value,"exponential functions not supported")),
        t.styleSpec.$version >= 8 && (l && !bn(t.valueSpec) ? c.push(new Un(t.key,t.value,"property functions not supported")) : o && !_n(t.valueSpec) && c.push(new Un(t.key,t.value,"zoom functions not supported"))),
        "categorical" !== r && !u || void 0 !== t.value.property || c.push(new Un(t.key,t.value,'"property" property is required')),
        c;
        function h(t) {
            let r = [];
            const n = t.value
              , o = t.key;
            if ("array" !== An(n))
                return [new Un(o,n,`array expected, ${An(n)} found`)];
            if (2 !== n.length)
                return [new Un(o,n,`array length 2 expected, length ${n.length} found`)];
            if (u) {
                if ("object" !== An(n[0]))
                    return [new Un(o,n,`object expected, ${An(n[0])} found`)];
                if (void 0 === n[0].zoom)
                    return [new Un(o,n,"object stop key must have zoom")];
                if (void 0 === n[0].value)
                    return [new Un(o,n,"object stop key must have value")];
                const e = Zt(n[0].zoom);
                if ("number" != typeof e)
                    return [new Un(o,n[0].zoom,"stop zoom values must be numbers")];
                if (s && s > e)
                    return [new Un(o,n[0].zoom,"stop zoom values must appear in ascending order")];
                e !== s && (s = e,
                i = void 0,
                a = {}),
                r = r.concat(On({
                    key: `${o}[0]`,
                    value: n[0],
                    valueSpec: {
                        zoom: {}
                    },
                    style: t.style,
                    styleSpec: t.styleSpec,
                    objectElementValidators: {
                        zoom: qn,
                        value: p
                    }
                }));
            } else
                r = r.concat(p({
                    key: `${o}[0]`,
                    value: n[0],
                    valueSpec: {},
                    style: t.style,
                    styleSpec: t.styleSpec
                }, n));
            return Pn(Gt(n[1])) ? r.concat([new Un(`${o}[1]`,n[1],"expressions are not allowed in function stops.")]) : r.concat(bi({
                key: `${o}[1]`,
                value: n[1],
                valueSpec: e,
                style: t.style,
                styleSpec: t.styleSpec
            }))
        }
        function p(t, s) {
            const o = An(t.value)
              , l = Zt(t.value)
              , u = null !== t.value ? t.value : s;
            if (n) {
                if (o !== n)
                    return [new Un(t.key,u,`${o} stop domain type must match previous stop domain type ${n}`)]
            } else
                n = o;
            if ("number" !== o && "string" !== o && "boolean" !== o && "number" != typeof l && "string" != typeof l && "boolean" != typeof l)
                return [new Un(t.key,u,"stop domain value must be a number, string, or boolean")];
            if ("number" !== o && "categorical" !== r) {
                let n = `number expected, ${o} found`;
                return bn(e) && void 0 === r && (n += '\nIf you intended to use a categorical function, specify `"type": "categorical"`.'),
                [new Un(t.key,u,n)]
            }
            return "categorical" !== r || "number" !== o || "number" == typeof l && isFinite(l) && Math.floor(l) === l ? "categorical" !== r && "number" === o && "number" == typeof l && "number" == typeof i && void 0 !== i && l < i ? [new Un(t.key,u,"stop domain values must appear in ascending order")] : (i = l,
            "categorical" === r && l in a ? [new Un(t.key,u,"stop domain values must be unique")] : (a[l] = !0,
            [])) : [new Un(t.key,u,`integer expected, found ${String(l)}`)]
        }
    }
    function Zn(t) {
        const e = ("property" === t.expressionContext ? Ln : Dn)(Gt(t.value), t.valueSpec);
        if ("error" === e.result)
            return e.value.map((e=>new Un(`${t.key}${e.key}`,t.value,e.message)));
        const r = e.value.expression || e.value._styleExpression.expression;
        if ("property" === t.expressionContext && "text-font" === t.propertyKey && !r.outputDefined())
            return [new Un(t.key,t.value,`Invalid data expression for "${t.propertyKey}". Output values must be contained as literals within the expression.`)];
        if ("property" === t.expressionContext && "layout" === t.propertyType && !ar(r))
            return [new Un(t.key,t.value,'"feature-state" data expressions are not supported with layout properties.')];
        if ("filter" === t.expressionContext)
            return Gn(r, t);
        if (t.expressionContext && 0 === t.expressionContext.indexOf("cluster")) {
            if (!or(r, ["zoom", "feature-state"]))
                return [new Un(t.key,t.value,'"zoom" and "feature-state" expressions are not supported with cluster properties.')];
            if ("cluster-initial" === t.expressionContext && !sr(r))
                return [new Un(t.key,t.value,"Feature data expressions are not supported with initial expression part of cluster properties.")]
        }
        return []
    }
    function Gn(t, e) {
        const r = new Set(["zoom", "feature-state", "pitch", "distance-from-center"]);
        if (e.valueSpec && e.valueSpec.expression)
            for (const t of e.valueSpec.expression.parameters)
                r.delete(t);
        if (0 === r.size)
            return [];
        const n = [];
        return t instanceof je && r.has(t.name) ? [new Un(e.key,e.value,`["${t.name}"] expression is not supported in a filter for a ${e.object.type} layer with id: ${e.object.id}`)] : (t.eachChild((t=>{
            n.push(...Gn(t, e));
        }
        )),
        n)
    }
    function Xn(t) {
        const e = t.key
          , r = t.value
          , n = t.valueSpec
          , i = [];
        return Array.isArray(n.values) ? -1 === n.values.indexOf(Zt(r)) && i.push(new Un(e,r,`expected one of [${n.values.join(", ")}], ${JSON.stringify(r)} found`)) : -1 === Object.keys(n.values).indexOf(Zt(r)) && i.push(new Un(e,r,`expected one of [${Object.keys(n.values).join(", ")}], ${JSON.stringify(r)} found`)),
        i
    }
    function Yn(t) {
        if (!0 === t || !1 === t)
            return !0;
        if (!Array.isArray(t) || 0 === t.length)
            return !1;
        switch (t[0]) {
        case "has":
            return t.length >= 2 && "$id" !== t[1] && "$type" !== t[1];
        case "in":
            return t.length >= 3 && ("string" != typeof t[1] || Array.isArray(t[2]));
        case "!in":
        case "!has":
        case "none":
            return !1;
        case "==":
        case "!=":
        case ">":
        case ">=":
        case "<":
        case "<=":
            return 3 !== t.length || Array.isArray(t[1]) || Array.isArray(t[2]);
        case "any":
        case "all":
            for (const e of t.slice(1))
                if (!Yn(e) && "boolean" != typeof e)
                    return !1;
            return !0;
        default:
            return !0
        }
    }
    function Hn(t, e="fill") {
        if (null == t)
            return {
                filter: ()=>!0,
                needGeometry: !1,
                needFeature: !1
            };
        Yn(t) || (t = ri(t));
        const r = t;
        let n = !0;
        try {
            n = function(t) {
                if (!Wn(t))
                    return t;
                let e = Gt(t);
                return Jn(e),
                e = Kn(e),
                e
            }(r);
        } catch (t) {
            console.warn(`Failed to extract static filter. Filter will continue working, but at higher memory usage and slower framerate.\nThis is most likely a bug, please report this via https://github.com/sgmap/sgmap-js/issues/new?assignees=&labels=&template=Bug_report.md\nand paste the contents of this message in the report.\nThank you!\nFilter Expression:\n${JSON.stringify(r, null, 2)}\n        `);
        }
        const i = qt[`filter_${e}`]
          , s = Dn(n, i);
        let a = null;
        if ("error" === s.result)
            throw new Error(s.value.map((t=>`${t.key}: ${t.message}`)).join(", "));
        a = (t,e,r)=>s.value.evaluate(t, e, {}, r);
        let o = null
          , l = null;
        if (n !== r) {
            const t = Dn(r, i);
            if ("error" === t.result)
                throw new Error(t.value.map((t=>`${t.key}: ${t.message}`)).join(", "));
            o = (e,r,n,i,s)=>t.value.evaluate(e, r, {}, n, void 0, void 0, i, s),
            l = !sr(t.value.expression);
        }
        return a = a,
        {
            filter: a,
            dynamicFilter: o || void 0,
            needGeometry: ei(n),
            needFeature: !!l
        }
    }
    function Kn(t) {
        if (!Array.isArray(t))
            return t;
        const e = function(t) {
            if (Qn.has(t[0]))
                for (let e = 1; e < t.length; e++)
                    if (Wn(t[e]))
                        return !0;
            return t
        }(t);
        return !0 === e ? e : e.map((t=>Kn(t)))
    }
    function Jn(t) {
        let e = !1;
        const r = [];
        if ("case" === t[0]) {
            for (let n = 1; n < t.length - 1; n += 2)
                e = e || Wn(t[n]),
                r.push(t[n + 1]);
            r.push(t[t.length - 1]);
        } else if ("match" === t[0]) {
            e = e || Wn(t[1]);
            for (let e = 2; e < t.length - 1; e += 2)
                r.push(t[e + 1]);
            r.push(t[t.length - 1]);
        } else if ("step" === t[0]) {
            e = e || Wn(t[1]);
            for (let e = 1; e < t.length - 1; e += 2)
                r.push(t[e + 1]);
        }
        e && (t.length = 0,
        t.push("any", ...r));
        for (let e = 1; e < t.length; e++)
            Jn(t[e]);
    }
    function Wn(t) {
        if (!Array.isArray(t))
            return !1;
        if ("pitch" === (e = t[0]) || "distance-from-center" === e)
            return !0;
        var e;
        for (let e = 1; e < t.length; e++)
            if (Wn(t[e]))
                return !0;
        return !1
    }
    const Qn = new Set(["in", "==", "!=", ">", ">=", "<", "<=", "to-boolean"]);
    function ti(t, e) {
        return t < e ? -1 : t > e ? 1 : 0
    }
    function ei(t) {
        if (!Array.isArray(t))
            return !1;
        if ("within" === t[0])
            return !0;
        for (let e = 1; e < t.length; e++)
            if (ei(t[e]))
                return !0;
        return !1
    }
    function ri(t) {
        if (!t)
            return !0;
        const e = t[0];
        return t.length <= 1 ? "any" !== e : "==" === e ? ni(t[1], t[2], "==") : "!=" === e ? ai(ni(t[1], t[2], "==")) : "<" === e || ">" === e || "<=" === e || ">=" === e ? ni(t[1], t[2], e) : "any" === e ? (r = t.slice(1),
        ["any"].concat(r.map(ri))) : "all" === e ? ["all"].concat(t.slice(1).map(ri)) : "none" === e ? ["all"].concat(t.slice(1).map(ri).map(ai)) : "in" === e ? ii(t[1], t.slice(2)) : "!in" === e ? ai(ii(t[1], t.slice(2))) : "has" === e ? si(t[1]) : "!has" === e ? ai(si(t[1])) : "within" !== e || t;
        var r;
    }
    function ni(t, e, r) {
        switch (t) {
        case "$type":
            return [`filter-type-${r}`, e];
        case "$id":
            return [`filter-id-${r}`, e];
        default:
            return [`filter-${r}`, t, e]
        }
    }
    function ii(t, e) {
        if (0 === e.length)
            return !1;
        switch (t) {
        case "$type":
            return ["filter-type-in", ["literal", e]];
        case "$id":
            return ["filter-id-in", ["literal", e]];
        default:
            return e.length > 200 && !e.some((t=>typeof t != typeof e[0])) ? ["filter-in-large", t, ["literal", e.sort(ti)]] : ["filter-in-small", t, ["literal", e]]
        }
    }
    function si(t) {
        switch (t) {
        case "$type":
            return !0;
        case "$id":
            return ["filter-has-id"];
        default:
            return ["filter-has", t]
        }
    }
    function ai(t) {
        return ["!", t]
    }
    function oi(t) {
        return Yn(Gt(t.value)) ? Zn(Nt({}, t, {
            expressionContext: "filter",
            valueSpec: t.styleSpec[`filter_${t.layerType || "fill"}`]
        })) : li(t)
    }
    function li(t) {
        const e = t.value
          , r = t.key;
        if ("array" !== An(e))
            return [new Un(r,e,`array expected, ${An(e)} found`)];
        const n = t.styleSpec;
        let i, s = [];
        if (e.length < 1)
            return [new Un(r,e,"filter array must have at least 1 element")];
        switch (s = s.concat(Xn({
            key: `${r}[0]`,
            value: e[0],
            valueSpec: n.filter_operator,
            style: t.style,
            styleSpec: t.styleSpec
        })),
        Zt(e[0])) {
        case "<":
        case "<=":
        case ">":
        case ">=":
            e.length >= 2 && "$type" === Zt(e[1]) && s.push(new Un(r,e,`"$type" cannot be use with operator "${e[0]}"`));
        case "==":
        case "!=":
            3 !== e.length && s.push(new Un(r,e,`filter array for operator "${e[0]}" must have 3 elements`));
        case "in":
        case "!in":
            e.length >= 2 && (i = An(e[1]),
            "string" !== i && s.push(new Un(`${r}[1]`,e[1],`string expected, ${i} found`)));
            for (let a = 2; a < e.length; a++)
                i = An(e[a]),
                "$type" === Zt(e[1]) ? s = s.concat(Xn({
                    key: `${r}[${a}]`,
                    value: e[a],
                    valueSpec: n.geometry_type,
                    style: t.style,
                    styleSpec: t.styleSpec
                })) : "string" !== i && "number" !== i && "boolean" !== i && s.push(new Un(`${r}[${a}]`,e[a],`string, number, or boolean expected, ${i} found`));
            break;
        case "any":
        case "all":
        case "none":
            for (let n = 1; n < e.length; n++)
                s = s.concat(li({
                    key: `${r}[${n}]`,
                    value: e[n],
                    style: t.style,
                    styleSpec: t.styleSpec
                }));
            break;
        case "has":
        case "!has":
            i = An(e[1]),
            2 !== e.length ? s.push(new Un(r,e,`filter array for "${e[0]}" operator must have 2 elements`)) : "string" !== i && s.push(new Un(`${r}[1]`,e[1],`string expected, ${i} found`));
            break;
        case "within":
            i = An(e[1]),
            2 !== e.length ? s.push(new Un(r,e,`filter array for "${e[0]}" operator must have 2 elements`)) : "object" !== i && s.push(new Un(`${r}[1]`,e[1],`object expected, ${i} found`));
        }
        return s
    }
    function ui(t, e) {
        const r = t.key
          , n = t.style
          , i = t.styleSpec
          , s = t.value
          , a = t.objectKey
          , o = i[`${e}_${t.layerType}`];
        if (!o)
            return [];
        const l = a.match(/^(.*)-transition$/);
        if ("paint" === e && l && o[l[1]] && o[l[1]].transition)
            return bi({
                key: r,
                value: s,
                valueSpec: i.transition,
                style: n,
                styleSpec: i
            });
        const u = t.valueSpec || o[a];
        if (!u)
            return [new Un(r,s,`unknown property "${a}"`)];
        let c;
        if ("string" === An(s) && bn(u) && !u.tokens && (c = /^{([^}]+)}$/.exec(s)))
            return [new Un(r,s,`"${a}" does not support interpolation syntax\nUse an identity property function instead: \`{ "type": "identity", "property": ${JSON.stringify(c[1])} }\`.`)];
        const h = [];
        return "symbol" === t.layerType && ("text-field" === a && n && !n.glyphs && h.push(new Un(r,s,'use of "text-field" requires a style "glyphs" property')),
        "text-font" === a && kn(Gt(s)) && "identity" === Zt(s.type) && h.push(new Un(r,s,'"text-font" does not support identity functions'))),
        h.concat(bi({
            key: t.key,
            value: s,
            valueSpec: u,
            style: n,
            styleSpec: i,
            expressionContext: "property",
            propertyType: e,
            propertyKey: a
        }))
    }
    function ci(t) {
        return ui(t, "paint")
    }
    function hi(t) {
        return ui(t, "layout")
    }
    function pi(t) {
        let e = [];
        const r = t.value
          , n = t.key
          , i = t.style
          , s = t.styleSpec;
        r.type || r.ref || e.push(new Un(n,r,'either "type" or "ref" is required'));
        let a = Zt(r.type);
        const o = Zt(r.ref);
        if (r.id) {
            const s = Zt(r.id);
            for (let a = 0; a < t.arrayIndex; a++) {
                const t = i.layers[a];
                Zt(t.id) === s && e.push(new Un(n,r.id,`duplicate layer id "${r.id}", previously used at line ${t.id.__line__}`));
            }
        }
        if ("ref"in r) {
            let t;
            ["type", "source", "source-layer", "filter", "layout"].forEach((t=>{
                t in r && e.push(new Un(n,r[t],`"${t}" is prohibited for ref layers`));
            }
            )),
            i.layers.forEach((e=>{
                Zt(e.id) === o && (t = e);
            }
            )),
            t ? t.ref ? e.push(new Un(n,r.ref,"ref cannot reference another ref layer")) : a = Zt(t.type) : "string" == typeof o && e.push(new Un(n,r.ref,`ref layer "${o}" not found`));
        } else if ("background" !== a && "sky" !== a)
            if (r.source) {
                const t = i.sources && i.sources[r.source]
                  , s = t && Zt(t.type);
                t ? "vector" === s && "raster" === a ? e.push(new Un(n,r.source,`layer "${r.id}" requires a raster source`)) : "raster" === s && "raster" !== a ? e.push(new Un(n,r.source,`layer "${r.id}" requires a vector source`)) : "vector" !== s || r["source-layer"] ? "raster-dem" === s && "hillshade" !== a ? e.push(new Un(n,r.source,"raster-dem source can only be used with layer type 'hillshade'.")) : "line" !== a || !r.paint || !r.paint["line-gradient"] && !r.paint["line-trim-offset"] || "geojson" === s && t.lineMetrics || e.push(new Un(n,r,`layer "${r.id}" specifies a line-gradient, which requires a GeoJSON source with \`lineMetrics\` enabled.`)) : e.push(new Un(n,r,`layer "${r.id}" must specify a "source-layer"`)) : e.push(new Un(n,r.source,`source "${r.source}" not found`));
            } else
                e.push(new Un(n,r,'missing required property "source"'));
        return e = e.concat(On({
            key: n,
            value: r,
            valueSpec: s.layer,
            style: t.style,
            styleSpec: t.styleSpec,
            objectElementValidators: {
                "*": ()=>[],
                type: ()=>bi({
                    key: `${n}.type`,
                    value: r.type,
                    valueSpec: s.layer.type,
                    style: t.style,
                    styleSpec: t.styleSpec,
                    object: r,
                    objectKey: "type"
                }),
                filter: t=>oi(Nt({
                    layerType: a
                }, t)),
                layout: t=>On({
                    layer: r,
                    key: t.key,
                    value: t.value,
                    valueSpec: {},
                    style: t.style,
                    styleSpec: t.styleSpec,
                    objectElementValidators: {
                        "*": t=>hi(Nt({
                            layerType: a
                        }, t))
                    }
                }),
                paint: t=>On({
                    layer: r,
                    key: t.key,
                    value: t.value,
                    valueSpec: {},
                    style: t.style,
                    styleSpec: t.styleSpec,
                    objectElementValidators: {
                        "*": t=>ci(Nt({
                            layerType: a
                        }, t))
                    }
                })
            }
        })),
        e
    }
    function fi(t) {
        const e = t.value
          , r = t.key
          , n = An(e);
        return "string" !== n ? [new Un(r,e,`string expected, ${n} found`)] : []
    }
    const di = {
        promoteId: function({key: t, value: e}) {
            if ("string" === An(e))
                return fi({
                    key: t,
                    value: e
                });
            {
                const r = [];
                for (const n in e)
                    r.push(...fi({
                        key: `${t}.${n}`,
                        value: e[n]
                    }));
                return r
            }
        }
    };
    function yi(t) {
        const e = t.value
          , r = t.key
          , n = t.styleSpec
          , i = t.style;
        if (!e.type)
            return [new Un(r,e,'"type" is required')];
        const s = Zt(e.type);
        let a;
        switch (s) {
        case "vector":
        case "raster":
        case "raster-dem":
            return a = On({
                key: r,
                value: e,
                valueSpec: n[`source_${s.replace("-", "_")}`],
                style: t.style,
                styleSpec: n,
                objectElementValidators: di
            }),
            a;
        case "geojson":
            if (a = On({
                key: r,
                value: e,
                valueSpec: n.source_geojson,
                style: i,
                styleSpec: n,
                objectElementValidators: di
            }),
            e.cluster)
                for (const t in e.clusterProperties) {
                    const [n,i] = e.clusterProperties[t]
                      , s = "string" == typeof n ? [n, ["accumulated"], ["get", t]] : n;
                    a.push(...Zn({
                        key: `${r}.${t}.map`,
                        value: i,
                        expressionContext: "cluster-map"
                    })),
                    a.push(...Zn({
                        key: `${r}.${t}.reduce`,
                        value: s,
                        expressionContext: "cluster-reduce"
                    }));
                }
            return a;
        case "video":
            return On({
                key: r,
                value: e,
                valueSpec: n.source_video,
                style: i,
                styleSpec: n
            });
        case "image":
            return On({
                key: r,
                value: e,
                valueSpec: n.source_image,
                style: i,
                styleSpec: n
            });
        case "canvas":
            return [new Un(r,null,"Please use runtime APIs to add canvas sources, rather than including them in stylesheets.","source.canvas")];
        default:
            return Xn({
                key: `${r}.type`,
                value: e.type,
                valueSpec: {
                    values: ["vector", "raster", "raster-dem", "geojson", "video", "image"]
                },
                style: i,
                styleSpec: n
            })
        }
    }
    function mi(t) {
        const e = t.value
          , r = t.styleSpec
          , n = r.light
          , i = t.style;
        let s = [];
        const a = An(e);
        if (void 0 === e)
            return s;
        if ("object" !== a)
            return s = s.concat([new Un("light",e,`object expected, ${a} found`)]),
            s;
        for (const t in e) {
            const a = t.match(/^(.*)-transition$/);
            s = s.concat(a && n[a[1]] && n[a[1]].transition ? bi({
                key: t,
                value: e[t],
                valueSpec: r.transition,
                style: i,
                styleSpec: r
            }) : n[t] ? bi({
                key: t,
                value: e[t],
                valueSpec: n[t],
                style: i,
                styleSpec: r
            }) : [new Un(t,e[t],`unknown property "${t}"`)]);
        }
        return s
    }
    function gi(t) {
        const e = t.value
          , r = t.key
          , n = t.style
          , i = t.styleSpec
          , s = i.terrain;
        let a = [];
        const o = An(e);
        if (void 0 === e)
            return a;
        if ("object" !== o)
            return a = a.concat([new Un("terrain",e,`object expected, ${o} found`)]),
            a;
        for (const t in e) {
            const r = t.match(/^(.*)-transition$/);
            a = a.concat(r && s[r[1]] && s[r[1]].transition ? bi({
                key: t,
                value: e[t],
                valueSpec: i.transition,
                style: n,
                styleSpec: i
            }) : s[t] ? bi({
                key: t,
                value: e[t],
                valueSpec: s[t],
                style: n,
                styleSpec: i
            }) : [new Un(t,e[t],`unknown property "${t}"`)]);
        }
        if (e.source) {
            const t = n.sources && n.sources[e.source]
              , i = t && Zt(t.type);
            t ? "raster-dem" !== i && a.push(new Un(r,e.source,`terrain cannot be used with a source of type ${String(i)}, it only be used with a "raster-dem" source type`)) : a.push(new Un(r,e.source,`source "${e.source}" not found`));
        } else
            a.push(new Un(r,e,'terrain is missing required property "source"'));
        return a
    }
    function xi(t) {
        const e = t.value
          , r = t.style
          , n = t.styleSpec
          , i = n.fog;
        let s = [];
        const a = An(e);
        if (void 0 === e)
            return s;
        if ("object" !== a)
            return s = s.concat([new Un("fog",e,`object expected, ${a} found`)]),
            s;
        for (const t in e) {
            const a = t.match(/^(.*)-transition$/);
            s = s.concat(a && i[a[1]] && i[a[1]].transition ? bi({
                key: t,
                value: e[t],
                valueSpec: n.transition,
                style: r,
                styleSpec: n
            }) : i[t] ? bi({
                key: t,
                value: e[t],
                valueSpec: i[t],
                style: r,
                styleSpec: n
            }) : [new Un(t,e[t],`unknown property "${t}"`)]);
        }
        return s
    }
    const vi = {
        "*": ()=>[],
        array: $n,
        boolean: function(t) {
            const e = t.value
              , r = t.key
              , n = An(e);
            return "boolean" !== n ? [new Un(r,e,`boolean expected, ${n} found`)] : []
        },
        number: qn,
        color: function(t) {
            const e = t.key
              , r = t.value
              , n = An(r);
            return "string" !== n ? [new Un(e,r,`color expected, ${n} found`)] : null === de.parseCSSColor(r) ? [new Un(e,r,`color expected, "${r}" found`)] : []
        },
        enum: Xn,
        filter: oi,
        function: Nn,
        layer: pi,
        object: On,
        source: yi,
        light: mi,
        terrain: gi,
        fog: xi,
        string: fi,
        formatted: function(t) {
            return 0 === fi(t).length ? [] : Zn(t)
        },
        resolvedImage: function(t) {
            return 0 === fi(t).length ? [] : Zn(t)
        },
        projection: function(t) {
            const e = t.value
              , r = t.styleSpec
              , n = r.projection
              , i = t.style;
            let s = [];
            const a = An(e);
            if ("object" === a)
                for (const t in e)
                    s = s.concat(bi({
                        key: t,
                        value: e[t],
                        valueSpec: n[t],
                        style: i,
                        styleSpec: r
                    }));
            else
                "string" !== a && (s = s.concat([new Un("projection",e,`object or string expected, ${a} found`)]));
            return s
        }
    };
    function bi(t) {
        const e = t.value
          , r = t.valueSpec
          , n = t.styleSpec;
        return r.expression && kn(Zt(e)) ? Nn(t) : r.expression && Pn(Gt(e)) ? Zn(t) : r.type && vi[r.type] ? vi[r.type](t) : On(Nt({}, t, {
            valueSpec: r.type ? n[r.type] : r
        }))
    }
    function _i(t) {
        const e = t.value
          , r = t.key
          , n = fi(t);
        return n.length || (-1 === e.indexOf("{fontstack}") && n.push(new Un(r,e,'"glyphs" url must include a "{fontstack}" token')),
        -1 === e.indexOf("{range}") && n.push(new Un(r,e,'"glyphs" url must include a "{range}" token'))),
        n
    }
    function wi(t, e=qt) {
        return zi(bi({
            key: "",
            value: t,
            valueSpec: e.$root,
            styleSpec: e,
            style: t,
            objectElementValidators: {
                glyphs: _i,
                "*": ()=>[]
            }
        }))
    }
    const Ai = t=>zi(ci(t))
      , ki = t=>zi(hi(t));
    function zi(t) {
        return t.slice().sort(((t,e)=>t.line && e.line ? t.line - e.line : 0))
    }
    function Si(t, e) {
        let r = !1;
        if (e && e.length)
            for (const n of e)
                t.fire(new Ot(new Error(n.message))),
                r = !0;
        return r
    }
    var Mi = Ii;
    function Ii(t, e, r) {
        var n = this.cells = [];
        if (t instanceof ArrayBuffer) {
            this.arrayBuffer = t;
            var i = new Int32Array(this.arrayBuffer);
            t = i[0],
            this.d = (e = i[1]) + 2 * (r = i[2]);
            for (var s = 0; s < this.d * this.d; s++) {
                var a = i[3 + s]
                  , o = i[3 + s + 1];
                n.push(a === o ? null : i.subarray(a, o));
            }
            var l = i[3 + n.length + 1];
            this.keys = i.subarray(i[3 + n.length], l),
            this.bboxes = i.subarray(l),
            this.insert = this._insertReadonly;
        } else {
            this.d = e + 2 * r;
            for (var u = 0; u < this.d * this.d; u++)
                n.push([]);
            this.keys = [],
            this.bboxes = [];
        }
        this.n = e,
        this.extent = t,
        this.padding = r,
        this.scale = e / t,
        this.uid = 0;
        var c = r / e * t;
        this.min = -c,
        this.max = t + c;
    }
    Ii.prototype.insert = function(t, e, r, n, i) {
        this._forEachCell(e, r, n, i, this._insertCell, this.uid++),
        this.keys.push(t),
        this.bboxes.push(e),
        this.bboxes.push(r),
        this.bboxes.push(n),
        this.bboxes.push(i);
    }
    ,
    Ii.prototype._insertReadonly = function() {
        throw "Cannot insert into a GridIndex created from an ArrayBuffer."
    }
    ,
    Ii.prototype._insertCell = function(t, e, r, n, i, s) {
        this.cells[i].push(s);
    }
    ,
    Ii.prototype.query = function(t, e, r, n, i) {
        var s = this.min
          , a = this.max;
        if (t <= s && e <= s && a <= r && a <= n && !i)
            return Array.prototype.slice.call(this.keys);
        var o = [];
        return this._forEachCell(t, e, r, n, this._queryCell, o, {}, i),
        o
    }
    ,
    Ii.prototype._queryCell = function(t, e, r, n, i, s, a, o) {
        var l = this.cells[i];
        if (null !== l)
            for (var u = this.keys, c = this.bboxes, h = 0; h < l.length; h++) {
                var p = l[h];
                if (void 0 === a[p]) {
                    var f = 4 * p;
                    (o ? o(c[f + 0], c[f + 1], c[f + 2], c[f + 3]) : t <= c[f + 2] && e <= c[f + 3] && r >= c[f + 0] && n >= c[f + 1]) ? (a[p] = !0,
                    s.push(u[p])) : a[p] = !1;
                }
            }
    }
    ,
    Ii.prototype._forEachCell = function(t, e, r, n, i, s, a, o) {
        for (var l = this._convertToCellCoord(t), u = this._convertToCellCoord(e), c = this._convertToCellCoord(r), h = this._convertToCellCoord(n), p = l; p <= c; p++)
            for (var f = u; f <= h; f++) {
                var d = this.d * f + p;
                if ((!o || o(this._convertFromCellCoord(p), this._convertFromCellCoord(f), this._convertFromCellCoord(p + 1), this._convertFromCellCoord(f + 1))) && i.call(this, t, e, r, n, d, s, a, o))
                    return
            }
    }
    ,
    Ii.prototype._convertFromCellCoord = function(t) {
        return (t - this.padding) / this.scale
    }
    ,
    Ii.prototype._convertToCellCoord = function(t) {
        return Math.max(0, Math.min(this.d - 1, Math.floor(t * this.scale) + this.padding))
    }
    ,
    Ii.prototype.toArrayBuffer = function() {
        if (this.arrayBuffer)
            return this.arrayBuffer;
        for (var t = this.cells, e = 3 + this.cells.length + 1 + 1, r = 0, n = 0; n < this.cells.length; n++)
            r += this.cells[n].length;
        var i = new Int32Array(e + r + this.keys.length + this.bboxes.length);
        i[0] = this.extent,
        i[1] = this.n,
        i[2] = this.padding;
        for (var s = e, a = 0; a < t.length; a++) {
            var o = t[a];
            i[3 + a] = s,
            i.set(o, s),
            s += o.length;
        }
        return i[3 + t.length] = s,
        i.set(this.keys, s),
        i[3 + t.length + 1] = s += this.keys.length,
        i.set(this.bboxes, s),
        s += this.bboxes.length,
        i.buffer
    }
    ;
    const Ti = {};
    function Bi(t, e, r={}) {
        Object.defineProperty(t, "_classRegistryKey", {
            value: e,
            writeable: !1
        }),
        Ti[e] = {
            klass: t,
            omit: r.omit || []
        };
    }
    Bi(Object, "Object"),
    Mi.serialize = function(t, e) {
        const r = t.toArrayBuffer();
        return e && e.push(r),
        {
            buffer: r
        }
    }
    ,
    Mi.deserialize = function(t) {
        return new Mi(t.buffer)
    }
    ,
    Object.defineProperty(Mi, "name", {
        value: "Grid"
    }),
    Bi(Mi, "Grid"),
    Bi(me, "Color"),
    Bi(Error, "Error"),
    Bi(St, "AJAXError"),
    Bi(be, "ResolvedImage"),
    Bi(Rn, "StylePropertyFunction"),
    Bi(Vn, "StyleExpression", {
        omit: ["_evaluator"]
    }),
    Bi(Fn, "ZoomDependentExpression"),
    Bi(En, "ZoomConstantExpression"),
    Bi(je, "CompoundExpression", {
        omit: ["_evaluate"]
    });
    for (const t in gn)
        Ti[gn[t]._classRegistryKey] || Bi(gn[t], `Expression${t}`);
    function Ci(t) {
        return t && "undefined" != typeof ArrayBuffer && (t instanceof ArrayBuffer || t.constructor && "ArrayBuffer" === t.constructor.name)
    }
    function Vi(t) {
        return e.ImageBitmap && t instanceof e.ImageBitmap
    }
    function Pi(t, r) {
        if (null == t || "boolean" == typeof t || "number" == typeof t || "string" == typeof t || t instanceof Boolean || t instanceof Number || t instanceof String || t instanceof Date || t instanceof RegExp)
            return t;
        if (Ci(t) || Vi(t))
            return r && r.push(t),
            t;
        if (ArrayBuffer.isView(t)) {
            const e = t;
            return r && r.push(e.buffer),
            e
        }
        if (t instanceof e.ImageData)
            return r && r.push(t.data.buffer),
            t;
        if (Array.isArray(t)) {
            const e = [];
            for (const n of t)
                e.push(Pi(n, r));
            return e
        }
        if ("object" == typeof t) {
            const e = t.constructor
              , n = e._classRegistryKey;
            if (!n)
                throw new Error(`can't serialize object of unregistered class ${n}`);
            const i = e.serialize ? e.serialize(t, r) : {};
            if (!e.serialize) {
                for (const e in t)
                    t.hasOwnProperty(e) && (Ti[n].omit.indexOf(e) >= 0 || (i[e] = Pi(t[e], r)));
                t instanceof Error && (i.message = t.message);
            }
            if (i.$name)
                throw new Error("$name property is reserved for worker serialization logic.");
            return "Object" !== n && (i.$name = n),
            i
        }
        throw new Error("can't serialize object of type " + typeof t)
    }
    function Di(t) {
        if (null == t || "boolean" == typeof t || "number" == typeof t || "string" == typeof t || t instanceof Boolean || t instanceof Number || t instanceof String || t instanceof Date || t instanceof RegExp || Ci(t) || Vi(t) || ArrayBuffer.isView(t) || t instanceof e.ImageData)
            return t;
        if (Array.isArray(t))
            return t.map(Di);
        if ("object" == typeof t) {
            const e = t.$name || "Object"
              , {klass: r} = Ti[e];
            if (!r)
                throw new Error(`can't deserialize unregistered class ${e}`);
            if (r.deserialize)
                return r.deserialize(t);
            const n = Object.create(r.prototype);
            for (const e of Object.keys(t))
                "$name" !== e && (n[e] = Di(t[e]));
            return n
        }
        throw new Error("can't deserialize object of type " + typeof t)
    }
    class Ei {
        constructor() {
            this.first = !0;
        }
        update(t, e) {
            const r = Math.floor(t);
            return this.first ? (this.first = !1,
            this.lastIntegerZoom = r,
            this.lastIntegerZoomTime = 0,
            this.lastZoom = t,
            this.lastFloorZoom = r,
            !0) : (this.lastFloorZoom > r ? (this.lastIntegerZoom = r + 1,
            this.lastIntegerZoomTime = e) : this.lastFloorZoom < r && (this.lastIntegerZoom = r,
            this.lastIntegerZoomTime = e),
            t !== this.lastZoom && (this.lastZoom = t,
            this.lastFloorZoom = r,
            !0))
        }
    }
    const Fi = t=>t >= 1536 && t <= 1791
      , Li = t=>t >= 1872 && t <= 1919
      , Ri = t=>t >= 2208 && t <= 2303
      , ji = t=>t >= 11904 && t <= 12031
      , Ui = t=>t >= 12032 && t <= 12255
      , Oi = t=>t >= 12272 && t <= 12287
      , $i = t=>t >= 12288 && t <= 12351
      , qi = t=>t >= 12352 && t <= 12447
      , Ni = t=>t >= 12448 && t <= 12543
      , Zi = t=>t >= 12544 && t <= 12591
      , Gi = t=>t >= 12704 && t <= 12735
      , Xi = t=>t >= 12736 && t <= 12783
      , Yi = t=>t >= 12784 && t <= 12799
      , Hi = t=>t >= 12800 && t <= 13055
      , Ki = t=>t >= 13056 && t <= 13311
      , Ji = t=>t >= 13312 && t <= 19903
      , Wi = t=>t >= 19968 && t <= 40959
      , Qi = t=>t >= 40960 && t <= 42127
      , ts = t=>t >= 42128 && t <= 42191
      , es = t=>t >= 44032 && t <= 55215
      , rs = t=>t >= 63744 && t <= 64255
      , ns = t=>t >= 64336 && t <= 65023
      , is = t=>t >= 65040 && t <= 65055
      , ss = t=>t >= 65072 && t <= 65103
      , as = t=>t >= 65104 && t <= 65135
      , os = t=>t >= 65136 && t <= 65279
      , ls = t=>t >= 65280 && t <= 65519;
    function us(t) {
        for (const e of t)
            if (ps(e.charCodeAt(0)))
                return !0;
        return !1
    }
    function cs(t) {
        for (const e of t)
            if (!hs(e.charCodeAt(0)))
                return !1;
        return !0
    }
    function hs(t) {
        return !(Fi(t) || Li(t) || Ri(t) || ns(t) || os(t))
    }
    function ps(t) {
        return !(746 !== t && 747 !== t && (t < 4352 || !(Gi(t) || Zi(t) || ss(t) && !(t >= 65097 && t <= 65103) || rs(t) || Ki(t) || ji(t) || Xi(t) || !(!$i(t) || t >= 12296 && t <= 12305 || t >= 12308 && t <= 12319 || 12336 === t) || Ji(t) || Wi(t) || Hi(t) || (t=>t >= 12592 && t <= 12687)(t) || (t=>t >= 43360 && t <= 43391)(t) || (t=>t >= 55216 && t <= 55295)(t) || (t=>t >= 4352 && t <= 4607)(t) || es(t) || qi(t) || Oi(t) || (t=>t >= 12688 && t <= 12703)(t) || Ui(t) || Yi(t) || Ni(t) && 12540 !== t || !(!ls(t) || 65288 === t || 65289 === t || 65293 === t || t >= 65306 && t <= 65310 || 65339 === t || 65341 === t || 65343 === t || t >= 65371 && t <= 65503 || 65507 === t || t >= 65512 && t <= 65519) || !(!as(t) || t >= 65112 && t <= 65118 || t >= 65123 && t <= 65126) || (t=>t >= 5120 && t <= 5759)(t) || (t=>t >= 6320 && t <= 6399)(t) || is(t) || (t=>t >= 19904 && t <= 19967)(t) || Qi(t) || ts(t))))
    }
    function fs(t) {
        return !(ps(t) || function(t) {
            return !!((t=>t >= 128 && t <= 255)(t) && (167 === t || 169 === t || 174 === t || 177 === t || 188 === t || 189 === t || 190 === t || 215 === t || 247 === t) || (t=>t >= 8192 && t <= 8303)(t) && (8214 === t || 8224 === t || 8225 === t || 8240 === t || 8241 === t || 8251 === t || 8252 === t || 8258 === t || 8263 === t || 8264 === t || 8265 === t || 8273 === t) || (t=>t >= 8448 && t <= 8527)(t) || (t=>t >= 8528 && t <= 8591)(t) || (t=>t >= 8960 && t <= 9215)(t) && (t >= 8960 && t <= 8967 || t >= 8972 && t <= 8991 || t >= 8996 && t <= 9e3 || 9003 === t || t >= 9085 && t <= 9114 || t >= 9150 && t <= 9165 || 9167 === t || t >= 9169 && t <= 9179 || t >= 9186 && t <= 9215) || (t=>t >= 9216 && t <= 9279)(t) && 9251 !== t || (t=>t >= 9280 && t <= 9311)(t) || (t=>t >= 9312 && t <= 9471)(t) || (t=>t >= 9632 && t <= 9727)(t) || (t=>t >= 9728 && t <= 9983)(t) && !(t >= 9754 && t <= 9759) || (t=>t >= 11008 && t <= 11263)(t) && (t >= 11026 && t <= 11055 || t >= 11088 && t <= 11097 || t >= 11192 && t <= 11243) || $i(t) || Ni(t) || (t=>t >= 57344 && t <= 63743)(t) || ss(t) || as(t) || ls(t) || 8734 === t || 8756 === t || 8757 === t || t >= 9984 && t <= 10087 || t >= 10102 && t <= 10131 || 65532 === t || 65533 === t)
        }(t))
    }
    function ds(t) {
        return t >= 1424 && t <= 2303 || ns(t) || os(t)
    }
    function ys(t, e) {
        return !(!e && ds(t) || t >= 2304 && t <= 3583 || t >= 3840 && t <= 4255 || (t=>t >= 6016 && t <= 6143)(t))
    }
    function ms(t) {
        for (const e of t)
            if (ds(e.charCodeAt(0)))
                return !0;
        return !1
    }
    const gs = "deferred"
      , xs = "loading"
      , vs = "loaded";
    let bs = null
      , _s = "unavailable"
      , ws = null;
    const As = function(t) {
        t && "string" == typeof t && t.indexOf("NetworkError") > -1 && (_s = "error"),
        bs && bs(t);
    };
    function ks() {
        zs.fire(new Ut("pluginStateChange",{
            pluginStatus: _s,
            pluginURL: ws
        }));
    }
    const zs = new $t
      , Ss = function() {
        return _s
    }
      , Ms = function() {
        if (_s !== gs || !ws)
            throw new Error("rtl-text-plugin cannot be downloaded unless a pluginURL is specified");
        _s = xs,
        ks(),
        ws && Vt({
            url: ws
        }, (t=>{
            t ? As(t) : (_s = vs,
            ks());
        }
        ));
    }
      , Is = {
        applyArabicShaping: null,
        processBidirectionalText: null,
        processStyledBidirectionalText: null,
        isLoaded: ()=>_s === vs || null != Is.applyArabicShaping,
        isLoading: ()=>_s === xs,
        setState(t) {
            _s = t.pluginStatus,
            ws = t.pluginURL;
        },
        isParsed: ()=>null != Is.applyArabicShaping && null != Is.processBidirectionalText && null != Is.processStyledBidirectionalText,
        getPluginURL: ()=>ws
    };
    class Ts {
        constructor(t, e) {
            this.zoom = t,
            e ? (this.now = e.now,
            this.fadeDuration = e.fadeDuration,
            this.zoomHistory = e.zoomHistory,
            this.transition = e.transition,
            this.pitch = e.pitch) : (this.now = 0,
            this.fadeDuration = 0,
            this.zoomHistory = new Ei,
            this.transition = {},
            this.pitch = 0);
        }
        isSupportedScript(t) {
            return function(t, e) {
                for (const r of t)
                    if (!ys(r.charCodeAt(0), e))
                        return !1;
                return !0
            }(t, Is.isLoaded())
        }
        crossFadingFactor() {
            return 0 === this.fadeDuration ? 1 : Math.min((this.now - this.zoomHistory.lastIntegerZoomTime) / this.fadeDuration, 1)
        }
        getCrossfadeParameters() {
            const t = this.zoom
              , e = t - Math.floor(t)
              , r = this.crossFadingFactor();
            return t > this.zoomHistory.lastIntegerZoom ? {
                fromScale: 2,
                toScale: 1,
                t: e + (1 - e) * r
            } : {
                fromScale: .5,
                toScale: 1,
                t: 1 - (1 - r) * e
            }
        }
    }
    class Bs {
        constructor(t, e) {
            this.property = t,
            this.value = e,
            this.expression = function(t, e) {
                if (kn(t))
                    return new Rn(t,e);
                if (Pn(t)) {
                    const r = Ln(t, e);
                    if ("error" === r.result)
                        throw new Error(r.value.map((t=>`${t.key}: ${t.message}`)).join(", "));
                    return r.value
                }
                {
                    let r = t;
                    return "string" == typeof t && "color" === e.type && (r = me.parse(t)),
                    {
                        kind: "constant",
                        evaluate: ()=>r
                    }
                }
            }(void 0 === e ? t.specification.default : e, t.specification);
        }
        isDataDriven() {
            return "source" === this.expression.kind || "composite" === this.expression.kind
        }
        possiblyEvaluate(t, e, r) {
            return this.property.possiblyEvaluate(this, t, e, r)
        }
    }
    class Cs {
        constructor(t) {
            this.property = t,
            this.value = new Bs(t,void 0);
        }
        transitioned(t, e) {
            return new Ps(this.property,this.value,e,v({}, t.transition, this.transition),t.now)
        }
        untransitioned() {
            return new Ps(this.property,this.value,null,{},0)
        }
    }
    class Vs {
        constructor(t) {
            this._properties = t,
            this._values = Object.create(t.defaultTransitionablePropertyValues);
        }
        getValue(t) {
            return I(this._values[t].value.value)
        }
        setValue(t, e) {
            this._values.hasOwnProperty(t) || (this._values[t] = new Cs(this._values[t].property)),
            this._values[t].value = new Bs(this._values[t].property,null === e ? void 0 : I(e));
        }
        getTransition(t) {
            return I(this._values[t].transition)
        }
        setTransition(t, e) {
            this._values.hasOwnProperty(t) || (this._values[t] = new Cs(this._values[t].property)),
            this._values[t].transition = I(e) || void 0;
        }
        serialize() {
            const t = {};
            for (const e of Object.keys(this._values)) {
                const r = this.getValue(e);
                void 0 !== r && (t[e] = r);
                const n = this.getTransition(e);
                void 0 !== n && (t[`${e}-transition`] = n);
            }
            return t
        }
        transitioned(t, e) {
            const r = new Ds(this._properties);
            for (const n of Object.keys(this._values))
                r._values[n] = this._values[n].transitioned(t, e._values[n]);
            return r
        }
        untransitioned() {
            const t = new Ds(this._properties);
            for (const e of Object.keys(this._values))
                t._values[e] = this._values[e].untransitioned();
            return t
        }
    }
    class Ps {
        constructor(t, e, r, n, i) {
            const s = n.delay || 0
              , a = n.duration || 0;
            i = i || 0,
            this.property = t,
            this.value = e,
            this.begin = i + s,
            this.end = this.begin + a,
            t.specification.transition && (n.delay || n.duration) && (this.prior = r);
        }
        possiblyEvaluate(t, e, r) {
            const n = t.now || 0
              , i = this.value.possiblyEvaluate(t, e, r)
              , s = this.prior;
            if (s) {
                if (n > this.end)
                    return this.prior = null,
                    i;
                if (this.value.isDataDriven())
                    return this.prior = null,
                    i;
                if (n < this.begin)
                    return s.possiblyEvaluate(t, e, r);
                {
                    const a = (n - this.begin) / (this.end - this.begin);
                    return this.property.interpolate(s.possiblyEvaluate(t, e, r), i, h(a))
                }
            }
            return i
        }
    }
    class Ds {
        constructor(t) {
            this._properties = t,
            this._values = Object.create(t.defaultTransitioningPropertyValues);
        }
        possiblyEvaluate(t, e, r) {
            const n = new Ls(this._properties);
            for (const i of Object.keys(this._values))
                n._values[i] = this._values[i].possiblyEvaluate(t, e, r);
            return n
        }
        hasTransition() {
            for (const t of Object.keys(this._values))
                if (this._values[t].prior)
                    return !0;
            return !1
        }
    }
    class Es {
        constructor(t) {
            this._properties = t,
            this._values = Object.create(t.defaultPropertyValues);
        }
        getValue(t) {
            return I(this._values[t].value)
        }
        setValue(t, e) {
            this._values[t] = new Bs(this._values[t].property,null === e ? void 0 : I(e));
        }
        serialize() {
            const t = {};
            for (const e of Object.keys(this._values)) {
                const r = this.getValue(e);
                void 0 !== r && (t[e] = r);
            }
            return t
        }
        possiblyEvaluate(t, e, r) {
            const n = new Ls(this._properties);
            for (const i of Object.keys(this._values))
                n._values[i] = this._values[i].possiblyEvaluate(t, e, r);
            return n
        }
    }
    class Fs {
        constructor(t, e, r) {
            this.property = t,
            this.value = e,
            this.parameters = r;
        }
        isConstant() {
            return "constant" === this.value.kind
        }
        constantOr(t) {
            return "constant" === this.value.kind ? this.value.value : t
        }
        evaluate(t, e, r, n) {
            return this.property.evaluate(this.value, this.parameters, t, e, r, n)
        }
    }
    class Ls {
        constructor(t) {
            this._properties = t,
            this._values = Object.create(t.defaultPossiblyEvaluatedValues);
        }
        get(t) {
            return this._values[t]
        }
    }
    class Rs {
        constructor(t) {
            this.specification = t;
        }
        possiblyEvaluate(t, e) {
            return t.expression.evaluate(e)
        }
        interpolate(t, e, r) {
            const n = gr[this.specification.type];
            return n ? n(t, e, r) : t
        }
    }
    class js {
        constructor(t, e) {
            this.specification = t,
            this.overrides = e;
        }
        possiblyEvaluate(t, e, r, n) {
            return new Fs(this,"constant" === t.expression.kind || "camera" === t.expression.kind ? {
                kind: "constant",
                value: t.expression.evaluate(e, null, {}, r, n)
            } : t.expression,e)
        }
        interpolate(t, e, r) {
            if ("constant" !== t.value.kind || "constant" !== e.value.kind)
                return t;
            if (void 0 === t.value.value || void 0 === e.value.value)
                return new Fs(this,{
                    kind: "constant",
                    value: void 0
                },t.parameters);
            const n = gr[this.specification.type];
            return n ? new Fs(this,{
                kind: "constant",
                value: n(t.value.value, e.value.value, r)
            },t.parameters) : t
        }
        evaluate(t, e, r, n, i, s) {
            return "constant" === t.kind ? t.value : t.evaluate(e, r, n, i, s)
        }
    }
    class Us extends js {
        possiblyEvaluate(t, e, r, n) {
            if (void 0 === t.value)
                return new Fs(this,{
                    kind: "constant",
                    value: void 0
                },e);
            if ("constant" === t.expression.kind) {
                const i = t.expression.evaluate(e, null, {}, r, n)
                  , s = "resolvedImage" === t.property.specification.type && "string" != typeof i ? i.name : i
                  , a = this._calculate(s, s, s, e);
                return new Fs(this,{
                    kind: "constant",
                    value: a
                },e)
            }
            if ("camera" === t.expression.kind) {
                const r = this._calculate(t.expression.evaluate({
                    zoom: e.zoom - 1
                }), t.expression.evaluate({
                    zoom: e.zoom
                }), t.expression.evaluate({
                    zoom: e.zoom + 1
                }), e);
                return new Fs(this,{
                    kind: "constant",
                    value: r
                },e)
            }
            return new Fs(this,t.expression,e)
        }
        evaluate(t, e, r, n, i, s) {
            if ("source" === t.kind) {
                const a = t.evaluate(e, r, n, i, s);
                return this._calculate(a, a, a, e)
            }
            return "composite" === t.kind ? this._calculate(t.evaluate({
                zoom: Math.floor(e.zoom) - 1
            }, r, n), t.evaluate({
                zoom: Math.floor(e.zoom)
            }, r, n), t.evaluate({
                zoom: Math.floor(e.zoom) + 1
            }, r, n), e) : t.value
        }
        _calculate(t, e, r, n) {
            return n.zoom > n.zoomHistory.lastIntegerZoom ? {
                from: t,
                to: e,
                other: r
            } : {
                from: r,
                to: e,
                other: t
            }
        }
        interpolate(t) {
            return t
        }
    }
    class Os {
        constructor(t) {
            this.specification = t;
        }
        possiblyEvaluate(t, e, r, n) {
            if (void 0 !== t.value) {
                if ("constant" === t.expression.kind) {
                    const i = t.expression.evaluate(e, null, {}, r, n);
                    return this._calculate(i, i, i, e)
                }
                return this._calculate(t.expression.evaluate(new Ts(Math.floor(e.zoom - 1),e)), t.expression.evaluate(new Ts(Math.floor(e.zoom),e)), t.expression.evaluate(new Ts(Math.floor(e.zoom + 1),e)), e)
            }
        }
        _calculate(t, e, r, n) {
            return n.zoom > n.zoomHistory.lastIntegerZoom ? {
                from: t,
                to: e
            } : {
                from: r,
                to: e
            }
        }
        interpolate(t) {
            return t
        }
    }
    class $s {
        constructor(t) {
            this.specification = t;
        }
        possiblyEvaluate(t, e, r, n) {
            return !!t.expression.evaluate(e, null, {}, r, n)
        }
        interpolate() {
            return !1
        }
    }
    class qs {
        constructor(t) {
            this.properties = t,
            this.defaultPropertyValues = {},
            this.defaultTransitionablePropertyValues = {},
            this.defaultTransitioningPropertyValues = {},
            this.defaultPossiblyEvaluatedValues = {},
            this.overridableProperties = [];
            const e = new Ts(0,{});
            for (const r in t) {
                const n = t[r];
                n.specification.overridable && this.overridableProperties.push(r);
                const i = this.defaultPropertyValues[r] = new Bs(n,void 0)
                  , s = this.defaultTransitionablePropertyValues[r] = new Cs(n);
                this.defaultTransitioningPropertyValues[r] = s.untransitioned(),
                this.defaultPossiblyEvaluatedValues[r] = i.possiblyEvaluate(e);
            }
        }
    }
    function Ns(t, e) {
        return 256 * (t = d(Math.floor(t), 0, 255)) + d(Math.floor(e), 0, 255)
    }
    Bi(js, "DataDrivenProperty"),
    Bi(Rs, "DataConstantProperty"),
    Bi(Us, "CrossFadedDataDrivenProperty"),
    Bi(Os, "CrossFadedProperty"),
    Bi($s, "ColorRampProperty");
    const Zs = {
        Int8: Int8Array,
        Uint8: Uint8Array,
        Int16: Int16Array,
        Uint16: Uint16Array,
        Int32: Int32Array,
        Uint32: Uint32Array,
        Float32: Float32Array
    };
    class Gs {
        constructor(t, e) {
            this._structArray = t,
            this._pos1 = e * this.size,
            this._pos2 = this._pos1 / 2,
            this._pos4 = this._pos1 / 4,
            this._pos8 = this._pos1 / 8;
        }
    }
    class Xs {
        constructor() {
            this.isTransferred = !1,
            this.capacity = -1,
            this.resize(0);
        }
        static serialize(t, e) {
            return t._trim(),
            e && (t.isTransferred = !0,
            e.push(t.arrayBuffer)),
            {
                length: t.length,
                arrayBuffer: t.arrayBuffer
            }
        }
        static deserialize(t) {
            const e = Object.create(this.prototype);
            return e.arrayBuffer = t.arrayBuffer,
            e.length = t.length,
            e.capacity = t.arrayBuffer.byteLength / e.bytesPerElement,
            e._refreshViews(),
            e
        }
        _trim() {
            this.length !== this.capacity && (this.capacity = this.length,
            this.arrayBuffer = this.arrayBuffer.slice(0, this.length * this.bytesPerElement),
            this._refreshViews());
        }
        clear() {
            this.length = 0;
        }
        resize(t) {
            this.reserve(t),
            this.length = t;
        }
        reserve(t) {
            if (t > this.capacity) {
                this.capacity = Math.max(t, Math.floor(5 * this.capacity), 128),
                this.arrayBuffer = new ArrayBuffer(this.capacity * this.bytesPerElement);
                const e = this.uint8;
                this._refreshViews(),
                e && this.uint8.set(e);
            }
        }
        _refreshViews() {
            throw new Error("_refreshViews() must be implemented by each concrete StructArray layout")
        }
        destroy() {
            this.int8 = this.uint8 = this.int16 = this.uint16 = this.int32 = this.uint32 = this.float32 = null,
            this.arrayBuffer = null;
        }
    }
    function Ys(t, e=1) {
        let r = 0
          , n = 0;
        return {
            members: t.map((t=>{
                const i = Zs[t.type].BYTES_PER_ELEMENT
                  , s = r = Hs(r, Math.max(e, i))
                  , a = t.components || 1;
                return n = Math.max(n, i),
                r += i * a,
                {
                    name: t.name,
                    type: t.type,
                    components: a,
                    offset: s
                }
            }
            )),
            size: Hs(r, Math.max(n, e)),
            alignment: e
        }
    }
    function Hs(t, e) {
        return Math.ceil(t / e) * e
    }
    class Ks extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer);
        }
        emplaceBack(t, e) {
            const r = this.length;
            return this.resize(r + 1),
            this.emplace(r, t, e)
        }
        emplace(t, e, r) {
            const n = 2 * t;
            return this.int16[n + 0] = e,
            this.int16[n + 1] = r,
            t
        }
    }
    Ks.prototype.bytesPerElement = 4,
    Bi(Ks, "StructArrayLayout2i4");
    class Js extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r) {
            const n = this.length;
            return this.resize(n + 1),
            this.emplace(n, t, e, r)
        }
        emplace(t, e, r, n) {
            const i = 3 * t;
            return this.int16[i + 0] = e,
            this.int16[i + 1] = r,
            this.int16[i + 2] = n,
            t
        }
    }
    Js.prototype.bytesPerElement = 6,
    Bi(Js, "StructArrayLayout3i6");
    class Ws extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n) {
            const i = this.length;
            return this.resize(i + 1),
            this.emplace(i, t, e, r, n)
        }
        emplace(t, e, r, n, i) {
            const s = 4 * t;
            return this.int16[s + 0] = e,
            this.int16[s + 1] = r,
            this.int16[s + 2] = n,
            this.int16[s + 3] = i,
            t
        }
    }
    Ws.prototype.bytesPerElement = 8,
    Bi(Ws, "StructArrayLayout4i8");
    class Qs extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a) {
            const o = this.length;
            return this.resize(o + 1),
            this.emplace(o, t, e, r, n, i, s, a)
        }
        emplace(t, e, r, n, i, s, a, o) {
            const l = 6 * t
              , u = 12 * t
              , c = 3 * t;
            return this.int16[l + 0] = e,
            this.int16[l + 1] = r,
            this.uint8[u + 4] = n,
            this.uint8[u + 5] = i,
            this.uint8[u + 6] = s,
            this.uint8[u + 7] = a,
            this.float32[c + 2] = o,
            t
        }
    }
    Qs.prototype.bytesPerElement = 12,
    Bi(Qs, "StructArrayLayout2i4ub1f12");
    class ta extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n) {
            const i = this.length;
            return this.resize(i + 1),
            this.emplace(i, t, e, r, n)
        }
        emplace(t, e, r, n, i) {
            const s = 4 * t;
            return this.float32[s + 0] = e,
            this.float32[s + 1] = r,
            this.float32[s + 2] = n,
            this.float32[s + 3] = i,
            t
        }
    }
    ta.prototype.bytesPerElement = 16,
    Bi(ta, "StructArrayLayout4f16");
    class ea extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a, o, l, u) {
            const c = this.length;
            return this.resize(c + 1),
            this.emplace(c, t, e, r, n, i, s, a, o, l, u)
        }
        emplace(t, e, r, n, i, s, a, o, l, u, c) {
            const h = 10 * t;
            return this.uint16[h + 0] = e,
            this.uint16[h + 1] = r,
            this.uint16[h + 2] = n,
            this.uint16[h + 3] = i,
            this.uint16[h + 4] = s,
            this.uint16[h + 5] = a,
            this.uint16[h + 6] = o,
            this.uint16[h + 7] = l,
            this.uint16[h + 8] = u,
            this.uint16[h + 9] = c,
            t
        }
    }
    ea.prototype.bytesPerElement = 20,
    Bi(ea, "StructArrayLayout10ui20");
    class ra extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a, o) {
            const l = this.length;
            return this.resize(l + 1),
            this.emplace(l, t, e, r, n, i, s, a, o)
        }
        emplace(t, e, r, n, i, s, a, o, l) {
            const u = 8 * t;
            return this.uint16[u + 0] = e,
            this.uint16[u + 1] = r,
            this.uint16[u + 2] = n,
            this.uint16[u + 3] = i,
            this.uint16[u + 4] = s,
            this.uint16[u + 5] = a,
            this.uint16[u + 6] = o,
            this.uint16[u + 7] = l,
            t
        }
    }
    ra.prototype.bytesPerElement = 16,
    Bi(ra, "StructArrayLayout8ui16");
    class na extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s) {
            const a = this.length;
            return this.resize(a + 1),
            this.emplace(a, t, e, r, n, i, s)
        }
        emplace(t, e, r, n, i, s, a) {
            const o = 6 * t;
            return this.int16[o + 0] = e,
            this.int16[o + 1] = r,
            this.int16[o + 2] = n,
            this.int16[o + 3] = i,
            this.int16[o + 4] = s,
            this.int16[o + 5] = a,
            t
        }
    }
    na.prototype.bytesPerElement = 12,
    Bi(na, "StructArrayLayout6i12");
    class ia extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a, o, l, u, c, h) {
            const p = this.length;
            return this.resize(p + 1),
            this.emplace(p, t, e, r, n, i, s, a, o, l, u, c, h)
        }
        emplace(t, e, r, n, i, s, a, o, l, u, c, h, p) {
            const f = 12 * t;
            return this.int16[f + 0] = e,
            this.int16[f + 1] = r,
            this.int16[f + 2] = n,
            this.int16[f + 3] = i,
            this.uint16[f + 4] = s,
            this.uint16[f + 5] = a,
            this.uint16[f + 6] = o,
            this.uint16[f + 7] = l,
            this.int16[f + 8] = u,
            this.int16[f + 9] = c,
            this.int16[f + 10] = h,
            this.int16[f + 11] = p,
            t
        }
    }
    ia.prototype.bytesPerElement = 24,
    Bi(ia, "StructArrayLayout4i4ui4i24");
    class sa extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s) {
            const a = this.length;
            return this.resize(a + 1),
            this.emplace(a, t, e, r, n, i, s)
        }
        emplace(t, e, r, n, i, s, a) {
            const o = 10 * t
              , l = 5 * t;
            return this.int16[o + 0] = e,
            this.int16[o + 1] = r,
            this.int16[o + 2] = n,
            this.float32[l + 2] = i,
            this.float32[l + 3] = s,
            this.float32[l + 4] = a,
            t
        }
    }
    sa.prototype.bytesPerElement = 20,
    Bi(sa, "StructArrayLayout3i3f20");
    class aa extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.uint32 = new Uint32Array(this.arrayBuffer);
        }
        emplaceBack(t) {
            const e = this.length;
            return this.resize(e + 1),
            this.emplace(e, t)
        }
        emplace(t, e) {
            return this.uint32[1 * t + 0] = e,
            t
        }
    }
    aa.prototype.bytesPerElement = 4,
    Bi(aa, "StructArrayLayout1ul4");
    class oa extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer),
            this.uint32 = new Uint32Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a, o, l, u, c, h, p) {
            const f = this.length;
            return this.resize(f + 1),
            this.emplace(f, t, e, r, n, i, s, a, o, l, u, c, h, p)
        }
        emplace(t, e, r, n, i, s, a, o, l, u, c, h, p, f) {
            const d = 20 * t
              , y = 10 * t;
            return this.int16[d + 0] = e,
            this.int16[d + 1] = r,
            this.int16[d + 2] = n,
            this.int16[d + 3] = i,
            this.int16[d + 4] = s,
            this.float32[y + 3] = a,
            this.float32[y + 4] = o,
            this.float32[y + 5] = l,
            this.float32[y + 6] = u,
            this.int16[d + 14] = c,
            this.uint32[y + 8] = h,
            this.uint16[d + 18] = p,
            this.uint16[d + 19] = f,
            t
        }
    }
    oa.prototype.bytesPerElement = 40,
    Bi(oa, "StructArrayLayout5i4f1i1ul2ui40");
    class la extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a) {
            const o = this.length;
            return this.resize(o + 1),
            this.emplace(o, t, e, r, n, i, s, a)
        }
        emplace(t, e, r, n, i, s, a, o) {
            const l = 8 * t;
            return this.int16[l + 0] = e,
            this.int16[l + 1] = r,
            this.int16[l + 2] = n,
            this.int16[l + 4] = i,
            this.int16[l + 5] = s,
            this.int16[l + 6] = a,
            this.int16[l + 7] = o,
            t
        }
    }
    la.prototype.bytesPerElement = 16,
    Bi(la, "StructArrayLayout3i2i2i16");
    class ua extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i) {
            const s = this.length;
            return this.resize(s + 1),
            this.emplace(s, t, e, r, n, i)
        }
        emplace(t, e, r, n, i, s) {
            const a = 4 * t
              , o = 8 * t;
            return this.float32[a + 0] = e,
            this.float32[a + 1] = r,
            this.float32[a + 2] = n,
            this.int16[o + 6] = i,
            this.int16[o + 7] = s,
            t
        }
    }
    ua.prototype.bytesPerElement = 16,
    Bi(ua, "StructArrayLayout2f1f2i16");
    class ca extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n) {
            const i = this.length;
            return this.resize(i + 1),
            this.emplace(i, t, e, r, n)
        }
        emplace(t, e, r, n, i) {
            const s = 12 * t
              , a = 3 * t;
            return this.uint8[s + 0] = e,
            this.uint8[s + 1] = r,
            this.float32[a + 1] = n,
            this.float32[a + 2] = i,
            t
        }
    }
    ca.prototype.bytesPerElement = 12,
    Bi(ca, "StructArrayLayout2ub2f12");
    class ha extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r) {
            const n = this.length;
            return this.resize(n + 1),
            this.emplace(n, t, e, r)
        }
        emplace(t, e, r, n) {
            const i = 3 * t;
            return this.float32[i + 0] = e,
            this.float32[i + 1] = r,
            this.float32[i + 2] = n,
            t
        }
    }
    ha.prototype.bytesPerElement = 12,
    Bi(ha, "StructArrayLayout3f12");
    class pa extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r) {
            const n = this.length;
            return this.resize(n + 1),
            this.emplace(n, t, e, r)
        }
        emplace(t, e, r, n) {
            const i = 3 * t;
            return this.uint16[i + 0] = e,
            this.uint16[i + 1] = r,
            this.uint16[i + 2] = n,
            t
        }
    }
    pa.prototype.bytesPerElement = 6,
    Bi(pa, "StructArrayLayout3ui6");
    class fa extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer),
            this.uint32 = new Uint32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y, m, g, x, v, b) {
            const _ = this.length;
            return this.resize(_ + 1),
            this.emplace(_, t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y, m, g, x, v, b)
        }
        emplace(t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y, m, g, x, v, b, _) {
            const w = 30 * t
              , A = 15 * t
              , k = 60 * t;
            return this.int16[w + 0] = e,
            this.int16[w + 1] = r,
            this.int16[w + 2] = n,
            this.float32[A + 2] = i,
            this.float32[A + 3] = s,
            this.uint16[w + 8] = a,
            this.uint16[w + 9] = o,
            this.uint32[A + 5] = l,
            this.uint32[A + 6] = u,
            this.uint32[A + 7] = c,
            this.uint16[w + 16] = h,
            this.uint16[w + 17] = p,
            this.uint16[w + 18] = f,
            this.float32[A + 10] = d,
            this.float32[A + 11] = y,
            this.uint8[k + 48] = m,
            this.uint8[k + 49] = g,
            this.uint8[k + 50] = x,
            this.uint32[A + 13] = v,
            this.int16[w + 28] = b,
            this.uint8[k + 58] = _,
            t
        }
    }
    fa.prototype.bytesPerElement = 60,
    Bi(fa, "StructArrayLayout3i2f2ui3ul3ui2f3ub1ul1i1ub60");
    class da extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer),
            this.uint32 = new Uint32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y, m, g, x, v, b, _, w, A, k, z, S, M, I, T) {
            const B = this.length;
            return this.resize(B + 1),
            this.emplace(B, t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y, m, g, x, v, b, _, w, A, k, z, S, M, I, T)
        }
        emplace(t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y, m, g, x, v, b, _, w, A, k, z, S, M, I, T, B) {
            const C = 38 * t
              , V = 19 * t;
            return this.int16[C + 0] = e,
            this.int16[C + 1] = r,
            this.int16[C + 2] = n,
            this.float32[V + 2] = i,
            this.float32[V + 3] = s,
            this.int16[C + 8] = a,
            this.int16[C + 9] = o,
            this.int16[C + 10] = l,
            this.int16[C + 11] = u,
            this.int16[C + 12] = c,
            this.int16[C + 13] = h,
            this.uint16[C + 14] = p,
            this.uint16[C + 15] = f,
            this.uint16[C + 16] = d,
            this.uint16[C + 17] = y,
            this.uint16[C + 18] = m,
            this.uint16[C + 19] = g,
            this.uint16[C + 20] = x,
            this.uint16[C + 21] = v,
            this.uint16[C + 22] = b,
            this.uint16[C + 23] = _,
            this.uint16[C + 24] = w,
            this.uint16[C + 25] = A,
            this.uint16[C + 26] = k,
            this.uint16[C + 27] = z,
            this.uint16[C + 28] = S,
            this.uint32[V + 15] = M,
            this.float32[V + 16] = I,
            this.float32[V + 17] = T,
            this.float32[V + 18] = B,
            t
        }
    }
    da.prototype.bytesPerElement = 76,
    Bi(da, "StructArrayLayout3i2f6i15ui1ul3f76");
    class ya extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t) {
            const e = this.length;
            return this.resize(e + 1),
            this.emplace(e, t)
        }
        emplace(t, e) {
            return this.float32[1 * t + 0] = e,
            t
        }
    }
    ya.prototype.bytesPerElement = 4,
    Bi(ya, "StructArrayLayout1f4");
    class ma extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i) {
            const s = this.length;
            return this.resize(s + 1),
            this.emplace(s, t, e, r, n, i)
        }
        emplace(t, e, r, n, i, s) {
            const a = 5 * t;
            return this.float32[a + 0] = e,
            this.float32[a + 1] = r,
            this.float32[a + 2] = n,
            this.float32[a + 3] = i,
            this.float32[a + 4] = s,
            t
        }
    }
    ma.prototype.bytesPerElement = 20,
    Bi(ma, "StructArrayLayout5f20");
    class ga extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.uint32 = new Uint32Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n) {
            const i = this.length;
            return this.resize(i + 1),
            this.emplace(i, t, e, r, n)
        }
        emplace(t, e, r, n, i) {
            const s = 6 * t;
            return this.uint32[3 * t + 0] = e,
            this.uint16[s + 2] = r,
            this.uint16[s + 3] = n,
            this.uint16[s + 4] = i,
            t
        }
    }
    ga.prototype.bytesPerElement = 12,
    Bi(ga, "StructArrayLayout1ul3ui12");
    class xa extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t, e) {
            const r = this.length;
            return this.resize(r + 1),
            this.emplace(r, t, e)
        }
        emplace(t, e, r) {
            const n = 2 * t;
            return this.uint16[n + 0] = e,
            this.uint16[n + 1] = r,
            t
        }
    }
    xa.prototype.bytesPerElement = 4,
    Bi(xa, "StructArrayLayout2ui4");
    class va extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.uint16 = new Uint16Array(this.arrayBuffer);
        }
        emplaceBack(t) {
            const e = this.length;
            return this.resize(e + 1),
            this.emplace(e, t)
        }
        emplace(t, e) {
            return this.uint16[1 * t + 0] = e,
            t
        }
    }
    va.prototype.bytesPerElement = 2,
    Bi(va, "StructArrayLayout1ui2");
    class ba extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e) {
            const r = this.length;
            return this.resize(r + 1),
            this.emplace(r, t, e)
        }
        emplace(t, e, r) {
            const n = 2 * t;
            return this.float32[n + 0] = e,
            this.float32[n + 1] = r,
            t
        }
    }
    ba.prototype.bytesPerElement = 8,
    Bi(ba, "StructArrayLayout2f8");
    class _a extends Gs {
        get a_pos_30() {
            return this._structArray.int16[this._pos2 + 0]
        }
        get a_pos_31() {
            return this._structArray.int16[this._pos2 + 1]
        }
        get a_pos_32() {
            return this._structArray.int16[this._pos2 + 2]
        }
        get a_pos_normal_30() {
            return this._structArray.int16[this._pos2 + 3]
        }
        get a_pos_normal_31() {
            return this._structArray.int16[this._pos2 + 4]
        }
        get a_pos_normal_32() {
            return this._structArray.int16[this._pos2 + 5]
        }
    }
    _a.prototype.size = 12;
    class wa extends na {
        get(t) {
            return new _a(this,t)
        }
    }
    Bi(wa, "FillExtrusionExtArray");
    class Aa extends Gs {
        get projectedAnchorX() {
            return this._structArray.int16[this._pos2 + 0]
        }
        get projectedAnchorY() {
            return this._structArray.int16[this._pos2 + 1]
        }
        get projectedAnchorZ() {
            return this._structArray.int16[this._pos2 + 2]
        }
        get tileAnchorX() {
            return this._structArray.int16[this._pos2 + 3]
        }
        get tileAnchorY() {
            return this._structArray.int16[this._pos2 + 4]
        }
        get x1() {
            return this._structArray.float32[this._pos4 + 3]
        }
        get y1() {
            return this._structArray.float32[this._pos4 + 4]
        }
        get x2() {
            return this._structArray.float32[this._pos4 + 5]
        }
        get y2() {
            return this._structArray.float32[this._pos4 + 6]
        }
        get padding() {
            return this._structArray.int16[this._pos2 + 14]
        }
        get featureIndex() {
            return this._structArray.uint32[this._pos4 + 8]
        }
        get sourceLayerIndex() {
            return this._structArray.uint16[this._pos2 + 18]
        }
        get bucketIndex() {
            return this._structArray.uint16[this._pos2 + 19]
        }
    }
    Aa.prototype.size = 40;
    class ka extends oa {
        get(t) {
            return new Aa(this,t)
        }
    }
    Bi(ka, "CollisionBoxArray");
    class za extends Gs {
        get projectedAnchorX() {
            return this._structArray.int16[this._pos2 + 0]
        }
        get projectedAnchorY() {
            return this._structArray.int16[this._pos2 + 1]
        }
        get projectedAnchorZ() {
            return this._structArray.int16[this._pos2 + 2]
        }
        get tileAnchorX() {
            return this._structArray.float32[this._pos4 + 2]
        }
        get tileAnchorY() {
            return this._structArray.float32[this._pos4 + 3]
        }
        get glyphStartIndex() {
            return this._structArray.uint16[this._pos2 + 8]
        }
        get numGlyphs() {
            return this._structArray.uint16[this._pos2 + 9]
        }
        get vertexStartIndex() {
            return this._structArray.uint32[this._pos4 + 5]
        }
        get lineStartIndex() {
            return this._structArray.uint32[this._pos4 + 6]
        }
        get lineLength() {
            return this._structArray.uint32[this._pos4 + 7]
        }
        get segment() {
            return this._structArray.uint16[this._pos2 + 16]
        }
        get lowerSize() {
            return this._structArray.uint16[this._pos2 + 17]
        }
        get upperSize() {
            return this._structArray.uint16[this._pos2 + 18]
        }
        get lineOffsetX() {
            return this._structArray.float32[this._pos4 + 10]
        }
        get lineOffsetY() {
            return this._structArray.float32[this._pos4 + 11]
        }
        get writingMode() {
            return this._structArray.uint8[this._pos1 + 48]
        }
        get placedOrientation() {
            return this._structArray.uint8[this._pos1 + 49]
        }
        set placedOrientation(t) {
            this._structArray.uint8[this._pos1 + 49] = t;
        }
        get hidden() {
            return this._structArray.uint8[this._pos1 + 50]
        }
        set hidden(t) {
            this._structArray.uint8[this._pos1 + 50] = t;
        }
        get crossTileID() {
            return this._structArray.uint32[this._pos4 + 13]
        }
        set crossTileID(t) {
            this._structArray.uint32[this._pos4 + 13] = t;
        }
        get associatedIconIndex() {
            return this._structArray.int16[this._pos2 + 28]
        }
        get flipState() {
            return this._structArray.uint8[this._pos1 + 58]
        }
        set flipState(t) {
            this._structArray.uint8[this._pos1 + 58] = t;
        }
    }
    za.prototype.size = 60;
    class Sa extends fa {
        get(t) {
            return new za(this,t)
        }
    }
    Bi(Sa, "PlacedSymbolArray");
    class Ma extends Gs {
        get projectedAnchorX() {
            return this._structArray.int16[this._pos2 + 0]
        }
        get projectedAnchorY() {
            return this._structArray.int16[this._pos2 + 1]
        }
        get projectedAnchorZ() {
            return this._structArray.int16[this._pos2 + 2]
        }
        get tileAnchorX() {
            return this._structArray.float32[this._pos4 + 2]
        }
        get tileAnchorY() {
            return this._structArray.float32[this._pos4 + 3]
        }
        get rightJustifiedTextSymbolIndex() {
            return this._structArray.int16[this._pos2 + 8]
        }
        get centerJustifiedTextSymbolIndex() {
            return this._structArray.int16[this._pos2 + 9]
        }
        get leftJustifiedTextSymbolIndex() {
            return this._structArray.int16[this._pos2 + 10]
        }
        get verticalPlacedTextSymbolIndex() {
            return this._structArray.int16[this._pos2 + 11]
        }
        get placedIconSymbolIndex() {
            return this._structArray.int16[this._pos2 + 12]
        }
        get verticalPlacedIconSymbolIndex() {
            return this._structArray.int16[this._pos2 + 13]
        }
        get key() {
            return this._structArray.uint16[this._pos2 + 14]
        }
        get textBoxStartIndex() {
            return this._structArray.uint16[this._pos2 + 15]
        }
        get textBoxEndIndex() {
            return this._structArray.uint16[this._pos2 + 16]
        }
        get verticalTextBoxStartIndex() {
            return this._structArray.uint16[this._pos2 + 17]
        }
        get verticalTextBoxEndIndex() {
            return this._structArray.uint16[this._pos2 + 18]
        }
        get iconBoxStartIndex() {
            return this._structArray.uint16[this._pos2 + 19]
        }
        get iconBoxEndIndex() {
            return this._structArray.uint16[this._pos2 + 20]
        }
        get verticalIconBoxStartIndex() {
            return this._structArray.uint16[this._pos2 + 21]
        }
        get verticalIconBoxEndIndex() {
            return this._structArray.uint16[this._pos2 + 22]
        }
        get featureIndex() {
            return this._structArray.uint16[this._pos2 + 23]
        }
        get numHorizontalGlyphVertices() {
            return this._structArray.uint16[this._pos2 + 24]
        }
        get numVerticalGlyphVertices() {
            return this._structArray.uint16[this._pos2 + 25]
        }
        get numIconVertices() {
            return this._structArray.uint16[this._pos2 + 26]
        }
        get numVerticalIconVertices() {
            return this._structArray.uint16[this._pos2 + 27]
        }
        get useRuntimeCollisionCircles() {
            return this._structArray.uint16[this._pos2 + 28]
        }
        get crossTileID() {
            return this._structArray.uint32[this._pos4 + 15]
        }
        set crossTileID(t) {
            this._structArray.uint32[this._pos4 + 15] = t;
        }
        get textOffset0() {
            return this._structArray.float32[this._pos4 + 16]
        }
        get textOffset1() {
            return this._structArray.float32[this._pos4 + 17]
        }
        get collisionCircleDiameter() {
            return this._structArray.float32[this._pos4 + 18]
        }
    }
    Ma.prototype.size = 76;
    class Ia extends da {
        get(t) {
            return new Ma(this,t)
        }
    }
    Bi(Ia, "SymbolInstanceArray");
    class Ta extends ya {
        getoffsetX(t) {
            return this.float32[1 * t + 0]
        }
    }
    Bi(Ta, "GlyphOffsetArray");
    class Ba extends Js {
        getx(t) {
            return this.int16[3 * t + 0]
        }
        gety(t) {
            return this.int16[3 * t + 1]
        }
        gettileUnitDistanceFromAnchor(t) {
            return this.int16[3 * t + 2]
        }
    }
    Bi(Ba, "SymbolLineVertexArray");
    class Ca extends Gs {
        get featureIndex() {
            return this._structArray.uint32[this._pos4 + 0]
        }
        get sourceLayerIndex() {
            return this._structArray.uint16[this._pos2 + 2]
        }
        get bucketIndex() {
            return this._structArray.uint16[this._pos2 + 3]
        }
        get layoutVertexArrayOffset() {
            return this._structArray.uint16[this._pos2 + 4]
        }
    }
    Ca.prototype.size = 12;
    class Va extends ga {
        get(t) {
            return new Ca(this,t)
        }
    }
    Bi(Va, "FeatureIndexArray");
    class Pa extends Gs {
        get a_centroid_pos0() {
            return this._structArray.uint16[this._pos2 + 0]
        }
        get a_centroid_pos1() {
            return this._structArray.uint16[this._pos2 + 1]
        }
    }
    Pa.prototype.size = 4;
    class Da extends xa {
        get(t) {
            return new Pa(this,t)
        }
    }
    Bi(Da, "FillExtrusionCentroidArray");
    class Ea extends Gs {
        get a_pos_30() {
            return this._structArray.int16[this._pos2 + 0]
        }
        get a_pos_31() {
            return this._structArray.int16[this._pos2 + 1]
        }
        get a_pos_32() {
            return this._structArray.int16[this._pos2 + 2]
        }
        get a_pos_normal_30() {
            return this._structArray.int16[this._pos2 + 3]
        }
        get a_pos_normal_31() {
            return this._structArray.int16[this._pos2 + 4]
        }
        get a_pos_normal_32() {
            return this._structArray.int16[this._pos2 + 5]
        }
    }
    Ea.prototype.size = 12;
    class Fa extends na {
        get(t) {
            return new Ea(this,t)
        }
    }
    Bi(Fa, "CircleGlobeExtArray");
    class La extends Xs {
        _refreshViews() {
            this.uint8 = new Uint8Array(this.arrayBuffer),
            this.int16 = new Int16Array(this.arrayBuffer),
            this.float32 = new Float32Array(this.arrayBuffer);
        }
        emplaceBack(t, e, r, n, i, s) {
            const a = this.length;
            return this.resize(a + 1),
            this.emplace(a, t, e, r, n, i, s)
        }
        emplace(t, e, r, n, i, s, a) {
            const o = 10 * t
              , l = 5 * t;
            return this.int16[o + 0] = e,
            this.int16[o + 1] = r,
            this.float32[l + 1] = n,
            this.float32[l + 2] = i,
            this.float32[l + 3] = s,
            this.float32[l + 4] = a,
            t
        }
    }
    La.prototype.bytesPerElement = 20,
    Bi(La, "StructArrayLayout2i4f20");
    const Ra = Ys([{
        name: "a_pattern_to",
        components: 4,
        type: "Uint16"
    }, {
        name: "a_pattern_from",
        components: 4,
        type: "Uint16"
    }, {
        name: "a_pixel_ratio_to",
        components: 1,
        type: "Uint16"
    }, {
        name: "a_pixel_ratio_from",
        components: 1,
        type: "Uint16"
    }])
      , ja = Ys([{
        name: "a_dash_to",
        components: 4,
        type: "Uint16"
    }, {
        name: "a_dash_from",
        components: 4,
        type: "Uint16"
    }]);
    var Ua = fe((function(t) {
        t.exports = function(t, e) {
            var r, n, i, s, a, o, l, u;
            for (n = t.length - (r = 3 & t.length),
            i = e,
            a = 3432918353,
            o = 461845907,
            u = 0; u < n; )
                l = 255 & t.charCodeAt(u) | (255 & t.charCodeAt(++u)) << 8 | (255 & t.charCodeAt(++u)) << 16 | (255 & t.charCodeAt(++u)) << 24,
                ++u,
                i = 27492 + (65535 & (s = 5 * (65535 & (i = (i ^= l = (65535 & (l = (l = (65535 & l) * a + (((l >>> 16) * a & 65535) << 16) & 4294967295) << 15 | l >>> 17)) * o + (((l >>> 16) * o & 65535) << 16) & 4294967295) << 13 | i >>> 19)) + ((5 * (i >>> 16) & 65535) << 16) & 4294967295)) + ((58964 + (s >>> 16) & 65535) << 16);
            switch (l = 0,
            r) {
            case 3:
                l ^= (255 & t.charCodeAt(u + 2)) << 16;
            case 2:
                l ^= (255 & t.charCodeAt(u + 1)) << 8;
            case 1:
                i ^= l = (65535 & (l = (l = (65535 & (l ^= 255 & t.charCodeAt(u))) * a + (((l >>> 16) * a & 65535) << 16) & 4294967295) << 15 | l >>> 17)) * o + (((l >>> 16) * o & 65535) << 16) & 4294967295;
            }
            return i ^= t.length,
            i = 2246822507 * (65535 & (i ^= i >>> 16)) + ((2246822507 * (i >>> 16) & 65535) << 16) & 4294967295,
            i = 3266489909 * (65535 & (i ^= i >>> 13)) + ((3266489909 * (i >>> 16) & 65535) << 16) & 4294967295,
            (i ^= i >>> 16) >>> 0
        }
        ;
    }
    ))
      , Oa = fe((function(t) {
        t.exports = function(t, e) {
            for (var r, n = t.length, i = e ^ n, s = 0; n >= 4; )
                r = 1540483477 * (65535 & (r = 255 & t.charCodeAt(s) | (255 & t.charCodeAt(++s)) << 8 | (255 & t.charCodeAt(++s)) << 16 | (255 & t.charCodeAt(++s)) << 24)) + ((1540483477 * (r >>> 16) & 65535) << 16),
                i = 1540483477 * (65535 & i) + ((1540483477 * (i >>> 16) & 65535) << 16) ^ (r = 1540483477 * (65535 & (r ^= r >>> 24)) + ((1540483477 * (r >>> 16) & 65535) << 16)),
                n -= 4,
                ++s;
            switch (n) {
            case 3:
                i ^= (255 & t.charCodeAt(s + 2)) << 16;
            case 2:
                i ^= (255 & t.charCodeAt(s + 1)) << 8;
            case 1:
                i = 1540483477 * (65535 & (i ^= 255 & t.charCodeAt(s))) + ((1540483477 * (i >>> 16) & 65535) << 16);
            }
            return i = 1540483477 * (65535 & (i ^= i >>> 13)) + ((1540483477 * (i >>> 16) & 65535) << 16),
            (i ^= i >>> 15) >>> 0
        }
        ;
    }
    ))
      , $a = Ua
      , qa = Oa;
    $a.murmur3 = Ua,
    $a.murmur2 = qa;
    class Na {
        constructor() {
            this.ids = [],
            this.positions = [],
            this.indexed = !1;
        }
        add(t, e, r, n) {
            this.ids.push(Za(t)),
            this.positions.push(e, r, n);
        }
        getPositions(t) {
            const e = Za(t);
            let r = 0
              , n = this.ids.length - 1;
            for (; r < n; ) {
                const t = r + n >> 1;
                this.ids[t] >= e ? n = t : r = t + 1;
            }
            const i = [];
            for (; this.ids[r] === e; )
                i.push({
                    index: this.positions[3 * r],
                    start: this.positions[3 * r + 1],
                    end: this.positions[3 * r + 2]
                }),
                r++;
            return i
        }
        static serialize(t, e) {
            const r = new Float64Array(t.ids)
              , n = new Uint32Array(t.positions);
            return Ga(r, n, 0, r.length - 1),
            e && e.push(r.buffer, n.buffer),
            {
                ids: r,
                positions: n
            }
        }
        static deserialize(t) {
            const e = new Na;
            return e.ids = t.ids,
            e.positions = t.positions,
            e.indexed = !0,
            e
        }
    }
    function Za(t) {
        const e = +t;
        return !isNaN(e) && Number.MIN_SAFE_INTEGER <= e && e <= Number.MAX_SAFE_INTEGER ? e : $a(String(t))
    }
    function Ga(t, e, r, n) {
        for (; r < n; ) {
            const i = t[r + n >> 1];
            let s = r - 1
              , a = n + 1;
            for (; ; ) {
                do {
                    s++;
                } while (t[s] < i);
                do {
                    a--;
                } while (t[a] > i);
                if (s >= a)
                    break;
                Xa(t, s, a),
                Xa(e, 3 * s, 3 * a),
                Xa(e, 3 * s + 1, 3 * a + 1),
                Xa(e, 3 * s + 2, 3 * a + 2);
            }
            a - r < n - a ? (Ga(t, e, r, a),
            r = a + 1) : (Ga(t, e, a + 1, n),
            n = a);
        }
    }
    function Xa(t, e, r) {
        const n = t[e];
        t[e] = t[r],
        t[r] = n;
    }
    Bi(Na, "FeaturePositionMap");
    class Ya {
        constructor(t) {
            this.gl = t.gl,
            this.initialized = !1;
        }
        fetchUniformLocation(t, e) {
            return this.location || this.initialized || (this.location = this.gl.getUniformLocation(t, e),
            this.initialized = !0),
            !!this.location
        }
    }
    class Ha extends Ya {
        constructor(t) {
            super(t),
            this.current = 0;
        }
        set(t, e, r) {
            this.fetchUniformLocation(t, e) && this.current !== r && (this.current = r,
            this.gl.uniform1f(this.location, r));
        }
    }
    class Ka extends Ya {
        constructor(t) {
            super(t),
            this.current = [0, 0, 0, 0];
        }
        set(t, e, r) {
            this.fetchUniformLocation(t, e) && (r[0] === this.current[0] && r[1] === this.current[1] && r[2] === this.current[2] && r[3] === this.current[3] || (this.current = r,
            this.gl.uniform4f(this.location, r[0], r[1], r[2], r[3])));
        }
    }
    class Ja extends Ya {
        constructor(t) {
            super(t),
            this.current = me.transparent;
        }
        set(t, e, r) {
            this.fetchUniformLocation(t, e) && (r.r === this.current.r && r.g === this.current.g && r.b === this.current.b && r.a === this.current.a || (this.current = r,
            this.gl.uniform4f(this.location, r.r, r.g, r.b, r.a)));
        }
    }
    const Wa = new Float32Array(16)
      , Qa = new Float32Array(9)
      , to = new Float32Array(4);
    function eo(t) {
        return [Ns(255 * t.r, 255 * t.g), Ns(255 * t.b, 255 * t.a)]
    }
    class ro {
        constructor(t, e, r) {
            this.value = t,
            this.uniformNames = e.map((t=>`u_${t}`)),
            this.type = r;
        }
        setUniform(t, e, r, n, i) {
            e.set(t, i, n.constantOr(this.value));
        }
        getBinding(t, e) {
            return "color" === this.type ? new Ja(t) : new Ha(t)
        }
    }
    class no {
        constructor(t, e) {
            this.uniformNames = e.map((t=>`u_${t}`)),
            this.patternFrom = null,
            this.patternTo = null,
            this.pixelRatioFrom = 1,
            this.pixelRatioTo = 1;
        }
        setConstantPatternPositions(t, e) {
            this.pixelRatioFrom = e.pixelRatio || 1,
            this.pixelRatioTo = t.pixelRatio || 1,
            this.patternFrom = e.tl.concat(e.br),
            this.patternTo = t.tl.concat(t.br);
        }
        setUniform(t, e, r, n, i) {
            const s = "u_pattern_to" === i || "u_dash_to" === i ? this.patternTo : "u_pattern_from" === i || "u_dash_from" === i ? this.patternFrom : "u_pixel_ratio_to" === i ? this.pixelRatioTo : "u_pixel_ratio_from" === i ? this.pixelRatioFrom : null;
            s && e.set(t, i, s);
        }
        getBinding(t, e) {
            return "u_pattern_from" === e || "u_pattern_to" === e || "u_dash_from" === e || "u_dash_to" === e ? new Ka(t) : new Ha(t)
        }
    }
    class io {
        constructor(t, e, r, n) {
            this.expression = t,
            this.type = r,
            this.maxValue = 0,
            this.paintVertexAttributes = e.map((t=>({
                name: `a_${t}`,
                type: "Float32",
                components: "color" === r ? 2 : 1,
                offset: 0
            }))),
            this.paintVertexArray = new n;
        }
        populatePaintArray(t, e, r, n, i, s) {
            const a = this.paintVertexArray.length
              , o = this.expression.evaluate(new Ts(0), e, {}, i, n, s);
            this.paintVertexArray.resize(t),
            this._setPaintValue(a, t, o);
        }
        updatePaintArray(t, e, r, n, i) {
            const s = this.expression.evaluate({
                zoom: 0
            }, r, n, void 0, i);
            this._setPaintValue(t, e, s);
        }
        _setPaintValue(t, e, r) {
            if ("color" === this.type) {
                const n = eo(r);
                for (let r = t; r < e; r++)
                    this.paintVertexArray.emplace(r, n[0], n[1]);
            } else {
                for (let n = t; n < e; n++)
                    this.paintVertexArray.emplace(n, r);
                this.maxValue = Math.max(this.maxValue, Math.abs(r));
            }
        }
        upload(t) {
            this.paintVertexArray && this.paintVertexArray.arrayBuffer && (this.paintVertexBuffer && this.paintVertexBuffer.buffer ? this.paintVertexBuffer.updateData(this.paintVertexArray) : this.paintVertexBuffer = t.createVertexBuffer(this.paintVertexArray, this.paintVertexAttributes, this.expression.isStateDependent));
        }
        destroy() {
            this.paintVertexBuffer && this.paintVertexBuffer.destroy();
        }
    }
    class so {
        constructor(t, e, r, n, i, s) {
            this.expression = t,
            this.uniformNames = e.map((t=>`u_${t}_t`)),
            this.type = r,
            this.useIntegerZoom = n,
            this.zoom = i,
            this.maxValue = 0,
            this.paintVertexAttributes = e.map((t=>({
                name: `a_${t}`,
                type: "Float32",
                components: "color" === r ? 4 : 2,
                offset: 0
            }))),
            this.paintVertexArray = new s;
        }
        populatePaintArray(t, e, r, n, i, s) {
            const a = this.expression.evaluate(new Ts(this.zoom), e, {}, i, n, s)
              , o = this.expression.evaluate(new Ts(this.zoom + 1), e, {}, i, n, s)
              , l = this.paintVertexArray.length;
            this.paintVertexArray.resize(t),
            this._setPaintValue(l, t, a, o);
        }
        updatePaintArray(t, e, r, n, i) {
            const s = this.expression.evaluate({
                zoom: this.zoom
            }, r, n, void 0, i)
              , a = this.expression.evaluate({
                zoom: this.zoom + 1
            }, r, n, void 0, i);
            this._setPaintValue(t, e, s, a);
        }
        _setPaintValue(t, e, r, n) {
            if ("color" === this.type) {
                const i = eo(r)
                  , s = eo(n);
                for (let r = t; r < e; r++)
                    this.paintVertexArray.emplace(r, i[0], i[1], s[0], s[1]);
            } else {
                for (let i = t; i < e; i++)
                    this.paintVertexArray.emplace(i, r, n);
                this.maxValue = Math.max(this.maxValue, Math.abs(r), Math.abs(n));
            }
        }
        upload(t) {
            this.paintVertexArray && this.paintVertexArray.arrayBuffer && (this.paintVertexBuffer && this.paintVertexBuffer.buffer ? this.paintVertexBuffer.updateData(this.paintVertexArray) : this.paintVertexBuffer = t.createVertexBuffer(this.paintVertexArray, this.paintVertexAttributes, this.expression.isStateDependent));
        }
        destroy() {
            this.paintVertexBuffer && this.paintVertexBuffer.destroy();
        }
        setUniform(t, e, r, n, i) {
            const s = this.useIntegerZoom ? Math.floor(r.zoom) : r.zoom
              , a = d(this.expression.interpolationFactor(s, this.zoom, this.zoom + 1), 0, 1);
            e.set(t, i, a);
        }
        getBinding(t, e) {
            return new Ha(t)
        }
    }
    class ao {
        constructor(t, e, r, n, i, s, a, o) {
            this.expression = t,
            this.type = r,
            this.useIntegerZoom = n,
            this.zoom = i,
            this.layerId = a,
            this.paintVertexAttributes = ("array" === r ? ja : Ra).members;
            for (let t = 0; t < e.length; ++t)
                ;
            this.zoomInPaintVertexArray = new s,
            this.zoomOutPaintVertexArray = new s,
            this.property = o;
        }
        populatePaintArray(t, e, r) {
            const n = this.zoomInPaintVertexArray.length;
            this.zoomInPaintVertexArray.resize(t),
            this.zoomOutPaintVertexArray.resize(t),
            this._setPaintValues(n, t, e.patterns && e.patterns[this.layerId], r);
        }
        updatePaintArray(t, e, r, n, i, s) {
            this._setPaintValues(t, e, r.patterns && r.patterns[this.layerId], s);
        }
        _setPaintValues(t, e, r, n) {
            if (!n || !r)
                return;
            let {min: i, mid: s, max: a} = r;
            "line-outline-dasharray" === String(this.property) && (i = r.min_out,
            s = r.mid_out,
            a = r.max_out);
            const o = n[i]
              , l = n[s]
              , u = n[a];
            if (o && l && u)
                for (let r = t; r < e; r++)
                    this._setPaintValue(this.zoomInPaintVertexArray, r, l, o),
                    this._setPaintValue(this.zoomOutPaintVertexArray, r, l, u);
        }
        _setPaintValue(t, e, r, n) {
            t.emplace(e, r.tl[0], r.tl[1], r.br[0], r.br[1], n.tl[0], n.tl[1], n.br[0], n.br[1], r.pixelRatio, n.pixelRatio);
        }
        upload(t) {
            this.zoomInPaintVertexArray && this.zoomInPaintVertexArray.arrayBuffer && this.zoomOutPaintVertexArray && this.zoomOutPaintVertexArray.arrayBuffer && (this.zoomInPaintVertexBuffer = t.createVertexBuffer(this.zoomInPaintVertexArray, this.paintVertexAttributes, this.expression.isStateDependent),
            this.zoomOutPaintVertexBuffer = t.createVertexBuffer(this.zoomOutPaintVertexArray, this.paintVertexAttributes, this.expression.isStateDependent));
        }
        destroy() {
            this.zoomOutPaintVertexBuffer && this.zoomOutPaintVertexBuffer.destroy(),
            this.zoomInPaintVertexBuffer && this.zoomInPaintVertexBuffer.destroy();
        }
    }
    class oo {
        constructor(t, e, r=(()=>!0)) {
            this.binders = {},
            this._buffers = [];
            const n = [];
            for (const i in t.paint._values) {
                if (!r(i))
                    continue;
                const s = t.paint.get(i);
                if (!(s instanceof Fs && bn(s.property.specification)))
                    continue;
                const a = co(i, t.type)
                  , o = s.value
                  , l = s.property.specification.type
                  , u = s.property.useIntegerZoom
                  , c = s.property.specification["property-type"]
                  , h = "cross-faded" === c || "cross-faded-data-driven" === c
                  , p = ("line-dasharray" === String(i) || "line-outline-dasharray" === String(i)) && "constant" !== t.layout.get("line-cap").value.kind;
                if ("constant" !== o.kind || p)
                    if ("source" === o.kind || p || h) {
                        const r = fo(i, l, "source");
                        this.binders[i] = h ? new ao(o,a,l,u,e,r,t.id,i) : new io(o,a,l,r),
                        n.push(`/a_${i}`);
                    } else {
                        const t = fo(i, l, "composite");
                        this.binders[i] = new so(o,a,l,u,e,t),
                        n.push(`/z_${i}`);
                    }
                else
                    this.binders[i] = h ? new no(o.value,a) : new ro(o.value,a,l),
                    n.push(`/u_${i}`);
            }
            this.cacheKey = n.sort().join("");
        }
        getMaxValue(t) {
            const e = this.binders[t];
            return e instanceof io || e instanceof so ? e.maxValue : 0
        }
        populatePaintArrays(t, e, r, n, i, s) {
            for (const a in this.binders) {
                const o = this.binders[a];
                (o instanceof io || o instanceof so || o instanceof ao) && o.populatePaintArray(t, e, r, n, i, s);
            }
        }
        setConstantPatternPositions(t, e) {
            for (const r in this.binders) {
                const n = this.binders[r];
                n instanceof no && n.setConstantPatternPositions(t, e);
            }
        }
        updatePaintArrays(t, e, r, n, i, s) {
            let a = !1;
            for (const o in t) {
                const l = e.getPositions(o);
                for (const e of l) {
                    const l = r.feature(e.index);
                    for (const r in this.binders) {
                        const u = this.binders[r];
                        if ((u instanceof io || u instanceof so || u instanceof ao) && !0 === u.expression.isStateDependent) {
                            const c = n.paint.get(r);
                            u.expression = c.value,
                            u.updatePaintArray(e.start, e.end, l, t[o], i, s),
                            a = !0;
                        }
                    }
                }
            }
            return a
        }
        defines() {
            const t = [];
            for (const e in this.binders) {
                const r = this.binders[e];
                (r instanceof ro || r instanceof no) && t.push(...r.uniformNames.map((t=>`#define HAS_UNIFORM_${t}`)));
            }
            return t
        }
        getBinderAttributes() {
            const t = [];
            for (const e in this.binders) {
                const r = this.binders[e];
                if (r instanceof io || r instanceof so || r instanceof ao)
                    for (let e = 0; e < r.paintVertexAttributes.length; e++)
                        t.push(r.paintVertexAttributes[e].name);
            }
            return t
        }
        getBinderUniforms() {
            const t = [];
            for (const e in this.binders) {
                const r = this.binders[e];
                if (r instanceof ro || r instanceof no || r instanceof so)
                    for (const e of r.uniformNames)
                        t.push(e);
            }
            return t
        }
        getPaintVertexBuffers() {
            return this._buffers
        }
        getUniforms(t) {
            const e = [];
            for (const r in this.binders) {
                const n = this.binders[r];
                if (n instanceof ro || n instanceof no || n instanceof so)
                    for (const i of n.uniformNames)
                        e.push({
                            name: i,
                            property: r,
                            binding: n.getBinding(t, i)
                        });
            }
            return e
        }
        setUniforms(t, e, r, n, i) {
            for (const {name: e, property: s, binding: a} of r)
                this.binders[s].setUniform(t, a, i, n.get(s), e);
        }
        updatePaintBuffers(t) {
            this._buffers = [];
            for (const e in this.binders) {
                const r = this.binders[e];
                if (t && r instanceof ao) {
                    const e = 2 === t.fromScale ? r.zoomInPaintVertexBuffer : r.zoomOutPaintVertexBuffer;
                    e && this._buffers.push(e);
                } else
                    (r instanceof io || r instanceof so) && r.paintVertexBuffer && this._buffers.push(r.paintVertexBuffer);
            }
        }
        upload(t) {
            for (const e in this.binders) {
                const r = this.binders[e];
                (r instanceof io || r instanceof so || r instanceof ao) && r.upload(t);
            }
            this.updatePaintBuffers();
        }
        destroy() {
            for (const t in this.binders) {
                const e = this.binders[t];
                (e instanceof io || e instanceof so || e instanceof ao) && e.destroy();
            }
        }
    }
    class lo {
        constructor(t, e, r=(()=>!0)) {
            this.programConfigurations = {};
            for (const n of t)
                this.programConfigurations[n.id] = new oo(n,e,r);
            this.needsUpload = !1,
            this._featureMap = new Na,
            this._bufferOffset = 0;
        }
        populatePaintArrays(t, e, r, n, i, s, a) {
            for (const r in this.programConfigurations)
                this.programConfigurations[r].populatePaintArrays(t, e, n, i, s, a);
            void 0 !== e.id && this._featureMap.add(e.id, r, this._bufferOffset, t),
            this._bufferOffset = t,
            this.needsUpload = !0;
        }
        updatePaintArrays(t, e, r, n, i) {
            for (const s of r)
                this.needsUpload = this.programConfigurations[s.id].updatePaintArrays(t, this._featureMap, e, s, n, i) || this.needsUpload;
        }
        get(t) {
            return this.programConfigurations[t]
        }
        upload(t) {
            if (this.needsUpload) {
                for (const e in this.programConfigurations)
                    this.programConfigurations[e].upload(t);
                this.needsUpload = !1;
            }
        }
        destroy() {
            for (const t in this.programConfigurations)
                this.programConfigurations[t].destroy();
        }
    }
    const uo = {
        "text-opacity": ["opacity"],
        "icon-opacity": ["opacity"],
        "text-color": ["fill_color"],
        "icon-color": ["fill_color"],
        "text-halo-color": ["halo_color"],
        "icon-halo-color": ["halo_color"],
        "text-halo-blur": ["halo_blur"],
        "icon-halo-blur": ["halo_blur"],
        "text-halo-width": ["halo_width"],
        "icon-halo-width": ["halo_width"],
        "line-gap-width": ["gapwidth"],
        "line-pattern": ["pattern_to", "pattern_from", "pixel_ratio_to", "pixel_ratio_from"],
        "fill-pattern": ["pattern_to", "pattern_from", "pixel_ratio_to", "pixel_ratio_from"],
        "fill-extrusion-pattern": ["pattern_to", "pattern_from", "pixel_ratio_to", "pixel_ratio_from"],
        "line-dasharray": ["dash_to", "dash_from"],
        "line-outline-dasharray": ["dash_to", "dash_from"],
        "line-outline-width": ["width"],
        "line-outline-floorwidth": ["floorwidth"],
        "line-outline-color": ["color"]
    };
    function co(t, e) {
        return "eline" == e && (e = "line"),
        uo[t] || [t.replace(`${e}-`, "").replace(/-/g, "_")]
    }
    const ho = {
        "line-pattern": {
            source: ea,
            composite: ea
        },
        "fill-pattern": {
            source: ea,
            composite: ea
        },
        "fill-extrusion-pattern": {
            source: ea,
            composite: ea
        },
        "line-dasharray": {
            source: ra,
            composite: ra
        },
        "line-outline-dasharray": {
            source: ra,
            composite: ra
        }
    }
      , po = {
        color: {
            source: ba,
            composite: ta
        },
        number: {
            source: ya,
            composite: ba
        }
    };
    function fo(t, e, r) {
        const n = ho[t];
        return n && n[r] || po[e][r]
    }
    Bi(ro, "ConstantBinder"),
    Bi(no, "CrossFadedConstantBinder"),
    Bi(io, "SourceExpressionBinder"),
    Bi(ao, "CrossFadedCompositeBinder"),
    Bi(so, "CompositeExpressionBinder"),
    Bi(oo, "ProgramConfiguration", {
        omit: ["_buffers"]
    }),
    Bi(lo, "ProgramConfigurationSet");
    const yo = "-transition";
    class mo extends $t {
        constructor(t, e) {
            if (super(),
            this.id = t.id,
            this.type = t.type,
            this._featureFilter = {
                filter: ()=>!0,
                needGeometry: !1,
                needFeature: !1
            },
            this._filterCompiled = !1,
            "custom" !== t.type && (this.metadata = (t = t).metadata,
            this.minzoom = t.minzoom,
            this.maxzoom = t.maxzoom,
            "background" !== t.type && "sky" !== t.type && (this.source = t.source,
            this.sourceLayer = t["source-layer"],
            this.filter = t.filter),
            e.layout && (this._unevaluatedLayout = new Es(e.layout)),
            e.paint)) {
                this._transitionablePaint = new Vs(e.paint);
                for (const e in t.paint)
                    this.setPaintProperty(e, t.paint[e], {
                        validate: !1
                    });
                for (const e in t.layout)
                    this.setLayoutProperty(e, t.layout[e], {
                        validate: !1
                    });
                this._transitioningPaint = this._transitionablePaint.untransitioned(),
                this.paint = new Ls(e.paint);
            }
        }
        getCrossfadeParameters() {
            return this._crossfadeParameters
        }
        getLayoutProperty(t) {
            return "visibility" === t ? this.visibility : this._unevaluatedLayout.getValue(t)
        }
        setLayoutProperty(t, e, r={}) {
            null != e && this._validate(ki, `layers.${this.id}.layout.${t}`, t, e, r) || ("visibility" !== t ? this._unevaluatedLayout.setValue(t, e) : this.visibility = e);
        }
        getPaintProperty(t) {
            return z(t, yo) ? this._transitionablePaint.getTransition(t.slice(0, -yo.length)) : this._transitionablePaint.getValue(t)
        }
        setPaintProperty(t, e, r={}) {
            if (null != e && this._validate(Ai, `layers.${this.id}.paint.${t}`, t, e, r))
                return !1;
            if (z(t, yo))
                return this._transitionablePaint.setTransition(t.slice(0, -yo.length), e || void 0),
                !1;
            {
                const r = this._transitionablePaint._values[t]
                  , n = "cross-faded-data-driven" === r.property.specification["property-type"]
                  , i = r.value.isDataDriven()
                  , s = r.value;
                this._transitionablePaint.setValue(t, e),
                this._handleSpecialPaintPropertyUpdate(t);
                const a = this._transitionablePaint._values[t].value;
                return a.isDataDriven() || i || n || this._handleOverridablePaintPropertyUpdate(t, s, a)
            }
        }
        _handleSpecialPaintPropertyUpdate(t) {}
        getProgramIds() {
            return null
        }
        getProgramConfiguration(t) {
            return null
        }
        _handleOverridablePaintPropertyUpdate(t, e, r) {
            return !1
        }
        isHidden(t) {
            return !!(this.minzoom && t < this.minzoom) || !!(this.maxzoom && t >= this.maxzoom) || "none" === this.visibility
        }
        updateTransitions(t) {
            this._transitioningPaint = this._transitionablePaint.transitioned(t, this._transitioningPaint);
        }
        hasTransition() {
            return this._transitioningPaint.hasTransition()
        }
        recalculate(t, e) {
            t.getCrossfadeParameters && (this._crossfadeParameters = t.getCrossfadeParameters()),
            this._unevaluatedLayout && (this.layout = this._unevaluatedLayout.possiblyEvaluate(t, void 0, e)),
            this.paint = this._transitioningPaint.possiblyEvaluate(t, void 0, e);
        }
        serialize() {
            const t = {
                id: this.id,
                type: this.type,
                source: this.source,
                "source-layer": this.sourceLayer,
                metadata: this.metadata,
                minzoom: this.minzoom,
                maxzoom: this.maxzoom,
                filter: this.filter,
                layout: this._unevaluatedLayout && this._unevaluatedLayout.serialize(),
                paint: this._transitionablePaint && this._transitionablePaint.serialize()
            };
            return this.visibility && (t.layout = t.layout || {},
            t.layout.visibility = this.visibility),
            M(t, ((t,e)=>!(void 0 === t || "layout" === e && !Object.keys(t).length || "paint" === e && !Object.keys(t).length)))
        }
        _validate(t, e, r, n, i={}) {
            return (!i || !1 !== i.validate) && Si(this, t.call(wi, {
                key: e,
                layerType: this.type,
                objectKey: r,
                value: n,
                styleSpec: qt,
                style: {
                    glyphs: !0,
                    sprite: !0
                }
            }))
        }
        is3D() {
            return !1
        }
        isSky() {
            return !1
        }
        isTileClipped() {
            return !1
        }
        hasOffscreenPass() {
            return !1
        }
        resize() {}
        isStateDependent() {
            for (const t in this.paint._values) {
                const e = this.paint.get(t);
                if (e instanceof Fs && bn(e.property.specification) && ("source" === e.value.kind || "composite" === e.value.kind) && e.value.isStateDependent)
                    return !0
            }
            return !1
        }
        compileFilter() {
            this._filterCompiled || (this._featureFilter = Hn(this.filter),
            this._filterCompiled = !0);
        }
        invalidateCompiledFilter() {
            this._filterCompiled = !1;
        }
        dynamicFilter() {
            return this._featureFilter.dynamicFilter
        }
        dynamicFilterNeedsFeature() {
            return this._featureFilter.needFeature
        }
    }
    const go = Ys([{
        name: "a_pos",
        components: 2,
        type: "Int16"
    }], 4)
      , xo = Ys([{
        name: "a_pos_3",
        components: 3,
        type: "Int16"
    }, {
        name: "a_pos_normal_3",
        components: 3,
        type: "Int16"
    }]);
    class vo {
        constructor(t=[]) {
            this.segments = t;
        }
        prepareSegment(t, e, r, n) {
            let i = this.segments[this.segments.length - 1];
            return t > vo.MAX_VERTEX_ARRAY_LENGTH && B(`Max vertices per segment is ${vo.MAX_VERTEX_ARRAY_LENGTH}: bucket requested ${t}`),
            (!i || i.vertexLength + t > vo.MAX_VERTEX_ARRAY_LENGTH || i.sortKey !== n) && (i = {
                vertexOffset: e.length,
                primitiveOffset: r.length,
                vertexLength: 0,
                primitiveLength: 0
            },
            void 0 !== n && (i.sortKey = n),
            this.segments.push(i)),
            i
        }
        get() {
            return this.segments
        }
        destroy() {
            for (const t of this.segments)
                for (const e in t.vaos)
                    t.vaos[e].destroy();
        }
        static simpleSegment(t, e, r, n) {
            return new vo([{
                vertexOffset: t,
                primitiveOffset: e,
                vertexLength: r,
                primitiveLength: n,
                vaos: {},
                sortKey: 0
            }])
        }
    }
    vo.MAX_VERTEX_ARRAY_LENGTH = Math.pow(2, 16) - 1,
    Bi(vo, "SegmentVector");
    var bo = 8192;
    class _o {
        constructor(t, e) {
            t && (e ? this.setSouthWest(t).setNorthEast(e) : 4 === t.length ? this.setSouthWest([t[0], t[1]]).setNorthEast([t[2], t[3]]) : this.setSouthWest(t[0]).setNorthEast(t[1]));
        }
        setNorthEast(t) {
            return this._ne = t instanceof Ao ? new Ao(t.lng,t.lat) : Ao.convert(t),
            this
        }
        setSouthWest(t) {
            return this._sw = t instanceof Ao ? new Ao(t.lng,t.lat) : Ao.convert(t),
            this
        }
        extend(t) {
            const e = this._sw
              , r = this._ne;
            let n, i;
            if (t instanceof Ao)
                n = t,
                i = t;
            else {
                if (!(t instanceof _o))
                    return Array.isArray(t) ? 4 === t.length || t.every(Array.isArray) ? this.extend(_o.convert(t)) : this.extend(Ao.convert(t)) : this;
                if (n = t._sw,
                i = t._ne,
                !n || !i)
                    return this
            }
            return e || r ? (e.lng = Math.min(n.lng, e.lng),
            e.lat = Math.min(n.lat, e.lat),
            r.lng = Math.max(i.lng, r.lng),
            r.lat = Math.max(i.lat, r.lat)) : (this._sw = new Ao(n.lng,n.lat),
            this._ne = new Ao(i.lng,i.lat)),
            this
        }
        getCenter() {
            return new Ao((this._sw.lng + this._ne.lng) / 2,(this._sw.lat + this._ne.lat) / 2)
        }
        getSouthWest() {
            return this._sw
        }
        getNorthEast() {
            return this._ne
        }
        getNorthWest() {
            return new Ao(this.getWest(),this.getNorth())
        }
        getSouthEast() {
            return new Ao(this.getEast(),this.getSouth())
        }
        getWest() {
            return this._sw.lng
        }
        getSouth() {
            return this._sw.lat
        }
        getEast() {
            return this._ne.lng
        }
        getNorth() {
            return this._ne.lat
        }
        toArray() {
            return [this._sw.toArray(), this._ne.toArray()]
        }
        toString() {
            return `LngLatBounds(${this._sw.toString()}, ${this._ne.toString()})`
        }
        isEmpty() {
            return !(this._sw && this._ne)
        }
        contains(t) {
            const {lng: e, lat: r} = Ao.convert(t);
            let n = this._sw.lng <= e && e <= this._ne.lng;
            return this._sw.lng > this._ne.lng && (n = this._sw.lng >= e && e >= this._ne.lng),
            this._sw.lat <= r && r <= this._ne.lat && n
        }
        static convert(t) {
            return !t || t instanceof _o ? t : new _o(t)
        }
    }
    const wo = 6371008.8;
    class Ao {
        constructor(t, e) {
            if (isNaN(t) || isNaN(e))
                throw new Error(`Invalid LngLat object: (${t}, ${e})`);
            if (this.lng = +t,
            this.lat = +e,
            this.lat > 90 || this.lat < -90)
                throw new Error("Invalid LngLat latitude value: must be between -90 and 90")
        }
        wrap() {
            return new Ao(m(this.lng, -180, 180),this.lat)
        }
        toArray() {
            return [this.lng, this.lat]
        }
        toString() {
            return `LngLat(${this.lng}, ${this.lat})`
        }
        distanceTo(t) {
            const e = Math.PI / 180
              , r = this.lat * e
              , n = t.lat * e
              , i = Math.sin(r) * Math.sin(n) + Math.cos(r) * Math.cos(n) * Math.cos((t.lng - this.lng) * e);
            return wo * Math.acos(Math.min(i, 1))
        }
        toBounds(t=0) {
            const e = 360 * t / 40075017
              , r = e / Math.cos(Math.PI / 180 * this.lat);
            return new _o(new Ao(this.lng - r,this.lat - e),new Ao(this.lng + r,this.lat + e))
        }
        static convert(t) {
            if (t instanceof Ao)
                return t;
            if (Array.isArray(t) && (2 === t.length || 3 === t.length))
                return new Ao(Number(t[0]),Number(t[1]));
            if (!Array.isArray(t) && "object" == typeof t && null !== t)
                return new Ao(Number("lng"in t ? t.lng : t.lon),Number(t.lat));
            throw new Error("`LngLatLike` argument must be specified as a LngLat instance, an object {lng: <lng>, lat: <lat>}, an object {lon: <lng>, lat: <lat>}, or an array of [<lng>, <lat>]")
        }
    }
    const ko = 2 * Math.PI * wo;
    function zo(t) {
        return ko * Math.cos(t * Math.PI / 180)
    }
    function So(t) {
        return (180 + t) / 360
    }
    function Mo(t) {
        return (180 - 180 / Math.PI * Math.log(Math.tan(Math.PI / 4 + t * Math.PI / 360))) / 360
    }
    function Io(t, e) {
        return t / zo(e)
    }
    function To(t) {
        return 360 * t - 180
    }
    function Bo(t) {
        return 360 / Math.PI * Math.atan(Math.exp((180 - 360 * t) * Math.PI / 180)) - 90
    }
    function Co(t, e) {
        return t * zo(Bo(e))
    }
    function Vo(t) {
        return 1 / Math.cos(t * Math.PI / 180)
    }
    class Po {
        constructor(t, e, r=0) {
            this.x = +t,
            this.y = +e,
            this.z = +r;
        }
        static fromLngLat(t, e=0) {
            const r = Ao.convert(t);
            return new Po(So(r.lng),Mo(r.lat),Io(e, r.lat))
        }
        toLngLat() {
            return new Ao(To(this.x),Bo(this.y))
        }
        toAltitude() {
            return Co(this.z, this.y)
        }
        meterInMercatorCoordinateUnits() {
            return 1 / ko * Vo(Bo(this.y))
        }
    }
    var Do = Object.freeze({
        __proto__: null,
        circumferenceAtLatitude: zo,
        mercatorXfromLng: So,
        mercatorYfromLat: Mo,
        mercatorZfromAltitude: Io,
        lngFromMercatorX: To,
        latFromMercatorY: Bo,
        altitudeFromMercatorZ: Co,
        MAX_MERCATOR_LATITUDE: 85.051129,
        mercatorScale: Vo,
        default: Po
    });
    const Eo = 2 * Math.PI * 6378137;
    function Fo(t) {
        return Eo * Math.cos(t * Math.PI / 180)
    }
    function Lo(t) {
        return (180 + t) / 360
    }
    function Ro(t) {
        return (90 - t) / 360
    }
    function jo(t, e) {
        return t / Fo(e)
    }
    function Uo(t) {
        return 360 * t - 180
    }
    function Oo(t) {
        return 90 - 360 * t
    }
    function $o(t, e) {
        return t * Fo(Oo(e))
    }
    function qo(t) {
        return 1 / Math.cos(t * Math.PI / 180)
    }
    class No {
        constructor(t, e, r=0) {
            this.x = +t,
            this.y = +e,
            this.z = +r;
        }
        static fromLngLat(t, e=0) {
            const r = Ao.convert(t);
            return new No(Lo(r.lng),Ro(r.lat),jo(e, r.lat))
        }
        toLngLat() {
            return new Ao(Uo(this.x),Oo(this.y))
        }
        toAltitude() {
            return $o(this.z, this.y)
        }
        meterInMercatorCoordinateUnits() {
            return 1 / Eo * qo(Oo(this.y))
        }
    }
    const Zo = {
        "EPSG:3857": Do,
        "EPSG:4326": Object.freeze({
            __proto__: null,
            mercatorXfromLng: Lo,
            mercatorYfromLat: Ro,
            mercatorZfromAltitude: jo,
            lngFromMercatorX: Uo,
            latFromMercatorY: Oo,
            altitudeFromMercatorZ: $o,
            MAX_MERCATOR_LATITUDE: 85.051129,
            mercatorScale: qo,
            default: No
        })
    };
    let Go = "EPSG:3857";
    function Xo(t) {
        t && (Z.crs = t,
        Go = t);
    }
    const Yo = 2 * Math.PI * 6378137;
    function Ho(t) {
        return Zo[Z.crs || Go].mercatorXfromLng(t)
    }
    function Ko(t) {
        return Zo[Z.crs || Go].mercatorYfromLat(t)
    }
    function Jo(t, e) {
        return Zo[Z.crs || Go].mercatorZfromAltitude(t, e)
    }
    function Wo(t) {
        return Zo[Z.crs || Go].lngFromMercatorX(t)
    }
    function Qo(t) {
        return Zo[Z.crs || Go].latFromMercatorY(t)
    }
    function tl(t, e) {
        return Zo[Z.crs || Go].altitudeFromMercatorZ(t, e)
    }
    const el = 85.051129;
    function rl(t) {
        return Zo[Z.crs || Go].mercatorScale(t)
    }
    class nl {
        constructor(t, e, r=0) {
            this.x = +t,
            this.y = +e,
            this.z = +r;
        }
        static fromLngLat(t, e=0) {
            const r = Ao.convert(t);
            return new nl(Ho(r.lng),Ko(r.lat),Jo(e, r.lat))
        }
        toLngLat() {
            return new Ao(Wo(this.x),Qo(this.y))
        }
        toAltitude() {
            return tl(this.z, this.y)
        }
        meterInMercatorCoordinateUnits() {
            return 1 / Yo * rl(Qo(this.y))
        }
    }
    function il(t, e, r, n, s, a, o, l, u) {
        const c = (e + n) / 2
          , h = (r + s) / 2
          , p = new i(c,h);
        l(p),
        function(t, e, r, n, i, s) {
            const a = r - i
              , o = n - s;
            return Math.abs((n - e) * a - (r - t) * o) / Math.hypot(a, o)
        }(p.x, p.y, a.x, a.y, o.x, o.y) >= u ? (il(t, e, r, c, h, a, p, l, u),
        il(t, c, h, n, s, p, o, l, u)) : t.push(o);
    }
    function sl(t, e, r) {
        let n = t[0]
          , i = n.x
          , s = n.y;
        e(n);
        const a = [n];
        for (let o = 1; o < t.length; o++) {
            const l = t[o]
              , {x: u, y: c} = l;
            e(l),
            il(a, i, s, u, c, n, l, e, r),
            i = u,
            s = c,
            n = l;
        }
        return a
    }
    function al(t, e, r, n, i) {
        if (i(e, r)) {
            const s = e.add(r).mult(.5);
            n(s),
            al(t, e, s, n, i),
            al(t, s, r, n, i);
        } else
            t.push(r);
    }
    function ol(t, e, r) {
        let n = t[0];
        e(n);
        const i = [n];
        for (let s = 1; s < t.length; s++) {
            const a = t[s];
            e(a),
            al(i, n, a, e, r),
            n = a;
        }
        return i
    }
    const ll = 2147483648
      , ul = function(t) {
        return Math.abs(t - 180) <= 1e-6 ? 2147483647 : parseInt(t * ll / 180 + .5)
    }
      , cl = function(t, e, r, n) {
        let i = parseInt(33 - e - t);
        n < -90 && (n = -90),
        n > 90 && (n = 90),
        r < -180 && (r = -180),
        r > 180 && (r = 180);
        let s = ul(r)
          , a = ul(n)
          , o = s / (1 << i)
          , l = a / (1 << i);
        return s = o > 0 ? parseInt(o + .5) : parseInt(o - .5),
        a = l > 0 ? parseInt(l + .5) : parseInt(l - .5),
        {
            x: s,
            y: a
        }
    }
      , hl = function(t, e, r) {
        let n = {}
          , i = 1 << r
          , s = 360 / i
          , a = 180 / i;
        return e = i - e - 1,
        n.low_lon = s * t - 180,
        n.low_lat = a * e - 90,
        n.high_lon = s * (t + 1) - 180,
        n.high_lat = a * (e + 1) - 90,
        n
    }
      , pl = function(t, e) {
        return 2 == e ? t < 5 ? 11 : t < 14 ? 12 : 13 : 3 == e ? 12 : t <= 3 ? 11 : 12
    }
      , fl = function(t, e, r, n, i, s) {
        let a = parseInt(i + r)
          , o = parseInt(s + n)
          , l = 33 - e - t;
        return i = a << l,
        a > 0 && i < 0 && (i = 2147483647),
        {
            lon: 180 * i / ll,
            lat: 180 * (s = o << l) / ll
        }
    }
      , dl = function(t, e, r, n, i, s, a) {
        let o = a || pl(t, e)
          , l = function(t, e, r, n) {
            let i = hl(r, n, t);
            return cl(t, e, i.low_lon, i.low_lat)
        }(t, o, r, n);
        return fl(t, o, l.x, l.y, i, s)
    }
      , yl = function(t) {
        return -90 == t ? 1 : 90 == t ? 0 : (180 - 180 / Math.PI * Math.log(Math.tan(Math.PI / 4 + t * Math.PI / 360))) / 360
    }
      , ml = function(t, e, r, n) {
        var i = Math.pow(2, r)
          , s = hl(t, e, r)
          , a = yl(s.high_lat);
        if ("all" == n) {
            var o = yl(s.low_lat);
            return {
                top: a * i,
                bottom: o * i,
                height: (o - a) * i
            }
        }
        return a * i
    }
      , gl = function(t, e) {
        return t / bo * (e._tileH || 1) + (e._tileY || e.y)
    }
      , xl = function(t) {
        let e = "Sg4326" == t.reference;
        return {
            top: e ? t._tileY : t.y,
            bottom: e ? t._tileY + t._tileH : t.y + 1
        }
    }
      , vl = Math.pow(2, 14) - 1
      , bl = -vl - 1;
    function _l(t, e) {
        const r = Math.round(t.x * e)
          , n = Math.round(t.y * e);
        return t.x = d(r, bl, vl),
        t.y = d(n, bl, vl),
        (r < t.x || r > t.x + 1 || n < t.y || n > t.y + 1) && B("Geometry exceeds allowed extent, reduce your vector tile buffer size"),
        t
    }
    function wl(t, e, r) {
        let n = t.loadGeometry();
        const s = t.extent
          , a = bo / s;
        if ("Sg4326" == e.reference) {
            const s = !t.properties && 1 !== t.type
              , a = r && r.projection.isReprojectedInTileSpace;
            var o = e.x
              , l = e.y
              , u = e.z
              , c = Math.pow(2, u)
              , h = e._tileY
              , p = e._tileH;
            let f = t.properties && t.properties.resolution || pl(u, t.type)
              , d = function(t, e, r, n) {
                let i = hl(r, n, t);
                return {
                    ws: cl(t, e, i.low_lon, i.low_lat),
                    ne: cl(t, e, i.high_lon, i.high_lat)
                }
            }(u, f, o, l)
              , y = d.ws.x
              , m = d.ws.y
              , g = Math.PI / 4
              , x = Math.PI / 360
              , v = 180 / Math.PI;
            s && (n = [[new i(0,0), new i(d.ne.x - d.ws.x,0), new i(d.ne.x - d.ws.x,d.ne.y - d.ws.y), new i(0,d.ne.y - d.ws.y), new i(0,0)]]);
            const b = t=>{
                var e, n, i = fl(u, f, y, m, t.x, t.y);
                if (a) {
                    const s = r.projection.project(i.lon, i.lat);
                    e = s.x,
                    n = s.y,
                    t.x = Math.round(bo * (e * r.scale - r.x)),
                    t.y = Math.round(bo * (n * r.scale - r._tileY) / r._tileH),
                    t.y < 0 ? t.y = 0 : t.y > bo && (t.y = bo),
                    t.x < 0 ? t.x = 0 : t.x > bo && (t.x = bo);
                } else {
                    e = (180 + i.lon) / 360;
                    var s = i.lat;
                    n = -90 == s ? 1 : 90 == s ? 0 : (180 - v * Math.log(Math.tan(g + s * x))) / 360,
                    t.x = Math.round(bo * (e * c - o)),
                    t.y = Math.round(bo * (n * c - h) / p);
                }
            }
            ;
            for (let e = 0; e < n.length; e++)
                if (a && 1 !== t.type)
                    n[e] = sl(n[e], b, 1);
                else {
                    const t = [];
                    for (const r of n[e])
                        b(r),
                        t.push(r);
                    n[e] = t;
                }
            return n
        }
        if (e && r && r.projection.isReprojectedInTileSpace) {
            const i = 1 << e.z
              , {scale: a, x: o, y: l, projection: u} = r
              , c = t=>{
                const r = Wo((e.x + t.x / s) / i)
                  , n = Qo((e.y + t.y / s) / i)
                  , c = u.project(r, n);
                t.x = (c.x * a - o) * s,
                t.y = (c.y * a - l) * s;
            }
            ;
            for (let e = 0; e < n.length; e++)
                if (1 !== t.type)
                    n[e] = sl(n[e], c, 1);
                else {
                    const t = [];
                    for (const r of n[e])
                        r.x < 0 || r.x >= s || r.y < 0 || r.y >= s || (c(r),
                        t.push(r));
                    n[e] = t;
                }
        }
        for (const t of n)
            for (const e of t)
                _l(e, a);
        return n
    }
    function Al(t, e) {
        return {
            type: t.type,
            id: t.id,
            properties: t.properties,
            geometry: e ? wl(t) : []
        }
    }
    function kl(t, e, r, n, i) {
        t.emplaceBack(2 * e + (n + 1) / 2, 2 * r + (i + 1) / 2);
    }
    function zl(t, e, r) {
        const n = 16384;
        t.emplaceBack(e.x, e.y, e.z, r[0] * n, r[1] * n, r[2] * n);
    }
    class Sl {
        constructor(t) {
            this.zoom = t.zoom,
            this.overscaling = t.overscaling,
            this.layers = t.layers,
            this.layerIds = this.layers.map((t=>t.id)),
            this.index = t.index,
            this.hasPattern = !1,
            this.projection = t.projection,
            this.layoutVertexArray = new Ks,
            this.indexArray = new pa,
            this.segments = new vo,
            this.programConfigurations = new lo(t.layers,t.zoom),
            this.stateDependentLayerIds = this.layers.filter((t=>t.isStateDependent())).map((t=>t.id));
        }
        populate(t, e, r, n) {
            const i = this.layers[0]
              , s = [];
            let a = null;
            "circle" === i.type && (a = i.layout.get("circle-sort-key"));
            for (const {feature: e, id: i, index: o, sourceLayerIndex: l, order: u} of t) {
                const t = this.layers[0]._featureFilter.needGeometry
                  , c = Al(e, t);
                if (!this.layers[0]._featureFilter.filter(new Ts(this.zoom), c, r))
                    continue;
                const h = a ? a.evaluate(c, {}, r) : void 0
                  , p = {
                    id: i,
                    properties: e.properties,
                    type: e.type,
                    sourceLayerIndex: l,
                    index: o,
                    geometry: t ? c.geometry : wl(e, r, n),
                    patterns: {},
                    sortKey: h,
                    order: u
                };
                s.push(p);
            }
            a && s.sort(((t,e)=>t.sortKey - e.sortKey));
            let o = null;
            "globe" === n.projection.name && (this.globeExtVertexArray = new Fa,
            o = n.projection);
            for (const n of s) {
                const {geometry: i, index: s, sourceLayerIndex: a, order: l} = n
                  , u = t[l].feature;
                this.addFeature(n, i, s, e.availableImages, r, o),
                e.featureIndex.insert(u, i, s, a, this.index);
            }
        }
        update(t, e, r, n) {
            this.stateDependentLayers.length && this.programConfigurations.updatePaintArrays(t, e, this.stateDependentLayers, r, n);
        }
        isEmpty() {
            return 0 === this.layoutVertexArray.length
        }
        uploadPending() {
            return !this.uploaded || this.programConfigurations.needsUpload
        }
        upload(t) {
            this.uploaded || (this.layoutVertexBuffer = t.createVertexBuffer(this.layoutVertexArray, go.members),
            this.indexBuffer = t.createIndexBuffer(this.indexArray),
            this.globeExtVertexArray && (this.globeExtVertexBuffer = t.createVertexBuffer(this.globeExtVertexArray, xo.members))),
            this.programConfigurations.upload(t),
            this.uploaded = !0;
        }
        destroy() {
            this.layoutVertexBuffer && (this.layoutVertexBuffer.destroy(),
            this.indexBuffer.destroy(),
            this.programConfigurations.destroy(),
            this.segments.destroy(),
            this.globeExtVertexBuffer && this.globeExtVertexBuffer.destroy());
        }
        addFeature(t, e, r, n, i, s) {
            for (const r of e)
                for (const e of r) {
                    const r = e.x
                      , n = e.y;
                    if (r < 0 || r >= bo || n < 0 || n >= bo)
                        continue;
                    if (s) {
                        const t = s.projectTilePoint(r, n, i)
                          , e = s.upVector(i, r, n)
                          , a = this.globeExtVertexArray;
                        zl(a, t, e),
                        zl(a, t, e),
                        zl(a, t, e),
                        zl(a, t, e);
                    }
                    const a = this.segments.prepareSegment(4, this.layoutVertexArray, this.indexArray, t.sortKey)
                      , o = a.vertexLength;
                    kl(this.layoutVertexArray, r, n, -1, -1),
                    kl(this.layoutVertexArray, r, n, 1, -1),
                    kl(this.layoutVertexArray, r, n, 1, 1),
                    kl(this.layoutVertexArray, r, n, -1, 1),
                    this.indexArray.emplaceBack(o, o + 1, o + 2),
                    this.indexArray.emplaceBack(o, o + 2, o + 3),
                    a.vertexLength += 4,
                    a.primitiveLength += 2;
                }
            this.programConfigurations.populatePaintArrays(this.layoutVertexArray.length, t, r, {}, n, i);
        }
    }
    function Ml(t, e) {
        for (let r = 0; r < t.length; r++)
            if (Fl(e, t[r]))
                return !0;
        for (let r = 0; r < e.length; r++)
            if (Fl(t, e[r]))
                return !0;
        return !!Cl(t, e)
    }
    function Il(t, e, r) {
        return !!Fl(t, e) || !!Pl(e, t, r)
    }
    function Tl(t, e) {
        if (1 === t.length)
            return El(e, t[0]);
        for (let r = 0; r < e.length; r++) {
            const n = e[r];
            for (let e = 0; e < n.length; e++)
                if (Fl(t, n[e]))
                    return !0
        }
        for (let r = 0; r < t.length; r++)
            if (El(e, t[r]))
                return !0;
        for (let r = 0; r < e.length; r++)
            if (Cl(t, e[r]))
                return !0;
        return !1
    }
    function Bl(t, e, r) {
        if (t.length > 1) {
            if (Cl(t, e))
                return !0;
            for (let n = 0; n < e.length; n++)
                if (Pl(e[n], t, r))
                    return !0
        }
        for (let n = 0; n < t.length; n++)
            if (Pl(t[n], e, r))
                return !0;
        return !1
    }
    function Cl(t, e) {
        if (0 === t.length || 0 === e.length)
            return !1;
        for (let r = 0; r < t.length - 1; r++) {
            const n = t[r]
              , i = t[r + 1];
            for (let t = 0; t < e.length - 1; t++)
                if (Vl(n, i, e[t], e[t + 1]))
                    return !0
        }
        return !1
    }
    function Vl(t, e, r, n) {
        return C(t, r, n) !== C(e, r, n) && C(t, e, r) !== C(t, e, n)
    }
    function Pl(t, e, r) {
        const n = r * r;
        if (1 === e.length)
            return t.distSqr(e[0]) < n;
        for (let r = 1; r < e.length; r++)
            if (Dl(t, e[r - 1], e[r]) < n)
                return !0;
        return !1
    }
    function Dl(t, e, r) {
        const n = e.distSqr(r);
        if (0 === n)
            return t.distSqr(e);
        const i = ((t.x - e.x) * (r.x - e.x) + (t.y - e.y) * (r.y - e.y)) / n;
        return t.distSqr(i < 0 ? e : i > 1 ? r : r.sub(e)._mult(i)._add(e))
    }
    function El(t, e) {
        let r, n, i, s = !1;
        for (let a = 0; a < t.length; a++) {
            r = t[a];
            for (let t = 0, a = r.length - 1; t < r.length; a = t++)
                n = r[t],
                i = r[a],
                n.y > e.y != i.y > e.y && e.x < (i.x - n.x) * (e.y - n.y) / (i.y - n.y) + n.x && (s = !s);
        }
        return s
    }
    function Fl(t, e) {
        let r = !1;
        for (let n = 0, i = t.length - 1; n < t.length; i = n++) {
            const s = t[n]
              , a = t[i];
            s.y > e.y != a.y > e.y && e.x < (a.x - s.x) * (e.y - s.y) / (a.y - s.y) + s.x && (r = !r);
        }
        return r
    }
    function Ll(t, e, r, n, s) {
        for (const i of t)
            if (e <= i.x && r <= i.y && n >= i.x && s >= i.y)
                return !0;
        const a = [new i(e,r), new i(e,s), new i(n,s), new i(n,r)];
        if (t.length > 2)
            for (const e of a)
                if (Fl(t, e))
                    return !0;
        for (let e = 0; e < t.length - 1; e++)
            if (Rl(t[e], t[e + 1], a))
                return !0;
        return !1
    }
    function Rl(t, e, r) {
        const n = r[0]
          , i = r[2];
        if (t.x < n.x && e.x < n.x || t.x > i.x && e.x > i.x || t.y < n.y && e.y < n.y || t.y > i.y && e.y > i.y)
            return !1;
        const s = C(t, e, r[0]);
        return s !== C(t, e, r[1]) || s !== C(t, e, r[2]) || s !== C(t, e, r[3])
    }
    function jl(t, e, r) {
        const n = e.paint.get(t).value;
        return "constant" === n.kind ? n.value : r.programConfigurations.get(e.id).getMaxValue(t)
    }
    function Ul(t) {
        return Math.sqrt(t[0] * t[0] + t[1] * t[1])
    }
    function Ol(t, e, r, n, s) {
        if (!e[0] && !e[1])
            return t;
        const a = i.convert(e)._mult(s);
        "viewport" === r && a._rotate(-n);
        const o = [];
        for (let e = 0; e < t.length; e++)
            o.push(t[e].sub(a));
        return o
    }
    function $l(t, e, r, n) {
        const s = i.convert(t)._mult(n);
        return "viewport" === e && s._rotate(-r),
        s
    }
    Bi(Sl, "CircleBucket", {
        omit: ["layers"]
    });
    const ql = new qs({
        "circle-sort-key": new js(qt.layout_circle["circle-sort-key"])
    });
    var Nl = {
        paint: new qs({
            "circle-radius": new js(qt.paint_circle["circle-radius"]),
            "circle-color": new js(qt.paint_circle["circle-color"]),
            "circle-blur": new js(qt.paint_circle["circle-blur"]),
            "circle-opacity": new js(qt.paint_circle["circle-opacity"]),
            "circle-translate": new Rs(qt.paint_circle["circle-translate"]),
            "circle-translate-anchor": new Rs(qt.paint_circle["circle-translate-anchor"]),
            "circle-pitch-scale": new Rs(qt.paint_circle["circle-pitch-scale"]),
            "circle-pitch-alignment": new Rs(qt.paint_circle["circle-pitch-alignment"]),
            "circle-stroke-width": new js(qt.paint_circle["circle-stroke-width"]),
            "circle-stroke-color": new js(qt.paint_circle["circle-stroke-color"]),
            "circle-stroke-opacity": new js(qt.paint_circle["circle-stroke-opacity"]),
            "circle-minzoom": new js(qt.paint_circle["circle-minzoom"]),
            "circle-maxzoom": new js(qt.paint_circle["circle-maxzoom"])
        }),
        layout: ql
    }
      , Zl = 1e-6
      , Gl = "undefined" != typeof Float32Array ? Float32Array : Array;
    function Xl() {
        var t = new Gl(9);
        return Gl != Float32Array && (t[1] = 0,
        t[2] = 0,
        t[3] = 0,
        t[5] = 0,
        t[6] = 0,
        t[7] = 0),
        t[0] = 1,
        t[4] = 1,
        t[8] = 1,
        t
    }
    function Yl(t, e, r) {
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = e[3]
          , o = e[4]
          , l = e[5]
          , u = e[6]
          , c = e[7]
          , h = e[8]
          , p = r[0]
          , f = r[1]
          , d = r[2]
          , y = r[3]
          , m = r[4]
          , g = r[5]
          , x = r[6]
          , v = r[7]
          , b = r[8];
        return t[0] = p * n + f * a + d * u,
        t[1] = p * i + f * o + d * c,
        t[2] = p * s + f * l + d * h,
        t[3] = y * n + m * a + g * u,
        t[4] = y * i + m * o + g * c,
        t[5] = y * s + m * l + g * h,
        t[6] = x * n + v * a + b * u,
        t[7] = x * i + v * o + b * c,
        t[8] = x * s + v * l + b * h,
        t
    }
    function Hl(t) {
        return t[0] = 1,
        t[1] = 0,
        t[2] = 0,
        t[3] = 0,
        t[4] = 0,
        t[5] = 1,
        t[6] = 0,
        t[7] = 0,
        t[8] = 0,
        t[9] = 0,
        t[10] = 1,
        t[11] = 0,
        t[12] = 0,
        t[13] = 0,
        t[14] = 0,
        t[15] = 1,
        t
    }
    function Kl(t, e) {
        var r = e[0]
          , n = e[1]
          , i = e[2]
          , s = e[3]
          , a = e[4]
          , o = e[5]
          , l = e[6]
          , u = e[7]
          , c = e[8]
          , h = e[9]
          , p = e[10]
          , f = e[11]
          , d = e[12]
          , y = e[13]
          , m = e[14]
          , g = e[15]
          , x = r * o - n * a
          , v = r * l - i * a
          , b = r * u - s * a
          , _ = n * l - i * o
          , w = n * u - s * o
          , A = i * u - s * l
          , k = c * y - h * d
          , z = c * m - p * d
          , S = c * g - f * d
          , M = h * m - p * y
          , I = h * g - f * y
          , T = p * g - f * m
          , B = x * T - v * I + b * M + _ * S - w * z + A * k;
        return B ? (t[0] = (o * T - l * I + u * M) * (B = 1 / B),
        t[1] = (i * I - n * T - s * M) * B,
        t[2] = (y * A - m * w + g * _) * B,
        t[3] = (p * w - h * A - f * _) * B,
        t[4] = (l * S - a * T - u * z) * B,
        t[5] = (r * T - i * S + s * z) * B,
        t[6] = (m * b - d * A - g * v) * B,
        t[7] = (c * A - p * b + f * v) * B,
        t[8] = (a * I - o * S + u * k) * B,
        t[9] = (n * S - r * I - s * k) * B,
        t[10] = (d * w - y * b + g * x) * B,
        t[11] = (h * b - c * w - f * x) * B,
        t[12] = (o * z - a * M - l * k) * B,
        t[13] = (r * M - n * z + i * k) * B,
        t[14] = (y * v - d * _ - m * x) * B,
        t[15] = (c * _ - h * v + p * x) * B,
        t) : null
    }
    function Jl(t, e, r) {
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = e[3]
          , o = e[4]
          , l = e[5]
          , u = e[6]
          , c = e[7]
          , h = e[8]
          , p = e[9]
          , f = e[10]
          , d = e[11]
          , y = e[12]
          , m = e[13]
          , g = e[14]
          , x = e[15]
          , v = r[0]
          , b = r[1]
          , _ = r[2]
          , w = r[3];
        return t[0] = v * n + b * o + _ * h + w * y,
        t[1] = v * i + b * l + _ * p + w * m,
        t[2] = v * s + b * u + _ * f + w * g,
        t[3] = v * a + b * c + _ * d + w * x,
        t[4] = (v = r[4]) * n + (b = r[5]) * o + (_ = r[6]) * h + (w = r[7]) * y,
        t[5] = v * i + b * l + _ * p + w * m,
        t[6] = v * s + b * u + _ * f + w * g,
        t[7] = v * a + b * c + _ * d + w * x,
        t[8] = (v = r[8]) * n + (b = r[9]) * o + (_ = r[10]) * h + (w = r[11]) * y,
        t[9] = v * i + b * l + _ * p + w * m,
        t[10] = v * s + b * u + _ * f + w * g,
        t[11] = v * a + b * c + _ * d + w * x,
        t[12] = (v = r[12]) * n + (b = r[13]) * o + (_ = r[14]) * h + (w = r[15]) * y,
        t[13] = v * i + b * l + _ * p + w * m,
        t[14] = v * s + b * u + _ * f + w * g,
        t[15] = v * a + b * c + _ * d + w * x,
        t
    }
    function Wl(t, e, r) {
        var n, i, s, a, o, l, u, c, h, p, f, d, y = r[0], m = r[1], g = r[2];
        return e === t ? (t[12] = e[0] * y + e[4] * m + e[8] * g + e[12],
        t[13] = e[1] * y + e[5] * m + e[9] * g + e[13],
        t[14] = e[2] * y + e[6] * m + e[10] * g + e[14],
        t[15] = e[3] * y + e[7] * m + e[11] * g + e[15]) : (i = e[1],
        s = e[2],
        a = e[3],
        o = e[4],
        l = e[5],
        u = e[6],
        c = e[7],
        h = e[8],
        p = e[9],
        f = e[10],
        d = e[11],
        t[0] = n = e[0],
        t[1] = i,
        t[2] = s,
        t[3] = a,
        t[4] = o,
        t[5] = l,
        t[6] = u,
        t[7] = c,
        t[8] = h,
        t[9] = p,
        t[10] = f,
        t[11] = d,
        t[12] = n * y + o * m + h * g + e[12],
        t[13] = i * y + l * m + p * g + e[13],
        t[14] = s * y + u * m + f * g + e[14],
        t[15] = a * y + c * m + d * g + e[15]),
        t
    }
    function Ql(t, e, r) {
        var n = r[0]
          , i = r[1]
          , s = r[2];
        return t[0] = e[0] * n,
        t[1] = e[1] * n,
        t[2] = e[2] * n,
        t[3] = e[3] * n,
        t[4] = e[4] * i,
        t[5] = e[5] * i,
        t[6] = e[6] * i,
        t[7] = e[7] * i,
        t[8] = e[8] * s,
        t[9] = e[9] * s,
        t[10] = e[10] * s,
        t[11] = e[11] * s,
        t[12] = e[12],
        t[13] = e[13],
        t[14] = e[14],
        t[15] = e[15],
        t
    }
    function tu(t, e, r) {
        var n = Math.sin(r)
          , i = Math.cos(r)
          , s = e[4]
          , a = e[5]
          , o = e[6]
          , l = e[7]
          , u = e[8]
          , c = e[9]
          , h = e[10]
          , p = e[11];
        return e !== t && (t[0] = e[0],
        t[1] = e[1],
        t[2] = e[2],
        t[3] = e[3],
        t[12] = e[12],
        t[13] = e[13],
        t[14] = e[14],
        t[15] = e[15]),
        t[4] = s * i + u * n,
        t[5] = a * i + c * n,
        t[6] = o * i + h * n,
        t[7] = l * i + p * n,
        t[8] = u * i - s * n,
        t[9] = c * i - a * n,
        t[10] = h * i - o * n,
        t[11] = p * i - l * n,
        t
    }
    function eu(t, e, r) {
        var n = Math.sin(r)
          , i = Math.cos(r)
          , s = e[0]
          , a = e[1]
          , o = e[2]
          , l = e[3]
          , u = e[8]
          , c = e[9]
          , h = e[10]
          , p = e[11];
        return e !== t && (t[4] = e[4],
        t[5] = e[5],
        t[6] = e[6],
        t[7] = e[7],
        t[12] = e[12],
        t[13] = e[13],
        t[14] = e[14],
        t[15] = e[15]),
        t[0] = s * i - u * n,
        t[1] = a * i - c * n,
        t[2] = o * i - h * n,
        t[3] = l * i - p * n,
        t[8] = s * n + u * i,
        t[9] = a * n + c * i,
        t[10] = o * n + h * i,
        t[11] = l * n + p * i,
        t
    }
    function ru(t, e) {
        return t[0] = e[0],
        t[1] = 0,
        t[2] = 0,
        t[3] = 0,
        t[4] = 0,
        t[5] = e[1],
        t[6] = 0,
        t[7] = 0,
        t[8] = 0,
        t[9] = 0,
        t[10] = e[2],
        t[11] = 0,
        t[12] = 0,
        t[13] = 0,
        t[14] = 0,
        t[15] = 1,
        t
    }
    function nu(t, e, r) {
        var n, i, s, a = r[0], o = r[1], l = r[2], u = Math.hypot(a, o, l);
        return u < Zl ? null : (a *= u = 1 / u,
        o *= u,
        l *= u,
        n = Math.sin(e),
        i = Math.cos(e),
        t[0] = a * a * (s = 1 - i) + i,
        t[1] = o * a * s + l * n,
        t[2] = l * a * s - o * n,
        t[3] = 0,
        t[4] = a * o * s - l * n,
        t[5] = o * o * s + i,
        t[6] = l * o * s + a * n,
        t[7] = 0,
        t[8] = a * l * s + o * n,
        t[9] = o * l * s - a * n,
        t[10] = l * l * s + i,
        t[11] = 0,
        t[12] = 0,
        t[13] = 0,
        t[14] = 0,
        t[15] = 1,
        t)
    }
    Math.hypot || (Math.hypot = function() {
        for (var t = 0, e = arguments.length; e--; )
            t += arguments[e] * arguments[e];
        return Math.sqrt(t)
    }
    );
    var iu = Jl;
    function su() {
        var t = new Gl(3);
        return Gl != Float32Array && (t[0] = 0,
        t[1] = 0,
        t[2] = 0),
        t
    }
    function au(t) {
        var e = new Gl(3);
        return e[0] = t[0],
        e[1] = t[1],
        e[2] = t[2],
        e
    }
    function ou(t) {
        return Math.hypot(t[0], t[1], t[2])
    }
    function lu(t, e, r) {
        var n = new Gl(3);
        return n[0] = t,
        n[1] = e,
        n[2] = r,
        n
    }
    function uu(t, e, r) {
        return t[0] = e[0] + r[0],
        t[1] = e[1] + r[1],
        t[2] = e[2] + r[2],
        t
    }
    function cu(t, e, r) {
        return t[0] = e[0] - r[0],
        t[1] = e[1] - r[1],
        t[2] = e[2] - r[2],
        t
    }
    function hu(t, e, r) {
        return t[0] = e[0] * r[0],
        t[1] = e[1] * r[1],
        t[2] = e[2] * r[2],
        t
    }
    function pu(t, e, r) {
        return t[0] = Math.min(e[0], r[0]),
        t[1] = Math.min(e[1], r[1]),
        t[2] = Math.min(e[2], r[2]),
        t
    }
    function fu(t, e, r) {
        return t[0] = Math.max(e[0], r[0]),
        t[1] = Math.max(e[1], r[1]),
        t[2] = Math.max(e[2], r[2]),
        t
    }
    function du(t, e, r) {
        return t[0] = e[0] * r,
        t[1] = e[1] * r,
        t[2] = e[2] * r,
        t
    }
    function yu(t, e, r, n) {
        return t[0] = e[0] + r[0] * n,
        t[1] = e[1] + r[1] * n,
        t[2] = e[2] + r[2] * n,
        t
    }
    function mu(t, e) {
        var r = e[0]
          , n = e[1]
          , i = e[2]
          , s = r * r + n * n + i * i;
        return s > 0 && (s = 1 / Math.sqrt(s)),
        t[0] = e[0] * s,
        t[1] = e[1] * s,
        t[2] = e[2] * s,
        t
    }
    function gu(t, e) {
        return t[0] * e[0] + t[1] * e[1] + t[2] * e[2]
    }
    function xu(t, e, r) {
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = r[0]
          , o = r[1]
          , l = r[2];
        return t[0] = i * l - s * o,
        t[1] = s * a - n * l,
        t[2] = n * o - i * a,
        t
    }
    function vu(t, e, r) {
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = r[3] * n + r[7] * i + r[11] * s + r[15];
        return t[0] = (r[0] * n + r[4] * i + r[8] * s + r[12]) / (a = a || 1),
        t[1] = (r[1] * n + r[5] * i + r[9] * s + r[13]) / a,
        t[2] = (r[2] * n + r[6] * i + r[10] * s + r[14]) / a,
        t
    }
    function bu(t, e, r) {
        var n = r[0]
          , i = r[1]
          , s = r[2]
          , a = e[0]
          , o = e[1]
          , l = e[2]
          , u = i * l - s * o
          , c = s * a - n * l
          , h = n * o - i * a
          , p = i * h - s * c
          , f = s * u - n * h
          , d = n * c - i * u
          , y = 2 * r[3];
        return c *= y,
        h *= y,
        f *= 2,
        d *= 2,
        t[0] = a + (u *= y) + (p *= 2),
        t[1] = o + c + f,
        t[2] = l + h + d,
        t
    }
    var _u, wu = cu, Au = hu, ku = ou;
    function zu(t, e, r) {
        return t[0] = e[0] * r,
        t[1] = e[1] * r,
        t[2] = e[2] * r,
        t[3] = e[3] * r,
        t
    }
    function Su(t, e, r) {
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = e[3];
        return t[0] = r[0] * n + r[4] * i + r[8] * s + r[12] * a,
        t[1] = r[1] * n + r[5] * i + r[9] * s + r[13] * a,
        t[2] = r[2] * n + r[6] * i + r[10] * s + r[14] * a,
        t[3] = r[3] * n + r[7] * i + r[11] * s + r[15] * a,
        t
    }
    function Mu() {
        var t = new Gl(4);
        return Gl != Float32Array && (t[0] = 0,
        t[1] = 0,
        t[2] = 0),
        t[3] = 1,
        t
    }
    function Iu(t) {
        return t[0] = 0,
        t[1] = 0,
        t[2] = 0,
        t[3] = 1,
        t
    }
    function Tu(t, e, r) {
        r *= .5;
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = e[3]
          , o = Math.sin(r)
          , l = Math.cos(r);
        return t[0] = n * l + a * o,
        t[1] = i * l + s * o,
        t[2] = s * l - i * o,
        t[3] = a * l - n * o,
        t
    }
    function Bu(t, e, r) {
        r *= .5;
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = e[3]
          , o = Math.sin(r)
          , l = Math.cos(r);
        return t[0] = n * l - s * o,
        t[1] = i * l + a * o,
        t[2] = s * l + n * o,
        t[3] = a * l - i * o,
        t
    }
    function Cu() {
        var t = new Gl(2);
        return Gl != Float32Array && (t[0] = 0,
        t[1] = 0),
        t
    }
    function Vu(t, e, r) {
        return t[0] = e[0] + r[0],
        t[1] = e[1] + r[1],
        t
    }
    function Pu(t, e, r) {
        return t[0] = e[0] - r[0],
        t[1] = e[1] - r[1],
        t
    }
    function Du(t, e, r) {
        return t[0] = e[0] * r,
        t[1] = e[1] * r,
        t
    }
    function Eu(t) {
        return Math.hypot(t[0], t[1])
    }
    function Fu(t, e) {
        var r = e[0]
          , n = e[1]
          , i = r * r + n * n;
        return i > 0 && (i = 1 / Math.sqrt(i)),
        t[0] = e[0] * i,
        t[1] = e[1] * i,
        t
    }
    function Lu(t, e) {
        return t[0] * e[0] + t[1] * e[1]
    }
    su(),
    _u = new Gl(4),
    Gl != Float32Array && (_u[0] = 0,
    _u[1] = 0,
    _u[2] = 0,
    _u[3] = 0),
    su(),
    lu(1, 0, 0),
    lu(0, 1, 0),
    Mu(),
    Mu(),
    Xl();
    var Ru = Pu;
    Cu();
    class ju {
        constructor(t, e) {
            this.pos = t,
            this.dir = e;
        }
        intersectsPlane(t, e, r) {
            const n = gu(e, this.dir);
            if (Math.abs(n) < 1e-6)
                return !1;
            const i = ((t[0] - this.pos[0]) * e[0] + (t[1] - this.pos[1]) * e[1] + (t[2] - this.pos[2]) * e[2]) / n;
            return r[0] = this.pos[0] + this.dir[0] * i,
            r[1] = this.pos[1] + this.dir[1] * i,
            r[2] = this.pos[2] + this.dir[2] * i,
            !0
        }
        closestPointOnSphere(t, e, r) {
            if (function(t, e) {
                var r = t[0]
                  , n = t[1]
                  , i = t[2]
                  , s = e[0]
                  , a = e[1]
                  , o = e[2];
                return Math.abs(r - s) <= Zl * Math.max(1, Math.abs(r), Math.abs(s)) && Math.abs(n - a) <= Zl * Math.max(1, Math.abs(n), Math.abs(a)) && Math.abs(i - o) <= Zl * Math.max(1, Math.abs(i), Math.abs(o))
            }(this.pos, t) || 0 === e)
                return r[0] = r[1] = r[2] = 0,
                !1;
            const [n,i,s] = this.dir
              , a = this.pos[0] - t[0]
              , o = this.pos[1] - t[1]
              , l = this.pos[2] - t[2]
              , u = n * n + i * i + s * s
              , c = 2 * (a * n + o * i + l * s)
              , h = c * c - 4 * u * (a * a + o * o + l * l - e * e);
            if (h < 0) {
                const t = Math.max(-c / 2, 0)
                  , u = a + n * t
                  , h = o + i * t
                  , p = l + s * t
                  , f = Math.hypot(u, h, p);
                return r[0] = u * e / f,
                r[1] = h * e / f,
                r[2] = p * e / f,
                !1
            }
            {
                const t = (-c - Math.sqrt(h)) / (2 * u);
                if (t < 0) {
                    const t = Math.hypot(a, o, l);
                    return r[0] = a * e / t,
                    r[1] = o * e / t,
                    r[2] = l * e / t,
                    !1
                }
                return r[0] = a + n * t,
                r[1] = o + i * t,
                r[2] = l + s * t,
                !0
            }
        }
    }
    class Uu {
        constructor(t, e, r, n, i) {
            this.TL = t,
            this.TR = e,
            this.BR = r,
            this.BL = n,
            this.horizon = i;
        }
        static fromInvProjectionMatrix(t, e, r) {
            const n = [-1, 1, 1]
              , i = [1, 1, 1]
              , s = [1, -1, 1]
              , a = [-1, -1, 1]
              , o = vu(n, n, t)
              , l = vu(i, i, t)
              , u = vu(s, s, t)
              , c = vu(a, a, t);
            return new Uu(o,l,u,c,e / r)
        }
    }
    class Ou {
        constructor(t, e) {
            this.points = t,
            this.planes = e;
        }
        static fromInvProjectionMatrix(t, e, r, n) {
            const i = Math.pow(2, r)
              , s = [[-1, 1, -1, 1], [1, 1, -1, 1], [1, -1, -1, 1], [-1, -1, -1, 1], [-1, 1, 1, 1], [1, 1, 1, 1], [1, -1, 1, 1], [-1, -1, 1, 1]].map((r=>{
                const s = Su([], r, t)
                  , a = 1 / s[3] / e * i;
                return function(t, e, r) {
                    return t[0] = e[0] * r[0],
                    t[1] = e[1] * r[1],
                    t[2] = e[2] * r[2],
                    t[3] = e[3] * r[3],
                    t
                }(s, s, [a, a, n ? 1 / s[3] : a, a])
            }
            ))
              , a = [[0, 1, 2], [6, 5, 4], [0, 3, 7], [2, 1, 5], [3, 2, 6], [0, 4, 5]].map((t=>{
                const e = mu([], xu([], wu([], s[t[0]], s[t[1]]), wu([], s[t[2]], s[t[1]])))
                  , r = -gu(e, s[t[1]]);
                return e.concat(r)
            }
            ));
            return new Ou(s,a)
        }
    }
    class $u {
        static fromPoints(t) {
            const e = [Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE]
              , r = [Number.MIN_VALUE, Number.MIN_VALUE, Number.MIN_VALUE];
            for (const n of t)
                e[0] = Math.min(e[0], n[0]),
                e[1] = Math.min(e[1], n[1]),
                e[2] = Math.min(e[2], n[2]),
                r[0] = Math.max(r[0], n[0]),
                r[1] = Math.max(r[1], n[1]),
                r[2] = Math.max(r[2], n[2]);
            return new $u(e,r)
        }
        constructor(t, e) {
            this.min = t,
            this.max = e,
            this.center = du([], uu([], this.min, this.max), .5);
        }
        quadrant(t) {
            const e = [t % 2 == 0, t < 2]
              , r = au(this.min)
              , n = au(this.max);
            for (let t = 0; t < e.length; t++)
                r[t] = e[t] ? this.min[t] : this.center[t],
                n[t] = e[t] ? this.center[t] : this.max[t];
            return n[2] = this.max[2],
            new $u(r,n)
        }
        distanceX(t) {
            return Math.max(Math.min(this.max[0], t[0]), this.min[0]) - t[0]
        }
        distanceY(t) {
            return Math.max(Math.min(this.max[1], t[1]), this.min[1]) - t[1]
        }
        distanceZ(t) {
            return Math.max(Math.min(this.max[2], t[2]), this.min[2]) - t[2]
        }
        getCorners() {
            const t = this.min
              , e = this.max;
            return [[t[0], t[1], t[2]], [e[0], t[1], t[2]], [e[0], e[1], t[2]], [t[0], e[1], t[2]], [t[0], t[1], e[2]], [e[0], t[1], e[2]], [e[0], e[1], e[2]], [t[0], e[1], e[2]]]
        }
        intersects(t) {
            const e = this.getCorners();
            let r = !0;
            for (let n = 0; n < t.planes.length; n++) {
                const i = t.planes[n];
                let s = 0;
                for (let t = 0; t < e.length; t++)
                    s += gu(i, e[t]) + i[3] >= 0;
                if (0 === s)
                    return 0;
                s !== e.length && (r = !1);
            }
            if (r)
                return 2;
            for (let e = 0; e < 3; e++) {
                let r = Number.MAX_VALUE
                  , n = -Number.MAX_VALUE;
                for (let i = 0; i < t.points.length; i++) {
                    const s = t.points[i][e] - this.min[e];
                    r = Math.min(r, s),
                    n = Math.max(n, s);
                }
                if (n < 0 || r > this.max[e] - this.min[e])
                    return 0
            }
            return 1
        }
    }
    function qu(t, e, r, n, i, s, a, o, l) {
        if (s && t.queryGeometry.isAboveHorizon)
            return !1;
        s && (l *= t.pixelToTileUnitsFactor);
        const u = t.tileID.canonical
          , c = r.projection.upVectorScale(u, r.center.lat, r.worldSize).metersToTile;
        for (const h of e)
            for (const e of h) {
                const h = e.add(o)
                  , p = i && r.elevation ? r.elevation.exaggeration() * i.getElevationAt(h.x, h.y, !0) : 0
                  , f = r.projection.projectTilePoint(h.x, h.y, u);
                if (p > 0) {
                    const t = r.projection.upVector(u, h.x, h.y);
                    f.x += t[0] * c * p,
                    f.y += t[1] * c * p,
                    f.z += t[2] * c * p;
                }
                const d = s ? h : Nu(f.x, f.y, f.z, n)
                  , y = s ? t.tilespaceRays.map((t=>Xu(t, p))) : t.queryGeometry.screenGeometry
                  , m = Su([], [f.x, f.y, f.z, 1], n);
                if (!a && s ? l *= m[3] / r.cameraToCenterDistance : a && !s && (l *= r.cameraToCenterDistance / m[3]),
                s) {
                    const t = Qo(gl(e.y, u) / (1 << u.z));
                    l /= r.projection.pixelsPerMeter(t, 1) / Jo(1, t);
                }
                if (Il(y, d, l))
                    return !0
            }
        return !1
    }
    function Nu(t, e, r, n) {
        const s = Su([], [t, e, r, 1], n);
        return new i(s[0] / s[3],s[1] / s[3])
    }
    const Zu = lu(0, 0, 0)
      , Gu = lu(0, 0, 1);
    function Xu(t, e) {
        const r = su();
        return Zu[2] = e,
        t.intersectsPlane(Zu, Gu, r),
        new i(r[0],r[1])
    }
    class Yu extends Sl {
    }
    function Hu(t, {width: e, height: r}, n, i) {
        if (i) {
            if (i instanceof Uint8ClampedArray)
                i = new Uint8Array(i.buffer);
            else if (i.length !== e * r * n)
                throw new RangeError("mismatched image size")
        } else
            i = new Uint8Array(e * r * n);
        return t.width = e,
        t.height = r,
        t.data = i,
        t
    }
    function Ku(t, e, r) {
        const {width: n, height: i} = e;
        n === t.width && i === t.height || (Ju(t, e, {
            x: 0,
            y: 0
        }, {
            x: 0,
            y: 0
        }, {
            width: Math.min(t.width, n),
            height: Math.min(t.height, i)
        }, r),
        t.width = n,
        t.height = i,
        t.data = e.data);
    }
    function Ju(t, e, r, n, i, s) {
        if (0 === i.width || 0 === i.height)
            return e;
        if (i.width > t.width || i.height > t.height || r.x > t.width - i.width || r.y > t.height - i.height)
            throw new RangeError("out of range source coordinates for image copy");
        if (i.width > e.width || i.height > e.height || n.x > e.width - i.width || n.y > e.height - i.height)
            throw new RangeError("out of range destination coordinates for image copy");
        const a = t.data
          , o = e.data;
        for (let l = 0; l < i.height; l++) {
            const u = ((r.y + l) * t.width + r.x) * s
              , c = ((n.y + l) * e.width + n.x) * s;
            for (let t = 0; t < i.width * s; t++)
                o[c + t] = a[u + t];
        }
        return e
    }
    Bi(Yu, "HeatmapBucket", {
        omit: ["layers"]
    });
    class Wu {
        constructor(t, e) {
            Hu(this, t, 1, e);
        }
        resize(t) {
            Ku(this, new Wu(t), 1);
        }
        clone() {
            return new Wu({
                width: this.width,
                height: this.height
            },new Uint8Array(this.data))
        }
        static copy(t, e, r, n, i) {
            Ju(t, e, r, n, i, 1);
        }
    }
    class Qu {
        constructor(t, e) {
            Hu(this, t, 4, e);
        }
        resize(t) {
            Ku(this, new Qu(t), 4);
        }
        replace(t, e) {
            e ? this.data.set(t) : this.data = t instanceof Uint8ClampedArray ? new Uint8Array(t.buffer) : t;
        }
        clone() {
            return new Qu({
                width: this.width,
                height: this.height
            },new Uint8Array(this.data))
        }
        static copy(t, e, r, n, i) {
            Ju(t, e, r, n, i, 4);
        }
    }
    Bi(Wu, "AlphaImage"),
    Bi(Qu, "RGBAImage");
    var tc = {
        paint: new qs({
            "heatmap-radius": new js(qt.paint_heatmap["heatmap-radius"]),
            "heatmap-weight": new js(qt.paint_heatmap["heatmap-weight"]),
            "heatmap-intensity": new Rs(qt.paint_heatmap["heatmap-intensity"]),
            "heatmap-color": new $s(qt.paint_heatmap["heatmap-color"]),
            "heatmap-opacity": new Rs(qt.paint_heatmap["heatmap-opacity"])
        })
    };
    function ec(t) {
        const e = {}
          , r = t.resolution || 256
          , n = t.clips ? t.clips.length : 1
          , i = t.image || new Qu({
            width: r,
            height: n
        })
          , s = (r,n,s)=>{
            e[t.evaluationKey] = s;
            const a = t.expression.evaluate(e);
            i.data[r + n + 0] = Math.floor(255 * a.r / a.a),
            i.data[r + n + 1] = Math.floor(255 * a.g / a.a),
            i.data[r + n + 2] = Math.floor(255 * a.b / a.a),
            i.data[r + n + 3] = Math.floor(255 * a.a);
        }
        ;
        if (t.clips)
            for (let e = 0, i = 0; e < n; ++e,
            i += 4 * r)
                for (let n = 0, a = 0; n < r; n++,
                a += 4) {
                    const o = n / (r - 1)
                      , {start: l, end: u} = t.clips[e];
                    s(i, a, l * (1 - o) + u * o);
                }
        else
            for (let t = 0, e = 0; t < r; t++,
            e += 4)
                s(0, e, t / (r - 1));
        return i
    }
    var rc = {
        paint: new qs({
            "hillshade-illumination-direction": new Rs(qt.paint_hillshade["hillshade-illumination-direction"]),
            "hillshade-illumination-anchor": new Rs(qt.paint_hillshade["hillshade-illumination-anchor"]),
            "hillshade-exaggeration": new Rs(qt.paint_hillshade["hillshade-exaggeration"]),
            "hillshade-shadow-color": new Rs(qt.paint_hillshade["hillshade-shadow-color"]),
            "hillshade-highlight-color": new Rs(qt.paint_hillshade["hillshade-highlight-color"]),
            "hillshade-accent-color": new Rs(qt.paint_hillshade["hillshade-accent-color"])
        })
    };
    const nc = Ys([{
        name: "a_pos",
        components: 2,
        type: "Int16"
    }], 4)
      , {members: ic} = nc;
    var sc = oc
      , ac = oc;
    function oc(t, e, r) {
        r = r || 2;
        var n, i, s, a, o, l, u, c = e && e.length, h = c ? e[0] * r : t.length, p = lc(t, 0, h, r, !0), f = [];
        if (!p || p.next === p.prev)
            return f;
        if (c && (p = function(t, e, r, n) {
            var i, s, a, o = [];
            for (i = 0,
            s = e.length; i < s; i++)
                (a = lc(t, e[i] * n, i < s - 1 ? e[i + 1] * n : t.length, n, !1)) === a.next && (a.steiner = !0),
                o.push(vc(a));
            for (o.sort(yc),
            i = 0; i < o.length; i++)
                r = mc(o[i], r);
            return r
        }(t, e, p, r)),
        t.length > 80 * r) {
            n = s = t[0],
            i = a = t[1];
            for (var d = r; d < h; d += r)
                (o = t[d]) < n && (n = o),
                (l = t[d + 1]) < i && (i = l),
                o > s && (s = o),
                l > a && (a = l);
            u = 0 !== (u = Math.max(s - n, a - i)) ? 32767 / u : 0;
        }
        return cc(p, f, r, n, i, u, 0),
        f
    }
    function lc(t, e, r, n, i) {
        var s, a;
        if (i === Pc(t, e, r, n) > 0)
            for (s = e; s < r; s += n)
                a = Bc(s, t[s], t[s + 1], a);
        else
            for (s = r - n; s >= e; s -= n)
                a = Bc(s, t[s], t[s + 1], a);
        return a && kc(a, a.next) && (Cc(a),
        a = a.next),
        a
    }
    function uc(t, e) {
        if (!t)
            return t;
        e || (e = t);
        var r, n = t;
        do {
            if (r = !1,
            n.steiner || !kc(n, n.next) && 0 !== wc(n.prev, n, n.next))
                n = n.next;
            else {
                if (Cc(n),
                (n = e = n.prev) === n.next)
                    break;
                r = !0;
            }
        } while (r || n !== e);
        return e
    }
    function cc(t, e, r, n, i, s, a) {
        if (t) {
            !a && s && function(t, e, r, n) {
                var i = t;
                do {
                    0 === i.z && (i.z = xc(i.x, i.y, e, r, n)),
                    i.prevZ = i.prev,
                    i.nextZ = i.next,
                    i = i.next;
                } while (i !== t);
                i.prevZ.nextZ = null,
                i.prevZ = null,
                function(t) {
                    var e, r, n, i, s, a, o, l, u = 1;
                    do {
                        for (r = t,
                        t = null,
                        s = null,
                        a = 0; r; ) {
                            for (a++,
                            n = r,
                            o = 0,
                            e = 0; e < u && (o++,
                            n = n.nextZ); e++)
                                ;
                            for (l = u; o > 0 || l > 0 && n; )
                                0 !== o && (0 === l || !n || r.z <= n.z) ? (i = r,
                                r = r.nextZ,
                                o--) : (i = n,
                                n = n.nextZ,
                                l--),
                                s ? s.nextZ = i : t = i,
                                i.prevZ = s,
                                s = i;
                            r = n;
                        }
                        s.nextZ = null,
                        u *= 2;
                    } while (a > 1)
                }(i);
            }(t, n, i, s);
            for (var o, l, u = t; t.prev !== t.next; )
                if (o = t.prev,
                l = t.next,
                s ? pc(t, n, i, s) : hc(t))
                    e.push(o.i / r | 0),
                    e.push(t.i / r | 0),
                    e.push(l.i / r | 0),
                    Cc(t),
                    t = l.next,
                    u = l.next;
                else if ((t = l) === u) {
                    a ? 1 === a ? cc(t = fc(uc(t), e, r), e, r, n, i, s, 2) : 2 === a && dc(t, e, r, n, i, s) : cc(uc(t), e, r, n, i, s, 1);
                    break
                }
        }
    }
    function hc(t) {
        var e = t.prev
          , r = t
          , n = t.next;
        if (wc(e, r, n) >= 0)
            return !1;
        for (var i = e.x, s = r.x, a = n.x, o = e.y, l = r.y, u = n.y, c = i < s ? i < a ? i : a : s < a ? s : a, h = o < l ? o < u ? o : u : l < u ? l : u, p = i > s ? i > a ? i : a : s > a ? s : a, f = o > l ? o > u ? o : u : l > u ? l : u, d = n.next; d !== e; ) {
            if (d.x >= c && d.x <= p && d.y >= h && d.y <= f && bc(i, o, s, l, a, u, d.x, d.y) && wc(d.prev, d, d.next) >= 0)
                return !1;
            d = d.next;
        }
        return !0
    }
    function pc(t, e, r, n) {
        var i = t.prev
          , s = t
          , a = t.next;
        if (wc(i, s, a) >= 0)
            return !1;
        for (var o = i.x, l = s.x, u = a.x, c = i.y, h = s.y, p = a.y, f = o < l ? o < u ? o : u : l < u ? l : u, d = c < h ? c < p ? c : p : h < p ? h : p, y = o > l ? o > u ? o : u : l > u ? l : u, m = c > h ? c > p ? c : p : h > p ? h : p, g = xc(f, d, e, r, n), x = xc(y, m, e, r, n), v = t.prevZ, b = t.nextZ; v && v.z >= g && b && b.z <= x; ) {
            if (v.x >= f && v.x <= y && v.y >= d && v.y <= m && v !== i && v !== a && bc(o, c, l, h, u, p, v.x, v.y) && wc(v.prev, v, v.next) >= 0)
                return !1;
            if (v = v.prevZ,
            b.x >= f && b.x <= y && b.y >= d && b.y <= m && b !== i && b !== a && bc(o, c, l, h, u, p, b.x, b.y) && wc(b.prev, b, b.next) >= 0)
                return !1;
            b = b.nextZ;
        }
        for (; v && v.z >= g; ) {
            if (v.x >= f && v.x <= y && v.y >= d && v.y <= m && v !== i && v !== a && bc(o, c, l, h, u, p, v.x, v.y) && wc(v.prev, v, v.next) >= 0)
                return !1;
            v = v.prevZ;
        }
        for (; b && b.z <= x; ) {
            if (b.x >= f && b.x <= y && b.y >= d && b.y <= m && b !== i && b !== a && bc(o, c, l, h, u, p, b.x, b.y) && wc(b.prev, b, b.next) >= 0)
                return !1;
            b = b.nextZ;
        }
        return !0
    }
    function fc(t, e, r) {
        var n = t;
        do {
            var i = n.prev
              , s = n.next.next;
            !kc(i, s) && zc(i, n, n.next, s) && Ic(i, s) && Ic(s, i) && (e.push(i.i / r | 0),
            e.push(n.i / r | 0),
            e.push(s.i / r | 0),
            Cc(n),
            Cc(n.next),
            n = t = s),
            n = n.next;
        } while (n !== t);
        return uc(n)
    }
    function dc(t, e, r, n, i, s) {
        var a = t;
        do {
            for (var o = a.next.next; o !== a.prev; ) {
                if (a.i !== o.i && _c(a, o)) {
                    var l = Tc(a, o);
                    return a = uc(a, a.next),
                    l = uc(l, l.next),
                    cc(a, e, r, n, i, s, 0),
                    void cc(l, e, r, n, i, s, 0)
                }
                o = o.next;
            }
            a = a.next;
        } while (a !== t)
    }
    function yc(t, e) {
        return t.x - e.x
    }
    function mc(t, e) {
        var r = function(t, e) {
            var r, n = e, i = t.x, s = t.y, a = -1 / 0;
            do {
                if (s <= n.y && s >= n.next.y && n.next.y !== n.y) {
                    var o = n.x + (s - n.y) * (n.next.x - n.x) / (n.next.y - n.y);
                    if (o <= i && o > a && (a = o,
                    r = n.x < n.next.x ? n : n.next,
                    o === i))
                        return r
                }
                n = n.next;
            } while (n !== e);
            if (!r)
                return null;
            var l, u = r, c = r.x, h = r.y, p = 1 / 0;
            n = r;
            do {
                i >= n.x && n.x >= c && i !== n.x && bc(s < h ? i : a, s, c, h, s < h ? a : i, s, n.x, n.y) && (l = Math.abs(s - n.y) / (i - n.x),
                Ic(n, t) && (l < p || l === p && (n.x > r.x || n.x === r.x && gc(r, n))) && (r = n,
                p = l)),
                n = n.next;
            } while (n !== u);
            return r
        }(t, e);
        if (!r)
            return e;
        var n = Tc(r, t);
        return uc(n, n.next),
        uc(r, r.next)
    }
    function gc(t, e) {
        return wc(t.prev, t, e.prev) < 0 && wc(e.next, t, t.next) < 0
    }
    function xc(t, e, r, n, i) {
        return (t = 1431655765 & ((t = 858993459 & ((t = 252645135 & ((t = 16711935 & ((t = (t - r) * i | 0) | t << 8)) | t << 4)) | t << 2)) | t << 1)) | (e = 1431655765 & ((e = 858993459 & ((e = 252645135 & ((e = 16711935 & ((e = (e - n) * i | 0) | e << 8)) | e << 4)) | e << 2)) | e << 1)) << 1
    }
    function vc(t) {
        var e = t
          , r = t;
        do {
            (e.x < r.x || e.x === r.x && e.y < r.y) && (r = e),
            e = e.next;
        } while (e !== t);
        return r
    }
    function bc(t, e, r, n, i, s, a, o) {
        return (i - a) * (e - o) >= (t - a) * (s - o) && (t - a) * (n - o) >= (r - a) * (e - o) && (r - a) * (s - o) >= (i - a) * (n - o)
    }
    function _c(t, e) {
        return t.next.i !== e.i && t.prev.i !== e.i && !function(t, e) {
            var r = t;
            do {
                if (r.i !== t.i && r.next.i !== t.i && r.i !== e.i && r.next.i !== e.i && zc(r, r.next, t, e))
                    return !0;
                r = r.next;
            } while (r !== t);
            return !1
        }(t, e) && (Ic(t, e) && Ic(e, t) && function(t, e) {
            var r = t
              , n = !1
              , i = (t.x + e.x) / 2
              , s = (t.y + e.y) / 2;
            do {
                r.y > s != r.next.y > s && r.next.y !== r.y && i < (r.next.x - r.x) * (s - r.y) / (r.next.y - r.y) + r.x && (n = !n),
                r = r.next;
            } while (r !== t);
            return n
        }(t, e) && (wc(t.prev, t, e.prev) || wc(t, e.prev, e)) || kc(t, e) && wc(t.prev, t, t.next) > 0 && wc(e.prev, e, e.next) > 0)
    }
    function wc(t, e, r) {
        return (e.y - t.y) * (r.x - e.x) - (e.x - t.x) * (r.y - e.y)
    }
    function kc(t, e) {
        return t.x === e.x && t.y === e.y
    }
    function zc(t, e, r, n) {
        var i = Mc(wc(t, e, r))
          , s = Mc(wc(t, e, n))
          , a = Mc(wc(r, n, t))
          , o = Mc(wc(r, n, e));
        return i !== s && a !== o || !(0 !== i || !Sc(t, r, e)) || !(0 !== s || !Sc(t, n, e)) || !(0 !== a || !Sc(r, t, n)) || !(0 !== o || !Sc(r, e, n))
    }
    function Sc(t, e, r) {
        return e.x <= Math.max(t.x, r.x) && e.x >= Math.min(t.x, r.x) && e.y <= Math.max(t.y, r.y) && e.y >= Math.min(t.y, r.y)
    }
    function Mc(t) {
        return t > 0 ? 1 : t < 0 ? -1 : 0
    }
    function Ic(t, e) {
        return wc(t.prev, t, t.next) < 0 ? wc(t, e, t.next) >= 0 && wc(t, t.prev, e) >= 0 : wc(t, e, t.prev) < 0 || wc(t, t.next, e) < 0
    }
    function Tc(t, e) {
        var r = new Vc(t.i,t.x,t.y)
          , n = new Vc(e.i,e.x,e.y)
          , i = t.next
          , s = e.prev;
        return t.next = e,
        e.prev = t,
        r.next = i,
        i.prev = r,
        n.next = r,
        r.prev = n,
        s.next = n,
        n.prev = s,
        n
    }
    function Bc(t, e, r, n) {
        var i = new Vc(t,e,r);
        return n ? (i.next = n.next,
        i.prev = n,
        n.next.prev = i,
        n.next = i) : (i.prev = i,
        i.next = i),
        i
    }
    function Cc(t) {
        t.next.prev = t.prev,
        t.prev.next = t.next,
        t.prevZ && (t.prevZ.nextZ = t.nextZ),
        t.nextZ && (t.nextZ.prevZ = t.prevZ);
    }
    function Vc(t, e, r) {
        this.i = t,
        this.x = e,
        this.y = r,
        this.prev = null,
        this.next = null,
        this.z = 0,
        this.prevZ = null,
        this.nextZ = null,
        this.steiner = !1;
    }
    function Pc(t, e, r, n) {
        for (var i = 0, s = e, a = r - n; s < r; s += n)
            i += (t[a] - t[s]) * (t[s + 1] + t[a + 1]),
            a = s;
        return i
    }
    function Dc(t, e, r, n, i) {
        Ec(t, e, r || 0, n || t.length - 1, i || Lc);
    }
    function Ec(t, e, r, n, i) {
        for (; n > r; ) {
            if (n - r > 600) {
                var s = n - r + 1
                  , a = e - r + 1
                  , o = Math.log(s)
                  , l = .5 * Math.exp(2 * o / 3)
                  , u = .5 * Math.sqrt(o * l * (s - l) / s) * (a - s / 2 < 0 ? -1 : 1);
                Ec(t, e, Math.max(r, Math.floor(e - a * l / s + u)), Math.min(n, Math.floor(e + (s - a) * l / s + u)), i);
            }
            var c = t[e]
              , h = r
              , p = n;
            for (Fc(t, r, e),
            i(t[n], c) > 0 && Fc(t, r, n); h < p; ) {
                for (Fc(t, h, p),
                h++,
                p--; i(t[h], c) < 0; )
                    h++;
                for (; i(t[p], c) > 0; )
                    p--;
            }
            0 === i(t[r], c) ? Fc(t, r, p) : Fc(t, ++p, n),
            p <= e && (r = p + 1),
            e <= p && (n = p - 1);
        }
    }
    function Fc(t, e, r) {
        var n = t[e];
        t[e] = t[r],
        t[r] = n;
    }
    function Lc(t, e) {
        return t < e ? -1 : t > e ? 1 : 0
    }
    function Rc(t, e) {
        const r = t.length;
        if (r <= 1)
            return [t];
        const n = [];
        let i, s;
        for (let e = 0; e < r; e++) {
            const r = V(t[e]);
            0 !== r && (t[e].area = Math.abs(r),
            void 0 === s && (s = r < 0),
            s === r < 0 ? (i && n.push(i),
            i = [t[e]]) : i.push(t[e]));
        }
        if (i && n.push(i),
        e > 1)
            for (let t = 0; t < n.length; t++)
                n[t].length <= e || (Dc(n[t], e, 1, n[t].length - 1, jc),
                n[t] = n[t].slice(0, e));
        return n
    }
    function jc(t, e) {
        return e.area - t.area
    }
    function Uc(t, e, r) {
        const n = r.patternDependencies;
        let i = !1;
        for (const r of e) {
            const e = r.paint.get(`${t}-pattern`);
            e.isConstant() || (i = !0);
            const s = e.constantOr(null);
            s && (i = !0,
            n[s.to] = !0,
            n[s.from] = !0);
        }
        return i
    }
    function Oc(t, e, r, n, i) {
        const s = i.patternDependencies;
        for (const a of e) {
            const e = a.paint.get(`${t}-pattern`).value;
            if ("constant" !== e.kind) {
                let t = e.evaluate({
                    zoom: n - 1
                }, r, {}, i.availableImages)
                  , o = e.evaluate({
                    zoom: n
                }, r, {}, i.availableImages)
                  , l = e.evaluate({
                    zoom: n + 1
                }, r, {}, i.availableImages);
                t = t && t.name ? t.name : t,
                o = o && o.name ? o.name : o,
                l = l && l.name ? l.name : l,
                s[t] = !0,
                s[o] = !0,
                s[l] = !0,
                r.patterns[a.id] = {
                    min: t,
                    mid: o,
                    max: l
                };
            }
        }
        return r
    }
    oc.deviation = function(t, e, r, n) {
        var i = e && e.length
          , s = Math.abs(Pc(t, 0, i ? e[0] * r : t.length, r));
        if (i)
            for (var a = 0, o = e.length; a < o; a++)
                s -= Math.abs(Pc(t, e[a] * r, a < o - 1 ? e[a + 1] * r : t.length, r));
        var l = 0;
        for (a = 0; a < n.length; a += 3) {
            var u = n[a] * r
              , c = n[a + 1] * r
              , h = n[a + 2] * r;
            l += Math.abs((t[u] - t[h]) * (t[c + 1] - t[u + 1]) - (t[u] - t[c]) * (t[h + 1] - t[u + 1]));
        }
        return 0 === s && 0 === l ? 0 : Math.abs((l - s) / s)
    }
    ,
    oc.flatten = function(t) {
        for (var e = t[0][0].length, r = {
            vertices: [],
            holes: [],
            dimensions: e
        }, n = 0, i = 0; i < t.length; i++) {
            for (var s = 0; s < t[i].length; s++)
                for (var a = 0; a < e; a++)
                    r.vertices.push(t[i][s][a]);
            i > 0 && r.holes.push(n += t[i - 1].length);
        }
        return r
    }
    ,
    sc.default = ac;
    class $c {
        constructor(t) {
            this.zoom = t.zoom,
            this.overscaling = t.overscaling,
            this.layers = t.layers,
            this.layerIds = this.layers.map((t=>t.id)),
            this.index = t.index,
            this.hasPattern = !1,
            this.patternFeatures = [],
            this.layoutVertexArray = new Ks,
            this.indexArray = new pa,
            this.indexArray2 = new xa,
            this.programConfigurations = new lo(t.layers,t.zoom),
            this.segments = new vo,
            this.segments2 = new vo,
            this.stateDependentLayerIds = this.layers.filter((t=>t.isStateDependent())).map((t=>t.id)),
            this.projection = t.projection;
        }
        populate(t, e, r, n) {
            this.hasPattern = Uc("fill", this.layers, e);
            const i = this.layers[0].layout.get("fill-sort-key")
              , s = [];
            for (const {feature: a, id: o, index: l, sourceLayerIndex: u, order: c} of t) {
                const t = this.layers[0]._featureFilter.needGeometry
                  , h = Al(a, t);
                if (!this.layers[0]._featureFilter.filter(new Ts(this.zoom), h, r))
                    continue;
                const p = i ? i.evaluate(h, {}, r, e.availableImages) : void 0
                  , f = {
                    id: o,
                    properties: a.properties,
                    type: a.type,
                    sourceLayerIndex: u,
                    index: l,
                    geometry: t ? h.geometry : wl(a, r, n),
                    patterns: {},
                    sortKey: p,
                    order: c
                };
                s.push(f);
            }
            i && s.sort(((t,e)=>t.sortKey - e.sortKey));
            for (const n of s) {
                const {geometry: i, index: s, sourceLayerIndex: a, order: o} = n;
                if (this.hasPattern) {
                    const t = Oc("fill", this.layers, n, this.zoom, e);
                    this.patternFeatures.push(t);
                } else
                    this.addFeature(n, i, s, r, {}, e.availableImages);
                e.featureIndex.insert(t[o].feature, i, s, a, this.index);
            }
        }
        update(t, e, r, n) {
            this.stateDependentLayers.length && this.programConfigurations.updatePaintArrays(t, e, this.stateDependentLayers, r, n);
        }
        addFeatures(t, e, r, n, i) {
            for (const t of this.patternFeatures)
                this.addFeature(t, t.geometry, t.index, e, r, n);
        }
        isEmpty() {
            return 0 === this.layoutVertexArray.length
        }
        uploadPending() {
            return !this.uploaded || this.programConfigurations.needsUpload
        }
        upload(t) {
            this.uploaded || (this.layoutVertexBuffer = t.createVertexBuffer(this.layoutVertexArray, ic),
            this.indexBuffer = t.createIndexBuffer(this.indexArray),
            this.indexBuffer2 = t.createIndexBuffer(this.indexArray2)),
            this.programConfigurations.upload(t),
            this.uploaded = !0;
        }
        destroy() {
            this.layoutVertexBuffer && (this.layoutVertexBuffer.destroy(),
            this.indexBuffer.destroy(),
            this.indexBuffer2.destroy(),
            this.programConfigurations.destroy(),
            this.segments.destroy(),
            this.segments2.destroy());
        }
        addFeature(t, e, r, n, i, s=[]) {
            for (const t of Rc(e, 500)) {
                let e = 0;
                for (const r of t)
                    e += r.length;
                const r = this.segments.prepareSegment(e, this.layoutVertexArray, this.indexArray)
                  , n = r.vertexLength
                  , i = []
                  , s = [];
                for (const e of t) {
                    if (0 === e.length)
                        continue;
                    e !== t[0] && s.push(i.length / 2);
                    const r = this.segments2.prepareSegment(e.length, this.layoutVertexArray, this.indexArray2)
                      , n = r.vertexLength;
                    this.layoutVertexArray.emplaceBack(e[0].x, e[0].y),
                    this.indexArray2.emplaceBack(n + e.length - 1, n),
                    i.push(e[0].x),
                    i.push(e[0].y);
                    for (let t = 1; t < e.length; t++)
                        this.layoutVertexArray.emplaceBack(e[t].x, e[t].y),
                        this.indexArray2.emplaceBack(n + t - 1, n + t),
                        i.push(e[t].x),
                        i.push(e[t].y);
                    r.vertexLength += e.length,
                    r.primitiveLength += e.length;
                }
                const a = sc(i, s);
                for (let t = 0; t < a.length; t += 3)
                    this.indexArray.emplaceBack(n + a[t], n + a[t + 1], n + a[t + 2]);
                r.vertexLength += e,
                r.primitiveLength += a.length / 3;
            }
            this.programConfigurations.populatePaintArrays(this.layoutVertexArray.length, t, r, i, s, n);
        }
    }
    Bi($c, "FillBucket", {
        omit: ["layers", "patternFeatures"]
    });
    const qc = new qs({
        "fill-sort-key": new js(qt.layout_fill["fill-sort-key"])
    });
    var Nc = {
        paint: new qs({
            "fill-antialias": new Rs(qt.paint_fill["fill-antialias"]),
            "fill-opacity": new js(qt.paint_fill["fill-opacity"]),
            "fill-color": new js(qt.paint_fill["fill-color"]),
            "fill-outline-color": new js(qt.paint_fill["fill-outline-color"]),
            "fill-translate": new Rs(qt.paint_fill["fill-translate"]),
            "fill-translate-anchor": new Rs(qt.paint_fill["fill-translate-anchor"]),
            "fill-pattern": new Us(qt.paint_fill["fill-pattern"]),
            "fill-minzoom": new js(qt.paint_fill["fill-minzoom"]),
            "fill-maxzoom": new js(qt.paint_fill["fill-maxzoom"])
        }),
        layout: qc
    };
    const Zc = Ys([{
        name: "a_pos_normal_ed",
        components: 4,
        type: "Int16"
    }])
      , Gc = Ys([{
        name: "a_centroid_pos",
        components: 2,
        type: "Uint16"
    }])
      , Xc = Ys([{
        name: "a_pos_3",
        components: 3,
        type: "Int16"
    }, {
        name: "a_pos_normal_3",
        components: 3,
        type: "Int16"
    }])
      , {members: Yc} = Zc;
    var Hc = Kc;
    function Kc(t, e, r, n, i) {
        this.properties = {},
        this.extent = r,
        this.type = 0,
        this._pbf = t,
        this._geometry = -1,
        this._keys = n,
        this._values = i,
        t.readFields(Jc, this, e);
    }
    function Jc(t, e, r) {
        1 == t ? e.id = r.readVarint() : 2 == t ? function(t, e) {
            for (var r = t.readVarint() + t.pos; t.pos < r; ) {
                var n = e._keys[t.readVarint()]
                  , i = e._values[t.readVarint()];
                e.properties[n] = i;
            }
        }(r, e) : 3 == t ? e.type = r.readVarint() : 4 == t && (e._geometry = r.pos);
    }
    function Wc(t) {
        for (var e, r, n = 0, i = 0, s = t.length, a = s - 1; i < s; a = i++)
            n += ((r = t[a]).x - (e = t[i]).x) * (e.y + r.y);
        return n
    }
    Kc.types = ["Unknown", "Point", "LineString", "Polygon"],
    Kc.prototype.loadGeometry = function() {
        var t = this._pbf;
        t.pos = this._geometry;
        for (var e, r = t.readVarint() + t.pos, n = 1, s = 0, a = 0, o = 0, l = []; t.pos < r; ) {
            if (s <= 0) {
                var u = t.readVarint();
                n = 7 & u,
                s = u >> 3;
            }
            if (s--,
            1 === n || 2 === n)
                a += t.readSVarint(),
                o += t.readSVarint(),
                1 === n && (e && l.push(e),
                e = []),
                e.push(new i(a,o));
            else {
                if (7 !== n)
                    throw new Error("unknown command " + n);
                e && e.push(e[0].clone());
            }
        }
        return e && l.push(e),
        l
    }
    ,
    Kc.prototype.bbox = function() {
        var t = this._pbf;
        t.pos = this._geometry;
        for (var e = t.readVarint() + t.pos, r = 1, n = 0, i = 0, s = 0, a = 1 / 0, o = -1 / 0, l = 1 / 0, u = -1 / 0; t.pos < e; ) {
            if (n <= 0) {
                var c = t.readVarint();
                r = 7 & c,
                n = c >> 3;
            }
            if (n--,
            1 === r || 2 === r)
                (i += t.readSVarint()) < a && (a = i),
                i > o && (o = i),
                (s += t.readSVarint()) < l && (l = s),
                s > u && (u = s);
            else if (7 !== r)
                throw new Error("unknown command " + r)
        }
        return [a, l, o, u]
    }
    ,
    Kc.prototype.toGeoJSON = function(t, e, r) {
        var n, i, s = this.extent * Math.pow(2, r), a = this.extent * t, o = this.extent * e, l = this.loadGeometry(), u = Kc.types[this.type];
        function c(t) {
            for (var e = 0; e < t.length; e++) {
                var r = t[e];
                t[e] = [360 * (r.x + a) / s - 180, 360 / Math.PI * Math.atan(Math.exp((180 - 360 * (r.y + o) / s) * Math.PI / 180)) - 90];
            }
        }
        switch (this.type) {
        case 1:
            var h = [];
            for (n = 0; n < l.length; n++)
                h[n] = l[n][0];
            c(l = h);
            break;
        case 2:
            for (n = 0; n < l.length; n++)
                c(l[n]);
            break;
        case 3:
            for (l = function(t) {
                var e = t.length;
                if (e <= 1)
                    return [t];
                for (var r, n, i = [], s = 0; s < e; s++) {
                    var a = Wc(t[s]);
                    0 !== a && (void 0 === n && (n = a < 0),
                    n === a < 0 ? (r && i.push(r),
                    r = [t[s]]) : r.push(t[s]));
                }
                return r && i.push(r),
                i
            }(l),
            n = 0; n < l.length; n++)
                for (i = 0; i < l[n].length; i++)
                    c(l[n][i]);
        }
        1 === l.length ? l = l[0] : u = "Multi" + u;
        var p = {
            type: "Feature",
            geometry: {
                type: u,
                coordinates: l
            },
            properties: this.properties
        };
        return "id"in this && (p.id = this.id),
        p
    }
    ;
    var Qc = th;
    function th(t, e) {
        this.version = 1,
        this.name = null,
        this.extent = 4096,
        this.length = 0,
        this._pbf = t,
        this._keys = [],
        this._values = [],
        this._features = [],
        t.readFields(eh, this, e),
        this.length = this._features.length;
    }
    function eh(t, e, r) {
        15 === t ? e.version = r.readVarint() : 1 === t ? e.name = r.readString() : 5 === t ? e.extent = r.readVarint() : 2 === t ? e._features.push(r.pos) : 3 === t ? e._keys.push(r.readString()) : 4 === t && e._values.push(function(t) {
            for (var e = null, r = t.readVarint() + t.pos; t.pos < r; ) {
                var n = t.readVarint() >> 3;
                e = 1 === n ? t.readString() : 2 === n ? t.readFloat() : 3 === n ? t.readDouble() : 4 === n ? t.readVarint64() : 5 === n ? t.readVarint() : 6 === n ? t.readSVarint() : 7 === n ? t.readBoolean() : null;
            }
            return e
        }(r));
    }
    function rh(t, e, r) {
        if (3 === t) {
            var n = new Qc(r,r.readVarint() + r.pos);
            n.length && (e[n.name] = n);
        }
    }
    th.prototype.feature = function(t) {
        if (t < 0 || t >= this._features.length)
            throw new Error("feature index out of bounds");
        this._pbf.pos = this._features[t];
        var e = this._pbf.readVarint() + this._pbf.pos;
        return new Hc(this._pbf,e,this.extent,this._keys,this._values)
    }
    ;
    var nh = {
        VectorTile: function(t, e) {
            this.layers = t.readFields(rh, {}, e);
        },
        VectorTileFeature: Hc,
        VectorTileLayer: Qc
    };
    function ih(t, e, r, n) {
        const s = []
          , a = 0 === n ? (t,e,r,n,s,a)=>{
            t.push(new i(a,r + (a - e) / (n - e) * (s - r)));
        }
        : (t,e,r,n,s,a)=>{
            t.push(new i(e + (a - r) / (s - r) * (n - e),a));
        }
        ;
        for (const i of t) {
            const t = [];
            for (const s of i) {
                if (s.length <= 2)
                    continue;
                const i = [];
                for (let t = 0; t < s.length - 1; t++) {
                    const o = s[t].x
                      , l = s[t].y
                      , u = s[t + 1].x
                      , c = s[t + 1].y
                      , h = 0 === n ? o : l
                      , p = 0 === n ? u : c;
                    h < e ? p > e && a(i, o, l, u, c, e) : h > r ? p < r && a(i, o, l, u, c, r) : i.push(s[t]),
                    p < e && h >= e && a(i, o, l, u, c, e),
                    p > r && h <= r && a(i, o, l, u, c, r);
                }
                let o = s[s.length - 1];
                const l = 0 === n ? o.x : o.y;
                l >= e && l <= r && i.push(o),
                i.length && (o = i[i.length - 1],
                i[0].x === o.x && i[0].y === o.y || i.push(i[0]),
                t.push(i));
            }
            t.length && s.push(t);
        }
        return s
    }
    const sh = nh.VectorTileFeature.types
      , ah = Math.pow(2, 13);
    function oh(t, e, r, n, i, s, a, o) {
        t.emplaceBack((e << 1) + a, (r << 1) + s, (Math.floor(n * ah) << 1) + i, Math.round(o));
    }
    function lh(t, e, r) {
        const n = 16384;
        t.emplaceBack(e.x, e.y, e.z, r[0] * n, r[1] * n, r[2] * n);
    }
    class uh {
        constructor() {
            this.acc = new i(0,0),
            this.polyCount = [];
        }
        startRing(t) {
            this.currentPolyCount = {
                edges: 0,
                top: 0
            },
            this.polyCount.push(this.currentPolyCount),
            this.min || (this.min = new i(t.x,t.y),
            this.max = new i(t.x,t.y));
        }
        append(t, e) {
            this.currentPolyCount.edges++,
            this.acc._add(t);
            const r = this.min
              , n = this.max;
            t.x < r.x ? r.x = t.x : t.x > n.x && (n.x = t.x),
            t.y < r.y ? r.y = t.y : t.y > n.y && (n.y = t.y),
            ((0 === t.x || t.x === bo) && t.x === e.x) != ((0 === t.y || t.y === bo) && t.y === e.y) && this.processBorderOverlap(t, e),
            e.x < 0 != t.x < 0 && this.addBorderIntersection(0, mr(e.y, t.y, (0 - e.x) / (t.x - e.x))),
            e.x > bo != t.x > bo && this.addBorderIntersection(1, mr(e.y, t.y, (bo - e.x) / (t.x - e.x))),
            e.y < 0 != t.y < 0 && this.addBorderIntersection(2, mr(e.x, t.x, (0 - e.y) / (t.y - e.y))),
            e.y > bo != t.y > bo && this.addBorderIntersection(3, mr(e.x, t.x, (bo - e.y) / (t.y - e.y)));
        }
        addBorderIntersection(t, e) {
            this.borders || (this.borders = [[Number.MAX_VALUE, -Number.MAX_VALUE], [Number.MAX_VALUE, -Number.MAX_VALUE], [Number.MAX_VALUE, -Number.MAX_VALUE], [Number.MAX_VALUE, -Number.MAX_VALUE]]);
            const r = this.borders[t];
            e < r[0] && (r[0] = e),
            e > r[1] && (r[1] = e);
        }
        processBorderOverlap(t, e) {
            if (t.x === e.x) {
                if (t.y === e.y)
                    return;
                const r = 0 === t.x ? 0 : 1;
                this.addBorderIntersection(r, e.y),
                this.addBorderIntersection(r, t.y);
            } else {
                const r = 0 === t.y ? 2 : 3;
                this.addBorderIntersection(r, e.x),
                this.addBorderIntersection(r, t.x);
            }
        }
        centroid() {
            const t = this.polyCount.reduce(((t,e)=>t + e.edges), 0);
            return 0 !== t ? this.acc.div(t)._round() : new i(0,0)
        }
        span() {
            return new i(this.max.x - this.min.x,this.max.y - this.min.y)
        }
        intersectsCount() {
            return this.borders.reduce(((t,e)=>t + +(e[0] !== Number.MAX_VALUE)), 0)
        }
    }
    class ch {
        constructor(t) {
            this.zoom = t.zoom,
            this.canonical = t.canonical,
            this.overscaling = t.overscaling,
            this.layers = t.layers,
            this.layerIds = this.layers.map((t=>t.id)),
            this.index = t.index,
            this.hasPattern = !1,
            this.edgeRadius = 0,
            this.projection = t.projection,
            this.layoutVertexArray = new Ws,
            this.centroidVertexArray = new Da,
            this.indexArray = new pa,
            this.programConfigurations = new lo(t.layers,t.zoom),
            this.segments = new vo,
            this.stateDependentLayerIds = this.layers.filter((t=>t.isStateDependent())).map((t=>t.id)),
            this.enableTerrain = t.enableTerrain;
        }
        populate(t, e, r, n) {
            this.features = [],
            this.hasPattern = Uc("fill-extrusion", this.layers, e),
            this.featuresOnBorder = [],
            this.borders = [[], [], [], []],
            this.borderDoneWithNeighborZ = [-1, -1, -1, -1],
            this.tileToMeter = function(t) {
                const e = Math.exp(Math.PI * (1 - t.y / (1 << t.z) * 2));
                return 80150034 * e / (e * e + 1) / bo / (1 << t.z)
            }(r),
            this.edgeRadius = this.layers[0].layout.get("fill-extrusion-edge-radius") / this.tileToMeter;
            for (const {feature: i, id: s, index: a, sourceLayerIndex: o} of t) {
                const t = this.layers[0]._featureFilter.needGeometry
                  , l = Al(i, t);
                if (!this.layers[0]._featureFilter.filter(new Ts(this.zoom), l, r))
                    continue;
                const u = {
                    id: s,
                    sourceLayerIndex: o,
                    index: a,
                    geometry: t ? l.geometry : wl(i, r, n),
                    properties: i.properties,
                    type: i.type,
                    patterns: {}
                }
                  , c = this.layoutVertexArray.length;
                this.hasPattern ? this.features.push(Oc("fill-extrusion", this.layers, u, this.zoom, e)) : this.addFeature(u, u.geometry, a, r, {}, e.availableImages, n),
                e.featureIndex.insert(i, u.geometry, a, o, this.index, c);
            }
            this.sortBorders();
        }
        addFeatures(t, e, r, n, i) {
            for (const t of this.features) {
                const {geometry: s} = t;
                this.addFeature(t, s, t.index, e, r, n, i);
            }
            this.sortBorders();
        }
        update(t, e, r, n) {
            this.stateDependentLayers.length && this.programConfigurations.updatePaintArrays(t, e, this.stateDependentLayers, r, n);
        }
        isEmpty() {
            return 0 === this.layoutVertexArray.length
        }
        uploadPending() {
            return !this.uploaded || this.programConfigurations.needsUpload
        }
        upload(t) {
            this.uploaded || (this.layoutVertexBuffer = t.createVertexBuffer(this.layoutVertexArray, Yc),
            this.indexBuffer = t.createIndexBuffer(this.indexArray),
            this.layoutVertexExtArray && (this.layoutVertexExtBuffer = t.createVertexBuffer(this.layoutVertexExtArray, Xc.members, !0))),
            this.programConfigurations.upload(t),
            this.uploaded = !0;
        }
        uploadCentroid(t) {
            0 !== this.centroidVertexArray.length && (this.centroidVertexBuffer ? this.needsCentroidUpdate && this.centroidVertexBuffer.updateData(this.centroidVertexArray) : this.centroidVertexBuffer = t.createVertexBuffer(this.centroidVertexArray, Gc.members, !0),
            this.needsCentroidUpdate = !1);
        }
        destroy() {
            this.layoutVertexBuffer && (this.layoutVertexBuffer.destroy(),
            this.centroidVertexBuffer && this.centroidVertexBuffer.destroy(),
            this.layoutVertexExtBuffer && this.layoutVertexExtBuffer.destroy(),
            this.indexBuffer.destroy(),
            this.programConfigurations.destroy(),
            this.segments.destroy());
        }
        addFeature(t, e, r, n, s, a, o) {
            const l = "Sg4326" == n.reference
              , u = [new i(0,0), new i(bo,bo)]
              , c = o.projection
              , h = "globe" === c.name
              , p = this.enableTerrain && !h ? new uh : null
              , f = "Polygon" === sh[t.type];
            h && !this.layoutVertexExtArray && (this.layoutVertexExtArray = new wa);
            const d = Rc(e, 500);
            for (let t = d.length - 1; t >= 0; t--) {
                const e = d[t];
                (0 === e.length || (y = e[0]).every((t=>t.x <= 0)) || y.every((t=>t.x >= bo)) || y.every((t=>t.y <= 0)) || y.every((t=>t.y >= bo))) && d.splice(t, 1);
            }
            var y;
            let m;
            if (h)
                m = xh(d, u, n);
            else {
                m = [];
                for (const t of d)
                    m.push({
                        polygon: t,
                        bounds: u
                    });
            }
            const g = f ? this.edgeRadius : 0;
            for (const {polygon: t, bounds: e} of m) {
                let r = 0
                  , i = 0;
                for (const e of t)
                    f && !e[0].equals(e[e.length - 1]) && e.push(e[0]),
                    i += f ? e.length - 1 : e.length;
                const s = this.segments.prepareSegment((f ? 5 : 4) * i, this.layoutVertexArray, this.indexArray);
                if (f) {
                    const e = []
                      , i = [];
                    r = s.vertexLength;
                    for (const r of t) {
                        let a, o;
                        r.length && r !== t[0] && i.push(e.length / 2),
                        a = r[1].sub(r[0])._perp()._unit();
                        for (let t = 1; t < r.length; t++) {
                            const i = r[t]
                              , l = r[t === r.length - 1 ? 1 : t + 1];
                            let {x: u, y: p} = i;
                            if (g) {
                                o = l.sub(i)._perp()._unit();
                                const t = a.add(o)._unit()
                                  , e = g * Math.min(4, 1 / (a.x * t.x + a.y * t.y));
                                u += e * t.x,
                                p += e * t.y,
                                a = o;
                            }
                            oh(this.layoutVertexArray, u, p, 0, 0, 1, 1, 0),
                            s.vertexLength++,
                            e.push(i.x, i.y),
                            h && lh(this.layoutVertexExtArray, c.projectTilePoint(u, p, n), c.upVector(n, u, p));
                        }
                    }
                    const a = sc(e, i);
                    for (let t = 0; t < a.length; t += 3)
                        this.indexArray.emplaceBack(r + a[t], r + a[t + 2], r + a[t + 1]),
                        s.primitiveLength++;
                }
                for (const i of t) {
                    p && i.length && p.startRing(i[0]);
                    let t, a, o, u = i.length > 4 && yh(i[i.length - 2], i[0], i[1]), d = g ? ph(i[i.length - 2], i[0], i[1], g) : 0;
                    a = i[1].sub(i[0])._perp()._unit();
                    for (let y = 1, m = 0; y < i.length; y++) {
                        let x = i[y - 1]
                          , v = i[y];
                        const b = i[y === i.length - 1 ? 1 : y + 1];
                        if (p && f && p.currentPolyCount.top++,
                        dh(v, x, e)) {
                            g && (a = b.sub(v)._perp()._unit());
                            continue
                        }
                        p && p.append(v, x);
                        let _ = v.sub(x)._perp();
                        l && (_ = _._mult(-1));
                        const w = _.x / (Math.abs(_.x) + Math.abs(_.y))
                          , A = _.y > 0 ? 1 : 0
                          , k = x.dist(v);
                        if (m + k > 32768 && (m = 0),
                        g) {
                            o = b.sub(v)._perp()._unit();
                            let t = fh(x, v, b, hh(a, o), g);
                            isNaN(t) && (t = 0);
                            const e = v.sub(x)._unit();
                            x = x.add(e.mult(d))._round(),
                            v = v.add(e.mult(-t))._round(),
                            d = t,
                            a = o;
                        }
                        const z = s.vertexLength
                          , S = i.length > 4 && yh(x, v, b);
                        let M = mh(m, u, !0);
                        if (oh(this.layoutVertexArray, x.x, x.y, w, A, 0, 0, M),
                        oh(this.layoutVertexArray, x.x, x.y, w, A, 0, 1, M),
                        m += k,
                        M = mh(m, S, !1),
                        u = S,
                        oh(this.layoutVertexArray, v.x, v.y, w, A, 0, 0, M),
                        oh(this.layoutVertexArray, v.x, v.y, w, A, 0, 1, M),
                        s.vertexLength += 4,
                        l ? (this.indexArray.emplaceBack(z + 0, z + 2, z + 1),
                        this.indexArray.emplaceBack(z + 1, z + 2, z + 3)) : (this.indexArray.emplaceBack(z + 0, z + 1, z + 2),
                        this.indexArray.emplaceBack(z + 1, z + 3, z + 2)),
                        s.primitiveLength += 2,
                        g) {
                            const n = r + (1 === y ? i.length - 2 : y - 2)
                              , a = 1 === y ? r : n + 1;
                            if (this.indexArray.emplaceBack(z + 1, n, z + 3),
                            this.indexArray.emplaceBack(n, a, z + 3),
                            s.primitiveLength += 2,
                            void 0 === t && (t = z),
                            !dh(b, i[y], e)) {
                                const e = y === i.length - 1 ? t : s.vertexLength;
                                this.indexArray.emplaceBack(z + 2, z + 3, e),
                                this.indexArray.emplaceBack(z + 3, e + 1, e),
                                this.indexArray.emplaceBack(z + 3, a, e + 1),
                                s.primitiveLength += 3;
                            }
                        }
                        if (h) {
                            const t = this.layoutVertexExtArray
                              , e = c.projectTilePoint(x.x, x.y, n)
                              , r = c.projectTilePoint(v.x, v.y, n)
                              , i = c.upVector(n, x.x, x.y)
                              , s = c.upVector(n, v.x, v.y);
                            lh(t, e, i),
                            lh(t, e, i),
                            lh(t, r, s),
                            lh(t, r, s);
                        }
                    }
                    f && (r += i.length - 1);
                }
            }
            if (p && p.polyCount.length > 0) {
                if (p.borders) {
                    p.vertexArrayOffset = this.centroidVertexArray.length;
                    const t = p.borders
                      , e = this.featuresOnBorder.push(p) - 1;
                    for (let r = 0; r < 4; r++)
                        t[r][0] !== Number.MAX_VALUE && this.borders[r].push(e);
                }
                this.encodeCentroid(p.borders ? void 0 : p.centroid(), p);
            }
            this.programConfigurations.populatePaintArrays(this.layoutVertexArray.length, t, r, s, a, n);
        }
        sortBorders() {
            for (let t = 0; t < 4; t++)
                this.borders[t].sort(((e,r)=>this.featuresOnBorder[e].borders[t][0] - this.featuresOnBorder[r].borders[t][0]));
        }
        encodeCentroid(t, e, r=!0) {
            let n, i;
            if (t)
                if (0 !== t.y) {
                    const r = e.span()._mult(this.tileToMeter);
                    n = (Math.max(t.x, 1) << 3) + Math.min(7, Math.round(r.x / 10)),
                    i = (Math.max(t.y, 1) << 3) + Math.min(7, Math.round(r.y / 10));
                } else
                    n = Math.ceil(7 * (t.x + 450)),
                    i = 0;
            else
                n = 0,
                i = +r;
            let s = r ? this.centroidVertexArray.length : e.vertexArrayOffset;
            for (const t of e.polyCount) {
                r && this.centroidVertexArray.resize(this.centroidVertexArray.length + 4 * t.edges + t.top);
                for (let e = 0; e < t.top; e++)
                    this.centroidVertexArray.emplace(s++, n, i);
                for (let e = 0; e < 2 * t.edges; e++)
                    this.centroidVertexArray.emplace(s++, 0, i),
                    this.centroidVertexArray.emplace(s++, n, i);
            }
        }
    }
    function hh(t, e) {
        const r = t.add(e)._unit();
        return t.x * r.x + t.y * r.y
    }
    function ph(t, e, r, n) {
        const i = e.sub(t)._perp()._unit()
          , s = r.sub(e)._perp()._unit();
        return fh(t, e, r, hh(i, s), n)
    }
    function fh(t, e, r, n, i) {
        const s = Math.sqrt(1 - n * n);
        return Math.min(t.dist(e) / 3, e.dist(r) / 3, i * s / n)
    }
    function dh(t, e, r) {
        return t.x < r[0].x && e.x < r[0].x || t.x > r[1].x && e.x > r[1].x || t.y < r[0].y && e.y < r[0].y || t.y > r[1].y && e.y > r[1].y
    }
    function yh(t, e, r) {
        if (t.x < 0 || t.x >= bo || e.x < 0 || e.x >= bo || r.x < 0 || r.x >= bo)
            return !1;
        const n = r.sub(e)
          , i = n.perp()
          , s = t.sub(e);
        return (n.x * s.x + n.y * s.y) / Math.sqrt((n.x * n.x + n.y * n.y) * (s.x * s.x + s.y * s.y)) > -.866 && i.x * s.x + i.y * s.y < 0
    }
    function mh(t, e, r) {
        const n = e ? 2 | t : -3 & t;
        return r ? 1 | n : -2 & n
    }
    function gh() {
        const t = Math.PI / 32
          , e = Math.tan(t)
          , r = wo;
        return r * Math.sqrt(1 + 2 * e * e) - r
    }
    function xh(t, e, r) {
        const n = 1 << r.z
          , s = Wo(r.x / n)
          , a = Wo((r.x + 1) / n)
          , o = xl(r)
          , l = Qo(o.top / n)
          , u = Qo(o.bottom / n);
        return function(t, e, r, n, s=0, a) {
            const o = [];
            if (!t.length || !r || !n)
                return o;
            const l = (t,e)=>{
                for (const r of t)
                    o.push({
                        polygon: r,
                        bounds: e
                    });
            }
              , u = Math.ceil(Math.log2(r))
              , c = Math.ceil(Math.log2(n))
              , h = u - c
              , p = [];
            for (let t = 0; t < Math.abs(h); t++)
                p.push(h > 0 ? 0 : 1);
            for (let t = 0; t < Math.min(u, c); t++)
                p.push(0),
                p.push(1);
            let f = t;
            if (f = ih(f, e[0].y - s, e[1].y + s, 1),
            f = ih(f, e[0].x - s, e[1].x + s, 0),
            !f.length)
                return o;
            const d = [];
            for (p.length ? d.push({
                polygons: f,
                bounds: e,
                depth: 0
            }) : l(f, e); d.length; ) {
                const t = d.pop()
                  , e = t.depth
                  , r = p[e]
                  , n = t.bounds[0]
                  , o = t.bounds[1]
                  , u = 0 === r ? n.x : n.y
                  , c = 0 === r ? o.x : o.y
                  , h = a ? a(r, u, c) : .5 * (u + c)
                  , f = ih(t.polygons, u - s, h + s, r)
                  , y = ih(t.polygons, h - s, c + s, r);
                if (f.length) {
                    const t = [n, new i(0 === r ? h : o.x,1 === r ? h : o.y)];
                    p.length > e + 1 ? d.push({
                        polygons: f,
                        bounds: t,
                        depth: e + 1
                    }) : l(f, t);
                }
                if (y.length) {
                    const t = [new i(0 === r ? h : n.x,1 === r ? h : n.y), o];
                    p.length > e + 1 ? d.push({
                        polygons: y,
                        bounds: t,
                        depth: e + 1
                    }) : l(y, t);
                }
            }
            return o
        }(t, e, Math.ceil((a - s) / 11.25), Math.ceil((l - u) / 11.25), 1, ((t,e,i)=>{
            if (0 === t)
                return .5 * (e + i);
            {
                const t = Qo(gl(e, r) / n);
                return (Ko(.5 * (Qo(gl(i, r) / n) + t)) * n - r.y) * bo
            }
        }
        ))
    }
    Bi(ch, "FillExtrusionBucket", {
        omit: ["layers", "features"]
    }),
    Bi(uh, "PartMetadata");
    const vh = new qs({
        "fill-extrusion-edge-radius": new Rs(qt["layout_fill-extrusion"]["fill-extrusion-edge-radius"])
    });
    var bh = {
        paint: new qs({
            "fill-extrusion-opacity": new Rs(qt["paint_fill-extrusion"]["fill-extrusion-opacity"]),
            "fill-extrusion-color": new js(qt["paint_fill-extrusion"]["fill-extrusion-color"]),
            "fill-extrusion-translate": new Rs(qt["paint_fill-extrusion"]["fill-extrusion-translate"]),
            "fill-extrusion-translate-anchor": new Rs(qt["paint_fill-extrusion"]["fill-extrusion-translate-anchor"]),
            "fill-extrusion-pattern": new Us(qt["paint_fill-extrusion"]["fill-extrusion-pattern"]),
            "fill-extrusion-height": new js(qt["paint_fill-extrusion"]["fill-extrusion-height"]),
            "fill-extrusion-base": new js(qt["paint_fill-extrusion"]["fill-extrusion-base"]),
            "fill-extrusion-vertical-gradient": new Rs(qt["paint_fill-extrusion"]["fill-extrusion-vertical-gradient"]),
            "fill-extrusion-ambient-occlusion-intensity": new Rs(qt["paint_fill-extrusion"]["fill-extrusion-ambient-occlusion-intensity"]),
            "fill-extrusion-ambient-occlusion-radius": new Rs(qt["paint_fill-extrusion"]["fill-extrusion-ambient-occlusion-radius"]),
            "fill-extrusion-minzoom": new js(qt["paint_fill-extrusion"]["fill-extrusion-minzoom"]),
            "fill-extrusion-maxzoom": new js(qt["paint_fill-extrusion"]["fill-extrusion-maxzoom"]),
            "fill-extrusion-topcolor": new js(qt["paint_fill-extrusion"]["fill-extrusion-topcolor"])
        }),
        layout: vh
    };
    function _h(t, e, r) {
        var n = 2 * Math.PI * 6378137 / 256 / Math.pow(2, r);
        return [t * n - 2 * Math.PI * 6378137 / 2, e * n - 2 * Math.PI * 6378137 / 2]
    }
    class wh {
        constructor(t, e, r, n) {
            this.z = t,
            this.x = e,
            this.y = r,
            this.reference = n && n.reference,
            this.sourceID = n && n.sourceID,
            this._tileY = n && null != n._tileY && null != n._tileY ? n._tileY : r,
            this._tileH = n && null != n._tileH && null != n._tileH ? n._tileH : 1,
            this.key = zh(0, t, t, e, r, this.sourceID);
        }
        equals(t) {
            var e = this.sourceID;
            return e ? this.z === t.z && this.x === t.x && this.y === t.y && e === t.sourceID : this.z === t.z && this.x === t.x && this.y === t.y
        }
        url(t, e) {
            const r = function(t, e, r) {
                var n = _h(256 * t, 256 * (e = Math.pow(2, r) - e - 1), r)
                  , i = _h(256 * (t + 1), 256 * (e + 1), r);
                return n[0] + "," + n[1] + "," + i[0] + "," + i[1]
            }(this.x, this.y, this.z)
              , n = function(t, e, r) {
                let n, i = "";
                for (let s = t; s > 0; s--)
                    n = 1 << s - 1,
                    i += (e & n ? 1 : 0) + (r & n ? 2 : 0);
                return i
            }(this.z, this.x, this.y);
            return t[(this.x + this.y) % t.length].replace("{prefix}", (this.x % 16).toString(16) + (this.y % 16).toString(16)).replace(/{z}/g, String(this.z)).replace(/{x}/g, String(this.x)).replace(/{y}/g, String("tms" === e ? Math.pow(2, this.z) - this.y - 1 : this.y)).replace("{quadkey}", n).replace("{bbox-epsg-3857}", r)
        }
        toString() {
            return `${this.z}/${this.x}/${this.y}`
        }
    }
    class Ah {
        constructor(t, e) {
            this.wrap = t,
            this.canonical = e,
            this.key = zh(t, e.z, e.z, e.x, e.y, e.sourceID);
        }
    }
    class kh {
        constructor(t, e, r, n, i, s) {
            if (this.reference = s && s.reference,
            this.sourceID = s && s.sourceID,
            this.zoomRule = s && s.zoomRule,
            this._tileY = s && s._tileY,
            this._tileH = s && s._tileH,
            this._mapZoom = s && s._mapZoom,
            !this._tileY && 0 != this._tileY || !this._tileH && 0 != this._tileH) {
                let t = function(t, e, r, n) {
                    let i = r
                      , s = 1;
                    if ("Sg4326" == t) {
                        let t = ml(e, r, n, "all");
                        i = t.top,
                        s = t.height;
                    }
                    return {
                        _tileY: i,
                        _tileH: s
                    }
                }(this.reference, n, i, r);
                this._tileY = t._tileY,
                this._tileH = t._tileH;
            }
            this.overscaledZ = t,
            this.wrap = e,
            this.canonical = new wh(r,+n,+i,this),
            this.key = 0 === e && t === r ? this.canonical.key : zh(e, t, r, n, i, this.sourceID);
        }
        equals(t) {
            return this.overscaledZ === t.overscaledZ && this.wrap === t.wrap && this.canonical.equals(t.canonical)
        }
        scaledTo(t, e) {
            e || (e = 0),
            t += e;
            var r = this.zoomRule;
            if (r && r.length > 0) {
                r = JSON.parse(r);
                var n = 0;
                for (var i in r) {
                    if (0 == n && i.indexOf(t) >= 0) {
                        n = 1;
                        break
                    }
                    if (1 == n) {
                        t = r[i] || 0,
                        n = 2;
                        break
                    }
                }
            }
            const s = this.canonical.z - t;
            if (t > this.canonical.z)
                return new kh(t,this.wrap,this.canonical.z,this.canonical.x,this.canonical.y,this);
            {
                const {reference: e, sourceID: r, zoomRule: n, _mapZoom: i} = this;
                return new kh(t,this.wrap,t,this.canonical.x >> s,this.canonical.y >> s,{
                    reference: e,
                    sourceID: r,
                    zoomRule: n,
                    _mapZoom: i
                })
            }
        }
        calculateScaledKey(t, e=!0) {
            if (this.overscaledZ === t && e)
                return this.key;
            if (t > this.canonical.z)
                return zh(this.wrap * +e, t, this.canonical.z, this.canonical.x, this.canonical.y, this.sourceID);
            {
                const r = this.canonical.z - t;
                return zh(this.wrap * +e, t, t, this.canonical.x >> r, this.canonical.y >> r, this.sourceID)
            }
        }
        isChildOf(t) {
            if (t.wrap !== this.wrap)
                return !1;
            const e = this.canonical.z - t.canonical.z;
            return 0 === t.overscaledZ || t.overscaledZ < this.overscaledZ && t.canonical.x === this.canonical.x >> e && t.canonical.y === this.canonical.y >> e
        }
        children(t) {
            if (this.overscaledZ >= t)
                return [new kh(this.overscaledZ + 1,this.wrap,this.canonical.z,this.canonical.x,this.canonical.y,this)];
            const e = this.canonical.z + 1
              , r = 2 * this.canonical.x
              , n = 2 * this.canonical.y
              , {reference: i, sourceID: s, zoomRule: a, _mapZoom: o} = this
              , l = {
                reference: i,
                sourceID: s,
                zoomRule: a,
                _mapZoom: o
            };
            return [new kh(e,this.wrap,e,r,n,this), new kh(e,this.wrap,e,r + 1,n,l), new kh(e,this.wrap,e,r,n + 1,l), new kh(e,this.wrap,e,r + 1,n + 1,l)]
        }
        isLessThan(t) {
            return this.wrap < t.wrap || !(this.wrap > t.wrap) && (this.overscaledZ < t.overscaledZ || !(this.overscaledZ > t.overscaledZ) && (this.canonical.x < t.canonical.x || !(this.canonical.x > t.canonical.x) && this.canonical.y < t.canonical.y))
        }
        wrapped() {
            return new kh(this.overscaledZ,0,this.canonical.z,this.canonical.x,this.canonical.y,this)
        }
        unwrapTo(t) {
            return new kh(this.overscaledZ,t,this.canonical.z,this.canonical.x,this.canonical.y,this)
        }
        overscaleFactor() {
            return Math.pow(2, this.overscaledZ - this.canonical.z)
        }
        toUnwrapped() {
            return new Ah(this.wrap,this.canonical)
        }
        toString() {
            return `${this.overscaledZ}/${this.canonical.x}/${this.canonical.y}`
        }
    }
    function zh(t, e, r, n, i, s) {
        let a = [t, e, r, n, i].join("_");
        return s && (a += s.toString(36)),
        a
    }
    function Sh(t, e) {
        return t.x * e.x + t.y * e.y
    }
    function Mh(t, e) {
        if (1 === t.length) {
            let r = 0;
            const n = e[r++];
            let i;
            for (; !i || n.equals(i); )
                if (i = e[r++],
                !i)
                    return 1 / 0;
            for (; r < e.length; r++) {
                const s = e[r]
                  , a = t[0]
                  , o = i.sub(n)
                  , l = s.sub(n)
                  , u = a.sub(n)
                  , c = Sh(o, o)
                  , h = Sh(o, l)
                  , p = Sh(l, l)
                  , f = Sh(u, o)
                  , d = Sh(u, l)
                  , y = c * p - h * h
                  , m = (p * f - h * d) / y
                  , g = (c * d - h * f) / y
                  , x = n.z * (1 - m - g) + i.z * m + s.z * g;
                if (isFinite(x))
                    return x
            }
            return 1 / 0
        }
        {
            let t = 1 / 0;
            for (const r of e)
                t = Math.min(t, r.z);
            return t
        }
    }
    function Ih(t) {
        const e = new i(t[0],t[1]);
        return e.z = t[2],
        e
    }
    function Th(t, e, r, n, i, s, a, o) {
        const l = a * i.getElevationAt(t, e, !0, !0)
          , u = 0 !== s[0]
          , c = u ? 0 === s[1] ? a * (s[0] / 7 - 450) : a * function(t, e, r) {
            const n = Math.floor(e[0] / 8)
              , i = Math.floor(e[1] / 8)
              , s = 10 * (e[0] - 8 * n)
              , a = 10 * (e[1] - 8 * i)
              , o = t.getElevationAt(n, i, !0, !0)
              , l = t.getMeterToDEM(r)
              , u = Math.floor(.5 * (s * l - 1))
              , c = Math.floor(.5 * (a * l - 1))
              , h = t.tileCoordToPixel(n, i)
              , p = 2 * u + 1
              , f = 2 * c + 1
              , d = function(t, e, r, n, i) {
                return [t.getElevationAtPixel(e, r, !0), t.getElevationAtPixel(e + i, r, !0), t.getElevationAtPixel(e, r + i, !0), t.getElevationAtPixel(e + n, r + i, !0)]
            }(t, h.x - u, h.y - c, p, f)
              , y = Math.abs(d[0] - d[1])
              , m = Math.abs(d[2] - d[3])
              , g = Math.abs(d[0] - d[2]) + Math.abs(d[1] - d[3])
              , x = Math.min(.25, .5 * l * (y + m) / p)
              , v = Math.min(.25, .5 * l * g / f);
            return o + Math.max(x * s, v * a)
        }(i, s, o) : l;
        return {
            base: l + (0 === r) ? -1 : r,
            top: u ? Math.max(c + n, l + r + 2) : l + n
        }
    }
    Bi(wh, "CanonicalTileID"),
    Bi(kh, "OverscaledTileID", {
        omit: ["projMatrix"]
    });
    const Bh = Ys([{
        name: "a_pos_normal",
        components: 2,
        type: "Int16"
    }, {
        name: "a_data",
        components: 4,
        type: "Uint8"
    }, {
        name: "a_linesofar",
        components: 1,
        type: "Float32"
    }], 4)
      , {members: Ch} = Bh
      , Vh = Ys([{
        name: "a_packed",
        components: 4,
        type: "Float32"
    }])
      , {members: Ph} = Vh
      , Dh = nh.VectorTileFeature.types
      , Eh = Math.cos(Math.PI / 180 * 37.5);
    class Fh {
        constructor(t) {
            this.zoom = t.zoom,
            this.overscaling = t.overscaling,
            this.layers = t.layers,
            this.layerIds = this.layers.map((t=>t.id)),
            this.index = t.index,
            this.projection = t.projection,
            this.hasPattern = !1,
            this.patternFeatures = [],
            this.lineClipsArray = [],
            this.gradients = {},
            this.layers.forEach((t=>{
                this.gradients[t.id] = {};
            }
            )),
            this.layoutVertexArray = new Qs,
            this.layoutVertexArray2 = new ta,
            this.indexArray = new pa,
            this.programConfigurations = new lo(t.layers,t.zoom,(t=>t.indexOf("line-outline") < 0));
            var e = ["line-color", "line-floorwidth", "line-width", "line-dasharray", "line-pattern"];
            this.programConfigurations_outline = new lo(t.layers,t.zoom,(t=>e.indexOf(t) < 0)),
            this.segments = new vo,
            this.maxLineLength = 0,
            this.stateDependentLayerIds = this.layers.filter((t=>t.isStateDependent())).map((t=>t.id));
        }
        populate(t, e, r, n) {
            this.hasPattern = Uc("line", this.layers, e);
            const i = this.layers[0].layout.get("line-sort-key")
              , s = [];
            for (const {feature: e, id: a, index: o, sourceLayerIndex: l, order: u} of t) {
                const t = this.layers[0]._featureFilter.needGeometry
                  , c = Al(e, t);
                if (!this.layers[0]._featureFilter.filter(new Ts(this.zoom), c, r))
                    continue;
                const h = i ? i.evaluate(c, {}, r) : void 0
                  , p = {
                    id: a,
                    properties: e.properties,
                    type: e.type,
                    sourceLayerIndex: l,
                    index: o,
                    geometry: t ? c.geometry : wl(e, r, n),
                    patterns: {},
                    sortKey: h,
                    order: u
                };
                s.push(p);
            }
            i && s.sort(((t,e)=>t.sortKey - e.sortKey));
            const {lineAtlas: a, featureIndex: o} = e
              , l = this.addConstantDashes(a);
            for (const n of s) {
                const {geometry: i, index: s, sourceLayerIndex: u, order: c} = n;
                if (l && this.addFeatureDashes(n, a),
                this.hasPattern) {
                    const t = Oc("line", this.layers, n, this.zoom, e);
                    this.patternFeatures.push(t);
                } else
                    this.addFeature(n, i, s, r, a.positions, e.availableImages);
                o.insert(t[c].feature, i, s, u, this.index);
            }
        }
        addConstantDashes(t) {
            let e = !1;
            for (const r of this.layers) {
                const n = r.paint.get("line-dasharray").value
                  , i = r.paint.get("line-outline-dasharray").value
                  , s = r.layout.get("line-cap").value;
                if ("constant" !== n.kind || "constant" !== i.kind || "constant" !== s.kind)
                    e = !0;
                else {
                    const e = s.value
                      , r = n.value;
                    r && (t.addDash(r.from, e),
                    t.addDash(r.to, e),
                    r.other && t.addDash(r.other, e));
                    const a = i.value;
                    a && (t.addDash(a.from, e),
                    t.addDash(a.to, e),
                    a.other && t.addDash(a.other, e));
                }
            }
            return e
        }
        addFeatureDashes(t, e) {
            const r = this.zoom;
            function n(t, e, r, n, i) {
                const s = r.paint.get(i).value
                  , a = r.layout.get("line-cap").value;
                if ("constant" === s.kind && "constant" === a.kind)
                    return null;
                let o, l, u, c, h, p;
                if ("constant" === s.kind) {
                    const t = s.value;
                    if (!t)
                        return null;
                    o = t.other || t.to,
                    l = t.to,
                    u = t.from;
                } else
                    o = s.evaluate({
                        zoom: e - 1
                    }, n),
                    l = s.evaluate({
                        zoom: e
                    }, n),
                    u = s.evaluate({
                        zoom: e + 1
                    }, n);
                return "constant" === a.kind ? c = h = p = a.value : (c = a.evaluate({
                    zoom: e - 1
                }, n),
                h = a.evaluate({
                    zoom: e
                }, n),
                p = a.evaluate({
                    zoom: e + 1
                }, n)),
                t.addDash(o, c),
                t.addDash(l, h),
                t.addDash(u, p),
                {
                    min: t.getKey(o, c),
                    mid: t.getKey(l, h),
                    max: t.getKey(u, p)
                }
            }
            for (const a of this.layers) {
                var i = n(e, r, a, t, "line-dasharray")
                  , s = n(e, r, a, t, "line-outline-dasharray");
                t.patterns[a.id] = {},
                null != i && (t.patterns[a.id].min = i.min,
                t.patterns[a.id].mid = i.mid,
                t.patterns[a.id].max = i.max),
                null != s && (t.patterns[a.id].min_out = s.min,
                t.patterns[a.id].mid_out = s.mid,
                t.patterns[a.id].max_out = s.max);
            }
        }
        update(t, e, r, n) {
            this.stateDependentLayers.length && (this.programConfigurations.updatePaintArrays(t, e, this.stateDependentLayers, r, n),
            this.programConfigurations_outline.updatePaintArrays(t, e, this.stateDependentLayers, r, n));
        }
        addFeatures(t, e, r, n, i) {
            for (const t of this.patternFeatures)
                this.addFeature(t, t.geometry, t.index, e, r, n);
        }
        isEmpty() {
            return 0 === this.layoutVertexArray.length
        }
        uploadPending() {
            return !this.uploaded || this.programConfigurations_outline.needsUpload || this.programConfigurations.needsUpload
        }
        upload(t) {
            this.uploaded || (0 !== this.layoutVertexArray2.length && (this.layoutVertexBuffer2 = t.createVertexBuffer(this.layoutVertexArray2, Ph)),
            this.layoutVertexBuffer = t.createVertexBuffer(this.layoutVertexArray, Ch),
            this.indexBuffer = t.createIndexBuffer(this.indexArray)),
            this.programConfigurations.upload(t),
            this.programConfigurations_outline.upload(t),
            this.uploaded = !0;
        }
        destroy() {
            this.layoutVertexBuffer && (this.layoutVertexBuffer.destroy(),
            this.indexBuffer.destroy(),
            this.programConfigurations.destroy(),
            this.programConfigurations_outline.destroy(),
            this.segments.destroy());
        }
        lineFeatureClips(t) {
            if (t.properties && t.properties.hasOwnProperty("sgmap_clip_start") && t.properties.hasOwnProperty("sgmap_clip_end"))
                return {
                    start: +t.properties.sgmap_clip_start,
                    end: +t.properties.sgmap_clip_end
                }
        }
        addFeature(t, e, r, n, i, s) {
            const a = this.layers[0].layout
              , o = a.get("line-join").evaluate(t, {})
              , l = a.get("line-cap").evaluate(t, {})
              , u = a.get("line-miter-limit")
              , c = a.get("line-round-limit");
            this.lineClips = this.lineFeatureClips(t);
            var h = this.layers[0].paint.get("line-offset").evaluate(t, {});
            for (const r of e)
                this.addLine(r, t, o, l, u, c, h);
            this.programConfigurations.populatePaintArrays(this.layoutVertexArray.length, t, r, i, s, n),
            this.programConfigurations_outline.populatePaintArrays(this.layoutVertexArray.length, t, r, i, s, n);
        }
        addLine(t, e, r, n, i, s, a) {
            if (this.distance = 0,
            this.scaledDistance = 0,
            this.totalDistance = 0,
            this.lineSoFar = 0,
            this.lineClips) {
                this.lineClipsArray.push(this.lineClips);
                for (let e = 0; e < t.length - 1; e++)
                    this.totalDistance += t[e].dist(t[e + 1]);
                this.updateScaledDistance(),
                this.maxLineLength = Math.max(this.maxLineLength, this.totalDistance);
            }
            const o = "Polygon" === Dh[e.type];
            let l = t.length;
            for (; l >= 2 && t[l - 1].equals(t[l - 2]); )
                l--;
            let u = 0;
            for (; u < l - 1 && t[u].equals(t[u + 1]); )
                u++;
            if (l < (o ? 3 : 2))
                return;
            "bevel" === r && (i = 1.05);
            const c = this.overscaling <= 16 ? 122880 / (512 * this.overscaling) : 0
              , h = this.segments.prepareSegment(10 * l, this.layoutVertexArray, this.indexArray);
            let p, f, d, y, m;
            this.e1 = this.e2 = -1,
            o && (p = t[l - 2],
            m = t[u].sub(p)._unit()._perp());
            for (let e = u; e < l; e++) {
                if (d = e === l - 1 ? o ? t[u + 1] : void 0 : t[e + 1],
                d && t[e].equals(d))
                    continue;
                m && (y = m),
                p && (f = p),
                p = t[e],
                m = d ? d.sub(p)._unit()._perp() : y,
                y = y || m;
                let g = y.add(m);
                0 === g.x && 0 === g.y || g._unit();
                const x = y.x * m.x + y.y * m.y
                  , v = g.x * m.x + g.y * m.y
                  , b = 0 !== v ? 1 / v : 1 / 0
                  , _ = 2 * Math.sqrt(2 - 2 * v)
                  , w = v < Eh && f && d
                  , A = y.x * m.y - y.y * m.x > 0;
                if (w && e > u) {
                    const t = p.dist(f);
                    if (t > 2 * c) {
                        const e = p.sub(p.sub(f)._mult(c / t)._round());
                        this.updateDistance(f, e),
                        this.addCurrentVertex(e, y, 0, 0, h),
                        f = e;
                    }
                }
                const k = f && d;
                let z = k ? r : o ? "butt" : n;
                if (k && "round" === z && (b < s ? z = "miter" : b <= 2 && (z = "fakeround")),
                "miter" === z && b > i && (z = "bevel"),
                "bevel" === z && (b > 2 && (z = "flipbevel"),
                b < i && (z = "miter")),
                f && this.updateDistance(f, p),
                "miter" === z)
                    g._mult(b),
                    this.addCurrentVertex(p, g, 0, 0, h);
                else if ("flipbevel" === z) {
                    if (b > 100)
                        g = m.mult(-1);
                    else if (a)
                        g = y.add(m)._mult(b),
                        this.addCurrentVertex(p, g, 0, 0, h);
                    else {
                        const t = b * y.add(m).mag() / y.sub(m).mag();
                        g._perp()._mult(t * (A ? -1 : 1));
                    }
                    this.addCurrentVertex(p, g, 0, 0, h),
                    this.addCurrentVertex(p, g.mult(-1), 0, 0, h);
                } else if ("bevel" === z || "fakeround" === z) {
                    const t = -Math.sqrt(b * b - 1)
                      , e = A ? t : 0
                      , r = A ? 0 : t;
                    if (f && this.addCurrentVertex(p, y, e, r, h),
                    "fakeround" === z) {
                        const t = Math.round(180 * _ / Math.PI / 20);
                        for (let e = 1; e < t; e++) {
                            let r = e / t;
                            if (.5 !== r) {
                                const t = r - .5;
                                r += r * t * (r - 1) * ((1.0904 + x * (x * (3.55645 - 1.43519 * x) - 3.2452)) * t * t + (.848013 + x * (.215638 * x - 1.06021)));
                            }
                            const n = m.sub(y)._mult(r)._add(y)._unit()._mult(A ? -1 : 1);
                            this.addHalfVertex(p, n.x, n.y, !1, A, 0, h);
                        }
                    }
                    d && this.addCurrentVertex(p, m, -e, -r, h);
                } else if ("butt" === z)
                    this.addCurrentVertex(p, g, 0, 0, h);
                else if ("square" === z) {
                    const t = f ? 1 : -1;
                    f || this.addCurrentVertex(p, g, t, t, h),
                    this.addCurrentVertex(p, g, 0, 0, h),
                    f && this.addCurrentVertex(p, g, t, t, h);
                } else
                    "round" === z && (f && (this.addCurrentVertex(p, y, 0, 0, h),
                    this.addCurrentVertex(p, y, 1, 1, h, !0)),
                    d && (this.addCurrentVertex(p, m, -1, -1, h, !0),
                    this.addCurrentVertex(p, m, 0, 0, h)));
                if (w && e < l - 1) {
                    const t = p.dist(d);
                    if (t > 2 * c) {
                        const e = p.add(d.sub(p)._mult(c / t)._round());
                        this.updateDistance(p, e),
                        this.addCurrentVertex(e, m, 0, 0, h),
                        p = e;
                    }
                }
            }
        }
        addCurrentVertex(t, e, r, n, i, s=!1) {
            const a = e.y * n - e.x
              , o = -e.y - e.x * n;
            this.addHalfVertex(t, e.x + e.y * r, e.y - e.x * r, s, !1, r, i),
            this.addHalfVertex(t, a, o, s, !0, -n, i);
        }
        addHalfVertex({x: t, y: e}, r, n, i, s, a, o) {
            this.layoutVertexArray.emplaceBack((t << 1) + (i ? 1 : 0), (e << 1) + (s ? 1 : 0), Math.round(63 * r) + 128, Math.round(63 * n) + 128, 1 + (0 === a ? 0 : a < 0 ? -1 : 1), 0, this.lineSoFar),
            this.lineClips && this.layoutVertexArray2.emplaceBack(this.scaledDistance, this.lineClipsArray.length, this.lineClips.start, this.lineClips.end);
            const l = o.vertexLength++;
            this.e1 >= 0 && this.e2 >= 0 && (this.indexArray.emplaceBack(this.e1, this.e2, l),
            o.primitiveLength++),
            s ? this.e2 = l : this.e1 = l;
        }
        updateScaledDistance() {
            if (this.lineClips) {
                const t = this.totalDistance / (this.lineClips.end - this.lineClips.start);
                this.scaledDistance = this.distance / this.totalDistance,
                this.lineSoFar = t * this.lineClips.start + this.distance;
            } else
                this.lineSoFar = this.distance;
        }
        updateDistance(t, e) {
            this.distance += t.dist(e),
            this.updateScaledDistance();
        }
    }
    Bi(Fh, "LineBucket", {
        omit: ["layers", "patternFeatures"]
    });
    const Lh = new qs({
        "line-cap": new js(qt.layout_line["line-cap"]),
        "line-join": new js(qt.layout_line["line-join"]),
        "line-miter-limit": new Rs(qt.layout_line["line-miter-limit"]),
        "line-round-limit": new Rs(qt.layout_line["line-round-limit"]),
        "line-sort-key": new js(qt.layout_line["line-sort-key"]),
        "esymbol-id": new js(qt.layout_line["esymbol-id"])
    });
    var Rh = {
        paint: new qs({
            "line-opacity": new js(qt.paint_line["line-opacity"]),
            "line-color": new js(qt.paint_line["line-color"]),
            "line-translate": new Rs(qt.paint_line["line-translate"]),
            "line-translate-anchor": new Rs(qt.paint_line["line-translate-anchor"]),
            "line-width": new js(qt.paint_line["line-width"]),
            "line-gap-width": new js(qt.paint_line["line-gap-width"]),
            "line-offset": new js(qt.paint_line["line-offset"]),
            "line-blur": new js(qt.paint_line["line-blur"]),
            "line-dasharray": new Us(qt.paint_line["line-dasharray"]),
            "line-pattern": new Us(qt.paint_line["line-pattern"]),
            "line-gradient": new $s(qt.paint_line["line-gradient"]),
            "line-trim-offset": new Rs(qt.paint_line["line-trim-offset"]),
            "line-outline-color": new js(qt.paint_line["line-outline-color"]),
            "line-outline-width": new js(qt.paint_line["line-outline-width"]),
            "line-outline-dasharray": new Us(qt.paint_line["line-outline-dasharray"]),
            "line-minzoom": new js(qt.paint_line["line-minzoom"]),
            "line-maxzoom": new js(qt.paint_line["line-maxzoom"])
        }),
        layout: Lh
    };
    const jh = new class extends js {
        possiblyEvaluate(t, e) {
            return e = new Ts(Math.floor(e.zoom),{
                now: e.now,
                fadeDuration: e.fadeDuration,
                zoomHistory: e.zoomHistory,
                transition: e.transition
            }),
            super.possiblyEvaluate(t, e)
        }
        evaluate(t, e, r, n) {
            return e = v({}, e, {
                zoom: Math.floor(e.zoom)
            }),
            super.evaluate(t, e, r, n)
        }
    }
    (Rh.paint.properties["line-width"].specification);
    jh.useIntegerZoom = !0;
    class Uh extends mo {
        constructor(t) {
            t && t.layout && "eline" == t.type && t.layout["esymbol-id"] && (t.paint["line-pattern"] = t.layout["esymbol-id"]),
            super(t, Rh),
            this.gradientVersion = 0;
        }
        _handleSpecialPaintPropertyUpdate(t) {
            if ("line-gradient" === t) {
                const t = this._transitionablePaint._values["line-gradient"].value.expression;
                this.stepInterpolant = t._styleExpression && t._styleExpression.expression instanceof yr,
                this.gradientVersion = (this.gradientVersion + 1) % Number.MAX_SAFE_INTEGER;
            }
        }
        gradientExpression() {
            return this._transitionablePaint._values["line-gradient"].value.expression
        }
        recalculate(t, e) {
            super.recalculate(t, e),
            this.paint._values["line-floorwidth"] = jh.possiblyEvaluate(this._transitioningPaint._values["line-width"].value, t),
            this.paint._values["line-outline-floorwidth"] = jh.possiblyEvaluate(this._transitioningPaint._values["line-outline-width"].value, t);
        }
        createBucket(t) {
            return new Fh(t)
        }
        getProgramIds() {
            return [this.paint.get("line-pattern").constantOr(1) ? "linePattern" : "line"]
        }
        getProgramConfiguration(t) {
            return new oo(this,t)
        }
        queryRadius(t) {
            const e = t
              , r = Oh(Math.max(jl("line-width", this, e), jl("line-outline-width", this, e)), jl("line-gap-width", this, e))
              , n = jl("line-offset", this, e);
            return r / 2 + Math.abs(n) + Ul(this.paint.get("line-translate"))
        }
        queryIntersectsFeature(t, e, r, n, s, a) {
            if (t.queryGeometry.isAboveHorizon)
                return !1;
            const o = Ol(t.tilespaceGeometry, this.paint.get("line-translate"), this.paint.get("line-translate-anchor"), a.angle, t.pixelToTileUnitsFactor)
              , l = t.pixelToTileUnitsFactor / 2 * Oh(this.paint.get("line-width").evaluate(e, r) + this.paint.get("line-outline-width").evaluate(e, r), this.paint.get("line-gap-width").evaluate(e, r))
              , u = this.paint.get("line-offset").evaluate(e, r);
            return u && (n = function(t, e) {
                const r = []
                  , n = new i(0,0);
                for (let i = 0; i < t.length; i++) {
                    const s = t[i]
                      , a = [];
                    for (let t = 0; t < s.length; t++) {
                        const r = s[t - 1]
                          , i = s[t]
                          , o = s[t + 1]
                          , l = 0 === t ? n : i.sub(r)._unit()._perp()
                          , u = t === s.length - 1 ? n : o.sub(i)._unit()._perp()
                          , c = l._add(u)._unit();
                        c._mult(1 / (c.x * u.x + c.y * u.y)),
                        a.push(c._mult(e)._add(i));
                    }
                    r.push(a);
                }
                return r
            }(n, u * t.pixelToTileUnitsFactor)),
            function(t, e, r) {
                for (let n = 0; n < e.length; n++) {
                    const i = e[n];
                    if (t.length >= 3)
                        for (let e = 0; e < i.length; e++)
                            if (Fl(t, i[e]))
                                return !0;
                    if (Bl(t, i, r))
                        return !0
                }
                return !1
            }(o, n, l)
        }
        isTileClipped() {
            return !0
        }
    }
    function Oh(t, e) {
        return e > 0 ? e + 2 * t : t
    }
    const $h = Ys([{
        name: "a_pos_offset",
        components: 4,
        type: "Int16"
    }, {
        name: "a_tex_size",
        components: 4,
        type: "Uint16"
    }, {
        name: "a_pixeloffset",
        components: 4,
        type: "Int16"
    }], 4)
      , qh = Ys([{
        name: "a_globe_anchor",
        components: 3,
        type: "Int16"
    }, {
        name: "a_globe_normal",
        components: 3,
        type: "Float32"
    }], 4)
      , Nh = Ys([{
        name: "a_projected_pos",
        components: 4,
        type: "Float32"
    }], 4);
    Ys([{
        name: "a_fade_opacity",
        components: 1,
        type: "Uint32"
    }], 4);
    const Zh = Ys([{
        name: "a_placed",
        components: 2,
        type: "Uint8"
    }, {
        name: "a_shift",
        components: 2,
        type: "Float32"
    }])
      , Gh = Ys([{
        name: "a_size_scale",
        components: 1,
        type: "Float32"
    }, {
        name: "a_padding",
        components: 2,
        type: "Float32"
    }]);
    Ys([{
        type: "Int16",
        name: "projectedAnchorX"
    }, {
        type: "Int16",
        name: "projectedAnchorY"
    }, {
        type: "Int16",
        name: "projectedAnchorZ"
    }, {
        type: "Int16",
        name: "tileAnchorX"
    }, {
        type: "Int16",
        name: "tileAnchorY"
    }, {
        type: "Float32",
        name: "x1"
    }, {
        type: "Float32",
        name: "y1"
    }, {
        type: "Float32",
        name: "x2"
    }, {
        type: "Float32",
        name: "y2"
    }, {
        type: "Int16",
        name: "padding"
    }, {
        type: "Uint32",
        name: "featureIndex"
    }, {
        type: "Uint16",
        name: "sourceLayerIndex"
    }, {
        type: "Uint16",
        name: "bucketIndex"
    }]);
    const Xh = Ys([{
        name: "a_pos",
        components: 3,
        type: "Int16"
    }, {
        name: "a_anchor_pos",
        components: 2,
        type: "Int16"
    }, {
        name: "a_extrude",
        components: 2,
        type: "Int16"
    }], 4)
      , Yh = Ys([{
        name: "a_pos_2f",
        components: 2,
        type: "Float32"
    }, {
        name: "a_radius",
        components: 1,
        type: "Float32"
    }, {
        name: "a_flags",
        components: 2,
        type: "Int16"
    }], 4);
    Ys([{
        name: "triangle",
        components: 3,
        type: "Uint16"
    }]),
    Ys([{
        type: "Int16",
        name: "projectedAnchorX"
    }, {
        type: "Int16",
        name: "projectedAnchorY"
    }, {
        type: "Int16",
        name: "projectedAnchorZ"
    }, {
        type: "Float32",
        name: "tileAnchorX"
    }, {
        type: "Float32",
        name: "tileAnchorY"
    }, {
        type: "Uint16",
        name: "glyphStartIndex"
    }, {
        type: "Uint16",
        name: "numGlyphs"
    }, {
        type: "Uint32",
        name: "vertexStartIndex"
    }, {
        type: "Uint32",
        name: "lineStartIndex"
    }, {
        type: "Uint32",
        name: "lineLength"
    }, {
        type: "Uint16",
        name: "segment"
    }, {
        type: "Uint16",
        name: "lowerSize"
    }, {
        type: "Uint16",
        name: "upperSize"
    }, {
        type: "Float32",
        name: "lineOffsetX"
    }, {
        type: "Float32",
        name: "lineOffsetY"
    }, {
        type: "Uint8",
        name: "writingMode"
    }, {
        type: "Uint8",
        name: "placedOrientation"
    }, {
        type: "Uint8",
        name: "hidden"
    }, {
        type: "Uint32",
        name: "crossTileID"
    }, {
        type: "Int16",
        name: "associatedIconIndex"
    }, {
        type: "Uint8",
        name: "flipState"
    }]),
    Ys([{
        type: "Int16",
        name: "projectedAnchorX"
    }, {
        type: "Int16",
        name: "projectedAnchorY"
    }, {
        type: "Int16",
        name: "projectedAnchorZ"
    }, {
        type: "Float32",
        name: "tileAnchorX"
    }, {
        type: "Float32",
        name: "tileAnchorY"
    }, {
        type: "Int16",
        name: "rightJustifiedTextSymbolIndex"
    }, {
        type: "Int16",
        name: "centerJustifiedTextSymbolIndex"
    }, {
        type: "Int16",
        name: "leftJustifiedTextSymbolIndex"
    }, {
        type: "Int16",
        name: "verticalPlacedTextSymbolIndex"
    }, {
        type: "Int16",
        name: "placedIconSymbolIndex"
    }, {
        type: "Int16",
        name: "verticalPlacedIconSymbolIndex"
    }, {
        type: "Uint16",
        name: "key"
    }, {
        type: "Uint16",
        name: "textBoxStartIndex"
    }, {
        type: "Uint16",
        name: "textBoxEndIndex"
    }, {
        type: "Uint16",
        name: "verticalTextBoxStartIndex"
    }, {
        type: "Uint16",
        name: "verticalTextBoxEndIndex"
    }, {
        type: "Uint16",
        name: "iconBoxStartIndex"
    }, {
        type: "Uint16",
        name: "iconBoxEndIndex"
    }, {
        type: "Uint16",
        name: "verticalIconBoxStartIndex"
    }, {
        type: "Uint16",
        name: "verticalIconBoxEndIndex"
    }, {
        type: "Uint16",
        name: "featureIndex"
    }, {
        type: "Uint16",
        name: "numHorizontalGlyphVertices"
    }, {
        type: "Uint16",
        name: "numVerticalGlyphVertices"
    }, {
        type: "Uint16",
        name: "numIconVertices"
    }, {
        type: "Uint16",
        name: "numVerticalIconVertices"
    }, {
        type: "Uint16",
        name: "useRuntimeCollisionCircles"
    }, {
        type: "Uint32",
        name: "crossTileID"
    }, {
        type: "Float32",
        components: 2,
        name: "textOffset"
    }, {
        type: "Float32",
        name: "collisionCircleDiameter"
    }]),
    Ys([{
        type: "Float32",
        name: "offsetX"
    }]),
    Ys([{
        type: "Int16",
        name: "x"
    }, {
        type: "Int16",
        name: "y"
    }, {
        type: "Int16",
        name: "tileUnitDistanceFromAnchor"
    }]);
    var Hh = 24;
    const Kh = 128;
    function Jh(t, e) {
        const {expression: r} = e;
        if ("constant" === r.kind)
            return {
                kind: "constant",
                layoutSize: r.evaluate(new Ts(t + 1))
            };
        if ("source" === r.kind)
            return {
                kind: "source"
            };
        {
            const {zoomStops: e, interpolationType: n} = r;
            let i = 0;
            for (; i < e.length && e[i] <= t; )
                i++;
            i = Math.max(0, i - 1);
            let s = i;
            for (; s < e.length && e[s] < t + 1; )
                s++;
            s = Math.min(e.length - 1, s);
            const a = e[i]
              , o = e[s];
            return "composite" === r.kind ? {
                kind: "composite",
                minZoom: a,
                maxZoom: o,
                interpolationType: n
            } : {
                kind: "camera",
                minZoom: a,
                maxZoom: o,
                minSize: r.evaluate(new Ts(a)),
                maxSize: r.evaluate(new Ts(o)),
                interpolationType: n
            }
        }
    }
    function Wh(t, {uSize: e, uSizeT: r}, {lowerSize: n, upperSize: i}) {
        return "source" === t.kind ? n / Kh : "composite" === t.kind ? mr(n / Kh, i / Kh, r) : e
    }
    function Qh(t, e) {
        let r = 0
          , n = 0;
        if ("constant" === t.kind)
            n = t.layoutSize;
        else if ("source" !== t.kind) {
            const {interpolationType: i, minZoom: s, maxZoom: a} = t
              , o = i ? d(Lr.interpolationFactor(i, e, s, a), 0, 1) : 0;
            "camera" === t.kind ? n = mr(t.minSize, t.maxSize, o) : r = o;
        }
        return {
            uSizeT: r,
            uSize: n
        }
    }
    var tp = Object.freeze({
        __proto__: null,
        getSizeData: Jh,
        evaluateSizeForFeature: Wh,
        evaluateSizeForZoom: Qh,
        SIZE_PACK_FACTOR: Kh
    });
    function ep(t, e, r) {
        return t.sections.forEach((t=>{
            t.text = function(t, e, r) {
                const n = e.layout.get("text-transform").evaluate(r, {});
                return "uppercase" === n ? t = t.toLocaleUpperCase() : "lowercase" === n && (t = t.toLocaleLowerCase()),
                Is.applyArabicShaping && (t = Is.applyArabicShaping(t)),
                t
            }(t.text, e, r);
        }
        )),
        t
    }
    const rp = {
        "!": "︕",
        "#": "＃",
        $: "＄",
        "%": "％",
        "&": "＆",
        "(": "︵",
        ")": "︶",
        "*": "＊",
        "+": "＋",
        ",": "︐",
        "-": "︲",
        ".": "・",
        "/": "／",
        ":": "︓",
        ";": "︔",
        "<": "︿",
        "=": "＝",
        ">": "﹀",
        "?": "︖",
        "@": "＠",
        "[": "﹇",
        "\\": "＼",
        "]": "﹈",
        "^": "＾",
        _: "︳",
        "`": "｀",
        "{": "︷",
        "|": "―",
        "}": "︸",
        "~": "～",
        "¢": "￠",
        "£": "￡",
        "¥": "￥",
        "¦": "￤",
        "¬": "￢",
        "¯": "￣",
        "–": "︲",
        "—": "︱",
        "‘": "﹃",
        "’": "﹄",
        "“": "﹁",
        "”": "﹂",
        "…": "︙",
        "‧": "・",
        "₩": "￦",
        "、": "︑",
        "。": "︒",
        "〈": "︿",
        "〉": "﹀",
        "《": "︽",
        "》": "︾",
        "「": "﹁",
        "」": "﹂",
        "『": "﹃",
        "』": "﹄",
        "【": "︻",
        "】": "︼",
        "〔": "︹",
        "〕": "︺",
        "〖": "︗",
        "〗": "︘",
        "！": "︕",
        "（": "︵",
        "）": "︶",
        "，": "︐",
        "－": "︲",
        "．": "・",
        "：": "︓",
        "；": "︔",
        "＜": "︿",
        "＞": "﹀",
        "？": "︖",
        "［": "﹇",
        "］": "﹈",
        "＿": "︳",
        "｛": "︷",
        "｜": "―",
        "｝": "︸",
        "｟": "︵",
        "｠": "︶",
        "｡": "︒",
        "｢": "﹁",
        "｣": "﹂"
    };
    function np(t) {
        return "︶" === t || "﹈" === t || "︸" === t || "﹄" === t || "﹂" === t || "︾" === t || "︼" === t || "︺" === t || "︘" === t || "﹀" === t || "︐" === t || "︓" === t || "︔" === t || "｀" === t || "￣" === t || "︑" === t || "︒" === t
    }
    function ip(t) {
        return "︵" === t || "﹇" === t || "︷" === t || "﹃" === t || "﹁" === t || "︽" === t || "︻" === t || "︹" === t || "︗" === t || "︿" === t
    }
    var sp = function(t, e, r, n, i) {
        var s, a, o = 8 * i - n - 1, l = (1 << o) - 1, u = l >> 1, c = -7, h = r ? i - 1 : 0, p = r ? -1 : 1, f = t[e + h];
        for (h += p,
        s = f & (1 << -c) - 1,
        f >>= -c,
        c += o; c > 0; s = 256 * s + t[e + h],
        h += p,
        c -= 8)
            ;
        for (a = s & (1 << -c) - 1,
        s >>= -c,
        c += n; c > 0; a = 256 * a + t[e + h],
        h += p,
        c -= 8)
            ;
        if (0 === s)
            s = 1 - u;
        else {
            if (s === l)
                return a ? NaN : 1 / 0 * (f ? -1 : 1);
            a += Math.pow(2, n),
            s -= u;
        }
        return (f ? -1 : 1) * a * Math.pow(2, s - n)
    }
      , ap = function(t, e, r, n, i, s) {
        var a, o, l, u = 8 * s - i - 1, c = (1 << u) - 1, h = c >> 1, p = 23 === i ? Math.pow(2, -24) - Math.pow(2, -77) : 0, f = n ? 0 : s - 1, d = n ? 1 : -1, y = e < 0 || 0 === e && 1 / e < 0 ? 1 : 0;
        for (e = Math.abs(e),
        isNaN(e) || e === 1 / 0 ? (o = isNaN(e) ? 1 : 0,
        a = c) : (a = Math.floor(Math.log(e) / Math.LN2),
        e * (l = Math.pow(2, -a)) < 1 && (a--,
        l *= 2),
        (e += a + h >= 1 ? p / l : p * Math.pow(2, 1 - h)) * l >= 2 && (a++,
        l /= 2),
        a + h >= c ? (o = 0,
        a = c) : a + h >= 1 ? (o = (e * l - 1) * Math.pow(2, i),
        a += h) : (o = e * Math.pow(2, h - 1) * Math.pow(2, i),
        a = 0)); i >= 8; t[r + f] = 255 & o,
        f += d,
        o /= 256,
        i -= 8)
            ;
        for (a = a << i | o,
        u += i; u > 0; t[r + f] = 255 & a,
        f += d,
        a /= 256,
        u -= 8)
            ;
        t[r + f - d] |= 128 * y;
    }
      , op = lp;
    function lp(t) {
        this.buf = ArrayBuffer.isView && ArrayBuffer.isView(t) ? t : new Uint8Array(t || 0),
        this.pos = 0,
        this.type = 0,
        this.length = this.buf.length;
    }
    lp.Varint = 0,
    lp.Fixed64 = 1,
    lp.Bytes = 2,
    lp.Fixed32 = 5;
    var up = 4294967296
      , cp = 1 / up
      , hp = "undefined" == typeof TextDecoder ? null : new TextDecoder("utf8");
    function pp(t) {
        return t.type === lp.Bytes ? t.readVarint() + t.pos : t.pos + 1
    }
    function fp(t, e, r) {
        return r ? 4294967296 * e + (t >>> 0) : 4294967296 * (e >>> 0) + (t >>> 0)
    }
    function dp(t, e, r) {
        var n = e <= 16383 ? 1 : e <= 2097151 ? 2 : e <= 268435455 ? 3 : Math.floor(Math.log(e) / (7 * Math.LN2));
        r.realloc(n);
        for (var i = r.pos - 1; i >= t; i--)
            r.buf[i + n] = r.buf[i];
    }
    function yp(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeVarint(t[r]);
    }
    function mp(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeSVarint(t[r]);
    }
    function gp(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeFloat(t[r]);
    }
    function xp(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeDouble(t[r]);
    }
    function vp(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeBoolean(t[r]);
    }
    function bp(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeFixed32(t[r]);
    }
    function _p(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeSFixed32(t[r]);
    }
    function wp(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeFixed64(t[r]);
    }
    function Ap(t, e) {
        for (var r = 0; r < t.length; r++)
            e.writeSFixed64(t[r]);
    }
    function kp(t, e) {
        return (t[e] | t[e + 1] << 8 | t[e + 2] << 16) + 16777216 * t[e + 3]
    }
    function zp(t, e, r) {
        t[r] = e,
        t[r + 1] = e >>> 8,
        t[r + 2] = e >>> 16,
        t[r + 3] = e >>> 24;
    }
    function Sp(t, e) {
        return (t[e] | t[e + 1] << 8 | t[e + 2] << 16) + (t[e + 3] << 24)
    }
    function Mp(t, e, r) {
        e.glyphs = [],
        1 === t && r.readMessage(Ip, e);
    }
    function Ip(t, e, r) {
        if (3 === t) {
            const {id: t, bitmap: n, width: i, height: s, left: a, top: o, advance: l} = r.readMessage(Tp, {});
            e.glyphs.push({
                id: t,
                bitmap: new Wu({
                    width: i + 6,
                    height: s + 6
                },n),
                metrics: {
                    width: i,
                    height: s,
                    left: a,
                    top: o,
                    advance: l
                }
            });
        } else
            4 === t ? e.ascender = r.readSVarint() : 5 === t && (e.descender = r.readSVarint());
    }
    function Tp(t, e, r) {
        1 === t ? e.id = r.readVarint() : 2 === t ? e.bitmap = r.readBytes() : 3 === t ? e.width = r.readVarint() : 4 === t ? e.height = r.readVarint() : 5 === t ? e.left = r.readSVarint() : 6 === t ? e.top = r.readSVarint() : 7 === t && (e.advance = r.readVarint());
    }
    function Bp(t) {
        let e = 0
          , r = 0;
        for (const n of t)
            e += n.w * n.h,
            r = Math.max(r, n.w);
        t.sort(((t,e)=>e.h - t.h));
        const n = [{
            x: 0,
            y: 0,
            w: Math.max(Math.ceil(Math.sqrt(e / .95)), r),
            h: 1 / 0
        }];
        let i = 0
          , s = 0;
        for (const e of t)
            for (let t = n.length - 1; t >= 0; t--) {
                const r = n[t];
                if (!(e.w > r.w || e.h > r.h)) {
                    if (e.x = r.x,
                    e.y = r.y,
                    s = Math.max(s, e.y + e.h),
                    i = Math.max(i, e.x + e.w),
                    e.w === r.w && e.h === r.h) {
                        const e = n.pop();
                        t < n.length && (n[t] = e);
                    } else
                        e.h === r.h ? (r.x += e.w,
                        r.w -= e.w) : e.w === r.w ? (r.y += e.h,
                        r.h -= e.h) : (n.push({
                            x: r.x + e.w,
                            y: r.y,
                            w: r.w - e.w,
                            h: e.h
                        }),
                        r.y += e.h,
                        r.h -= e.h);
                    break
                }
            }
        return {
            w: i,
            h: s,
            fill: e / (i * s) || 0
        }
    }
    lp.prototype = {
        destroy: function() {
            this.buf = null;
        },
        readFields: function(t, e, r) {
            for (r = r || this.length; this.pos < r; ) {
                var n = this.readVarint()
                  , i = n >> 3
                  , s = this.pos;
                this.type = 7 & n,
                t(i, e, this),
                this.pos === s && this.skip(n);
            }
            return e
        },
        readMessage: function(t, e) {
            return this.readFields(t, e, this.readVarint() + this.pos)
        },
        readFixed32: function() {
            var t = kp(this.buf, this.pos);
            return this.pos += 4,
            t
        },
        readSFixed32: function() {
            var t = Sp(this.buf, this.pos);
            return this.pos += 4,
            t
        },
        readFixed64: function() {
            var t = kp(this.buf, this.pos) + kp(this.buf, this.pos + 4) * up;
            return this.pos += 8,
            t
        },
        readSFixed64: function() {
            var t = kp(this.buf, this.pos) + Sp(this.buf, this.pos + 4) * up;
            return this.pos += 8,
            t
        },
        readFloat: function() {
            var t = sp(this.buf, this.pos, !0, 23, 4);
            return this.pos += 4,
            t
        },
        readDouble: function() {
            var t = sp(this.buf, this.pos, !0, 52, 8);
            return this.pos += 8,
            t
        },
        readVarint: function(t) {
            var e, r, n = this.buf;
            return e = 127 & (r = n[this.pos++]),
            r < 128 ? e : (e |= (127 & (r = n[this.pos++])) << 7,
            r < 128 ? e : (e |= (127 & (r = n[this.pos++])) << 14,
            r < 128 ? e : (e |= (127 & (r = n[this.pos++])) << 21,
            r < 128 ? e : function(t, e, r) {
                var n, i, s = r.buf;
                if (n = (112 & (i = s[r.pos++])) >> 4,
                i < 128)
                    return fp(t, n, e);
                if (n |= (127 & (i = s[r.pos++])) << 3,
                i < 128)
                    return fp(t, n, e);
                if (n |= (127 & (i = s[r.pos++])) << 10,
                i < 128)
                    return fp(t, n, e);
                if (n |= (127 & (i = s[r.pos++])) << 17,
                i < 128)
                    return fp(t, n, e);
                if (n |= (127 & (i = s[r.pos++])) << 24,
                i < 128)
                    return fp(t, n, e);
                if (n |= (1 & (i = s[r.pos++])) << 31,
                i < 128)
                    return fp(t, n, e);
                throw new Error("Expected varint not more than 10 bytes")
            }(e |= (15 & (r = n[this.pos])) << 28, t, this))))
        },
        readVarint64: function() {
            return this.readVarint(!0)
        },
        readSVarint: function() {
            var t = this.readVarint();
            return t % 2 == 1 ? (t + 1) / -2 : t / 2
        },
        readBoolean: function() {
            return Boolean(this.readVarint())
        },
        readString: function() {
            var t = this.readVarint() + this.pos
              , e = this.pos;
            return this.pos = t,
            t - e >= 12 && hp ? function(t, e, r) {
                return hp.decode(t.subarray(e, r))
            }(this.buf, e, t) : function(t, e, r) {
                for (var n = "", i = e; i < r; ) {
                    var s, a, o, l = t[i], u = null, c = l > 239 ? 4 : l > 223 ? 3 : l > 191 ? 2 : 1;
                    if (i + c > r)
                        break;
                    1 === c ? l < 128 && (u = l) : 2 === c ? 128 == (192 & (s = t[i + 1])) && (u = (31 & l) << 6 | 63 & s) <= 127 && (u = null) : 3 === c ? (a = t[i + 2],
                    128 == (192 & (s = t[i + 1])) && 128 == (192 & a) && ((u = (15 & l) << 12 | (63 & s) << 6 | 63 & a) <= 2047 || u >= 55296 && u <= 57343) && (u = null)) : 4 === c && (a = t[i + 2],
                    o = t[i + 3],
                    128 == (192 & (s = t[i + 1])) && 128 == (192 & a) && 128 == (192 & o) && ((u = (15 & l) << 18 | (63 & s) << 12 | (63 & a) << 6 | 63 & o) <= 65535 || u >= 1114112) && (u = null)),
                    null === u ? (u = 65533,
                    c = 1) : u > 65535 && (u -= 65536,
                    n += String.fromCharCode(u >>> 10 & 1023 | 55296),
                    u = 56320 | 1023 & u),
                    n += String.fromCharCode(u),
                    i += c;
                }
                return n
            }(this.buf, e, t)
        },
        readBytes: function() {
            var t = this.readVarint() + this.pos
              , e = this.buf.subarray(this.pos, t);
            return this.pos = t,
            e
        },
        readPackedVarint: function(t, e) {
            if (this.type !== lp.Bytes)
                return t.push(this.readVarint(e));
            var r = pp(this);
            for (t = t || []; this.pos < r; )
                t.push(this.readVarint(e));
            return t
        },
        readPackedSVarint: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readSVarint());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readSVarint());
            return t
        },
        readPackedBoolean: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readBoolean());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readBoolean());
            return t
        },
        readPackedFloat: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readFloat());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readFloat());
            return t
        },
        readPackedDouble: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readDouble());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readDouble());
            return t
        },
        readPackedFixed32: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readFixed32());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readFixed32());
            return t
        },
        readPackedSFixed32: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readSFixed32());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readSFixed32());
            return t
        },
        readPackedFixed64: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readFixed64());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readFixed64());
            return t
        },
        readPackedSFixed64: function(t) {
            if (this.type !== lp.Bytes)
                return t.push(this.readSFixed64());
            var e = pp(this);
            for (t = t || []; this.pos < e; )
                t.push(this.readSFixed64());
            return t
        },
        skip: function(t) {
            var e = 7 & t;
            if (e === lp.Varint)
                for (; this.buf[this.pos++] > 127; )
                    ;
            else if (e === lp.Bytes)
                this.pos = this.readVarint() + this.pos;
            else if (e === lp.Fixed32)
                this.pos += 4;
            else {
                if (e !== lp.Fixed64)
                    throw new Error("Unimplemented type: " + e);
                this.pos += 8;
            }
        },
        writeTag: function(t, e) {
            this.writeVarint(t << 3 | e);
        },
        realloc: function(t) {
            for (var e = this.length || 16; e < this.pos + t; )
                e *= 2;
            if (e !== this.length) {
                var r = new Uint8Array(e);
                r.set(this.buf),
                this.buf = r,
                this.length = e;
            }
        },
        finish: function() {
            return this.length = this.pos,
            this.pos = 0,
            this.buf.subarray(0, this.length)
        },
        writeFixed32: function(t) {
            this.realloc(4),
            zp(this.buf, t, this.pos),
            this.pos += 4;
        },
        writeSFixed32: function(t) {
            this.realloc(4),
            zp(this.buf, t, this.pos),
            this.pos += 4;
        },
        writeFixed64: function(t) {
            this.realloc(8),
            zp(this.buf, -1 & t, this.pos),
            zp(this.buf, Math.floor(t * cp), this.pos + 4),
            this.pos += 8;
        },
        writeSFixed64: function(t) {
            this.realloc(8),
            zp(this.buf, -1 & t, this.pos),
            zp(this.buf, Math.floor(t * cp), this.pos + 4),
            this.pos += 8;
        },
        writeVarint: function(t) {
            (t = +t || 0) > 268435455 || t < 0 ? function(t, e) {
                var r, n;
                if (t >= 0 ? (r = t % 4294967296 | 0,
                n = t / 4294967296 | 0) : (n = ~(-t / 4294967296),
                4294967295 ^ (r = ~(-t % 4294967296)) ? r = r + 1 | 0 : (r = 0,
                n = n + 1 | 0)),
                t >= 0x10000000000000000 || t < -0x10000000000000000)
                    throw new Error("Given varint doesn't fit into 10 bytes");
                e.realloc(10),
                function(t, e, r) {
                    r.buf[r.pos++] = 127 & t | 128,
                    t >>>= 7,
                    r.buf[r.pos++] = 127 & t | 128,
                    t >>>= 7,
                    r.buf[r.pos++] = 127 & t | 128,
                    t >>>= 7,
                    r.buf[r.pos++] = 127 & t | 128,
                    r.buf[r.pos] = 127 & (t >>>= 7);
                }(r, 0, e),
                function(t, e) {
                    var r = (7 & t) << 4;
                    e.buf[e.pos++] |= r | ((t >>>= 3) ? 128 : 0),
                    t && (e.buf[e.pos++] = 127 & t | ((t >>>= 7) ? 128 : 0),
                    t && (e.buf[e.pos++] = 127 & t | ((t >>>= 7) ? 128 : 0),
                    t && (e.buf[e.pos++] = 127 & t | ((t >>>= 7) ? 128 : 0),
                    t && (e.buf[e.pos++] = 127 & t | ((t >>>= 7) ? 128 : 0),
                    t && (e.buf[e.pos++] = 127 & t)))));
                }(n, e);
            }(t, this) : (this.realloc(4),
            this.buf[this.pos++] = 127 & t | (t > 127 ? 128 : 0),
            t <= 127 || (this.buf[this.pos++] = 127 & (t >>>= 7) | (t > 127 ? 128 : 0),
            t <= 127 || (this.buf[this.pos++] = 127 & (t >>>= 7) | (t > 127 ? 128 : 0),
            t <= 127 || (this.buf[this.pos++] = t >>> 7 & 127))));
        },
        writeSVarint: function(t) {
            this.writeVarint(t < 0 ? 2 * -t - 1 : 2 * t);
        },
        writeBoolean: function(t) {
            this.writeVarint(Boolean(t));
        },
        writeString: function(t) {
            t = String(t),
            this.realloc(4 * t.length),
            this.pos++;
            var e = this.pos;
            this.pos = function(t, e, r) {
                for (var n, i, s = 0; s < e.length; s++) {
                    if ((n = e.charCodeAt(s)) > 55295 && n < 57344) {
                        if (!i) {
                            n > 56319 || s + 1 === e.length ? (t[r++] = 239,
                            t[r++] = 191,
                            t[r++] = 189) : i = n;
                            continue
                        }
                        if (n < 56320) {
                            t[r++] = 239,
                            t[r++] = 191,
                            t[r++] = 189,
                            i = n;
                            continue
                        }
                        n = i - 55296 << 10 | n - 56320 | 65536,
                        i = null;
                    } else
                        i && (t[r++] = 239,
                        t[r++] = 191,
                        t[r++] = 189,
                        i = null);
                    n < 128 ? t[r++] = n : (n < 2048 ? t[r++] = n >> 6 | 192 : (n < 65536 ? t[r++] = n >> 12 | 224 : (t[r++] = n >> 18 | 240,
                    t[r++] = n >> 12 & 63 | 128),
                    t[r++] = n >> 6 & 63 | 128),
                    t[r++] = 63 & n | 128);
                }
                return r
            }(this.buf, t, this.pos);
            var r = this.pos - e;
            r >= 128 && dp(e, r, this),
            this.pos = e - 1,
            this.writeVarint(r),
            this.pos += r;
        },
        writeFloat: function(t) {
            this.realloc(4),
            ap(this.buf, t, this.pos, !0, 23, 4),
            this.pos += 4;
        },
        writeDouble: function(t) {
            this.realloc(8),
            ap(this.buf, t, this.pos, !0, 52, 8),
            this.pos += 8;
        },
        writeBytes: function(t) {
            var e = t.length;
            this.writeVarint(e),
            this.realloc(e);
            for (var r = 0; r < e; r++)
                this.buf[this.pos++] = t[r];
        },
        writeRawMessage: function(t, e) {
            this.pos++;
            var r = this.pos;
            t(e, this);
            var n = this.pos - r;
            n >= 128 && dp(r, n, this),
            this.pos = r - 1,
            this.writeVarint(n),
            this.pos += n;
        },
        writeMessage: function(t, e, r) {
            this.writeTag(t, lp.Bytes),
            this.writeRawMessage(e, r);
        },
        writePackedVarint: function(t, e) {
            e.length && this.writeMessage(t, yp, e);
        },
        writePackedSVarint: function(t, e) {
            e.length && this.writeMessage(t, mp, e);
        },
        writePackedBoolean: function(t, e) {
            e.length && this.writeMessage(t, vp, e);
        },
        writePackedFloat: function(t, e) {
            e.length && this.writeMessage(t, gp, e);
        },
        writePackedDouble: function(t, e) {
            e.length && this.writeMessage(t, xp, e);
        },
        writePackedFixed32: function(t, e) {
            e.length && this.writeMessage(t, bp, e);
        },
        writePackedSFixed32: function(t, e) {
            e.length && this.writeMessage(t, _p, e);
        },
        writePackedFixed64: function(t, e) {
            e.length && this.writeMessage(t, wp, e);
        },
        writePackedSFixed64: function(t, e) {
            e.length && this.writeMessage(t, Ap, e);
        },
        writeBytesField: function(t, e) {
            this.writeTag(t, lp.Bytes),
            this.writeBytes(e);
        },
        writeFixed32Field: function(t, e) {
            this.writeTag(t, lp.Fixed32),
            this.writeFixed32(e);
        },
        writeSFixed32Field: function(t, e) {
            this.writeTag(t, lp.Fixed32),
            this.writeSFixed32(e);
        },
        writeFixed64Field: function(t, e) {
            this.writeTag(t, lp.Fixed64),
            this.writeFixed64(e);
        },
        writeSFixed64Field: function(t, e) {
            this.writeTag(t, lp.Fixed64),
            this.writeSFixed64(e);
        },
        writeVarintField: function(t, e) {
            this.writeTag(t, lp.Varint),
            this.writeVarint(e);
        },
        writeSVarintField: function(t, e) {
            this.writeTag(t, lp.Varint),
            this.writeSVarint(e);
        },
        writeStringField: function(t, e) {
            this.writeTag(t, lp.Bytes),
            this.writeString(e);
        },
        writeFloatField: function(t, e) {
            this.writeTag(t, lp.Fixed32),
            this.writeFloat(e);
        },
        writeDoubleField: function(t, e) {
            this.writeTag(t, lp.Fixed64),
            this.writeDouble(e);
        },
        writeBooleanField: function(t, e) {
            this.writeVarintField(t, Boolean(e));
        }
    };
    class Cp {
        constructor(t, {pixelRatio: e, version: r, stretchX: n, stretchY: i, content: s}) {
            this.paddedRect = t,
            this.pixelRatio = e,
            this.stretchX = n,
            this.stretchY = i,
            this.content = s,
            this.version = r;
        }
        get tl() {
            return [this.paddedRect.x + 1, this.paddedRect.y + 1]
        }
        get br() {
            return [this.paddedRect.x + this.paddedRect.w - 1, this.paddedRect.y + this.paddedRect.h - 1]
        }
        get displaySize() {
            return [(this.paddedRect.w - 2) / this.pixelRatio, (this.paddedRect.h - 2) / this.pixelRatio]
        }
    }
    class Vp {
        constructor(t, e) {
            const r = {}
              , n = {};
            this.haveRenderCallbacks = [];
            const i = [];
            this.addImages(t, r, i),
            this.addImages(e, n, i);
            const {w: s, h: a} = Bp(i)
              , o = new Qu({
                width: s || 1,
                height: a || 1
            });
            for (const e in t) {
                const n = t[e]
                  , i = r[e].paddedRect;
                Qu.copy(n.data, o, {
                    x: 0,
                    y: 0
                }, {
                    x: i.x + 1,
                    y: i.y + 1
                }, n.data);
            }
            for (const t in e) {
                const r = e[t]
                  , i = n[t].paddedRect
                  , s = i.x + 1
                  , a = i.y + 1
                  , l = r.data.width
                  , u = r.data.height;
                Qu.copy(r.data, o, {
                    x: 0,
                    y: 0
                }, {
                    x: s,
                    y: a
                }, r.data),
                Qu.copy(r.data, o, {
                    x: 0,
                    y: u - 1
                }, {
                    x: s,
                    y: a - 1
                }, {
                    width: l,
                    height: 1
                }),
                Qu.copy(r.data, o, {
                    x: 0,
                    y: 0
                }, {
                    x: s,
                    y: a + u
                }, {
                    width: l,
                    height: 1
                }),
                Qu.copy(r.data, o, {
                    x: l - 1,
                    y: 0
                }, {
                    x: s - 1,
                    y: a
                }, {
                    width: 1,
                    height: u
                }),
                Qu.copy(r.data, o, {
                    x: 0,
                    y: 0
                }, {
                    x: s + l,
                    y: a
                }, {
                    width: 1,
                    height: u
                });
            }
            this.image = o,
            this.iconPositions = r,
            this.patternPositions = n;
        }
        addImages(t, e, r) {
            for (const n in t) {
                const i = t[n]
                  , s = {
                    x: 0,
                    y: 0,
                    w: i.data.width + 2,
                    h: i.data.height + 2
                };
                r.push(s),
                e[n] = new Cp(s,i),
                i.hasRenderCallback && this.haveRenderCallbacks.push(n);
            }
        }
        patchUpdatedImages(t, e) {
            this.haveRenderCallbacks = this.haveRenderCallbacks.filter((e=>t.hasImage(e))),
            t.dispatchRenderCallbacks(this.haveRenderCallbacks);
            for (const r in t.updatedImages)
                this.patchUpdatedImage(this.iconPositions[r], t.getImage(r), e),
                this.patchUpdatedImage(this.patternPositions[r], t.getImage(r), e);
        }
        patchUpdatedImage(t, e, r) {
            if (!t || !e)
                return;
            if (t.version === e.version)
                return;
            t.version = e.version;
            const [n,i] = t.tl;
            r.update(e.data, void 0, {
                x: n,
                y: i
            });
        }
    }
    Bi(Cp, "ImagePosition"),
    Bi(Vp, "ImageAtlas");
    const Pp = {
        horizontal: 1,
        vertical: 2,
        horizontalOnly: 3
    };
    class Dp {
        constructor() {
            this.scale = 1,
            this.fontStack = "",
            this.imageName = null;
        }
        static forText(t, e) {
            const r = new Dp;
            return r.scale = t || 1,
            r.fontStack = e,
            r
        }
        static forImage(t) {
            const e = new Dp;
            return e.imageName = t,
            e
        }
    }
    class Ep {
        constructor() {
            this.text = "",
            this.sectionIndex = [],
            this.sections = [],
            this.imageSectionID = null;
        }
        static fromFeature(t, e) {
            const r = new Ep;
            for (let n = 0; n < t.sections.length; n++) {
                const i = t.sections[n];
                i.image ? r.addImageSection(i) : r.addTextSection(i, e);
            }
            return r
        }
        length() {
            return this.text.length
        }
        getSection(t) {
            return this.sections[this.sectionIndex[t]]
        }
        getSections() {
            return this.sections
        }
        getSectionIndex(t) {
            return this.sectionIndex[t]
        }
        getCharCode(t) {
            return this.text.charCodeAt(t)
        }
        verticalizePunctuation(t) {
            this.text = function(t, e) {
                let r = "";
                for (let n = 0; n < t.length; n++) {
                    const i = t.charCodeAt(n + 1) || null
                      , s = t.charCodeAt(n - 1) || null;
                    r += !e && (i && fs(i) && !rp[t[n + 1]] || s && fs(s) && !rp[t[n - 1]]) || !rp[t[n]] ? t[n] : rp[t[n]];
                }
                return r
            }(this.text, t);
        }
        trim() {
            let t = 0;
            for (let e = 0; e < this.text.length && Lp[this.text.charCodeAt(e)]; e++)
                t++;
            let e = this.text.length;
            for (let r = this.text.length - 1; r >= 0 && r >= t && Lp[this.text.charCodeAt(r)]; r--)
                e--;
            this.text = this.text.substring(t, e),
            this.sectionIndex = this.sectionIndex.slice(t, e);
        }
        substring(t, e) {
            const r = new Ep;
            return r.text = this.text.substring(t, e),
            r.sectionIndex = this.sectionIndex.slice(t, e),
            r.sections = this.sections,
            r
        }
        toString() {
            return this.text
        }
        getMaxScale() {
            return this.sectionIndex.reduce(((t,e)=>Math.max(t, this.sections[e].scale)), 0)
        }
        addTextSection(t, e) {
            this.text += t.text,
            this.sections.push(Dp.forText(t.scale, t.fontStack || e));
            const r = this.sections.length - 1;
            for (let e = 0; e < t.text.length; ++e)
                this.sectionIndex.push(r);
        }
        addImageSection(t) {
            const e = t.image ? t.image.name : "";
            if (0 === e.length)
                return void B("Can't add FormattedSection with an empty image.");
            const r = this.getNextImageSectionCharCode();
            r ? (this.text += String.fromCharCode(r),
            this.sections.push(Dp.forImage(e)),
            this.sectionIndex.push(this.sections.length - 1)) : B("Reached maximum number of images 6401");
        }
        getNextImageSectionCharCode() {
            return this.imageSectionID ? this.imageSectionID >= 63743 ? null : ++this.imageSectionID : (this.imageSectionID = 57344,
            this.imageSectionID)
        }
    }
    function Fp(t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y) {
        const m = Ep.fromFeature(t, i);
        let g;
        h === Pp.vertical && m.verticalizePunctuation(p);
        const {processBidirectionalText: x, processStyledBidirectionalText: v} = Is;
        if (x && 1 === m.sections.length) {
            g = [];
            const t = x(m.toString(), Np(m, u, s, e, n, f, d));
            for (const e of t) {
                const t = new Ep;
                t.text = e,
                t.sections = m.sections;
                for (let r = 0; r < e.length; r++)
                    t.sectionIndex.push(0);
                g.push(t);
            }
        } else if (v) {
            g = [];
            const t = v(m.text, m.sectionIndex, Np(m, u, s, e, n, f, d));
            for (const e of t) {
                const t = new Ep;
                t.text = e[0],
                t.sectionIndex = e[1],
                t.sections = m.sections,
                g.push(t);
            }
        } else
            g = function(t, e) {
                const r = []
                  , n = t.text;
                let i = 0;
                for (const n of e)
                    r.push(t.substring(i, n)),
                    i = n;
                return i < n.length && r.push(t.substring(i, n.length)),
                r
            }(m, Np(m, u, s, e, n, f, d));
        const b = []
          , _ = {
            positionedLines: b,
            text: m.toString(),
            top: c[1],
            bottom: c[1],
            left: c[0],
            right: c[0],
            writingMode: h,
            iconsInText: !1,
            verticalizable: !1,
            hasBaseline: !1
        };
        return function(t, e, r, n, i, s, a, o, l, u, c, h) {
            let p = 0
              , f = 0
              , d = 0;
            const y = "right" === o ? 1 : "left" === o ? 0 : .5;
            let m = !1;
            for (const t of i) {
                const r = t.getSections();
                for (const t of r) {
                    if (t.imageName)
                        continue;
                    const r = e[t.fontStack];
                    if (r && (m = void 0 !== r.ascender && void 0 !== r.descender,
                    !m))
                        break
                }
                if (!m)
                    break
            }
            let g = 0;
            for (const a of i) {
                a.trim();
                const i = a.getMaxScale()
                  , o = (i - 1) * Hh
                  , v = {
                    positionedGlyphs: [],
                    lineOffset: 0
                };
                t.positionedLines[g] = v;
                const b = v.positionedGlyphs;
                let _ = 0;
                if (!a.length()) {
                    f += s,
                    ++g;
                    continue
                }
                let w = 0
                  , A = 0;
                for (let s = 0; s < a.length(); s++) {
                    const o = a.getSection(s)
                      , d = a.getSectionIndex(s)
                      , y = a.getCharCode(s);
                    let g = o.scale
                      , v = null
                      , k = null
                      , z = null
                      , S = Hh
                      , M = 0;
                    const I = !(l === Pp.horizontal || !c && !ps(y) || c && (Lp[y] || (x = y,
                    Fi(x) || Li(x) || Ri(x) || ns(x) || os(x))));
                    if (o.imageName) {
                        const e = n[o.imageName];
                        if (!e)
                            continue;
                        z = o.imageName,
                        t.iconsInText = t.iconsInText || !0,
                        k = e.paddedRect;
                        const r = e.displaySize;
                        g = g * Hh / h,
                        v = {
                            width: r[0],
                            height: r[1],
                            left: 1,
                            top: -3,
                            advance: I ? r[1] : r[0],
                            localGlyph: !1
                        },
                        M = m ? -v.height * g : i * Hh - 17 - r[1] * g,
                        S = v.advance;
                        const s = (I ? r[0] : r[1]) * g - Hh * i;
                        s > 0 && s > _ && (_ = s);
                    } else {
                        const t = r[o.fontStack];
                        if (!t)
                            continue;
                        t[y] && (k = t[y]);
                        const n = e[o.fontStack];
                        if (!n)
                            continue;
                        const s = n.glyphs[y];
                        if (!s)
                            continue;
                        if (v = s.metrics,
                        S = 8203 !== y ? Hh : 0,
                        m) {
                            const t = void 0 !== n.ascender ? Math.abs(n.ascender) : 0
                              , e = void 0 !== n.descender ? Math.abs(n.descender) : 0
                              , r = (t + e) * g;
                            w < r && (w = r,
                            A = (t - e) / 2 * g),
                            M = -t * g;
                        } else
                            M = (i - g) * Hh - 17;
                    }
                    I ? (t.verticalizable = !0,
                    b.push({
                        glyph: y,
                        imageName: z,
                        x: p,
                        y: f + M,
                        vertical: I,
                        scale: g,
                        localGlyph: v.localGlyph,
                        fontStack: o.fontStack,
                        sectionIndex: d,
                        metrics: v,
                        rect: k
                    }),
                    p += S * g + u) : (b.push({
                        glyph: y,
                        imageName: z,
                        x: p,
                        y: f + M,
                        vertical: I,
                        scale: g,
                        localGlyph: v.localGlyph,
                        fontStack: o.fontStack,
                        sectionIndex: d,
                        metrics: v,
                        rect: k
                    }),
                    p += v.advance * g + u);
                }
                0 !== b.length && (d = Math.max(p - u, d),
                m ? Gp(b, y, _, A, s * i / 2) : Gp(b, y, _, 0, s / 2)),
                p = 0;
                const k = s * i + _;
                v.lineOffset = Math.max(_, o),
                f += k,
                ++g;
            }
            var x;
            const v = f
              , {horizontalAlign: b, verticalAlign: _} = Zp(a);
            ((function(t, e, r, n, i, s) {
                const a = (e - r) * i
                  , o = -s * n;
                for (const e of t)
                    for (const t of e.positionedGlyphs)
                        t.x += a,
                        t.y += o;
            }
            ))(t.positionedLines, y, b, _, d, v),
            t.top += -_ * v,
            t.bottom = t.top + v,
            t.left += -b * d,
            t.right = t.left + d,
            t.hasBaseline = m;
        }(_, e, r, n, g, a, o, l, h, u, p, y),
        !function(t) {
            for (const e of t)
                if (0 !== e.positionedGlyphs.length)
                    return !1;
            return !0
        }(b) && _
    }
    const Lp = {
        9: !0,
        10: !0,
        11: !0,
        12: !0,
        13: !0,
        32: !0
    }
      , Rp = {
        10: !0,
        32: !0,
        38: !0,
        40: !0,
        41: !0,
        43: !0,
        45: !0,
        47: !0,
        173: !0,
        183: !0,
        8203: !0,
        8208: !0,
        8211: !0,
        8231: !0
    };
    function jp(t, e, r, n, i, s) {
        if (e.imageName) {
            const t = n[e.imageName];
            return t ? t.displaySize[0] * e.scale * Hh / s + i : 0
        }
        {
            const n = r[e.fontStack]
              , s = n && n.glyphs[t];
            return s ? s.metrics.advance * e.scale + i : 0
        }
    }
    function Up(t, e, r, n) {
        const i = Math.pow(t - e, 2);
        return n ? t < e ? i / 2 : 2 * i : i + Math.abs(r) * r
    }
    function Op(t, e, r) {
        let n = 0;
        return 10 === t && (n -= 1e4),
        r && (n += 150),
        40 !== t && 65288 !== t || (n += 50),
        41 !== e && 65289 !== e || (n += 50),
        n
    }
    function $p(t, e, r, n, i, s) {
        let a = null
          , o = Up(e, r, i, s);
        for (const t of n) {
            const n = Up(e - t.x, r, i, s) + t.badness;
            n <= o && (a = t,
            o = n);
        }
        return {
            index: t,
            x: e,
            priorBreak: a,
            badness: o
        }
    }
    function qp(t) {
        return t ? qp(t.priorBreak).concat(t.index) : []
    }
    function Np(t, e, r, n, i, s, a) {
        if ("point" !== s)
            return [];
        if (!t)
            return [];
        const o = []
          , l = function(t, e, r, n, i, s) {
            let a = 0;
            for (let r = 0; r < t.length(); r++) {
                const o = t.getSection(r);
                a += jp(t.getCharCode(r), o, n, i, e, s);
            }
            return a / Math.max(1, Math.ceil(a / r))
        }(t, e, r, n, i, a)
          , u = t.text.indexOf("​") >= 0;
        let c = 0;
        for (let r = 0; r < t.length(); r++) {
            const s = t.getSection(r)
              , p = t.getCharCode(r);
            if (Lp[p] || (c += jp(p, s, n, i, e, a)),
            r < t.length() - 1) {
                const e = !((h = p) < 11904 || !(Gi(h) || Zi(h) || ss(h) || rs(h) || Ki(h) || ji(h) || Xi(h) || $i(h) || Ji(h) || Wi(h) || Hi(h) || ls(h) || qi(h) || Oi(h) || Ui(h) || Yi(h) || Ni(h) || is(h) || ts(h) || Qi(h)));
                (Rp[p] || e || s.imageName) && o.push($p(r + 1, c, l, o, Op(p, t.getCharCode(r + 1), e && u), !1));
            }
        }
        var h;
        return qp($p(t.length(), c, l, o, 0, !0))
    }
    function Zp(t) {
        let e = .5
          , r = .5;
        switch (t) {
        case "right":
        case "top-right":
        case "bottom-right":
            e = 1;
            break;
        case "left":
        case "top-left":
        case "bottom-left":
            e = 0;
        }
        switch (t) {
        case "bottom":
        case "bottom-right":
        case "bottom-left":
            r = 1;
            break;
        case "top":
        case "top-right":
        case "top-left":
            r = 0;
        }
        return {
            horizontalAlign: e,
            verticalAlign: r
        }
    }
    function Gp(t, e, r, n, i) {
        if (!(e || r || n || i))
            return;
        const s = t.length - 1
          , a = t[s]
          , o = (a.x + a.metrics.advance * a.scale) * e;
        for (let e = 0; e <= s; e++)
            t[e].x -= o,
            t[e].y += r + n + i;
    }
    function Xp(t, e, r) {
        const {horizontalAlign: n, verticalAlign: i} = Zp(r)
          , s = e[0] - t.displaySize[0] * n
          , a = e[1] - t.displaySize[1] * i;
        return {
            image: t,
            top: a,
            bottom: a + t.displaySize[1],
            left: s,
            right: s + t.displaySize[0]
        }
    }
    function Yp(t, e, r, n, i, s) {
        const a = t.image;
        let o;
        if (a.content) {
            const t = a.content
              , e = a.pixelRatio || 1;
            o = [t[0] / e, t[1] / e, a.displaySize[0] - t[2] / e, a.displaySize[1] - t[3] / e];
        }
        const l = e.left * s
          , u = e.right * s;
        let c, h, p, f;
        "width" === r || "both" === r ? (f = i[0] + l - n[3],
        h = i[0] + u + n[1]) : (f = i[0] + (l + u - a.displaySize[0]) / 2,
        h = f + a.displaySize[0]);
        const d = e.top * s
          , y = e.bottom * s;
        return "height" === r || "both" === r ? (c = i[1] + d - n[0],
        p = i[1] + y + n[2]) : (c = i[1] + (d + y - a.displaySize[1]) / 2,
        p = c + a.displaySize[1]),
        {
            image: a,
            top: c,
            right: h,
            bottom: p,
            left: f,
            collisionPadding: o
        }
    }
    class Hp extends i {
        constructor(t, e, r, n, i) {
            super(t, e),
            this.angle = n,
            this.z = r,
            void 0 !== i && (this.segment = i);
        }
        clone() {
            return new Hp(this.x,this.y,this.z,this.angle,this.segment)
        }
    }
    function Kp(t, e, r, n, i) {
        if (void 0 === e.segment)
            return !0;
        let s = e
          , a = e.segment + 1
          , o = 0;
        for (; o > -r / 2; ) {
            if (a--,
            a < 0)
                return !1;
            o -= t[a].dist(s),
            s = t[a];
        }
        o += t[a].dist(t[a + 1]),
        a++;
        const l = [];
        let u = 0;
        for (; o < r / 2; ) {
            const e = t[a]
              , r = t[a + 1];
            if (!r)
                return !1;
            let s = t[a - 1].angleTo(e) - e.angleTo(r);
            for (s = Math.abs((s + 3 * Math.PI) % (2 * Math.PI) - Math.PI),
            l.push({
                distance: o,
                angleDelta: s
            }),
            u += s; o - l[0].distance > n; )
                u -= l.shift().angleDelta;
            if (u > i)
                return !1;
            a++,
            o += e.dist(r);
        }
        return !0
    }
    function Jp(t) {
        let e = 0;
        for (let r = 0; r < t.length - 1; r++)
            e += t[r].dist(t[r + 1]);
        return e
    }
    function Wp(t, e, r) {
        return t ? .6 * e * r : 0
    }
    function Qp(t, e) {
        return Math.max(t ? t.right - t.left : 0, e ? e.right - e.left : 0)
    }
    function tf(t, e, r, n, i, s) {
        const a = Wp(r, i, s)
          , o = Qp(r, n) * s;
        let l = 0;
        const u = Jp(t) / 2;
        for (let r = 0; r < t.length - 1; r++) {
            const n = t[r]
              , i = t[r + 1]
              , s = n.dist(i);
            if (l + s > u) {
                const c = (u - l) / s
                  , h = mr(n.x, i.x, c)
                  , p = mr(n.y, i.y, c)
                  , f = new Hp(h,p,0,i.angleTo(n),r);
                return !a || Kp(t, f, o, a, e) ? f : void 0
            }
            l += s;
        }
    }
    function ef(t, e, r, n, i, s, a, o, l) {
        const u = Wp(n, s, a)
          , c = Qp(n, i)
          , h = c * a
          , p = 0 === t[0].x || t[0].x === l || 0 === t[0].y || t[0].y === l;
        return e - h < e / 4 && (e = h + e / 4),
        rf(t, p ? e / 2 * o % e : (c / 2 + 2 * s) * a * o % e, e, u, r, h, p, !1, l)
    }
    function rf(t, e, r, n, i, s, a, o, l) {
        const u = s / 2
          , c = Jp(t);
        let h = 0
          , p = e - r
          , f = [];
        for (let e = 0; e < t.length - 1; e++) {
            const a = t[e]
              , o = t[e + 1]
              , d = a.dist(o)
              , y = o.angleTo(a);
            for (; p + r < h + d; ) {
                p += r;
                const m = (p - h) / d
                  , g = mr(a.x, o.x, m)
                  , x = mr(a.y, o.y, m);
                if (g >= 0 && g < l && x >= 0 && x < l && p - u >= 0 && p + u <= c) {
                    const r = new Hp(g,x,0,y,e);
                    r._round(),
                    n && !Kp(t, r, s, n, i) || f.push(r);
                }
            }
            h += d;
        }
        return o || f.length || a || (f = rf(t, h / 2, r, n, i, s, a, !0, l)),
        f
    }
    function nf(t, e, r, n, s) {
        const a = [];
        for (let o = 0; o < t.length; o++) {
            const l = t[o];
            let u;
            for (let t = 0; t < l.length - 1; t++) {
                let o = l[t]
                  , c = l[t + 1];
                o.x < e && c.x < e || (o.x < e ? o = new i(e,o.y + (e - o.x) / (c.x - o.x) * (c.y - o.y))._round() : c.x < e && (c = new i(e,o.y + (e - o.x) / (c.x - o.x) * (c.y - o.y))._round()),
                o.y < r && c.y < r || (o.y < r ? o = new i(o.x + (r - o.y) / (c.y - o.y) * (c.x - o.x),r)._round() : c.y < r && (c = new i(o.x + (r - o.y) / (c.y - o.y) * (c.x - o.x),r)._round()),
                o.x >= n && c.x >= n || (o.x >= n ? o = new i(n,o.y + (n - o.x) / (c.x - o.x) * (c.y - o.y))._round() : c.x >= n && (c = new i(n,o.y + (n - o.x) / (c.x - o.x) * (c.y - o.y))._round()),
                o.y >= s && c.y >= s || (o.y >= s ? o = new i(o.x + (s - o.y) / (c.y - o.y) * (c.x - o.x),s)._round() : c.y >= s && (c = new i(o.x + (s - o.y) / (c.y - o.y) * (c.x - o.x),s)._round()),
                u && o.equals(u[u.length - 1]) || (u = [o],
                a.push(u)),
                u.push(c)))));
            }
        }
        return a
    }
    Bi(Hp, "Anchor");
    const sf = 1e20;
    function af(t, e, r, n, i, s, a, o, l) {
        for (let u = e; u < e + n; u++)
            of(t, r * s + u, s, i, a, o, l);
        for (let u = r; u < r + i; u++)
            of(t, u * s + e, 1, n, a, o, l);
    }
    function of(t, e, r, n, i, s, a) {
        s[0] = 0,
        a[0] = -sf,
        a[1] = sf,
        i[0] = t[e];
        for (let o = 1, l = 0, u = 0; o < n; o++) {
            i[o] = t[e + o * r];
            const n = o * o;
            do {
                const t = s[l];
                u = (i[o] - i[t] + n - t * t) / (o - t) / 2;
            } while (u <= a[l] && --l > -1);
            l++,
            s[l] = o,
            a[l] = u,
            a[l + 1] = sf;
        }
        for (let o = 0, l = 0; o < n; o++) {
            for (; a[l + 1] < o; )
                l++;
            const n = s[l]
              , u = o - n;
            t[e + o * r] = i[n] + u * u;
        }
    }
    const lf = {
        none: 0,
        ideographs: 1,
        all: 2
    };
    class uf {
        constructor(t, e, r) {
            this.requestManager = t,
            this.localGlyphMode = e,
            this.localFontFamily = r,
            this.entries = {},
            this.localGlyphs = {
                200: {},
                400: {},
                500: {},
                900: {}
            };
        }
        setURL(t) {
            this.url = t;
        }
        setURLData(t) {
            this.urlData = t;
        }
        getGlyphs(t, e) {
            const r = [];
            for (const e in t)
                for (const n of t[e])
                    r.push({
                        stack: e,
                        id: n
                    });
            g(r, (({stack: t, id: e},r)=>{
                let n = this.entries[t];
                n || (n = this.entries[t] = {
                    glyphs: {},
                    requests: {},
                    ranges: {},
                    ascender: void 0,
                    descender: void 0
                });
                let i = n.glyphs[e];
                if (void 0 !== i)
                    return void r(null, {
                        stack: t,
                        id: e,
                        glyph: i
                    });
                if (i = this._tinySDF(n, t, e),
                i)
                    return n.glyphs[e] = i,
                    void r(null, {
                        stack: t,
                        id: e,
                        glyph: i
                    });
                const s = Math.floor(e / 256);
                if (256 * s > 65535)
                    return void r(new Error("glyphs > 65535 not supported"));
                if (n.ranges[s])
                    return void r(null, {
                        stack: t,
                        id: e,
                        glyph: i
                    });
                let a = n.requests[s];
                if (!a) {
                    a = n.requests[s] = [];
                    let e = this.url;
                    "Microsoft YaHei Regular" != t && (e = this.urlData && this.urlData[t] || this.url),
                    uf.loadGlyphRange(t, s, e, this.requestManager, ((t,e)=>{
                        if (e) {
                            n.ascender = e.ascender,
                            n.descender = e.descender;
                            for (const t in e.glyphs)
                                this._doesCharSupportLocalGlyph(+t) || (n.glyphs[+t] = e.glyphs[+t],
                                t >= 19968 && t <= 40943 && (n.glyphs[+t].metrics.top = -4));
                            n.ranges[s] = !0;
                        }
                        for (const r of a)
                            r(t, e);
                        delete n.requests[s];
                    }
                    ));
                }
                a.push(((n,i)=>{
                    n ? r(n) : i && r(null, {
                        stack: t,
                        id: e,
                        glyph: i.glyphs[e] || null
                    });
                }
                ));
            }
            ), ((t,r)=>{
                if (t)
                    e(t);
                else if (r) {
                    const t = {};
                    for (const {stack: e, id: n, glyph: i} of r)
                        void 0 === t[e] && (t[e] = {}),
                        void 0 === t[e].glyphs && (t[e].glyphs = {}),
                        t[e].glyphs[n] = i && {
                            id: i.id,
                            bitmap: i.bitmap.clone(),
                            metrics: i.metrics
                        },
                        t[e].ascender = this.entries[e].ascender,
                        t[e].descender = this.entries[e].descender;
                    e(null, t);
                }
            }
            ));
        }
        _doesCharSupportLocalGlyph(t) {
            return this.localGlyphMode !== lf.none && (this.localGlyphMode === lf.all ? !!this.localFontFamily : !!this.localFontFamily && (Wi(t) || es(t) || qi(t) || Ni(t) || $i(t)))
        }
        _tinySDF(t, e, r) {
            const n = this.localFontFamily;
            if (!n || !this._doesCharSupportLocalGlyph(r))
                return;
            let i = t.tinySDF;
            if (!i) {
                let r = "400";
                /bold/i.test(e) ? r = "900" : /medium/i.test(e) ? r = "500" : /light/i.test(e) && (r = "200"),
                i = t.tinySDF = new uf.TinySDF({
                    fontFamily: n,
                    fontWeight: r,
                    fontSize: 48,
                    buffer: 6,
                    radius: 16,
                    cutoff: .23
                }),
                i.fontWeight = r;
            }
            if (this.localGlyphs[i.fontWeight][r])
                return this.localGlyphs[i.fontWeight][r];
            const s = String.fromCharCode(r)
              , {data: a, width: o, height: l, glyphWidth: u, glyphHeight: c, glyphLeft: h, glyphTop: p, glyphAdvance: f} = i.draw(s);
            return this.localGlyphs[i.fontWeight][r] = {
                id: r,
                bitmap: new Wu({
                    width: o,
                    height: l
                },a),
                metrics: {
                    width: u / 2,
                    height: c / 2,
                    left: h / 2,
                    top: p / 2 - 27 + (r >= 19968 && r <= 40943 ? 4 : 0),
                    advance: f / 2,
                    localGlyph: !0
                }
            }
        }
    }
    function cf(t, e, r, n) {
        const s = []
          , a = t.image
          , o = a.pixelRatio
          , l = a.paddedRect.w - 2
          , u = a.paddedRect.h - 2
          , c = t.right - t.left
          , h = t.bottom - t.top
          , p = a.stretchX || [[0, l]]
          , f = a.stretchY || [[0, u]]
          , d = (t,e)=>t + e[1] - e[0]
          , y = p.reduce(d, 0)
          , m = f.reduce(d, 0)
          , g = l - y
          , x = u - m;
        let v = 0
          , b = y
          , _ = 0
          , w = m
          , A = 0
          , k = g
          , z = 0
          , S = x;
        if (a.content && n) {
            const t = a.content;
            v = hf(p, 0, t[0]),
            _ = hf(f, 0, t[1]),
            b = hf(p, t[0], t[2]),
            w = hf(f, t[1], t[3]),
            A = t[0] - v,
            z = t[1] - _,
            k = t[2] - t[0] - b,
            S = t[3] - t[1] - w;
        }
        const M = (n,s,l,u)=>{
            const p = ff(n.stretch - v, b, c, t.left)
              , f = df(n.fixed - A, k, n.stretch, y)
              , d = ff(s.stretch - _, w, h, t.top)
              , g = df(s.fixed - z, S, s.stretch, m)
              , x = ff(l.stretch - v, b, c, t.left)
              , M = df(l.fixed - A, k, l.stretch, y)
              , I = ff(u.stretch - _, w, h, t.top)
              , T = df(u.fixed - z, S, u.stretch, m)
              , B = new i(p,d)
              , C = new i(x,d)
              , V = new i(x,I)
              , P = new i(p,I)
              , D = new i(f / o,g / o)
              , E = new i(M / o,T / o)
              , F = e * Math.PI / 180;
            if (F) {
                const t = Math.sin(F)
                  , e = Math.cos(F)
                  , r = [e, -t, t, e];
                B._matMult(r),
                C._matMult(r),
                P._matMult(r),
                V._matMult(r);
            }
            const L = n.stretch + n.fixed
              , R = s.stretch + s.fixed;
            return {
                tl: B,
                tr: C,
                bl: P,
                br: V,
                tex: {
                    x: a.paddedRect.x + 1 + L,
                    y: a.paddedRect.y + 1 + R,
                    w: l.stretch + l.fixed - L,
                    h: u.stretch + u.fixed - R
                },
                writingMode: void 0,
                glyphOffset: [0, 0],
                sectionIndex: 0,
                pixelOffsetTL: D,
                pixelOffsetBR: E,
                minFontScaleX: k / o / c,
                minFontScaleY: S / o / h,
                isSDF: r
            }
        }
        ;
        if (n && (a.stretchX || a.stretchY)) {
            const t = pf(p, g, y)
              , e = pf(f, x, m);
            for (let r = 0; r < t.length - 1; r++) {
                const n = t[r]
                  , i = t[r + 1];
                for (let t = 0; t < e.length - 1; t++)
                    s.push(M(n, e[t], i, e[t + 1]));
            }
        } else
            s.push(M({
                fixed: 0,
                stretch: -1
            }, {
                fixed: 0,
                stretch: -1
            }, {
                fixed: 0,
                stretch: l + 1
            }, {
                fixed: 0,
                stretch: u + 1
            }));
        return s
    }
    function hf(t, e, r) {
        let n = 0;
        for (const i of t)
            n += Math.max(e, Math.min(r, i[1])) - Math.max(e, Math.min(r, i[0]));
        return n
    }
    function pf(t, e, r) {
        const n = [{
            fixed: -1,
            stretch: 0
        }];
        for (const [e,r] of t) {
            const t = n[n.length - 1];
            n.push({
                fixed: e - t.stretch,
                stretch: t.stretch
            }),
            n.push({
                fixed: e - t.stretch,
                stretch: t.stretch + (r - e)
            });
        }
        return n.push({
            fixed: e + 1,
            stretch: r
        }),
        n
    }
    function ff(t, e, r, n) {
        return t / e * r + n
    }
    function df(t, e, r, n) {
        return t - e * r / n
    }
    function yf(t, e, r, n) {
        const i = e + t.positionedLines[n].lineOffset;
        return 0 === n ? r + i / 2 : r + (i + (e + t.positionedLines[n - 1].lineOffset)) / 2
    }
    uf.loadGlyphRange = function(t, e, r, n, i) {
        const s = 256 * e
          , a = s + 255
          , o = n.transformRequest(n.normalizeGlyphsURL(r).replace("{fontstack}", t).replace("{range}", `${s}-${a}`), zt.Glyphs);
        Vt(o, ((t,e)=>{
            if (t)
                i(t);
            else if (e) {
                const t = {}
                  , r = function(t) {
                    return new op(t).readFields(Mp, {})
                }(e);
                for (const e of r.glyphs)
                    t[e.id] = e;
                i(null, {
                    glyphs: t,
                    ascender: r.ascender,
                    descender: r.descender
                });
            }
        }
        ));
    }
    ,
    uf.TinySDF = class {
        constructor({fontSize: t=24, buffer: e=3, radius: r=8, cutoff: n=.25, fontFamily: i="sans-serif", fontWeight: s="normal", fontStyle: a="normal"}) {
            this.buffer = e,
            this.cutoff = n,
            this.radius = r;
            const o = this.size = t + 4 * e
              , l = this._createCanvas(o)
              , u = this.ctx = l.getContext("2d", {
                willReadFrequently: !0
            });
            u.font = `${a} ${s} ${t}px ${i}`,
            u.textBaseline = "alphabetic",
            u.textAlign = "left",
            u.fillStyle = "black",
            this.gridOuter = new Float64Array(o * o),
            this.gridInner = new Float64Array(o * o),
            this.f = new Float64Array(o),
            this.z = new Float64Array(o + 1),
            this.v = new Uint16Array(o);
        }
        _createCanvas(t) {
            const e = document.createElement("canvas");
            return e.width = e.height = t,
            e
        }
        draw(t) {
            const {width: e, actualBoundingBoxAscent: r, actualBoundingBoxDescent: n, actualBoundingBoxLeft: i, actualBoundingBoxRight: s} = this.ctx.measureText(t);
            let a, o, l, u, c;
            r ? (a = Math.floor(r),
            o = Math.min(this.size - this.buffer, Math.ceil(s - i)),
            l = Math.min(this.size - this.buffer, Math.ceil(r) + Math.ceil(n)),
            u = o + 2 * this.buffer,
            c = l + 2 * this.buffer) : (a = Math.round(this.size / 2 * (navigator.userAgent.indexOf("Gecko/") >= 0 ? 1.2 : 1)),
            o = this.size - this.buffer,
            l = this.size - this.buffer,
            u = o,
            c = l);
            const h = u * c
              , p = new Uint8ClampedArray(h)
              , f = {
                data: p,
                width: u,
                height: c,
                glyphWidth: o,
                glyphHeight: l,
                glyphTop: a,
                glyphLeft: 0,
                glyphAdvance: e
            };
            if (0 === o || 0 === l)
                return f;
            const {ctx: d, buffer: y, gridInner: m, gridOuter: g} = this;
            d.clearRect(y, y, o, l),
            d.fillText(t, y, y + a + 1);
            const x = d.getImageData(y, y, o, l);
            g.fill(sf, 0, h),
            m.fill(0, 0, h);
            for (let t = 0; t < l; t++)
                for (let e = 0; e < o; e++) {
                    const r = x.data[4 * (t * o + e) + 3] / 255;
                    if (0 === r)
                        continue;
                    const n = (t + y) * u + e + y;
                    if (1 === r)
                        g[n] = 0,
                        m[n] = sf;
                    else {
                        const t = .5 - r;
                        g[n] = t > 0 ? t * t : 0,
                        m[n] = t < 0 ? t * t : 0;
                    }
                }
            af(g, 0, 0, u, c, u, this.f, this.v, this.z),
            af(m, y, y, o, l, u, this.f, this.v, this.z);
            for (let t = 0; t < h; t++) {
                const e = Math.sqrt(g[t]) - Math.sqrt(m[t]);
                p[t] = Math.round(255 - 255 * (e / this.radius + this.cutoff));
            }
            return f
        }
    }
    ;
    class mf {
        constructor(t=[], e=gf) {
            if (this.data = t,
            this.length = this.data.length,
            this.compare = e,
            this.length > 0)
                for (let t = (this.length >> 1) - 1; t >= 0; t--)
                    this._down(t);
        }
        push(t) {
            this.data.push(t),
            this.length++,
            this._up(this.length - 1);
        }
        pop() {
            if (0 === this.length)
                return;
            const t = this.data[0]
              , e = this.data.pop();
            return this.length--,
            this.length > 0 && (this.data[0] = e,
            this._down(0)),
            t
        }
        peek() {
            return this.data[0]
        }
        _up(t) {
            const {data: e, compare: r} = this
              , n = e[t];
            for (; t > 0; ) {
                const i = t - 1 >> 1
                  , s = e[i];
                if (r(n, s) >= 0)
                    break;
                e[t] = s,
                t = i;
            }
            e[t] = n;
        }
        _down(t) {
            const {data: e, compare: r} = this
              , n = this.length >> 1
              , i = e[t];
            for (; t < n; ) {
                let n = 1 + (t << 1)
                  , s = e[n];
                const a = n + 1;
                if (a < this.length && r(e[a], s) < 0 && (n = a,
                s = e[a]),
                r(s, i) >= 0)
                    break;
                e[t] = s,
                t = n;
            }
            e[t] = i;
        }
    }
    function gf(t, e) {
        return t < e ? -1 : t > e ? 1 : 0
    }
    function xf(t, e=1, r=!1) {
        let n = 1 / 0
          , s = 1 / 0
          , a = -1 / 0
          , o = -1 / 0;
        const l = t[0];
        for (let t = 0; t < l.length; t++) {
            const e = l[t];
            (!t || e.x < n) && (n = e.x),
            (!t || e.y < s) && (s = e.y),
            (!t || e.x > a) && (a = e.x),
            (!t || e.y > o) && (o = e.y);
        }
        const u = Math.min(a - n, o - s);
        let c = u / 2;
        const h = new mf([],vf);
        if (0 === u)
            return new i(n,s);
        for (let e = n; e < a; e += u)
            for (let r = s; r < o; r += u)
                h.push(new bf(e + c,r + c,c,t));
        let p = function(t) {
            let e = 0
              , r = 0
              , n = 0;
            const i = t[0];
            for (let t = 0, s = i.length, a = s - 1; t < s; a = t++) {
                const s = i[t]
                  , o = i[a]
                  , l = s.x * o.y - o.x * s.y;
                r += (s.x + o.x) * l,
                n += (s.y + o.y) * l,
                e += 3 * l;
            }
            return new bf(r / e,n / e,0,t)
        }(t)
          , f = h.length;
        for (; h.length; ) {
            const n = h.pop();
            (n.d > p.d || !p.d) && (p = n,
            r && console.log("found best %d after %d probes", Math.round(1e4 * n.d) / 1e4, f)),
            n.max - p.d <= e || (c = n.h / 2,
            h.push(new bf(n.p.x - c,n.p.y - c,c,t)),
            h.push(new bf(n.p.x + c,n.p.y - c,c,t)),
            h.push(new bf(n.p.x - c,n.p.y + c,c,t)),
            h.push(new bf(n.p.x + c,n.p.y + c,c,t)),
            f += 4);
        }
        return r && (console.log(`num probes: ${f}`),
        console.log(`best distance: ${p.d}`)),
        p.p
    }
    function vf(t, e) {
        return e.max - t.max
    }
    function bf(t, e, r, n) {
        this.p = new i(t,e),
        this.h = r,
        this.d = function(t, e) {
            let r = !1
              , n = 1 / 0;
            for (let i = 0; i < e.length; i++) {
                const s = e[i];
                for (let e = 0, i = s.length, a = i - 1; e < i; a = e++) {
                    const i = s[e]
                      , o = s[a];
                    i.y > t.y != o.y > t.y && t.x < (o.x - i.x) * (t.y - i.y) / (o.y - i.y) + i.x && (r = !r),
                    n = Math.min(n, Dl(t, i, o));
                }
            }
            return (r ? 1 : -1) * Math.sqrt(n)
        }(this.p, n),
        this.max = this.d + this.h * Math.SQRT2;
    }
    const _f = Number.POSITIVE_INFINITY
      , wf = Math.sqrt(2);
    function Af(t, e) {
        return e[1] !== _f ? function(t, e, r) {
            let n = 0
              , i = 0;
            switch (e = Math.abs(e),
            r = Math.abs(r),
            t) {
            case "top-right":
            case "top-left":
            case "top":
                i = r - 7;
                break;
            case "bottom-right":
            case "bottom-left":
            case "bottom":
                i = 7 - r;
            }
            switch (t) {
            case "top-right":
            case "bottom-right":
            case "right":
                n = -e;
                break;
            case "top-left":
            case "bottom-left":
            case "left":
                n = e;
            }
            return [n, i]
        }(t, e[0], e[1]) : function(t, e) {
            let r = 0
              , n = 0;
            e < 0 && (e = 0);
            const i = e / wf;
            switch (t) {
            case "top-right":
            case "top-left":
                n = i - 7;
                break;
            case "bottom-right":
            case "bottom-left":
                n = 7 - i;
                break;
            case "bottom":
                n = 7 - e;
                break;
            case "top":
                n = e - 7;
            }
            switch (t) {
            case "top-right":
            case "bottom-right":
                r = -i;
                break;
            case "top-left":
            case "bottom-left":
                r = i;
                break;
            case "left":
                r = e;
                break;
            case "right":
                r = -e;
            }
            return [r, n]
        }(t, e[0])
    }
    function kf(t, e, r, n, i, s, a, o, l, u) {
        t.createArrays(),
        t.tilePixelRatio = bo / (512 * t.overscaling),
        t.compareText = {},
        t.iconsNeedLinear = !1;
        const c = t.layers[0].layout
          , h = t.layers[0]._unevaluatedLayout._values
          , p = {};
        if ("composite" === t.textSizeData.kind) {
            const {minZoom: e, maxZoom: r} = t.textSizeData;
            p.compositeTextSizes = [h["text-size"].possiblyEvaluate(new Ts(e), o), h["text-size"].possiblyEvaluate(new Ts(r), o)];
        }
        if ("composite" === t.iconSizeData.kind) {
            const {minZoom: e, maxZoom: r} = t.iconSizeData;
            p.compositeIconSizes = [h["icon-size"].possiblyEvaluate(new Ts(e), o), h["icon-size"].possiblyEvaluate(new Ts(r), o)];
        }
        p.layoutTextSize = h["text-size"].possiblyEvaluate(new Ts(l + 1), o),
        p.layoutIconSize = h["icon-size"].possiblyEvaluate(new Ts(l + 1), o),
        p.textMaxSize = h["text-size"].possiblyEvaluate(new Ts(18), o);
        const f = "map" === c.get("text-rotation-alignment") && "point" !== c.get("symbol-placement")
          , d = c.get("text-size");
        for (const s of t.features) {
            const l = c.get("text-font").evaluate(s, {}, o).join(",")
              , h = d.evaluate(s, {}, o)
              , y = p.layoutTextSize.evaluate(s, {}, o)
              , m = (p.layoutIconSize.evaluate(s, {}, o),
            {
                horizontal: {},
                vertical: void 0
            })
              , g = s.text;
            let x, v = [0, 0];
            if (g) {
                const n = g.toString()
                  , a = c.get("text-letter-spacing").evaluate(s, {}, o) * Hh
                  , u = c.get("text-line-height").evaluate(s, {}, o) * Hh
                  , p = cs(n) ? a : 0
                  , d = c.get("text-anchor").evaluate(s, {}, o)
                  , x = c.get("text-variable-anchor");
                if (!x) {
                    const t = c.get("text-radial-offset").evaluate(s, {}, o);
                    v = t ? Af(d, [t * Hh, _f]) : c.get("text-offset").evaluate(s, {}, o).map((t=>t * Hh));
                }
                let b = f ? "center" : c.get("text-justify").evaluate(s, {}, o);
                const _ = c.get("symbol-placement")
                  , w = "point" === _
                  , A = "point" === _ ? c.get("text-max-width").evaluate(s, {}, o) * Hh : 0
                  , k = s=>{
                    t.allowVerticalPlacement && us(n) && (m.vertical = Fp(g, e, r, i, l, A, u, d, s, p, v, Pp.vertical, !0, _, y, h));
                }
                ;
                if (!f && x) {
                    const t = "auto" === b ? x.map((t=>zf(t))) : [b];
                    let n = !1;
                    for (let s = 0; s < t.length; s++) {
                        const a = t[s];
                        if (!m.horizontal[a])
                            if (n)
                                m.horizontal[a] = m.horizontal[0];
                            else {
                                const t = Fp(g, e, r, i, l, A, u, "center", a, p, v, Pp.horizontal, !1, _, y, h);
                                t && (m.horizontal[a] = t,
                                n = 1 === t.positionedLines.length);
                            }
                    }
                    k("left");
                } else {
                    if ("auto" === b && (b = zf(d)),
                    w || c.get("text-writing-mode").indexOf("horizontal") >= 0 || !us(n)) {
                        const t = Fp(g, e, r, i, l, A, u, d, b, p, v, Pp.horizontal, !1, _, y, h);
                        t && (m.horizontal[b] = t);
                    }
                    k("point" === _ ? "left" : b);
                }
            }
            let b = !1;
            if (s.icon && s.icon.name) {
                const e = n[s.icon.name];
                e && (x = Xp(i[s.icon.name], c.get("icon-offset").evaluate(s, {}, o), c.get("icon-anchor").evaluate(s, {}, o)),
                b = e.sdf,
                void 0 === t.sdfIcons ? t.sdfIcons = e.sdf : t.sdfIcons !== e.sdf && B("Style sheet warning: Cannot mix SDF and non-SDF icons in one buffer"),
                (e.pixelRatio !== t.pixelRatio || 0 !== c.get("icon-rotate").constantOr(1)) && (t.iconsNeedLinear = !0));
            }
            const _ = Tf(m.horizontal) || m.vertical;
            t.iconsInText || (t.iconsInText = !!_ && _.iconsInText),
            (_ || x) && Sf(t, s, m, x, n, p, y, 0, v, b, a, o, u);
        }
        s && t.generateCollisionDebugBuffers(l, t.collisionBoxArray);
    }
    function zf(t) {
        switch (t) {
        case "right":
        case "top-right":
        case "bottom-right":
            return "right";
        case "left":
        case "top-left":
        case "bottom-left":
            return "left"
        }
        return "center"
    }
    function Sf(t, e, r, n, i, s, a, o, u, c, h, p, f) {
        let d = s.textMaxSize.evaluate(e, {}, p);
        void 0 === d && (d = a);
        const y = t.layers[0].layout
          , m = y.get("icon-offset").evaluate(e, {}, p)
          , g = Tf(r.horizontal) || r.vertical
          , x = "globe" === f.name
          , v = a / 24
          , b = t.tilePixelRatio * d / 24
          , _ = (T = t.overscaling,
        t.zoom > 18 && T > 2 && (T >>= 1),
        Math.max(bo / (512 * T), 1) * y.get("symbol-spacing"))
          , w = y.get("text-padding") * t.tilePixelRatio
          , A = y.get("icon-padding") * t.tilePixelRatio
          , k = l(y.get("text-max-angle"))
          , z = "map" === y.get("text-rotation-alignment") && "point" !== y.get("symbol-placement")
          , S = "map" === y.get("icon-rotation-alignment") && "point" !== y.get("symbol-placement")
          , M = y.get("symbol-placement")
          , I = _ / 2;
        var T;
        const C = y.get("icon-text-fit");
        let V;
        n && "none" !== C && (t.allowVerticalPlacement && r.vertical && (V = Yp(n, r.vertical, C, y.get("icon-text-fit-padding"), m, v)),
        g && (n = Yp(n, g, C, y.get("icon-text-fit-padding"), m, v)));
        const P = (a,o,l)=>{
            if (o.x < 0 || o.x >= bo || o.y < 0 || o.y >= bo)
                return;
            let d = null;
            if (x) {
                const {x: t, y: e, z: r} = f.projectTilePoint(o.x, o.y, l);
                d = {
                    anchor: new Hp(t,e,r,0,void 0),
                    up: f.upVector(l, o.x, o.y)
                };
            }
            !function(t, e, r, n, i, s, a, o, l, u, c, h, p, f, d, y, m, g, x, v, b, _, w, A, k) {
                const z = t.addToLineVertexArray(e, n);
                let S, M, I, T, C, V, P, D = 0, E = 0, F = 0, L = 0, R = -1, j = -1;
                const U = {};
                let O = $a("");
                const $ = r ? r.anchor : e;
                let q = 0
                  , N = 0;
                if (void 0 === l._unevaluatedLayout.getValue("text-radial-offset") ? [q,N] = l.layout.get("text-offset").evaluate(b, {}, k).map((t=>t * Hh)) : (q = l.layout.get("text-radial-offset").evaluate(b, {}, k) * Hh,
                N = _f),
                t.allowVerticalPlacement && i.vertical) {
                    const t = i.vertical;
                    if (d)
                        V = Cf(t),
                        o && (P = Cf(o));
                    else {
                        const r = l.layout.get("text-rotate").evaluate(b, {}, k) + 90;
                        I = Bf(u, $, e, c, h, p, t, f, r, y),
                        o && (T = Bf(u, $, e, c, h, p, o, g, r));
                    }
                }
                if (s) {
                    const n = l.layout.get("icon-rotate").evaluate(b, {}, k)
                      , i = "none" !== l.layout.get("icon-text-fit")
                      , a = cf(s, n, w, i)
                      , f = o ? cf(o, n, w, i) : void 0;
                    M = Bf(u, $, e, c, h, p, s, g, n),
                    D = 4 * a.length;
                    const d = t.iconSizeData;
                    let y = null;
                    "source" === d.kind ? (y = [Kh * l.layout.get("icon-size").evaluate(b, {}, k)],
                    y[0] > Mf && B(`${t.layerIds[0]}: Value for "icon-size" is >= 255. Reduce your "icon-size".`)) : "composite" === d.kind && (y = [Kh * _.compositeIconSizes[0].evaluate(b, {}, k), Kh * _.compositeIconSizes[1].evaluate(b, {}, k)],
                    (y[0] > Mf || y[1] > Mf) && B(`${t.layerIds[0]}: Value for "icon-size" is >= 255. Reduce your "icon-size".`)),
                    t.addSymbols(t.icon, a, y, v, x, b, !1, r, e, z.lineStartIndex, z.lineLength, -1, A, k),
                    R = t.icon.placedSymbolArray.length - 1,
                    f && (E = 4 * f.length,
                    t.addSymbols(t.icon, f, y, v, x, b, Pp.vertical, r, e, z.lineStartIndex, z.lineLength, -1, A, k),
                    j = t.icon.placedSymbolArray.length - 1);
                }
                for (const n in i.horizontal) {
                    const s = i.horizontal[n];
                    S || (O = $a(s.text),
                    d ? C = Cf(s) : S = Bf(u, $, e, c, h, p, s, f, l.layout.get("text-rotate").evaluate(b, {}, k), y));
                    const o = 1 === s.positionedLines.length;
                    if (F += If(t, r, e, s, a, l, d, b, y, z, i.vertical ? Pp.horizontal : Pp.horizontalOnly, o ? Object.keys(i.horizontal) : [n], U, R, _, A, k),
                    o)
                        break
                }
                i.vertical && (L += If(t, r, e, i.vertical, a, l, d, b, y, z, Pp.vertical, ["vertical"], U, j, _, A, k));
                let Z = -1;
                const G = (t,e)=>t ? Math.max(t, e) : e;
                Z = G(C, Z),
                Z = G(V, Z),
                Z = G(P, Z);
                const X = Z > -1 ? 1 : 0;
                t.glyphOffsetArray.length >= Nd.MAX_GLYPHS && B("Too many glyphs being rendered in a tile. See https://github.com/sgmap/sgmap-js/issues/2907"),
                void 0 !== b.sortKey && t.addToSortKeyRanges(t.symbolInstances.length, b.sortKey),
                t.symbolInstances.emplaceBack($.x, $.y, $.z, e.x, e.y, U.right >= 0 ? U.right : -1, U.center >= 0 ? U.center : -1, U.left >= 0 ? U.left : -1, U.vertical >= 0 ? U.vertical : -1, R, j, O, void 0 !== S ? S : t.collisionBoxArray.length, void 0 !== S ? S + 1 : t.collisionBoxArray.length, void 0 !== I ? I : t.collisionBoxArray.length, void 0 !== I ? I + 1 : t.collisionBoxArray.length, void 0 !== M ? M : t.collisionBoxArray.length, void 0 !== M ? M + 1 : t.collisionBoxArray.length, T || t.collisionBoxArray.length, T ? T + 1 : t.collisionBoxArray.length, c, F, L, D, E, X, 0, q, N, Z);
            }(t, o, d, a, r, n, i, V, t.layers[0], t.collisionBoxArray, e.index, e.sourceLayerIndex, t.index, w, z, u, 0, A, S, m, e, s, c, h, p);
        }
        ;
        if ("line" === M)
            for (const i of nf(e.geometry, 0, 0, bo, bo)) {
                const e = ef(i, _, k, r.vertical || g, n, 24, b, t.overscaling, bo);
                for (const r of e) {
                    const e = g;
                    e && Vf(t, e.text, I, r) || P(i, r, p);
                }
            }
        else if ("line-center" === M) {
            for (const t of e.geometry)
                if (t.length > 1) {
                    const e = tf(t, k, r.vertical || g, n, 24, b);
                    e && P(t, e, p);
                }
        } else if ("Polygon" === e.type)
            for (const t of Rc(e.geometry, 0)) {
                const e = xf(t, 16);
                P(t[0], new Hp(e.x,e.y,0,0,void 0), p);
            }
        else if ("LineString" === e.type)
            for (const t of e.geometry)
                P(t, new Hp(t[0].x,t[0].y,0,0,void 0), p);
        else if ("Point" === e.type)
            for (const t of e.geometry)
                for (const e of t)
                    P([e], new Hp(e.x,e.y,0,0,void 0), p);
    }
    const Mf = 32640;
    function If(t, e, r, n, s, a, o, l, u, c, h, p, f, d, y, m, g) {
        const x = function(t, e, r, n, s, a, o, l) {
            const u = [];
            if (0 === e.positionedLines.length)
                return u;
            const c = n.layout.get("text-rotate").evaluate(a, {}) * Math.PI / 180
              , h = function(t) {
                const e = t[0]
                  , r = t[1]
                  , n = e * r;
                return n > 0 ? [e, -r] : n < 0 ? [-e, r] : 0 === e ? [r, e] : [r, -e]
            }(r);
            let p = Math.abs(e.top - e.bottom);
            for (const t of e.positionedLines)
                p -= t.lineOffset;
            const f = e.positionedLines.length
              , d = p / f;
            let y = e.top - r[1];
            for (let t = 0; t < f; ++t) {
                const n = e.positionedLines[t];
                y = yf(e, d, y, t);
                for (const t of n.positionedGlyphs) {
                    if (!t.rect)
                        continue;
                    const n = t.rect || {};
                    let a = 4
                      , p = !0
                      , f = 1
                      , d = 0;
                    if (t.imageName) {
                        const e = o[t.imageName];
                        if (!e)
                            continue;
                        if (e.sdf) {
                            B("SDF images are not supported in formatted text and will be ignored.");
                            continue
                        }
                        p = !1,
                        f = e.pixelRatio,
                        a = 1 / f;
                    }
                    const m = (s || l) && t.vertical
                      , g = t.metrics.advance * t.scale / 2
                      , x = t.metrics
                      , v = t.rect;
                    if (null === v)
                        continue;
                    l && e.verticalizable && (d = t.imageName ? g - t.metrics.width * t.scale / 2 : 0);
                    const b = s ? [t.x + g, t.y] : [0, 0];
                    let _ = [0, 0]
                      , w = [0, 0]
                      , A = !1;
                    s || (m ? (w = [t.x + g + h[0], t.y + h[1] - d],
                    A = !0) : _ = [t.x + g + r[0], t.y + r[1] - d]);
                    const k = v.w * t.scale / (f * (t.localGlyph ? 2 : 1))
                      , z = v.h * t.scale / (f * (t.localGlyph ? 2 : 1));
                    let S, M, I, T;
                    if (m) {
                        const e = t.y - y
                          , r = new i(-g,g - e)
                          , n = -Math.PI / 2
                          , s = new i(...w);
                        S = new i(-g + _[0],_[1]),
                        S._rotateAround(n, r)._add(s),
                        S.x += -e + g,
                        S.y -= (x.left - a) * t.scale;
                        const o = t.imageName ? x.advance * t.scale : Hh * t.scale
                          , l = String.fromCharCode(t.glyph);
                        np(l) ? S.x += (1 - a) * t.scale : ip(l) ? S.x += o - x.height * t.scale + (-a - 1) * t.scale : S.x += t.imageName || x.width + 2 * a === v.w && x.height + 2 * a === v.h ? (o - z) / 2 : (o - (x.height + 2 * a) * t.scale) / 2,
                        M = new i(S.x,S.y - k),
                        I = new i(S.x + z,S.y),
                        T = new i(S.x + z,S.y - k);
                    } else {
                        const e = (x.left - a) * t.scale - g + _[0]
                          , r = (-x.top - a) * t.scale + _[1]
                          , n = e + k
                          , s = r + z;
                        S = new i(e,r),
                        M = new i(n,r),
                        I = new i(e,s),
                        T = new i(n,s);
                    }
                    if (c) {
                        let t;
                        t = s ? new i(0,0) : A ? new i(h[0],h[1]) : new i(r[0],r[1]),
                        S._rotateAround(c, t),
                        M._rotateAround(c, t),
                        I._rotateAround(c, t),
                        T._rotateAround(c, t);
                    }
                    const C = new i(0,0)
                      , V = new i(0,0);
                    u.push({
                        tl: S,
                        tr: M,
                        bl: I,
                        br: T,
                        tex: n,
                        writingMode: e.writingMode,
                        glyphOffset: b,
                        sectionIndex: t.sectionIndex,
                        isSDF: p,
                        pixelOffsetTL: C,
                        pixelOffsetBR: V,
                        minFontScaleX: 0,
                        minFontScaleY: 0
                    });
                }
            }
            return u
        }(0, n, u, a, o, l, s, t.allowVerticalPlacement)
          , v = t.textSizeData;
        let b = null;
        "source" === v.kind ? (b = [Kh * a.layout.get("text-size").evaluate(l, {}, g)],
        b[0] > Mf && B(`${t.layerIds[0]}: Value for "text-size" is >= 255. Reduce your "text-size".`)) : "composite" === v.kind && (b = [Kh * y.compositeTextSizes[0].evaluate(l, {}, g), Kh * y.compositeTextSizes[1].evaluate(l, {}, g)],
        (b[0] > Mf || b[1] > Mf) && B(`${t.layerIds[0]}: Value for "text-size" is >= 255. Reduce your "text-size".`)),
        t.addSymbols(t.text, x, b, u, o, l, h, e, r, c.lineStartIndex, c.lineLength, d, m, g);
        for (const e of p)
            f[e] = t.text.placedSymbolArray.length - 1;
        return 4 * x.length
    }
    function Tf(t) {
        for (const e in t)
            return t[e];
        return null
    }
    function Bf(t, e, r, n, s, a, o, u, c, h) {
        let p = o.top
          , f = o.bottom
          , d = o.left
          , y = o.right;
        const m = o.collisionPadding;
        if (m && (d -= m[0],
        p -= m[1],
        y += m[2],
        f += m[3]),
        c) {
            const t = new i(d,p)
              , e = new i(y,p)
              , r = new i(d,f)
              , n = new i(y,f)
              , s = l(c);
            let a = new i(0,0);
            h && (a = new i(h[0],h[1])),
            t._rotateAround(s, a),
            e._rotateAround(s, a),
            r._rotateAround(s, a),
            n._rotateAround(s, a),
            d = Math.min(t.x, e.x, r.x, n.x),
            y = Math.max(t.x, e.x, r.x, n.x),
            p = Math.min(t.y, e.y, r.y, n.y),
            f = Math.max(t.y, e.y, r.y, n.y);
        }
        return t.emplaceBack(e.x, e.y, e.z, r.x, r.y, d, p, y, f, u, n, s, a),
        t.length - 1
    }
    function Cf(t) {
        t.collisionPadding && (t.top -= t.collisionPadding[1],
        t.bottom += t.collisionPadding[3]);
        const e = t.bottom - t.top;
        return e > 0 ? Math.max(10, e) : null
    }
    function Vf(t, e, r, n) {
        const i = t.compareText;
        if (e in i) {
            const t = i[e];
            for (let e = t.length - 1; e >= 0; e--)
                if (n.dist(t[e]) < r)
                    return !0
        } else
            i[e] = [];
        return i[e].push(n),
        !1
    }
    const Pf = Ys([{
        type: "Float32",
        name: "a_globe_pos",
        components: 3
    }, {
        type: "Float32",
        name: "a_uv",
        components: 2
    }])
      , {members: Df} = Pf
      , Ef = Ys([{
        name: "a_pos_3",
        components: 3,
        type: "Int16"
    }]);
    var Ff = Ys([{
        name: "a_pos",
        type: "Int16",
        components: 2
    }]);
    const Lf = bo / Math.PI / 2
      , Rf = 2 * Jo(1, 0) * Lf * Math.PI
      , jf = 64
      , Uf = [jf, 32, 16]
      , Of = -Lf
      , $f = Lf
      , qf = [new $u([Of, Of, Of],[$f, $f, $f]), new $u([Of, Of, Of],[0, 0, $f]), new $u([0, Of, Of],[$f, 0, $f]), new $u([Of, 0, Of],[0, $f, $f]), new $u([0, 0, Of],[$f, $f, $f])];
    function Nf(t, e, r, n=!0) {
        const i = du([], t._camera.position, t.worldSize)
          , s = [e, r, 1, 1];
        Su(s, s, t.pixelMatrixInverse),
        zu(s, s, 1 / s[3]);
        const a = mu([], wu([], s, i))
          , o = t.globeMatrix
          , l = [o[12], o[13], o[14]]
          , c = wu([], l, i)
          , h = ou(c)
          , p = mu([], c)
          , f = t.worldSize / (2 * Math.PI)
          , y = gu(p, a)
          , m = Math.asin(f / h);
        if (m < Math.acos(y)) {
            if (!n)
                return null;
            const t = []
              , e = [];
            du(t, a, h / y),
            mu(e, wu(e, t, c)),
            mu(a, uu(a, c, du(a, e, Math.tan(m) * h)));
        }
        const g = [];
        new ju(i,a).closestPointOnSphere(l, f, g);
        const x = mu([], L(o, 0))
          , v = mu([], L(o, 1))
          , b = mu([], L(o, 2))
          , _ = gu(x, g)
          , w = gu(v, g)
          , A = gu(b, g)
          , k = u(Math.asin(-w / f));
        let z = u(Math.atan2(_, A));
        z = t.center.lng + function(t, e) {
            const r = (e - t + 180) % 360 - 180;
            return r < -180 ? r + 360 : r
        }(t.center.lng, z);
        const S = Ho(z)
          , M = d(Ko(k), 0, 1);
        return new nl(S,M)
    }
    class Zf {
        constructor(t, e, r) {
            this.a = wu([], t, r),
            this.b = wu([], e, r),
            this.center = r;
            const n = mu([], this.a)
              , i = mu([], this.b);
            this.angle = Math.acos(gu(n, i));
        }
    }
    function Gf(t, e) {
        if (0 === t.angle)
            return null;
        let r;
        return r = 0 === t.a[e] ? 1 / t.angle * .5 * Math.PI : 1 / t.angle * Math.atan(t.b[e] / t.a[e] / Math.sin(t.angle) - 1 / Math.tan(t.angle)),
        r < 0 || r > 1 ? null : function(t, e, r, n) {
            const i = Math.sin(r);
            return t * (Math.sin((1 - n) * r) / i) + e * (Math.sin(n * r) / i)
        }(t.a[e], t.b[e], t.angle, d(r, 0, 1)) + t.center[e]
    }
    function Xf(t) {
        if (t.z <= 1)
            return qf[t.z + 2 * t.y + t.x];
        const e = Qf(Wf(t));
        return $u.fromPoints(e)
    }
    function Yf(t, e, r) {
        return du(t, t, 1 - r),
        yu(t, t, e, r)
    }
    function Hf(t, e) {
        const r = ld(e.zoom);
        if (0 === r)
            return Xf(t);
        const n = Wf(t)
          , i = Qf(n)
          , s = Ho(n.getWest()) * e.worldSize
          , a = Ho(n.getEast()) * e.worldSize
          , o = Ko(n.getNorth()) * e.worldSize
          , l = Ko(n.getSouth()) * e.worldSize
          , u = [s, o, 0]
          , c = [a, o, 0]
          , h = [s, l, 0]
          , p = [a, l, 0]
          , f = Kl([], e.globeMatrix);
        return vu(u, u, f),
        vu(c, c, f),
        vu(h, h, f),
        vu(p, p, f),
        i[0] = Yf(i[0], h, r),
        i[1] = Yf(i[1], p, r),
        i[2] = Yf(i[2], c, r),
        i[3] = Yf(i[3], u, r),
        $u.fromPoints(i)
    }
    function Kf(t, e, r) {
        for (const n of t)
            vu(n, n, e),
            du(n, n, r);
    }
    function Jf(t, e, r) {
        const n = e / t.worldSize
          , i = t.globeMatrix;
        if (r.z <= 1) {
            const t = Xf(r).getCorners();
            return Kf(t, i, n),
            $u.fromPoints(t)
        }
        const s = Wf(r)
          , a = Qf(s);
        Kf(a, i, n);
        const o = Number.MAX_VALUE
          , u = [-o, -o, -o]
          , c = [o, o, o];
        if (s.contains(t.center)) {
            for (const t of a)
                pu(c, c, t),
                fu(u, u, t);
            u[2] = 0;
            const e = t.point
              , r = [e.x * n, e.y * n, 0];
            return pu(c, c, r),
            fu(u, u, r),
            new $u(c,u)
        }
        const h = [i[12] * n, i[13] * n, i[14] * n]
          , p = s.getCenter()
          , f = d(t.center.lat, -85.051129, el)
          , y = d(p.lat, -85.051129, el)
          , m = Ho(t.center.lng)
          , g = Ko(f);
        let x = m - Ho(p.lng);
        const v = g - Ko(y);
        x > .5 ? x -= 1 : x < -.5 && (x += 1);
        let b = 0;
        Math.abs(x) > Math.abs(v) ? b = x >= 0 ? 1 : 3 : (b = v >= 0 ? 0 : 2,
        yu(h, h, [i[4] * n, i[5] * n, i[6] * n], -Math.sin(l(v >= 0 ? s.getSouth() : s.getNorth())) * Lf));
        const _ = a[b]
          , w = a[(b + 1) % 4]
          , A = new Zf(_,w,h)
          , k = [Gf(A, 0) || _[0], Gf(A, 1) || _[1], Gf(A, 2) || _[2]]
          , z = ld(t.zoom);
        if (z > 0) {
            const n = function(t, e, r, n, i) {
                const {x: s, z: a} = t
                  , o = 1 / (1 << a);
                let l = s * o
                  , u = l + o
                  , c = t._tileY * o
                  , h = (t._tileY + t._tileH) * o
                  , p = 0;
                const f = (l + u) / 2 - n;
                return f > .5 ? p = -1 : f < -.5 && (p = 1),
                l = ((l + p) * e - (n *= e)) * r + n,
                u = ((u + p) * e - n) * r + n,
                c = (c * e - (i *= e)) * r + i,
                h = (h * e - i) * r + i,
                [[l, h, 0], [u, h, 0], [u, c, 0], [l, c, 0]]
            }(r, e, t._pixelsPerMercatorPixel, m, g);
            for (let t = 0; t < a.length; t++)
                Yf(a[t], n[t], z);
            const i = uu([], n[b], n[(b + 1) % 4]);
            du(i, i, .5),
            Yf(k, i, z);
        }
        for (const t of a)
            pu(c, c, t),
            fu(u, u, t);
        return c[2] = Math.min(_[2], w[2]),
        pu(c, c, k),
        fu(u, u, k),
        new $u(c,u)
    }
    function Wf(t) {
        const {x: e, z: r} = t
          , n = 1 / (1 << r)
          , i = xl(t)
          , s = new Ao(Wo(e * n),Qo(i.bottom * n))
          , a = new Ao(Wo((e + 1) * n),Qo(i.top * n));
        return new _o(s,a)
    }
    function Qf(t) {
        const e = l(t.getNorth())
          , r = l(t.getSouth())
          , n = Math.cos(e)
          , i = Math.cos(r)
          , s = Math.sin(e)
          , a = Math.sin(r)
          , o = t.getWest()
          , u = t.getEast();
        return [td(i, a, o), td(i, a, u), td(n, s, u), td(n, s, o)]
    }
    function td(t, e, r, n=Lf) {
        return r = l(r),
        [t * Math.sin(r) * n, -e * n, t * Math.cos(r) * n]
    }
    function ed(t, e, r) {
        return td(Math.cos(l(t)), Math.sin(l(t)), e, r)
    }
    function rd(t, e, r, n) {
        const i = 1 << r.z
          , s = (t / bo + r.x) / i;
        return ed(Qo(gl(e, r) / i), Wo(s), n)
    }
    function nd({min: t, max: e}) {
        return 16383 / Math.max(e[0] - t[0], e[1] - t[1], e[2] - t[2])
    }
    const id = new Float64Array(16);
    function sd(t) {
        const e = nd(t)
          , r = ru(id, [e, e, e]);
        return Wl(r, r, ((n = [])[0] = -(i = t.min)[0],
        n[1] = -i[1],
        n[2] = -i[2],
        n));
        var n, i;
    }
    function ad(t) {
        const e = (n = t.min,
        (r = id)[0] = 1,
        r[1] = 0,
        r[2] = 0,
        r[3] = 0,
        r[4] = 0,
        r[5] = 1,
        r[6] = 0,
        r[7] = 0,
        r[8] = 0,
        r[9] = 0,
        r[10] = 1,
        r[11] = 0,
        r[12] = n[0],
        r[13] = n[1],
        r[14] = n[2],
        r[15] = 1,
        r);
        var r, n;
        const i = 1 / nd(t);
        return Ql(e, e, [i, i, i])
    }
    function od(t, e, r, n, i) {
        const s = function(t) {
            const e = bo / (2 * Math.PI);
            return t / (2 * Math.PI) / e
        }(r)
          , a = [t, e, -r / (2 * Math.PI)]
          , o = Hl(new Float64Array(16));
        return Wl(o, o, a),
        Ql(o, o, [s, s, s]),
        tu(o, o, l(-i)),
        eu(o, o, l(-n)),
        o
    }
    function ld(t) {
        return y(5, 6, t)
    }
    function ud(t, e) {
        const r = ed(e.lat, e.lng);
        return s = (n = cu([], function(t) {
            const e = ed(t._center.lat, t._center.lng);
            let r = xu([], lu(0, 1, 0), e);
            const n = nu([], -t.angle, e);
            r = vu(r, r, n),
            nu(n, -t._pitch, r);
            const i = mu([], e);
            return du(i, i, t.cameraToCenterDistance / t.pixelsPerMeter * Rf),
            vu(i, i, n),
            uu([], e, i)
        }(t), r))[0],
        a = n[1],
        o = n[2],
        l = (i = r)[0],
        u = i[1],
        c = i[2],
        p = (h = Math.sqrt(s * s + a * a + o * o) * Math.sqrt(l * l + u * u + c * c)) && gu(n, i) / h,
        Math.acos(Math.min(Math.max(p, -1), 1));
        var n, i, s, a, o, l, u, c, h, p;
    }
    const cd = l(85)
      , hd = Math.cos(cd)
      , pd = Math.sin(cd);
    function fd(t, e) {
        const r = t.fovAboveCenter
          , n = t.elevation ? t.elevation.getMinElevationBelowMSL() * e : 0
          , i = (t._camera.position[2] * t.worldSize - n) / Math.cos(t._pitch)
          , s = Math.sin(r) * i / Math.sin(Math.max(Math.PI / 2 - t._pitch - r, .01))
          , a = Math.sin(t._pitch) * s + i;
        return Math.min(1.01 * a, i * (1 / t._horizonShift))
    }
    function dd(t, e) {
        if (!e.isReprojectedInTileSpace) {
            const r = xl(t);
            return {
                scale: 1 << t.z,
                x: t.x,
                y: r.top,
                x2: t.x + 1,
                y2: r.bottom,
                projection: e,
                reference: t.reference,
                _tileY: t._tileY,
                _tileH: t._tileH
            }
        }
        const r = Math.pow(2, -t.z)
          , n = t.x * r
          , i = (t.x + 1) * r
          , s = xl(t)
          , a = s.top * r
          , o = s.bottom * r
          , l = Wo(n)
          , u = Wo(i)
          , c = Qo(a)
          , h = Qo(o)
          , p = e.project(l, c)
          , f = e.project(u, c)
          , d = e.project(u, h)
          , y = e.project(l, h);
        let m = Math.min(p.x, f.x, d.x, y.x)
          , g = Math.min(p.y, f.y, d.y, y.y)
          , x = Math.max(p.x, f.x, d.x, y.x)
          , v = Math.max(p.y, f.y, d.y, y.y);
        const b = r / 16;
        function _(t, r, n, i, s, a) {
            const o = (n + s) / 2
              , l = (i + a) / 2
              , u = e.project(Wo(o), Qo(l))
              , c = Math.max(0, m - u.x, g - u.y, u.x - x, u.y - v);
            m = Math.min(m, u.x),
            x = Math.max(x, u.x),
            g = Math.min(g, u.y),
            v = Math.max(v, u.y),
            c > b && (_(t, u, n, i, o, l),
            _(u, r, o, l, s, a));
        }
        _(p, f, n, a, i, a),
        _(f, d, i, a, i, o),
        _(d, y, i, o, n, o),
        _(y, p, n, o, n, a),
        m -= b,
        g -= b,
        x += b,
        v += b;
        const w = 1 / Math.max(x - m, v - g);
        return {
            scale: w,
            x: m * w,
            y: g * w,
            x2: x * w,
            y2: v * w,
            projection: e,
            _tileY: g * w,
            _tileH: v * w - g * w
        }
    }
    const yd = Hl(new Float32Array(16));
    class md {
        constructor(t) {
            this.spec = t,
            this.name = t.name,
            this.wrap = !1,
            this.requiresDraping = !1,
            this.supportsWorldCopies = !1,
            this.supportsTerrain = !1,
            this.supportsFog = !1,
            this.supportsFreeCamera = !1,
            this.zAxisUnit = "meters",
            this.isReprojectedInTileSpace = !0,
            this.unsupportedLayers = ["custom"],
            this.center = [0, 0],
            this.range = [3.5, 7];
        }
        project(t, e) {
            return {
                x: 0,
                y: 0,
                z: 0
            }
        }
        unproject(t, e) {
            return new Ao(0,0)
        }
        projectTilePoint(t, e, r) {
            return {
                x: t,
                y: e,
                z: 0
            }
        }
        locationPoint(t, e, r=!0) {
            return t._coordinatePoint(t.locationCoordinate(e), r)
        }
        pixelsPerMeter(t, e) {
            return Jo(1, t) * e
        }
        pixelSpaceConversion(t, e, r) {
            return 1
        }
        farthestPixelDistance(t) {
            return fd(t, t.pixelsPerMeter)
        }
        pointCoordinate(t, e, r, n) {
            const s = t.horizonLineFromTop(!1)
              , a = new i(e,Math.max(s, r));
            return t.rayIntersectionCoordinate(t.pointRayIntersection(a, n))
        }
        pointCoordinate3D(t, e, r) {
            const n = new i(e,r);
            if (t.elevation)
                return t.elevation.pointCoordinate(n);
            {
                const e = this.pointCoordinate(t, n.x, n.y, 0);
                return [e.x, e.y, e.z]
            }
        }
        isPointAboveHorizon(t, e) {
            if (t.elevation)
                return !this.pointCoordinate3D(t, e.x, e.y);
            const r = t.horizonLineFromTop();
            return e.y < r
        }
        createInversionMatrix(t, e) {
            return yd
        }
        createTileMatrix(t, e, r) {
            let n, i, s;
            const a = r.canonical
              , o = Hl(new Float64Array(16));
            let l = a._tileY
              , u = a._tileH;
            if (this.isReprojectedInTileSpace) {
                const c = dd(a, this);
                n = 1,
                i = c.x + r.wrap * c.scale,
                s = c.y,
                l = c._tileY,
                u = c._tileH,
                Ql(o, o, [n / c.scale, n / c.scale, t.pixelsPerMeter / e]);
            } else
                n = e / t.zoomScale(a.z),
                i = (a.x + Math.pow(2, a.z) * r.wrap) * n,
                s = a.y * n;
            return "Sg4326" == a.reference ? (Wl(o, o, [i, l * n, 0]),
            Ql(o, o, [1, u, 1])) : Wl(o, o, [i, s, 0]),
            Ql(o, o, [n / bo, n / bo, 1]),
            o
        }
        upVector(t, e, r) {
            return [0, 0, 1]
        }
        upVectorScale(t, e, r) {
            return {
                metersToTile: 1
            }
        }
    }
    class gd extends md {
        constructor(t) {
            super(t),
            this.range = [4, 7],
            this.center = t.center || [-96, 37.5];
            const [e,r] = this.parallels = t.parallels || [29.5, 45.5]
              , n = Math.sin(l(e));
            this.n = (n + Math.sin(l(r))) / 2,
            this.c = 1 + n * (2 * this.n - n),
            this.r0 = Math.sqrt(this.c) / this.n;
        }
        project(t, e) {
            const {n: r, c: n, r0: i} = this
              , s = l(t - this.center[0])
              , a = l(e)
              , o = Math.sqrt(n - 2 * r * Math.sin(a)) / r;
            return {
                x: o * Math.sin(s * r),
                y: o * Math.cos(s * r) - i,
                z: 0
            }
        }
        unproject(t, e) {
            const {n: r, c: n, r0: i} = this
              , s = i + e;
            let a = Math.atan2(t, Math.abs(s)) * Math.sign(s);
            s * r < 0 && (a -= Math.PI * Math.sign(t) * Math.sign(s));
            const o = l(this.center[0]) * r;
            a = m(a, -Math.PI - o, Math.PI - o);
            const c = u(a / r) + this.center[0]
              , h = Math.asin(d((n - (t * t + s * s) * r * r) / (2 * r), -1, 1))
              , p = d(u(h), -85.051129, el);
            return new Ao(c,p)
        }
    }
    const xd = 1.340264
      , vd = -.081106
      , bd = 893e-6
      , _d = .003796
      , wd = Math.sqrt(3) / 2;
    class Ad extends md {
        project(t, e) {
            e = e / 180 * Math.PI,
            t = t / 180 * Math.PI;
            const r = Math.asin(wd * Math.sin(e))
              , n = r * r
              , i = n * n * n;
            return {
                x: .5 * (t * Math.cos(r) / (wd * (xd + 3 * vd * n + i * (7 * bd + 9 * _d * n))) / Math.PI + .5),
                y: 1 - .5 * (r * (xd + vd * n + i * (bd + _d * n)) / Math.PI + 1),
                z: 0
            }
        }
        unproject(t, e) {
            t = (2 * t - .5) * Math.PI;
            let r = e = (2 * (1 - e) - 1) * Math.PI
              , n = r * r
              , i = n * n * n;
            for (let t, s, a, o = 0; o < 12 && (s = r * (xd + vd * n + i * (bd + _d * n)) - e,
            a = xd + 3 * vd * n + i * (7 * bd + 9 * _d * n),
            t = s / a,
            r = d(r - t, -Math.PI / 3, Math.PI / 3),
            n = r * r,
            i = n * n * n,
            !(Math.abs(t) < 1e-12)); ++o)
                ;
            const s = wd * t * (xd + 3 * vd * n + i * (7 * bd + 9 * _d * n)) / Math.cos(r)
              , a = Math.asin(Math.sin(r) / wd)
              , o = d(180 * s / Math.PI, -180, 180)
              , l = d(180 * a / Math.PI, -85.051129, el);
            return new Ao(o,l)
        }
    }
    class kd extends md {
        constructor(t) {
            super(t),
            this.wrap = !0,
            this.supportsWorldCopies = !0;
        }
        project(t, e) {
            return {
                x: .5 + t / 360,
                y: .5 - e / 360,
                z: 0
            }
        }
        unproject(t, e) {
            const r = 360 * (t - .5)
              , n = d(360 * (.5 - e), -85.051129, el);
            return new Ao(r,n)
        }
    }
    const zd = Math.PI / 2;
    function Sd(t) {
        return Math.tan((zd + t) / 2)
    }
    class Md extends md {
        constructor(t) {
            super(t),
            this.center = t.center || [0, 30];
            const [e,r] = this.parallels = t.parallels || [30, 30];
            let n = l(e)
              , i = l(r);
            this.southernCenter = n + i < 0,
            this.southernCenter && (n = -n,
            i = -i);
            const s = Math.cos(n)
              , a = Sd(n);
            this.n = n === i ? Math.sin(n) : Math.log(s / Math.cos(i)) / Math.log(Sd(i) / a),
            this.f = s * Math.pow(Sd(n), this.n) / this.n;
        }
        project(t, e) {
            e = l(e),
            this.southernCenter && (e = -e),
            t = l(t - this.center[0]);
            const r = 1e-6
              , {n: n, f: i} = this;
            i > 0 ? e < -zd + r && (e = -zd + r) : e > zd - r && (e = zd - r);
            const s = i / Math.pow(Sd(e), n);
            let a = s * Math.sin(n * t)
              , o = i - s * Math.cos(n * t);
            return a = .5 * (a / Math.PI + .5),
            o = .5 * (o / Math.PI + .5),
            {
                x: a,
                y: this.southernCenter ? o : 1 - o,
                z: 0
            }
        }
        unproject(t, e) {
            t = (2 * t - .5) * Math.PI,
            this.southernCenter && (e = 1 - e),
            e = (2 * (1 - e) - .5) * Math.PI;
            const {n: r, f: n} = this
              , i = n - e
              , s = Math.sign(i)
              , a = Math.sign(r) * Math.sqrt(t * t + i * i);
            let o = Math.atan2(t, Math.abs(i)) * s;
            i * r < 0 && (o -= Math.PI * Math.sign(t) * s);
            const l = d(u(o / r) + this.center[0], -180, 180)
              , c = d(u(2 * Math.atan(Math.pow(n / a, 1 / r)) - zd), -85.051129, el);
            return new Ao(l,this.southernCenter ? -c : c)
        }
    }
    class Id extends md {
        constructor(t) {
            super(t),
            this.wrap = !0,
            this.supportsWorldCopies = !0,
            this.supportsTerrain = !0,
            this.supportsFog = !0,
            this.supportsFreeCamera = !0,
            this.isReprojectedInTileSpace = !1,
            this.unsupportedLayers = [],
            this.range = null;
        }
        project(t, e) {
            return {
                x: Ho(t),
                y: Ko(e),
                z: 0
            }
        }
        unproject(t, e) {
            const r = Wo(t)
              , n = Qo(e);
            return new Ao(r,n)
        }
    }
    const Td = l(el);
    class Bd extends md {
        project(t, e) {
            const r = (e = l(e)) * e
              , n = r * r;
            return {
                x: .5 * ((t = l(t)) * (.8707 - .131979 * r + n * (n * (.003971 * r - .001529 * n) - .013791)) / Math.PI + .5),
                y: 1 - .5 * (e * (1.007226 + r * (.015085 + n * (.028874 * r - .044475 - .005916 * n))) / Math.PI + 1),
                z: 0
            }
        }
        unproject(t, e) {
            t = (2 * t - .5) * Math.PI;
            let r = e = (2 * (1 - e) - 1) * Math.PI
              , n = 25
              , i = 0
              , s = r * r;
            do {
                s = r * r;
                const t = s * s;
                i = (r * (1.007226 + s * (.015085 + t * (.028874 * s - .044475 - .005916 * t))) - e) / (1.007226 + s * (.045255 + t * (.259866 * s - .311325 - .005916 * 11 * t))),
                r = d(r - i, -Td, Td);
            } while (Math.abs(i) > 1e-6 && --n > 0);
            s = r * r;
            const a = d(u(t / (.8707 + s * (s * (s * s * s * (.003971 - .001529 * s) - .013791) - .131979))), -180, 180)
              , o = u(r);
            return new Ao(a,o)
        }
    }
    const Cd = l(el);
    class Vd extends md {
        project(t, e) {
            e = l(e),
            t = l(t);
            const r = Math.cos(e)
              , n = 2 / Math.PI
              , i = Math.acos(r * Math.cos(t / 2))
              , s = Math.sin(i) / i
              , a = .5 * (t * n + 2 * r * Math.sin(t / 2) / s) || 0
              , o = .5 * (e + Math.sin(e) / s) || 0;
            return {
                x: .5 * (a / Math.PI + .5),
                y: 1 - .5 * (o / Math.PI + 1),
                z: 0
            }
        }
        unproject(t, e) {
            let r = t = (2 * t - .5) * Math.PI
              , n = e = (2 * (1 - e) - 1) * Math.PI
              , i = 25;
            const s = 1e-6;
            let a = 0
              , o = 0;
            do {
                const i = Math.cos(n)
                  , s = Math.sin(n)
                  , l = 2 * s * i
                  , u = s * s
                  , c = i * i
                  , h = Math.cos(r / 2)
                  , p = Math.sin(r / 2)
                  , f = 2 * h * p
                  , y = p * p
                  , m = 1 - c * h * h
                  , g = m ? 1 / m : 0
                  , x = m ? Math.acos(i * h) * Math.sqrt(1 / m) : 0
                  , v = .5 * (2 * x * i * p + 2 * r / Math.PI) - t
                  , b = .5 * (x * s + n) - e
                  , _ = .5 * g * (c * y + x * i * h * u) + 1 / Math.PI
                  , w = g * (f * l / 4 - x * s * p)
                  , A = .125 * g * (l * p - x * s * c * f)
                  , k = .5 * g * (u * h + x * y * i) + .5
                  , z = w * A - k * _;
                a = (b * w - v * k) / z,
                o = (v * A - b * _) / z,
                r = d(r - a, -Math.PI, Math.PI),
                n = d(n - o, -Cd, Cd);
            } while ((Math.abs(a) > s || Math.abs(o) > s) && --i > 0);
            return new Ao(u(r),u(n))
        }
    }
    class Pd extends md {
        constructor(t) {
            super(t),
            this.center = t.center || [0, 0],
            this.parallels = t.parallels || [0, 0],
            this.cosPhi = Math.max(.01, Math.cos(l(this.parallels[0]))),
            this.scale = 1 / (2 * Math.max(Math.PI * this.cosPhi, 1 / this.cosPhi)),
            this.wrap = !0,
            this.supportsWorldCopies = !0;
        }
        project(t, e) {
            const {scale: r, cosPhi: n} = this;
            return {
                x: l(t) * n * r + .5,
                y: -Math.sin(l(e)) / n * r + .5,
                z: 0
            }
        }
        unproject(t, e) {
            const {scale: r, cosPhi: n} = this
              , i = -(e - .5) / r
              , s = d(u((t - .5) / r) / n, -180, 180)
              , a = Math.asin(d(i * n, -1, 1))
              , o = d(u(a), -85.051129, el);
            return new Ao(s,o)
        }
    }
    class Dd extends Id {
        constructor(t) {
            super(t),
            this.requiresDraping = !0,
            this.supportsWorldCopies = !1,
            this.supportsFog = !0,
            this.zAxisUnit = "pixels",
            this.unsupportedLayers = ["debug", "custom"],
            this.range = [3, 5];
        }
        projectTilePoint(t, e, r) {
            const n = rd(t, e, r);
            return vu(n, n, sd(Xf(r))),
            {
                x: n[0],
                y: n[1],
                z: n[2]
            }
        }
        locationPoint(t, e) {
            const r = ed(e.lat, e.lng)
              , n = mu([], r)
              , s = t.elevation ? t.elevation.getAtPointOrZero(t.locationCoordinate(e), t._centerAltitude) : t._centerAltitude;
            yu(r, r, n, Jo(1, 0) * bo * s);
            const a = Hl(new Float64Array(16));
            return Jl(a, t.pixelMatrix, t.globeMatrix),
            vu(r, r, a),
            new i(r[0],r[1])
        }
        pixelsPerMeter(t, e) {
            return Jo(1, 0) * e
        }
        pixelSpaceConversion(t, e, r) {
            const n = mr(Jo(1, 45) * e, Jo(1, t) * e, r);
            return this.pixelsPerMeter(t, e) / n
        }
        createTileMatrix(t, e, r) {
            const n = ad(Xf(r.canonical));
            return Jl(new Float64Array(16), t.globeMatrix, n)
        }
        createInversionMatrix(t, e) {
            const {center: r} = t
              , n = sd(Xf(e));
            return eu(n, n, l(r.lng)),
            tu(n, n, l(r.lat)),
            Ql(n, n, [t._pixelsPerMercatorPixel, t._pixelsPerMercatorPixel, 1]),
            Float32Array.from(n)
        }
        pointCoordinate(t, e, r, n) {
            return Nf(t, e, r, !0) || new nl(0,0)
        }
        pointCoordinate3D(t, e, r) {
            const n = this.pointCoordinate(t, e, r, 0);
            return [n.x, n.y, n.z]
        }
        isPointAboveHorizon(t, e) {
            return !Nf(t, e.x, e.y, !1)
        }
        farthestPixelDistance(t) {
            const e = function(t, e) {
                const r = t.cameraToCenterDistance
                  , n = t._centerAltitude * e
                  , i = t._camera
                  , s = t._camera.forward()
                  , a = uu([], du([], s, -r), [0, 0, n])
                  , o = t.worldSize / (2 * Math.PI)
                  , l = [0, 0, -o]
                  , u = t.width / t.height
                  , c = Math.tan(t.fovAboveCenter)
                  , h = du([], i.up(), c)
                  , p = du([], i.right(), c * u)
                  , f = mu([], uu([], uu([], s, h), p))
                  , d = [];
                let y;
                if (new ju(a,f).closestPointOnSphere(l, o, d)) {
                    const e = uu([], d, l)
                      , r = wu([], e, a);
                    y = Math.cos(t.fovAboveCenter) * ou(r);
                } else {
                    const t = wu([], a, l)
                      , e = wu([], l, a);
                    mu(e, e);
                    const r = ou(t) - o;
                    y = Math.sqrt(r * (r + 2 * o));
                    const n = Math.acos(y / (o + r)) - Math.acos(gu(s, e));
                    y *= Math.cos(n);
                }
                return 1.01 * y
            }(t, this.pixelsPerMeter(t.center.lat, t.worldSize))
              , r = ld(t.zoom);
            if (r > 0) {
                const n = fd(t, Jo(1, t.center.lat) * t.worldSize)
                  , i = t.worldSize / (2 * Math.PI)
                  , s = Math.max(t.width, t.height) / t.worldSize * Math.PI;
                return mr(e, n + i * (1 - Math.cos(s)), Math.pow(r, 10))
            }
            return e
        }
        upVector(t, e, r) {
            return rd(e, r, t, 1)
        }
        upVectorScale(t) {
            return {
                metersToTile: Rf * nd(Xf(t))
            }
        }
    }
    function Ed(t) {
        const e = t.parallels
          , r = !!e && Math.abs(e[0] + e[1]) < .01;
        switch (t.name) {
        case "mercator":
            return new Id(t);
        case "equirectangular":
            return new kd(t);
        case "naturalEarth":
            return new Bd(t);
        case "equalEarth":
            return new Ad(t);
        case "winkelTripel":
            return new Vd(t);
        case "albers":
            return r ? new Pd(t) : new gd(t);
        case "lambertConformalConic":
            return r ? new Pd(t) : new Md(t);
        case "globe":
            return new Dd(t)
        }
        throw new Error(`Invalid projection name: ${t.name}`)
    }
    const Fd = nh.VectorTileFeature.types
      , Ld = [{
        name: "a_fade_opacity",
        components: 1,
        type: "Uint8",
        offset: 0
    }];
    function Rd(t, e, r, n, i, s, a, o, l, u, c, h, p) {
        const f = o ? Math.min(Mf, Math.round(o[0])) : 0
          , d = o ? Math.min(Mf, Math.round(o[1])) : 0;
        t.emplaceBack(e, r, Math.round(32 * n), Math.round(32 * i), s, a, (f << 1) + (l ? 1 : 0), d, 16 * u, 16 * c, 256 * h, 256 * p);
    }
    function jd(t, e, r, n, i, s, a) {
        t.emplaceBack(e, r, n, i, s, a);
    }
    function Ud(t, e, r, n, i, s) {
        s && (i = -1 * (i + 100)),
        t.emplaceBack(e, r, n, i),
        t.emplaceBack(e, r, n, i),
        t.emplaceBack(e, r, n, i),
        t.emplaceBack(e, r, n, i);
    }
    function Od(t) {
        for (const e of t.sections)
            if (ms(e.text))
                return !0;
        return !1
    }
    class $d {
        constructor(t) {
            this.layoutVertexArray = new ia,
            this.indexArray = new pa,
            this.programConfigurations = t,
            this.segments = new vo,
            this.dynamicLayoutVertexArray = new ta,
            this.opacityVertexArray = new aa,
            this.placedSymbolArray = new Sa,
            this.globeExtVertexArray = new sa;
        }
        isEmpty() {
            return 0 === this.layoutVertexArray.length && 0 === this.indexArray.length && 0 === this.dynamicLayoutVertexArray.length && 0 === this.opacityVertexArray.length
        }
        upload(t, e, r, n) {
            this.isEmpty() || (r && (this.layoutVertexBuffer = t.createVertexBuffer(this.layoutVertexArray, $h.members),
            this.indexBuffer = t.createIndexBuffer(this.indexArray, e),
            this.dynamicLayoutVertexBuffer = t.createVertexBuffer(this.dynamicLayoutVertexArray, Nh.members, !0),
            this.opacityVertexBuffer = t.createVertexBuffer(this.opacityVertexArray, Ld, !0),
            this.globeExtVertexArray.length > 0 && (this.globeExtVertexBuffer = t.createVertexBuffer(this.globeExtVertexArray, qh.members, !0)),
            this.opacityVertexBuffer.itemSize = 1),
            (r || n) && this.programConfigurations.upload(t));
        }
        destroy() {
            this.layoutVertexBuffer && (this.layoutVertexBuffer.destroy(),
            this.indexBuffer.destroy(),
            this.programConfigurations.destroy(),
            this.segments.destroy(),
            this.dynamicLayoutVertexBuffer.destroy(),
            this.opacityVertexBuffer.destroy(),
            this.globeExtVertexBuffer && this.globeExtVertexBuffer.destroy());
        }
    }
    Bi($d, "SymbolBuffers");
    class qd {
        constructor(t, e, r) {
            this.layoutVertexArray = new t,
            this.layoutAttributes = e,
            this.indexArray = new r,
            this.segments = new vo,
            this.collisionVertexArray = new ca,
            this.collisionVertexArrayExt = new ha;
        }
        upload(t) {
            this.layoutVertexBuffer = t.createVertexBuffer(this.layoutVertexArray, this.layoutAttributes),
            this.indexBuffer = t.createIndexBuffer(this.indexArray),
            this.collisionVertexBuffer = t.createVertexBuffer(this.collisionVertexArray, Zh.members, !0),
            this.collisionVertexBufferExt = t.createVertexBuffer(this.collisionVertexArrayExt, Gh.members, !0);
        }
        destroy() {
            this.layoutVertexBuffer && (this.layoutVertexBuffer.destroy(),
            this.indexBuffer.destroy(),
            this.segments.destroy(),
            this.collisionVertexBuffer.destroy(),
            this.collisionVertexBufferExt.destroy());
        }
    }
    Bi(qd, "CollisionBuffers");
    class Nd {
        constructor(t) {
            this.collisionBoxArray = t.collisionBoxArray,
            this.zoom = t.zoom,
            this.overscaling = t.overscaling,
            this.layers = t.layers,
            this.layerIds = this.layers.map((t=>t.id)),
            this.index = t.index,
            this.pixelRatio = t.pixelRatio,
            this.sourceLayerIndex = t.sourceLayerIndex,
            this.hasPattern = !1,
            this.hasRTLText = !1,
            this.fullyClipped = !1,
            this.sortKeyRanges = [],
            this.collisionCircleArray = [],
            this.placementInvProjMatrix = Hl([]),
            this.placementViewportMatrix = Hl([]);
            const e = this.layers[0]._unevaluatedLayout._values;
            this.textSizeData = Jh(this.zoom, e["text-size"]),
            this.iconSizeData = Jh(this.zoom, e["icon-size"]);
            const r = this.layers[0].layout
              , n = r.get("symbol-sort-key")
              , i = r.get("symbol-z-order");
            this.canOverlap = r.get("text-allow-overlap") || r.get("icon-allow-overlap") || r.get("text-ignore-placement") || r.get("icon-ignore-placement"),
            this.sortFeaturesByKey = "viewport-y" !== i && void 0 !== n.constantOr(1),
            this.sortFeaturesByY = ("viewport-y" === i || "auto" === i && !this.sortFeaturesByKey) && this.canOverlap,
            this.writingModes = r.get("text-writing-mode").map((t=>Pp[t])),
            this.stateDependentLayerIds = this.layers.filter((t=>t.isStateDependent())).map((t=>t.id)),
            this.sourceID = t.sourceID,
            this.projection = t.projection,
            this.feature_values = {};
        }
        createArrays() {
            this.text = new $d(new lo(this.layers,this.zoom,(t=>/^text/.test(t) || /symbol-minzoom/.test(t) || /symbol-maxzoom/.test(t)))),
            this.icon = new $d(new lo(this.layers,this.zoom,(t=>/^icon/.test(t) || /symbol-minzoom/.test(t) || /symbol-maxzoom/.test(t)))),
            this.glyphOffsetArray = new Ta,
            this.lineVertexArray = new Ba,
            this.symbolInstances = new Ia;
        }
        calculateGlyphDependencies(t, e, r, n, i) {
            for (let r = 0; r < t.length; r++)
                if (e[t.charCodeAt(r)] = !0,
                n && i) {
                    const n = rp[t.charAt(r)];
                    n && (e[n.charCodeAt(0)] = !0);
                }
        }
        populate(t, e, r, n) {
            const i = this.layers[0]
              , s = i.layout
              , a = i.paint
              , o = "globe" === this.projection.name
              , l = s.get("text-font")
              , u = s.get("text-field")
              , c = s.get("icon-image")
              , h = ("constant" !== u.value.kind || u.value.value instanceof ve && !u.value.value.isEmpty() || u.value.value.toString().length > 0) && ("constant" !== l.value.kind || l.value.value.length > 0)
              , p = "constant" !== c.value.kind || !!c.value.value || Object.keys(c.parameters).length > 0
              , f = s.get("symbol-sort-key");
            this.features = [],
            this.feature_values = [];
            const d = a.get("symbol-minzoom")
              , y = a.get("symbol-maxzoom");
            if (!h && !p)
                return;
            const m = e.iconDependencies
              , g = e.glyphDependencies
              , x = e.availableImages
              , v = new Ts(this.zoom);
            for (const {feature: e, id: a, index: u, sourceLayerIndex: c} of t) {
                const t = i._featureFilter.needGeometry
                  , w = Al(e, t);
                if (!i._featureFilter.filter(v, w, r))
                    continue;
                if (t || (w.geometry = wl(e, r, n)),
                o && 1 !== e.type && r.z <= 5) {
                    const t = w.geometry
                      , e = .98078528056;
                    for (let n = 0; n < t.length; n++)
                        t[n] = ol(t[n], (t=>t), ((t,n)=>gu(rd(t.x, t.y, r, 1), rd(n.x, n.y, r, 1)) < e));
                }
                let A, k;
                if (h) {
                    const t = i.getValueAndResolveTokens("text-field", w, r, x)
                      , e = ve.factory(t);
                    Od(e) && (this.hasRTLText = !0),
                    (!this.hasRTLText || "unavailable" === Ss() || this.hasRTLText && Is.isParsed()) && (A = ep(e, i, w));
                }
                if (p) {
                    const t = i.getValueAndResolveTokens("icon-image", w, r, x);
                    k = t instanceof be ? t : be.fromString(t);
                }
                if (!A && !k)
                    continue;
                const z = this.sortFeaturesByKey ? f.evaluate(w, {}, r) : void 0;
                if (this.features.push({
                    id: a,
                    text: A,
                    icon: k,
                    index: u,
                    sourceLayerIndex: c,
                    geometry: w.geometry,
                    properties: e.properties,
                    type: Fd[e.type],
                    sortKey: z
                }),
                d && y && 0 != d.constantOr(1) && 24 != y.constantOr(1)) {
                    var b = d.evaluate(w)
                      , _ = y.evaluate(w);
                    this.feature_values.push([u, b = b <= 3 ? 0 : b - 1, _ = _ >= 19 ? 25 : _ > b ? _ : b + 1]);
                }
                if (k && (m[k.name] = !0),
                A) {
                    const t = l.evaluate(w, {}, r).join(",")
                      , e = "map" === s.get("text-rotation-alignment") && "point" !== s.get("symbol-placement");
                    this.allowVerticalPlacement = this.writingModes && this.writingModes.indexOf(Pp.vertical) >= 0;
                    for (const r of A.sections)
                        if (r.image)
                            m[r.image.name] = !0;
                        else {
                            const n = us(A.toString())
                              , i = r.fontStack || t
                              , s = g[i] = g[i] || {};
                            this.calculateGlyphDependencies(r.text, s, e, this.allowVerticalPlacement, n);
                        }
                }
            }
            "line" === s.get("symbol-placement") && (this.features = function(t) {
                const e = {}
                  , r = {}
                  , n = [];
                let i = 0;
                function s(e) {
                    n.push(t[e]),
                    i++;
                }
                function a(t, e, i) {
                    const s = r[t];
                    return delete r[t],
                    r[e] = s,
                    n[s].geometry[0].pop(),
                    n[s].geometry[0] = n[s].geometry[0].concat(i[0]),
                    s
                }
                function o(t, r, i) {
                    const s = e[r];
                    return delete e[r],
                    e[t] = s,
                    n[s].geometry[0].shift(),
                    n[s].geometry[0] = i[0].concat(n[s].geometry[0]),
                    s
                }
                function l(t, e, r) {
                    const n = r ? e[0][e[0].length - 1] : e[0][0];
                    return `${t}:${n.x}:${n.y}`
                }
                for (let u = 0; u < t.length; u++) {
                    const c = t[u]
                      , h = c.geometry
                      , p = c.text ? c.text.toString() : null;
                    if (!p) {
                        s(u);
                        continue
                    }
                    const f = l(p, h)
                      , d = l(p, h, !0);
                    if (f in r && d in e && r[f] !== e[d]) {
                        const t = o(f, d, h)
                          , i = a(f, d, n[t].geometry);
                        delete e[f],
                        delete r[d],
                        r[l(p, n[i].geometry, !0)] = i,
                        n[t].geometry = null;
                    } else
                        f in r ? a(f, d, h) : d in e ? o(f, d, h) : (s(u),
                        e[f] = i - 1,
                        r[d] = i - 1);
                }
                return n.filter((t=>t.geometry))
            }(this.features)),
            this.sortFeaturesByKey && this.features.sort(((t,e)=>t.sortKey - e.sortKey));
        }
        update(t, e, r, n) {
            this.stateDependentLayers.length && (this.text.programConfigurations.updatePaintArrays(t, e, this.layers, r, n),
            this.icon.programConfigurations.updatePaintArrays(t, e, this.layers, r, n));
        }
        isEmpty() {
            return 0 === this.symbolInstances.length && !this.hasRTLText
        }
        uploadPending() {
            return !this.uploaded || this.text.programConfigurations.needsUpload || this.icon.programConfigurations.needsUpload
        }
        upload(t) {
            !this.uploaded && this.hasDebugData() && (this.textCollisionBox.upload(t),
            this.iconCollisionBox.upload(t)),
            this.text.upload(t, this.sortFeaturesByY, !this.uploaded, this.text.programConfigurations.needsUpload),
            this.icon.upload(t, this.sortFeaturesByY, !this.uploaded, this.icon.programConfigurations.needsUpload),
            this.uploaded = !0;
        }
        destroyDebugData() {
            this.textCollisionBox.destroy(),
            this.iconCollisionBox.destroy();
        }
        getProjection() {
            return this.projectionInstance || (this.projectionInstance = Ed(this.projection)),
            this.projectionInstance
        }
        destroy() {
            this.text.destroy(),
            this.icon.destroy(),
            this.hasDebugData() && this.destroyDebugData();
        }
        addToLineVertexArray(t, e) {
            const r = this.lineVertexArray.length
              , n = t.segment;
            if (void 0 !== n) {
                let r = t.dist(e[n + 1])
                  , i = t.dist(e[n]);
                const s = {};
                for (let t = n + 1; t < e.length; t++)
                    s[t] = {
                        x: e[t].x,
                        y: e[t].y,
                        tileUnitDistanceFromAnchor: r
                    },
                    t < e.length - 1 && (r += e[t + 1].dist(e[t]));
                for (let t = n || 0; t >= 0; t--)
                    s[t] = {
                        x: e[t].x,
                        y: e[t].y,
                        tileUnitDistanceFromAnchor: i
                    },
                    t > 0 && (i += e[t - 1].dist(e[t]));
                for (let t = 0; t < e.length; t++) {
                    const e = s[t];
                    this.lineVertexArray.emplaceBack(e.x, e.y, e.tileUnitDistanceFromAnchor);
                }
            }
            return {
                lineStartIndex: r,
                lineLength: this.lineVertexArray.length - r
            }
        }
        addSymbols(t, e, r, n, i, s, a, o, l, u, c, h, p, f) {
            const d = t.indexArray
              , y = t.layoutVertexArray
              , m = t.globeExtVertexArray
              , g = t.segments.prepareSegment(4 * e.length, y, d, this.canOverlap ? s.sortKey : void 0)
              , x = this.glyphOffsetArray.length
              , v = g.vertexLength
              , b = this.allowVerticalPlacement && a === Pp.vertical ? Math.PI / 2 : 0
              , _ = s.text && s.text.sections;
            let w = this.layers[0].layout.get("symbol-scaleable").evaluate(s, {});
            for (let n = 0; n < e.length; n++) {
                const {tl: i, tr: a, bl: u, br: c, tex: h, pixelOffsetTL: x, pixelOffsetBR: v, minFontScaleX: A, minFontScaleY: k, glyphOffset: z, isSDF: S, sectionIndex: M} = e[n]
                  , I = g.vertexLength
                  , T = z[1];
                if (Rd(y, l.x, l.y, i.x, T + i.y, h.x, h.y, r, S, x.x, x.y, A, k),
                Rd(y, l.x, l.y, a.x, T + a.y, h.x + h.w, h.y, r, S, v.x, x.y, A, k),
                Rd(y, l.x, l.y, u.x, T + u.y, h.x, h.y + h.h, r, S, x.x, v.y, A, k),
                Rd(y, l.x, l.y, c.x, T + c.y, h.x + h.w, h.y + h.h, r, S, v.x, v.y, A, k),
                o) {
                    const e = o.anchor
                      , r = o.up;
                    jd(m, e.x, e.y, e.z, r[0], r[1], r[2]),
                    jd(m, e.x, e.y, e.z, r[0], r[1], r[2]),
                    jd(m, e.x, e.y, e.z, r[0], r[1], r[2]),
                    jd(m, e.x, e.y, e.z, r[0], r[1], r[2]),
                    Ud(t.dynamicLayoutVertexArray, e.x, e.y, e.z, b);
                } else
                    Ud(t.dynamicLayoutVertexArray, l.x, l.y, l.z, b, w);
                d.emplaceBack(I, I + 1, I + 2),
                d.emplaceBack(I + 1, I + 2, I + 3),
                g.vertexLength += 4,
                g.primitiveLength += 2,
                this.glyphOffsetArray.emplaceBack(z[0]),
                n !== e.length - 1 && M === e[n + 1].sectionIndex || t.programConfigurations.populatePaintArrays(y.length, s, s.index, {}, p, f, _ && _[M]);
            }
            const A = o ? o.anchor : l;
            t.placedSymbolArray.emplaceBack(A.x, A.y, A.z, l.x, l.y, x, this.glyphOffsetArray.length - x, v, u, c, l.segment, r ? r[0] : 0, r ? r[1] : 0, n[0], n[1], a, 0, !1, 0, h, 0);
        }
        _commitLayoutVertex(t, e, r, n, i, s, a) {
            t.emplaceBack(e, r, n, i, s, Math.round(a.x), Math.round(a.y));
        }
        _addCollisionDebugVertices(t, e, r, n, s, a, o) {
            const l = r.segments.prepareSegment(4, r.layoutVertexArray, r.indexArray)
              , u = l.vertexLength
              , c = o.tileAnchorX
              , h = o.tileAnchorY;
            for (let t = 0; t < 4; t++)
                r.collisionVertexArray.emplaceBack(0, 0, 0, 0);
            r.collisionVertexArrayExt.emplaceBack(e, -t.padding, -t.padding),
            r.collisionVertexArrayExt.emplaceBack(e, t.padding, -t.padding),
            r.collisionVertexArrayExt.emplaceBack(e, t.padding, t.padding),
            r.collisionVertexArrayExt.emplaceBack(e, -t.padding, t.padding),
            this._commitLayoutVertex(r.layoutVertexArray, n, s, a, c, h, new i(t.x1,t.y1)),
            this._commitLayoutVertex(r.layoutVertexArray, n, s, a, c, h, new i(t.x2,t.y1)),
            this._commitLayoutVertex(r.layoutVertexArray, n, s, a, c, h, new i(t.x2,t.y2)),
            this._commitLayoutVertex(r.layoutVertexArray, n, s, a, c, h, new i(t.x1,t.y2)),
            l.vertexLength += 4;
            const p = r.indexArray;
            p.emplaceBack(u, u + 1),
            p.emplaceBack(u + 1, u + 2),
            p.emplaceBack(u + 2, u + 3),
            p.emplaceBack(u + 3, u),
            l.primitiveLength += 4;
        }
        _addTextDebugCollisionBoxes(t, e, r, n, i, s) {
            for (let a = n; a < i; a++) {
                const n = r.get(a)
                  , i = this.getSymbolInstanceTextSize(t, s, e, a);
                this._addCollisionDebugVertices(n, i, this.textCollisionBox, n.projectedAnchorX, n.projectedAnchorY, n.projectedAnchorZ, s);
            }
        }
        _addIconDebugCollisionBoxes(t, e, r, n, i, s) {
            for (let a = n; a < i; a++) {
                const n = r.get(a)
                  , i = this.getSymbolInstanceIconSize(t, e, a);
                this._addCollisionDebugVertices(n, i, this.iconCollisionBox, n.projectedAnchorX, n.projectedAnchorY, n.projectedAnchorZ, s);
            }
        }
        generateCollisionDebugBuffers(t, e) {
            this.hasDebugData() && this.destroyDebugData(),
            this.textCollisionBox = new qd(la,Xh.members,xa),
            this.iconCollisionBox = new qd(la,Xh.members,xa);
            const r = Qh(this.iconSizeData, t)
              , n = Qh(this.textSizeData, t);
            for (let i = 0; i < this.symbolInstances.length; i++) {
                const s = this.symbolInstances.get(i);
                this._addTextDebugCollisionBoxes(n, t, e, s.textBoxStartIndex, s.textBoxEndIndex, s),
                this._addTextDebugCollisionBoxes(n, t, e, s.verticalTextBoxStartIndex, s.verticalTextBoxEndIndex, s),
                this._addIconDebugCollisionBoxes(r, t, e, s.iconBoxStartIndex, s.iconBoxEndIndex, s),
                this._addIconDebugCollisionBoxes(r, t, e, s.verticalIconBoxStartIndex, s.verticalIconBoxEndIndex, s);
            }
        }
        getSymbolInstanceTextSize(t, e, r, n) {
            const i = this.text.placedSymbolArray.get(e.rightJustifiedTextSymbolIndex >= 0 ? e.rightJustifiedTextSymbolIndex : e.centerJustifiedTextSymbolIndex >= 0 ? e.centerJustifiedTextSymbolIndex : e.leftJustifiedTextSymbolIndex >= 0 ? e.leftJustifiedTextSymbolIndex : e.verticalPlacedTextSymbolIndex >= 0 ? e.verticalPlacedTextSymbolIndex : n)
              , s = Wh(this.textSizeData, t, i) / Hh;
            return this.tilePixelRatio * s
        }
        getSymbolInstanceIconSize(t, e, r) {
            const n = this.symbolInstances.get(r)
              , i = this.icon.placedSymbolArray.get(n.placedIconSymbolIndex >= 0 ? n.placedIconSymbolIndex : r)
              , s = Wh(this.iconSizeData, t, i);
            return this.tilePixelRatio * s
        }
        _commitDebugCollisionVertexUpdate(t, e, r) {
            t.emplaceBack(e, -r, -r),
            t.emplaceBack(e, r, -r),
            t.emplaceBack(e, r, r),
            t.emplaceBack(e, -r, r);
        }
        _updateTextDebugCollisionBoxes(t, e, r, n, i, s) {
            for (let a = n; a < i; a++) {
                const n = r.get(a)
                  , i = this.getSymbolInstanceTextSize(t, s, e, a);
                this._commitDebugCollisionVertexUpdate(this.textCollisionBox.collisionVertexArrayExt, i, n.padding);
            }
        }
        _updateIconDebugCollisionBoxes(t, e, r, n, i) {
            for (let s = n; s < i; s++) {
                const n = r.get(s)
                  , i = this.getSymbolInstanceIconSize(t, e, s);
                this._commitDebugCollisionVertexUpdate(this.iconCollisionBox.collisionVertexArrayExt, i, n.padding);
            }
        }
        updateCollisionDebugBuffers(t, e) {
            if (!this.hasDebugData())
                return;
            this.hasTextCollisionBoxData() && this.textCollisionBox.collisionVertexArrayExt.clear(),
            this.hasIconCollisionBoxData() && this.iconCollisionBox.collisionVertexArrayExt.clear();
            const r = Qh(this.iconSizeData, t)
              , n = Qh(this.textSizeData, t);
            for (let i = 0; i < this.symbolInstances.length; i++) {
                const s = this.symbolInstances.get(i);
                this._updateTextDebugCollisionBoxes(n, t, e, s.textBoxStartIndex, s.textBoxEndIndex, s),
                this._updateTextDebugCollisionBoxes(n, t, e, s.verticalTextBoxStartIndex, s.verticalTextBoxEndIndex, s),
                this._updateIconDebugCollisionBoxes(r, t, e, s.iconBoxStartIndex, s.iconBoxEndIndex),
                this._updateIconDebugCollisionBoxes(r, t, e, s.verticalIconBoxStartIndex, s.verticalIconBoxEndIndex);
            }
            this.hasTextCollisionBoxData() && this.textCollisionBox.collisionVertexBufferExt && this.textCollisionBox.collisionVertexBufferExt.updateData(this.textCollisionBox.collisionVertexArrayExt),
            this.hasIconCollisionBoxData() && this.iconCollisionBox.collisionVertexBufferExt && this.iconCollisionBox.collisionVertexBufferExt.updateData(this.iconCollisionBox.collisionVertexArrayExt);
        }
        _deserializeCollisionBoxesForSymbol(t, e, r, n, i, s, a, o, l) {
            const u = {};
            for (let n = e; n < r; n++) {
                const e = t.get(n);
                u.textBox = {
                    x1: e.x1,
                    y1: e.y1,
                    x2: e.x2,
                    y2: e.y2,
                    padding: e.padding,
                    projectedAnchorX: e.projectedAnchorX,
                    projectedAnchorY: e.projectedAnchorY,
                    projectedAnchorZ: e.projectedAnchorZ,
                    tileAnchorX: e.tileAnchorX,
                    tileAnchorY: e.tileAnchorY
                },
                u.textFeatureIndex = e.featureIndex;
                break
            }
            for (let e = n; e < i; e++) {
                const r = t.get(e);
                u.verticalTextBox = {
                    x1: r.x1,
                    y1: r.y1,
                    x2: r.x2,
                    y2: r.y2,
                    padding: r.padding,
                    projectedAnchorX: r.projectedAnchorX,
                    projectedAnchorY: r.projectedAnchorY,
                    projectedAnchorZ: r.projectedAnchorZ,
                    tileAnchorX: r.tileAnchorX,
                    tileAnchorY: r.tileAnchorY
                },
                u.verticalTextFeatureIndex = r.featureIndex;
                break
            }
            for (let e = s; e < a; e++) {
                const r = t.get(e);
                u.iconBox = {
                    x1: r.x1,
                    y1: r.y1,
                    x2: r.x2,
                    y2: r.y2,
                    padding: r.padding,
                    projectedAnchorX: r.projectedAnchorX,
                    projectedAnchorY: r.projectedAnchorY,
                    projectedAnchorZ: r.projectedAnchorZ,
                    tileAnchorX: r.tileAnchorX,
                    tileAnchorY: r.tileAnchorY
                },
                u.iconFeatureIndex = r.featureIndex;
                break
            }
            for (let e = o; e < l; e++) {
                const r = t.get(e);
                u.verticalIconBox = {
                    x1: r.x1,
                    y1: r.y1,
                    x2: r.x2,
                    y2: r.y2,
                    padding: r.padding,
                    projectedAnchorX: r.projectedAnchorX,
                    projectedAnchorY: r.projectedAnchorY,
                    projectedAnchorZ: r.projectedAnchorZ,
                    tileAnchorX: r.tileAnchorX,
                    tileAnchorY: r.tileAnchorY
                },
                u.verticalIconFeatureIndex = r.featureIndex;
                break
            }
            return u
        }
        deserializeCollisionBoxes(t) {
            this.collisionArrays = [];
            for (let e = 0; e < this.symbolInstances.length; e++) {
                const r = this.symbolInstances.get(e);
                this.collisionArrays.push(this._deserializeCollisionBoxesForSymbol(t, r.textBoxStartIndex, r.textBoxEndIndex, r.verticalTextBoxStartIndex, r.verticalTextBoxEndIndex, r.iconBoxStartIndex, r.iconBoxEndIndex, r.verticalIconBoxStartIndex, r.verticalIconBoxEndIndex));
            }
        }
        hasTextData() {
            return this.text.segments.get().length > 0
        }
        hasIconData() {
            return this.icon.segments.get().length > 0
        }
        hasDebugData() {
            return this.textCollisionBox && this.iconCollisionBox
        }
        hasTextCollisionBoxData() {
            return this.hasDebugData() && this.textCollisionBox.segments.get().length > 0
        }
        hasIconCollisionBoxData() {
            return this.hasDebugData() && this.iconCollisionBox.segments.get().length > 0
        }
        addIndicesForPlacedSymbol(t, e) {
            const r = t.placedSymbolArray.get(e)
              , n = r.vertexStartIndex + 4 * r.numGlyphs;
            for (let e = r.vertexStartIndex; e < n; e += 4)
                t.indexArray.emplaceBack(e, e + 1, e + 2),
                t.indexArray.emplaceBack(e + 1, e + 2, e + 3);
        }
        getSortedSymbolIndexes(t) {
            if (this.sortedAngle === t && void 0 !== this.symbolInstanceIndexes)
                return this.symbolInstanceIndexes;
            const e = Math.sin(t)
              , r = Math.cos(t)
              , n = []
              , i = []
              , s = [];
            for (let t = 0; t < this.symbolInstances.length; ++t) {
                s.push(t);
                const a = this.symbolInstances.get(t);
                n.push(0 | Math.round(e * a.tileAnchorX + r * a.tileAnchorY)),
                i.push(a.featureIndex);
            }
            return s.sort(((t,e)=>n[t] - n[e] || i[e] - i[t])),
            s
        }
        addToSortKeyRanges(t, e) {
            const r = this.sortKeyRanges[this.sortKeyRanges.length - 1];
            r && r.sortKey === e ? r.symbolInstanceEnd = t + 1 : this.sortKeyRanges.push({
                sortKey: e,
                symbolInstanceStart: t,
                symbolInstanceEnd: t + 1
            });
        }
        sortFeatures(t) {
            if (this.sortFeaturesByY && this.sortedAngle !== t && !(this.text.segments.get().length > 1 || this.icon.segments.get().length > 1)) {
                this.symbolInstanceIndexes = this.getSortedSymbolIndexes(t),
                this.sortedAngle = t,
                this.text.indexArray.clear(),
                this.icon.indexArray.clear(),
                this.featureSortOrder = [];
                for (const t of this.symbolInstanceIndexes) {
                    const e = this.symbolInstances.get(t);
                    this.featureSortOrder.push(e.featureIndex),
                    [e.rightJustifiedTextSymbolIndex, e.centerJustifiedTextSymbolIndex, e.leftJustifiedTextSymbolIndex].forEach(((t,e,r)=>{
                        t >= 0 && r.indexOf(t) === e && this.addIndicesForPlacedSymbol(this.text, t);
                    }
                    )),
                    e.verticalPlacedTextSymbolIndex >= 0 && this.addIndicesForPlacedSymbol(this.text, e.verticalPlacedTextSymbolIndex),
                    e.placedIconSymbolIndex >= 0 && this.addIndicesForPlacedSymbol(this.icon, e.placedIconSymbolIndex),
                    e.verticalPlacedIconSymbolIndex >= 0 && this.addIndicesForPlacedSymbol(this.icon, e.verticalPlacedIconSymbolIndex);
                }
                this.text.indexBuffer && this.text.indexBuffer.updateData(this.text.indexArray),
                this.icon.indexBuffer && this.icon.indexBuffer.updateData(this.icon.indexArray);
            }
        }
    }
    Bi(Nd, "SymbolBucket", {
        omit: ["layers", "collisionBoxArray", "features", "compareText"]
    }),
    Nd.MAX_GLYPHS = 65535,
    Nd.addDynamicAttributes = Ud;
    const Zd = new qs({
        "symbol-placement": new Rs(qt.layout_symbol["symbol-placement"]),
        "symbol-spacing": new Rs(qt.layout_symbol["symbol-spacing"]),
        "symbol-avoid-edges": new Rs(qt.layout_symbol["symbol-avoid-edges"]),
        "symbol-sort-key": new js(qt.layout_symbol["symbol-sort-key"]),
        "symbol-z-order": new Rs(qt.layout_symbol["symbol-z-order"]),
        "icon-allow-overlap": new Rs(qt.layout_symbol["icon-allow-overlap"]),
        "icon-ignore-placement": new Rs(qt.layout_symbol["icon-ignore-placement"]),
        "icon-optional": new Rs(qt.layout_symbol["icon-optional"]),
        "icon-rotation-alignment": new Rs(qt.layout_symbol["icon-rotation-alignment"]),
        "icon-size": new js(qt.layout_symbol["icon-size"]),
        "icon-text-fit": new Rs(qt.layout_symbol["icon-text-fit"]),
        "icon-text-fit-padding": new Rs(qt.layout_symbol["icon-text-fit-padding"]),
        "icon-image": new js(qt.layout_symbol["icon-image"]),
        "icon-rotate": new js(qt.layout_symbol["icon-rotate"]),
        "icon-padding": new Rs(qt.layout_symbol["icon-padding"]),
        "icon-keep-upright": new Rs(qt.layout_symbol["icon-keep-upright"]),
        "icon-offset": new js(qt.layout_symbol["icon-offset"]),
        "icon-anchor": new js(qt.layout_symbol["icon-anchor"]),
        "icon-pitch-alignment": new Rs(qt.layout_symbol["icon-pitch-alignment"]),
        "text-pitch-alignment": new Rs(qt.layout_symbol["text-pitch-alignment"]),
        "text-rotation-alignment": new Rs(qt.layout_symbol["text-rotation-alignment"]),
        "text-field": new js(qt.layout_symbol["text-field"]),
        "text-font": new js(qt.layout_symbol["text-font"]),
        "text-size": new js(qt.layout_symbol["text-size"]),
        "text-max-width": new js(qt.layout_symbol["text-max-width"]),
        "text-line-height": new js(qt.layout_symbol["text-line-height"]),
        "text-letter-spacing": new js(qt.layout_symbol["text-letter-spacing"]),
        "text-justify": new js(qt.layout_symbol["text-justify"]),
        "text-radial-offset": new js(qt.layout_symbol["text-radial-offset"]),
        "text-variable-anchor": new Rs(qt.layout_symbol["text-variable-anchor"]),
        "text-anchor": new js(qt.layout_symbol["text-anchor"]),
        "text-max-angle": new Rs(qt.layout_symbol["text-max-angle"]),
        "text-writing-mode": new Rs(qt.layout_symbol["text-writing-mode"]),
        "text-rotate": new js(qt.layout_symbol["text-rotate"]),
        "text-padding": new Rs(qt.layout_symbol["text-padding"]),
        "text-keep-upright": new Rs(qt.layout_symbol["text-keep-upright"]),
        "text-transform": new js(qt.layout_symbol["text-transform"]),
        "text-offset": new js(qt.layout_symbol["text-offset"]),
        "text-allow-overlap": new Rs(qt.layout_symbol["text-allow-overlap"]),
        "text-ignore-placement": new Rs(qt.layout_symbol["text-ignore-placement"]),
        "text-optional": new Rs(qt.layout_symbol["text-optional"]),
        "symbol-scaleable": new js(qt.layout_symbol["symbol-scaleable"])
    });
    var Gd = {
        paint: new qs({
            "icon-opacity": new js(qt.paint_symbol["icon-opacity"]),
            "icon-color": new js(qt.paint_symbol["icon-color"]),
            "icon-halo-color": new js(qt.paint_symbol["icon-halo-color"]),
            "icon-halo-width": new js(qt.paint_symbol["icon-halo-width"]),
            "icon-halo-blur": new js(qt.paint_symbol["icon-halo-blur"]),
            "icon-translate": new Rs(qt.paint_symbol["icon-translate"]),
            "icon-translate-anchor": new Rs(qt.paint_symbol["icon-translate-anchor"]),
            "text-opacity": new js(qt.paint_symbol["text-opacity"]),
            "text-color": new js(qt.paint_symbol["text-color"],{
                runtimeType: ee,
                getOverride: t=>t.textColor,
                hasOverride: t=>!!t.textColor
            }),
            "text-halo-color": new js(qt.paint_symbol["text-halo-color"]),
            "text-halo-width": new js(qt.paint_symbol["text-halo-width"]),
            "text-halo-blur": new js(qt.paint_symbol["text-halo-blur"]),
            "text-translate": new Rs(qt.paint_symbol["text-translate"]),
            "text-translate-anchor": new Rs(qt.paint_symbol["text-translate-anchor"]),
            "symbol-minzoom": new js(qt.paint_symbol["symbol-minzoom"]),
            "symbol-maxzoom": new js(qt.paint_symbol["symbol-maxzoom"])
        }),
        layout: Zd
    };
    class Xd {
        constructor(t) {
            this.type = t.property.overrides ? t.property.overrides.runtimeType : Jt,
            this.defaultValue = t;
        }
        evaluate(t) {
            if (t.formattedSection) {
                const e = this.defaultValue.property.overrides;
                if (e && e.hasOverride(t.formattedSection))
                    return e.getOverride(t.formattedSection)
            }
            return t.feature && t.featureState ? this.defaultValue.evaluate(t.feature, t.featureState) : this.defaultValue.property.specification.default
        }
        eachChild(t) {
            this.defaultValue.isConstant() || t(this.defaultValue.value._styleExpression.expression);
        }
        outputDefined() {
            return !1
        }
        serialize() {
            return null
        }
    }
    Bi(Xd, "FormatSectionOverride", {
        omit: ["defaultValue"]
    });
    class Yd extends mo {
        constructor(t) {
            super(t, Gd);
        }
        recalculate(t, e) {
            super.recalculate(t, e),
            "auto" === this.layout.get("icon-rotation-alignment") && (this.layout._values["icon-rotation-alignment"] = "point" !== this.layout.get("symbol-placement") ? "map" : "viewport"),
            "auto" === this.layout.get("text-rotation-alignment") && (this.layout._values["text-rotation-alignment"] = "point" !== this.layout.get("symbol-placement") ? "map" : "viewport"),
            "auto" === this.layout.get("text-pitch-alignment") && (this.layout._values["text-pitch-alignment"] = this.layout.get("text-rotation-alignment")),
            "auto" === this.layout.get("icon-pitch-alignment") && (this.layout._values["icon-pitch-alignment"] = this.layout.get("icon-rotation-alignment"));
            const r = this.layout.get("text-writing-mode");
            if (r) {
                const t = [];
                for (const e of r)
                    t.indexOf(e) < 0 && t.push(e);
                this.layout._values["text-writing-mode"] = t;
            } else
                this.layout._values["text-writing-mode"] = "point" === this.layout.get("symbol-placement") ? ["horizontal"] : ["horizontal", "vertical"];
            this._setPaintOverrides();
        }
        getValueAndResolveTokens(t, e, r, n) {
            const i = this.layout.get(t).evaluate(e, {}, r, n)
              , s = this._unevaluatedLayout._values[t];
            return s.isDataDriven() || Pn(s.value) || !i ? i : function(t, e) {
                return e.replace(/{([^{}]+)}/g, ((e,r)=>r in t ? String(t[r]) : ""))
            }(e.properties, i)
        }
        createBucket(t) {
            return new Nd(t)
        }
        queryRadius() {
            return 0
        }
        queryIntersectsFeature() {
            return !1
        }
        _setPaintOverrides() {
            for (const t of Gd.paint.overridableProperties) {
                if (!Yd.hasPaintOverride(this.layout, t))
                    continue;
                const e = this.paint.get(t)
                  , r = new Xd(e)
                  , n = new Vn(r,e.property.specification);
                let i = null;
                i = "constant" === e.value.kind || "source" === e.value.kind ? new En("source",n) : new Fn("composite",n,e.value.zoomStops,e.value._interpolationType),
                this.paint._values[t] = new Fs(e.property,i,e.parameters);
            }
        }
        _handleOverridablePaintPropertyUpdate(t, e, r) {
            return !(!this.layout || e.isDataDriven() || r.isDataDriven()) && Yd.hasPaintOverride(this.layout, t)
        }
        static hasPaintOverride(t, e) {
            const r = t.get("text-field")
              , n = Gd.paint.properties[e];
            let i = !1;
            const s = t=>{
                for (const e of t)
                    if (n.overrides && n.overrides.hasOverride(e))
                        return void (i = !0)
            }
            ;
            if ("constant" === r.value.kind && r.value.value instanceof ve)
                s(r.value.value.sections);
            else if ("source" === r.value.kind) {
                const t = e=>{
                    i || (e instanceof Se && Ae(e.value) === se ? s(e.value.sections) : e instanceof Ce ? s(e.sections) : e.eachChild(t));
                }
                  , e = r.value;
                e._styleExpression && t(e._styleExpression.expression);
            }
            return i
        }
        getProgramConfiguration(t) {
            return new oo(this,t)
        }
    }
    var Hd = {
        paint: new qs({
            "background-color": new Rs(qt.paint_background["background-color"]),
            "background-pattern": new Os(qt.paint_background["background-pattern"]),
            "background-opacity": new Rs(qt.paint_background["background-opacity"])
        })
    }
      , Kd = {
        paint: new qs({
            "raster-opacity": new Rs(qt.paint_raster["raster-opacity"]),
            "raster-hue-rotate": new Rs(qt.paint_raster["raster-hue-rotate"]),
            "raster-brightness-min": new Rs(qt.paint_raster["raster-brightness-min"]),
            "raster-brightness-max": new Rs(qt.paint_raster["raster-brightness-max"]),
            "raster-saturation": new Rs(qt.paint_raster["raster-saturation"]),
            "raster-contrast": new Rs(qt.paint_raster["raster-contrast"]),
            "raster-resampling": new Rs(qt.paint_raster["raster-resampling"]),
            "raster-fade-duration": new Rs(qt.paint_raster["raster-fade-duration"])
        })
    };
    class Jd extends mo {
        constructor(t) {
            super(t, {}),
            this.implementation = t;
        }
        is3D() {
            return "3d" === this.implementation.renderingMode
        }
        hasOffscreenPass() {
            return void 0 !== this.implementation.prerender
        }
        recalculate() {}
        updateTransitions() {}
        hasTransition() {
            return !1
        }
        serialize() {}
        onAdd(t) {
            this.implementation.onAdd && this.implementation.onAdd(t, t.painter.context.gl);
        }
        onRemove(t) {
            this.implementation.onRemove && this.implementation.onRemove(t, t.painter.context.gl);
        }
    }
    var Wd = {
        paint: new qs({
            "sky-type": new Rs(qt.paint_sky["sky-type"]),
            "sky-atmosphere-sun": new Rs(qt.paint_sky["sky-atmosphere-sun"]),
            "sky-atmosphere-sun-intensity": new Rs(qt.paint_sky["sky-atmosphere-sun-intensity"]),
            "sky-gradient-center": new Rs(qt.paint_sky["sky-gradient-center"]),
            "sky-gradient-radius": new Rs(qt.paint_sky["sky-gradient-radius"]),
            "sky-gradient": new $s(qt.paint_sky["sky-gradient"]),
            "sky-atmosphere-halo-color": new Rs(qt.paint_sky["sky-atmosphere-halo-color"]),
            "sky-atmosphere-color": new Rs(qt.paint_sky["sky-atmosphere-color"]),
            "sky-opacity": new Rs(qt.paint_sky["sky-opacity"])
        })
    };
    function Qd(t, e, r) {
        const n = [0, 0, 1]
          , i = Iu([]);
        return Bu(i, i, r ? -l(t) + Math.PI : l(t)),
        Tu(i, i, -l(e)),
        bu(n, n, i),
        mu(n, n)
    }
    const ty = Ys([{
        name: "a_pos",
        components: 2,
        type: "Int16"
    }, {
        name: "a_eoffset",
        components: 2,
        type: "Float32"
    }, {
        name: "a_normal",
        components: 2,
        type: "Float32"
    }])
      , ey = Ys([{
        name: "a_ecolor",
        components: 1,
        type: "Float32"
    }, {
        name: "a_erotate",
        components: 1,
        type: "Float32"
    }, {
        name: "a_esize",
        components: 1,
        type: "Float32"
    }], 4)
      , ry = Ys([{
        name: "a_pos_3",
        components: 3,
        type: "Int16"
    }, {
        name: "a_pos_normal_3",
        components: 3,
        type: "Int16"
    }]);
    function ny(t, e, r, n, i, s, a) {
        t.emplaceBack(e, r, n, i, s, a);
    }
    function iy(t, e, r) {
        const n = 16384;
        t.emplaceBack(e.x, e.y, e.z, r[0] * n, r[1] * n, r[2] * n);
    }
    class sy {
        constructor(t) {
            this.zoom = t.zoom,
            this.overscaling = t.overscaling,
            this.layers = t.layers,
            this.layerIds = this.layers.map((t=>t.id)),
            this.index = t.index,
            this.hasPattern = !1,
            this.projection = t.projection,
            this.layoutVertexArray = new La,
            this.indexArray = new pa,
            this.segments = new vo,
            this.programConfigurations = new lo(t.layers,t.zoom),
            this.stateDependentLayerIds = this.layers.filter((t=>t.isStateDependent())).map((t=>t.id)),
            this.symbolIconArray = {},
            this.symbolFeatures = [],
            this.colorVertexArray = new ha;
        }
        populate(t, e, r, n) {
            const i = this.layers[0]
              , s = [];
            let a = null;
            "esymbol" === i.type && (a = i.layout.get("esymbol-sort-key"));
            let o = e.eleSymbolVertexs;
            for (const {feature: e, id: l, index: u, sourceLayerIndex: c} of t) {
                const t = this.layers[0]._featureFilter.needGeometry
                  , h = Al(e, t);
                if (!this.layers[0]._featureFilter.filter(new Ts(this.zoom), h, r))
                    continue;
                const p = a ? a.evaluate(h, {}, r) : void 0
                  , f = i.getValueAndResolveTokens("esymbol-id", e);
                f && (o[f] = !0);
                const d = {
                    id: l,
                    properties: e.properties,
                    type: e.type,
                    sourceLayerIndex: c,
                    index: u,
                    geometry: t ? h.geometry : wl(e, r, n),
                    patterns: {},
                    sortKey: p,
                    symbolId: f
                };
                s.push(d);
            }
            a && s.sort(((t,e)=>t.sortKey - e.sortKey)),
            "globe" === n.projection.name && (this.globeExtVertexArray = new Fa);
            for (const r of s) {
                const {geometry: n, index: i, sourceLayerIndex: s} = r
                  , a = t[i].feature;
                this.symbolFeatures.push(r),
                e.featureIndex.insert(a, n, i, s, this.index);
            }
        }
        addFeatures(t, e, r) {
            let n = null;
            "globe" === r.projection.name && (n = r.projection);
            for (const r of this.symbolFeatures) {
                let s = r.symbolId;
                if (s) {
                    if (!this.symbolIconArray[s]) {
                        var i = t[s];
                        if (!i) {
                            console.log("符号：" + s + "没有找到");
                            continue
                        }
                        this.symbolIconArray[s] = this.getSymbolData(i[0]),
                        this.symbolIconArray[s].CellsBound = {
                            right: i[1],
                            left: i[2],
                            top: i[3],
                            bottom: i[4]
                        };
                    }
                    this.addFeature(r, r.geometry, r.index, t, e, n);
                }
            }
        }
        update(t, e, r, n) {
            this.stateDependentLayers.length && this.programConfigurations.updatePaintArrays(t, e, this.stateDependentLayers, r, n);
        }
        isEmpty() {
            return 0 === this.layoutVertexArray.length
        }
        getProjection() {
            return this.projectionInstance || (this.projectionInstance = Ed(this.projection)),
            this.projectionInstance
        }
        uploadPending() {
            return !this.uploaded || this.programConfigurations.needsUpload
        }
        upload(t) {
            this.uploaded || (this.layoutVertexBuffer = t.createVertexBuffer(this.layoutVertexArray, ty.members),
            this.colorVertexBuffer = t.createVertexBuffer(this.colorVertexArray, ey.members, !0),
            this.indexBuffer = t.createIndexBuffer(this.indexArray),
            this.globeExtVertexArray && (this.globeExtVertexBuffer = t.createVertexBuffer(this.globeExtVertexArray, ry.members))),
            this.programConfigurations.upload(t),
            this.uploaded = !0;
        }
        destroy() {
            this.layoutVertexBuffer && (this.layoutVertexBuffer.destroy(),
            this.colorVertexBuffer.destroy(),
            this.indexBuffer.destroy(),
            this.programConfigurations.destroy(),
            this.segments.destroy(),
            this.globeExtVertexBuffer && this.globeExtVertexBuffer.destroy(),
            this.colorVertexArray.clear());
        }
        getLayoutValue(t, e, r) {
            const n = this.layers[0]
              , i = n.layout.get(t);
            var s = e;
            return "constant" !== i.value.kind || i.value.value && i.value.value.length > 0 ? s = n.getValueAndResolveTokens(t, r) : (i.value.value || 0 == i.value.value) && i.value.value.toString().length && (s = i.value.value),
            s
        }
        _perp2(t) {
            return [-t[1], t[0]]
        }
        countPath(t, e, r, n, i) {
            for (var s, a, o = n || "miter", l = i || "square", u = 2, c = t.length, h = t[c - 2] == t[0] && t[c - 1] == t[1], p = [], f = 0; f < c / 2; f++) {
                var d = {
                    x: t[2 * f],
                    y: t[2 * f + 1]
                }
                  , y = {
                    x: t[2 * (f - 1)],
                    y: t[2 * (f - 1) + 1]
                };
                f >= 1 && d.x == y.x && d.y == y.y || p.push((s = Cu(),
                a = d.y,
                s[0] = d.x,
                s[1] = a,
                s));
            }
            if (!((c = p.length) < (h ? 3 : 2))) {
                "bevel" === o && (u = 1.05);
                var m, g, x, v, b, _ = {
                    pointArray: [],
                    indexArray: [],
                    paintArray: [],
                    index: 0,
                    color: r,
                    normalVector: [],
                    len: 5
                }, w = e / 2;
                for (h && (m = p[c - 2],
                b = this._perp2(Fu(Cu(), Pu(Cu(), p[0], m)))),
                f = 0; f < c; f++) {
                    b && (v = b),
                    m && (g = m),
                    m = p[f],
                    b = (x = h && f == c - 1 ? p[1] : p[f + 1]) ? this._perp2(Fu(Cu(), Pu(Cu(), x, m))) : v,
                    v = v || b;
                    var A = Vu(Cu(), v, b);
                    0 == A[0] && 0 == A[1] || (A = Fu(Cu(), A));
                    var k = Lu(v, b)
                      , z = Lu(A, b)
                      , S = v[0] * b[1] - v[1] * b[0] > 0
                      , M = w / Math.sqrt((k + 1) / 2)
                      , I = 0 !== z ? 1 / z : 1 / 0
                      , T = g && x
                      , B = T ? o : h ? "butt" : l;
                    if (T && "round" === B && (I < 1.05 ? B = "miter" : I <= 2 && (B = "fakeround")),
                    "miter" === B && I > u && (B = "bevel"),
                    "bevel" === B && (I < 100 && I > 2 && (B = "flipbevel"),
                    I < u && (B = "miter")),
                    "miter" === B) {
                        if (A = Du(Cu(), A, M),
                        g) {
                            var C = Du(Cu(), v, w);
                            _ = this.addCurrentVertex(m, A, 0, 0, _, C);
                        }
                        if (x) {
                            var V = Du(Cu(), b, w);
                            _ = this.addCurrentVertex(m, A, 0, 0, _, V);
                        }
                    } else if ("flipbevel" === B) {
                        if (I > 100)
                            A = Du(Cu(), b, -1);
                        else {
                            var P = Vu(Cu(), v, b)
                              , D = Ru(Cu(), v, b);
                            const t = M * Eu(P) / Eu(D);
                            A = Du(Cu(), this._perp2(A), t * (S ? -1 : 1));
                        }
                        this.addCurrentVertex(m, A, 0, 0, _),
                        this.addCurrentVertex(m, Du(Cu(), A, -1), 0, 0, _);
                    } else if ("bevel" === B || "fakeround" === B) {
                        if (g && (A = Du(Cu(), v, w),
                        _ = this.addCurrentVertex(m, A, 0, 0, _)),
                        "fakeround" === B) {
                            var E = 2 * Math.sqrt(2 - 2 * z);
                            const t = Math.round(180 * E / Math.PI / 20);
                            for (let e = 1; e < t; e++) {
                                let r = e / t;
                                if (.5 !== r) {
                                    const t = r - .5;
                                    r += r * t * (r - 1) * ((1.0904 + k * (k * (3.55645 - 1.43519 * k) - 3.2452)) * t * t + (.848013 + k * (.215638 * k - 1.06021)));
                                }
                                var F = Ru(Cu(), b, v);
                                F = Du(Cu(), F, r),
                                F = Vu(Cu(), F, v),
                                F = Fu(Cu(), F),
                                F = Du(Cu(), F, w),
                                _ = this.addCurrentVertex(m, F, 0, 0, _);
                            }
                        }
                        x && (A = Du(Cu(), b, w),
                        _ = this.addCurrentVertex(m, A, 0, 0, _));
                    } else if ("butt" === B)
                        A = Du(Cu(), A, w),
                        _ = this.addCurrentVertex(m, A, 0, 0, _);
                    else if ("square" === B) {
                        var L = Fu(Cu(), Ru(Cu(), m, g || x));
                        L = Du(Cu(), L, w),
                        A = Du(Cu(), A, w),
                        this.addCurrentVertex(m, A, L, 0, _);
                    } else
                        "round" === B && (g && (this.addCurrentVertex(m, v, 0, 0, _),
                        this.addCurrentVertex(m, v, 1, 1, _)),
                        x && (this.addCurrentVertex(m, b, -1, -1, _),
                        this.addCurrentVertex(m, b, 0, 0, _)));
                }
                return _
            }
        }
        addCurrentVertex(t, e, r, n, i, s) {
            var a = Vu(Cu(), t, e)
              , o = Ru(Cu(), t, e);
            r && (a = Vu(Cu(), a, r),
            o = Vu(Cu(), o, r));
            var l = i.index;
            i.pointArray = i.pointArray.concat([a[0], a[1]]).concat([o[0], o[1]]);
            var u = s || e;
            return i.paintArray = i.paintArray.concat(i.color).concat([u[0], u[1]]).concat(i.color).concat([0 - u[0], 0 - u[1]]),
            l > 0 && (i.indexArray = i.indexArray.concat([l - 2, l - 1, l]),
            i.indexArray = i.indexArray.concat([l - 1, l, l + 1])),
            i.index += 2,
            i
        }
        getSymbolData(t) {
            var e = []
              , r = []
              , n = [];
            this.layers[0].paint.get("esymbol-color");
            for (var i = 0; i < t.length; i++) {
                var s = t[i]
                  , a = s[0] * s[1]
                  , o = s[3]
                  , l = s[4]
                  , u = []
                  , c = []
                  , h = [];
                if (7 == s[2] || 1 == l) {
                    if (1 == l || 8 == l) {
                        var p = [s[5], s[6]];
                        u = s.slice(7);
                    } else
                        u = s.slice(5);
                    c = sc(u);
                    for (let t = 0; t < u.length / 2; t++)
                        1 == l || 8 == l ? h.push(a, u[2 * t] - p[0], u[2 * t + 1] - p[1]) : h.push(a, 0, 0);
                } else {
                    if (8 == l)
                        var f = this.countPath(s.slice(5), o, a, "bevel", "butt");
                    else
                        f = this.countPath(s.slice(5), o, a);
                    u = f.pointArray,
                    c = f.indexArray,
                    h = f.paintArray;
                }
                c = c.map((function(t) {
                    return e.length / 2 + t
                }
                )),
                e = e.concat(u),
                r = r.concat(c),
                n = n.concat(h);
            }
            return {
                pointArray: e,
                indexArray: r,
                paintArray: n
            }
        }
        addFeature(t, e, r, n, i, s) {
            var a = this.getLayoutValue("esymbol-rotate", 0, t)
              , o = this.getLayoutValue("esymbol-size", 1, t)
              , l = this.getLayoutValue("esymbol-scaleable", !0, t)
              , u = this.layers[0].paint.get("esymbol-color").parameters.zoom >= 0;
            (a > 360 || a < -360) && (a %= 360),
            o < 0 && (o = 0 - o),
            o *= l ? 1 : -1;
            for (const r of e)
                for (const e of r) {
                    const r = e.x
                      , n = e.y;
                    if (r < 0 || r >= bo || n < 0 || n >= bo)
                        continue;
                    const l = this.symbolIconArray[t.symbolId];
                    var c = l.pointArray
                      , h = l.indexArray
                      , p = l.paintArray;
                    const v = this.segments.prepareSegment(c.length / 2, this.layoutVertexArray, this.indexArray, t.sortKey);
                    for (var f = Number(v.vertexLength), d = 0; d < h.length / 3; d++) {
                        var y = 3 * d;
                        this.indexArray.emplaceBack(f + h[y], f + h[y + 1], f + h[y + 2]),
                        v.primitiveLength++;
                    }
                    for (var m = 0; m < c.length / 4; m++) {
                        var g = 4 * m
                          , x = 6 * m;
                        if (ny(this.layoutVertexArray, r, n, c[g], c[g + 1], p[x + 1], p[x + 2]),
                        ny(this.layoutVertexArray, r, n, c[g + 2], c[g + 3], p[x + 4], p[x + 5]),
                        this.colorVertexArray.emplaceBack(!u && p[x] > 0 ? 0 - p[x] : p[x], a, o),
                        this.colorVertexArray.emplaceBack(!u && p[x + 3] > 0 ? 0 - p[x + 3] : p[x + 3], a, o),
                        s) {
                            const t = s.projectTilePoint(r, n, i)
                              , e = s.upVector(i, r, n)
                              , a = this.globeExtVertexArray;
                            iy(a, t, e),
                            iy(a, t, e);
                        }
                        v.vertexLength += 2;
                    }
                }
            this.programConfigurations.populatePaintArrays(this.layoutVertexArray.length, t, r, {}, [], i);
        }
    }
    Bi(sy, "EleSymbolBucket", {
        omit: ["layers"]
    });
    const ay = new qs({
        "esymbol-sort-key": new js(qt.layout_esymbol["esymbol-sort-key"]),
        "esymbol-id": new js(qt.layout_esymbol["esymbol-id"]),
        "esymbol-rotate": new js(qt.layout_esymbol["esymbol-rotate"]),
        "esymbol-size": new js(qt.layout_esymbol["esymbol-size"]),
        "esymbol-scaleable": new js(qt.layout_esymbol["esymbol-scaleable"])
    });
    var oy = {
        paint: new qs({
            "esymbol-radius": new js(qt.paint_esymbol["esymbol-radius"]),
            "esymbol-color": new js(qt.paint_esymbol["esymbol-color"]),
            "esymbol-blur": new js(qt.paint_esymbol["esymbol-blur"]),
            "esymbol-opacity": new js(qt.paint_esymbol["esymbol-opacity"]),
            "esymbol-translate": new Rs(qt.paint_esymbol["esymbol-translate"]),
            "esymbol-translate-anchor": new Rs(qt.paint_esymbol["esymbol-translate-anchor"]),
            "esymbol-stroke-width": new js(qt.paint_esymbol["esymbol-stroke-width"]),
            "esymbol-stroke-color": new js(qt.paint_esymbol["esymbol-stroke-color"]),
            "esymbol-stroke-opacity": new js(qt.paint_esymbol["esymbol-stroke-opacity"]),
            "esymbol-minzoom": new js(qt.paint_esymbol["esymbol-minzoom"]),
            "esymbol-maxzoom": new js(qt.paint_esymbol["esymbol-maxzoom"])
        }),
        layout: ay
    };
    const ly = lu(0, 0, 0)
      , uy = lu(0, 0, 1);
    function cy(t, e) {
        const r = su();
        return ly[2] = e,
        t.intersectsPlane(ly, uy, r),
        new i(r[0],r[1])
    }
    const hy = {
        circle: class extends mo {
            constructor(t) {
                super(t, Nl);
            }
            createBucket(t) {
                return new Sl(t)
            }
            queryRadius(t) {
                const e = t;
                return jl("circle-radius", this, e) + jl("circle-stroke-width", this, e) + Ul(this.paint.get("circle-translate"))
            }
            queryIntersectsFeature(t, e, r, n, i, s, a, o) {
                const l = $l(this.paint.get("circle-translate"), this.paint.get("circle-translate-anchor"), s.angle, t.pixelToTileUnitsFactor)
                  , u = this.paint.get("circle-radius").evaluate(e, r) + this.paint.get("circle-stroke-width").evaluate(e, r);
                return qu(t, n, s, a, o, "map" === this.paint.get("circle-pitch-alignment"), "map" === this.paint.get("circle-pitch-scale"), l, u)
            }
            getProgramIds() {
                return ["circle"]
            }
            getProgramConfiguration(t) {
                return new oo(this,t)
            }
        }
        ,
        heatmap: class extends mo {
            createBucket(t) {
                return new Yu(t)
            }
            constructor(t) {
                super(t, tc),
                this._updateColorRamp();
            }
            _handleSpecialPaintPropertyUpdate(t) {
                "heatmap-color" === t && this._updateColorRamp();
            }
            _updateColorRamp() {
                this.colorRamp = ec({
                    expression: this._transitionablePaint._values["heatmap-color"].value.expression,
                    evaluationKey: "heatmapDensity",
                    image: this.colorRamp
                }),
                this.colorRampTexture = null;
            }
            resize() {
                this.heatmapFbo && (this.heatmapFbo.destroy(),
                this.heatmapFbo = null);
            }
            queryRadius(t) {
                return jl("heatmap-radius", this, t)
            }
            queryIntersectsFeature(t, e, r, n, s, a, o, l) {
                const u = this.paint.get("heatmap-radius").evaluate(e, r);
                return qu(t, n, a, o, l, !0, !0, new i(0,0), u)
            }
            hasOffscreenPass() {
                return 0 !== this.paint.get("heatmap-opacity") && "none" !== this.visibility
            }
            getProgramIds() {
                return ["heatmap", "heatmapTexture"]
            }
            getProgramConfiguration(t) {
                return new oo(this,t)
            }
        }
        ,
        hillshade: class extends mo {
            constructor(t) {
                super(t, rc);
            }
            hasOffscreenPass() {
                return 0 !== this.paint.get("hillshade-exaggeration") && "none" !== this.visibility
            }
            getProgramIds() {
                return ["hillshade", "hillshadePrepare"]
            }
        }
        ,
        fill: class extends mo {
            constructor(t) {
                super(t, Nc);
            }
            getProgramIds() {
                const t = this.paint.get("fill-pattern")
                  , e = t && t.constantOr(1)
                  , r = [e ? "fillPattern" : "fill"];
                return this.paint.get("fill-antialias") && r.push(e && !this.getPaintProperty("fill-outline-color") ? "fillOutlinePattern" : "fillOutline"),
                r
            }
            getProgramConfiguration(t) {
                return new oo(this,t)
            }
            recalculate(t, e) {
                super.recalculate(t, e);
                const r = this.paint._values["fill-outline-color"];
                "constant" === r.value.kind && void 0 === r.value.value && (this.paint._values["fill-outline-color"] = this.paint._values["fill-color"]);
            }
            createBucket(t) {
                return new $c(t)
            }
            queryRadius() {
                return Ul(this.paint.get("fill-translate"))
            }
            queryIntersectsFeature(t, e, r, n, i, s) {
                return !t.queryGeometry.isAboveHorizon && Tl(Ol(t.tilespaceGeometry, this.paint.get("fill-translate"), this.paint.get("fill-translate-anchor"), s.angle, t.pixelToTileUnitsFactor), n)
            }
            isTileClipped() {
                return !0
            }
        }
        ,
        "fill-extrusion": class extends mo {
            constructor(t) {
                super(t, bh);
            }
            createBucket(t) {
                return new ch(t)
            }
            queryRadius() {
                return Ul(this.paint.get("fill-extrusion-translate"))
            }
            is3D() {
                return !0
            }
            getProgramIds() {
                return [this.paint.get("fill-extrusion-pattern").constantOr(1) ? "fillExtrusionPattern" : "fillExtrusion"]
            }
            getProgramConfiguration(t) {
                return new oo(this,t)
            }
            queryIntersectsFeature(t, e, r, n, s, a, o, l, u) {
                const c = $l(this.paint.get("fill-extrusion-translate"), this.paint.get("fill-extrusion-translate-anchor"), a.angle, t.pixelToTileUnitsFactor)
                  , h = this.paint.get("fill-extrusion-height").evaluate(e, r)
                  , p = this.paint.get("fill-extrusion-base").evaluate(e, r)
                  , f = [0, 0]
                  , d = l && a.elevation
                  , y = a.elevation ? a.elevation.exaggeration() : 1
                  , m = t.tile.getBucket(this);
                if (d && m instanceof ch) {
                    const t = m.centroidVertexArray
                      , e = u + 1;
                    if (e < t.length) {
                        const r = t.get(e);
                        f[0] = r.a_centroid_pos0,
                        f[1] = r.a_centroid_pos1;
                    }
                }
                if (0 === f[0] && 1 === f[1])
                    return !1;
                "globe" === a.projection.name && (n = xh([n], [new i(0,0), new i(bo,bo)], t.tileID.canonical).map((t=>t.polygon)).flat());
                const g = function(t, e, r, n, s, a, o, l, u, c, h) {
                    return "globe" === t.projection.name ? function(t, e, r, n, i, s, a, o, l, u, c) {
                        const h = []
                          , p = []
                          , f = t.projection.upVectorScale(c, t.center.lat, t.worldSize).metersToTile
                          , d = [0, 0, 0, 1]
                          , y = [0, 0, 0, 1]
                          , m = (t,e,r,n)=>{
                            t[0] = e,
                            t[1] = r,
                            t[2] = n,
                            t[3] = 1;
                        }
                          , g = gh();
                        r > 0 && (r += g),
                        n += g;
                        for (const g of e) {
                            const e = []
                              , x = [];
                            for (const h of g) {
                                const p = h.x + i.x
                                  , g = h.y + i.y
                                  , v = t.projection.projectTilePoint(p, g, c)
                                  , b = t.projection.upVector(c, h.x, h.y);
                                let _ = r
                                  , w = n;
                                if (a) {
                                    const t = Th(p, g, r, n, a, o, l, u);
                                    _ += t.base,
                                    w += t.top;
                                }
                                0 !== r ? m(d, v.x + b[0] * f * _, v.y + b[1] * f * _, v.z + b[2] * f * _) : m(d, v.x, v.y, v.z),
                                m(y, v.x + b[0] * f * w, v.y + b[1] * f * w, v.z + b[2] * f * w),
                                vu(d, d, s),
                                vu(y, y, s),
                                e.push(Ih(d)),
                                x.push(Ih(y));
                            }
                            h.push(e),
                            p.push(x);
                        }
                        return [h, p]
                    }(t, e, r, n, s, a, o, l, u, c, h) : o ? function(t, e, r, n, i, s, a, o, l) {
                        const u = []
                          , c = []
                          , h = [0, 0, 0, 1];
                        for (const p of t) {
                            const t = []
                              , f = [];
                            for (const u of p) {
                                const c = u.x + n.x
                                  , p = u.y + n.y
                                  , d = Th(c, p, e, r, s, a, o, l);
                                h[0] = c,
                                h[1] = p,
                                h[2] = d.base,
                                h[3] = 1,
                                Su(h, h, i),
                                h[3] = Math.max(h[3], 1e-5);
                                const y = Ih([h[0] / h[3], h[1] / h[3], h[2] / h[3]]);
                                h[0] = c,
                                h[1] = p,
                                h[2] = d.top,
                                h[3] = 1,
                                Su(h, h, i),
                                h[3] = Math.max(h[3], 1e-5);
                                const m = Ih([h[0] / h[3], h[1] / h[3], h[2] / h[3]]);
                                t.push(y),
                                f.push(m);
                            }
                            u.push(t),
                            c.push(f);
                        }
                        return [u, c]
                    }(e, r, n, s, a, o, l, u, c) : function(t, e, r, n, s) {
                        const a = []
                          , o = []
                          , l = s[8] * e
                          , u = s[9] * e
                          , c = s[10] * e
                          , h = s[11] * e
                          , p = s[8] * r
                          , f = s[9] * r
                          , d = s[10] * r
                          , y = s[11] * r;
                        for (const e of t) {
                            const t = []
                              , r = [];
                            for (const a of e) {
                                const e = a.x + n.x
                                  , o = a.y + n.y
                                  , m = s[0] * e + s[4] * o + s[12]
                                  , g = s[1] * e + s[5] * o + s[13]
                                  , x = s[2] * e + s[6] * o + s[14]
                                  , v = s[3] * e + s[7] * o + s[15]
                                  , b = m + l
                                  , _ = g + u
                                  , w = x + c
                                  , A = Math.max(v + h, 1e-5)
                                  , k = m + p
                                  , z = g + f
                                  , S = x + d
                                  , M = Math.max(v + y, 1e-5)
                                  , I = new i(b / A,_ / A);
                                I.z = w / A,
                                t.push(I);
                                const T = new i(k / M,z / M);
                                T.z = S / M,
                                r.push(T);
                            }
                            a.push(t),
                            o.push(r);
                        }
                        return [a, o]
                    }(e, r, n, s, a)
                }(a, n, p, h, c, o, d ? l : null, f, y, a.center.lat, t.tileID.canonical)
                  , x = t.queryGeometry;
                return function(t, e, r) {
                    let n = 1 / 0;
                    Tl(r, e) && (n = Mh(r, e[0]));
                    for (let i = 0; i < e.length; i++) {
                        const s = e[i]
                          , a = t[i];
                        for (let t = 0; t < s.length - 1; t++) {
                            const e = s[t]
                              , i = [e, s[t + 1], a[t + 1], a[t], e];
                            Ml(r, i) && (n = Math.min(n, Mh(r, i)));
                        }
                    }
                    return n !== 1 / 0 && n
                }(g[0], g[1], x.isPointQuery() ? x.screenBounds : x.screenGeometry)
            }
        }
        ,
        line: Uh,
        symbol: Yd,
        background: class extends mo {
            constructor(t) {
                super(t, Hd);
            }
            getProgramIds() {
                return [this.paint.get("background-pattern") ? "backgroundPattern" : "background"]
            }
        }
        ,
        raster: class extends mo {
            constructor(t) {
                super(t, Kd);
            }
            getProgramIds() {
                return ["raster"]
            }
        }
        ,
        sky: class extends mo {
            constructor(t) {
                super(t, Wd),
                this._updateColorRamp();
            }
            _handleSpecialPaintPropertyUpdate(t) {
                "sky-gradient" === t ? this._updateColorRamp() : "sky-atmosphere-sun" !== t && "sky-atmosphere-halo-color" !== t && "sky-atmosphere-color" !== t && "sky-atmosphere-sun-intensity" !== t || (this._skyboxInvalidated = !0);
            }
            _updateColorRamp() {
                this.colorRamp = ec({
                    expression: this._transitionablePaint._values["sky-gradient"].value.expression,
                    evaluationKey: "skyRadialProgress"
                }),
                this.colorRampTexture && (this.colorRampTexture.destroy(),
                this.colorRampTexture = null);
            }
            needsSkyboxCapture(t) {
                if (this._skyboxInvalidated || !this.skyboxTexture || !this.skyboxGeometry)
                    return !0;
                if (!this.paint.get("sky-atmosphere-sun")) {
                    const e = t.style.light.properties.get("position");
                    return this._lightPosition.azimuthal !== e.azimuthal || this._lightPosition.polar !== e.polar
                }
                return !1
            }
            getCenter(t, e) {
                if ("atmosphere" === this.paint.get("sky-type")) {
                    const r = this.paint.get("sky-atmosphere-sun")
                      , n = !r
                      , i = t.style.light
                      , s = i.properties.get("position");
                    return n && "viewport" === i.properties.get("anchor") && B("The sun direction is attached to a light with viewport anchor, lighting may behave unexpectedly."),
                    n ? Qd(s.azimuthal, 90 - s.polar, e) : Qd(r[0], 90 - r[1], e)
                }
                const r = this.paint.get("sky-gradient-center");
                return Qd(r[0], 90 - r[1], e)
            }
            is3D() {
                return !1
            }
            isSky() {
                return !0
            }
            markSkyboxValid(t) {
                this._skyboxInvalidated = !1,
                this._lightPosition = t.style.light.properties.get("position");
            }
            hasOffscreenPass() {
                return !0
            }
            getProgramIds() {
                const t = this.paint.get("sky-type");
                return "atmosphere" === t ? ["skyboxCapture", "skybox"] : "gradient" === t ? ["skyboxGradient"] : null
            }
        }
        ,
        esymbol: class extends mo {
            constructor(t) {
                super(t, oy);
            }
            createBucket(t) {
                return new sy(t)
            }
            getValueAndResolveTokens(t, e) {
                const r = this.layout.get(t).evaluate(e, {})
                  , n = this._unevaluatedLayout._values[t];
                return n.isDataDriven() || isExpression(n.value) ? r : resolveTokens(e.properties, r)
            }
            queryRadius(t) {
                const e = t;
                var r = e.symbolFeatures
                  , n = 0
                  , i = this.layout.get("esymbol-size").value
                  , s = this.layout.get("esymbol-scaleable").value;
                if ("constant" === i.kind)
                    n = i.value;
                else
                    for (var a = 0; a < r.length; a++) {
                        var o = this.getValueAndResolveTokens("esymbol-size", r[a]);
                        o > n && (n = o);
                    }
                return n = 2 * n * Math.sqrt(2),
                "constant" === s.kind ? s.value && (n *= Math.pow(2, e.zoom - 18)) : n = Math.max(n, n * Math.pow(2, e.zoom - 18)),
                n + Ul(this.paint.get("esymbol-translate"))
            }
            queryIntersectsFeature(t, e, r, n, i, s, a, o, l, u) {
                const c = $l(this.paint.get("esymbol-translate"), this.paint.get("esymbol-translate-anchor"), s.angle, t.pixelToTileUnitsFactor);
                let h = 2 * this.layout.get("esymbol-size").evaluate(e, r);
                const p = this.layout.get("esymbol-scaleable").evaluate(e, r)
                  , f = this.layout.get("esymbol-id").evaluate(e, r);
                if (!f && 0 != f || !u || !u.symbolIconArray || !u.symbolIconArray[f])
                    return !1;
                const d = u.symbolIconArray[f].CellsBound
                  , y = d.right - d.left
                  , m = d.top - d.bottom
                  , g = y / m;
                let x = this.layout.get("esymbol-rotate").evaluate(e, r);
                if (p && (h *= Math.pow(2, s.zoom - 18)),
                t.queryGeometry.isAboveHorizon)
                    return !1;
                h *= t.pixelToTileUnitsFactor;
                for (const e of n)
                    for (const r of e) {
                        const e = r.add(c)
                          , n = o && s.elevation ? s.elevation.exaggeration() * o.getElevationAt(e.x, e.y, !0) : 0
                          , i = e
                          , l = t.tilespaceRays.map((t=>cy(t, n)));
                        Su([], [r.x, r.y, n, 1], a);
                        let u = h;
                        u *= 2;
                        let p = u
                          , f = u;
                        g <= 1 ? p = u * g : f = u / g;
                        let I = Math.abs(d.right) / y * p
                          , T = Math.abs(d.left) / y * p
                          , B = Math.abs(d.top) / m * f
                          , C = Math.abs(d.bottom) / m * f
                          , V = [[{
                            x: i.x + I,
                            y: i.y + C
                        }, {
                            x: i.x - T,
                            y: i.y + C
                        }, {
                            x: i.x - T,
                            y: i.y - B
                        }, {
                            x: i.x + I,
                            y: i.y - B
                        }]];
                        if (0 != x && x % 360 != 0) {
                            x = x / 180 * Math.PI;
                            for (let t = 0; t < V[0].length; t++) {
                                var v = (b = Cu(),
                                A = x,
                                k = (_ = [V[0][t].x, V[0][t].y])[0] - (w = [i.x, i.y])[0],
                                z = _[1] - w[1],
                                S = Math.sin(A),
                                M = Math.cos(A),
                                b[0] = k * M - z * S + w[0],
                                b[1] = k * S + z * M + w[1],
                                b);
                                V[0][t] = {
                                    x: v[0],
                                    y: v[1]
                                };
                            }
                        }
                        if (V[0].push(V[0][0]),
                        Tl(l, V))
                            return !0
                    }
                var b, _, w, A, k, z, S, M;
                return !1
            }
            getProgramIds() {
                return ["eleSymbol"]
            }
            getProgramConfiguration(t) {
                return new oo(this,t)
            }
        }
        ,
        eline: Uh
    };
    class py {
        constructor(t, e, r, n) {
            this.context = t,
            this.format = r,
            this.texture = t.gl.createTexture(),
            this.update(e, n);
        }
        update(t, r, n) {
            const {width: i, height: s} = t
              , {context: a} = this
              , {gl: o} = a
              , {HTMLImageElement: l, HTMLCanvasElement: u, HTMLVideoElement: c, ImageData: h, ImageBitmap: p} = e;
            if (o.bindTexture(o.TEXTURE_2D, this.texture),
            a.pixelStoreUnpackFlipY.set(!1),
            a.pixelStoreUnpack.set(1),
            a.pixelStoreUnpackPremultiplyAlpha.set(this.format === o.RGBA && (!r || !1 !== r.premultiply)),
            n || this.size && this.size[0] === i && this.size[1] === s) {
                const {x: e, y: r} = n || {
                    x: 0,
                    y: 0
                };
                t instanceof l || t instanceof u || t instanceof c || t instanceof h || p && t instanceof p ? o.texSubImage2D(o.TEXTURE_2D, 0, e, r, o.RGBA, o.UNSIGNED_BYTE, t) : o.texSubImage2D(o.TEXTURE_2D, 0, e, r, i, s, o.RGBA, o.UNSIGNED_BYTE, t.data);
            } else
                this.size = [i, s],
                t instanceof l || t instanceof u || t instanceof c || t instanceof h || p && t instanceof p ? o.texImage2D(o.TEXTURE_2D, 0, this.format, this.format, o.UNSIGNED_BYTE, t) : o.texImage2D(o.TEXTURE_2D, 0, this.format, i, s, 0, this.format, o.UNSIGNED_BYTE, t.data);
            this.useMipmap = Boolean(r && r.useMipmap && this.isSizePowerOfTwo()),
            this.useMipmap && o.generateMipmap(o.TEXTURE_2D);
        }
        bind(t, e) {
            const {context: r} = this
              , {gl: n} = r;
            n.bindTexture(n.TEXTURE_2D, this.texture),
            t !== this.filter && (n.texParameteri(n.TEXTURE_2D, n.TEXTURE_MAG_FILTER, t),
            n.texParameteri(n.TEXTURE_2D, n.TEXTURE_MIN_FILTER, this.useMipmap ? t === n.NEAREST ? n.NEAREST_MIPMAP_NEAREST : n.LINEAR_MIPMAP_NEAREST : t),
            this.filter = t),
            e !== this.wrap && (n.texParameteri(n.TEXTURE_2D, n.TEXTURE_WRAP_S, e),
            n.texParameteri(n.TEXTURE_2D, n.TEXTURE_WRAP_T, e),
            this.wrap = e);
        }
        isSizePowerOfTwo() {
            return this.size[0] === this.size[1] && Math.log(this.size[0]) / Math.LN2 % 1 == 0
        }
        destroy() {
            const {gl: t} = this.context;
            t.deleteTexture(this.texture),
            this.texture = null;
        }
    }
    class fy {
        constructor(t, e) {
            this.width = t,
            this.height = e,
            this.nextRow = 0,
            this.image = new Wu({
                width: t,
                height: e
            }),
            this.positions = {},
            this.uploaded = !1;
        }
        getDash(t, e) {
            const r = this.getKey(t, e);
            return this.positions[r]
        }
        trim() {
            const t = this.width
              , e = this.height = A(this.nextRow);
            this.image.resize({
                width: t,
                height: e
            });
        }
        getKey(t, e) {
            return t.join(",") + e
        }
        getDashRanges(t, e, r) {
            const n = [];
            let i = t.length % 2 == 1 ? -t[t.length - 1] * r : 0
              , s = t[0] * r
              , a = !0;
            n.push({
                left: i,
                right: s,
                isDash: a,
                zeroLength: 0 === t[0]
            });
            let o = t[0];
            for (let e = 1; e < t.length; e++) {
                a = !a;
                const l = t[e];
                i = o * r,
                o += l,
                s = o * r,
                n.push({
                    left: i,
                    right: s,
                    isDash: a,
                    zeroLength: 0 === l
                });
            }
            return n
        }
        addRoundDash(t, e, r) {
            const n = e / 2;
            for (let e = -r; e <= r; e++) {
                const i = this.width * (this.nextRow + r + e);
                let s = 0
                  , a = t[s];
                for (let o = 0; o < this.width; o++) {
                    o / a.right > 1 && (a = t[++s]);
                    const l = Math.abs(o - a.left)
                      , u = Math.abs(o - a.right)
                      , c = Math.min(l, u);
                    let h;
                    const p = e / r * (n + 1);
                    if (a.isDash) {
                        const t = n - Math.abs(p);
                        h = Math.sqrt(c * c + t * t);
                    } else
                        h = n - Math.sqrt(c * c + p * p);
                    this.image.data[i + o] = Math.max(0, Math.min(255, h + 128));
                }
            }
        }
        addRegularDash(t, e) {
            for (let e = t.length - 1; e >= 0; --e) {
                const r = t[e]
                  , n = t[e + 1];
                r.zeroLength ? t.splice(e, 1) : n && n.isDash === r.isDash && (n.left = r.left,
                t.splice(e, 1));
            }
            const r = t[0]
              , n = t[t.length - 1];
            r.isDash === n.isDash && (r.left = n.left - this.width,
            n.right = r.right + this.width);
            const i = this.width * this.nextRow;
            let s = 0
              , a = t[s];
            for (let r = 0; r < this.width; r++) {
                r / a.right > 1 && (a = t[++s]);
                const n = Math.abs(r - a.left)
                  , o = Math.abs(r - a.right)
                  , l = Math.min(n, o);
                this.image.data[i + r] = Math.max(0, Math.min(255, (a.isDash ? l : -l) + e + 128));
            }
        }
        addDash(t, e) {
            const r = this.getKey(t, e);
            if (this.positions[r])
                return this.positions[r];
            const n = "round" === e
              , i = n ? 7 : 0
              , s = 2 * i + 1;
            if (this.nextRow + s > this.height)
                return B("LineAtlas out of space"),
                null;
            0 === t.length && t.push(1);
            let a = 0;
            for (let e = 0; e < t.length; e++)
                t[e] < 0 && (B("Negative value is found in line dasharray, replacing values with 0"),
                t[e] = 0),
                a += t[e];
            if (0 !== a) {
                const r = this.width / a
                  , s = this.getDashRanges(t, this.width, r);
                n ? this.addRoundDash(s, r, i) : this.addRegularDash(s, "square" === e ? .5 * r : 0);
            }
            const o = this.nextRow + i;
            this.nextRow += s;
            const l = {
                tl: [o, i],
                br: [a, 0]
            };
            return this.positions[r] = l,
            l
        }
    }
    Bi(fy, "LineAtlas");
    class dy {
        constructor(t) {
            this._callback = t,
            this._triggered = !1,
            "undefined" != typeof MessageChannel && (this._channel = new MessageChannel,
            this._channel.port2.onmessage = ()=>{
                this._triggered = !1,
                this._callback();
            }
            );
        }
        trigger() {
            this._triggered || (this._triggered = !0,
            this._channel ? this._channel.port1.postMessage(!0) : setTimeout((()=>{
                this._triggered = !1,
                this._callback();
            }
            ), 0));
        }
        remove() {
            this._channel = void 0,
            this._callback = ()=>{}
            ;
        }
    }
    class yy {
        constructor() {
            this.tasks = {},
            this.taskQueue = [],
            k(["process"], this),
            this.invoker = new dy(this.process),
            this.nextId = 0;
        }
        add(t, e) {
            const r = this.nextId++
              , n = function({type: t, isSymbolTile: e, zoom: r}) {
                return r = r || 0,
                "message" === t ? 0 : "maybePrepare" !== t || e ? "parseTile" !== t || e ? "parseTile" === t && e ? 300 - r : "maybePrepare" === t && e ? 400 - r : 500 : 200 - r : 100 - r
            }(e);
            if (0 === n) {
                P();
                try {
                    t();
                } finally {}
                return {
                    cancel: ()=>{}
                }
            }
            return this.tasks[r] = {
                fn: t,
                metadata: e,
                priority: n,
                id: r
            },
            this.taskQueue.push(r),
            this.invoker.trigger(),
            {
                cancel: ()=>{
                    delete this.tasks[r];
                }
            }
        }
        process() {
            P();
            try {
                if (this.taskQueue = this.taskQueue.filter((t=>!!this.tasks[t])),
                !this.taskQueue.length)
                    return;
                const t = this.pick();
                if (null === t)
                    return;
                const e = this.tasks[t];
                if (delete this.tasks[t],
                this.taskQueue.length && this.invoker.trigger(),
                !e)
                    return;
                e.fn();
            } finally {}
        }
        pick() {
            let t = null
              , e = 1 / 0;
            for (let r = 0; r < this.taskQueue.length; r++) {
                const n = this.tasks[this.taskQueue[r]];
                n.priority < e && (e = n.priority,
                t = r);
            }
            if (null === t)
                return null;
            const r = this.taskQueue[t];
            return this.taskQueue.splice(t, 1),
            r
        }
        remove() {
            this.invoker.remove();
        }
    }
    function my(t, e, r, n, i) {
        this.properties = {},
        this.extent = r,
        this.type = 0,
        this._pbf = t,
        this._geometry = -1,
        this._keys = n,
        this._values = i,
        t.readFields(gy, this, e);
    }
    function gy(t, e, r) {
        1 == t ? e.id = r.readVarint() : 2 == t ? function(t, e) {
            for (var r = t.readVarint() + t.pos; t.pos < r; ) {
                var n = e._keys[t.readVarint()]
                  , i = e._values[t.readVarint()];
                e.properties[n] = i;
            }
        }(r, e) : 3 == t ? e.type = r.readVarint() : 4 == t && (e._geometry = r.pos);
    }
    function xy(t) {
        for (var e, r, n = 0, i = 0, s = t.length, a = s - 1; i < s; a = i++)
            n += ((r = t[a]).x - (e = t[i]).x) * (e.y + r.y);
        return n
    }
    function vy(t, e, r) {
        this.version = 1,
        this.name = null,
        this.extent = 4096,
        this.length = 0,
        this._pbf = t,
        this._keys = [],
        this._values = [],
        this._features = [],
        t.readFields(by, this, e),
        this.length = this._features.length,
        this.tileID = r;
    }
    function by(t, e, r) {
        15 === t ? e.version = r.readVarint() : 1 === t ? e.name = r.readString() : 5 === t ? e.extent = r.readVarint() : 2 === t ? e._features.push(r.pos) : 3 === t ? e._keys.push(r.readString()) : 4 === t && e._values.push(function(t) {
            for (var e = null, r = t.readVarint() + t.pos; t.pos < r; ) {
                var n = t.readVarint() >> 3;
                e = 1 === n ? t.readString() : 2 === n ? t.readFloat() : 3 === n ? t.readDouble() : 4 === n ? t.readVarint64() : 5 === n ? t.readVarint() : 6 === n ? t.readSVarint() : 7 === n ? t.readBoolean() : null;
            }
            return e
        }(r));
    }
    my.types = ["Unknown", "Point", "LineString", "Polygon"],
    my.prototype.loadGeometry = function() {
        var t = this._pbf;
        t.pos = this._geometry;
        for (var e, r = t.readVarint() + t.pos, n = 1, s = 0, a = 0, o = 0, l = []; t.pos < r; ) {
            if (s <= 0) {
                var u = t.readVarint();
                n = 7 & u,
                s = u >> 3;
            }
            if (s--,
            1 === n || 2 === n)
                a += t.readSVarint(),
                o += t.readSVarint(),
                1 === n && (e && l.push(e),
                e = []),
                e.push(new i(a,o));
            else {
                if (7 !== n)
                    throw new Error("unknown command " + n);
                e && e.push(e[0].clone());
            }
        }
        return e && l.push(e),
        l
    }
    ,
    my.prototype.bbox = function() {
        var t = this._pbf;
        t.pos = this._geometry;
        for (var e = t.readVarint() + t.pos, r = 1, n = 0, i = 0, s = 0, a = 1 / 0, o = -1 / 0, l = 1 / 0, u = -1 / 0; t.pos < e; ) {
            if (n <= 0) {
                var c = t.readVarint();
                r = 7 & c,
                n = c >> 3;
            }
            if (n--,
            1 === r || 2 === r)
                (i += t.readSVarint()) < a && (a = i),
                i > o && (o = i),
                (s += t.readSVarint()) < l && (l = s),
                s > u && (u = s);
            else if (7 !== r)
                throw new Error("unknown command " + r)
        }
        return [a, l, o, u]
    }
    ,
    my.prototype.toGeoJSON = function(t, e, r) {
        var n, i, s = this.extent * Math.pow(2, r), a = this.extent * t, o = this.extent * e, l = this.loadGeometry(), u = my.types[this.type];
        let c = this.tileID && "Sg4326" == this.tileID.reference;
        var h = this.properties.resolution;
        let p = Number(this.type);
        function f(n) {
            for (var i = 0; i < n.length; i++) {
                var l = n[i];
                if (c) {
                    let s = dl(r, p, t, e, l.x, l.y, h);
                    n[i] = [s.lon, s.lat];
                } else
                    n[i] = [360 * (l.x + a) / s - 180, 360 / Math.PI * Math.atan(Math.exp((180 - 360 * (l.y + o) / s) * Math.PI / 180)) - 90];
            }
        }
        switch (this.type) {
        case 1:
            var d = [];
            for (n = 0; n < l.length; n++)
                d[n] = l[n][0];
            f(l = d);
            break;
        case 2:
            for (n = 0; n < l.length; n++)
                f(l[n]);
            break;
        case 3:
            for (l = function(t) {
                var e = t.length;
                if (e <= 1)
                    return [t];
                for (var r, n, i = [], s = 0; s < e; s++) {
                    var a = xy(t[s]);
                    0 !== a && (void 0 === n && (n = a < 0),
                    n === a < 0 ? (r && i.push(r),
                    r = [t[s]]) : r.push(t[s]));
                }
                return r && i.push(r),
                i
            }(l),
            n = 0; n < l.length; n++)
                for (i = 0; i < l[n].length; i++)
                    f(l[n][i]);
        }
        1 === l.length ? l = l[0] : u = "Multi" + u;
        var y = {
            type: "Feature",
            geometry: {
                type: u,
                coordinates: l
            },
            properties: this.properties
        };
        return "id"in this && (y.id = this.id),
        y
    }
    ,
    vy.prototype.feature = function(t) {
        if (t < 0 || t >= this._features.length)
            throw new Error("feature index out of bounds");
        this._pbf.pos = this._features[t];
        var e = this._pbf.readVarint() + this._pbf.pos
          , r = new my(this._pbf,e,this.extent,this._keys,this._values);
        return this.tileID && (r.tileID = this.tileID),
        r
    }
    ;
    var _y = {
        VectorTile: function(t, e, r) {
            this.layers = t.readFields((function(t, e, n) {
                if (3 === t) {
                    var i = new vy(n,n.readVarint() + n.pos,r);
                    i.length && (e[i.name] = i);
                }
            }
            ), {}, e);
        },
        VectorTileFeature: my,
        VectorTileLayer: vy
    };
    class wy {
        constructor(t) {
            this._stringToNumber = {},
            this._numberToString = [];
            for (let e = 0; e < t.length; e++) {
                const r = t[e];
                this._stringToNumber[r] = e,
                this._numberToString[e] = r;
            }
        }
        encode(t) {
            return this._stringToNumber[t]
        }
        decode(t) {
            return this._numberToString[t]
        }
    }
    const Ay = ["tile", "layer", "source", "sourceLayer", "state"];
    class ky {
        constructor(t, e, r, n, i) {
            this.type = "Feature",
            this._vectorTileFeature = t,
            this._z = e,
            this._x = r,
            this._y = n,
            this.properties = t.properties,
            this.id = i;
        }
        get geometry() {
            return void 0 === this._geometry && (this._geometry = this._vectorTileFeature.toGeoJSON(this._x, this._y, this._z).geometry),
            this._geometry
        }
        set geometry(t) {
            this._geometry = t;
        }
        toJSON() {
            const t = {
                type: "Feature",
                geometry: this.geometry,
                properties: this.properties
            };
            void 0 !== this.id && (t.id = this.id);
            for (const e of Ay)
                void 0 !== this[e] && (t[e] = this[e]);
            return t
        }
    }
    const zy = 32
      , Sy = 33
      , My = new Uint16Array(8184);
    for (let t = 0; t < 2046; t++) {
        let e = t + 2
          , r = 0
          , n = 0
          , i = 0
          , s = 0
          , a = 0
          , o = 0;
        for (1 & e ? i = s = a = zy : r = n = o = zy; (e >>= 1) > 1; ) {
            const t = r + i >> 1
              , l = n + s >> 1;
            1 & e ? (i = r,
            s = n,
            r = a,
            n = o) : (r = i,
            n = s,
            i = a,
            s = o),
            a = t,
            o = l;
        }
        const l = 4 * t;
        My[l + 0] = r,
        My[l + 1] = n,
        My[l + 2] = i,
        My[l + 3] = s;
    }
    const Iy = new Uint16Array(2178)
      , Ty = new Uint8Array(1089)
      , By = new Uint16Array(1089);
    function Cy(t) {
        return 0 === t ? -.03125 : 32 === t ? .03125 : 0
    }
    var Vy = Ys([{
        name: "a_pos",
        type: "Int16",
        components: 2
    }, {
        name: "a_texture_pos",
        type: "Int16",
        components: 2
    }]);
    const Py = {
        type: 2,
        extent: bo,
        loadGeometry: ()=>[[new i(0,0), new i(8193,0), new i(8193,8193), new i(0,8193), new i(0,0)]]
    };
    class Dy {
        constructor(t, e, r, n, i) {
            this.tileID = t,
            this.uid = w(),
            this.uses = 0,
            this.tileSize = e,
            this.tileZoom = r,
            this.buckets = {},
            this.expirationTime = null,
            this.queryPadding = 0,
            this.hasSymbolBuckets = !1,
            this.hasRTLText = !1,
            this.dependencies = {},
            this.isRaster = i,
            this.expiredRequestCount = 0,
            this.state = "loading",
            n && n.transform && (this.projection = n.transform.projection);
        }
        registerFadeDuration(t) {
            const e = t + this.timeAdded;
            e < N.now() || this.fadeEndTime && e < this.fadeEndTime || (this.fadeEndTime = e);
        }
        wasRequested() {
            return "errored" === this.state || "loaded" === this.state || "reloading" === this.state
        }
        get tileTransform() {
            return this._tileTransform || (this._tileTransform = dd(this.tileID.canonical, this.projection)),
            this._tileTransform
        }
        loadVectorData(t, e, r) {
            if (this.unloadVectorData(),
            this.state = "loaded",
            t) {
                t.featureIndex && (this.latestFeatureIndex = t.featureIndex,
                t.rawTileData ? (this.latestRawTileData = t.rawTileData,
                this.latestFeatureIndex.rawTileData = t.rawTileData) : this.latestRawTileData && (this.latestFeatureIndex.rawTileData = this.latestRawTileData)),
                this.collisionBoxArray = t.collisionBoxArray,
                this.buckets = function(t, e) {
                    const r = {};
                    if (!e)
                        return r;
                    for (const n of t) {
                        const t = n.layerIds.map((t=>e.getLayer(t))).filter(Boolean);
                        if (0 !== t.length) {
                            n.layers = t,
                            n.stateDependentLayerIds && (n.stateDependentLayers = n.stateDependentLayerIds.map((e=>t.filter((t=>t.id === e))[0])));
                            for (const e of t)
                                r[e.id] = n;
                        }
                    }
                    return r
                }(t.buckets, e.style),
                this.hasSymbolBuckets = !1;
                for (const t in this.buckets) {
                    const e = this.buckets[t];
                    if (e instanceof Nd) {
                        if (this.hasSymbolBuckets = !0,
                        !r)
                            break;
                        e.justReloaded = !0;
                    }
                }
                if (this.hasRTLText = !1,
                this.hasSymbolBuckets)
                    for (const t in this.buckets) {
                        const e = this.buckets[t];
                        if (e instanceof Nd && e.hasRTLText) {
                            this.hasRTLText = !0,
                            Is.isLoading() || Is.isLoaded() || "deferred" !== Ss() || Ms();
                            break
                        }
                    }
                this.queryPadding = 0;
                for (const t in this.buckets) {
                    const r = this.buckets[t];
                    this.queryPadding = Math.max(this.queryPadding, e.style.getLayer(t).queryRadius(r));
                }
                t.imageAtlas && (this.imageAtlas = t.imageAtlas),
                t.glyphAtlasImage && (this.glyphAtlasImage = t.glyphAtlasImage),
                t.lineAtlas && (this.lineAtlas = t.lineAtlas);
            } else
                this.collisionBoxArray = new ka;
        }
        unloadVectorData() {
            if (this.hasData()) {
                for (const t in this.buckets)
                    this.buckets[t].destroy();
                this.buckets = {},
                this.imageAtlas && (this.imageAtlas = null),
                this.lineAtlas && (this.lineAtlas = null),
                this.imageAtlasTexture && this.imageAtlasTexture.destroy(),
                this.glyphAtlasTexture && this.glyphAtlasTexture.destroy(),
                this.lineAtlasTexture && this.lineAtlasTexture.destroy(),
                this._tileBoundsBuffer && (this._tileBoundsBuffer.destroy(),
                this._tileBoundsIndexBuffer.destroy(),
                this._tileBoundsSegments.destroy(),
                this._tileBoundsBuffer = null),
                this._tileDebugBuffer && (this._tileDebugBuffer.destroy(),
                this._tileDebugSegments.destroy(),
                this._tileDebugBuffer = null),
                this._tileDebugIndexBuffer && (this._tileDebugIndexBuffer.destroy(),
                this._tileDebugIndexBuffer = null),
                this._globeTileDebugBorderBuffer && (this._globeTileDebugBorderBuffer.destroy(),
                this._globeTileDebugBorderBuffer = null),
                this._tileDebugTextBuffer && (this._tileDebugTextBuffer.destroy(),
                this._tileDebugTextSegments.destroy(),
                this._tileDebugTextIndexBuffer.destroy(),
                this._tileDebugTextBuffer = null),
                this._globeTileDebugTextBuffer && (this._globeTileDebugTextBuffer.destroy(),
                this._globeTileDebugTextBuffer = null),
                this.latestFeatureIndex = null,
                this.state = "unloaded";
            }
        }
        getBucket(t) {
            return this.buckets[t.id]
        }
        upload(t) {
            for (const e in this.buckets) {
                const r = this.buckets[e];
                r.uploadPending() && r.upload(t);
            }
            const e = t.gl;
            this.imageAtlas && !this.imageAtlas.uploaded && (this.imageAtlasTexture = new py(t,this.imageAtlas.image,e.RGBA),
            this.imageAtlas.uploaded = !0),
            this.glyphAtlasImage && (this.glyphAtlasTexture = new py(t,this.glyphAtlasImage,e.ALPHA),
            this.glyphAtlasImage = null),
            this.lineAtlas && !this.lineAtlas.uploaded && (this.lineAtlasTexture = new py(t,this.lineAtlas.image,e.ALPHA),
            this.lineAtlas.uploaded = !0);
        }
        prepare(t) {
            this.imageAtlas && this.imageAtlas.patchUpdatedImages(t, this.imageAtlasTexture);
        }
        queryRenderedFeatures(t, e, r, n, i, s, a, o) {
            return this.latestFeatureIndex && this.latestFeatureIndex.rawTileData ? this.latestFeatureIndex.query({
                tileResult: n,
                pixelPosMatrix: a,
                transform: s,
                params: i,
                tileTransform: this.tileTransform
            }, t, e, r, this.buckets) : {}
        }
        querySourceFeatures(t, e) {
            const r = this.latestFeatureIndex;
            if (!r || !r.rawTileData)
                return;
            const n = r.loadVTLayers()
              , i = e ? e.sourceLayer : ""
              , s = n._geojsonTileLayer || n[i];
            if (!s)
                return;
            const a = Hn(e && e.filter)
              , {z: o, x: l, y: u} = this.tileID.canonical
              , c = {
                z: o,
                x: l,
                y: u
            };
            for (let e = 0; e < s.length; e++) {
                const n = s.feature(e);
                if (a.needGeometry) {
                    const t = Al(n, !0);
                    if (!a.filter(new Ts(this.tileID.overscaledZ), t, this.tileID.canonical))
                        continue
                } else if (!a.filter(new Ts(this.tileID.overscaledZ), n))
                    continue;
                const h = r.getId(n, i)
                  , p = new ky(n,o,l,u,h);
                p.tile = c,
                t.push(p);
            }
        }
        hasData() {
            return "loaded" === this.state || "reloading" === this.state || "expired" === this.state
        }
        patternsLoaded() {
            return !!this.imageAtlas && !!Object.keys(this.imageAtlas.patternPositions).length
        }
        setExpiryData(t) {
            const e = this.expirationTime;
            if (t.cacheControl) {
                const e = D(t.cacheControl);
                e["max-age"] && (this.expirationTime = Date.now() + 1e3 * e["max-age"]);
            } else
                t.expires && (this.expirationTime = new Date(t.expires).getTime());
            if (this.expirationTime) {
                const t = Date.now();
                let r = !1;
                if (this.expirationTime > t)
                    r = !1;
                else if (e)
                    if (this.expirationTime < e)
                        r = !0;
                    else {
                        const n = this.expirationTime - e;
                        n ? this.expirationTime = t + Math.max(n, 3e4) : r = !0;
                    }
                else
                    r = !0;
                r ? (this.expiredRequestCount++,
                this.state = "expired") : this.expiredRequestCount = 0;
            }
        }
        getExpiryTimeout() {
            if (this.expirationTime)
                return this.expiredRequestCount ? 1e3 * (1 << Math.min(this.expiredRequestCount - 1, 31)) : Math.min(this.expirationTime - (new Date).getTime(), Math.pow(2, 31) - 1)
        }
        setFeatureState(t, e) {
            if (!this.latestFeatureIndex || !this.latestFeatureIndex.rawTileData || 0 === Object.keys(t).length || !e)
                return;
            const r = this.latestFeatureIndex.loadVTLayers()
              , n = e.style.listImages();
            for (const i in this.buckets) {
                if (!e.style.hasLayer(i))
                    continue;
                const s = this.buckets[i]
                  , a = s.layers[0].sourceLayer || "_geojsonTileLayer"
                  , o = r[a]
                  , l = t[a];
                if (!o || !l || 0 === Object.keys(l).length)
                    continue;
                if (s.update(l, o, n, this.imageAtlas && this.imageAtlas.patternPositions || {}),
                s instanceof Fh || s instanceof $c) {
                    const t = e.style._getSourceCache(s.layers[0].source);
                    e._terrain && e._terrain.enabled && t && s.programConfigurations.needsUpload && e._terrain._clearRenderCacheForTile(t.id, this.tileID);
                }
                const u = e && e.style && e.style.getLayer(i);
                u && (this.queryPadding = Math.max(this.queryPadding, u.queryRadius(s)));
            }
        }
        holdingForFade() {
            return void 0 !== this.symbolFadeHoldUntil
        }
        symbolFadeFinished() {
            return !this.symbolFadeHoldUntil || this.symbolFadeHoldUntil < N.now()
        }
        clearFadeHold() {
            this.symbolFadeHoldUntil = void 0;
        }
        setHoldDuration(t) {
            this.symbolFadeHoldUntil = N.now() + t;
        }
        setTexture(t, e) {
            const r = e.context
              , n = r.gl;
            this.texture = e.getTileTexture(t.width),
            this.texture ? this.texture.update(t, {
                useMipmap: !0
            }) : (this.texture = new py(r,t,n.RGBA,{
                useMipmap: !0
            }),
            this.texture.bind(n.LINEAR, n.CLAMP_TO_EDGE),
            r.extTextureFilterAnisotropic && n.texParameterf(n.TEXTURE_2D, r.extTextureFilterAnisotropic.TEXTURE_MAX_ANISOTROPY_EXT, r.extTextureFilterAnisotropicMax));
        }
        setDependencies(t, e) {
            const r = {};
            for (const t of e)
                r[t] = !0;
            this.dependencies[t] = r;
        }
        hasDependency(t, e) {
            for (const r of t) {
                const t = this.dependencies[r];
                if (t)
                    for (const r of e)
                        if (t[r])
                            return !0
            }
            return !1
        }
        clearQueryDebugViz() {}
        _makeDebugTileBoundsBuffers(t, e) {
            if (!e || "mercator" === e.name || this._tileDebugBuffer)
                return;
            const r = wl(Py, this.tileID.canonical, this.tileTransform)[0]
              , n = new Ks
              , i = new va;
            for (let t = 0; t < r.length; t++) {
                const {x: e, y: s} = r[t];
                n.emplaceBack(e, s),
                i.emplaceBack(t);
            }
            i.emplaceBack(0),
            this._tileDebugIndexBuffer = t.createIndexBuffer(i),
            this._tileDebugBuffer = t.createVertexBuffer(n, Ff.members),
            this._tileDebugSegments = vo.simpleSegment(0, 0, n.length, i.length);
        }
        _makeTileBoundsBuffers(t, e) {
            if (this._tileBoundsBuffer || !e || "mercator" === e.name)
                return;
            const r = wl(Py, this.tileID.canonical, this.tileTransform)[0];
            let n, i;
            if (this.isRaster) {
                const t = function(t, e) {
                    const r = dd(t, e)
                      , n = Math.pow(2, t.z);
                    for (let i = 0; i < Sy; i++)
                        for (let s = 0; s < Sy; s++) {
                            const a = Wo((t.x + (s + Cy(s)) / zy) / n)
                              , o = Qo((t.y + (i + Cy(i)) / zy) / n)
                              , l = e.project(a, o)
                              , u = i * Sy + s;
                            Iy[2 * u + 0] = Math.round((l.x * r.scale - r.x) * bo),
                            Iy[2 * u + 1] = Math.round((l.y * r.scale - r.y) * bo);
                        }
                    Ty.fill(0),
                    By.fill(0);
                    for (let t = 2045; t >= 0; t--) {
                        const e = 4 * t
                          , r = My[e + 0]
                          , n = My[e + 1]
                          , i = My[e + 2]
                          , s = My[e + 3]
                          , a = r + i >> 1
                          , o = n + s >> 1
                          , l = a + o - n
                          , u = o + r - a
                          , c = n * Sy + r
                          , h = s * Sy + i
                          , p = o * Sy + a
                          , f = Math.hypot((Iy[2 * c + 0] + Iy[2 * h + 0]) / 2 - Iy[2 * p + 0], (Iy[2 * c + 1] + Iy[2 * h + 1]) / 2 - Iy[2 * p + 1]) >= 16;
                        if (Ty[p] = Ty[p] || (f ? 1 : 0),
                        t < 1022) {
                            const t = (n + u >> 1) * Sy + (r + l >> 1)
                              , e = (s + u >> 1) * Sy + (i + l >> 1);
                            Ty[p] = Ty[p] || Ty[t] || Ty[e];
                        }
                    }
                    const i = new Ws
                      , s = new pa;
                    let a = 0;
                    function o(t, e) {
                        const r = e * Sy + t;
                        return 0 === By[r] && (i.emplaceBack(Iy[2 * r + 0], Iy[2 * r + 1], t * bo / zy, e * bo / zy),
                        By[r] = ++a),
                        By[r] - 1
                    }
                    function l(t, e, r, n, i, a) {
                        const u = t + r >> 1
                          , c = e + n >> 1;
                        if (Math.abs(t - i) + Math.abs(e - a) > 1 && Ty[c * Sy + u])
                            l(i, a, t, e, u, c),
                            l(r, n, i, a, u, c);
                        else {
                            const l = o(t, e)
                              , u = o(r, n)
                              , c = o(i, a);
                            s.emplaceBack(l, u, c);
                        }
                    }
                    return l(0, 0, zy, zy, zy, 0),
                    l(zy, zy, 0, 0, 0, zy),
                    {
                        vertices: i,
                        indices: s
                    }
                }(this.tileID.canonical, e);
                n = t.vertices,
                i = t.indices;
            } else {
                n = new Ws,
                i = new pa;
                for (const {x: t, y: e} of r)
                    n.emplaceBack(t, e, 0, 0);
                const t = sc(n.int16, void 0, 4);
                for (let e = 0; e < t.length; e += 3)
                    i.emplaceBack(t[e], t[e + 1], t[e + 2]);
            }
            this._tileBoundsBuffer = t.createVertexBuffer(n, Vy.members),
            this._tileBoundsIndexBuffer = t.createIndexBuffer(i),
            this._tileBoundsSegments = vo.simpleSegment(0, 0, n.length, i.length);
        }
        _makeGlobeTileDebugBuffers(t, e) {
            const r = e.projection;
            if (!r || "globe" !== r.name || e.freezeTileCoverage)
                return;
            const n = this.tileID.canonical
              , i = sd(Hf(n, e))
              , s = ld(e.zoom);
            let a;
            s > 0 && (a = Kl(new Float64Array(16), e.globeMatrix));
            const o = (n.x + .5) / (1 << n.z) - Ho(e.center.lng);
            let l = 0;
            o > .5 ? l = -1 : o < -.5 && (l = 1),
            this._makeGlobeTileDebugBorderBuffer(t, n, e, i, a, s, l),
            this._makeGlobeTileDebugTextBuffer(t, n, e, i, a, s, l);
        }
        _globePoint(t, e, r, n, i, s, a, o) {
            let l = rd(t, e, r);
            if (s) {
                const i = 1 << r.z
                  , u = [((t / bo + r.x) / i + o) * n, gl(e, r) / i * n, 0];
                vu(u, u, s),
                l = Yf(l, u, a);
            }
            return vu(l, l, i)
        }
        _makeGlobeTileDebugBorderBuffer(t, e, r, n, i, s, a) {
            const o = new Ks
              , l = new va
              , u = new Js
              , c = (t,c,h,p,f)=>{
                const d = (h - t) / (f - 1)
                  , y = (p - c) / (f - 1)
                  , m = o.length;
                for (let h = 0; h < f; h++) {
                    const p = t + h * d
                      , f = c + h * y;
                    o.emplaceBack(p, f);
                    const g = this._globePoint(p, f, e, r.worldSize, n, i, s, a);
                    u.emplaceBack(g[0], g[1], g[2]),
                    l.emplaceBack(m + h);
                }
            }
              , h = bo;
            c(0, 0, h, 0, 16),
            c(h, 0, h, h, 16),
            c(h, h, 0, h, 16),
            c(0, h, 0, 0, 16),
            this._tileDebugIndexBuffer = t.createIndexBuffer(l),
            this._tileDebugBuffer = t.createVertexBuffer(o, Ff.members),
            this._globeTileDebugBorderBuffer = t.createVertexBuffer(u, Ef.members),
            this._tileDebugSegments = vo.simpleSegment(0, 0, o.length, l.length);
        }
        _makeGlobeTileDebugTextBuffer(t, e, r, n, i, s, a) {
            const o = new Ks
              , l = new pa
              , u = new Js
              , c = 25;
            l.reserve(32),
            o.reserve(c),
            u.reserve(c);
            const h = (t,e)=>c * t + e;
            for (let t = 0; t < c; t++) {
                const l = 2048 * t;
                for (let t = 0; t < c; t++) {
                    const c = 2048 * t;
                    o.emplaceBack(c, l);
                    const h = this._globePoint(c, l, e, r.worldSize, n, i, s, a);
                    u.emplaceBack(h[0], h[1], h[2]);
                }
            }
            for (let t = 0; t < 4; t++)
                for (let e = 0; e < 4; e++) {
                    const r = h(t, e)
                      , n = h(t, e + 1)
                      , i = h(t + 1, e)
                      , s = h(t + 1, e + 1);
                    l.emplaceBack(r, n, i),
                    l.emplaceBack(i, n, s);
                }
            this._tileDebugTextIndexBuffer = t.createIndexBuffer(l),
            this._tileDebugTextBuffer = t.createVertexBuffer(o, Ff.members),
            this._globeTileDebugTextBuffer = t.createVertexBuffer(u, Ef.members),
            this._tileDebugTextSegments = vo.simpleSegment(0, 0, c, 32);
        }
    }
    class Ey {
        constructor() {
            this.state = {},
            this.stateChanges = {},
            this.deletedStates = {};
        }
        updateState(t, e, r) {
            const n = String(e);
            if (this.stateChanges[t] = this.stateChanges[t] || {},
            this.stateChanges[t][n] = this.stateChanges[t][n] || {},
            v(this.stateChanges[t][n], r),
            null === this.deletedStates[t]) {
                this.deletedStates[t] = {};
                for (const e in this.state[t])
                    e !== n && (this.deletedStates[t][e] = null);
            } else if (this.deletedStates[t] && null === this.deletedStates[t][n]) {
                this.deletedStates[t][n] = {};
                for (const e in this.state[t][n])
                    r[e] || (this.deletedStates[t][n][e] = null);
            } else
                for (const e in r)
                    this.deletedStates[t] && this.deletedStates[t][n] && null === this.deletedStates[t][n][e] && delete this.deletedStates[t][n][e];
        }
        removeFeatureState(t, e, r) {
            if (null === this.deletedStates[t])
                return;
            const n = String(e);
            if (this.deletedStates[t] = this.deletedStates[t] || {},
            r && void 0 !== e)
                null !== this.deletedStates[t][n] && (this.deletedStates[t][n] = this.deletedStates[t][n] || {},
                this.deletedStates[t][n][r] = null);
            else if (void 0 !== e)
                if (this.stateChanges[t] && this.stateChanges[t][n])
                    for (r in this.deletedStates[t][n] = {},
                    this.stateChanges[t][n])
                        this.deletedStates[t][n][r] = null;
                else
                    this.deletedStates[t][n] = null;
            else
                this.deletedStates[t] = null;
        }
        getState(t, e) {
            const r = String(e)
              , n = v({}, (this.state[t] || {})[r], (this.stateChanges[t] || {})[r]);
            if (null === this.deletedStates[t])
                return {};
            if (this.deletedStates[t]) {
                const r = this.deletedStates[t][e];
                if (null === r)
                    return {};
                for (const t in r)
                    delete n[t];
            }
            return n
        }
        initializeTileState(t, e) {
            t.setFeatureState(this.state, e);
        }
        coalesceChanges(t, e) {
            const r = {};
            for (const t in this.stateChanges) {
                this.state[t] = this.state[t] || {};
                const e = {};
                for (const r in this.stateChanges[t])
                    this.state[t][r] || (this.state[t][r] = {}),
                    v(this.state[t][r], this.stateChanges[t][r]),
                    e[r] = this.state[t][r];
                r[t] = e;
            }
            for (const t in this.deletedStates) {
                this.state[t] = this.state[t] || {};
                const e = {};
                if (null === this.deletedStates[t])
                    for (const r in this.state[t])
                        e[r] = {},
                        this.state[t][r] = {};
                else
                    for (const r in this.deletedStates[t]) {
                        if (null === this.deletedStates[t][r])
                            this.state[t][r] = {};
                        else
                            for (const e of Object.keys(this.deletedStates[t][r]))
                                delete this.state[t][r][e];
                        e[r] = this.state[t][r];
                    }
                r[t] = r[t] || {},
                v(r[t], e);
            }
            if (this.stateChanges = {},
            this.deletedStates = {},
            0 !== Object.keys(r).length)
                for (const n in t)
                    t[n].setFeatureState(r, e);
        }
    }
    class Fy {
        constructor(t) {
            this.size = t,
            this.minimums = [],
            this.maximums = [],
            this.leaves = [];
        }
        getElevation(t, e) {
            const r = this.toIdx(t, e);
            return {
                min: this.minimums[r],
                max: this.maximums[r]
            }
        }
        isLeaf(t, e) {
            return this.leaves[this.toIdx(t, e)]
        }
        toIdx(t, e) {
            return e * this.size + t
        }
    }
    function Ly(t, e, r, n) {
        let i = 0
          , s = Number.MAX_VALUE;
        for (let a = 0; a < 3; a++)
            if (Math.abs(n[a]) < 1e-15) {
                if (r[a] < t[a] || r[a] > e[a])
                    return null
            } else {
                const o = 1 / n[a];
                let l = (t[a] - r[a]) * o
                  , u = (e[a] - r[a]) * o;
                if (l > u) {
                    const t = l;
                    l = u,
                    u = t;
                }
                if (l > i && (i = l),
                u < s && (s = u),
                i > s)
                    return null
            }
        return i
    }
    function Ry(t, e, r, n, i, s, a, o, l, u, c) {
        const h = n - t
          , p = i - e
          , f = s - r
          , d = a - t
          , y = o - e
          , m = l - r
          , g = c[1] * m - c[2] * y
          , x = c[2] * d - c[0] * m
          , v = c[0] * y - c[1] * d
          , b = h * g + p * x + f * v;
        if (Math.abs(b) < 1e-15)
            return null;
        const _ = 1 / b
          , w = u[0] - t
          , A = u[1] - e
          , k = u[2] - r
          , z = (w * g + A * x + k * v) * _;
        if (z < 0 || z > 1)
            return null;
        const S = A * f - k * p
          , M = k * h - w * f
          , I = w * p - A * h
          , T = (c[0] * S + c[1] * M + c[2] * I) * _;
        return T < 0 || z + T > 1 ? null : (d * S + y * M + m * I) * _
    }
    function jy(t, e, r) {
        return (t - e) / (r - e)
    }
    function Uy(t, e, r, n, i, s, a, o, l) {
        const u = 1 << r
          , c = s - n
          , h = a - i
          , p = (t + 1) / u * c + n
          , f = (e + 0) / u * h + i
          , d = (e + 1) / u * h + i;
        o[0] = (t + 0) / u * c + n,
        o[1] = f,
        l[0] = p,
        l[1] = d;
    }
    class Oy {
        constructor(t) {
            if (this.maximums = [],
            this.minimums = [],
            this.leaves = [],
            this.childOffsets = [],
            this.nodeCount = 0,
            this.dem = t,
            this._siblingOffset = [[0, 0], [1, 0], [0, 1], [1, 1]],
            !this.dem)
                return;
            const e = function(t) {
                const e = Math.ceil(Math.log2(t.dim / 8))
                  , r = [];
                let n = Math.ceil(Math.pow(2, e));
                const i = 1 / n
                  , s = (t,e,r,n,i)=>{
                    const s = n ? 1 : 0
                      , a = (t + 1) * r - s
                      , o = e * r
                      , l = (e + 1) * r - s;
                    i[0] = t * r,
                    i[1] = o,
                    i[2] = a,
                    i[3] = l;
                }
                ;
                let a = new Fy(n);
                const o = [];
                for (let e = 0; e < n * n; e++) {
                    s(e % n, Math.floor(e / n), i, !1, o);
                    const r = qy(o[0], o[1], t)
                      , l = qy(o[2], o[1], t)
                      , u = qy(o[2], o[3], t)
                      , c = qy(o[0], o[3], t);
                    a.minimums.push(Math.min(r, l, u, c)),
                    a.maximums.push(Math.max(r, l, u, c)),
                    a.leaves.push(1);
                }
                for (r.push(a),
                n /= 2; n >= 1; n /= 2) {
                    const t = r[r.length - 1];
                    a = new Fy(n);
                    for (let e = 0; e < n * n; e++) {
                        s(e % n, Math.floor(e / n), 2, !0, o);
                        const r = t.getElevation(o[0], o[1])
                          , i = t.getElevation(o[2], o[1])
                          , l = t.getElevation(o[2], o[3])
                          , u = t.getElevation(o[0], o[3])
                          , c = t.isLeaf(o[0], o[1])
                          , h = t.isLeaf(o[2], o[1])
                          , p = t.isLeaf(o[2], o[3])
                          , f = t.isLeaf(o[0], o[3])
                          , d = Math.min(r.min, i.min, l.min, u.min)
                          , y = Math.max(r.max, i.max, l.max, u.max)
                          , m = c && h && p && f;
                        a.maximums.push(y),
                        a.minimums.push(d),
                        a.leaves.push(y - d <= 5 && m ? 1 : 0);
                    }
                    r.push(a);
                }
                return r
            }(this.dem)
              , r = e.length - 1
              , n = e[r];
            this._addNode(n.minimums[0], n.maximums[0], n.leaves[0]),
            this._construct(e, 0, 0, r, 0);
        }
        raycastRoot(t, e, r, n, i, s, a=1) {
            return Ly([t, e, -100], [r, n, this.maximums[0] * a], i, s)
        }
        raycast(t, e, r, n, i, s, a=1) {
            if (!this.nodeCount)
                return null;
            const o = this.raycastRoot(t, e, r, n, i, s, a);
            if (null == o)
                return null;
            const l = []
              , u = []
              , c = []
              , h = []
              , p = [{
                idx: 0,
                t: o,
                nodex: 0,
                nodey: 0,
                depth: 0
            }];
            for (; p.length > 0; ) {
                const {idx: o, t: f, nodex: d, nodey: y, depth: m} = p.pop();
                if (this.leaves[o]) {
                    Uy(d, y, m, t, e, r, n, c, h);
                    const o = 1 << m
                      , l = (d + 0) / o
                      , u = (d + 1) / o
                      , p = (y + 0) / o
                      , g = (y + 1) / o
                      , x = qy(l, p, this.dem) * a
                      , v = qy(u, p, this.dem) * a
                      , b = qy(u, g, this.dem) * a
                      , _ = qy(l, g, this.dem) * a
                      , w = Ry(c[0], c[1], x, h[0], c[1], v, h[0], h[1], b, i, s)
                      , A = Ry(h[0], h[1], b, c[0], h[1], _, c[0], c[1], x, i, s)
                      , k = Math.min(null !== w ? w : Number.MAX_VALUE, null !== A ? A : Number.MAX_VALUE);
                    if (k !== Number.MAX_VALUE)
                        return k;
                    {
                        const t = yu([], i, s, f);
                        if ($y(x, v, _, b, jy(t[0], c[0], h[0]), jy(t[1], c[1], h[1])) >= t[2])
                            return f
                    }
                    continue
                }
                let g = 0;
                for (let p = 0; p < this._siblingOffset.length; p++) {
                    Uy((d << 1) + this._siblingOffset[p][0], (y << 1) + this._siblingOffset[p][1], m + 1, t, e, r, n, c, h),
                    c[2] = -100,
                    h[2] = this.maximums[this.childOffsets[o] + p] * a;
                    const f = Ly(c, h, i, s);
                    if (null != f) {
                        const t = f;
                        l[p] = t;
                        let e = !1;
                        for (let r = 0; r < g && !e; r++)
                            t >= l[u[r]] && (u.splice(r, 0, p),
                            e = !0);
                        e || (u[g] = p),
                        g++;
                    }
                }
                for (let t = 0; t < g; t++) {
                    const e = u[t];
                    p.push({
                        idx: this.childOffsets[o] + e,
                        t: l[e],
                        nodex: (d << 1) + this._siblingOffset[e][0],
                        nodey: (y << 1) + this._siblingOffset[e][1],
                        depth: m + 1
                    });
                }
            }
            return null
        }
        _addNode(t, e, r) {
            return this.minimums.push(t),
            this.maximums.push(e),
            this.leaves.push(r),
            this.childOffsets.push(0),
            this.nodeCount++
        }
        _construct(t, e, r, n, i) {
            if (1 === t[n].isLeaf(e, r))
                return;
            this.childOffsets[i] || (this.childOffsets[i] = this.nodeCount);
            const s = n - 1
              , a = t[s];
            let o = 0
              , l = 0;
            for (let t = 0; t < this._siblingOffset.length; t++) {
                const n = 2 * e + this._siblingOffset[t][0]
                  , i = 2 * r + this._siblingOffset[t][1]
                  , s = a.getElevation(n, i)
                  , u = a.isLeaf(n, i)
                  , c = this._addNode(s.min, s.max, u);
                u && (o |= 1 << t),
                l || (l = c);
            }
            for (let n = 0; n < this._siblingOffset.length; n++)
                o & 1 << n || this._construct(t, 2 * e + this._siblingOffset[n][0], 2 * r + this._siblingOffset[n][1], s, l + n);
        }
    }
    function $y(t, e, r, n, i, s) {
        return mr(mr(t, r, s), mr(e, n, s), i)
    }
    function qy(t, e, r) {
        const n = r.dim
          , i = d(t * n - .5, 0, n - 1)
          , s = d(e * n - .5, 0, n - 1)
          , a = Math.floor(i)
          , o = Math.floor(s)
          , l = Math.min(a + 1, n - 1)
          , u = Math.min(o + 1, n - 1);
        return $y(r.get(a, o), r.get(l, o), r.get(a, u), r.get(l, u), i - a, s - o)
    }
    const Ny = {
        sgmap: [6553.6, 25.6, .1, 1e4],
        terrarium: [256, 1, 1 / 256, 32768],
        epgis: [9362.285714285717, 36.571428571428584, .1428571428571429, 9866]
    };
    class Zy {
        get tree() {
            return this._tree || this._buildQuadTree(),
            this._tree
        }
        constructor(t, e, r, n=!1, i=!1) {
            if (this.uid = t,
            e.height !== e.width)
                throw new RangeError("DEM tiles must be square");
            if (r && "sgmap" !== r && "terrarium" !== r && "epgis" !== r)
                return B(`"${r}" is not a valid encoding type. Valid types include "sgmap" and "terrarium"、"epgis".`);
            this.stride = e.height;
            const s = this.dim = e.height - 2
              , a = new Uint32Array(e.data.buffer);
            if (this.pixels = new Uint8Array(e.data.buffer),
            this.encoding = r || "epgis",
            this.borderReady = n,
            !n) {
                for (let t = 0; t < s; t++)
                    a[this._idx(-1, t)] = a[this._idx(0, t)],
                    a[this._idx(s, t)] = a[this._idx(s - 1, t)],
                    a[this._idx(t, -1)] = a[this._idx(t, 0)],
                    a[this._idx(t, s)] = a[this._idx(t, s - 1)];
                a[this._idx(-1, -1)] = a[this._idx(0, 0)],
                a[this._idx(s, -1)] = a[this._idx(s - 1, 0)],
                a[this._idx(-1, s)] = a[this._idx(0, s - 1)],
                a[this._idx(s, s)] = a[this._idx(s - 1, s - 1)],
                i && this._buildQuadTree();
            }
        }
        _buildQuadTree() {
            this._tree = new Oy(this);
        }
        get(t, e, r=!1) {
            r && (t = d(t, -1, this.dim),
            e = d(e, -1, this.dim));
            const n = 4 * this._idx(t, e)
              , i = Ny[this.encoding];
            return this.pixels[n] * i[0] + this.pixels[n + 1] * i[1] + this.pixels[n + 2] * i[2] - i[3]
        }
        static getUnpackVector(t) {
            return Ny[t]
        }
        get unpackVector() {
            return Ny[this.encoding]
        }
        _idx(t, e) {
            if (t < -1 || t >= this.dim + 1 || e < -1 || e >= this.dim + 1)
                throw new RangeError("out of range source coordinates for DEM data");
            return (e + 1) * this.stride + (t + 1)
        }
        _unpacksgmap(t, e, r) {
            return (256 * t * 256 + 256 * e + r) / 10 - 1e4
        }
        _unpackTerrarium(t, e, r) {
            return 256 * t + e + r / 256 - 32768
        }
        static pack(t, e) {
            const r = [0, 0, 0, 0]
              , n = Zy.getUnpackVector(e);
            let i = Math.floor((t + n[3]) / n[2]);
            return r[2] = i % 256,
            i = Math.floor(i / 256),
            r[1] = i % 256,
            i = Math.floor(i / 256),
            r[0] = i,
            r
        }
        getPixels() {
            return new Qu({
                width: this.stride,
                height: this.stride
            },this.pixels)
        }
        backfillBorder(t, e, r) {
            if (this.dim !== t.dim)
                throw new Error("dem dimension mismatch");
            let n = e * this.dim
              , i = e * this.dim + this.dim
              , s = r * this.dim
              , a = r * this.dim + this.dim;
            switch (e) {
            case -1:
                n = i - 1;
                break;
            case 1:
                i = n + 1;
            }
            switch (r) {
            case -1:
                s = a - 1;
                break;
            case 1:
                a = s + 1;
            }
            const o = -e * this.dim
              , l = -r * this.dim;
            for (let e = s; e < a; e++)
                for (let r = n; r < i; r++) {
                    const n = 4 * this._idx(r, e)
                      , i = 4 * this._idx(r + o, e + l);
                    this.pixels[n + 0] = t.pixels[i + 0],
                    this.pixels[n + 1] = t.pixels[i + 1],
                    this.pixels[n + 2] = t.pixels[i + 2],
                    this.pixels[n + 3] = t.pixels[i + 3];
                }
        }
        onDeserialize() {
            this._tree && (this._tree.dem = this);
        }
    }
    Bi(Zy, "DEMData"),
    Bi(Oy, "DemMinMaxQuadTree", {
        omit: ["dem"]
    });
    class Gy {
        constructor(t, e) {
            this.max = t,
            this.onRemove = e,
            this.reset();
        }
        reset() {
            for (const t in this.data)
                for (const e of this.data[t])
                    e.timeout && clearTimeout(e.timeout),
                    this.onRemove(e.value);
            return this.data = {},
            this.order = [],
            this
        }
        add(t, e, r) {
            const n = t.wrapped().key;
            void 0 === this.data[n] && (this.data[n] = []);
            const i = {
                value: e,
                timeout: void 0
            };
            if (void 0 !== r && (i.timeout = setTimeout((()=>{
                this.remove(t, i);
            }
            ), r)),
            this.data[n].push(i),
            this.order.push(n),
            this.order.length > this.max) {
                const t = this._getAndRemoveByKey(this.order[0]);
                t && this.onRemove(t);
            }
            return this
        }
        has(t) {
            return t.wrapped().key in this.data
        }
        getAndRemove(t) {
            return this.has(t) ? this._getAndRemoveByKey(t.wrapped().key) : null
        }
        _getAndRemoveByKey(t) {
            const e = this.data[t].shift();
            return e.timeout && clearTimeout(e.timeout),
            0 === this.data[t].length && delete this.data[t],
            this.order.splice(this.order.indexOf(t), 1),
            e.value
        }
        getByKey(t) {
            const e = this.data[t];
            return e ? e[0].value : null
        }
        get(t) {
            return this.has(t) ? this.data[t.wrapped().key][0].value : null
        }
        remove(t, e) {
            if (!this.has(t))
                return this;
            const r = t.wrapped().key
              , n = void 0 === e ? 0 : this.data[r].indexOf(e)
              , i = this.data[r][n];
            return this.data[r].splice(n, 1),
            i.timeout && clearTimeout(i.timeout),
            0 === this.data[r].length && delete this.data[r],
            this.onRemove(i.value),
            this.order.splice(this.order.indexOf(r), 1),
            this
        }
        setMaxSize(t) {
            for (this.max = t; this.order.length > this.max; ) {
                const t = this._getAndRemoveByKey(this.order[0]);
                t && this.onRemove(t);
            }
            return this
        }
        filter(t) {
            const e = [];
            for (const r in this.data)
                for (const n of this.data[r])
                    t(n.value) || e.push(n);
            for (const t of e)
                this.remove(t.value.tileID, t);
        }
    }
    class Xy {
        constructor(t, e, r) {
            this.func = t,
            this.mask = e,
            this.range = r;
        }
    }
    Xy.ReadOnly = !1,
    Xy.ReadWrite = !0,
    Xy.disabled = new Xy(519,Xy.ReadOnly,[0, 1]);
    const Yy = 7680;
    class Hy {
        constructor(t, e, r, n, i, s) {
            this.test = t,
            this.ref = e,
            this.mask = r,
            this.fail = n,
            this.depthFail = i,
            this.pass = s;
        }
    }
    Hy.disabled = new Hy({
        func: 519,
        mask: 0
    },0,0,Yy,Yy,Yy);
    class Ky {
        constructor(t, e, r) {
            this.blendFunction = t,
            this.blendColor = e,
            this.mask = r;
        }
    }
    Ky.Replace = [1, 0],
    Ky.disabled = new Ky(Ky.Replace,me.transparent,[!1, !1, !1, !1]),
    Ky.unblended = new Ky(Ky.Replace,me.transparent,[!0, !0, !0, !0]),
    Ky.alphaBlended = new Ky([1, 771],me.transparent,[!0, !0, !0, !0]);
    const Jy = 1029
      , Wy = 2305;
    class Qy {
        constructor(t, e, r) {
            this.enable = t,
            this.mode = e,
            this.frontFace = r;
        }
    }
    Qy.disabled = new Qy(!1,Jy,Wy),
    Qy.backCCW = new Qy(!0,Jy,Wy),
    Qy.backCW = new Qy(!0,Jy,2304),
    Qy.frontCW = new Qy(!0,1028,2304),
    Qy.frontCCW = new Qy(!0,1028,Wy);
    class tm extends $t {
        constructor(t, e, r) {
            super(),
            this.id = t,
            this._onlySymbols = r,
            e.on("data", (t=>{
                "source" === t.dataType && "metadata" === t.sourceDataType && (this._sourceLoaded = !0),
                this._sourceLoaded && !this._paused && "source" === t.dataType && "content" === t.sourceDataType && (this.reload(),
                this.transform && this.update(this.transform));
            }
            )),
            e.on("error", (()=>{
                this._sourceErrored = !0;
            }
            )),
            this._source = e,
            this._tiles = {},
            this._cache = new Gy(0,this._unloadTile.bind(this)),
            this._timers = {},
            this._cacheTimers = {},
            this._minTileCacheSize = e.minTileCacheSize,
            this._maxTileCacheSize = e.maxTileCacheSize,
            this._loadedParentTiles = {},
            this._coveredTiles = {},
            this._state = new Ey,
            this._isRaster = "raster" === this._source.type || "raster-dem" === this._source.type || "custom" === this._source.type && "raster" === this._source._dataType;
        }
        onAdd(t) {
            this.map = t,
            this._minTileCacheSize = void 0 === this._minTileCacheSize && t ? t._minTileCacheSize : this._minTileCacheSize,
            this._maxTileCacheSize = void 0 === this._maxTileCacheSize && t ? t._maxTileCacheSize : this._maxTileCacheSize;
        }
        loaded() {
            if (this._sourceErrored)
                return !0;
            if (!this._sourceLoaded)
                return !1;
            if (!this._source.loaded())
                return !1;
            for (const t in this._tiles) {
                const e = this._tiles[t];
                if ("loaded" !== e.state && "errored" !== e.state)
                    return !1
            }
            return !0
        }
        getSource() {
            return this._source
        }
        pause() {
            this._paused = !0;
        }
        resume() {
            if (!this._paused)
                return;
            const t = this._shouldReloadOnResume;
            this._paused = !1,
            this._shouldReloadOnResume = !1,
            t && this.reload(),
            this.transform && this.update(this.transform);
        }
        _loadTile(t, e) {
            return t.isSymbolTile = this._onlySymbols,
            this._source.loadTile(t, e)
        }
        _unloadTile(t) {
            if (this._source.unloadTile)
                return this._source.unloadTile(t, (()=>{}
                ))
        }
        _abortTile(t) {
            if (this._source.abortTile)
                return this._source.abortTile(t, (()=>{}
                ))
        }
        serialize() {
            return this._source.serialize()
        }
        prepare(t) {
            if (this._source.prepare && this._source.prepare(),
            this._state.coalesceChanges(this._tiles, this.map ? this.map.painter : null),
            this._source.prepareTile)
                for (const e in this._tiles) {
                    const r = this._tiles[e];
                    this._source.prepareTile(r) && this.map.painter.terrain && this.map.painter.terrain._clearRenderCacheForTile(this.id, r.tileID),
                    r.upload(t),
                    r.prepare(this.map.style.imageManager);
                }
            else
                for (const e in this._tiles) {
                    const r = this._tiles[e];
                    r.upload(t),
                    r.prepare(this.map.style.imageManager);
                }
        }
        getIds() {
            return x(this._tiles).map((t=>t.tileID)).sort(em).map((t=>t.key))
        }
        getRenderableIds(t) {
            const e = [];
            for (const r in this._tiles)
                this._isIdRenderable(r, t) && e.push(this._tiles[r]);
            return t ? e.sort(((t,e)=>{
                const r = t.tileID
                  , n = e.tileID
                  , s = new i(r.canonical.x,r.canonical.y)._rotate(this.transform.angle)
                  , a = new i(n.canonical.x,n.canonical.y)._rotate(this.transform.angle);
                return r.overscaledZ - n.overscaledZ || a.y - s.y || a.x - s.x
            }
            )).map((t=>t.tileID.key)) : e.map((t=>t.tileID)).sort(em).map((t=>t.key))
        }
        hasRenderableParent(t) {
            const e = this.findLoadedParent(t, 0);
            return !!e && this._isIdRenderable(e.tileID.key)
        }
        _isIdRenderable(t, e) {
            return this._tiles[t] && this._tiles[t].hasData() && !this._coveredTiles[t] && (e || !this._tiles[t].holdingForFade())
        }
        reload() {
            if (this._paused)
                this._shouldReloadOnResume = !0;
            else {
                this._cache.reset();
                for (const t in this._tiles)
                    "errored" !== this._tiles[t].state && this._reloadTile(t, "reloading");
            }
        }
        _reloadTile(t, e) {
            const r = this._tiles[t];
            r && ("loading" !== r.state && (r.state = e),
            this._loadTile(r, this._tileLoaded.bind(this, r, t, e)));
        }
        _tileLoaded(t, e, r, n) {
            if (n)
                if (t.state = "errored",
                404 !== n.status)
                    this._source.fire(new Ot(n,{
                        tile: t
                    }));
                else if ("raster-dem" === this._source.type && this.usedForTerrain && this.map.painter.terrain) {
                    const t = this.map.painter.terrain;
                    this.update(this.transform, t.getScaledDemTileSize(), !0),
                    t.resetTileLookupCache(this.id);
                } else
                    this.update(this.transform);
            else
                t.timeAdded = N.now(),
                "expired" === r && (t.refreshedUponExpiration = !0),
                this._setTileReloadTimer(e, t),
                "raster-dem" === this._source.type && t.dem && this._backfillDEM(t),
                this._state.initializeTileState(t, this.map ? this.map.painter : null),
                this._source.fire(new Ut("data",{
                    dataType: "source",
                    tile: t,
                    coord: t.tileID,
                    sourceCacheId: this.id
                }));
        }
        _backfillDEM(t) {
            const e = this.getRenderableIds();
            for (let n = 0; n < e.length; n++) {
                const i = e[n];
                if (t.neighboringTiles && t.neighboringTiles[i]) {
                    const e = this.getTileByID(i);
                    r(t, e),
                    r(e, t);
                }
            }
            function r(t, e) {
                if (!t.dem || t.dem.borderReady)
                    return;
                t.needsHillshadePrepare = !0,
                t.needsDEMTextureUpload = !0;
                let r = e.tileID.canonical.x - t.tileID.canonical.x;
                const n = e.tileID.canonical.y - t.tileID.canonical.y
                  , i = Math.pow(2, t.tileID.canonical.z)
                  , s = e.tileID.key;
                0 === r && 0 === n || Math.abs(n) > 1 || (Math.abs(r) > 1 && (1 === Math.abs(r + i) ? r += i : 1 === Math.abs(r - i) && (r -= i)),
                e.dem && t.dem && (t.dem.backfillBorder(e.dem, r, n),
                t.neighboringTiles && t.neighboringTiles[s] && (t.neighboringTiles[s].backfilled = !0)));
            }
        }
        getTile(t) {
            return this.getTileByID(t.key)
        }
        getTileByID(t) {
            return this._tiles[t]
        }
        _retainLoadedChildren(t, e, r, n) {
            for (const i in this._tiles) {
                let s = this._tiles[i];
                if (n[i] || !s.hasData() || s.tileID.overscaledZ <= e || s.tileID.overscaledZ > r)
                    continue;
                let a = s.tileID;
                for (; s && s.tileID.overscaledZ > e + 1; ) {
                    const t = s.tileID.scaledTo(s.tileID.overscaledZ, -1);
                    s = this._tiles[t.key],
                    s && s.hasData() && (a = t);
                }
                let o = a;
                for (; o.overscaledZ > e; )
                    if (o = o.scaledTo(o.overscaledZ, -1),
                    t[o.key]) {
                        n[a.key] = a;
                        break
                    }
            }
        }
        findLoadedParent(t, e) {
            if (t.key in this._loadedParentTiles) {
                const r = this._loadedParentTiles[t.key];
                return r && r.tileID.overscaledZ >= e ? r : null
            }
            for (let r = t.overscaledZ - 1; r >= e; r--) {
                const e = t.scaledTo(r)
                  , n = this._getLoadedTile(e);
                if (n)
                    return n
            }
        }
        _getLoadedTile(t) {
            const e = this._tiles[t.key];
            return e && e.hasData() ? e : this._cache.getByKey(this._source.reparseOverscaled ? t.wrapped().key : t.canonical.key)
        }
        updateCacheSize(t, e) {
            e = e || this._source.tileSize;
            const r = Math.ceil(t.width / e) + 1
              , n = Math.ceil(t.height / e) + 1
              , i = Math.floor(r * n * 5)
              , s = "number" == typeof this._minTileCacheSize ? Math.max(this._minTileCacheSize, i) : i
              , a = "number" == typeof this._maxTileCacheSize ? Math.min(this._maxTileCacheSize, s) : s;
            this._cache.setMaxSize(a);
        }
        handleWrapJump(t) {
            const e = Math.round((t - (void 0 === this._prevLng ? t : this._prevLng)) / 360);
            if (this._prevLng = t,
            e) {
                const t = {};
                for (const r in this._tiles) {
                    const n = this._tiles[r];
                    n.tileID = n.tileID.unwrapTo(n.tileID.wrap + e),
                    t[n.tileID.key] = n;
                }
                this._tiles = t;
                for (const t in this._timers)
                    clearTimeout(this._timers[t]),
                    delete this._timers[t];
                for (const t in this._tiles)
                    this._setTileReloadTimer(t, this._tiles[t]);
            }
        }
        update(t, e, r, n) {
            if (this.transform = t,
            !this._sourceLoaded || this._paused || this.transform.freezeTileCoverage)
                return;
            if (this.usedForTerrain && !r)
                return;
            let i;
            this.updateCacheSize(t, e),
            "globe" !== this.transform.projection.name && this.handleWrapJump(this.transform.center.lng),
            this._coveredTiles = {},
            this.used || this.usedForTerrain ? this._source.tileID ? i = t.getVisibleUnwrappedCoordinates(this._source.tileID).map((t=>new kh(t.canonical.z,t.wrap,t.canonical.z,t.canonical.x,t.canonical.y,t))) : (i = t.coveringTiles({
                tileSize: e || this._source.tileSize,
                minzoom: this._source.minzoom,
                maxzoom: this._source.maxzoom,
                roundZoom: this._source.roundZoom && !r,
                reparseOverscaled: this._source.reparseOverscaled,
                isTerrainDEM: this.usedForTerrain,
                reference: this._source.reference,
                zoomRule: this._source.zoomRule,
                sourceID: this._source.id
            }),
            this._source.hasTile && (i = i.filter((t=>this._source.hasTile(t))))) : i = [];
            const s = t.coveringZoomLevel(this._source)
              , a = this._updateRetainedTiles(i, s);
            if (rm(this._source.type) && 0 !== i.length) {
                const t = {}
                  , e = {}
                  , r = Object.keys(a);
                for (const n of r) {
                    const r = a[n]
                      , i = this._tiles[n];
                    if (!i || i.fadeEndTime && i.fadeEndTime <= N.now())
                        continue;
                    const s = this.findLoadedParent(r, Math.max(r.overscaledZ - tm.maxOverzooming, this._source.minzoom));
                    s && (this._addTile(s.tileID),
                    t[s.tileID.key] = s.tileID),
                    e[n] = r;
                }
                const n = i[i.length - 1].overscaledZ;
                for (const t in this._tiles) {
                    const r = this._tiles[t];
                    if (a[t] || !r.hasData())
                        continue;
                    let i = r.tileID;
                    for (; i.overscaledZ > n; ) {
                        i = i.scaledTo(i.overscaledZ, -1);
                        const n = this._tiles[i.key];
                        if (n && n.hasData() && e[i.key]) {
                            a[t] = r.tileID;
                            break
                        }
                    }
                }
                for (const e in t)
                    a[e] || (this._coveredTiles[e] = !0,
                    a[e] = t[e]);
            }
            for (const t in a)
                this._tiles[t].clearFadeHold();
            const o = function(t, e) {
                const r = [];
                for (const n in t)
                    n in e || r.push(n);
                return r
            }(this._tiles, a);
            for (const t of o) {
                const e = this._tiles[t];
                e.hasSymbolBuckets && !e.holdingForFade() ? e.setHoldDuration(this.map._fadeDuration) : e.hasSymbolBuckets && !e.symbolFadeFinished() || this._removeTile(t);
            }
            this._updateLoadedParentTileCache(),
            this._onlySymbols && this._source.afterUpdate && this._source.afterUpdate();
        }
        releaseSymbolFadeTiles() {
            for (const t in this._tiles)
                this._tiles[t].holdingForFade() && this._removeTile(t);
        }
        _updateRetainedTiles(t, e) {
            const r = "Sg4326" == this._source.reference
              , n = {};
            if (0 === t.length)
                return n;
            const i = {}
              , s = t.reduce(((t,e)=>Math.min(t, e.overscaledZ)), 1 / 0)
              , a = t[0].overscaledZ
              , o = Math.max(a - tm.maxOverzooming, this._source.minzoom)
              , l = Math.max(a + tm.maxUnderzooming, this._source.minzoom)
              , u = {};
            for (const i of t) {
                const t = this._addTile(i);
                n[i.key] = i,
                r && this._tiles[i.key] && "reloading" != t.state && (t.tileZoom != e || t.tileID._mapZoom != e) && (t.tileZoom = e,
                t.tileID._mapZoom = e,
                this._reloadTile(i.key, "reloading")),
                t.hasData() || s < this._source.maxzoom && (u[i.key] = i);
            }
            this._retainLoadedChildren(u, s, l, n);
            for (const e of t) {
                let t = this._tiles[e.key];
                if (t.hasData())
                    continue;
                if (e.canonical.z >= this._source.maxzoom) {
                    const t = e.children(this._source.maxzoom)[0]
                      , r = this.getTile(t);
                    if (r && r.hasData()) {
                        n[t.key] = t;
                        continue
                    }
                } else {
                    const t = e.children(this._source.maxzoom);
                    if (n[t[0].key] && n[t[1].key] && n[t[2].key] && n[t[3].key])
                        continue
                }
                let r = t.wasRequested();
                for (let s = e.overscaledZ - 1; s >= o; --s) {
                    const a = e.scaledTo(s);
                    if (i[a.key])
                        break;
                    if (i[a.key] = !0,
                    t = this.getTile(a),
                    !t && r && (t = this._addTile(a)),
                    t && (n[a.key] = a,
                    r = t.wasRequested(),
                    t.hasData()))
                        break
                }
            }
            return n
        }
        _updateLoadedParentTileCache() {
            this._loadedParentTiles = {};
            for (const t in this._tiles) {
                const e = [];
                let r, n = this._tiles[t].tileID;
                for (; n.overscaledZ > 0; ) {
                    if (n.key in this._loadedParentTiles) {
                        r = this._loadedParentTiles[n.key];
                        break
                    }
                    e.push(n.key);
                    const t = n.scaledTo(n.overscaledZ, -1);
                    if (r = this._getLoadedTile(t),
                    r)
                        break;
                    n = t;
                }
                for (const t of e)
                    this._loadedParentTiles[t] = r;
            }
        }
        _addTile(t) {
            let e = this._tiles[t.key];
            if (e)
                return this._source.prepareTile && this._source.prepareTile(e),
                e;
            e = this._cache.getAndRemove(t),
            e && (this._setTileReloadTimer(t.key, e),
            e.tileID = t,
            this._state.initializeTileState(e, this.map ? this.map.painter : null),
            this._cacheTimers[t.key] && (clearTimeout(this._cacheTimers[t.key]),
            delete this._cacheTimers[t.key],
            this._setTileReloadTimer(t.key, e)));
            const r = Boolean(e);
            if (!r) {
                const r = this.map ? this.map.painter : null;
                e = new Dy(t,this._source.tileSize * t.overscaleFactor(),this.transform.tileZoom,r,this._isRaster),
                this._source.prepareTile && this._source.prepareTile(e) || this._loadTile(e, this._tileLoaded.bind(this, e, t.key, e.state));
            }
            return e ? (e.uses++,
            this._tiles[t.key] = e,
            r || this._source.fire(new Ut("dataloading",{
                tile: e,
                coord: e.tileID,
                dataType: "source"
            })),
            e) : null
        }
        _setTileReloadTimer(t, e) {
            t in this._timers && (clearTimeout(this._timers[t]),
            delete this._timers[t]);
            const r = e.getExpiryTimeout();
            r && (this._timers[t] = setTimeout((()=>{
                this._reloadTile(t, "expired"),
                delete this._timers[t];
            }
            ), r));
        }
        _removeTile(t) {
            const e = this._tiles[t];
            e && (e.uses--,
            delete this._tiles[t],
            this._timers[t] && (clearTimeout(this._timers[t]),
            delete this._timers[t]),
            e.uses > 0 || (e.hasData() && "reloading" !== e.state ? this._cache.add(e.tileID, e, e.getExpiryTimeout()) : (e.aborted = !0,
            this._abortTile(e),
            this._unloadTile(e))));
        }
        clearTiles() {
            this._shouldReloadOnResume = !1,
            this._paused = !1;
            for (const t in this._tiles)
                this._removeTile(t);
            this._source._clear && this._source._clear(),
            this._cache.reset(),
            this.map && this.usedForTerrain && this.map.painter.terrain && this.map.painter.terrain.resetTileLookupCache(this.id);
        }
        tilesIn(t, e, r) {
            const n = []
              , i = this.transform;
            if (!i)
                return n;
            const s = "globe" === i.projection.name
              , a = Ho(i.center.lng);
            for (const o in this._tiles) {
                const l = this._tiles[o];
                if (r && l.clearQueryDebugViz(),
                l.holdingForFade())
                    continue;
                let u;
                if (s) {
                    const t = l.tileID.canonical;
                    if (0 === t.z) {
                        const e = [Math.abs(d(a, ...nm(t, -1)) - a), Math.abs(d(a, ...nm(t, 1)) - a)];
                        u = [0, 2 * e.indexOf(Math.min(...e)) - 1];
                    } else {
                        const e = [Math.abs(d(a, ...nm(t, -1)) - a), Math.abs(d(a, ...nm(t, 0)) - a), Math.abs(d(a, ...nm(t, 1)) - a)];
                        u = [e.indexOf(Math.min(...e)) - 1];
                    }
                } else
                    u = [0];
                for (const r of u) {
                    const s = t.containsTile(l, i, e, r);
                    s && n.push(s);
                }
            }
            return n
        }
        getVisibleCoordinates(t) {
            const e = this.getRenderableIds(t).map((t=>this._tiles[t].tileID));
            for (const t of e)
                t.projMatrix = this.transform.calculateProjMatrix(t.toUnwrapped());
            return e
        }
        hasTransition() {
            if (this._source.hasTransition())
                return !0;
            if (rm(this._source.type))
                for (const t in this._tiles) {
                    const e = this._tiles[t];
                    if (void 0 !== e.fadeEndTime && e.fadeEndTime >= N.now())
                        return !0
                }
            return !1
        }
        setFeatureState(t, e, r) {
            this._state.updateState(t = t || "_geojsonTileLayer", e, r);
        }
        removeFeatureState(t, e, r) {
            this._state.removeFeatureState(t = t || "_geojsonTileLayer", e, r);
        }
        getFeatureState(t, e) {
            return this._state.getState(t = t || "_geojsonTileLayer", e)
        }
        setDependencies(t, e, r) {
            const n = this._tiles[t];
            n && n.setDependencies(e, r);
        }
        reloadTilesForDependencies(t, e) {
            for (const r in this._tiles)
                this._tiles[r].hasDependency(t, e) && this._reloadTile(r, "reloading");
            this._cache.filter((r=>!r.hasDependency(t, e)));
        }
        _preloadTiles(t, e) {
            const r = new Map
              , n = Array.isArray(t) ? t : [t]
              , i = this.map.painter.terrain
              , s = this.usedForTerrain && i ? i.getScaledDemTileSize() : this._source.tileSize;
            for (const t of n) {
                const e = t.coveringTiles({
                    tileSize: s,
                    minzoom: this._source.minzoom,
                    maxzoom: this._source.maxzoom,
                    roundZoom: this._source.roundZoom && !this.usedForTerrain,
                    reparseOverscaled: this._source.reparseOverscaled,
                    isTerrainDEM: this.usedForTerrain,
                    reference: this._source.reference,
                    zoomRule: this._source.zoomRule,
                    sourceID: this._source.id
                });
                for (const t of e)
                    r.set(t.key, t);
                this.usedForTerrain && t.updateElevation(!1);
            }
            g(Array.from(r.values()), ((t,e)=>{
                const r = new Dy(t,this._source.tileSize * t.overscaleFactor(),this.transform.tileZoom,this.map.painter,this._isRaster);
                this._loadTile(r, (t=>{
                    "raster-dem" === this._source.type && r.dem && this._backfillDEM(r),
                    e(t, r);
                }
                ));
            }
            ), e);
        }
    }
    function em(t, e) {
        const r = Math.abs(2 * t.wrap) - +(t.wrap < 0)
          , n = Math.abs(2 * e.wrap) - +(e.wrap < 0);
        return t.overscaledZ - e.overscaledZ || n - r || e.canonical.y - t.canonical.y || e.canonical.x - t.canonical.x
    }
    function rm(t) {
        return "raster" === t || "image" === t || "video" === t
    }
    function nm(t, e) {
        const r = 1 << t.z;
        return [t.x / r + e, (t.x + 1) / r + e]
    }
    tm.maxOverzooming = 10,
    tm.maxUnderzooming = 3;
    class im {
        constructor(t, e, r) {
            this._demTile = t,
            this._dem = this._demTile.dem,
            this._scale = e,
            this._offset = r;
        }
        static create(t, e, r) {
            const n = r || t.findDEMTileFor(e);
            if (!n || !n.dem)
                return;
            const i = n.dem
              , s = n.tileID
              , a = 1 << e.canonical.z - s.canonical.z;
            return new im(n,n.tileSize / bo / a,[(e.canonical.x / a - s.canonical.x) * i.dim, (e.canonical._tileY / a - s.canonical.y) * i.dim])
        }
        tileCoordToPixel(t, e) {
            const r = e * this._scale + this._offset[1]
              , n = Math.floor(t * this._scale + this._offset[0])
              , s = Math.floor(r);
            return new i(n,s)
        }
        getElevationAt(t, e, r, n) {
            const i = t * this._scale + this._offset[0]
              , s = e * this._scale + this._offset[1]
              , a = Math.floor(i)
              , o = Math.floor(s)
              , l = this._dem;
            return n = !!n,
            r ? mr(mr(l.get(a, o, n), l.get(a, o + 1, n), s - o), mr(l.get(a + 1, o, n), l.get(a + 1, o + 1, n), s - o), i - a) : l.get(a, o, n)
        }
        getElevationAtPixel(t, e, r) {
            return this._dem.get(t, e, !!r)
        }
        getMeterToDEM(t) {
            return (1 << this._demTile.tileID.canonical.z) * Jo(1, t) * this._dem.stride
        }
    }
    class sm {
        constructor(t, e) {
            this.tileID = t,
            this.x = t.canonical.x,
            this.y = t.canonical.y,
            this.z = t.canonical.z,
            this.grid = new Mi(bo,16,0),
            this.featureIndexArray = new Va,
            this.promoteId = e;
        }
        insert(t, e, r, n, i, s=0) {
            const a = this.featureIndexArray.length;
            this.featureIndexArray.emplaceBack(r, n, i, s);
            const o = this.grid;
            for (let t = 0; t < e.length; t++) {
                const r = e[t]
                  , n = [1 / 0, 1 / 0, -1 / 0, -1 / 0];
                for (let t = 0; t < r.length; t++) {
                    const e = r[t];
                    n[0] = Math.min(n[0], e.x),
                    n[1] = Math.min(n[1], e.y),
                    n[2] = Math.max(n[2], e.x),
                    n[3] = Math.max(n[3], e.y);
                }
                n[0] < bo && n[1] < bo && n[2] >= 0 && n[3] >= 0 && o.insert(a, n[0], n[1], n[2], n[3]);
            }
        }
        loadVTLayers() {
            if (!this.vtLayers) {
                let {canonical: t, reference: e, _tileY: r, _tileH: n} = this.tileID;
                this.vtLayers = new _y.VectorTile(new op(this.rawTileData),null,{
                    reference: e,
                    _tileY: r,
                    _tileH: n,
                    x: t.x,
                    y: t.y,
                    z: t.z
                }).layers,
                this.sourceLayerCoder = new wy(this.vtLayers ? Object.keys(this.vtLayers).sort() : ["_geojsonTileLayer"]),
                this.vtFeatures = {};
                for (const t in this.vtLayers)
                    this.vtFeatures[t] = [];
            }
            return this.vtLayers
        }
        query(t, e, r, n, i) {
            this.loadVTLayers();
            const s = t.params || {}
              , a = Hn(s.filter)
              , o = t.tileResult
              , l = t.transform
              , u = o.bufferedTilespaceBounds
              , c = this.grid.query(u.min.x, u.min.y, u.max.x, u.max.y, ((t,e,r,n)=>Ll(o.bufferedTilespaceGeometry, t, e, r, n)));
            c.sort(om);
            let h = null;
            l.elevation && c.length > 0 && (h = im.create(l.elevation, this.tileID));
            const p = {};
            let f;
            for (let l = 0; l < c.length; l++) {
                const u = c[l];
                if (u === f)
                    continue;
                f = u;
                const d = this.featureIndexArray.get(u);
                let y = null;
                this.loadMatchingFeature(p, d, a, s.layers, s.availableImages, e, r, n, ((e,r,n,s=0)=>(y || (y = wl(e, this.tileID.canonical, t.tileTransform)),
                r.queryIntersectsFeature(o, e, n, y, this.z, t.transform, t.pixelPosMatrix, h, s, i[r.id]))));
            }
            return p
        }
        loadMatchingFeature(t, e, r, n, i, s, a, o, l) {
            const {featureIndex: u, bucketIndex: c, sourceLayerIndex: h, layoutVertexArrayOffset: p} = e
              , f = this.bucketLayerIDs[c];
            if (n && !function(t, e) {
                for (let r = 0; r < t.length; r++)
                    if (e.indexOf(t[r]) >= 0)
                        return !0;
                return !1
            }(n, f))
                return;
            const d = this.sourceLayerCoder.decode(h)
              , y = this.vtLayers[d].feature(u);
            if (r.needGeometry) {
                const t = Al(y, !0);
                if (!r.filter(new Ts(this.tileID.overscaledZ), t, this.tileID.canonical))
                    return
            } else if (!r.filter(new Ts(this.tileID.overscaledZ), y))
                return;
            const m = this.getId(y, d);
            for (let e = 0; e < f.length; e++) {
                const r = f[e];
                if (n && n.indexOf(r) < 0)
                    continue;
                const c = s[r];
                if (!c)
                    continue;
                let h = {};
                void 0 !== m && o && (h = o.getState(c.sourceLayer || "_geojsonTileLayer", m));
                const d = v({}, a[r]);
                d.paint = am(d.paint, c.paint, y, h, i),
                d.layout = am(d.layout, c.layout, y, h, i);
                const g = !l || l(y, c, h, p);
                if (!g)
                    continue;
                const x = new ky(y,this.z,this.x,this.y,m);
                x.layer = d;
                let b = t[r];
                void 0 === b && (b = t[r] = []),
                b.push({
                    featureIndex: u,
                    feature: x,
                    intersectionZ: g
                });
            }
        }
        lookupSymbolFeatures(t, e, r, n, i, s, a, o) {
            const l = {};
            this.loadVTLayers();
            const u = Hn(i);
            for (const i of t)
                this.loadMatchingFeature(l, {
                    bucketIndex: r,
                    sourceLayerIndex: n,
                    featureIndex: i,
                    layoutVertexArrayOffset: 0
                }, u, s, a, o, e);
            return l
        }
        loadFeature(t) {
            const {featureIndex: e, sourceLayerIndex: r} = t;
            this.loadVTLayers();
            const n = this.sourceLayerCoder.decode(r)
              , i = this.vtFeatures[n];
            if (i[e])
                return i[e];
            const s = this.vtLayers[n].feature(e);
            return i[e] = s,
            s
        }
        hasLayer(t) {
            for (const e of this.bucketLayerIDs)
                for (const r of e)
                    if (t === r)
                        return !0;
            return !1
        }
        getId(t, e) {
            let r = t.id;
            return this.promoteId && (r = t.properties["string" == typeof this.promoteId ? this.promoteId : this.promoteId[e]],
            "boolean" == typeof r && (r = Number(r))),
            r
        }
    }
    function am(t, e, r, n, i) {
        return S(t, ((t,s)=>{
            const a = e instanceof Ls ? e.get(s) : null;
            return a && a.evaluate ? a.evaluate(r, n, i) : a
        }
        ))
    }
    function om(t, e) {
        return e - t
    }
    Bi(sm, "FeatureIndex", {
        omit: ["rawTileData", "sourceLayerCoder"]
    });
    class lm {
        constructor(t) {
            const e = {}
              , r = [];
            for (const n in t) {
                const i = t[n]
                  , s = e[n] = {};
                for (const t in i.glyphs) {
                    const e = i.glyphs[+t];
                    if (!e || 0 === e.bitmap.width || 0 === e.bitmap.height)
                        continue;
                    const n = e.metrics.localGlyph ? 2 : 1
                      , a = {
                        x: 0,
                        y: 0,
                        w: e.bitmap.width + 2 * n,
                        h: e.bitmap.height + 2 * n
                    };
                    r.push(a),
                    s[t] = a;
                }
            }
            const {w: n, h: i} = Bp(r)
              , s = new Wu({
                width: n || 1,
                height: i || 1
            });
            for (const r in t) {
                const n = t[r];
                for (const t in n.glyphs) {
                    const i = n.glyphs[+t];
                    if (!i || 0 === i.bitmap.width || 0 === i.bitmap.height)
                        continue;
                    const a = e[r][t]
                      , o = i.metrics.localGlyph ? 2 : 1;
                    Wu.copy(i.bitmap, s, {
                        x: 0,
                        y: 0
                    }, {
                        x: a.x + o,
                        y: a.y + o
                    }, i.bitmap);
                }
            }
            this.image = s,
            this.positions = e;
        }
    }
    Bi(lm, "GlyphAtlas");
    class um {
        constructor(t) {
            Xo(t.crs),
            this.tileID = new kh(t.tileID.overscaledZ,t.tileID.wrap,t.tileID.canonical.z,t.tileID.canonical.x,t.tileID.canonical.y,t.tileID),
            this.tileZoom = t.tileZoom,
            this.uid = t.uid,
            this.zoom = t.tileID._mapZoom || t.zoom,
            this.canonical = t.tileID.canonical,
            this.pixelRatio = t.pixelRatio,
            this.tileSize = t.tileSize,
            this.source = t.source,
            this.overscaling = this.tileID.overscaleFactor(),
            this.showCollisionBoxes = t.showCollisionBoxes,
            this.collectResourceTiming = !!t.collectResourceTiming,
            this.returnDependencies = !!t.returnDependencies,
            this.promoteId = t.promoteId,
            this.enableTerrain = !!t.enableTerrain,
            this.isSymbolTile = t.isSymbolTile,
            this.tileTransform = dd(t.tileID.canonical, t.projection),
            this.projection = t.projection;
        }
        parse(t, e, r, n, i) {
            let s = this.tileID
              , a = s._mapZoom || this.zoom
              , o = e._xml;
            const l = "Sg4326" == s.reference;
            let u = o && o["epgis-zoom-scale"];
            u && (a = a + u > 0 ? a + u : 1),
            this.status = "parsing",
            this.data = t,
            this.collisionBoxArray = new ka;
            const c = new wy(Object.keys(t.layers).sort())
              , h = new sm(this.tileID,this.promoteId);
            h.bucketLayerIDs = [];
            const p = {}
              , f = new fy(256,256)
              , d = {
                featureIndex: h,
                iconDependencies: {},
                patternDependencies: {},
                glyphDependencies: {},
                lineAtlas: f,
                availableImages: r,
                eleSymbolVertexs: {}
            }
              , y = e.familiesBySource[this.source];
            for (const e in y) {
                const n = t.layers[e];
                if (!n)
                    continue;
                let i = !1
                  , u = !1;
                for (const t of y[e])
                    "symbol" === t[0].type ? i = !0 : u = !0;
                if (!0 === this.isSymbolTile && !i)
                    continue;
                if (!1 === this.isSymbolTile && !u)
                    continue;
                const f = c.encode(e);
                let x = []
                  , w = 0;
                for (let t = 0; t < n.length; t++) {
                    let r = n.feature(t);
                    const i = h.getId(r, e);
                    if (l) {
                        var m = r.properties
                          , g = m.maxzoom
                          , v = m.minzoom
                          , b = 0
                          , _ = 25;
                        if (v >= 0 ? b = v <= 3 ? 0 : v - 1 : v = 0,
                        g >= 0 && (_ = g >= 19 ? 25 : g > b ? 3 == r.type ? g + 1 : g : b + 1),
                        a < b || a >= _)
                            continue;
                        if (null == (m = wt(m, o, a, l)))
                            continue
                    }
                    x.push({
                        feature: r,
                        id: i,
                        index: t,
                        sourceLayerIndex: f,
                        order: w
                    }),
                    w++;
                }
                if (x.length > 0) {
                    l && x.length > 1 && x[0].feature.properties.paintLevel && x.sort((function(t, e) {
                        return t.feature.properties.paintLevel - e.feature.properties.paintLevel
                    }
                    ));
                    for (let t = 0, n = y[e].length; t < n; t++) {
                        const n = y[e][t]
                          , i = n[0];
                        void 0 !== this.isSymbolTile && "symbol" === i.type !== this.isSymbolTile || i.minzoom && a < Math.floor(i.minzoom) || i.maxzoom && a >= i.maxzoom || "none" !== i.visibility && (cm(n, a, r),
                        (p[i.id] = i.createBucket({
                            index: h.bucketLayerIDs.length,
                            layers: n,
                            zoom: a,
                            canonical: this.canonical,
                            pixelRatio: this.pixelRatio,
                            overscaling: this.overscaling,
                            collisionBoxArray: this.collisionBoxArray,
                            sourceLayerIndex: f,
                            sourceID: this.source,
                            enableTerrain: this.enableTerrain,
                            projection: this.projection.spec,
                            availableImages: r
                        })).populate(x, d, s.canonical, this.tileTransform),
                        h.bucketLayerIDs.push(n.map((t=>t.id))));
                    }
                }
            }
            let w, A, k, z;
            f.trim();
            const M = {
                type: "maybePrepare",
                isSymbolTile: this.isSymbolTile,
                zoom: this.zoom
            }
              , I = S(d.glyphDependencies, (t=>Object.keys(t).map(Number)));
            Object.keys(I).length ? n.send("getGlyphs", {
                uid: this.uid,
                stacks: I
            }, ((t,e)=>{
                w || (w = t,
                A = e,
                P.call(this));
            }
            ), void 0, !1, M) : A = {};
            const T = Object.keys(d.iconDependencies);
            T.length ? n.send("getImages", {
                icons: T,
                source: this.source,
                tileID: this.tileID,
                type: "icons"
            }, ((t,e)=>{
                w || (w = t,
                k = e,
                P.call(this));
            }
            ), void 0, !1, M) : k = {};
            const B = Object.keys(d.patternDependencies);
            let C;
            B.length ? n.send("getImages", {
                icons: B,
                source: this.source,
                tileID: this.tileID,
                type: "patterns"
            }, ((t,e)=>{
                w || (w = t,
                z = e,
                P.call(this));
            }
            ), void 0, !1, M) : z = {};
            const V = Object.keys(d.eleSymbolVertexs);
            function P() {
                if (w)
                    return i(w);
                if (A && k && z && C) {
                    const t = new lm(A)
                      , e = new Vp(k,z);
                    for (const n in p) {
                        const i = p[n];
                        i instanceof Nd ? (cm(i.layers, this.zoom, r),
                        kf(i, A, t.positions, k, e.iconPositions, this.showCollisionBoxes, r, this.tileID.canonical, this.tileZoom, this.projection)) : i instanceof sy ? i.addFeatures(C, s.canonical, this.tileTransform) : i.hasPattern && (i instanceof Fh || i instanceof $c || i instanceof ch) && (cm(i.layers, a, r),
                        i.addFeatures(d, s.canonical, e.patternPositions, r, this.tileTransform));
                    }
                    this.status = "done",
                    i(null, {
                        buckets: x(p).filter((t=>!t.isEmpty())),
                        featureIndex: h,
                        collisionBoxArray: this.collisionBoxArray,
                        glyphAtlasImage: t.image,
                        lineAtlas: f,
                        imageAtlas: e,
                        glyphMap: this.returnDependencies ? A : null,
                        iconMap: this.returnDependencies ? k : null,
                        glyphPositions: this.returnDependencies ? t.positions : null
                    });
                }
            }
            V.length ? n.send("getEleSymbolVertexs", {
                eleSymbolVertexs: V
            }, ((t,e)=>{
                w || (w = t,
                C = e,
                P.call(this));
            }
            ), void 0, void 0, M) : C = {},
            P.call(this);
        }
    }
    function cm(t, e, r) {
        const n = new Ts(e);
        for (const e of t)
            e.recalculate(n, r);
    }
    class hm {
        constructor(t) {
            this.entries = {},
            this.scheduler = t;
        }
        request(t, e, r, n) {
            const i = this.entries[t] = this.entries[t] || {
                callbacks: []
            };
            if (i.result) {
                const [t,r] = i.result;
                return this.scheduler ? this.scheduler.add((()=>{
                    n(t, r);
                }
                ), e) : n(t, r),
                ()=>{}
            }
            return i.callbacks.push(n),
            i.cancel || (i.cancel = r(((r,n)=>{
                i.result = [r, n];
                for (const t of i.callbacks)
                    this.scheduler ? this.scheduler.add((()=>{
                        t(r, n);
                    }
                    ), e) : t(r, n);
                setTimeout((()=>delete this.entries[t]), 3e3);
            }
            ))),
            ()=>{
                i.result || (i.callbacks = i.callbacks.filter((t=>t !== n)),
                i.callbacks.length || (i.cancel(),
                delete this.entries[t]));
            }
        }
    }
    function pm(t, e, r) {
        const n = JSON.stringify(t.request);
        return t.data && (this.deduped.entries[n] = {
            result: [null, t.data]
        }),
        this.deduped.request(n, {
            type: "parseTile",
            isSymbolTile: t.isSymbolTile,
            zoom: t.tileZoom
        }, (e=>{
            const n = Vt(t.request, ((n,i,s,a)=>{
                if (n)
                    e(n);
                else if (i) {
                    let {canonical: n, reference: o, _tileY: l, _tileH: u} = t.tileID;
                    e(null, {
                        vectorTile: r ? void 0 : new _y.VectorTile(new op(i),null,{
                            reference: o,
                            _tileY: l,
                            _tileH: u,
                            x: n.x,
                            y: n.y,
                            z: n.z
                        }),
                        rawData: i,
                        cacheControl: s,
                        expires: a
                    });
                }
            }
            ));
            return ()=>{
                n.cancel(),
                e();
            }
        }
        ), e)
    }
    var fm = ["background", "symbol", "line", "fill", "fill-extrusion", "circle", "heatmap", "raster", "hillshade", "esymbol"]
      , dm = []
      , ym = []
      , mm = ""
      , gm = []
      , xm = [];
    t.ARRAY_TYPE = Gl,
    t.Aabb = $u,
    t.Actor = class {
        constructor(t, r, n) {
            this.target = t,
            this.parent = r,
            this.mapId = n,
            this.callbacks = {},
            this.cancelCallbacks = {},
            k(["receive"], this),
            this.target.addEventListener("message", this.receive, !1),
            this.globalScope = P() ? t : e,
            this.scheduler = new yy;
        }
        send(t, e, r, n, i=!1, s) {
            const a = Math.round(1e18 * Math.random()).toString(36).substring(0, 10);
            r && (r.metadata = s,
            this.callbacks[a] = r);
            const o = F(this.globalScope) ? void 0 : [];
            var l;
            return (l = e) && "undefined" != typeof ArrayBuffer && (l instanceof ArrayBuffer || l.constructor && "ArrayBuffer" === l.constructor.name) && (e = e.slice(0)),
            this.target.postMessage({
                id: a,
                type: t,
                hasCallback: !!r,
                targetMapId: n,
                mustQueue: i,
                sourceMapId: this.mapId,
                data: Pi(e, o)
            }, o),
            {
                cancel: ()=>{
                    r && delete this.callbacks[a],
                    this.target.postMessage({
                        id: a,
                        type: "<cancel>",
                        targetMapId: n,
                        sourceMapId: this.mapId
                    });
                }
            }
        }
        receive(t) {
            const e = t.data
              , r = e.id;
            if (r && (!e.targetMapId || this.mapId === e.targetMapId))
                if ("<cancel>" === e.type) {
                    const t = this.cancelCallbacks[r];
                    delete this.cancelCallbacks[r],
                    t && t.cancel();
                } else if (e.mustQueue || P()) {
                    const t = this.callbacks[r];
                    this.cancelCallbacks[r] = this.scheduler.add((()=>this.processTask(r, e)), t && t.metadata || {
                        type: "message"
                    });
                } else
                    this.processTask(r, e);
        }
        processTask(t, e) {
            if ("<response>" === e.type) {
                const r = this.callbacks[t];
                delete this.callbacks[t],
                r && (e.error ? r(Di(e.error)) : r(null, Di(e.data)));
            } else {
                const r = F(this.globalScope) ? void 0 : []
                  , n = e.hasCallback ? (e,n)=>{
                    delete this.cancelCallbacks[t],
                    this.target.postMessage({
                        id: t,
                        type: "<response>",
                        sourceMapId: this.mapId,
                        error: e ? Pi(e) : null,
                        data: Pi(n, r)
                    }, r);
                }
                : t=>{}
                  , i = Di(e.data);
                if (this.parent[e.type])
                    this.parent[e.type](e.sourceMapId, i, n);
                else if (this.parent.getWorkerSource) {
                    const t = e.type.split(".");
                    this.parent.getWorkerSource(e.sourceMapId, t[0], i.source)[t[1]](i, n);
                } else
                    n(new Error(`Could not find function ${e.type}`));
            }
        }
        remove() {
            this.scheduler.remove(),
            this.target.removeEventListener("message", this.receive, !1);
        }
    }
    ,
    t.BufferTostyle = function(t) {
        function e(t, e, n) {
            e[xm[t]] = n.readMessage(r, {}),
            delete e[xm[t]].zoomRange;
        }
        function r(t, e, r) {
            0 === t ? e.zoomRange = r.readString().split(",").map((t=>t.replace(/_/g, ","))) : e[e.zoomRange[t - 1]] = r.readMessage(n, {});
        }
        function n(t, e, r) {
            e[gm[t]] = JSON.parse(r.readString());
        }
        function i(t, e, r) {
            e[t] = r.readMessage(s, {});
        }
        function s(t, e, r) {
            1 === t && (e.id = r.readString()),
            2 === t && (e.type = fm[r.readVarint()]),
            3 === t && (e.source = mm[r.readVarint()]),
            4 === t && (e["source-layer"] = r.readString()),
            5 === t && (e.minzoom = r.readVarint()),
            6 === t && (e.maxzoom = r.readVarint()),
            7 === t && (e.layout = r.readMessage(a, {})),
            8 === t && (e.paint = r.readMessage(o, {})),
            9 === t && (e.filter = JSON.parse(r.readString()));
        }
        function a(t, e, r) {
            e[dm[t]] = JSON.parse(r.readString());
        }
        function o(t, e, r) {
            e[ym[t]] = JSON.parse(r.readString());
        }
        var l = t.readFields((function(t, r, n) {
            1 === t ? (r._layout = n.readString().split(","),
            dm = r._layout) : 2 === t ? (r._paint = n.readString().split(","),
            ym = r._paint) : 3 === t ? (r._source = n.readString(),
            mm = r._source.split(",")) : 4 === t ? r.layers = n.readMessage(i, []) : 5 === t ? r.created = n.readString() : 6 === t ? r.draft = n.readBoolean() : 7 === t ? r.glyphs = n.readString() : 8 === t ? r.id = n.readString() : 9 === t ? r.modified = n.readString() : 10 === t ? r.owner = n.readString() : 11 === t ? r.scheme = n.readString() : 12 === t ? r.sources = JSON.parse(n.readString()) : 13 === t ? r.sprite = n.readString() : 14 === t ? r.type = n.readString() : 15 === t ? r.url = n.readString() : 16 === t ? r.version = n.readVarint() : 17 === t ? r.minZoom = n.readVarint() : 18 === t ? r.maxZoom = n.readVarint() : 19 === t ? (r._xml_keys = n.readString().split(","),
            gm = r._xml_keys) : 20 === t ? (r._xml_ids = n.readString().split(","),
            xm = r._xml_ids) : 21 === t && (r.xml = n.readMessage(e, {}));
        }
        ), {});
        return delete l._paint,
        delete l._layout,
        delete l._source,
        delete l._xml_keys,
        delete l._xml_ids,
        l
    }
    ,
    t.CanonicalTileID = wh,
    t.Color = me,
    t.ColorMode = Ky,
    t.CullFaceMode = Qy,
    t.DEMData = Zy,
    t.DataConstantProperty = Rs,
    t.DedupedRequest = hm,
    t.DepthMode = Xy,
    t.EXTENT = bo,
    t.Elevation = class {
        isDataAvailableAtPoint(t) {
            const e = this._source();
            if (this.isUsingMockSource() || !e || t.y < 0 || t.y > 1)
                return !1;
            const r = e.getSource().maxzoom
              , n = 1 << r
              , i = Math.floor(t.x)
              , s = Math.floor((t.x - i) * n)
              , a = Math.floor(t.y * n)
              , o = this.findDEMTileFor(new kh(r,i,r,s,a));
            return !(!o || !o.dem)
        }
        getAtPointOrZero(t, e=0) {
            return this.getAtPoint(t, e) || 0
        }
        getAtPoint(t, e, r=!0) {
            if (this.isUsingMockSource())
                return null;
            null == e && (e = null);
            const n = this._source();
            if (!n)
                return e;
            if (t.y < 0 || t.y > 1)
                return e;
            const i = n.getSource().maxzoom
              , s = 1 << i
              , a = Math.floor(t.x)
              , o = t.x - a
              , l = new kh(i,a,i,Math.floor(o * s),Math.floor(t.y * s))
              , u = this.findDEMTileFor(l);
            if (!u || !u.dem)
                return e;
            const c = u.dem
              , h = 1 << u.tileID.canonical.z
              , p = (o * h - u.tileID.canonical.x) * c.dim
              , f = (t.y * h - u.tileID.canonical.y) * c.dim
              , d = Math.floor(p)
              , y = Math.floor(f);
            return (r ? this.exaggeration() : 1) * mr(mr(c.get(d, y), c.get(d, y + 1), f - y), mr(c.get(d + 1, y), c.get(d + 1, y + 1), f - y), p - d)
        }
        getAtTileOffset(t, e, r) {
            const n = 1 << t.canonical.z;
            return this.getAtPointOrZero(new nl(t.wrap + (t.canonical.x + e / bo) / n,gl(r, t.canonical) / n))
        }
        getAtTileOffsetFunc(t, e, r, n) {
            return i=>{
                const s = this.getAtTileOffset(t, i.x, i.y)
                  , a = n.upVector(t.canonical, i.x, i.y);
                return du(a, a, s * n.upVectorScale(t.canonical, e, r).metersToTile),
                a
            }
        }
        getForTilePoints(t, e, r, n) {
            if (this.isUsingMockSource())
                return !1;
            const i = im.create(this, t, n);
            return !!i && (e.forEach((t=>{
                t[2] = this.exaggeration() * i.getElevationAt(t[0], t[1], r);
            }
            )),
            !0)
        }
        getMinMaxForTile(t) {
            if (this.isUsingMockSource())
                return null;
            const e = this.findDEMTileFor(t);
            if (!e || !e.dem)
                return null;
            const r = e.dem.tree
              , n = e.tileID
              , i = 1 << t.canonical.z - n.canonical.z;
            let s = t.canonical.x / i - n.canonical.x
              , a = t.canonical._tileY / i - n.canonical.y
              , o = 0;
            for (let e = 0; e < t.canonical.z - n.canonical.z && !r.leaves[o]; e++) {
                s *= 2,
                a *= 2;
                const t = 2 * Math.floor(a) + Math.floor(s);
                o = r.childOffsets[o] + t,
                s %= 1,
                a %= 1;
            }
            return {
                min: this.exaggeration() * r.minimums[o],
                max: this.exaggeration() * r.maximums[o]
            }
        }
        getMinElevationBelowMSL() {
            throw new Error("Pure virtual method called.")
        }
        raycast(t, e, r) {
            throw new Error("Pure virtual method called.")
        }
        pointCoordinate(t) {
            throw new Error("Pure virtual method called.")
        }
        _source() {
            throw new Error("Pure virtual method called.")
        }
        isUsingMockSource() {
            throw new Error("Pure virtual method called.")
        }
        exaggeration() {
            throw new Error("Pure virtual method called.")
        }
        findDEMTileFor(t) {
            throw new Error("Pure virtual method called.")
        }
        get visibleDemTiles() {
            throw new Error("Getter must be implemented in subclass.")
        }
    }
    ,
    t.ErrorEvent = Ot,
    t.EvaluationParameters = Ts,
    t.Event = Ut,
    t.Evented = $t,
    t.FillExtrusionBucket = ch,
    t.Frustum = Ou,
    t.FrustumCorners = Uu,
    t.GLOBE_METERS_TO_ECEF = Rf,
    t.GLOBE_RADIUS = Lf,
    t.GLOBE_SCALE_MATCH_LATITUDE = 45,
    t.GLOBE_ZOOM_THRESHOLD_MAX = 6,
    t.GLOBE_ZOOM_THRESHOLD_MIN = 5,
    t.GlobeSharedBuffers = class {
        constructor(t) {
            this._createGrid(t),
            this._createPoles(t);
        }
        destroy() {
            this._poleIndexBuffer.destroy(),
            this._gridBuffer.destroy(),
            this._gridIndexBuffer.destroy(),
            this._poleNorthVertexBuffer.destroy(),
            this._poleSouthVertexBuffer.destroy();
            for (const t of this._poleSegments)
                t.destroy();
            for (const t of this._gridSegments)
                t.destroy();
            if (this._wireframeIndexBuffer) {
                this._wireframeIndexBuffer.destroy();
                for (const t of this._wireframeSegments)
                    t.destroy();
            }
        }
        _createGrid(t) {
            const e = new Ks
              , r = new pa
              , n = 65;
            for (let t = 0; t < n; t++)
                for (let r = 0; r < n; r++)
                    e.emplaceBack(r, t);
            this._gridSegments = [];
            for (let t = 0, e = 0; t < Uf.length; t++) {
                const i = Uf[t];
                for (let t = 0; t < i; t++)
                    for (let e = 0; e < 64; e++) {
                        const i = t * n + e;
                        r.emplaceBack(i + 1, i, i + n),
                        r.emplaceBack(i + n, i + n + 1, i + 1);
                    }
                const s = 64 * i * 2;
                this._gridSegments.push(vo.simpleSegment(0, e, (i + 1) * n, s)),
                e += s;
            }
            this._gridBuffer = t.createVertexBuffer(e, Ff.members),
            this._gridIndexBuffer = t.createIndexBuffer(r, !0);
        }
        _createPoles(t) {
            const e = new pa;
            for (let t = 0; t <= jf; t++)
                e.emplaceBack(0, t + 1, t + 2);
            this._poleIndexBuffer = t.createIndexBuffer(e, !0);
            const r = new ma
              , n = new ma;
            this._poleSegments = [];
            for (let t = 0, e = 0; t < 5; t++) {
                const i = 360 / (1 << t);
                r.emplaceBack(0, -Lf, 0, .5, 0),
                n.emplaceBack(0, -Lf, 0, .5, 1);
                for (let t = 0; t <= jf; t++) {
                    const e = t / jf
                      , s = mr(0, i, e)
                      , [a,o,l] = td(hd, pd, s, Lf);
                    r.emplaceBack(a, o, l, e, 0),
                    n.emplaceBack(a, o, l, e, 1);
                }
                this._poleSegments.push(vo.simpleSegment(e, 0, 66, 64)),
                e += 66;
            }
            this._poleNorthVertexBuffer = t.createVertexBuffer(r, Df, !1),
            this._poleSouthVertexBuffer = t.createVertexBuffer(n, Df, !1);
        }
        getGridBuffers(t) {
            return [this._gridBuffer, this._gridIndexBuffer, this._gridSegments[t]]
        }
        getPoleBuffers(t) {
            return [this._poleNorthVertexBuffer, this._poleSouthVertexBuffer, this._poleIndexBuffer, this._poleSegments[t]]
        }
        getWirefameBuffers(t, e) {
            if (!this._wireframeSegments) {
                const e = new xa
                  , r = jf
                  , n = r + 1;
                this._wireframeSegments = [];
                for (let t = 0, i = 0; t < Uf.length; t++) {
                    const s = Uf[t];
                    for (let t = 0; t < s; t++)
                        for (let i = 0; i < r; i++) {
                            const r = t * n + i;
                            e.emplaceBack(r, r + 1),
                            e.emplaceBack(r, r + n),
                            e.emplaceBack(r, r + n + 1);
                        }
                    const a = s * r * 3;
                    this._wireframeSegments.push(vo.simpleSegment(0, i, (s + 1) * n, a)),
                    i += a;
                }
                this._wireframeIndexBuffer = t.createIndexBuffer(e);
            }
            return [this._gridBuffer, this._wireframeIndexBuffer, this._wireframeSegments[e]]
        }
    }
    ,
    t.GlyphManager = uf,
    t.ImagePosition = Cp,
    t.LineAtlas = fy,
    t.LngLat = Ao,
    t.LngLatBounds = _o,
    t.LocalGlyphMode = lf,
    t.MAX_MERCATOR_LATITUDE = el,
    t.MercatorCoordinate = nl,
    t.MercatorTileY = ml,
    t.ONE_EM = Hh,
    t.OverscaledTileID = kh,
    t.Properties = qs,
    t.RGBAImage = Qu,
    t.Ray = ju,
    t.RequestManager = class {
        constructor(t, e, r) {
            this._transformRequestFn = t,
            this._silenceAuthErrors = !!r,
            this._createSkuToken();
        }
        _createSkuToken() {
            const t = function() {
                let t = "";
                for (let e = 0; e < 10; e++)
                    t += "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[Math.floor(62 * Math.random())];
                return {
                    token: ["1", W, t].join(""),
                    tokenExpiresAt: Date.now() + 432e5
                }
            }();
            this._skuToken = t.token,
            this._skuTokenExpiresAt = t.tokenExpiresAt;
        }
        _isSkuTokenExpired() {
            return Date.now() > this._skuTokenExpiresAt
        }
        transformRequest(t, e) {
            return this._transformRequestFn && this._transformRequestFn(t, e) || {
                url: t
            }
        }
        normalizeStyleURL(t, e) {
            if (!Q(t))
                return t;
            const r = it(t);
            return r.path = `/styles/v1${r.path}`,
            this._makeAPIURL(r, this._customAccessToken || e)
        }
        normalizeGlyphsURL(t, e) {
            if (!function(t) {
                return 0 === t.indexOf("aegis:")
            }(t))
                return t;
            const r = it(t);
            return r.path = `/fonts/v1${r.path}`,
            this._makeAPIURL(r, this._customAccessToken || e)
        }
        normalizeSourceURL(t, e, r, n) {
            if (!Q(t))
                return t;
            const i = it(t);
            return i.path = `/v1/${i.authority}.json`,
            r && i.params.push(`language=${r}`),
            n && i.params.push(`worldview=${n}`),
            this._makeAPIURL(i, this._customAccessToken || e)
        }
        normalizeSpriteURL(t, e, r, n) {
            const i = it(t);
            return Q(t) ? (i.path = `/styles/v1${i.path}/sprite${e}${r}`,
            this._makeAPIURL(i, this._customAccessToken || n)) : (i.path += `${e}${r}`,
            st(i))
        }
        normalizeTileURL(t, e, r) {
            if (t && !Q(t) && !et(t))
                return t;
            const n = it(t);
            n.path = n.path.replace(/(\.(png|jpg)\d*)(?=$)/, "$1"),
            n.path = `${n.path}`;
            const i = this._customAccessToken || rt(n.params) || Z.ACCESS_TOKEN;
            return rt(n.params) || n.params.push(`access_token=${i}`),
            st(n)
        }
        canonicalizeTileURL(t, e) {
            const r = it(t);
            if (!r.path.match(/(^\/v4\/)/) || !r.path.match(/\.[\w]+$/))
                return t;
            let n = "sgmap://tiles/";
            n += r.path.replace("/v4/", "");
            let i = r.params;
            return e && (i = i.filter((t=>!t.match(/^access_token=/)))),
            i.length && (n += `?${i.join("&")}`),
            n
        }
        canonicalizeTileset(t, e) {
            const r = !!e && Q(e)
              , n = [];
            for (const e of t.tiles || [])
                et(e) ? n.push("Sg4326" == t.reference ? this.normalizeTilesURL(e, r) : this.canonicalizeTileURL(e, r)) : n.push(e);
            return n
        }
        normalizeTilesURL(t, e) {
            if (0 !== t.indexOf("aegis:"))
                return t;
            const r = it(t);
            r.path = `/v1${r.path}`;
            const n = it(Z.API_URL);
            return r.protocol = n.protocol,
            r.authority = n.authority,
            st(r)
        }
        _makeAPIURL(t, e) {
            const r = it(Z.API_URL);
            if (t.protocol = r.protocol,
            t.authority = r.authority,
            "/" !== r.path && (t.path = `${r.path}${t.path}`),
            !(e = e || Z.ACCESS_TOKEN))
                throw new Error("请参考. See https://map.sgcc.com.cn/products/js-sdk/v3/# 进行登陆后获取资源");
            return t.params = t.params.filter((t=>-1 === t.indexOf("access_token"))),
            t.params.push(`access_token=${e || ""}`),
            st(t)
        }
    }
    ,
    t.ResourceType = zt,
    t.SegmentVector = vo,
    t.SourceCache = tm,
    t.StencilMode = Hy,
    t.StructArrayLayout1ui2 = va,
    t.StructArrayLayout2f1f2i16 = ua,
    t.StructArrayLayout2i4 = Ks,
    t.StructArrayLayout2ui4 = xa,
    t.StructArrayLayout3f12 = ha,
    t.StructArrayLayout3ui6 = pa,
    t.StructArrayLayout4i8 = Ws,
    t.StructArrayLayout5f20 = ma,
    t.Texture = py,
    t.Tile = Dy,
    t.Transitionable = Vs,
    t.Uniform1f = Ha,
    t.Uniform1i = class extends Ya {
        constructor(t) {
            super(t),
            this.current = 0;
        }
        set(t, e, r) {
            this.fetchUniformLocation(t, e) && this.current !== r && (this.current = r,
            this.gl.uniform1i(this.location, r));
        }
    }
    ,
    t.Uniform2f = class extends Ya {
        constructor(t) {
            super(t),
            this.current = [0, 0];
        }
        set(t, e, r) {
            this.fetchUniformLocation(t, e) && (r[0] === this.current[0] && r[1] === this.current[1] || (this.current = r,
            this.gl.uniform2f(this.location, r[0], r[1])));
        }
    }
    ,
    t.Uniform3f = class extends Ya {
        constructor(t) {
            super(t),
            this.current = [0, 0, 0];
        }
        set(t, e, r) {
            this.fetchUniformLocation(t, e) && (r[0] === this.current[0] && r[1] === this.current[1] && r[2] === this.current[2] || (this.current = r,
            this.gl.uniform3f(this.location, r[0], r[1], r[2])));
        }
    }
    ,
    t.Uniform4f = Ka,
    t.UniformColor = Ja,
    t.UniformMatrix2f = class extends Ya {
        constructor(t) {
            super(t),
            this.current = to;
        }
        set(t, e, r) {
            if (this.fetchUniformLocation(t, e))
                for (let t = 0; t < 4; t++)
                    if (r[t] !== this.current[t]) {
                        this.current = r,
                        this.gl.uniformMatrix2fv(this.location, !1, r);
                        break
                    }
        }
    }
    ,
    t.UniformMatrix3f = class extends Ya {
        constructor(t) {
            super(t),
            this.current = Qa;
        }
        set(t, e, r) {
            if (this.fetchUniformLocation(t, e))
                for (let t = 0; t < 9; t++)
                    if (r[t] !== this.current[t]) {
                        this.current = r,
                        this.gl.uniformMatrix3fv(this.location, !1, r);
                        break
                    }
        }
    }
    ,
    t.UniformMatrix4f = class extends Ya {
        constructor(t) {
            super(t),
            this.current = Wa;
        }
        set(t, e, r) {
            if (this.fetchUniformLocation(t, e)) {
                if (r[12] !== this.current[12] || r[0] !== this.current[0])
                    return this.current = r,
                    void this.gl.uniformMatrix4fv(this.location, !1, r);
                for (let t = 1; t < 16; t++)
                    if (r[t] !== this.current[t]) {
                        this.current = r,
                        this.gl.uniformMatrix4fv(this.location, !1, r);
                        break
                    }
            }
        }
    }
    ,
    t.UnwrappedTileID = Ah,
    t.ValidationError = Un,
    t.VectorTileWorkerSource = class extends $t {
        constructor(t, e, r, n, i) {
            super(),
            this.actor = t,
            this.layerIndex = e,
            this.availableImages = r,
            this.loadVectorData = i || pm,
            this.loading = {},
            this.loaded = {},
            this.deduped = new hm(t.scheduler),
            this.isSpriteLoaded = n,
            this.scheduler = t.scheduler;
        }
        loadTile(t, e) {
            const r = t.uid
              , n = t && t.request
              , i = n && n.collectResourceTiming
              , s = this.loading[r] = new um(t);
            s.abort = this.loadVectorData(t, ((a,o)=>{
                const l = !this.loading[r];
                if (delete this.loading[r],
                l || a || !o)
                    return s.status = "done",
                    l || (this.loaded[r] = s),
                    e(a);
                const u = o.rawData
                  , c = {};
                o.expires && (c.expires = o.expires),
                o.cacheControl && (c.cacheControl = o.cacheControl);
                let {canonical: h, reference: p, _tileY: f, _tileH: d} = t.tileID;
                s.vectorTile = o.vectorTile || new _y.VectorTile(new op(u),null,{
                    reference: p,
                    _tileY: f,
                    _tileH: d,
                    x: h.x,
                    y: h.y,
                    z: h.z
                });
                const y = ()=>{
                    s.parse(s.vectorTile, this.layerIndex, this.availableImages, this.actor, ((t,r)=>{
                        if (t || !r)
                            return e(t);
                        const s = {};
                        if (i) {
                            const t = j(n);
                            t.length > 0 && (s.resourceTiming = JSON.parse(JSON.stringify(t)));
                        }
                        e(null, v({
                            rawTileData: u.slice(0)
                        }, r, c, s));
                    }
                    ));
                }
                ;
                this.isSpriteLoaded ? y() : this.once("isSpriteLoaded", (()=>{
                    this.scheduler ? this.scheduler.add(y, {
                        type: "parseTile",
                        isSymbolTile: t.isSymbolTile,
                        zoom: t.tileZoom
                    }) : y();
                }
                )),
                this.loaded = this.loaded || {},
                this.loaded[r] = s;
            }
            ));
        }
        reloadTile(t, e) {
            const r = this.loaded
              , n = t.uid
              , i = this;
            if (r && r[n]) {
                const s = r[n];
                s.showCollisionBoxes = t.showCollisionBoxes,
                s.enableTerrain = !!t.enableTerrain,
                s.projection = t.projection,
                s.tileTransform = dd(t.tileID.canonical, t.projection),
                s.tileID = t.tileID;
                const a = (t,r)=>{
                    const n = s.reloadCallback;
                    n && (delete s.reloadCallback,
                    s.parse(s.vectorTile, i.layerIndex, this.availableImages, i.actor, n)),
                    e(t, r);
                }
                ;
                "parsing" === s.status ? s.reloadCallback = a : "done" === s.status && (s.vectorTile ? s.parse(s.vectorTile, this.layerIndex, this.availableImages, this.actor, a) : a());
            }
        }
        abortTile(t, e) {
            const r = t.uid
              , n = this.loading[r];
            n && (n.abort && n.abort(),
            delete this.loading[r]),
            e();
        }
        removeTile(t, e) {
            const r = this.loaded
              , n = t.uid;
            r && r[n] && delete r[n],
            e();
        }
    }
    ,
    t.WritingMode = Pp,
    t.ZoomHistory = Ei,
    t._addCustomSource = function(t) {
        !kt(t) && At.push(t);
    }
    ,
    t._removeCustomSource = function(t) {
        kt(t) && At.splice(At.indexOf(t), 1);
    }
    ,
    t.add = uu,
    t.addDynamicAttributes = Ud,
    t.adjoint = function(t, e) {
        var r = e[0]
          , n = e[1]
          , i = e[2]
          , s = e[3]
          , a = e[4]
          , o = e[5]
          , l = e[6]
          , u = e[7]
          , c = e[8];
        return t[0] = a * c - o * u,
        t[1] = i * u - n * c,
        t[2] = n * o - i * a,
        t[3] = o * l - s * c,
        t[4] = r * c - i * l,
        t[5] = i * s - r * o,
        t[6] = s * u - a * l,
        t[7] = n * l - r * u,
        t[8] = r * a - n * s,
        t
    }
    ,
    t.asyncAll = g,
    t.bezier = p,
    t.bindAll = k,
    t.boundsAttributes = Vy,
    t.bufferConvexPolygon = function(t, e) {
        const r = [];
        for (let n = 0; n < t.length; n++) {
            const i = m(n - 1, -1, t.length - 1)
              , s = m(n + 1, -1, t.length - 1)
              , a = t[n]
              , o = t[s]
              , l = t[i].sub(a).unit()
              , u = o.sub(a).unit()
              , c = u.angleWithSep(l.x, l.y)
              , h = l.add(u).unit().mult(-1 * e / Math.sin(c / 2));
            r.push(a.add(h));
        }
        return r
    }
    ,
    t.cacheEntryPossiblyAdded = function(t) {
        yt++,
        yt > lt && (t.getActor().send("enforceCacheSizeLimit", ot),
        yt = 0);
    }
    ,
    t.calculateGlobeLabelMatrix = function(t, e) {
        const {x: r, y: n} = t.point
          , i = od(r, n, t.worldSize / t._pixelsPerMercatorPixel, 0, 0);
        return Jl(i, i, ad(Xf(e)))
    }
    ,
    t.calculateGlobeMatrix = function(t) {
        const {x: e, y: r} = t.point
          , {lng: n, lat: i} = t._center;
        return od(e, r, t.worldSize, n, i)
    }
    ,
    t.calculateGlobeMercatorMatrix = function(t) {
        const e = t.pixelsPerMeter
          , r = e / Jo(1, t.center.lat)
          , n = Hl(new Float64Array(16));
        return Wl(n, n, [t.point.x, t.point.y, 0]),
        Ql(n, n, [r, r, e]),
        Float32Array.from(n)
    }
    ,
    t.changeCrs = Xo,
    t.checkCustomTileSource = function(t, e, r) {
        if ("raster" != e.type && "raster-dem" != e.type)
            return;
        let n = e.tiles;
        if (!n)
            return;
        if (kt(t))
            return void (e.tilesecurity = !1);
        let i = !0;
        for (let t = 0; t < n.length; t++)
            if (n[t] && !n[t].split("?")[0].match(/\.sg$/)) {
                i = !1;
                break
            }
        if (!i)
            throw delete r._userDatas.sources[t],
            new Error(`source:${t} 非标准数据源`);
        e.tilesecurity = !0;
    }
    ,
    t.circumferenceAtLatitude = function(t) {
        return Zo[Z.crs || Go].circumferenceAtLatitude(t)
    }
    ,
    t.clamp = d,
    t.clearTileCache = function(t) {
        const e = ht()
          , r = [];
        for (const t in ut)
            e && r.push(e.delete(t)),
            delete ut[t];
        t && Promise.all(r).catch(t).then((()=>t()));
    }
    ,
    t.clipLine = nf,
    t.clone = function(t) {
        var e = new Gl(16);
        return e[0] = t[0],
        e[1] = t[1],
        e[2] = t[2],
        e[3] = t[3],
        e[4] = t[4],
        e[5] = t[5],
        e[6] = t[6],
        e[7] = t[7],
        e[8] = t[8],
        e[9] = t[9],
        e[10] = t[10],
        e[11] = t[11],
        e[12] = t[12],
        e[13] = t[13],
        e[14] = t[14],
        e[15] = t[15],
        e
    }
    ,
    t.clone$1 = I,
    t.collisionCircleLayout = Yh,
    t.config = Z,
    t.conjugate = function(t, e) {
        return t[0] = -e[0],
        t[1] = -e[1],
        t[2] = -e[2],
        t[3] = e[3],
        t
    }
    ,
    t.create = function() {
        var t = new Gl(16);
        return Gl != Float32Array && (t[1] = 0,
        t[2] = 0,
        t[3] = 0,
        t[4] = 0,
        t[6] = 0,
        t[7] = 0,
        t[8] = 0,
        t[9] = 0,
        t[11] = 0,
        t[12] = 0,
        t[13] = 0,
        t[14] = 0),
        t[0] = 1,
        t[5] = 1,
        t[10] = 1,
        t[15] = 1,
        t
    }
    ,
    t.create$1 = Xl,
    t.createCommonjsModule = fe,
    t.createExpression = Dn,
    t.createLayout = Ys,
    t.createStyleLayer = function(t) {
        return "custom" === t.type ? new Jd(t) : new hy[t.type](t)
    }
    ,
    t.cross = xu,
    t.decodeFeatures = t=>{
        t.features && t.features.length > 0 && (t=>{
            const e = t=>Array.isArray(t) ? e(t[0]) : "string" == typeof t && isNaN(t);
            return e(t.coordinates)
        }
        )(t.features[0].geometry) && t.features.forEach((t=>{
            (t=>{
                const e = _t(t.geometry.coordinates);
                t.geometry.coordinates = e;
            }
            )(t);
        }
        ));
    }
    ,
    t.degToRad = l,
    t.distance = function(t, e) {
        return Math.hypot(e[0] - t[0], e[1] - t[1], e[2] - t[2])
    }
    ,
    t.div = function(t, e, r) {
        return t[0] = e[0] / r[0],
        t[1] = e[1] / r[1],
        t[2] = e[2] / r[2],
        t
    }
    ,
    t.dot = gu,
    t.ease = f,
    t.easeCubicInOut = h,
    t.emitValidationErrors = Si,
    t.endsWith = z,
    t.enforceCacheSizeLimit = function(t) {
        for (const e in ut)
            pt(e),
            ut[e].then((e=>{
                e.keys().then((r=>{
                    for (let n = 0; n < r.length - t; n++)
                        e.delete(r[n]);
                }
                ));
            }
            ));
    }
    ,
    t.evaluateSizeForFeature = Wh,
    t.evaluateSizeForZoom = Qh,
    t.evaluateVariableOffset = Af,
    t.evented = zs,
    t.exactEquals = function(t, e) {
        return t[0] === e[0] && t[1] === e[1] && t[2] === e[2] && t[3] === e[3]
    }
    ,
    t.exactEquals$1 = function(t, e) {
        return t[0] === e[0] && t[1] === e[1] && t[2] === e[2]
    }
    ,
    t.exported = N,
    t.exported$1 = G,
    t.extend = v,
    t.extend$1 = Nt,
    t.fillExtrusionHeightLift = gh,
    t.filterObject = M,
    t.formatAjax = t=>"string" == typeof t ? {
        method: "GET",
        url: t
    } : (t.method || (t.method = "GET"),
    t.data && (t.body = t.body ? {
        ...t.data,
        ...t.body
    } : t.data,
    delete t.data),
    "GET" === t.method.toUpperCase() && (t.url = gt({
        url: t.url,
        params: t.body
    }),
    delete t.body),
    t),
    t.fromMat4 = function(t, e) {
        return t[0] = e[0],
        t[1] = e[1],
        t[2] = e[2],
        t[3] = e[4],
        t[4] = e[5],
        t[5] = e[6],
        t[6] = e[8],
        t[7] = e[9],
        t[8] = e[10],
        t
    }
    ,
    t.fromQuat = function(t, e) {
        var r = e[0]
          , n = e[1]
          , i = e[2]
          , s = e[3]
          , a = r + r
          , o = n + n
          , l = i + i
          , u = r * a
          , c = n * a
          , h = n * o
          , p = i * a
          , f = i * o
          , d = i * l
          , y = s * a
          , m = s * o
          , g = s * l;
        return t[0] = 1 - h - d,
        t[1] = c + g,
        t[2] = p - m,
        t[3] = 0,
        t[4] = c - g,
        t[5] = 1 - u - d,
        t[6] = f + y,
        t[7] = 0,
        t[8] = p + m,
        t[9] = f - y,
        t[10] = 1 - u - h,
        t[11] = 0,
        t[12] = 0,
        t[13] = 0,
        t[14] = 0,
        t[15] = 1,
        t
    }
    ,
    t.fromRotation = function(t, e) {
        var r = Math.sin(e)
          , n = Math.cos(e);
        return t[0] = n,
        t[1] = r,
        t[2] = 0,
        t[3] = -r,
        t[4] = n,
        t[5] = 0,
        t[6] = 0,
        t[7] = 0,
        t[8] = 1,
        t
    }
    ,
    t.fromScaling = ru,
    t.furthestTileCorner = function(t) {
        const e = Math.round((t + 45 + 360) % 360 / 90) % 4;
        return c[e]
    }
    ,
    t.getAABBPointSquareDist = function(t, e, r) {
        let n = 0;
        for (let i = 0; i < 2; ++i) {
            const s = r ? r[i] : 0;
            t[i] > s && (n += (t[i] - s) * (t[i] - s)),
            e[i] < s && (n += (s - e[i]) * (s - e[i]));
        }
        return n
    }
    ,
    t.getAnchorAlignment = Zp,
    t.getAnchorJustification = zf,
    t.getBounds = function(t) {
        let e = 1 / 0
          , r = 1 / 0
          , n = -1 / 0
          , s = -1 / 0;
        for (const i of t)
            e = Math.min(e, i.x),
            r = Math.min(r, i.y),
            n = Math.max(n, i.x),
            s = Math.max(s, i.y);
        return {
            min: new i(e,r),
            max: new i(n,s)
        }
    }
    ,
    t.getColumn = L,
    t.getGridMatrix = function(t, e, r, n) {
        const i = e.getNorth()
          , s = e.getSouth()
          , a = e.getWest()
          , o = e.getEast()
          , l = 1 << t.z
          , u = o - a
          , c = i - s
          , h = u / jf
          , p = -c / Uf[r]
          , f = [0, h, 0, p, 0, 0, i, a, 0];
        if (t.z > 0) {
            const t = 180 / n;
            Yl(f, f, [t / u + 1, 0, 0, 0, t / c + 1, 0, -.5 * t / h, .5 * t / p, 1]);
        }
        return f[2] = l,
        f[5] = t.x,
        f[8] = t._tileY,
        f
    }
    ,
    t.getImage = Lt,
    t.getJSON = function(t, e) {
        return Ct(v(t, {
            type: "json"
        }), e)
    }
    ,
    t.getLatitudinalLod = function(t) {
        const e = 80.051129;
        t = d(t, -80.051129, e) / e * 90;
        const r = Math.pow(Math.abs(Math.sin(l(t))), 3);
        return Math.round(r * (Uf.length - 1))
    }
    ,
    t.getMecYRange = xl,
    t.getPerformanceMeasurement = j,
    t.getProjection = Ed,
    t.getRTLTextPluginStatus = Ss,
    t.getReferrer = Mt,
    t.getTilePoint = function(t, {x: e, y: r}, n=0) {
        return new i(((e - n) * t.scale - t.x) * bo,(r * t.scale - (t._tileY || t.y)) / (t._tileH || 1) * bo)
    }
    ,
    t.getTileVec3 = function(t, e, r=0) {
        return lu(((e.x - r) * t.scale - t.x) * bo, (e.y * t.scale - (t._tileY || t.y)) / (t._tileH || 1) * bo, tl(e.z, e.y))
    }
    ,
    t.getVideo = function(t, r) {
        const n = e.document.createElement("video");
        n.muted = !0,
        n.onloadstart = function() {
            r(null, n);
        }
        ;
        for (let r = 0; r < t.length; r++) {
            const i = e.document.createElement("source");
            Pt(t[r]) || (n.crossOrigin = "Anonymous"),
            i.src = t[r],
            n.appendChild(i);
        }
        return {
            cancel: ()=>{}
        }
    }
    ,
    t.globeCenterToScreenPoint = function(t) {
        const e = [0, 0, 0]
          , r = Hl(new Float64Array(16));
        return Jl(r, t.pixelMatrix, t.globeMatrix),
        vu(e, e, r),
        new i(e[0],e[1])
    }
    ,
    t.globeDenormalizeECEF = ad,
    t.globeECEFOrigin = function(t, e) {
        const r = [0, 0, 0];
        return vu(r, r, sd(Xf(e.canonical))),
        vu(r, r, t),
        r
    }
    ,
    t.globeNormalizeECEF = sd,
    t.globePixelsToTileUnits = function(t, e) {
        return bo / (512 * Math.pow(2, t)) * nd(Xf(e))
    }
    ,
    t.globePoleMatrixForTile = function(t, e, r) {
        const n = Hl(new Float64Array(16))
          , i = (e / (1 << t) - .5) * Math.PI * 2;
        return eu(n, r.globeMatrix, i),
        Float32Array.from(n)
    }
    ,
    t.globeTileBounds = Xf,
    t.globeTiltAtLngLat = ud,
    t.globeToMercatorTransition = ld,
    t.globeUseCustomAntiAliasing = function(t, e, r) {
        const n = ld(r.zoom)
          , i = t.style.map._antialias
          , s = !!e.extStandardDerivatives
          , a = e.extStandardDerivativesForceOff || t.terrain && t.terrain.exaggeration() > 0;
        return 0 === n && !i && !a && s
    }
    ,
    t.identity = Hl,
    t.identity$1 = Iu,
    t.initApiURI = (t,e)=>{
        const r = document.getElementsByTagName("script")
          , n = [];
        let i = -1;
        for (; ++i < r.length; ) {
            const e = r[i];
            e.src && /http[s]?\:\/\/[\w\d\.\:-]+\/(maps\?v=[\d\.]+|api\/gl\/epgis-[\d\.]+\.min\.js)/.test(e.src) && -1 !== e.src.indexOf(t) && n.push(/http[s]?\:\/\/[\w\d\.\:-]+/.exec(e.src)[0]);
        }
        vt("识别SDK JS加载的路径"),
        vt(n),
        0 === n.length ? console.warn("版本没有匹配") : (e.API_URL = n[0],
        (({API_URL: t},e)=>{
            const r = document.createElement("link");
            r.setAttribute("rel", "stylesheet"),
            r.setAttribute("href", `${t}/api/gl/epgis-${e}.min.css`),
            (document.head || document.getElementsByTagName("head")[0]).appendChild(r);
        }
        )(e, t));
    }
    ,
    t.invert = Kl,
    t.isFullscreen = function() {
        return !!e.document.fullscreenElement || !!e.document.webkitFullscreenElement
    }
    ,
    t.isLngLatBehindGlobe = function(t, e) {
        return ud(t, e) > Math.PI / 2 * 1.01
    }
    ,
    t.issgmapURL = Q,
    t.isSafariWithAntialiasingBug = function(t) {
        const e = t.navigator ? t.navigator.userAgent : null;
        return !!F(t) && e && (e.match("Version/15.4") || e.match("Version/15.5") || e.match(/CPU (OS|iPhone OS) (15_4|15_5) like Mac OS X/))
    }
    ,
    t.latFromMercatorY = Qo,
    t.len = ku,
    t.length = ou,
    t.length$1 = function(t) {
        return Math.hypot(t[0], t[1], t[2], t[3])
    }
    ,
    t.loadVectorTile = pm,
    t.makeRequest = Ct,
    t.makeRequest2 = function(t, r) {
        const n = xt(t.url)
          , {access_token: i} = n.params;
        if (void 0 === t.cache && (t.cache = !0),
        i && (delete n.params.access_token,
        t.headers || (t.headers = {}),
        t.headers.Authorization = i),
        t.url = gt(n),
        t.url = encodeURI(t.url),
        !It(t.url)) {
            if (e.fetch && e.Request && e.AbortController && e.Request.prototype.hasOwnProperty("signal"))
                return Tt(t, r);
            if (P() && self.worker && self.worker.actor)
                return self.worker.actor.send("getResource", t, r, void 0, !0)
        }
        return Bt(t, r)
    }
    ,
    t.mapValue = function(t, e, r, n, i) {
        return d((t - e) / (r - e) * (i - n) + n, n, i)
    }
    ,
    t.mercatorScale = rl,
    t.mercatorXfromLng = Ho,
    t.mercatorYfromLat = Ko,
    t.mercatorZfromAltitude = Jo,
    t.mul = iu,
    t.mul$1 = Au,
    t.multiply = Jl,
    t.multiply$1 = Yl,
    t.multiply$2 = hu,
    t.mvt = _y,
    t.nextPowerOfTwo = A,
    t.normalize = mu,
    t.normalize$1 = function(t, e) {
        var r = e[0]
          , n = e[1]
          , i = e[2]
          , s = e[3]
          , a = r * r + n * n + i * i + s * s;
        return a > 0 && (a = 1 / Math.sqrt(a)),
        t[0] = r * a,
        t[1] = n * a,
        t[2] = i * a,
        t[3] = s * a,
        t
    }
    ,
    t.number = mr,
    t.ortho = function(t, e, r, n, i, s, a) {
        var o = 1 / (e - r)
          , l = 1 / (n - i)
          , u = 1 / (s - a);
        return t[0] = -2 * o,
        t[1] = 0,
        t[2] = 0,
        t[3] = 0,
        t[4] = 0,
        t[5] = -2 * l,
        t[6] = 0,
        t[7] = 0,
        t[8] = 0,
        t[9] = 0,
        t[10] = 2 * u,
        t[11] = 0,
        t[12] = (e + r) * o,
        t[13] = (i + n) * l,
        t[14] = (a + s) * u,
        t[15] = 1,
        t
    }
    ,
    t.pbf = op,
    t.perspective = function(t, e, r, n, i) {
        var s, a = 1 / Math.tan(e / 2);
        return t[0] = a / r,
        t[1] = 0,
        t[2] = 0,
        t[3] = 0,
        t[4] = 0,
        t[5] = a,
        t[6] = 0,
        t[7] = 0,
        t[8] = 0,
        t[9] = 0,
        t[11] = -1,
        t[12] = 0,
        t[13] = 0,
        t[15] = 0,
        null != i && i !== 1 / 0 ? (t[10] = (i + n) * (s = 1 / (n - i)),
        t[14] = 2 * i * n * s) : (t[10] = -1,
        t[14] = -2 * n),
        t
    }
    ,
    t.pick = function(t, e) {
        const r = {};
        for (let n = 0; n < e.length; n++) {
            const i = e[n];
            i in t && (r[i] = t[i]);
        }
        return r
    }
    ,
    t.plugin = Is,
    t.pointGeometry = i,
    t.polygonContainsPoint = Fl,
    t.polygonIntersectsBox = Ll,
    t.polygonIntersectsPolygon = Ml,
    t.polygonizeBounds = function(t, e, r=0, n=!0) {
        const s = new i(r,r)
          , a = t.sub(s)
          , o = e.add(s)
          , l = [a, new i(o.x,a.y), o, new i(a.x,o.y)];
        return n && l.push(a.clone()),
        l
    }
    ,
    t.posAttributes = Ff,
    t.potpack = Bp,
    t.prevPowerOfTwo = function(t) {
        return t <= 1 ? 1 : Math.pow(2, Math.floor(Math.log(t) / Math.LN2))
    }
    ,
    t.radToDeg = u,
    t.refProperties = ["type", "source", "source-layer", "minzoom", "maxzoom", "filter", "layout"],
    t.registerForPluginStateChange = function(t) {
        return t({
            pluginStatus: _s,
            pluginURL: ws
        }),
        zs.on("pluginStateChange", t),
        t
    }
    ,
    t.renderColorRamp = ec,
    t.resample = sl,
    t.rotateX = tu,
    t.rotateX$1 = Tu,
    t.rotateY = eu,
    t.rotateY$1 = Bu,
    t.rotateZ = function(t, e, r) {
        var n = Math.sin(r)
          , i = Math.cos(r)
          , s = e[0]
          , a = e[1]
          , o = e[2]
          , l = e[3]
          , u = e[4]
          , c = e[5]
          , h = e[6]
          , p = e[7];
        return e !== t && (t[8] = e[8],
        t[9] = e[9],
        t[10] = e[10],
        t[11] = e[11],
        t[12] = e[12],
        t[13] = e[13],
        t[14] = e[14],
        t[15] = e[15]),
        t[0] = s * i + u * n,
        t[1] = a * i + c * n,
        t[2] = o * i + h * n,
        t[3] = l * i + p * n,
        t[4] = u * i - s * n,
        t[5] = c * i - a * n,
        t[6] = h * i - o * n,
        t[7] = p * i - l * n,
        t
    }
    ,
    t.rotateZ$1 = function(t, e, r) {
        r *= .5;
        var n = e[0]
          , i = e[1]
          , s = e[2]
          , a = e[3]
          , o = Math.sin(r)
          , l = Math.cos(r);
        return t[0] = n * l + i * o,
        t[1] = i * l - n * o,
        t[2] = s * l + a * o,
        t[3] = a * l - s * o,
        t
    }
    ,
    t.scale = Ql,
    t.scale$1 = zu,
    t.scale$2 = du,
    t.scaleAndAdd = yu,
    t.securityTile = mt,
    t.setCacheLimits = function(t, e) {
        ot = t,
        lt = e;
    }
    ,
    t.setColumn = function(t, e, r) {
        t[4 * e + 0] = r[0],
        t[4 * e + 1] = r[1],
        t[4 * e + 2] = r[2],
        t[4 * e + 3] = r[3];
    }
    ,
    t.setRTLTextPlugin = function(t, e, r=!1) {
        if (_s === gs || _s === xs || _s === vs)
            throw new Error("setRTLTextPlugin cannot be called multiple times.");
        ws = N.resolveURL(t),
        _s = gs,
        bs = e,
        ks(),
        r || Ms();
    }
    ,
    t.setWaterMarkLayer = (t,e=!1,r)=>{
        const n = JSON.parse(window.atob(Z.ACCESS_TOKEN.split(".")[1]));
        let i = n && "N" === n.Issuance
          , s = {
            text: r || "",
            color: "rgba(17, 102, 184,0.1)",
            rotate: 0
        };
        i || e ? (!i && e ? (s.text = r,
        s.size = 18) : i && !e ? (s.text = "思极地图-测试",
        s.color = "rgba(0, 0,0, 0.1)",
        s.size = 30) : (s.text = "思极地图-测试\n" + r,
        s.rotate = 30,
        s.size = 18),
        s.show = !0) : s.show = !1,
        t.painter._waterSetting = s,
        t._update(!0);
    }
    ,
    t.smoothstep = y,
    t.spec = qt,
    t.sub = wu,
    t.subtract = cu,
    t.symbolSize = tp,
    t.tileAABB = function(t, e, r, n, i, s, a, o, l, u, c, h, p) {
        if ("globe" === l.name)
            return Jf(t, e, new wh(r,n,i,{
                reference: u,
                sourceID: c,
                _tileY: h,
                _tileH: p
            }));
        const f = dd({
            z: r,
            x: n,
            y: i,
            reference: u,
            sourceID: c,
            _tileY: h,
            _tileH: p
        }, l);
        return new $u([(s + f.x / f.scale) * e, e * (f.y / f.scale), a],[(s + f.x2 / f.scale) * e, e * (f.y2 / f.scale), o])
    }
    ,
    t.tileCornersToBounds = Wf,
    t.tileTransform = dd,
    t.transformMat3 = function(t, e, r) {
        var n = e[0]
          , i = e[1]
          , s = e[2];
        return t[0] = n * r[0] + i * r[3] + s * r[6],
        t[1] = n * r[1] + i * r[4] + s * r[7],
        t[2] = n * r[2] + i * r[5] + s * r[8],
        t
    }
    ,
    t.transformMat4 = vu,
    t.transformMat4$1 = Su,
    t.transformQuat = bu,
    t.transitionTileAABBinECEF = Hf,
    t.translate = Wl,
    t.transpose = function(t, e) {
        if (t === e) {
            var r = e[1]
              , n = e[2]
              , i = e[5];
            t[1] = e[3],
            t[2] = e[6],
            t[3] = r,
            t[5] = e[7],
            t[6] = n,
            t[7] = i;
        } else
            t[0] = e[0],
            t[1] = e[3],
            t[2] = e[6],
            t[3] = e[1],
            t[4] = e[4],
            t[5] = e[7],
            t[6] = e[2],
            t[7] = e[5],
            t[8] = e[8];
        return t
    }
    ,
    t.triggerPluginCompletionEvent = As,
    t.uniqueId = w,
    t.updateGlobeVertexNormal = function(t, e, r, n, i) {
        const s = 5 * e + 2;
        t.float32[s + 0] = r,
        t.float32[s + 1] = n,
        t.float32[s + 2] = i;
    }
    ,
    t.validateCustomStyleLayer = function(t) {
        const e = []
          , r = t.id;
        return void 0 === r && e.push({
            message: `layers.${r}: missing required property "id"`
        }),
        void 0 === t.render && e.push({
            message: `layers.${r}: missing required method "render"`
        }),
        t.renderingMode && "2d" !== t.renderingMode && "3d" !== t.renderingMode && e.push({
            message: `layers.${r}: property "renderingMode" must be either "2d" or "3d"`
        }),
        e
    }
    ,
    t.validateFilter = t=>zi(oi(t)),
    t.validateFog = t=>zi(xi(t)),
    t.validateLayer = t=>zi(pi(t)),
    t.validateLight = t=>zi(mi(t)),
    t.validateSource = t=>zi(yi(t)),
    t.validateStyle = wi,
    t.validateTerrain = t=>zi(gi(t)),
    t.values = x,
    t.vectorTile = nh,
    t.warnOnce = B,
    t.window = e,
    t.wrap = m;
}
)(sharedChunk);
(function(e) {
    "use strict";
    function t(e) {
        if ("number" == typeof e || "boolean" == typeof e || "string" == typeof e || null == e)
            return JSON.stringify(e);
        if (Array.isArray(e)) {
            let r = "[";
            for (const o of e)
                r += `${t(o)},`;
            return `${r}]`
        }
        let r = "{";
        for (const o of Object.keys(e).sort())
            r += `${o}:${t(e[o])},`;
        return `${r}}`
    }
    function r(r) {
        let o = "";
        for (const n of e.refProperties)
            o += `/${t(r[n])}`;
        return o
    }
    class o {
        constructor(e) {
            this.keyCache = {},
            e && this.replace(e);
        }
        replace(e) {
            this._layerConfigs = {},
            this._layers = {},
            this.update(e, []);
        }
        update(t, o) {
            for (const r of t)
                this._layerConfigs[r.id] = r,
                (this._layers[r.id] = e.createStyleLayer(r)).compileFilter(),
                this.keyCache[r.id] && delete this.keyCache[r.id];
            for (const e of o)
                delete this.keyCache[e],
                delete this._layerConfigs[e],
                delete this._layers[e];
            this.familiesBySource = {};
            const n = function(e, t) {
                const o = {};
                for (let n = 0; n < e.length; n++) {
                    const i = t && t[e[n].id] || r(e[n]);
                    t && (t[e[n].id] = i);
                    let s = o[i];
                    s || (s = o[i] = []),
                    s.push(e[n]);
                }
                const n = [];
                for (const e in o)
                    n.push(o[e]);
                return n
            }(e.values(this._layerConfigs), this.keyCache);
            for (const e of n) {
                const t = e.map((e=>this._layers[e.id]))
                  , r = t[0];
                if ("none" === r.visibility)
                    continue;
                const o = r.source || "";
                let n = this.familiesBySource[o];
                n || (n = this.familiesBySource[o] = {});
                const i = r.sourceLayer || "_geojsonTileLayer";
                let s = n[i];
                s || (s = n[i] = []),
                s.push(t);
            }
        }
    }
    class n {
        loadTile(t, r) {
            const {uid: o, encoding: n, rawImageData: i, padding: s, buildQuadTree: a} = t
              , l = e.window.ImageBitmap && i instanceof e.window.ImageBitmap ? this.getImageData(i, s) : i;
            r(null, new e.DEMData(o,l,n,s < 1,a));
        }
        getImageData(e, t) {
            this.offscreenCanvas && this.offscreenCanvasContext || (this.offscreenCanvas = new OffscreenCanvas(e.width,e.height),
            this.offscreenCanvasContext = this.offscreenCanvas.getContext("2d", {
                willReadFrequently: !0
            })),
            this.offscreenCanvas.width = e.width,
            this.offscreenCanvas.height = e.height,
            this.offscreenCanvasContext.drawImage(e, 0, 0, e.width, e.height);
            const r = this.offscreenCanvasContext.getImageData(-t, -t, e.width + 2 * t, e.height + 2 * t);
            return this.offscreenCanvasContext.clearRect(0, 0, this.offscreenCanvas.width, this.offscreenCanvas.height),
            r
        }
    }
    var i = function e(t, r) {
        var o, n = t && t.type;
        if ("FeatureCollection" === n)
            for (o = 0; o < t.features.length; o++)
                e(t.features[o], r);
        else if ("GeometryCollection" === n)
            for (o = 0; o < t.geometries.length; o++)
                e(t.geometries[o], r);
        else if ("Feature" === n)
            e(t.geometry, r);
        else if ("Polygon" === n)
            s(t.coordinates, r);
        else if ("MultiPolygon" === n)
            for (o = 0; o < t.coordinates.length; o++)
                s(t.coordinates[o], r);
        return t
    };
    function s(e, t) {
        if (0 !== e.length) {
            a(e[0], t);
            for (var r = 1; r < e.length; r++)
                a(e[r], !t);
        }
    }
    function a(e, t) {
        for (var r = 0, o = 0, n = 0, i = e.length, s = i - 1; n < i; s = n++) {
            var a = (e[n][0] - e[s][0]) * (e[s][1] + e[n][1])
              , l = r + a;
            o += Math.abs(r) >= Math.abs(a) ? r - l + a : a - l + r,
            r = l;
        }
        r + o >= 0 != !!t && e.reverse();
    }
    const l = e.mvt.VectorTileFeature.prototype.toGeoJSON;
    class u {
        constructor(t) {
            this._feature = t,
            this.extent = e.EXTENT,
            this.type = t.type,
            this.properties = t.tags,
            "id"in t && !isNaN(t.id) && (this.id = parseInt(t.id, 10));
        }
        loadGeometry() {
            if (1 === this._feature.type) {
                const t = [];
                for (const r of this._feature.geometry)
                    t.push([new e.pointGeometry(r[0],r[1])]);
                return t
            }
            {
                const t = [];
                for (const r of this._feature.geometry) {
                    const o = [];
                    for (const t of r)
                        o.push(new e.pointGeometry(t[0],t[1]));
                    t.push(o);
                }
                return t
            }
        }
        toGeoJSON(e, t, r) {
            return l.call(this, e, t, r)
        }
    }
    class h {
        constructor(t) {
            this.layers = {
                _geojsonTileLayer: this
            },
            this.name = "_geojsonTileLayer",
            this.extent = e.EXTENT,
            this.length = t.length,
            this._features = t;
        }
        feature(e) {
            return new u(this._features[e])
        }
    }
    var c = e.vectorTile.VectorTileFeature
      , f = p;
    function p(e, t) {
        this.options = t || {},
        this.features = e,
        this.length = e.length;
    }
    function g(e, t) {
        this.id = "number" == typeof e.id ? e.id : void 0,
        this.type = e.type,
        this.rawGeometry = 1 === e.type ? [e.geometry] : e.geometry,
        this.properties = e.tags,
        this.extent = t || 4096;
    }
    p.prototype.feature = function(e) {
        return new g(this.features[e],this.options.extent)
    }
    ,
    g.prototype.loadGeometry = function() {
        var t = this.rawGeometry;
        this.geometry = [];
        for (var r = 0; r < t.length; r++) {
            for (var o = t[r], n = [], i = 0; i < o.length; i++)
                n.push(new e.pointGeometry(o[i][0],o[i][1]));
            this.geometry.push(n);
        }
        return this.geometry
    }
    ,
    g.prototype.bbox = function() {
        this.geometry || this.loadGeometry();
        for (var e = this.geometry, t = 1 / 0, r = -1 / 0, o = 1 / 0, n = -1 / 0, i = 0; i < e.length; i++)
            for (var s = e[i], a = 0; a < s.length; a++) {
                var l = s[a];
                t = Math.min(t, l.x),
                r = Math.max(r, l.x),
                o = Math.min(o, l.y),
                n = Math.max(n, l.y);
            }
        return [t, o, r, n]
    }
    ,
    g.prototype.toGeoJSON = c.prototype.toGeoJSON;
    var d = y
      , m = f;
    function y(t) {
        var r = new e.pbf;
        return function(e, t) {
            for (var r in e.layers)
                t.writeMessage(3, v, e.layers[r]);
        }(t, r),
        r.finish()
    }
    function v(e, t) {
        var r;
        t.writeVarintField(15, e.version || 1),
        t.writeStringField(1, e.name || ""),
        t.writeVarintField(5, e.extent || 4096);
        var o = {
            keys: [],
            values: [],
            keycache: {},
            valuecache: {}
        };
        for (r = 0; r < e.length; r++)
            o.feature = e.feature(r),
            t.writeMessage(2, x, o);
        var n = o.keys;
        for (r = 0; r < n.length; r++)
            t.writeStringField(3, n[r]);
        var i = o.values;
        for (r = 0; r < i.length; r++)
            t.writeMessage(4, b, i[r]);
    }
    function x(e, t) {
        var r = e.feature;
        void 0 !== r.id && t.writeVarintField(1, r.id),
        t.writeMessage(2, w, e),
        t.writeVarintField(3, r.type),
        t.writeMessage(4, P, r);
    }
    function w(e, t) {
        var r = e.feature
          , o = e.keys
          , n = e.values
          , i = e.keycache
          , s = e.valuecache;
        for (var a in r.properties) {
            var l = r.properties[a]
              , u = i[a];
            if (null !== l) {
                void 0 === u && (o.push(a),
                i[a] = u = o.length - 1),
                t.writeVarint(u);
                var h = typeof l;
                "string" !== h && "boolean" !== h && "number" !== h && (l = JSON.stringify(l));
                var c = h + ":" + l
                  , f = s[c];
                void 0 === f && (n.push(l),
                s[c] = f = n.length - 1),
                t.writeVarint(f);
            }
        }
    }
    function S(e, t) {
        return (t << 3) + (7 & e)
    }
    function M(e) {
        return e << 1 ^ e >> 31
    }
    function P(e, t) {
        for (var r = e.loadGeometry(), o = e.type, n = 0, i = 0, s = r.length, a = 0; a < s; a++) {
            var l = r[a]
              , u = 1;
            1 === o && (u = l.length),
            t.writeVarint(S(1, u));
            for (var h = 3 === o ? l.length - 1 : l.length, c = 0; c < h; c++) {
                1 === c && 1 !== o && t.writeVarint(S(2, h - 1));
                var f = l[c].x - n
                  , p = l[c].y - i;
                t.writeVarint(M(f)),
                t.writeVarint(M(p)),
                n += f,
                i += p;
            }
            3 === o && t.writeVarint(S(7, 1));
        }
    }
    function b(e, t) {
        var r = typeof e;
        "string" === r ? t.writeStringField(1, e) : "boolean" === r ? t.writeBooleanField(7, e) : "number" === r && (e % 1 != 0 ? t.writeDoubleField(3, e) : e < 0 ? t.writeSVarintField(6, e) : t.writeVarintField(5, e));
    }
    function T(e, t, r, o, n, i) {
        if (n - o <= r)
            return;
        const s = o + n >> 1;
        k(e, t, s, o, n, i % 2),
        T(e, t, r, o, s - 1, i + 1),
        T(e, t, r, s + 1, n, i + 1);
    }
    function k(e, t, r, o, n, i) {
        for (; n > o; ) {
            if (n - o > 600) {
                const s = n - o + 1
                  , a = r - o + 1
                  , l = Math.log(s)
                  , u = .5 * Math.exp(2 * l / 3)
                  , h = .5 * Math.sqrt(l * u * (s - u) / s) * (a - s / 2 < 0 ? -1 : 1);
                k(e, t, r, Math.max(o, Math.floor(r - a * u / s + h)), Math.min(n, Math.floor(r + (s - a) * u / s + h)), i);
            }
            const s = t[2 * r + i];
            let a = o
              , l = n;
            for (I(e, t, o, r),
            t[2 * n + i] > s && I(e, t, o, n); a < l; ) {
                for (I(e, t, a, l),
                a++,
                l--; t[2 * a + i] < s; )
                    a++;
                for (; t[2 * l + i] > s; )
                    l--;
            }
            t[2 * o + i] === s ? I(e, t, o, l) : (l++,
            I(e, t, l, n)),
            l <= r && (o = l + 1),
            r <= l && (n = l - 1);
        }
    }
    function I(e, t, r, o) {
        _(e, r, o),
        _(t, 2 * r, 2 * o),
        _(t, 2 * r + 1, 2 * o + 1);
    }
    function _(e, t, r) {
        const o = e[t];
        e[t] = e[r],
        e[r] = o;
    }
    function L(e, t, r, o) {
        const n = e - r
          , i = t - o;
        return n * n + i * i
    }
    d.fromVectorTileJs = y,
    d.fromGeojsonVt = function(e, t) {
        t = t || {};
        var r = {};
        for (var o in e)
            r[o] = new f(e[o].features,t),
            r[o].name = o,
            r[o].version = t.version,
            r[o].extent = t.extent;
        return y({
            layers: r
        })
    }
    ,
    d.GeoJSONWrapper = m;
    const C = e=>e[0]
      , O = e=>e[1];
    class z {
        constructor(e, t=C, r=O, o=64, n=Float64Array) {
            this.nodeSize = o,
            this.points = e;
            const i = e.length < 65536 ? Uint16Array : Uint32Array
              , s = this.ids = new i(e.length)
              , a = this.coords = new n(2 * e.length);
            for (let o = 0; o < e.length; o++)
                s[o] = o,
                a[2 * o] = t(e[o]),
                a[2 * o + 1] = r(e[o]);
            T(s, a, o, 0, s.length - 1, 0);
        }
        range(e, t, r, o) {
            return function(e, t, r, o, n, i, s) {
                const a = [0, e.length - 1, 0]
                  , l = [];
                let u, h;
                for (; a.length; ) {
                    const c = a.pop()
                      , f = a.pop()
                      , p = a.pop();
                    if (f - p <= s) {
                        for (let s = p; s <= f; s++)
                            u = t[2 * s],
                            h = t[2 * s + 1],
                            u >= r && u <= n && h >= o && h <= i && l.push(e[s]);
                        continue
                    }
                    const g = Math.floor((p + f) / 2);
                    u = t[2 * g],
                    h = t[2 * g + 1],
                    u >= r && u <= n && h >= o && h <= i && l.push(e[g]);
                    const d = (c + 1) % 2;
                    (0 === c ? r <= u : o <= h) && (a.push(p),
                    a.push(g - 1),
                    a.push(d)),
                    (0 === c ? n >= u : i >= h) && (a.push(g + 1),
                    a.push(f),
                    a.push(d));
                }
                return l
            }(this.ids, this.coords, e, t, r, o, this.nodeSize)
        }
        within(e, t, r) {
            return function(e, t, r, o, n, i) {
                const s = [0, e.length - 1, 0]
                  , a = []
                  , l = n * n;
                for (; s.length; ) {
                    const u = s.pop()
                      , h = s.pop()
                      , c = s.pop();
                    if (h - c <= i) {
                        for (let n = c; n <= h; n++)
                            L(t[2 * n], t[2 * n + 1], r, o) <= l && a.push(e[n]);
                        continue
                    }
                    const f = Math.floor((c + h) / 2)
                      , p = t[2 * f]
                      , g = t[2 * f + 1];
                    L(p, g, r, o) <= l && a.push(e[f]);
                    const d = (u + 1) % 2;
                    (0 === u ? r - n <= p : o - n <= g) && (s.push(c),
                    s.push(f - 1),
                    s.push(d)),
                    (0 === u ? r + n >= p : o + n >= g) && (s.push(f + 1),
                    s.push(h),
                    s.push(d));
                }
                return a
            }(this.ids, this.coords, e, t, r, this.nodeSize)
        }
    }
    const E = {
        minZoom: 0,
        maxZoom: 16,
        minPoints: 2,
        radius: 40,
        extent: 512,
        nodeSize: 64,
        log: !1,
        generateId: !1,
        reduce: null,
        map: e=>e
    }
      , F = Math.fround || (N = new Float32Array(1),
    e=>(N[0] = +e,
    N[0]));
    var N;
    class j {
        constructor(e) {
            this.options = A(Object.create(E), e),
            this.trees = new Array(this.options.maxZoom + 1);
        }
        load(e) {
            const {log: t, minZoom: r, maxZoom: o, nodeSize: n} = this.options;
            t && console.time("total time");
            const i = `prepare ${e.length} points`;
            t && console.time(i),
            this.points = e;
            let s = [];
            for (let t = 0; t < e.length; t++)
                e[t].geometry && s.push(G(e[t], t));
            this.trees[o + 1] = new z(s,D,$,n,Float32Array),
            t && console.timeEnd(i);
            for (let e = o; e >= r; e--) {
                const r = +Date.now();
                s = this._cluster(s, e),
                this.trees[e] = new z(s,D,$,n,Float32Array),
                t && console.log("z%d: %d clusters in %dms", e, s.length, +Date.now() - r);
            }
            return t && console.timeEnd("total time"),
            this
        }
        getClusters(e, t) {
            let r = ((e[0] + 180) % 360 + 360) % 360 - 180;
            const o = Math.max(-90, Math.min(90, e[1]));
            let n = 180 === e[2] ? 180 : ((e[2] + 180) % 360 + 360) % 360 - 180;
            const i = Math.max(-90, Math.min(90, e[3]));
            if (e[2] - e[0] >= 360)
                r = -180,
                n = 180;
            else if (r > n) {
                const e = this.getClusters([r, o, 180, i], t)
                  , s = this.getClusters([-180, o, n, i], t);
                return e.concat(s)
            }
            const s = this.trees[this._limitZoom(t)]
              , a = s.range(W(r), X(i), W(n), X(o))
              , l = [];
            for (const e of a) {
                const t = s.points[e];
                l.push(t.numPoints ? J(t) : this.points[t.index]);
            }
            return l
        }
        getChildren(e) {
            const t = this._getOriginId(e)
              , r = this._getOriginZoom(e)
              , o = "No cluster with the specified id."
              , n = this.trees[r];
            if (!n)
                throw new Error(o);
            const i = n.points[t];
            if (!i)
                throw new Error(o);
            const s = this.options.radius / (this.options.extent * Math.pow(2, r - 1))
              , a = n.within(i.x, i.y, s)
              , l = [];
            for (const t of a) {
                const r = n.points[t];
                r.parentId === e && l.push(r.numPoints ? J(r) : this.points[r.index]);
            }
            if (0 === l.length)
                throw new Error(o);
            return l
        }
        getLeaves(e, t, r) {
            const o = [];
            return this._appendLeaves(o, e, t = t || 10, r = r || 0, 0),
            o
        }
        getTile(e, t, r) {
            const o = this.trees[this._limitZoom(e)]
              , n = Math.pow(2, e)
              , {extent: i, radius: s} = this.options
              , a = s / i
              , l = (r - a) / n
              , u = (r + 1 + a) / n
              , h = {
                features: []
            };
            return this._addTileFeatures(o.range((t - a) / n, l, (t + 1 + a) / n, u), o.points, t, r, n, h),
            0 === t && this._addTileFeatures(o.range(1 - a / n, l, 1, u), o.points, n, r, n, h),
            t === n - 1 && this._addTileFeatures(o.range(0, l, a / n, u), o.points, -1, r, n, h),
            h.features.length ? h : null
        }
        getClusterExpansionZoom(e) {
            let t = this._getOriginZoom(e) - 1;
            for (; t <= this.options.maxZoom; ) {
                const r = this.getChildren(e);
                if (t++,
                1 !== r.length)
                    break;
                e = r[0].properties.cluster_id;
            }
            return t
        }
        _appendLeaves(e, t, r, o, n) {
            const i = this.getChildren(t);
            for (const t of i) {
                const i = t.properties;
                if (i && i.cluster ? n + i.point_count <= o ? n += i.point_count : n = this._appendLeaves(e, i.cluster_id, r, o, n) : n < o ? n++ : e.push(t),
                e.length === r)
                    break
            }
            return n
        }
        _addTileFeatures(e, t, r, o, n, i) {
            for (const s of e) {
                const e = t[s]
                  , a = e.numPoints;
                let l, u, h;
                if (a)
                    l = Y(e),
                    u = e.x,
                    h = e.y;
                else {
                    const t = this.points[e.index];
                    l = t.properties,
                    u = W(t.geometry.coordinates[0]),
                    h = X(t.geometry.coordinates[1]);
                }
                const c = {
                    type: 1,
                    geometry: [[Math.round(this.options.extent * (u * n - r)), Math.round(this.options.extent * (h * n - o))]],
                    tags: l
                };
                let f;
                a ? f = e.id : this.options.generateId ? f = e.index : this.points[e.index].id && (f = this.points[e.index].id),
                void 0 !== f && (c.id = f),
                i.features.push(c);
            }
        }
        _limitZoom(e) {
            return Math.max(this.options.minZoom, Math.min(+e, this.options.maxZoom + 1))
        }
        _cluster(e, t) {
            const r = []
              , {radius: o, extent: n, reduce: i, minPoints: s} = this.options
              , a = o / (n * Math.pow(2, t));
            for (let o = 0; o < e.length; o++) {
                const n = e[o];
                if (n.zoom <= t)
                    continue;
                n.zoom = t;
                const l = this.trees[t + 1]
                  , u = l.within(n.x, n.y, a)
                  , h = n.numPoints || 1;
                let c = h;
                for (const e of u) {
                    const r = l.points[e];
                    r.zoom > t && (c += r.numPoints || 1);
                }
                if (c > h && c >= s) {
                    let e = n.x * h
                      , s = n.y * h
                      , a = i && h > 1 ? this._map(n, !0) : null;
                    const f = (o << 5) + (t + 1) + this.points.length;
                    for (const r of u) {
                        const o = l.points[r];
                        if (o.zoom <= t)
                            continue;
                        o.zoom = t;
                        const u = o.numPoints || 1;
                        e += o.x * u,
                        s += o.y * u,
                        o.parentId = f,
                        i && (a || (a = this._map(n, !0)),
                        i(a, this._map(o)));
                    }
                    n.parentId = f,
                    r.push(Z(e / c, s / c, f, c, a));
                } else if (r.push(n),
                c > 1)
                    for (const e of u) {
                        const o = l.points[e];
                        o.zoom <= t || (o.zoom = t,
                        r.push(o));
                    }
            }
            return r
        }
        _getOriginId(e) {
            return e - this.points.length >> 5
        }
        _getOriginZoom(e) {
            return (e - this.points.length) % 32
        }
        _map(e, t) {
            if (e.numPoints)
                return t ? A({}, e.properties) : e.properties;
            const r = this.points[e.index].properties
              , o = this.options.map(r);
            return t && o === r ? A({}, o) : o
        }
    }
    function Z(e, t, r, o, n) {
        return {
            x: F(e),
            y: F(t),
            zoom: 1 / 0,
            id: r,
            parentId: -1,
            numPoints: o,
            properties: n
        }
    }
    function G(e, t) {
        const [r,o] = e.geometry.coordinates;
        return {
            x: F(W(r)),
            y: F(X(o)),
            zoom: 1 / 0,
            index: t,
            parentId: -1
        }
    }
    function J(e) {
        return {
            type: "Feature",
            id: e.id,
            properties: Y(e),
            geometry: {
                type: "Point",
                coordinates: [(t = e.x,
                360 * (t - .5)), V(e.y)]
            }
        };
        var t;
    }
    function Y(e) {
        const t = e.numPoints
          , r = t >= 1e4 ? `${Math.round(t / 1e3)}k` : t >= 1e3 ? Math.round(t / 100) / 10 + "k" : t;
        return A(A({}, e.properties), {
            cluster: !0,
            cluster_id: e.id,
            point_count: t,
            point_count_abbreviated: r
        })
    }
    function W(e) {
        return e / 360 + .5
    }
    function X(e) {
        const t = Math.sin(e * Math.PI / 180)
          , r = .5 - .25 * Math.log((1 + t) / (1 - t)) / Math.PI;
        return r < 0 ? 0 : r > 1 ? 1 : r
    }
    function V(e) {
        const t = (180 - 360 * e) * Math.PI / 180;
        return 360 * Math.atan(Math.exp(t)) / Math.PI - 90
    }
    function A(e, t) {
        for (const r in t)
            e[r] = t[r];
        return e
    }
    function D(e) {
        return e.x
    }
    function $(e) {
        return e.y
    }
    function B(e, t, r, o) {
        for (var n, i = o, s = r - t >> 1, a = r - t, l = e[t], u = e[t + 1], h = e[r], c = e[r + 1], f = t + 3; f < r; f += 3) {
            var p = R(e[f], e[f + 1], l, u, h, c);
            if (p > i)
                n = f,
                i = p;
            else if (p === i) {
                var g = Math.abs(f - s);
                g < a && (n = f,
                a = g);
            }
        }
        i > o && (n - t > 3 && B(e, t, n, o),
        e[n + 2] = i,
        r - n > 3 && B(e, n, r, o));
    }
    function R(e, t, r, o, n, i) {
        var s = n - r
          , a = i - o;
        if (0 !== s || 0 !== a) {
            var l = ((e - r) * s + (t - o) * a) / (s * s + a * a);
            l > 1 ? (r = n,
            o = i) : l > 0 && (r += s * l,
            o += a * l);
        }
        return (s = e - r) * s + (a = t - o) * a
    }
    function q(e, t, r, o) {
        var n = {
            id: void 0 === e ? null : e,
            type: t,
            geometry: r,
            tags: o,
            minX: 1 / 0,
            minY: 1 / 0,
            maxX: -1 / 0,
            maxY: -1 / 0
        };
        return function(e) {
            var t = e.geometry
              , r = e.type;
            if ("Point" === r || "MultiPoint" === r || "LineString" === r)
                U(e, t);
            else if ("Polygon" === r || "MultiLineString" === r)
                for (var o = 0; o < t.length; o++)
                    U(e, t[o]);
            else if ("MultiPolygon" === r)
                for (o = 0; o < t.length; o++)
                    for (var n = 0; n < t[o].length; n++)
                        U(e, t[o][n]);
        }(n),
        n
    }
    function U(e, t) {
        for (var r = 0; r < t.length; r += 3)
            e.minX = Math.min(e.minX, t[r]),
            e.minY = Math.min(e.minY, t[r + 1]),
            e.maxX = Math.max(e.maxX, t[r]),
            e.maxY = Math.max(e.maxY, t[r + 1]);
    }
    function Q(e, t, r, o) {
        if (t.geometry) {
            var n = t.geometry.coordinates
              , i = t.geometry.type
              , s = Math.pow(r.tolerance / ((1 << r.maxZoom) * r.extent), 2)
              , a = []
              , l = t.id;
            if (r.promoteId ? l = t.properties[r.promoteId] : r.generateId && (l = o || 0),
            "Point" === i)
                H(n, a);
            else if ("MultiPoint" === i)
                for (var u = 0; u < n.length; u++)
                    H(n[u], a);
            else if ("LineString" === i)
                K(n, a, s, !1);
            else if ("MultiLineString" === i) {
                if (r.lineMetrics) {
                    for (u = 0; u < n.length; u++)
                        K(n[u], a = [], s, !1),
                        e.push(q(l, "LineString", a, t.properties));
                    return
                }
                ee(n, a, s, !1);
            } else if ("Polygon" === i)
                ee(n, a, s, !0);
            else {
                if ("MultiPolygon" !== i) {
                    if ("GeometryCollection" === i) {
                        for (u = 0; u < t.geometry.geometries.length; u++)
                            Q(e, {
                                id: l,
                                geometry: t.geometry.geometries[u],
                                properties: t.properties
                            }, r, o);
                        return
                    }
                    throw new Error("Input data is not a valid GeoJSON object.")
                }
                for (u = 0; u < n.length; u++) {
                    var h = [];
                    ee(n[u], h, s, !0),
                    a.push(h);
                }
            }
            e.push(q(l, i, a, t.properties));
        }
    }
    function H(e, t) {
        t.push(te(e[0])),
        t.push(re(e[1])),
        t.push(0);
    }
    function K(e, t, r, o) {
        for (var n, i, s = 0, a = 0; a < e.length; a++) {
            var l = te(e[a][0])
              , u = re(e[a][1]);
            t.push(l),
            t.push(u),
            t.push(0),
            a > 0 && (s += o ? (n * u - l * i) / 2 : Math.sqrt(Math.pow(l - n, 2) + Math.pow(u - i, 2))),
            n = l,
            i = u;
        }
        var h = t.length - 3;
        t[2] = 1,
        B(t, 0, h, r),
        t[h + 2] = 1,
        t.size = Math.abs(s),
        t.start = 0,
        t.end = t.size;
    }
    function ee(e, t, r, o) {
        for (var n = 0; n < e.length; n++) {
            var i = [];
            K(e[n], i, r, o),
            t.push(i);
        }
    }
    function te(t) {
        return e.mercatorXfromLng(t)
    }
    function re(t) {
        return e.mercatorYfromLat(t)
    }
    function oe(e, t, r, o, n, i, s, a) {
        if (o /= t,
        i >= (r /= t) && s < o)
            return e;
        if (s < r || i >= o)
            return null;
        for (var l = [], u = 0; u < e.length; u++) {
            var h = e[u]
              , c = h.geometry
              , f = h.type
              , p = 0 === n ? h.minX : h.minY
              , g = 0 === n ? h.maxX : h.maxY;
            if (p >= r && g < o)
                l.push(h);
            else if (!(g < r || p >= o)) {
                var d = [];
                if ("Point" === f || "MultiPoint" === f)
                    ne(c, d, r, o, n);
                else if ("LineString" === f)
                    ie(c, d, r, o, n, !1, a.lineMetrics);
                else if ("MultiLineString" === f)
                    ae(c, d, r, o, n, !1);
                else if ("Polygon" === f)
                    ae(c, d, r, o, n, !0);
                else if ("MultiPolygon" === f)
                    for (var m = 0; m < c.length; m++) {
                        var y = [];
                        ae(c[m], y, r, o, n, !0),
                        y.length && d.push(y);
                    }
                if (d.length) {
                    if (a.lineMetrics && "LineString" === f) {
                        for (m = 0; m < d.length; m++)
                            l.push(q(h.id, f, d[m], h.tags));
                        continue
                    }
                    "LineString" !== f && "MultiLineString" !== f || (1 === d.length ? (f = "LineString",
                    d = d[0]) : f = "MultiLineString"),
                    "Point" !== f && "MultiPoint" !== f || (f = 3 === d.length ? "Point" : "MultiPoint"),
                    l.push(q(h.id, f, d, h.tags));
                }
            }
        }
        return l.length ? l : null
    }
    function ne(e, t, r, o, n) {
        for (var i = 0; i < e.length; i += 3) {
            var s = e[i + n];
            s >= r && s <= o && (t.push(e[i]),
            t.push(e[i + 1]),
            t.push(e[i + 2]));
        }
    }
    function ie(e, t, r, o, n, i, s) {
        for (var a, l, u = se(e), h = 0 === n ? ue : he, c = e.start, f = 0; f < e.length - 3; f += 3) {
            var p = e[f]
              , g = e[f + 1]
              , d = e[f + 2]
              , m = e[f + 3]
              , y = e[f + 4]
              , v = 0 === n ? p : g
              , x = 0 === n ? m : y
              , w = !1;
            s && (a = Math.sqrt(Math.pow(p - m, 2) + Math.pow(g - y, 2))),
            v < r ? x > r && (l = h(u, p, g, m, y, r),
            s && (u.start = c + a * l)) : v > o ? x < o && (l = h(u, p, g, m, y, o),
            s && (u.start = c + a * l)) : le(u, p, g, d),
            x < r && v >= r && (l = h(u, p, g, m, y, r),
            w = !0),
            x > o && v <= o && (l = h(u, p, g, m, y, o),
            w = !0),
            !i && w && (s && (u.end = c + a * l),
            t.push(u),
            u = se(e)),
            s && (c += a);
        }
        var S = e.length - 3;
        p = e[S],
        g = e[S + 1],
        d = e[S + 2],
        (v = 0 === n ? p : g) >= r && v <= o && le(u, p, g, d),
        S = u.length - 3,
        i && S >= 3 && (u[S] !== u[0] || u[S + 1] !== u[1]) && le(u, u[0], u[1], u[2]),
        u.length && t.push(u);
    }
    function se(e) {
        var t = [];
        return t.size = e.size,
        t.start = e.start,
        t.end = e.end,
        t
    }
    function ae(e, t, r, o, n, i) {
        for (var s = 0; s < e.length; s++)
            ie(e[s], t, r, o, n, i, !1);
    }
    function le(e, t, r, o) {
        e.push(t),
        e.push(r),
        e.push(o);
    }
    function ue(e, t, r, o, n, i) {
        var s = (i - t) / (o - t);
        return e.push(i),
        e.push(r + (n - r) * s),
        e.push(1),
        s
    }
    function he(e, t, r, o, n, i) {
        var s = (i - r) / (n - r);
        return e.push(t + (o - t) * s),
        e.push(i),
        e.push(1),
        s
    }
    function ce(e, t) {
        for (var r = [], o = 0; o < e.length; o++) {
            var n, i = e[o], s = i.type;
            if ("Point" === s || "MultiPoint" === s || "LineString" === s)
                n = fe(i.geometry, t);
            else if ("MultiLineString" === s || "Polygon" === s) {
                n = [];
                for (var a = 0; a < i.geometry.length; a++)
                    n.push(fe(i.geometry[a], t));
            } else if ("MultiPolygon" === s)
                for (n = [],
                a = 0; a < i.geometry.length; a++) {
                    for (var l = [], u = 0; u < i.geometry[a].length; u++)
                        l.push(fe(i.geometry[a][u], t));
                    n.push(l);
                }
            r.push(q(i.id, s, n, i.tags));
        }
        return r
    }
    function fe(e, t) {
        var r = [];
        r.size = e.size,
        void 0 !== e.start && (r.start = e.start,
        r.end = e.end);
        for (var o = 0; o < e.length; o += 3)
            r.push(e[o] + t, e[o + 1], e[o + 2]);
        return r
    }
    function pe(e, t) {
        if (e.transformed)
            return e;
        var r, o, n, i = 1 << e.z, s = e.x, a = e.y;
        for (r = 0; r < e.features.length; r++) {
            var l = e.features[r]
              , u = l.geometry
              , h = l.type;
            if (l.geometry = [],
            1 === h)
                for (o = 0; o < u.length; o += 2)
                    l.geometry.push(ge(u[o], u[o + 1], t, i, s, a));
            else
                for (o = 0; o < u.length; o++) {
                    var c = [];
                    for (n = 0; n < u[o].length; n += 2)
                        c.push(ge(u[o][n], u[o][n + 1], t, i, s, a));
                    l.geometry.push(c);
                }
        }
        return e.transformed = !0,
        e
    }
    function ge(e, t, r, o, n, i) {
        return [Math.round(r * (e * o - n)), Math.round(r * (t * o - i))]
    }
    function de(e, t, r, o, n) {
        for (var i = t === n.maxZoom ? 0 : n.tolerance / ((1 << t) * n.extent), s = {
            features: [],
            numPoints: 0,
            numSimplified: 0,
            numFeatures: 0,
            source: null,
            x: r,
            y: o,
            z: t,
            transformed: !1,
            minX: 2,
            minY: 1,
            maxX: -1,
            maxY: 0
        }, a = 0; a < e.length; a++) {
            s.numFeatures++,
            me(s, e[a], i, n);
            var l = e[a].minX
              , u = e[a].minY
              , h = e[a].maxX
              , c = e[a].maxY;
            l < s.minX && (s.minX = l),
            u < s.minY && (s.minY = u),
            h > s.maxX && (s.maxX = h),
            c > s.maxY && (s.maxY = c);
        }
        return s
    }
    function me(e, t, r, o) {
        var n = t.geometry
          , i = t.type
          , s = [];
        if ("Point" === i || "MultiPoint" === i)
            for (var a = 0; a < n.length; a += 3)
                s.push(n[a]),
                s.push(n[a + 1]),
                e.numPoints++,
                e.numSimplified++;
        else if ("LineString" === i)
            ye(s, n, e, r, !1, !1);
        else if ("MultiLineString" === i || "Polygon" === i)
            for (a = 0; a < n.length; a++)
                ye(s, n[a], e, r, "Polygon" === i, 0 === a);
        else if ("MultiPolygon" === i)
            for (var l = 0; l < n.length; l++) {
                var u = n[l];
                for (a = 0; a < u.length; a++)
                    ye(s, u[a], e, r, !0, 0 === a);
            }
        if (s.length) {
            var h = t.tags || null;
            if ("LineString" === i && o.lineMetrics) {
                for (var c in h = {},
                t.tags)
                    h[c] = t.tags[c];
                h.sgmap_clip_start = n.start / n.size,
                h.sgmap_clip_end = n.end / n.size;
            }
            var f = {
                geometry: s,
                type: "Polygon" === i || "MultiPolygon" === i ? 3 : "LineString" === i || "MultiLineString" === i ? 2 : 1,
                tags: h
            };
            null !== t.id && (f.id = t.id),
            e.features.push(f);
        }
    }
    function ye(e, t, r, o, n, i) {
        var s = o * o;
        if (o > 0 && t.size < (n ? s : o))
            r.numPoints += t.length / 3;
        else {
            for (var a = [], l = 0; l < t.length; l += 3)
                (0 === o || t[l + 2] > s) && (r.numSimplified++,
                a.push(t[l]),
                a.push(t[l + 1])),
                r.numPoints++;
            n && function(e, t) {
                for (var r = 0, o = 0, n = e.length, i = n - 2; o < n; i = o,
                o += 2)
                    r += (e[o] - e[i]) * (e[o + 1] + e[i + 1]);
                if (r > 0 === t)
                    for (o = 0,
                    n = e.length; o < n / 2; o += 2) {
                        var s = e[o]
                          , a = e[o + 1];
                        e[o] = e[n - 2 - o],
                        e[o + 1] = e[n - 1 - o],
                        e[n - 2 - o] = s,
                        e[n - 1 - o] = a;
                    }
            }(a, i),
            e.push(a);
        }
    }
    function ve(t, r) {
        var o = (r = this.options = function(e, t) {
            for (var r in t)
                e[r] = t[r];
            return e
        }(Object.create(this.options), r)).debug;
        if (o && console.time("preprocess data"),
        r.maxZoom < 0 || r.maxZoom > 24)
            throw new Error("maxZoom should be in the 0-24 range");
        if (r.promoteId && r.generateId)
            throw new Error("promoteId and generateId cannot be used together.");
        var n = function(t, r) {
            var o = [];
            if (e.changeCrs(r.crs),
            "FeatureCollection" === t.type)
                for (var n = 0; n < t.features.length; n++)
                    Q(o, t.features[n], r, n);
            else
                Q(o, "Feature" === t.type ? t : {
                    geometry: t
                }, r);
            return o
        }(t, r);
        this.tiles = {},
        this.tileCoords = [],
        o && (console.timeEnd("preprocess data"),
        console.log("index: maxZoom: %d, maxPoints: %d", r.indexMaxZoom, r.indexMaxPoints),
        console.time("generate tiles"),
        this.stats = {},
        this.total = 0),
        (n = function(e, t) {
            var r = t.buffer / t.extent
              , o = e
              , n = oe(e, 1, -1 - r, r, 0, -1, 2, t)
              , i = oe(e, 1, 1 - r, 2 + r, 0, -1, 2, t);
            return (n || i) && (o = oe(e, 1, -r, 1 + r, 0, -1, 2, t) || [],
            n && (o = ce(n, 1).concat(o)),
            i && (o = o.concat(ce(i, -1)))),
            o
        }(n, r)).length && this.splitTile(n, 0, 0, 0),
        o && (n.length && console.log("features: %d, points: %d", this.tiles[0].numFeatures, this.tiles[0].numPoints),
        console.timeEnd("generate tiles"),
        console.log("tiles generated:", this.total, JSON.stringify(this.stats)));
    }
    function xe(e, t, r) {
        return 32 * ((1 << e) * r + t) + e
    }
    function we(e, t) {
        const r = e.tileID.canonical;
        if (!this._geoJSONIndex)
            return t(null, null);
        const o = this._geoJSONIndex.getTile(r.z, r.x, r.y);
        if (!o)
            return t(null, null);
        const n = new h(o.features);
        let i = d(n);
        0 === i.byteOffset && i.byteLength === i.buffer.byteLength || (i = new Uint8Array(i)),
        t(null, {
            vectorTile: n,
            rawData: i.buffer
        });
    }
    ve.prototype.options = {
        maxZoom: 14,
        indexMaxZoom: 5,
        indexMaxPoints: 1e5,
        tolerance: 3,
        extent: 4096,
        buffer: 64,
        lineMetrics: !1,
        promoteId: null,
        generateId: !1,
        debug: 0
    },
    ve.prototype.splitTile = function(e, t, r, o, n, i, s) {
        for (var a = [e, t, r, o], l = this.options, u = l.debug; a.length; ) {
            o = a.pop(),
            r = a.pop(),
            t = a.pop(),
            e = a.pop();
            var h = 1 << t
              , c = xe(t, r, o)
              , f = this.tiles[c];
            if (!f && (u > 1 && console.time("creation"),
            f = this.tiles[c] = de(e, t, r, o, l),
            this.tileCoords.push({
                z: t,
                x: r,
                y: o
            }),
            u)) {
                u > 1 && (console.log("tile z%d-%d-%d (features: %d, points: %d, simplified: %d)", t, r, o, f.numFeatures, f.numPoints, f.numSimplified),
                console.timeEnd("creation"));
                var p = "z" + t;
                this.stats[p] = (this.stats[p] || 0) + 1,
                this.total++;
            }
            if (f.source = e,
            n) {
                if (t === l.maxZoom || t === n)
                    continue;
                var g = 1 << n - t;
                if (r !== Math.floor(i / g) || o !== Math.floor(s / g))
                    continue
            } else if (t === l.indexMaxZoom || f.numPoints <= l.indexMaxPoints)
                continue;
            if (f.source = null,
            0 !== e.length) {
                u > 1 && console.time("clipping");
                var d, m, y, v, x, w, S = .5 * l.buffer / l.extent, M = .5 - S, P = .5 + S, b = 1 + S;
                d = m = y = v = null,
                x = oe(e, h, r - S, r + P, 0, f.minX, f.maxX, l),
                w = oe(e, h, r + M, r + b, 0, f.minX, f.maxX, l),
                e = null,
                x && (d = oe(x, h, o - S, o + P, 1, f.minY, f.maxY, l),
                m = oe(x, h, o + M, o + b, 1, f.minY, f.maxY, l),
                x = null),
                w && (y = oe(w, h, o - S, o + P, 1, f.minY, f.maxY, l),
                v = oe(w, h, o + M, o + b, 1, f.minY, f.maxY, l),
                w = null),
                u > 1 && console.timeEnd("clipping"),
                a.push(d || [], t + 1, 2 * r, 2 * o),
                a.push(m || [], t + 1, 2 * r, 2 * o + 1),
                a.push(y || [], t + 1, 2 * r + 1, 2 * o),
                a.push(v || [], t + 1, 2 * r + 1, 2 * o + 1);
            }
        }
    }
    ,
    ve.prototype.getTile = function(e, t, r) {
        var o = this.options
          , n = o.extent
          , i = o.debug;
        if (e < 0 || e > 24)
            return null;
        var s = 1 << e
          , a = xe(e, t = (t % s + s) % s, r);
        if (this.tiles[a])
            return pe(this.tiles[a], n);
        i > 1 && console.log("drilling down to z%d-%d-%d", e, t, r);
        for (var l, u = e, h = t, c = r; !l && u > 0; )
            u--,
            h = Math.floor(h / 2),
            c = Math.floor(c / 2),
            l = this.tiles[xe(u, h, c)];
        return l && l.source ? (i > 1 && console.log("found parent tile z%d-%d-%d", u, h, c),
        i > 1 && console.time("drilling down"),
        this.splitTile(l.source, u, h, c, e, t, r),
        i > 1 && console.timeEnd("drilling down"),
        this.tiles[a] ? pe(this.tiles[a], n) : null) : null
    }
    ;
    class Se extends e.VectorTileWorkerSource {
        constructor(e, t, r, o, n) {
            super(e, t, r, o, we),
            n && (this.loadGeoJSON = n);
        }
        loadData(t, r) {
            const o = t && t.request
              , n = o && o.collectResourceTiming;
            this.loadGeoJSON(t, ((s,a)=>{
                if (s || !a)
                    return r(s);
                if ("object" != typeof a)
                    return r(new Error(`Input data given to '${t.source}' is not a valid GeoJSON object.`));
                {
                    e.decodeFeatures(a),
                    i(a, !0);
                    try {
                        if (t.filter) {
                            const r = e.createExpression(t.filter, {
                                type: "boolean",
                                "property-type": "data-driven",
                                overridable: !1,
                                transition: !1
                            });
                            if ("error" === r.result)
                                throw new Error(r.value.map((e=>`${e.key}: ${e.message}`)).join(", "));
                            const o = a.features.filter((e=>r.value.evaluate({
                                zoom: 0
                            }, e)));
                            a = {
                                type: "FeatureCollection",
                                features: o
                            };
                        }
                        this._geoJSONIndex = t.cluster ? new j(function({superclusterOptions: t, clusterProperties: r}) {
                            if (!r || !t)
                                return t;
                            const o = {}
                              , n = {}
                              , i = {
                                accumulated: null,
                                zoom: 0
                            }
                              , s = {
                                properties: null
                            }
                              , a = Object.keys(r);
                            for (const t of a) {
                                const [i,s] = r[t]
                                  , a = e.createExpression(s)
                                  , l = e.createExpression("string" == typeof i ? [i, ["accumulated"], ["get", t]] : i);
                                o[t] = a.value,
                                n[t] = l.value;
                            }
                            return t.map = e=>{
                                s.properties = e;
                                const t = {};
                                for (const e of a)
                                    t[e] = o[e].evaluate(i, s);
                                return t
                            }
                            ,
                            t.reduce = (e,t)=>{
                                s.properties = t;
                                for (const t of a)
                                    i.accumulated = e[t],
                                    e[t] = n[t].evaluate(i, s);
                            }
                            ,
                            t
                        }(t)).load(a.features) : function(e, t) {
                            return new ve(e,t)
                        }(a, t.geojsonVtOptions);
                    } catch (s) {
                        return r(s)
                    }
                    this.loaded = {};
                    const l = {};
                    if (n) {
                        const r = e.getPerformanceMeasurement(o);
                        r && (l.resourceTiming = {},
                        l.resourceTiming[t.source] = JSON.parse(JSON.stringify(r)));
                    }
                    r(null, l);
                }
            }
            ));
        }
        reloadTile(e, t) {
            const r = this.loaded;
            return r && r[e.uid] ? super.reloadTile(e, t) : this.loadTile(e, t)
        }
        loadGeoJSON(t, r) {
            if (t.request)
                e.getJSON(t.request, r);
            else {
                if ("string" != typeof t.data)
                    return r(new Error(`Input data given to '${t.source}' is not a valid GeoJSON object.`));
                try {
                    return r(null, JSON.parse(t.data))
                } catch (e) {
                    return r(new Error(`Input data given to '${t.source}' is not a valid GeoJSON object.`))
                }
            }
        }
        getClusterExpansionZoom(e, t) {
            try {
                t(null, this._geoJSONIndex.getClusterExpansionZoom(e.clusterId));
            } catch (e) {
                t(e);
            }
        }
        getClusterChildren(e, t) {
            try {
                t(null, this._geoJSONIndex.getChildren(e.clusterId));
            } catch (e) {
                t(e);
            }
        }
        getClusterLeaves(e, t) {
            try {
                t(null, this._geoJSONIndex.getLeaves(e.clusterId, e.limit, e.offset));
            } catch (e) {
                t(e);
            }
        }
    }
    class Me {
        constructor(t) {
            this.self = t,
            this.actor = new e.Actor(t,this),
            this.layerIndexes = {},
            this.availableImages = {},
            this.isSpriteLoaded = {},
            this.projections = {},
            this.defaultProjection = e.getProjection({
                name: "mercator"
            }),
            this.workerSourceTypes = {
                vector: e.VectorTileWorkerSource,
                geojson: Se,
                geobuf: Se,
                flatgeobuf: Se
            },
            this.workerSources = {},
            this.demWorkerSources = {},
            this.self.registerWorkerSource = (e,t)=>{
                if (this.workerSourceTypes[e])
                    throw new Error(`Worker source with name "${e}" already registered.`);
                this.workerSourceTypes[e] = t;
            }
            ,
            this.self.registerRTLTextPlugin = t=>{
                if (e.plugin.isParsed())
                    throw new Error("RTL text plugin already registered.");
                e.plugin.applyArabicShaping = t.applyArabicShaping,
                e.plugin.processBidirectionalText = t.processBidirectionalText,
                e.plugin.processStyledBidirectionalText = t.processStyledBidirectionalText;
            }
            ;
        }
        clearCaches(e, t, r) {
            delete this.layerIndexes[e],
            delete this.availableImages[e],
            delete this.workerSources[e],
            delete this.demWorkerSources[e],
            r();
        }
        checkIfReady(e, t, r) {
            r();
        }
        setReferrer(e, t) {
            this.referrer = t;
        }
        spriteLoaded(t, r) {
            this.isSpriteLoaded[t] = r;
            for (const o in this.workerSources[t]) {
                const n = this.workerSources[t][o];
                for (const t in n)
                    n[t]instanceof e.VectorTileWorkerSource && (n[t].isSpriteLoaded = r,
                    n[t].fire(new e.Event("isSpriteLoaded")));
            }
        }
        setImages(e, t, r) {
            this.availableImages[e] = t;
            for (const r in this.workerSources[e]) {
                const o = this.workerSources[e][r];
                for (const e in o)
                    o[e].availableImages = t;
            }
            r();
        }
        enableTerrain(e, t, r) {
            this.terrain = t,
            r();
        }
        setProjection(t, r) {
            this.projections[t] = e.getProjection(r);
        }
        setLayers(e, t, r) {
            this.getLayerIndex(e).replace(t),
            r();
        }
        setXml(e, t, r) {
            this.getLayerIndex(e)._xml = t,
            r();
        }
        setLayersbuffer(t, r, o) {
            var n = e.BufferTostyle(new e.pbf(r))
              , i = this.getLayerIndex(t);
            i.replace(n.layers),
            i._xml = n.xml,
            o();
        }
        updateLayers(e, t, r) {
            this.getLayerIndex(e).update(t.layers, t.removedIds),
            r();
        }
        loadTile(t, r, o) {
            const n = this.enableTerrain ? e.extend({
                enableTerrain: this.terrain
            }, r) : r;
            n.projection = this.projections[t] || this.defaultProjection,
            this.getWorkerSource(t, r.type, r.source).loadTile(n, o);
        }
        loadDEMTile(t, r, o) {
            const n = this.enableTerrain ? e.extend({
                buildQuadTree: this.terrain
            }, r) : r;
            this.getDEMWorkerSource(t, r.source).loadTile(n, o);
        }
        reloadTile(t, r, o) {
            const n = this.enableTerrain ? e.extend({
                enableTerrain: this.terrain
            }, r) : r;
            n.projection = this.projections[t] || this.defaultProjection,
            this.getWorkerSource(t, r.type, r.source).reloadTile(n, o);
        }
        abortTile(e, t, r) {
            this.getWorkerSource(e, t.type, t.source).abortTile(t, r);
        }
        removeTile(e, t, r) {
            this.getWorkerSource(e, t.type, t.source).removeTile(t, r);
        }
        removeSource(e, t, r) {
            if (!this.workerSources[e] || !this.workerSources[e][t.type] || !this.workerSources[e][t.type][t.source])
                return;
            const o = this.workerSources[e][t.type][t.source];
            delete this.workerSources[e][t.type][t.source],
            void 0 !== o.removeSource ? o.removeSource(t, r) : r();
        }
        loadWorkerSource(e, t, r) {
            try {
                this.self.importScripts(t.url),
                r();
            } catch (e) {
                r(e.toString());
            }
        }
        syncRTLPluginState(t, r, o) {
            try {
                e.plugin.setState(r);
                const t = e.plugin.getPluginURL();
                if (e.plugin.isLoaded() && !e.plugin.isParsed() && null != t) {
                    this.self.importScripts(t);
                    const r = e.plugin.isParsed();
                    o(r ? void 0 : new Error(`RTL Text Plugin failed to import scripts from ${t}`), r);
                }
            } catch (e) {
                o(e.toString());
            }
        }
        getAvailableImages(e) {
            let t = this.availableImages[e];
            return t || (t = []),
            t
        }
        getLayerIndex(e) {
            let t = this.layerIndexes[e];
            return t || (t = this.layerIndexes[e] = new o),
            t
        }
        getWorkerSource(e, t, r) {
            return this.workerSources[e] || (this.workerSources[e] = {}),
            this.workerSources[e][t] || (this.workerSources[e][t] = {}),
            this.workerSources[e][t][r] || (this.workerSources[e][t][r] = new this.workerSourceTypes[t]({
                send: (t,r,o,n,i,s)=>{
                    this.actor.send(t, r, o, e, i, s);
                }
                ,
                scheduler: this.actor.scheduler
            },this.getLayerIndex(e),this.getAvailableImages(e),this.isSpriteLoaded[e])),
            this.workerSources[e][t][r]
        }
        getDEMWorkerSource(e, t) {
            return this.demWorkerSources[e] || (this.demWorkerSources[e] = {}),
            this.demWorkerSources[e][t] || (this.demWorkerSources[e][t] = new n),
            this.demWorkerSources[e][t]
        }
        enforceCacheSizeLimit(t, r) {
            e.enforceCacheSizeLimit(r);
        }
        getWorkerPerformanceMetrics(e, t, r) {
            r(void 0, void 0);
        }
    }
    return "undefined" != typeof WorkerGlobalScope && "undefined" != typeof self && self instanceof WorkerGlobalScope && (self.worker = new Me(self)),
    Me
}
)


/**
 * 解码SG矢量瓦片二进制数据，返回所有图层和要素的对象
 * @param {ArrayBuffer|Uint8Array} buffer - .sg接口返回的二进制数据
 * @param {Object} [tileID] - 可选，传递z/x/y等信息
 * @returns {Object} - { layerName: [feature, ...], ... }
 */
function decodeSGTile(buffer, tileID) {
    return '123';
    // 兼容ArrayBuffer/Uint8Array
    var bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
    // 构造PBF读取器
    var pbf = new op(bytes);
    // 解码为VectorTile对象
    var vt = new _y.VectorTile(pbf, null, tileID);
    var result = {};
    for (var layerName in vt.layers) {
        var layer = vt.layers[layerName];
        var features = [];
        for (var i = 0; i < layer.length; i++) {
            var feature = layer.feature(i);
            // 可选：转为GeoJSON或原始属性
            features.push({
                id: feature.id,
                properties: feature.properties,
                type: feature.type,
                geometry: feature.loadGeometry(),
                // geojson: feature.toGeoJSON && feature.toGeoJSON(0,0,0)
            });
        }
        result[layerName] = features;
    }
    return result;
}