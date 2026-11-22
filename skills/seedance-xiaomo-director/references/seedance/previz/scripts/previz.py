#!/usr/bin/env python3
"""草图预演渲染引擎（导演台版）：把一份三维场景 JSON 渲成 HTML 草图。

三维是唯一真相源——监视器画面是它的透视投影，俯视图是它的正交投影，导演视图是同一份数据换个角度看。
判据：只渲染镜头表里写死的东西——站位、姿态、构图、走位、运镜、时长、台词时点。
不渲染布光、表演、材质质感——草图给不出，给了会误导；人偶只有体量与朝向，一盏工作室灯只为分清体块与遮挡。

画面由浏览器里的 three.js 实时渲染（WebGL）：同目录放 three.min.js 则内嵌进 HTML、离线可开；
没有就写一个 cdnjs 的 <script> 标签，打开时需联网。站位图 plan 与场记平面图 stage 是 SVG 图解，不需要 three.js。

用法：python3 previz.py 场景.json -m play|grid|keyframes|plan|stage|cut [-o 输出.html] [--cols N]
"""
import json, sys, os, html, argparse, math

ENGINE_VERSION = "3.1"                          # 导演台三维白模；skill 的 [依赖检测] 用 --version 核对，低于 3 一律停

def esc(t):
    return html.escape(str(t), quote=True)

# ── 词表：schema 的唯一真相源 ────────────────────────────────────────────
SOLID_KINDS = {"wall","floor","counter","table","desk","chair","stool","bench","sofa","bed","shelf","cabinet",
               "window","door","curtain","slat","pillar","stairs","platform","screen","lamp","plant","tree",
               "car","rock","vat","animal","block","mirror","frame","rug","streetlamp","cabin",
               "cylinder","sphere","cone","dome","fog","water","statue"}   # 后七个是通用基元：词表没有的东西用它们拼
ALIASES = {"fridge":"cabinet","wardrobe":"cabinet","dresser":"cabinet","bookshelf":"shelf","rack":"shelf","nightstand":"table",
           "bar":"counter","railing":"slat","fence":"slat","column":"pillar","crate":"block","box":"block","tv":"screen",
           "monitor":"screen","blackboard":"screen","barrel":"vat","bin":"vat","pot":"vat","bus":"car","truck":"car","train":"car",
           "armchair":"sofa","couch":"sofa","step":"platform","stage":"platform","painting":"frame","photo":"frame","carpet":"rug",
           "mat":"rug","streetlight":"streetlamp","lamppost":"streetlamp","dog":"animal","cat":"animal","horse":"animal",
           "bush":"plant","flower":"plant","hill":"dome","dune":"dome","mound":"dome","ridge":"dome","rock2":"sphere",
           "ball":"sphere","pipe":"cylinder","drum":"cylinder","tent":"cone","smoke":"fog","dust":"fog","steam":"fog","mist":"fog",
           "cloud":"fog","rain":"fog","beam":"fog","pond":"water","pool":"water","river":"water","sea":"water","lake":"water",
           "colossus":"statue","sculpture":"statue","mannequin":"statue"}   # 常用叫法 → 预制件或基元，与浏览器端 ALIAS 同表
POSES = {"stand","sit","kneel","crouch","lie","prone"}
ARMS = {"down","forward","hold","up","cross","back","akimbo","point"}
FOCUS_SHAPES = {"disc","box","ball","stick"}
TONE_RAMP = {                                   # 只在 SVG 图解（plan / stage）里用：人物与焦点物的哑色
    "amber": ("#8a5f33", "#e5bb80"), "blue": ("#3d5670", "#87a9c6"),
    "green": ("#3f5a3c", "#93b08d"), "rose":  ("#6b4046", "#b78e94"),
    "gold":  ("#a8862a", "#f0da92"), "grey":  ("#3a3f49", "#949aa6"),
    "dark":  ("#2a2724", "#8a8580"), "white": ("#8f8d88", "#e8e6e1"),
}
THREE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
THREE_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "three.min.js")

_PT = {}                                        # id → 三维点：人取头部高度，物取物件位置；cam_at 与自检共用

def _pt(x):
    """坐标或 id → 三维点。id 认不出就返回 None，数据健康自检会报。"""
    if isinstance(x, (list, tuple)): return list(x)
    if isinstance(x, str): return _PT.get(x)
    return None

def load_scene(path):
    """判据：JSON 缺 meta/shots 任一即拒绝渲染，不猜、不补默认场景。"""
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    for k in ("meta", "shots"):
        if k not in s:
            sys.stderr.write("场景 JSON 缺少必需块：%s\n" % k); sys.exit(2)
    if not s["shots"]:
        sys.stderr.write("shots 为空，没有可渲染的镜\n"); sys.exit(2)
    s.setdefault("solids", []); s.setdefault("figures", []); s.setdefault("focus", [])
    _PT.clear()
    for f in s["figures"]:
        p = f.get("p")
        if isinstance(p, list) and len(p) == 3 and all(isinstance(v, (int, float)) for v in p) and isinstance(f.get("h"), (int, float)):
            _PT[f.get("id")] = [p[0], (f.get("stand", 0) if isinstance(f.get("stand", 0), (int, float)) else 0) + f["h"] * 0.85, p[2]]
    for f in s["focus"] + [x for x in s["solids"] if x.get("id")]:
        p = f.get("p")
        if isinstance(p, list) and len(p) == 3 and all(isinstance(v, (int, float)) for v in p):
            _PT[f.get("id")] = list(p)
    return s

def tone(name):
    return TONE_RAMP.get(name, TONE_RAMP["grey"])[1]

def parse_aspect(a):
    """判据：aspect 写成 W:H。9:16 出竖幅、16:9 出横幅——画幅错则构图判断全错，不设默认猜测。"""
    try:
        w, h = str(a).split(":"); w, h = float(w), float(h)
        if w <= 0 or h <= 0: raise ValueError
        return w, h
    except Exception:
        sys.stderr.write("meta.aspect 必须写成 W:H，如 9:16 或 16:9；当前值：%r\n" % (a,)); sys.exit(2)

def move_offsets(shot, k):
    """走位：镜内位移，只做移动不做表演。返回 {id: [dx,dy,dz]}。"""
    out = {}
    for mv in shot.get("moves", []) or []:
        try:
            a, b = mv["t"][0], mv["t"][1]
            u = min(1.0, max(0.0, (k - a) / max(1e-6, b - a)))
            u = u*u*2 if u < .5 else 1 - (-2*u+2)**2/2
            out[mv["who"]] = [mv["from"][i] + (mv["to"][i]-mv["from"][i])*u for i in range(3)]
        except Exception:
            pass
    return out

def _look(shot, k, key):
    """look / lookTo：坐标照用；写 id 时取那个人或物此刻的位置——主体一动，摄影机自己跟上。"""
    v = shot.get(key); p = _pt(v)
    if p is None: return None
    if isinstance(v, str):
        o = move_offsets(shot, k).get(v)
        if o: p = [p[i] + o[i] for i in range(3)]
    return p

def cam_at(shot, k):
    """摄影机由数据描述，三种形态：静止 / 两点插值 / 环绕。与浏览器端 camAt 同一套数学。"""
    e = k*k*2 if k < .5 else 1 - (-2*k+2)**2/2               # 缓入缓出——运镜起停都有加速度
    if shot.get("moveEase") == "linear": e = k
    elif shot.get("moveEase") == "out":  e = 1 - (1-k)**2
    lerp = lambda a, b: a + (b-a)*e
    l3 = lambda a, b: [lerp(a[i], b[i]) for i in range(3)]
    o = shot.get("orbit")
    if o:
        ang = math.radians(lerp(o["from"], o["to"]))
        return {"pos": [o["center"][0]+math.sin(ang)*o["r"], o.get("y", o["center"][1]),
                        o["center"][2]+math.cos(ang)*o["r"]],
                "look": _look(shot, k, "look") or o["center"], "fov": shot.get("fov", 40)}
    look, look_to = _look(shot, k, "look") or [50, 10, 50], _look(shot, k, "lookTo")
    return {"pos": l3(shot["cam"], shot["to"]) if shot.get("to") else shot["cam"],
            "look": l3(look, look_to) if look_to else look,
            "fov": lerp(shot.get("fov", 40), shot["fovTo"]) if shot.get("fovTo") else shot.get("fov", 40)}

def axis_side(p, q, pt, tol=2.0):
    """判据：点在轴线哪一侧，用叉积符号。同号 = 同侧 = 守轴；异号 = 越轴。
    离线不到 tol 个单位算骑在轴上——骑轴中性镜不算越轴。"""
    c = (q[0]-p[0])*(pt[2]-p[2]) - (q[2]-p[2])*(pt[0]-p[0])
    L = math.hypot(q[0]-p[0], q[2]-p[2]) or 1.0
    return 0 if abs(c)/L < tol else (1 if c > 0 else -1)

def axis_ends(scene):
    """轴线两端：figure / focus / 带 id 的 solid，或直接写坐标。认不出返回 (None, None)。"""
    ax = scene.get("axis")
    if not ax or len(ax) != 2: return None, None
    return _pt(ax[0]), _pt(ax[1])

def check_axis(scene):
    """越轴自检：所有机位应在轴线同侧。代码能算准的事不留给人眼。
    镜头表标了轴上镜 / 骑轴中性镜的写 onAxis: true，不参与投票、不报。"""
    p, q = axis_ends(scene)
    if not p or not q:
        return ("未声明轴线——单人场或无对视关系时属正常", [])
    sides, shots = [], scene["shots"]
    for sh in shots:
        if sh.get("onAxis") is True:
            sides.append(0); continue
        c = cam_at(sh, 0.5)                                   # 取中点：环绕镜整段都要在同侧
        sides.append(axis_side(p, q, c["pos"]))
    nz = [x for x in sides if x]
    if not nz: return ("机位均在轴上——轴上镜不算越轴", [])
    major = 1 if nz.count(1) >= nz.count(-1) else -1
    bad = [shots[i].get("n", i+1) for i, x in enumerate(sides) if x and x != major]
    return ("%d 镜全部在轴线同侧，守轴成立" % len(shots), []) if not bad \
           else ("镜 %s 在轴线另一侧" % "、".join(map(str, bad)), bad)

def check_cuts(scene):
    """接缝自检：相邻两镜在被摄者处张开的夹角。小于 30° 会被读成跳切。
    三条豁免——切入的是运动镜（运动打断读感）、景别跨两档以上（尺寸变化本身即区分）、
    或两镜看的不是同一个被摄者（换了主体就不是同一画面的跳）。"""
    out, shots = [], scene["shots"]
    for i in range(len(shots)-1):
        a, b = cam_at(shots[i], 1.0), cam_at(shots[i+1], 0.0)
        s = a["look"]
        va = math.degrees(math.atan2(a["pos"][2]-s[2], a["pos"][0]-s[0]))
        vb = math.degrees(math.atan2(b["pos"][2]-s[2], b["pos"][0]-s[0]))
        d = abs(((vb-va+180) % 360) - 180)
        moving = bool(shots[i+1].get("orbit") or shots[i+1].get("to") or shots[i+1].get("fovTo"))
        fa, fb = shots[i].get("fov", 40) or 40, shots[i+1].get("fov", 40) or 40
        resize = max(fa, fb) / max(1e-6, min(fa, fb)) >= 2.0   # 景别跨两档以上
        subject = math.dist(s, b["look"]) > 12                  # 换了被摄者
        out.append((shots[i].get("n", i+1), shots[i+1].get("n", i+2), round(d), moving or resize or subject))
    return out

def check_health(scene):
    """数据健康自检，两档。
    致命：会让引擎崩的写法——坐标位留着占位符或字符串。拦在渲染之前，好过甩一段 traceback。
    提醒：照样渲得出图，但那张图是错的、或另外两项自检在空转。「没报错」不等于「全绿」。
    返回 [(fatal, msg)]。"""
    w = []
    def nums(v, n):
        return isinstance(v, (list, tuple)) and len(v) == n and all(
            isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
    def isnum(v): return isinstance(v, (int, float)) and not isinstance(v, bool)
    ids = {f.get("id") for f in scene.get("figures", [])} | {f.get("id") for f in scene.get("focus", [])}
    mov_ids = ids | {s.get("id") for s in scene.get("solids", []) if s.get("id")}   # 可被朝向 / 视线 / 走位引用的一切
    for i, s in enumerate(scene.get("solids", [])):
        if s.get("kind") not in SOLID_KINDS and s.get("kind") not in ALIASES:
            w.append((0, "solids 第 %d 项的 kind「%s」不在词表内，按 block 画灰盒子——词表：%s；常用别名：%s"
                      % (i+1, s.get("kind"), " / ".join(sorted(SOLID_KINDS)), " / ".join(sorted(ALIASES)))))
        for k in ("p", "s"):
            if not nums(s.get(k), 3):
                w.append((1, "solids 第 %d 项的 %s 不是三个数字——占位符没填完，或写成了字符串" % (i+1, k)))
        if "rot" in s and not isnum(s["rot"]):
            w.append((1, "solids 第 %d 项的 rot 不是数字——它是绕竖轴的旋转角度" % (i+1)))
        if "opacity" in s and not (isnum(s["opacity"]) and 0 < s["opacity"] <= 1):
            w.append((1, "solids 第 %d 项的 opacity 要写 0 到 1 之间的数——雾、烟、纱、水汽这类半透明体量用它" % (i+1)))
        if "glow" in s and not (isinstance(s["glow"], bool) or isnum(s["glow"])):
            w.append((1, "solids 第 %d 项的 glow 写 true 或一个亮度数字——窗纸透光、灯、屏幕、发亮的边用它" % (i+1)))
        g = s.get("slats")
        if g is not None:
            if not isinstance(g, dict):
                w.append((1, "solids 第 %d 项的 slats 要写成 {step, gap}" % (i+1)))
            else:
                if "step" in g and not isnum(g["step"]):
                    w.append((1, "solids 第 %d 项的 slats.step 不是数字" % (i+1)))
                if g.get("gap") is not None and not nums(g["gap"], 2):
                    w.append((1, "solids 第 %d 项的 slats.gap 要写成窄口的两个 x 坐标 [起, 止]，"
                                 "不是一个数——它是开口的范围，不是缝宽" % (i+1)))
    blocks = [x for x in scene.get("solids", []) if (x.get("kind") or "block") == "block"]
    if blocks and len(blocks) >= max(2, len(scene.get("solids", [])) // 2):
        w.append((0, "%d 件陈设写成了 block（%s）：灰盒子读不出它是什么——先在词表里找预制件，找不到就用 sphere / cylinder / cone / dome / fog / water / statue 这些基元拼，"
                     "再配 tone、opacity（半透明）、glow（发光）。真是方的才写 block。"
                  % (len(blocks), "、".join(str(x.get("label") or "无标签") for x in blocks[:6]))))
    for f in list(scene.get("figures", [])) + list(scene.get("focus", [])):
        who = f.get("id", "?")
        if "id" not in f: w.append((0, "figures 或 focus 里有一项缺 id，被它引用的地方会静默失效"))
        if not nums(f.get("p"), 3):
            w.append((1, "%s 的 p 不是三个数字——占位符没填完，或把纵深写进了 y" % who))
        for k in ("h", "r", "stand", "seat"):
            if k in f and not isnum(f[k]):
                w.append((1, "%s 的 %s 不是数字" % (who, k)))
        if "h" not in f and "r" not in f: w.append((0, "%s 既没有 h 也没有 r，画不出体量" % who))
        if "pose" in f and f["pose"] not in POSES:
            w.append((0, "%s 的 pose「%s」不在词表内，按站姿画——词表：%s" % (who, f["pose"], " / ".join(sorted(POSES)))))
        for k in ("arms", "armL", "armR"):
            if k in f and f[k] not in ARMS:
                w.append((0, "%s 的 %s「%s」不在词表内，按垂臂画——词表：%s" % (who, k, f[k], " / ".join(sorted(ARMS)))))
        if "shape" in f and f["shape"] not in FOCUS_SHAPES:
            w.append((0, "%s 的 shape「%s」不在词表内，按圆盘画——词表：%s" % (who, f["shape"], " / ".join(sorted(FOCUS_SHAPES)))))
        if "s" in f and not nums(f["s"], 3):
            w.append((1, "%s 的 s 不是三个数字——焦点物的 s 是可选的 [宽, 高, 深]" % who))
        if "rot" in f and not isnum(f["rot"]):
            w.append((1, "%s 的 rot 不是数字" % who))
        for k in ("facing", "gaze"):
            v = f.get(k)
            if v is None: continue
            if isinstance(v, str) and v not in mov_ids:
                w.append((0, "%s 的 %s 指向不存在的 id「%s」：朝向或视线不画，且看不出错" % (who, k, v)))
            elif not isinstance(v, str) and not nums(v, 3):
                w.append((1, "%s 的 %s 要写另一个 id 或一个三维点 [x, y, z]" % (who, k)))
    ax = scene.get("axis")
    if len(scene.get("figures", [])) >= 2 and (not ax or len(ax) != 2):
        w.append((0, "两人以上却没声明 axis：越轴与接缝检查空转——对手戏必须声明轴线"))
    elif ax and any(_pt(x) is None for x in ax):
        w.append((0, "axis 指向不存在的 id 或不合法的点 %s：越轴检查空转——两端可写 figure / focus / 带 id 的 solid，或 [x, y, z]"
                  % [x for x in ax if _pt(x) is None]))
    for i, sh in enumerate(scene.get("shots", [])):
        n = sh.get("n", i+1)
        o = sh.get("orbit")
        if "onAxis" in sh and not isinstance(sh["onAxis"], bool):
            w.append((0, "镜 %s 的 onAxis 要写 true / false——镜头表标了轴上镜或骑轴中性镜才写 true" % n))
        for fid, ov in (sh.get("figures") or {}).items():
            if fid not in {f.get("id") for f in scene.get("figures", [])}:
                w.append((0, "镜 %s 的 figures 覆盖指向不存在的人「%s」：这一镜的姿态改写静默失效" % (n, fid)))
            if not isinstance(ov, dict):
                w.append((1, "镜 %s 的 figures.%s 要写成 {pose, arms, armL, armR, seat, facing, gaze} 里的若干项" % (n, fid))); continue
            if "pose" in ov and ov["pose"] not in POSES:
                w.append((0, "镜 %s 里 %s 的 pose「%s」不在词表内——词表：%s" % (n, fid, ov["pose"], " / ".join(sorted(POSES)))))
            for k in ("arms", "armL", "armR"):
                if k in ov and ov[k] not in ARMS:
                    w.append((0, "镜 %s 里 %s 的 %s「%s」不在词表内——词表：%s" % (n, fid, k, ov[k], " / ".join(sorted(ARMS)))))
            if "seat" in ov and not isnum(ov["seat"]):
                w.append((1, "镜 %s 里 %s 的 seat 不是数字" % (n, fid)))
            for k in ("facing", "gaze"):
                v = ov.get(k)
                if v is None: continue
                if isinstance(v, str) and v not in mov_ids:
                    w.append((0, "镜 %s 里 %s 的 %s 指向不存在的 id「%s」" % (n, fid, k, v)))
                elif not isinstance(v, str) and not nums(v, 3):
                    w.append((1, "镜 %s 里 %s 的 %s 要写另一个 id 或一个三维点 [x, y, z]" % (n, fid, k)))
        if not o and not sh.get("cam"):
            w.append((0, "镜 %s 既无 cam 也无 orbit：这一镜没有摄影机，画不出来" % n))
        if not o and sh.get("look") is None:
            w.append((0, "镜 %s 缺 look：摄影机不知道看哪儿" % n))
        for k in ("cam", "to"):
            if k in sh and not nums(sh[k], 3):
                w.append((1, "镜 %s 的 %s 不是三个数字——占位符没填完" % (n, k)))
        for k in ("look", "lookTo"):
            v = sh.get(k)
            if v is None: continue
            if isinstance(v, str):
                if v not in _PT: w.append((1, "镜 %s 的 %s 指向不存在的 id「%s」" % (n, k, v)))
            elif not nums(v, 3):
                w.append((1, "镜 %s 的 %s 要写三个数字，或一个 figure / focus 的 id" % (n, k)))
        if o:
            if not nums(o.get("center"), 3):
                w.append((1, "镜 %s 的 orbit.center 不是三个数字" % n))
            for k in ("r", "from", "to", "y"):
                if k in o and not isnum(o[k]):
                    w.append((1, "镜 %s 的 orbit.%s 不是数字" % (n, k)))
        for k in ("dur", "fovTo"):
            if k in sh and not isnum(sh[k]):
                w.append((1, "镜 %s 的 %s 不是数字——写成字符串会让时长与运镜算错" % (n, k)))
        if not isnum(sh.get("fov")):
            w.append((0, "镜 %s 缺 fov：视场角决定景别，按 40° 兜底但景别判断会失真" % n))
        for j, mv in enumerate(sh.get("moves", []) or []):
            if mv.get("who") not in mov_ids:
                w.append((0, "镜 %s 的 moves 第 %d 项 who「%s」不存在：这一步走位静默不动——可挪的是 figure / focus / 带 id 的 solid" % (n, j+1, mv.get("who"))))
            for k in ("from", "to"):
                if not nums(mv.get(k), 3):
                    w.append((1, "镜 %s 的 moves 第 %d 项 %s 不是三个数字" % (n, j+1, k)))
            if not nums(mv.get("t"), 2):
                w.append((1, "镜 %s 的 moves 第 %d 项 t 要写 [起, 止] 两个 0–1 的数" % (n, j+1)))
    return w

# ── SVG 图解：俯视是同一份场景的正交投影 ──────────────────────────────────
def _rect(x, y, w, h, fill, stroke, sw, rot=0, cx=0, cy=0):
    tr = ' transform="rotate(%.1f %.1f %.1f)"' % (-rot, cx, cy) if rot else ""
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" stroke-width="%s"%s/>' % (x, y, w, h, fill, stroke, sw, tr)

def render_plan(scene, cams=None, cur=-1, bad_idx=(), pure=False, W=240, H=300):
    """俯视：同一份场景的正交投影——不是另画一张，所以永远与画面一致。
    pure=True 出站位图成品：只画站位；机位、镜号、景别一概不画，那是工作视图的活。"""
    px = lambda v: 8 + v*(W-16)/100
    pz = lambda v: 8 + v*(H-16)/100
    P = ['<rect x="6" y="6" width="%d" height="%d" fill="none" stroke="#1e222a"/>' % (W-12, H-12)]
    for s in scene.get("solids", []):
        if s.get("kind") in ("wall", "floor"): continue
        P.append(_rect(px(s["p"][0]-s["s"][0]/2), pz(s["p"][2]-s["s"][2]/2), s["s"][0]*(W-16)/100,
                       max(2.4, s["s"][2]*(H-16)/100), "#1c1a14", "#2e2718", ".8", s.get("rot", 0), px(s["p"][0]), pz(s["p"][2])))
        if s.get("label"):
            P.append('<text x="%.1f" y="%.1f" fill="#4b5160" font-size="8.5">%s</text>'
                     % (px(s["p"][0]-s["s"][0]/2), pz(s["p"][2]-s["s"][2]/2)-6, esc(s["label"])))
    a, b = axis_ends(scene)
    if a and b:
        P.append('<line id="axline" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#e8e6e1" '
                 'stroke-dasharray="6 5" stroke-width="1.3" opacity=".34"/>'
                 % (px(a[0]), pz(a[2]), px(b[0]), pz(b[2])))
    for g in scene.get("figures", []):
        c = tone(g.get("tone", "grey"))
        if pure:
            t = _pt(g.get("gaze"))
            if t:                                              # 视线：细虚线指到看的对象
                P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" '
                         'stroke-dasharray="3 3" opacity=".5"/>' % (px(g["p"][0]), pz(g["p"][2]), px(t[0]), pz(t[2]), c))
            pth = g.get("path")
            if pth and len(pth) >= 2:                          # 走位：粗虚线带空心起点
                d = " ".join(("M" if i == 0 else "L") + "%.1f %.1f" % (px(q[0]), pz(q[1])) for i, q in enumerate(pth))
                P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="5 3" opacity=".8"/>' % (d, c))
                P.append('<circle cx="%.1f" cy="%.1f" r="4" fill="none" stroke="%s" stroke-width="1.6"/>' % (px(pth[0][0]), pz(pth[0][1]), c))
        t = _pt(g.get("facing"))
        if t:                                                  # 躯干朝向：与视线分开画
            ang = math.degrees(math.atan2(pz(t[2])-pz(g["p"][2]), px(t[0])-px(g["p"][0])))
            P.append('<g transform="translate(%.1f %.1f) rotate(%.1f)"><line x1="8.5" y1="0" x2="17.5" y2="0" '
                     'stroke="%s" stroke-width="2.6" stroke-linecap="round"/></g>' % (px(g["p"][0]), pz(g["p"][2]), ang, c))
        P.append('<circle cx="%.1f" cy="%.1f" r="8" fill="%s"/>' % (px(g["p"][0]), pz(g["p"][2]), c))
        if g.get("label"):
            P.append('<text x="%.1f" y="%.1f" fill="%s" font-size="9.5">%s</text>'
                     % (px(g["p"][0])+11, pz(g["p"][2])+3.5, c, esc(g["label"])))
    if pure:
        for f in scene.get("focus", []):
            c = tone(f.get("tone", "gold"))
            P.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s"/>' % (px(f["p"][0]), pz(f["p"][2]), c))
            if f.get("label"):
                P.append('<text x="%.1f" y="%.1f" fill="%s" font-size="9">%s</text>'
                         % (px(f["p"][0])+8, pz(f["p"][2])+3, c, esc(f["label"])))
        return "".join(P)
    for i, sh in enumerate(cams or scene["shots"]):            # 机位与轨迹：工作视图才画
        o, on = sh.get("orbit"), (i == cur)
        col = "#f0a238" if on else "#4c5566"
        if o:
            d = ""
            for j in range(25):
                a = math.radians(o["from"] + (o["to"]-o["from"])*j/24)
                d += ("M" if j == 0 else "L") + "%.1f %.1f" % (px(o["center"][0]+math.sin(a)*o["r"]),
                                                              pz(o["center"][2]+math.cos(a)*o["r"]))
            P.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3" '
                     'opacity="%s"/>' % (d, col, ".5" if on else ".22"))
        elif sh.get("to"):
            P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" '
                     'stroke-dasharray="4 3" opacity="%s"/>' % (px(sh["cam"][0]), pz(sh["cam"][2]),
                     px(sh["to"][0]), pz(sh["to"][2]), col, ".5" if on else ".22"))
        c = cam_at(sh, 0.0)
        ang = math.degrees(math.atan2(pz(c["look"][2])-pz(c["pos"][2]), px(c["look"][0])-px(c["pos"][0])))
        cc = "#c97b6b" if i in set(bad_idx) else col
        P.append('<g class="wedge%s" data-i="%d"><g transform="translate(%.1f %.1f) rotate(%.1f)">'
                 '<path d="M0 0 L28 -11 L28 11 Z" fill="%s" stroke="%s" stroke-width="1.3"/></g>'
                 '<circle cx="%.1f" cy="%.1f" r="7" fill="#12151a" stroke="%s" stroke-width="1.3"/>'
                 '<text x="%.1f" y="%.1f" text-anchor="middle" fill="%s" font-size="8">%s</text></g>'
                 % (" on" if on else "", i, px(c["pos"][0]), pz(c["pos"][2]), ang,
                    "rgba(240,162,56,.22)" if on else "#2a2f3a", cc,
                    px(c["pos"][0]), pz(c["pos"][2]), cc,
                    px(c["pos"][0]), pz(c["pos"][2])+3, cc, sh.get("n", i+1)))
    return "".join(P)

def render_stage(scene, shots):
    """场记平面图：垂直俯视，无遮挡、距离为真——覆盖冗余与覆盖空洞都看得出来。"""
    W, H = 1000, 1000
    px = lambda v: 60 + v*(W-120)/100
    pz = lambda v: 60 + v*(H-120)/100
    P = ['<rect width="%d" height="%d" fill="#0b0d11"/>' % (W, H)]
    for g in range(0, 101, 10):
        P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#14171d" stroke-width="1"/>' % (px(g), pz(0), px(g), pz(100)))
        P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#14171d" stroke-width="1"/>' % (px(0), pz(g), px(100), pz(g)))
    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#252a33" stroke-width="1.5"/>'
             % (px(0), pz(0), px(100)-px(0), pz(100)-pz(0)))
    P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#4a505c" stroke-width="2"/>'
             '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#4a505c" stroke-width="2"/>'
             '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#4a505c" stroke-width="2"/>'
             '<text x="%.1f" y="%.1f" fill="#5a606e" font-size="13">网格一格 = 全景宽的十分之一</text>'
             % (px(0), H-32, px(10), H-32, px(0), H-38, px(0), H-26, px(10), H-38, px(10), H-26, px(11), H-27))
    for so in scene.get("solids", []):
        if so.get("kind") in ("wall", "floor"): continue
        x0, z0 = so["p"][0]-so["s"][0]/2, so["p"][2]-so["s"][2]/2
        P.append(_rect(px(x0), pz(z0), so["s"][0]*(W-120)/100, max(4, so["s"][2]*(H-120)/100), "#1a1811", "#33301f", "1.4",
                       so.get("rot", 0), px(so["p"][0]), pz(so["p"][2])))
        if so.get("label"):
            P.append('<text x="%.1f" y="%.1f" fill="#5a6070" font-size="15">%s</text>' % (px(x0), pz(z0)-8, esc(so["label"])))
    for sh in shots:                                       # 覆盖扇形：张角就是这台机器的视场角
        c = cam_at(sh, 0.5); fov = sh.get("fov", 40) or 40
        d = math.hypot(c["look"][0]-c["pos"][0], c["look"][2]-c["pos"][2])
        base = math.degrees(math.atan2(c["look"][2]-c["pos"][2], c["look"][0]-c["pos"][0]))
        rr = max(d*1.18, 12) * (W-120)/100
        pts = ["%.1f,%.1f" % (px(c["pos"][0]), pz(c["pos"][2]))]
        for j in range(13):
            a2 = math.radians(base - fov/2 + fov*j/12)
            pts.append("%.1f,%.1f" % (px(c["pos"][0]) + math.cos(a2)*rr, pz(c["pos"][2]) + math.sin(a2)*rr))
        P.append('<polygon points="%s" fill="#f0a238" opacity=".055" stroke="#f0a238" stroke-width="1" stroke-opacity=".16"/>' % " ".join(pts))
    p, q_ = axis_ends(scene)
    if p and q_:
        dx, dz = q_[0]-p[0], q_[2]-p[2]
        L = math.hypot(dx, dz) or 1
        e0 = [p[0]-dx/L*26, p[2]-dz/L*26]; e1 = [q_[0]+dx/L*26, q_[2]+dz/L*26]
        P.append('<line id="axline" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#e8e6e1" '
                 'stroke-dasharray="12 9" stroke-width="2" opacity=".38"/>' % (px(e0[0]), pz(e0[1]), px(e1[0]), pz(e1[1])))
        tip = e0 if e0[1] > e1[1] else e1
        tx, tz = min(max(px(tip[0]), 90), W-96), pz(tip[1])
        P.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#e8e6e1" opacity=".5"/>' % (tx, tz))
        P.append('<rect x="%.1f" y="%.1f" width="150" height="24" rx="3" fill="#0b0d11" opacity=".9"/>'
                 '<text x="%.1f" y="%.1f" fill="#8a8f9c" font-size="13">180° 轴线 · 机位不得越过</text>' % (tx-75, tz+11, tx-64, tz+27))
    for g in scene.get("figures", []):
        c = tone(g.get("tone", "grey"))
        t = _pt(g.get("gaze"))
        if t:
            P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" stroke-dasharray="4 5" opacity=".5"/>'
                     % (px(g["p"][0]), pz(g["p"][2]), px(t[0]), pz(t[2]), c))
        t = _pt(g.get("facing"))
        if t:
            an = math.degrees(math.atan2(pz(t[2])-pz(g["p"][2]), px(t[0])-px(g["p"][0])))
            P.append('<g transform="translate(%.1f %.1f) rotate(%.1f)"><line x1="14" y1="0" x2="30" y2="0" stroke="%s" stroke-width="4" stroke-linecap="round"/></g>'
                     % (px(g["p"][0]), pz(g["p"][2]), an, c))
        P.append('<circle cx="%.1f" cy="%.1f" r="13" fill="%s"/>' % (px(g["p"][0]), pz(g["p"][2]), c))
        P.append('<text x="%.1f" y="%.1f" fill="%s" font-size="17">%s%s</text>'
                 % (px(g["p"][0])+19, pz(g["p"][2])+6, c, esc(g.get("label", "")),
                    " · " + {"sit": "坐", "kneel": "跪", "crouch": "蹲", "lie": "卧"}[g["pose"]] if g.get("pose") in ("sit", "kneel", "crouch", "lie") else ""))
    for f in scene.get("focus", []):
        c = tone(f.get("tone", "gold"))
        P.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s"/>' % (px(f["p"][0]), pz(f["p"][2]), c))
        P.append('<text x="%.1f" y="%.1f" fill="%s" font-size="14">%s</text>' % (px(f["p"][0])+12, pz(f["p"][2])+5, c, esc(f.get("label", ""))))
    for i, sh in enumerate(shots):
        o = sh.get("orbit"); col = "#f0a238"
        if o:
            d = ""
            for j in range(33):
                a2 = math.radians(o["from"] + (o["to"]-o["from"])*j/32)
                d += ("M" if j == 0 else "L") + "%.1f %.1f" % (px(o["center"][0]+math.sin(a2)*o["r"]), pz(o["center"][2]+math.cos(a2)*o["r"]))
            P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="7 5" opacity=".6"/>' % (d, col))
            ae = math.radians(o["to"]); ap_ = math.radians(o["to"] - (o["to"]-o["from"])*0.06)
            ex, ez = px(o["center"][0]+math.sin(ae)*o["r"]), pz(o["center"][2]+math.cos(ae)*o["r"])
            bx, bz = px(o["center"][0]+math.sin(ap_)*o["r"]), pz(o["center"][2]+math.cos(ap_)*o["r"])
            an = math.degrees(math.atan2(ez-bz, ex-bx))
            P.append('<g transform="translate(%.1f %.1f) rotate(%.1f)"><path d="M0 0 L-13 -6 L-13 6 Z" fill="%s" opacity=".75"/></g>' % (ex, ez, an, col))
        elif sh.get("to"):
            P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="7 5" opacity=".6"/>'
                     % (px(sh["cam"][0]), pz(sh["cam"][2]), px(sh["to"][0]), pz(sh["to"][2]), col))
        c = cam_at(sh, 0.0)
        P.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#8a8f9c" stroke-width="1.2" stroke-dasharray="3 4" opacity=".4"/>'
                 % (px(c["pos"][0]), pz(c["pos"][2]), px(c["look"][0]), pz(c["look"][2])))
        P.append('<circle cx="%.1f" cy="%.1f" r="15" fill="#12151a" stroke="%s" stroke-width="2"/>'
                 '<text x="%.1f" y="%.1f" text-anchor="middle" fill="%s" font-size="16">%s</text>'
                 % (px(c["pos"][0]), pz(c["pos"][2]), col, px(c["pos"][0]), pz(c["pos"][2])+6, col, sh.get("n", i+1)))
        P.append('<text x="%.1f" y="%.1f" fill="#6d7381" font-size="13">%s° · %s%s</text>'
                 % (px(c["pos"][0])+21, pz(c["pos"][2])-6, sh.get("fov", 40), esc(sh.get("framing", "")),
                    " · 轴上/骑轴" if sh.get("onAxis") is True else ""))
    return W, H, "".join(P)

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0b0c0f;--panel:#111318;--panel2:#171a20;--line:#1c1f26;--line2:#293039;
 --ink:#e8e6e1;--dim:#8a8f9c;--dim2:#5c626f;--acc:#f0a238;--warn:#c97b6b;--ok:#7d9a6f;
 --vp1:#3b3d43;--vp2:#232529;--r:6px;--s2:8px;--s3:12px;--s4:16px;--s5:24px;--max:1440px}
body{background:var(--bg);color:var(--ink);
 font:400 13px/1.55 Archivo,-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
 -webkit-font-smoothing:antialiased;padding:12px 14px 16px;display:flex;flex-direction:column;align-items:center;gap:10px}
body.play{height:100vh;overflow:hidden;display:grid;grid-template-rows:auto 1fr auto auto;align-items:stretch}
.w{width:100%;max-width:var(--max)}
body.play .w{max-width:none}
.cn{font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.mo{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}
/* 页眉 */
.hd{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding-bottom:10px;border-bottom:1px solid var(--line)}
.hd .mk{width:15px;height:15px;border:1.5px solid var(--acc);border-radius:2px;position:relative;flex:0 0 15px}
.hd .mk::after{content:"";position:absolute;inset:3px;background:var(--acc);border-radius:1px}
.hd h1{font-size:14px;font-weight:600;letter-spacing:.02em}
.hd .sep{width:1px;height:18px;background:var(--line2)}
.hd .mode{font-size:12.5px;color:var(--acc)}
.hd .id{font-size:11.5px;color:var(--dim2)}
.chips{display:flex;gap:7px}
.chip{font-size:10.5px;color:var(--dim);border:1px solid var(--line2);border-radius:99px;padding:3px 11px;
 font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.hd .tools{margin-left:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.segbtn{display:flex;border:1px solid var(--line2);border-radius:4px;overflow:hidden}
.segbtn button{border:0;border-radius:0;background:var(--panel);padding:5px 12px;font-size:12px;color:var(--dim)}
.segbtn button+button{border-left:1px solid var(--line2)}
.segbtn button.on{background:#2a2410;color:var(--acc)}
button{background:var(--panel2);border:1px solid var(--line2);color:#c8c6c1;border-radius:4px;padding:6px 14px;
 font-size:12px;cursor:pointer;font-family:inherit;transition:background .12s}
button:hover{background:#242935}
button:focus-visible{outline:1.5px solid var(--acc);outline-offset:1px}
.note{font-size:12px;color:var(--dim2);line-height:1.6}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px}
.card>h2{font-size:9.5px;color:var(--dim2);font-weight:600;letter-spacing:.16em;text-transform:uppercase;margin-bottom:10px}
/* play 三栏：左镜头列表与自检 · 中导演视图 · 右监视器与规格 */
.main{display:grid;grid-template-columns:262px 1fr 336px;gap:10px;min-height:0}
body.land .main{grid-template-columns:262px 1fr 520px}
.side{display:flex;flex-direction:column;gap:10px;min-height:0;overflow:auto}
.shot{display:grid;grid-template-columns:8px 24px 1fr;gap:8px;align-items:start;padding:8px 6px;border-radius:4px;cursor:pointer;border:1px solid transparent}
.shot:hover{background:var(--panel2)}
.shot.on{background:#181a20;border-color:#2c3038}
.shot .dot{width:8px;height:8px;border-radius:99px;background:#3a4150;margin-top:6px}
.shot.on .dot{background:var(--acc);box-shadow:0 0 8px var(--acc)}
.shot .no{font-size:13px;color:var(--dim2);font-family:"IBM Plex Mono",monospace;padding-top:2px}
.shot.on .no{color:var(--acc)}
.shot .t{font-size:12.5px;line-height:1.35;color:#d4d2cc}
.shot .m{font-size:10.5px;color:var(--dim2);margin-top:3px;display:flex;gap:8px;flex-wrap:wrap}
.axmsg{font-size:11.5px;padding:7px 10px;border-radius:4px;line-height:1.5;display:flex;gap:8px;align-items:flex-start;margin-top:6px}
.axmsg.ok{color:#94a68c;background:rgba(125,154,111,.07);border:1px solid rgba(125,154,111,.26)}
.axmsg.no{color:#e0b3a8;background:rgba(201,123,107,.1);border:1px solid rgba(201,123,107,.3)}
.legend{font-size:11px;color:var(--dim2);line-height:1.6}
.legend b{color:var(--dim);font-weight:600}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;vertical-align:-1px;margin-right:5px}
.stage{position:relative;min-width:0;min-height:0;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;
 background:radial-gradient(ellipse 80% 70% at 50% 40%,var(--vp1) 0%,var(--vp2) 100%)}
.vp{position:absolute;inset:0}
.vp canvas{display:block;width:100%;height:100%;cursor:grab}
.vp canvas:active{cursor:grabbing}
.labels{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.lb{position:absolute;transform:translate(-50%,-100%);white-space:nowrap;font-size:11px;line-height:1;padding:4px 7px;
 border-radius:3px;background:rgba(10,11,14,.72);border:1px solid rgba(255,255,255,.08);color:var(--ink);
 font-family:"PingFang SC","Hiragino Sans GB",sans-serif;backdrop-filter:blur(2px)}
.lb.cam{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.04em;transform:translate(-50%,-160%)}
.lb.cam.on{border-color:rgba(240,162,56,.6);color:var(--acc)}
.lb.solid{font-size:10px;color:#b9bcc4;opacity:.75;padding:3px 6px;background:rgba(10,11,14,.5)}
.lb.axis{font-size:10px;color:#d8d6d0;letter-spacing:.06em}
.lb.mon{font-size:12px;opacity:.85}
.hud{position:absolute;font-size:10.5px;color:#c4c7ce;text-shadow:0 1px 2px #000;pointer-events:none;font-family:"IBM Plex Mono",monospace;letter-spacing:.04em}
.hud.tl{top:11px;left:13px;display:flex;gap:10px;align-items:baseline}
.hud.tl .k{color:var(--acc);font-family:"PingFang SC",sans-serif;font-size:11.5px;letter-spacing:.08em}
.hud.br{bottom:10px;right:13px;color:#8b8f98;font-family:"PingFang SC",sans-serif;letter-spacing:.02em}
.hud.bl{bottom:10px;left:13px;color:#8b8f98}
.gizmo{position:absolute;right:12px;top:10px;width:58px;height:58px;pointer-events:none}
/* 监视器 */
.mon{position:relative;width:100%;background:#0d0e11;border-radius:3px;overflow:hidden;
 box-shadow:0 0 0 1px var(--line2),0 26px 60px -20px rgba(0,0,0,.9),0 0 90px -30px rgba(240,162,56,.1)}
.mon canvas{display:block;width:100%;height:100%}
.mon::before{content:"";position:absolute;top:0;left:9%;right:9%;height:1px;background:linear-gradient(90deg,transparent,#3d444f,transparent);z-index:3}
.tick{position:absolute;width:11px;height:11px;border:1.4px solid #4a515c;opacity:.85;z-index:3}
.tick.a{top:7px;left:7px;border-right:0;border-bottom:0}.tick.b{top:7px;right:7px;border-left:0;border-bottom:0}
.tick.c{bottom:7px;left:7px;border-right:0;border-top:0}.tick.d{bottom:7px;right:7px;border-left:0;border-top:0}
.tally{position:absolute;top:11px;right:15px;display:flex;align-items:center;gap:5px;z-index:3}
.tally i{width:5px;height:5px;border-radius:99px;background:var(--acc);box-shadow:0 0 7px var(--acc)}
.tally span{font-size:9px;color:var(--acc);letter-spacing:.1em;font-family:"IBM Plex Mono",monospace}
.vig{position:absolute;inset:0;pointer-events:none;z-index:2;background:radial-gradient(ellipse 75% 70% at 50% 45%,transparent 55%,rgba(0,0,0,.42) 100%)}
.monhud{position:absolute;left:11px;bottom:9px;z-index:3;display:flex;gap:8px;align-items:baseline;font-size:10px;color:#cfd2d8;text-shadow:0 1px 2px #000;letter-spacing:.04em}
.monhud .mo{color:var(--acc)}
#flick{position:absolute;inset:0;background:#000;opacity:0;pointer-events:none;transition:opacity .06s linear;z-index:4}
.beat{display:flex;align-items:flex-start;gap:9px}
.beat .k{font-size:9px;color:var(--acc);border:1px solid rgba(240,162,56,.34);border-radius:3px;padding:2px 6px;flex:0 0 auto;margin-top:1px;font-family:"IBM Plex Mono",monospace}
.beat .v{font-size:11.5px;color:#a8adb8;line-height:1.55}
.sn{display:flex;align-items:baseline;gap:9px}
.sn .no{font-size:22px;color:var(--acc);line-height:1;font-family:"IBM Plex Mono",monospace}
.sn .t{font-size:14px;font-weight:600;line-height:1.35}
dl.meta{display:flex;flex-direction:column}
dl.meta>div{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:8px 0;border-bottom:1px solid #16191f}
dl.meta dt{font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim2);flex:0 0 auto}
dl.meta dd{font-size:12.5px;color:#c8c6c1;text-align:right}
.blk .k{font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim2);margin-bottom:5px}
.blk .v{font-size:12px;color:#a8adb8;line-height:1.65;white-space:pre-line}
.lens .v{font-size:11.5px;color:#7a808d;line-height:1.7}
/* 时间轴 */
.strip{background:#0d0f13;border:1px solid var(--line);border-radius:var(--r);padding:10px 14px}
.lbl{font-size:9.5px;color:var(--dim2);letter-spacing:.16em;text-transform:uppercase}
.striphd{display:flex;align-items:baseline;gap:13px;margin-bottom:8px}
.clock{margin-left:auto;font-size:12px;color:var(--ink);font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.clock small{color:#4c5361;font-size:12px}
.segs{display:flex;gap:3px;height:36px}
.seg{position:relative;overflow:hidden;background:#12151b;border:1px solid #1e222a;border-radius:3px;cursor:pointer;display:flex;align-items:center;justify-content:center;
 font-size:11px;color:#6d7381;min-width:26px;font-family:"IBM Plex Mono",monospace;transition:border-color .12s,color .12s}
.seg:hover{border-color:var(--line2)}
.seg.on{color:var(--ink);border-color:#3a4150;background:#171b23}
.seg .fill{position:absolute;left:0;top:0;bottom:0;width:0;background:rgba(240,162,56,.2)}
.seg .ph{position:absolute;top:0;bottom:0;width:1.5px;background:var(--acc);box-shadow:0 0 8px var(--acc);display:none}
.seg.on .ph{display:block}
.seg span{position:relative}
.bar{display:flex;align-items:center;gap:12px;margin-top:10px;flex-wrap:wrap}
.tg{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--dim);cursor:pointer;user-select:none}
.tg input{accent-color:var(--acc)}
.bar .sp{flex:1}
/* grid 宫格 */
.gridwrap{display:flex;flex-direction:column;align-items:center;gap:var(--s4)}
.gimg{display:grid;gap:14px;width:100%;max-width:var(--gw)}
.gcell{position:relative;background:#000;aspect-ratio:var(--ar);overflow:hidden;border-radius:3px;box-shadow:0 0 0 1px #1e222a}
.gcell canvas{position:absolute;inset:0;width:100%;height:100%}
.gcell .no{position:absolute;top:6px;left:7px;font-size:10px;color:rgba(232,230,225,.55);font-family:"IBM Plex Mono",monospace;text-shadow:0 1px 3px #000;z-index:2}
.gitem{display:flex;flex-direction:column;gap:8px;min-width:0}
.gcap .t{font-size:12px;color:#c8c6c1;line-height:1.4}
.gcap .m{display:flex;justify-content:space-between;margin-top:3px;font-size:10.5px;color:var(--dim2)}
/* keyframes 关键帧条 */
.kfstrip{display:flex;align-items:stretch;overflow-x:auto;padding-bottom:var(--s2)}
.kf{flex:0 0 auto;width:var(--kw);display:flex;flex-direction:column;gap:var(--s2)}
.kf .im{position:relative;background:#000;aspect-ratio:var(--ar);border-radius:3px;overflow:hidden;box-shadow:0 0 0 1px #1e222a}
.kf .im canvas{position:absolute;inset:0;width:100%;height:100%}
.kf .t{font-size:11px;color:var(--acc);font-family:"IBM Plex Mono",monospace}
.kf .n{font-size:12.5px;font-weight:600}
.kf .d{font-size:11px;color:var(--dim2);line-height:1.5}
.gap{flex:1 1 40px;min-width:40px;display:flex;flex-direction:column;align-items:center;padding-top:calc(var(--kh) / 2)}
.gap .ln{width:100%;height:1px;background:var(--line2)}
.gap .v{font-size:10.5px;color:var(--dim2);margin-top:5px;font-family:"IBM Plex Mono",monospace;white-space:nowrap}
/* plan 站位图 · stage 场记平面图 */
.planwrap{display:flex;justify-content:center}
.planwrap .card{width:100%;max-width:560px}
.plan{width:100%;background:#0b0d11;border:1px solid var(--line);border-radius:4px;display:block}
.stagewrap{display:flex;justify-content:center}
.stagewrap .card{width:100%}
/* cut 接缝检查 */
.cutrow{display:grid;grid-template-columns:1fr 300px;gap:var(--s4);align-items:start;padding:var(--s4) 0;border-bottom:1px solid var(--line)}
.cutrow:last-child{border-bottom:0}
@media(max-width:900px){.cutrow{grid-template-columns:1fr}}
.cutpair{display:flex;gap:var(--s3);align-items:flex-start}
.cutf{flex:1;min-width:0;max-width:var(--cutw,440px)}
.cutf .im{position:relative;background:#000;border-radius:3px;overflow:hidden;box-shadow:0 0 0 1px var(--line2);aspect-ratio:var(--ar)}
.cutf .im canvas{position:absolute;inset:0;width:100%;height:100%}
.cutf .no{position:absolute;top:6px;left:7px;font-size:10px;color:rgba(232,230,225,.6);text-shadow:0 1px 3px #000}
.cutf .t{font-size:12.5px;font-weight:600;margin-top:9px}
.cutf .m{font-size:11px;color:var(--dim2);margin-top:2px}
.arr{flex:0 0 26px;display:flex;align-items:center;justify-content:center;align-self:center}
.cutchk{display:flex;flex-direction:column;gap:9px}
/* 下载条与页脚 */
.dl{display:flex;align-items:center;gap:var(--s2);flex-wrap:wrap;background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:var(--s3) var(--s4)}
.dl .t{font-size:9.5px;color:var(--dim2);letter-spacing:.16em;text-transform:uppercase;margin-right:4px}
.dl .h{font-size:11px;color:var(--dim2);margin-left:auto;line-height:1.5;max-width:560px}
.foot{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:9px 14px;font-size:11px;color:var(--dim2);line-height:1.7}
.foot b{color:#a8adb8;font-weight:600}
.foot .sep{color:var(--line2);margin:0 8px}
.needs-webgl:not(:empty){color:#e0b3a8;background:rgba(201,123,107,.1);border:1px solid rgba(201,123,107,.3);border-radius:4px;padding:8px 11px;font-size:12px;line-height:1.5}
@media(max-width:1180px){.main,body.land .main{grid-template-columns:1fr 300px}.side.l{display:none}}
@media(max-width:820px){.main,body.land .main{grid-template-columns:1fr}.side.r{display:none}}
@media(prefers-reduced-motion:reduce){#flick{transition:none}}
"""

SVG_EXPORT_JS = r"""
function exportSvg(sel,vbDefault,w,name,bg){ var n=document.querySelector(sel); if(!n) return; var vb=(n.getAttribute('viewBox')||vbDefault).split(/\s+/), vw=parseFloat(vb[2]), vh=parseFloat(vb[3]);
  var c=document.createElement('canvas'); c.width=w; c.height=Math.round(w*vh/vw); var x=c.getContext('2d'); x.fillStyle=bg||'#101319'; x.fillRect(0,0,c.width,c.height);
  var s='<svg xmlns="http://www.w3.org/2000/svg" width="'+c.width+'" height="'+c.height+'" viewBox="0 0 '+vw+' '+vh+'" preserveAspectRatio="xMidYMid meet"><style>text{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}</style>'+n.innerHTML+'</svg>';
  var im=new Image(); im.onload=function(){ x.drawImage(im,0,0,c.width,c.height); var a=document.createElement('a'); a.href=c.toDataURL('image/png'); a.download=name; document.body.appendChild(a); a.click(); a.remove() };
  im.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(s) }
"""

STAGE_JS = r"""// 导演台渲染层：三维场景 → 导演视图（自由环视）与监视器（本镜画面）。与 Python 侧同一套摄影机数学。
// 白模只表示体量、朝向、站位与遮挡；一盏工作室灯只为分清体块，不是布光。
var PV = (function(){
'use strict';
if(!window.THREE){ return null }
var SHOTS = SCENE.shots, META = SCENE.meta;
var V = function(a){ return new THREE.Vector3(a[0],a[1],a[2]) };
var clamp = function(x,a,b){ return Math.max(a,Math.min(b,x)) };
var TONE = {amber:0xd9a86c, blue:0x7f9fbf, green:0x8fae88, rose:0xb58a90, gold:0xe3c06a, grey:0x9ca2ad,
  wood:0x6e5236, slat:0x7a6446, shelf:0x5f4d35, window:0x6e5236, curtain:0x857b6a, wall:0x878a90, floor:0x3f4247,
  lamp:0xffc46a, stone:0x7f7a74, clay:0x7d6b5c, metal:0x9aa3ad, fabric:0x7d7466, leaf:0x6f8f5f, dark:0x3d3a36, white:0xd8d6d0,
  sand:0xb8a17e, asphalt:0x4a4d52, snow:0xe6e6e2, water:0x2a3a4a, brick:0x8a5a48};
var TONE_CSS = {amber:'#e5bb80', blue:'#87a9c6', green:'#93b08d', rose:'#b78e94', gold:'#f0da92', grey:'#949aa6', dark:'#8a8580', white:'#e8e6e1'};
var KIND_TONE = {counter:'wood', table:'wood', desk:'wood', chair:'wood', stool:'wood', bench:'wood', door:'wood', cabinet:'shelf',
  sofa:'fabric', bed:'fabric', pillar:'stone', stairs:'stone', platform:'floor', screen:'dark', plant:'leaf', tree:'leaf',
  car:'metal', rock:'stone', vat:'clay', animal:'dark', block:'wall', mirror:'metal', frame:'dark', rug:'fabric', streetlamp:'metal', cabin:'dark',
  fridge:'white', tv:'dark', bus:'metal', truck:'metal', train:'metal', cylinder:'stone', sphere:'stone', cone:'stone', dome:'stone', fog:'white', water:'water', statue:'stone'};
var ALIAS = {fridge:'cabinet', wardrobe:'cabinet', dresser:'cabinet', bookshelf:'shelf', rack:'shelf', nightstand:'table', bar:'counter',
  railing:'slat', fence:'slat', column:'pillar', crate:'block', box:'block', tv:'screen', monitor:'screen', blackboard:'screen',
  barrel:'vat', bin:'vat', pot:'vat', bus:'car', truck:'car', train:'car', armchair:'sofa', couch:'sofa', step:'platform', stage:'platform',
  painting:'frame', photo:'frame', carpet:'rug', mat:'rug', streetlight:'streetlamp', lamppost:'streetlamp', dog:'animal', cat:'animal',
  horse:'animal', bush:'plant', flower:'plant', hill:'dome', dune:'dome', mound:'dome', ridge:'dome', rock2:'sphere', ball:'sphere', pipe:'cylinder', drum:'cylinder',
  tent:'cone', smoke:'fog', dust:'fog', steam:'fog', mist:'fog', cloud:'fog', rain:'fog', beam:'fog', pond:'water', pool:'water', river:'water', sea:'water', lake:'water',
  colossus:'statue', sculpture:'statue', mannequin:'statue'};
var POSES = {stand:1, sit:1, kneel:1, crouch:1, lie:1, prone:1};
var ARMS = {down:{ax:0,el:0,az:.11}, forward:{ax:-1.41,el:0,az:.05}, hold:{ax:-.6,el:-1.25,az:.05}, up:{ax:-2.98,el:0,az:.15},
  cross:{ax:-1.05,el:-2.0,az:-.45}, back:{ax:.55,el:-.9,az:.2}, akimbo:{ax:0,el:0,az:.6,ez:-1.5}, point:{ax:-1.5,el:0,az:.05}};
var FOCUS_SHAPES = {disc:1, box:1, ball:1, stick:1};
var byid = {}, focusById = {}, solidById = {}, tg = {};
(SCENE.figures||[]).forEach(function(f){ byid[f.id]=f; tg[f.id]=f });
(SCENE.focus||[]).forEach(function(f){ focusById[f.id]=f; tg[f.id]=f });
(SCENE.solids||[]).forEach(function(s){ if(s.id){ solidById[s.id]=s; tg[s.id]=s } });
function pt(x){                                              // 坐标或 id → 三维点；id 指人取头部高度、指物取物件位置
  if(Array.isArray(x)) return x;
  if(typeof x==='string'){ var f=byid[x]; if(f) return [f.p[0], (f.stand||0)+(f.h||20)*.85, f.p[2]]; var o=focusById[x]||solidById[x]; if(o) return o.p }
  return null }

// ── 摄影机：静止 / 两点插值 / 环绕，三种都是数据 ────────────────────────
function ease(s,k){ var e = k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
  if(s.moveEase==='linear') e=k; else if(s.moveEase==='out') e=1-Math.pow(1-k,2); return e }
function moveOffsets(s,k){ var o={}; (s.moves||[]).forEach(function(mv){
  var u=clamp((k-mv.t[0])/Math.max(1e-6,mv.t[1]-mv.t[0]),0,1); u=u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2;
  o[mv.who]=[mv.from[0]+(mv.to[0]-mv.from[0])*u, mv.from[1]+(mv.to[1]-mv.from[1])*u, mv.from[2]+(mv.to[2]-mv.from[2])*u] }); return o }
function lookPt(s,k,key){                                    // look 写 id 时跟着走位走：主体一动，摄影机自己跟上
  var v=s[key], p=pt(v); if(!p) return null;
  if(typeof v==='string'){ var o=moveOffsets(s,k)[v]; if(o) p=[p[0]+o[0],p[1]+o[1],p[2]+o[2]] } return p }
function camAt(s,k){ var e=ease(s,k), L=function(a,b){return a+(b-a)*e}, L3=function(a,b){return [L(a[0],b[0]),L(a[1],b[1]),L(a[2],b[2])]};
  if(s.orbit){ var o=s.orbit, a=L(o.from,o.to)*Math.PI/180;
    return {pos:[o.center[0]+Math.sin(a)*o.r, (o.y!==undefined?o.y:o.center[1]), o.center[2]+Math.cos(a)*o.r], look:lookPt(s,k,'look')||o.center, fov:s.fov||40} }
  var look=lookPt(s,k,'look')||[50,10,50], lookTo=lookPt(s,k,'lookTo');
  return {pos:s.to?L3(s.cam,s.to):s.cam, look:lookTo?L3(look,lookTo):look, fov:s.fovTo?L(s.fov||40,s.fovTo):(s.fov||40)} }
function vfov(h){ return 2*Math.atan(Math.tan(h*Math.PI/360)*AH/AW)*180/Math.PI }

// ── 三维世界 ───────────────────────────────────────────────────────────
var scene = new THREE.Scene(), CTR = new THREE.Vector3(50,0,50), UP = new THREE.Vector3(0,1,0);
scene.add(new THREE.HemisphereLight(0xe6e9ef, 0x3a3431, .62));
var key = new THREE.DirectionalLight(0xfff1dd, .95); key.position.set(50+.55*170, .62*170, 50-.56*170); key.target.position.copy(CTR);
key.castShadow=true; key.shadow.mapSize.set(2048,2048); var sc=key.shadow.camera; sc.left=sc.bottom=-100; sc.right=sc.top=100; sc.near=10; sc.far=450;
sc.updateProjectionMatrix(); key.shadow.bias=-.0007; key.shadow.normalBias=.04; key.shadow.radius=2.5; scene.add(key, key.target);
var fill = new THREE.DirectionalLight(0xd2dbe8, .26); fill.position.set(-50,80,200); scene.add(fill);

function std(color,o){ return new THREE.MeshStandardMaterial(Object.assign({color:color, roughness:.9, metalness:0}, o||{})) }
var edgeMat = new THREE.LineBasicMaterial({color:0x101114, transparent:true, opacity:.32});
function boxMesh(w,h,d,m,edges){ var g=new THREE.BoxGeometry(w,h,d), mesh=new THREE.Mesh(g,m); mesh.castShadow=mesh.receiveShadow=true;
  if(edges) mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(g), edgeMat)); return mesh }
function cyl(rt,rb,h,m,seg){ var mesh=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,seg||18),m); mesh.castShadow=mesh.receiveShadow=true; return mesh }
function sph(r,m,w,h){ var mesh=new THREE.Mesh(new THREE.SphereGeometry(r,w||18,h||14),m); mesh.castShadow=mesh.receiveShadow=true; return mesh }
function at(mesh,x,y,z){ mesh.position.set(x,y,z); return mesh }
function setLayer(o,l){ o.traverse(function(x){ x.layers.set(l) }) }
function tube(a,b,r,m){ var d=new THREE.Vector3().subVectors(b,a), len=d.length(); if(len<1e-4) return new THREE.Group();
  var mesh=new THREE.Mesh(new THREE.CylinderGeometry(r,r,len,8),m); mesh.position.copy(a).addScaledVector(d,.5);
  mesh.quaternion.setFromUnitVectors(UP,d.normalize()); return mesh }
function cone(tip,dir,r,len,m){ var mesh=new THREE.Mesh(new THREE.ConeGeometry(r,len,14),m); mesh.position.copy(tip).addScaledVector(dir,-len/2);
  mesh.quaternion.setFromUnitVectors(UP,dir.clone().normalize()); return mesh }

// 地面与天空：地板接影子，网格给距离参照；天穹只给监视器看（第 2 层），室外镜的上半幅不再是一片黑
var floor = new THREE.Mesh(new THREE.PlaneGeometry(400,400), std(TONE.floor,{roughness:1})); floor.rotation.x=-Math.PI/2; floor.position.set(50,0,50); floor.receiveShadow=true; scene.add(floor);
var grid = new THREE.GridHelper(100,10,0x666a72,0x53575e); grid.position.set(50,.05,50); scene.add(grid);
var grid2 = new THREE.GridHelper(100,50,0x4b4f56,0x4b4f56); grid2.material.transparent=true; grid2.material.opacity=.5; grid2.position.set(50,.04,50); scene.add(grid2);
var edgeLine = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(100,100)), new THREE.LineBasicMaterial({color:0x7d8188}));
edgeLine.rotation.x=-Math.PI/2; edgeLine.position.set(50,.06,50); scene.add(edgeLine);
(function(){ var g=new THREE.SphereGeometry(600,24,16), pos=g.attributes.position, col=[], top=new THREE.Color(0x2a2e36), hor=new THREE.Color(0x717983);
  for(var i=0;i<pos.count;i++){ var t=clamp(pos.getY(i)/600,0,1), c=hor.clone().lerp(top,Math.pow(t,.6)); col.push(c.r,c.g,c.b) }
  g.setAttribute('color', new THREE.Float32BufferAttribute(col,3));
  var dome=new THREE.Mesh(g, new THREE.MeshBasicMaterial({vertexColors:true, side:THREE.BackSide})); dome.position.copy(CTR); dome.layers.set(2); scene.add(dome) })();

// 陈设：kind 词表 → 组合体。词表外的 kind 画灰盒子，数据健康自检会报
var walls = [], solidLabels = [], wallTop = 0;
function buildSolid(s){ var raw=s.kind||'block', kind=ALIAS[raw]||raw, sx=s.s[0], sy=s.s[1], sz=s.s[2], g=new THREE.Group(); g.position.set(s.p[0],s.p[1],s.p[2]);
  if(s.rot) g.rotation.y=-s.rot*Math.PI/180;
  var toneName = s.tone || KIND_TONE[raw] || KIND_TONE[kind] || (TONE[kind]!==undefined?kind:'wall'), col = TONE[toneName]!==undefined?TONE[toneName]:TONE.wall, m=std(col);
  var wood2=std(0x8a6a45), dark=std(0x3b2c1c);
  if(kind==='floor'){ if(s.tone&&TONE[s.tone]!==undefined) floor.material.color.setHex(TONE[s.tone]); return null }
  var glow=s.glow===true?1.2:(typeof s.glow==='number'?s.glow:(toneName==='lamp'?1.2:0));       // 发光：窗纸、屏幕、亮边
  var op=(typeof s.opacity==='number'&&s.opacity>0&&s.opacity<1)?s.opacity:(kind==='fog'?.45:0);   // 半透明：雾、烟、纱、雨幕、光柱
  if(glow>0||op){ m=new THREE.MeshStandardMaterial({color:col,roughness:op?1:.5,emissive:glow>0?col:0x000000,emissiveIntensity:glow,transparent:!!op,opacity:op||1,depthWrite:!op,side:op?THREE.DoubleSide:THREE.FrontSide}) }
  function prim(mesh){ mesh.castShadow=!op; mesh.receiveShadow=true; mesh.scale.set(sx,sy,sz); g.add(mesh); return finish() }
  if(kind==='cylinder') return prim(new THREE.Mesh(new THREE.CylinderGeometry(.5,.5,1,28),m));
  if(kind==='sphere') return prim(new THREE.Mesh(new THREE.SphereGeometry(.5,28,20),m));
  if(kind==='cone') return prim(new THREE.Mesh(new THREE.ConeGeometry(.5,1,28),m));
  if(kind==='dome'){ var dm=new THREE.Mesh(new THREE.SphereGeometry(1,28,18,0,Math.PI*2,0,Math.PI/2),m); dm.scale.set(sx/2,sy,sz/2); dm.position.y=-sy/2; dm.castShadow=!op; dm.receiveShadow=true; g.add(dm); return finish() }
  if(kind==='fog'){ var fmesh=Math.abs(sx-sz)<1.5?new THREE.Mesh(new THREE.CylinderGeometry(.5,.45,1,24,1,true),m):new THREE.Mesh(new THREE.BoxGeometry(1,1,1),m); fmesh.scale.set(sx,sy,sz); fmesh.castShadow=false; g.add(fmesh); return finish() }
  if(kind==='water'){ var wm2=new THREE.Mesh(new THREE.PlaneGeometry(sx,sz), new THREE.MeshStandardMaterial({color:col,metalness:.9,roughness:.08})); wm2.rotation.x=-Math.PI/2; wm2.position.y=sy/2; wm2.receiveShadow=true; g.add(wm2); return finish() }
  if(kind==='statue'){ var sb=buildBody(sy, std(col,{roughness:.95})); sb.body.position.y=-sy/2; g.add(sb.body); applyPose({f:{pose:s.pose,arms:s.arms,armL:s.armL,armR:s.armR}, h:sy, yaw:0, body:sb.body, upper:sb.upper, lL:sb.lL, lR:sb.lR, aL:sb.aL, aR:sb.aR}, 0); return finish() }
  if(kind==='mirror'){ var mf=std(TONE.wood), mt=1; [[0,sy/2-mt/2,sx,mt],[0,-sy/2+mt/2,sx,mt],[-sx/2+mt/2,0,mt,sy],[sx/2-mt/2,0,mt,sy]].forEach(function(r){ g.add(at(boxMesh(r[2],r[3],Math.max(sz,1),mf),r[0],r[1],0)) });
    g.add(at(new THREE.Mesh(new THREE.PlaneGeometry(sx-2*mt,sy-2*mt), new THREE.MeshStandardMaterial({color:0xdfe6ee,metalness:.92,roughness:.06})),0,0,Math.max(sz,1)/2)); return finish() }
  if(kind==='frame'){ g.add(boxMesh(sx,sy,Math.max(sz,.6),std(TONE.dark),true)); g.add(at(new THREE.Mesh(new THREE.PlaneGeometry(sx*.8,sy*.78), std(0xe4dfd3,{roughness:.7})),0,0,Math.max(sz,.6)/2+.03)); return finish() }
  if(kind==='rug'){ var rg=new THREE.Mesh(new THREE.PlaneGeometry(sx,sz), std(col,{roughness:1})); rg.rotation.x=-Math.PI/2; rg.position.y=.08; rg.receiveShadow=true; g.add(rg); return finish() }
  if(kind==='streetlamp'){ var pr=Math.max(.5,sx*.12); g.add(at(cyl(pr,pr*1.4,sy*.9,std(col,{metalness:.3}),10),0,-sy*.05,0)); g.add(at(cyl(pr*2.2,pr*1.2,sy*.08,std(col,{metalness:.3}),10),0,sy*.44,0));
    g.add(at(sph(Math.max(1,sx*.28),new THREE.MeshStandardMaterial({color:0xffe1a8,emissive:0xffc46a,emissiveIntensity:1.5}),12,10),0,sy*.4,0)); return finish() }
  if(kind==='cabin'){                                      // 车内：车头朝 +x，左舵在 +z 侧；车顶只给监视器看，导演视图从上面看得进去
    var dm=std(0x2f3338,{roughness:.8}), sm=std(0x4a4d55,{roughness:.9}); g.add(at(boxMesh(sx,.6,sz,dm),0,-sy/2+.3,0));
    g.add(at(boxMesh(sx*.2,sy*.34,sz,dm,true),sx*.4,-sy/2+sy*.17,0));
    [sz*.25,-sz*.25].forEach(function(z){ g.add(at(boxMesh(sx*.2,sy*.18,sz*.34,sm,true),sx*.08,-sy/2+sy*.13,z)); g.add(at(boxMesh(sx*.06,sy*.42,sz*.34,sm,true),-sx*.02,-sy/2+sy*.4,z)) });
    if(sx>14){ g.add(at(boxMesh(sx*.2,sy*.18,sz*.8,sm,true),-sx*.28,-sy/2+sy*.13,0)); g.add(at(boxMesh(sx*.06,sy*.42,sz*.8,sm,true),-sx*.38,-sy/2+sy*.4,0)) }
    var wh=new THREE.Mesh(new THREE.TorusGeometry(sy*.11,sy*.014,8,24),std(TONE.dark)); wh.position.set(sx*.26,-sy/2+sy*.36,sz*.25); wh.rotation.y=-Math.PI/2; wh.rotation.x=.4; g.add(wh);
    [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(function(c){ g.add(at(cyl(.35,.35,sy*.55,dm,8),c[0]*(sx/2-1),sy/2-sy*.28,c[1]*(sz/2-.3))) });
    [1,-1].forEach(function(c){ g.add(at(boxMesh(sx*.9,sy*.42,.5,dm,true),0,-sy/2+sy*.21,c*(sz/2-.25))) });
    var roof=boxMesh(sx*.95,.5,sz,dm); roof.position.y=sy/2; roof.castShadow=false; roof.layers.set(2); g.add(roof);
    var ws=new THREE.Mesh(new THREE.PlaneGeometry(sz,sy*.5),new THREE.MeshStandardMaterial({color:0xcfd8e2,transparent:true,opacity:.18,roughness:.1,side:THREE.DoubleSide})); ws.position.set(sx/2-.5,sy*.18,0); ws.rotation.y=Math.PI/2; ws.rotation.x=-.35; ws.layers.set(2); g.add(ws);
    return finish() }
  function finish(){ if(s.label && kind!=='wall'){ solidLabels.push({text:s.label, pos:new THREE.Vector3(s.p[0], s.p[1]+sy/2+1.2, s.p[2])}) } return g }
  if(kind==='wall'){ var wm=std(TONE.wall,{transparent:true}); var w=boxMesh(sx,sy,sz,wm,true); w.castShadow=false; g.add(w); wallTop=Math.max(wallTop, s.p[1]+sy/2);
    var n=new THREE.Vector3().subVectors(g.position,CTR); n.y=0; if(Math.abs(n.x)>Math.abs(n.z)) n.set(Math.sign(n.x)||1,0,0); else n.set(0,0,Math.sign(n.z)||-1);
    walls.push({mesh:w, mat:wm, n:n, low:sy<14}) }
  else if(kind==='counter'){ g.add(at(boxMesh(sx,sy-1.2,sz,m,true),0,-.6,0)); g.add(at(boxMesh(sx+1.6,1.2,sz+1.6,wood2,true),0,sy/2-.6,0));
    var kh=Math.min(2,sy*.15); g.add(at(boxMesh(sx-.4,kh,.3,dark),0,-sy/2+kh/2,sz/2+.16)) }
  else if(kind==='table'||kind==='desk'){ g.add(at(boxMesh(sx,1,sz,wood2,true),0,sy/2-.5,0));
    if(kind==='desk'){ [-1,1].forEach(function(c){ g.add(at(boxMesh(sx*.22,sy-1,sz*.9,m,true),c*(sx/2-sx*.11),-.5,0)) }) }
    else [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(function(c){ g.add(at(cyl(.55,.55,sy-1,m,10),c[0]*(sx/2-1.2),-.5,c[1]*(sz/2-1.2))) }) }
  else if(kind==='chair'){ var seatY=-sy/2+sy*.5; g.add(at(boxMesh(sx,.8,sz,wood2,true),0,seatY,0)); g.add(at(boxMesh(sx,sy*.5,.7,m,true),0,seatY+sy*.25+.4,-sz/2+.35));
    [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(function(c){ g.add(at(cyl(.4,.4,sy*.5,m,8),c[0]*(sx/2-.7),seatY-sy*.25-.4,c[1]*(sz/2-.7))) }) }
  else if(kind==='stool'){ g.add(at(cyl(sx/2,sx/2,.9,wood2,20),0,sy/2-.45,0)); for(var i3=0;i3<3;i3++){ var a3=i3*Math.PI*2/3; g.add(at(cyl(.4,.4,sy-.9,m,8),Math.cos(a3)*sx*.3,-.45,Math.sin(a3)*sx*.3)) } }
  else if(kind==='bench'){ g.add(at(boxMesh(sx,1,sz,wood2,true),0,sy/2-.5,0)); [-1,1].forEach(function(c){ g.add(at(boxMesh(1,sy-1,sz*.9,m),c*(sx/2-1.5),-.5,0)) }) }
  else if(kind==='sofa'){ g.add(at(boxMesh(sx,sy*.45,sz,m,true),0,-sy/2+sy*.225,0)); g.add(at(boxMesh(sx,sy,sz*.28,m,true),0,0,-sz/2+sz*.14));
    [-1,1].forEach(function(c){ g.add(at(boxMesh(sx*.1,sy*.72,sz,m,true),c*(sx/2-sx*.05),-sy/2+sy*.36,0)) }) }
  else if(kind==='bed'){ g.add(at(boxMesh(sx,sy*.5,sz,m,true),0,-sy/2+sy*.25,0)); g.add(at(boxMesh(sx-1,sy*.35,sz-1,std(TONE.white),true),0,sy*.17,0));
    g.add(at(boxMesh(sx*.36,sy*.18,sz*.16,std(TONE.white)),-sx*.22,sy*.44,-sz/2+sz*.14)); g.add(at(boxMesh(sx*.36,sy*.18,sz*.16,std(TONE.white)),sx*.22,sy*.44,-sz/2+sz*.14));
    g.add(at(boxMesh(sx,sy*1.3,.8,m,true),0,sy*.15,-sz/2-.4)) }
  else if(kind==='shelf'){ g.add(at(boxMesh(sx,sy,.6,m),0,0,-sz/2+.3)); [-1,1].forEach(function(c){ g.add(at(boxMesh(.6,sy,sz,m,true),c*(sx/2-.3),0,0)) });
    var n1=Math.max(2,Math.round(sy/4)); for(var i=0;i<=n1;i++) g.add(at(boxMesh(sx-1.2,.5,sz-.6,m),0,-sy/2+i*sy/n1,0));
    var n2=Math.max(2,Math.round(sx/4.5)); for(var j=1;j<n2;j++) g.add(at(boxMesh(.5,sy-.5,sz-.6,m),-sx/2+j*sx/n2,0,0)) }
  else if(kind==='cabinet'){ g.add(boxMesh(sx,sy,sz,m,true)); var nd=Math.max(1,Math.round(sx/9)); for(var d=0;d<nd;d++){ var dx=-sx/2+(d+.5)*sx/nd;
      g.add(at(boxMesh(sx/nd-1,sy-1.2,.3,std(col,{roughness:.7}),true),dx,0,sz/2+.15)); g.add(at(sph(.35,std(0xb9a074,{metalness:.5,roughness:.4}),8,6),dx+sx/nd*.32,0,sz/2+.5)) } }
  else if(kind==='window'){ var t=1.2, dz=Math.max(sz,1.2);
    [[0,sy/2-t/2,sx,t],[0,-sy/2+t/2,sx,t],[-sx/2+t/2,0,t,sy],[sx/2-t/2,0,t,sy]].forEach(function(r){ g.add(at(boxMesh(r[2],r[3],dz,m),r[0],r[1],0)) });
    g.add(boxMesh(.6,sy-2*t,dz*.8,m)); g.add(boxMesh(sx-2*t,.6,dz*.8,m));
    var pm=new THREE.MeshStandardMaterial({color:0xc4cdd8,emissive:s.tone==='lamp'?0xffb060:0xa9b8c8,emissiveIntensity:s.tone==='lamp'?.9:.55,roughness:.35,side:THREE.DoubleSide});
    g.add(new THREE.Mesh(new THREE.PlaneGeometry(sx-2*t,sy-2*t),pm)) }
  else if(kind==='door'){ g.add(boxMesh(sx,sy,sz,m,true)); g.add(at(boxMesh(sx*.68,sy*.78,sz*.5,std(0x5a4230)),0,0,sz/2)); g.add(at(sph(.5,std(0xb9a074,{metalness:.5,roughness:.4}),10,8),sx*.34,0,sz/2+.7)) }
  else if(kind==='curtain'){ var geo=new THREE.PlaneGeometry(sx,sy,36,1), pos=geo.attributes.position;
    for(var v=0;v<pos.count;v++) pos.setZ(v, Math.sin(pos.getX(v)/sx*Math.PI*7)*.9); geo.computeVertexNormals();
    var cm=new THREE.Mesh(geo, std(col,{side:THREE.DoubleSide,roughness:1})); cm.castShadow=cm.receiveShadow=true; g.add(cm);
    var rod=cyl(.35,.35,sx+2,dark,10); rod.rotation.z=Math.PI/2; rod.position.y=sy/2+.5; g.add(rod) }
  else if(kind==='slat'){ var step=(s.slats&&s.slats.step)||6, gap=s.slats&&s.slats.gap, slm=std(TONE.slat);
    for(var x2=-sx/2; x2<=sx/2+1e-6; x2+=step){ var wx=s.p[0]+x2, short=gap&&gap[0]<wx&&wx<gap[1], hh=sy*(short?.42:1); g.add(at(boxMesh(1.6,hh,1.6,slm),x2,sy/2-hh/2,0)) }
    g.add(at(boxMesh(sx+1.6,.8,1.9,slm),0,sy/2+.4,0)) }
  else if(kind==='pillar'){ g.add(cyl(Math.min(sx,sz)/2,Math.min(sx,sz)/2,sy,m,20)) }
  else if(kind==='stairs'){ var ns=Math.max(3,Math.round(sy/3)); for(var st=0;st<ns;st++){ var hs=sy*(st+1)/ns; g.add(at(boxMesh(sx,hs,sz/ns,m,true),0,-sy/2+hs/2,sz/2-(st+.5)*sz/ns)) } }
  else if(kind==='screen'){ g.add(boxMesh(sx,sy,sz,std(TONE.dark),true)); g.add(at(new THREE.Mesh(new THREE.PlaneGeometry(sx*.92,sy*.88),new THREE.MeshStandardMaterial({color:0xdfe6ee,emissive:0xbcc9d8,emissiveIntensity:.7,roughness:.3})),0,0,sz/2+.05)) }
  else if(kind==='lamp'){ g.add(at(cyl(sx*.42,sx*.5,sy*.28,std(0x4a3b28,{metalness:.3}),14),0,-sy*.36,0));
    g.add(at(cyl(sx*.3,sx*.36,sy*.6,new THREE.MeshStandardMaterial({color:0xffd58a,emissive:0xffb347,emissiveIntensity:1.6,roughness:.5}),14),0,sy*.08,0));
    g.add(at(cyl(sx*.15,sx*.34,sy*.18,std(0x4a3b28,{metalness:.3}),14),0,sy*.47,0)) }
  else if(kind==='plant'){ g.add(at(cyl(sx*.3,sx*.22,sy*.3,std(TONE.clay),14),0,-sy*.35,0)); g.add(at(sph(sx*.5,m,12,10),0,sy*.1,0)); g.add(at(sph(sx*.36,m,10,8),sx*.25,sy*.32,sx*.1)); g.add(at(sph(sx*.32,m,10,8),-sx*.28,sy*.28,-sx*.12)) }
  else if(kind==='tree'){ g.add(at(cyl(sx*.07,sx*.1,sy*.55,std(0x5a4632),10),0,-sy*.22,0)); g.add(at(sph(sx*.5,m,14,11),0,sy*.22,0)) }
  else if(kind==='car'){ var mm=std(col,{metalness:.4,roughness:.5}); g.add(at(boxMesh(sx,sy*.42,sz,mm,true),0,-sy*.1,0)); g.add(at(boxMesh(sx*.55,sy*.42,sz*.88,std(0x2d3239,{metalness:.2,roughness:.3}),true),-sx*.05,sy*.31,0));
    [[1,1],[1,-1],[-1,1],[-1,-1]].forEach(function(c){ var wh=cyl(sy*.2,sy*.2,1.4,std(TONE.dark),16); wh.rotation.x=Math.PI/2; g.add(at(wh,c[0]*sx*.32,-sy*.3,c[1]*sz/2)) }) }
  else if(kind==='rock'){ var rk=new THREE.Mesh(new THREE.DodecahedronGeometry(.5,0),m); rk.scale.set(sx,sy,sz); rk.castShadow=rk.receiveShadow=true; g.add(rk) }
  else if(kind==='vat'){ g.add(cyl(sx/2,sx*.38,sy,m,24)); g.add(at(new THREE.Mesh(new THREE.CircleGeometry(sx*.44,24),new THREE.MeshStandardMaterial({color:0x1d232b,metalness:.85,roughness:.12})),0,sy/2-sy*.12,0).rotateX(-Math.PI/2)); g.children[1].receiveShadow=true }
  else if(kind==='animal'){ var am=std(col,{roughness:.8}); g.add(at(boxMesh(sx*.6,sy*.45,sz*.8,am),0,sy*.05,0)); g.add(at(sph(sy*.28,am,12,9),sx*.42,sy*.28,0));
    [[.2,1],[.2,-1],[-.2,1],[-.2,-1]].forEach(function(c){ g.add(at(cyl(sy*.08,sy*.08,sy*.45,am,8),c[0]*sx,-sy*.27,c[1]*sz*.28)) });
    var tl=cyl(sy*.06,sy*.03,sx*.5,am,8); tl.rotation.z=Math.PI/2-.5; g.add(at(tl,-sx*.5,sy*.28,0)) }
  else { g.add(boxMesh(sx,sy,sz,m,true)) }
  return finish() }
var solidObjs = {};                                           // 带 id 的陈设：可被 look / axis 引用，也可被 moves 挪动（猫沿墙头走）
(SCENE.solids||[]).forEach(function(s){ var g=buildSolid(s); if(g){ scene.add(g); if(s.id) solidObjs[s.id]={f:s, root:g, base:[s.p[0],s.p[1],s.p[2]]} } });
// 天花板：三面以上高墙才算室内（meta.ceiling 可显式指定）；室外只有天穹
var tall=walls.filter(function(w){return !w.low}).length, interior=(META.ceiling!==undefined)?!!META.ceiling:tall>=3, ceiling=null;
if(interior){ ceiling=new THREE.Mesh(new THREE.PlaneGeometry(104,104), std(0x5e6169,{roughness:1})); ceiling.rotation.x=Math.PI/2; ceiling.position.set(50,wallTop||44,50); ceiling.layers.set(2); scene.add(ceiling) }

// 人偶：头、颈、躯干、骨盆、双臂（肩肘）、双腿（髋膝）、双脚。姿态 pose 与手臂 arms 是数据，表演不是
var figures = {};
function buildBody(h,m){                                    // 人偶身体：人物与雕像共用同一套关节
  var body=new THREE.Group(); body.rotation.order='YXZ';
  function cap(r,len){ var grp=new THREE.Group(); grp.add(cyl(r,r,len,m,14), at(sph(r,m,14,10),0,len/2,0), at(sph(r,m,14,10),0,-len/2,0)); return grp }
  var upper=new THREE.Group(); upper.position.y=h*.5; body.add(upper);           // 上身以髋为轴，可前倾
  var torso=cap(h*.1,h*.24); torso.position.y=h*.19; torso.scale.set(1.12,1,.66); upper.add(torso);
  var waist=cyl(h*.075,h*.085,h*.1,m,14); waist.position.y=h*.06; waist.scale.z=.7; upper.add(waist);
  var neck=cyl(h*.028,h*.03,h*.06,m,12); neck.position.y=h*.365; upper.add(neck);
  var headG=new THREE.Group(); headG.position.y=h*.38; upper.add(headG);
  var head=sph(h*.066,m,20,16); head.scale.set(.92,1.1,.96); head.position.y=h*.06; headG.add(head);
  var nose=new THREE.Mesh(new THREE.ConeGeometry(h*.012,h*.03,8),m); nose.rotation.x=Math.PI/2; nose.position.set(0,h*.055,h*.066*.96+h*.012); headG.add(nose);
  var pelvis=cap(h*.085,h*.05); pelvis.position.y=h*.5; pelvis.scale.set(1,1,.7); body.add(pelvis);
  function arm(side){ var sh=new THREE.Group(); sh.position.set(side*h*.125,h*.34,0); var up=cap(h*.026,h*.17); up.position.y=-h*.085; sh.add(up);
    var el=new THREE.Group(); el.position.y=-h*.17; sh.add(el); var fo=cap(h*.023,h*.16); fo.position.y=-h*.08; el.add(fo); el.add(at(sph(h*.028,m,10,8),0,-h*.17,0));
    upper.add(sh); return {sh:sh, el:el} }
  function leg(side){ var hip=new THREE.Group(); hip.position.set(side*h*.05,h*.5,0); var th=cap(h*.04,h*.23); th.position.y=-h*.115; hip.add(th);
    var kn=new THREE.Group(); kn.position.y=-h*.23; hip.add(kn); var sn=cap(h*.034,h*.21); sn.position.y=-h*.105; kn.add(sn);
    kn.add(at(boxMesh(h*.07,h*.03,h*.13,m),0,-h*.225,h*.03)); body.add(hip); return {hip:hip, kn:kn} }
  return {body:body, upper:upper, head:headG, aL:arm(-1), aR:arm(1), lL:leg(-1), lR:leg(1)} }
function buildFigure(f){ var h=f.h, col=TONE[f.tone]!==undefined?TONE[f.tone]:TONE.grey, m=std(col,{roughness:.78});
  var root=new THREE.Group(); root.position.set(f.p[0], f.stand||0, f.p[2]); var b=buildBody(h,m); root.add(b.body);
  if((f.stand||0)>0){ root.add(at(cyl(h*.14,h*.15,f.stand,std(0x4a4d53),24),0,-f.stand/2,0)) }
  var ring=new THREE.Mesh(new THREE.RingGeometry(h*.075,h*.09,40), new THREE.MeshBasicMaterial({color:col,transparent:true,opacity:.55,side:THREE.DoubleSide}));
  ring.rotation.x=-Math.PI/2; ring.position.y=-(f.stand||0)+.12; ring.layers.set(1); root.add(ring);
  scene.add(root);
  var fg={f:f, root:root, body:b.body, upper:b.upper, head:b.head, aL:b.aL, aR:b.aR, lL:b.lL, lR:b.lR, h:h, base:[f.p[0],f.stand||0,f.p[2]], phase:0, last:null, moving:0};
  applyPose(fg); return fg }
function armSpec(name){ return ARMS[name]||ARMS.down }
function applyPose(fg,sw,ov){ var h=fg.h, f=fg.f, s=sw||0; ov=ov||{};
  var pose=POSES[ov.pose]?ov.pose:(POSES[f.pose]?f.pose:'stand'); fg.pose=pose;
  var arms=ARMS[ov.arms]?ov.arms:(ARMS[f.arms]?f.arms:'down');
  var aL=ARMS[ov.armL]?ov.armL:(ARMS[f.armL]?f.armL:(arms==='point'?'down':arms)), aR=ARMS[ov.armR]?ov.armR:(ARMS[f.armR]?f.armR:arms);
  var seatV=(ov.seat!==undefined?ov.seat:f.seat), seat=(typeof seatV==='number')?seatV:h*.27;
  var b=fg.body, u=fg.upper, L=fg.lL, R=fg.lR, A=fg.aL, B=fg.aR;
  b.rotation.x=0; b.rotation.y=fg.yaw||0; b.position.y=0; u.rotation.x=0;
  L.hip.rotation.x=R.hip.rotation.x=L.kn.rotation.x=R.kn.rotation.x=0;
  if(pose==='sit'){ b.position.y=seat-h*.5; L.hip.rotation.x=R.hip.rotation.x=-Math.PI/2; var kn=seat<h*.18?.25:Math.PI/2; L.kn.rotation.x=R.kn.rotation.x=kn }
  else if(pose==='kneel'){ b.position.y=-(h*.5-h*.27); L.kn.rotation.x=R.kn.rotation.x=Math.PI/2 }
  else if(pose==='crouch'){ b.position.y=-(h*.5-h*.26); L.hip.rotation.x=R.hip.rotation.x=-Math.PI/2*.95; L.kn.rotation.x=R.kn.rotation.x=Math.PI/2*1.05; u.rotation.x=.55 }
  else if(pose==='lie'){ b.rotation.x=-Math.PI/2; b.rotation.y=(fg.yaw||0)+Math.PI; b.position.y=h*.09 }   // 仰卧：头朝 facing
  else if(pose==='prone'){ b.rotation.x=Math.PI/2; b.position.y=h*.09 }                                    // 俯卧：头朝 facing
  else { L.hip.rotation.x=s; R.hip.rotation.x=-s; L.kn.rotation.x=Math.max(0,s)*.6; R.kn.rotation.x=Math.max(0,-s)*.6 }
  function setArm(arm,side,name,swing){ var sp=armSpec(name), ax=sp.ax, el=sp.el;
    if(pose==='crouch'&&name==='down'){ ax=-.9; el=-.5 }
    arm.sh.rotation.set(ax+swing, 0, side*sp.az); arm.el.rotation.set(el, 0, sp.ez?side*sp.ez:0) }
  setArm(A,-1,aL,pose==='stand'?-s*.6:0); setArm(B,1,aR,pose==='stand'?s*.6:0) }
(SCENE.figures||[]).forEach(function(f){ figures[f.id]=buildFigure(f) });

// 焦点物：小物件画成有形的东西，不是一个大色块
var focusObjs = {};
(SCENE.focus||[]).forEach(function(f){ var r=f.r||1.5, col=TONE[f.tone]!==undefined?TONE[f.tone]:TONE.gold, m=std(col,{metalness:.65,roughness:.32}), shape=FOCUS_SHAPES[f.shape]?f.shape:'disc';
  var g=new THREE.Group(); g.position.set(f.p[0],f.p[1],f.p[2]); if(f.rot) g.rotation.y=-f.rot*Math.PI/180;
  var S=(Array.isArray(f.s)&&f.s.length===3)?f.s:null;
  if(shape==='box'){ var bs=S||[r*1.4,r*.25,r*2]; g.add(boxMesh(bs[0],bs[1],bs[2],std(col,{metalness:.2,roughness:.6}),true)) }
  else if(shape==='ball'){ g.add(sph(r,m,20,16)) }
  else if(shape==='stick'){ var ss=S||[r*2.6,r*.25,r*.35]; g.add(boxMesh(ss[0],ss[1],ss[2],m,true)) }
  else { g.add(cyl(r,r,r*.32,m,28)); var rim=new THREE.Mesh(new THREE.TorusGeometry(r*.97,r*.09,8,36),m); rim.rotation.x=Math.PI/2; rim.position.y=r*.16; rim.castShadow=true; g.add(rim);
    var crown=cyl(r*.14,r*.14,r*.24,m,10); crown.rotation.z=Math.PI/2; crown.position.set(r*1.05,0,0); g.add(crown);
    var face=new THREE.Mesh(new THREE.CircleGeometry(r*.8,28), std(0xf3ecd8,{roughness:.6})); face.rotation.x=-Math.PI/2; face.position.y=r*.165; g.add(face) }
  scene.add(g); focusObjs[f.id]={f:f, root:g, base:[f.p[0],f.p[1],f.p[2]]} });

// 机位：每镜一台机器；当前镜带取景锥，锥底就是画框、落在被摄者处；轨迹是实体管
var rigs=[], paths=[], pathGroup=new THREE.Group(), camGroup=new THREE.Group(); scene.add(pathGroup, camGroup);
var rigMatOff=std(0x6b7280,{roughness:.6}), rigMatOn=std(0xf0a238,{emissive:0xf0a238,emissiveIntensity:.35,roughness:.5}), rigMatBad=std(0xc97b6b,{emissive:0xc97b6b,emissiveIntensity:.3});
var pathMatOff=new THREE.MeshStandardMaterial({color:0x8d939c,roughness:.7,transparent:true,opacity:.55}), pathMatOn=std(0xf0a238,{emissive:0xf0a238,emissiveIntensity:.4});
function buildRig(){ var g=new THREE.Group(), m=rigMatOff, body=boxMesh(2.6,1.7,1.5,m), lens=cyl(.55,.7,1.6,m,16); lens.rotation.x=Math.PI/2; lens.position.z=1.5;
  var vf=at(boxMesh(.9,.6,.9,m),0,1.1,-.25), mag=cyl(.7,.7,.5,m,16); mag.rotation.x=Math.PI/2; mag.position.set(0,1.5,.2);
  g.add(body,lens,vf,mag); g.userData.parts=[body,lens,vf,mag]; setLayer(g,1); camGroup.add(g); return g }
function buildPath(s){ var pts=[], g=new THREE.Group();
  if(s.orbit){ var o=s.orbit; for(var j=0;j<=48;j++){ var a=(o.from+(o.to-o.from)*j/48)*Math.PI/180; pts.push(new THREE.Vector3(o.center[0]+Math.sin(a)*o.r,(o.y!==undefined?o.y:o.center[1]),o.center[2]+Math.cos(a)*o.r)) } }
  else if(s.to){ pts.push(V(s.cam),V(s.to)) }
  if(pts.length<2) return null;
  var curve=s.orbit?new THREE.CatmullRomCurve3(pts):new THREE.LineCurve3(pts[0],pts[1]);
  var t=new THREE.Mesh(new THREE.TubeGeometry(curve,s.orbit?72:2,.17,8,false),pathMatOff); g.add(t);
  var end=pts[pts.length-1], tan=new THREE.Vector3().subVectors(end,pts[pts.length-2]).normalize();
  g.add(cone(end.clone().addScaledVector(tan,1.2),tan,.7,2.2,pathMatOff)); g.userData.meshes=[t,g.children[1]];
  setLayer(g,1); pathGroup.add(g); return g }
SHOTS.forEach(function(s){ rigs.push(buildRig()); paths.push(buildPath(s)) });
var frGeo=new THREE.BufferGeometry(); frGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(16*3),3));
var frLines=new THREE.LineSegments(frGeo, new THREE.LineBasicMaterial({color:0xf0a238,transparent:true,opacity:.85})); frLines.layers.set(1); scene.add(frLines);
var frPlane=new THREE.Mesh(new THREE.PlaneGeometry(2,2), new THREE.MeshBasicMaterial({color:0xf0a238,transparent:true,opacity:.07,side:THREE.DoubleSide,depthWrite:false})); frPlane.layers.set(1); scene.add(frPlane);
frPlane.add(new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(2,2)), new THREE.LineBasicMaterial({color:0xf0a238,transparent:true,opacity:.9}))); frPlane.children[0].layers.set(1);
var lookDot=sph(.55, std(0xf0a238,{emissive:0xf0a238,emissiveIntensity:.8}),12,10); lookDot.castShadow=false; lookDot.layers.set(1); scene.add(lookDot);
var lookLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]), new THREE.LineDashedMaterial({color:0xf0a238,dashSize:1.4,gapSize:1,transparent:true,opacity:.5})); lookLine.layers.set(1); scene.add(lookLine);
var _f=new THREE.Vector3(), _r=new THREE.Vector3(), _u=new THREE.Vector3(), _p=new THREE.Vector3(), _l=new THREE.Vector3(), _tmp=new THREE.Vector3();
function updateFrustum(c){ _p.set(c.pos[0],c.pos[1],c.pos[2]); _l.set(c.look[0],c.look[1],c.look[2]); _f.subVectors(_l,_p); var d=_f.length(); _f.normalize();
  _r.crossVectors(_f,UP).normalize(); _u.crossVectors(_r,_f); var hw=d*Math.tan(c.fov*Math.PI/360), hh=hw*AH/AW;
  var cs=[[1,1],[1,-1],[-1,-1],[-1,1]].map(function(k){ return _l.clone().addScaledVector(_r,k[0]*hw).addScaledVector(_u,k[1]*hh) });
  var arr=frGeo.attributes.position.array, w=0; function put(v){ arr[w++]=v.x; arr[w++]=v.y; arr[w++]=v.z }
  for(var i=0;i<4;i++){ put(_p); put(cs[i]) } for(i=0;i<4;i++){ put(cs[i]); put(cs[(i+1)%4]) }
  frGeo.attributes.position.needsUpdate=true; frGeo.computeBoundingSphere();
  frPlane.position.copy(_l); frPlane.lookAt(_p); frPlane.scale.set(hw,hh,1); lookDot.position.copy(_l);
  lookLine.geometry.setFromPoints([_p.clone(),_l.clone()]); lookLine.computeLineDistances() }

// 轴线、视线、走位箭头：导演视图专属（第 1 层），监视器里永远看不见
var axisGroup=new THREE.Group(), axisLabelPos=null; scene.add(axisGroup);
(function(){ var ax=SCENE.axis; if(!ax||ax.length!==2) return; var p=pt(ax[0]), q=pt(ax[1]); if(!p||!q) return;
  var a=new THREE.Vector3(p[0],.25,p[2]), b=new THREE.Vector3(q[0],.25,q[2]), d=new THREE.Vector3().subVectors(b,a).normalize();
  var e0=a.clone().addScaledVector(d,-26), e1=b.clone().addScaledVector(d,26), len=e0.distanceTo(e1), n=Math.round(len/3.2), m=new THREE.MeshBasicMaterial({color:0xe8e6e1,transparent:true,opacity:.6});
  for(var i=0;i<n;i+=2){ axisGroup.add(tube(e0.clone().addScaledVector(d,len*i/n), e0.clone().addScaledVector(d,len*Math.min(n,i+1.1)/n),.16,m)) }
  axisLabelPos=(e0.z>e1.z?e0:e1).clone(); axisLabelPos.y=1.5; setLayer(axisGroup,1) })();
var gazeLines=[]; Object.keys(figures).forEach(function(id){ var fg=figures[id]; var col=TONE[fg.f.tone]!==undefined?TONE[fg.f.tone]:TONE.grey;
  var ln=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]), new THREE.LineDashedMaterial({color:col,dashSize:1.1,gapSize:.9,transparent:true,opacity:.7}));
  ln.layers.set(1); scene.add(ln); gazeLines.push({line:ln, fg:fg}) });
var arrowGroups=SHOTS.map(function(s){ var g=new THREE.Group(); (s.moves||[]).forEach(function(mv){ var who=figures[mv.who]||focusObjs[mv.who]; if(!who) return;
  var b=who.base, col=TONE[who.f.tone]!==undefined?TONE[who.f.tone]:TONE.grey, m=std(col,{emissive:col,emissiveIntensity:.25});
  var a0=new THREE.Vector3(b[0]+mv.from[0],.45,b[2]+mv.from[2]), a1=new THREE.Vector3(b[0]+mv.to[0],.45,b[2]+mv.to[2]), dir=new THREE.Vector3().subVectors(a1,a0);
  if(dir.length()<.5) return; dir.normalize(); g.add(tube(a0,a1.clone().addScaledVector(dir,-1.6),.14,m)); g.add(cone(a1,dir,.6,1.8,m)) });
  setLayer(g,1); g.visible=false; scene.add(g); return g });

// ── 状态：把一镜的第 k 帧摆出来（人、物、机位、取景锥），两台摄影机共用 ─────
var camMon=new THREE.PerspectiveCamera(vfov(40),AW/AH,.5,900); camMon.layers.enable(2);
function headPos(fg){ var p=fg.pose||fg.f.pose, y=(p==='lie'||p==='prone')?fg.h*.2:(p==='sit'||p==='kneel'||p==='crouch'?fg.h*.78:fg.h*1.02); return new THREE.Vector3(fg.root.position.x, fg.root.position.y+y, fg.root.position.z) }
function targetPos(x){ if(Array.isArray(x)) return new THREE.Vector3(x[0],x[1]===undefined?0:x[1],x[2]===undefined?x[1]:x[2]);
  var o=figures[x]||focusObjs[x]||solidObjs[x]; return o?(o.h!==undefined?headPos(o).sub(new THREE.Vector3(0,o.h*.12,0)):o.root.position.clone()):null }
function setState(i,k,dt){ var s=SHOTS[i], c=camAt(s,k), off=moveOffsets(s,k), OV=s.figures||{}; dt=dt||0;
  Object.keys(figures).forEach(function(id){ var fg=figures[id], o=off[id]||[0,0,0]; fg.root.position.set(fg.base[0]+o[0],fg.base[1]+o[1],fg.base[2]+o[2]) });
  Object.keys(focusObjs).forEach(function(id){ var fo=focusObjs[id], o=off[id]||[0,0,0]; fo.root.position.set(fo.base[0]+o[0],fo.base[1]+o[1],fo.base[2]+o[2]) });
  Object.keys(solidObjs).forEach(function(id){ var so=solidObjs[id], o=off[id]||[0,0,0]; so.root.position.set(so.base[0]+o[0],so.base[1]+o[1],so.base[2]+o[2]) });
  Object.keys(figures).forEach(function(id){ var fg=figures[id], f=fg.f, ov=OV[id]||{}, fc=ov.facing!==undefined?ov.facing:f.facing, gz=ov.gaze!==undefined?ov.gaze:f.gaze;
    var t=fc!==undefined?targetPos(fc):null, yaw=fg.yaw||0;
    if(t){ yaw=Math.atan2(t.x-fg.root.position.x, t.z-fg.root.position.z) } fg.yaw=yaw; fg.gazeT=gz;
    var g=gz!==undefined?targetPos(gz):null; if(g){ var gy=Math.atan2(g.x-fg.root.position.x,g.z-fg.root.position.z)-yaw; gy=Math.atan2(Math.sin(gy),Math.cos(gy));
      var hp=headPos(fg), dist=Math.hypot(g.x-hp.x,g.z-hp.z), pitch=Math.atan2(hp.y-g.y,Math.max(dist,1e-3));
      fg.head.rotation.y=clamp(gy,-1.2,1.2); fg.head.rotation.x=clamp(pitch,-.6,.9) } else { fg.head.rotation.y=0; fg.head.rotation.x=0 }
    var sp=0; if(dt>0&&fg.last){ sp=_tmp.subVectors(fg.root.position,fg.last).length()/Math.max(dt,1e-3) } fg.last=(fg.last||new THREE.Vector3()).copy(fg.root.position);
    if(dt>0){ var mv=sp>.8?1:0; fg.moving+=(mv-fg.moving)*Math.min(1,dt*8); if(mv) fg.phase+=dt*Math.min(sp,14)*.85 }
    else { var isMoving=(s.moves||[]).some(function(m){ return m.who===id&&k>m.t[0]&&k<m.t[1] }); fg.phase=isMoving?Math.PI/2:0; fg.moving=isMoving?1:0 }
    applyPose(fg, Math.sin(fg.phase)*.55*fg.moving, ov) });
  gazeLines.forEach(function(g){ var t=g.fg.gazeT!==undefined?targetPos(g.fg.gazeT):null; g.line.visible=!!t; if(!t) return; var pa=headPos(g.fg); pa.y-=1; g.line.geometry.setFromPoints([pa,t]); g.line.computeLineDistances() });
  rigs.forEach(function(r,j){ var cc=j===i?c:camAt(SHOTS[j],0); r.position.set(cc.pos[0],cc.pos[1],cc.pos[2]); r.lookAt(cc.look[0],cc.look[1],cc.look[2]) });
  updateFrustum(c);
  camMon.position.set(c.pos[0],c.pos[1],c.pos[2]); camMon.lookAt(c.look[0],c.look[1],c.look[2]); camMon.fov=vfov(c.fov); camMon.updateProjectionMatrix();
  return c }
function markActive(i, bad){ arrowGroups.forEach(function(g,j){ g.visible=(j===i) });
  rigs.forEach(function(r,j){ var m=j===i?rigMatOn:((bad||[]).indexOf(j)>=0?rigMatBad:rigMatOff); r.userData.parts.forEach(function(p){ p.material=m }) });
  paths.forEach(function(p,j){ if(p) p.userData.meshes.forEach(function(m){ m.material=j===i?pathMatOn:pathMatOff }) }) }
function wallsSolid(){ walls.forEach(function(w){ w.mat.opacity=1; w.mat.depthWrite=true }) }
function wallsCut(cam,on){ walls.forEach(function(w){ var outside=on&&_tmp.subVectors(cam.position,w.mesh.getWorldPosition(new THREE.Vector3())).dot(w.n)>0; w.mat.opacity=outside?.16:1; w.mat.depthWrite=!outside }) }

// ── 渲染器 ───────────────────────────────────────────────────────────────
function mkRenderer(canvas,alpha){ var r=new THREE.WebGLRenderer({canvas:canvas,antialias:true,alpha:alpha,preserveDrawingBuffer:true});
  r.setPixelRatio(1); r.shadowMap.enabled=true; r.shadowMap.type=THREE.PCFSoftShadowMap; r.outputEncoding=THREE.sRGBEncoding; r.toneMapping=THREE.ACESFilmicToneMapping; r.toneMappingExposure=1.05; return r }
var off=null;
function drawLabels(ctx,cam,W,H){ var v=new THREE.Vector3(), fs=Math.max(11,Math.round(H/36)); ctx.font='500 '+fs+'px "PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif'; ctx.textAlign='center'; ctx.textBaseline='bottom'; ctx.lineJoin='round';
  var items=[]; Object.keys(figures).forEach(function(id){ var fg=figures[id]; if(fg.f.label) items.push({t:fg.f.label,p:headPos(fg).add(new THREE.Vector3(0,1.2,0)),c:TONE_CSS[fg.f.tone]||TONE_CSS.grey}) });
  Object.keys(focusObjs).forEach(function(id){ var fo=focusObjs[id]; if(fo.f.label) items.push({t:fo.f.label,p:fo.root.position.clone().add(new THREE.Vector3(0,(fo.f.r||1.5)*1.6+.6,0)),c:TONE_CSS[fo.f.tone]||TONE_CSS.gold}) });
  items.forEach(function(it){ v.copy(it.p).project(cam); if(v.z>=1||Math.abs(v.x)>1||Math.abs(v.y)>1) return; var x=(v.x+1)/2*W, y=(1-v.y)/2*H;
    ctx.lineWidth=fs*.3; ctx.strokeStyle='rgba(0,0,0,.72)'; ctx.strokeText(it.t,x,y); ctx.fillStyle=it.c; ctx.globalAlpha=.9; ctx.fillText(it.t,x,y); ctx.globalAlpha=1 }) }
function drawVignette(ctx,W,H){ var g=ctx.createRadialGradient(W/2,H*.45,Math.min(W,H)*.45,W/2,H*.45,Math.max(W,H)*.78); g.addColorStop(0,'rgba(0,0,0,0)'); g.addColorStop(1,'rgba(0,0,0,.42)'); ctx.fillStyle=g; ctx.fillRect(0,0,W,H) }
function renderStatic(canvas,i,k,opt){ opt=opt||{}; if(!off){ off=mkRenderer(document.createElement('canvas'),false); off.setClearColor(0x2b2e34,1) }
  var W=canvas.width, H=canvas.height; if(!W||!H) return; off.setSize(W,H,false); setState(i,k,0); markActive(i,[]);
  camMon.aspect=W/H; camMon.updateProjectionMatrix(); wallsSolid(); off.render(scene,camMon);
  var ctx=canvas.getContext('2d'); ctx.clearRect(0,0,W,H); ctx.drawImage(off.domElement,0,0,W,H);
  if(opt.labels!==false) drawLabels(ctx,camMon,W,H); if(opt.vignette!==false) drawVignette(ctx,W,H) }
function renderCells(){ var dpr=Math.min(window.devicePixelRatio||1,2);
  document.querySelectorAll('canvas.cell').forEach(function(c){ var r=c.getBoundingClientRect(); if(!r.width) return; c.width=Math.round(r.width*dpr); c.height=Math.round(r.height*dpr);
    renderStatic(c, +c.dataset.i, +c.dataset.k, {labels:c.dataset.labels!=='0'}) }) }

// 下载：短边 1080 的 PNG。能否当参考图投喂须过 skills/previz 那三道门，未过门只作沟通稿与写控制图提示词的构图依据
var PX=(AH>AW)?[1080,Math.round(1080*AH/AW)]:[Math.round(1080*AW/AH),1080];
function save(canvas,name){ var a=document.createElement('a'); a.href=canvas.toDataURL('image/png'); a.download=name; document.body.appendChild(a); a.click(); a.remove() }
function frameCanvas(i,k,labels){ var c=document.createElement('canvas'); c.width=PX[0]; c.height=PX[1]; renderStatic(c,i,k,{labels:labels}); return c }
function exportFrame(i,k,labels){ save(frameCanvas(i,k,labels), ID+'-镜'+(SHOTS[i].n||i+1)+'.png') }
function exportAll(kFn,labels){ SHOTS.forEach(function(s,i){ setTimeout(function(){ exportFrame(i,kFn?kFn(s,i):.5,labels) }, i*320) }) }
function exportGrid(cols,labels){ cols=cols||(SHOTS.length>4?3:2); var rows=Math.ceil(SHOTS.length/cols), g=8, cw=Math.round(PX[0]/cols), ch=Math.round(cw*AH/AW);
  var c=document.createElement('canvas'); c.width=cw*cols+g*(cols+1); c.height=ch*rows+g*(rows+1); var x=c.getContext('2d'); x.fillStyle='#0e1014'; x.fillRect(0,0,c.width,c.height);
  SHOTS.forEach(function(s,i){ var fc=frameCanvas(i,.5,labels); x.drawImage(fc, g+(i%cols)*(cw+g), g+Math.floor(i/cols)*(ch+g), cw, ch) });
  save(c, ID+'-宫格'+cols+'x'+rows+'.png') }
function exportSvg(sel,vbDefault,w,name,bg){ var n=document.querySelector(sel); if(!n) return; var vb=(n.getAttribute('viewBox')||vbDefault).split(/\s+/), vw=parseFloat(vb[2]), vh=parseFloat(vb[3]);
  var c=document.createElement('canvas'); c.width=w; c.height=Math.round(w*vh/vw); var x=c.getContext('2d'); x.fillStyle=bg||'#101319'; x.fillRect(0,0,c.width,c.height);
  var s='<svg xmlns="http://www.w3.org/2000/svg" width="'+c.width+'" height="'+c.height+'" viewBox="0 0 '+vw+' '+vh+'" preserveAspectRatio="xMidYMid meet"><style>text{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}</style>'+n.innerHTML+'</svg>';
  var im=new Image(); im.onload=function(){ x.drawImage(im,0,0,c.width,c.height); save(c,name) }; im.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(s) }

// ── 放映页：导演视图（自由环视）+ 监视器（本镜画面）+ 时间轴 ─────────────
function player(bad){ var el=function(id){ return document.getElementById(id) };
  var vpDir=el('vp-dir'), vpMon=el('vp-mon'), cDir=el('c-dir'), cMon=el('c-mon'); if(!vpDir||!vpMon) return;
  var rDir=mkRenderer(cDir,true), rMon=mkRenderer(cMon,false); rDir.setPixelRatio(Math.min(window.devicePixelRatio||1,2)); rMon.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  rDir.setClearColor(0x000000,0); rMon.setClearColor(0x2b2e34,1);
  var camDir=new THREE.PerspectiveCamera(40,1,.5,1200); camDir.layers.enable(1);
  var orbit={target:new THREE.Vector3(50,11,50), theta:.62, phi:1.08, dist:150}, viewMode='free';
  function applyOrbit(){ var s=Math.sin(orbit.phi); camDir.position.set(orbit.target.x+orbit.dist*s*Math.sin(orbit.theta), orbit.target.y+orbit.dist*Math.cos(orbit.phi), orbit.target.z+orbit.dist*s*Math.cos(orbit.theta)); camDir.lookAt(orbit.target) }
  function setView(v,keep){ viewMode=v; document.querySelectorAll('#views button').forEach(function(b){ b.classList.toggle('on',b.dataset.v===v) }); var info=el('vpinfo');
    if(v==='free'){ if(!keep){ orbit.target.set(50,11,50); orbit.theta=.62; orbit.phi=1.08; orbit.dist=150 } info.textContent='透视 · 自由环视' }
    else if(v==='top'){ orbit.target.set(50,0,50); orbit.theta=0; orbit.phi=.12; orbit.dist=175; info.textContent='俯视 · 站位与机位分布' }
    else info.textContent='机位肩后 · 这台机器与被摄者的关系' }
  el('views').addEventListener('click',function(e){ var b=e.target.closest('button'); if(b) setView(b.dataset.v) });
  function behindView(c){ _p.set(c.pos[0],c.pos[1],c.pos[2]); _l.set(c.look[0],c.look[1],c.look[2]); _f.subVectors(_l,_p).normalize();
    var eye=_p.clone().addScaledVector(_f,-24).add(new THREE.Vector3(0,9,0)); orbit.target.copy(_l); var d=new THREE.Vector3().subVectors(eye,orbit.target);
    orbit.dist=d.length(); orbit.phi=Math.acos(clamp(d.y/orbit.dist,-1,1)); orbit.theta=Math.atan2(d.x,d.z) }
  (function(){ var drag=null; cDir.addEventListener('contextmenu',function(e){e.preventDefault()});
    cDir.addEventListener('pointerdown',function(e){ drag={x:e.clientX,y:e.clientY,pan:e.button===2||e.shiftKey}; cDir.setPointerCapture(e.pointerId); if(viewMode==='behind') setView('free',true) });
    cDir.addEventListener('pointermove',function(e){ if(!drag) return; var dx=e.clientX-drag.x, dy=e.clientY-drag.y; drag.x=e.clientX; drag.y=e.clientY;
      if(drag.pan){ var right=new THREE.Vector3().setFromMatrixColumn(camDir.matrix,0), up=new THREE.Vector3().setFromMatrixColumn(camDir.matrix,1), kk=orbit.dist*.0011; orbit.target.addScaledVector(right,-dx*kk).addScaledVector(up,dy*kk) }
      else { orbit.theta-=dx*.006; orbit.phi=clamp(orbit.phi-dy*.006,.08,1.52) } });
    cDir.addEventListener('pointerup',function(){ drag=null }); cDir.addEventListener('pointercancel',function(){ drag=null });
    cDir.addEventListener('wheel',function(e){ e.preventDefault(); orbit.dist=clamp(orbit.dist*Math.exp(e.deltaY*.0012),28,600) },{passive:false}) })();
  function resize(){ var a=vpDir.getBoundingClientRect(), b=vpMon.getBoundingClientRect();
    if(a.width&&a.height){ rDir.setSize(a.width,a.height,false); camDir.aspect=a.width/a.height; camDir.updateProjectionMatrix() }
    if(b.width&&b.height){ rMon.setSize(b.width,b.height,false) } }
  new ResizeObserver(resize).observe(vpDir); new ResizeObserver(resize).observe(vpMon); resize();
  // 标签层：HTML 文字浮在三维点上
  function labelLayer(node){ var items=[]; return {add:function(text,cls,posFn){ var d=document.createElement('div'); d.className='lb '+(cls||''); d.textContent=text; node.appendChild(d); var it={el:d,pos:posFn}; items.push(it); return it },
    place:function(cam,w,h,on){ var v=new THREE.Vector3(); items.forEach(function(it){ if(!on||it.hidden){ it.el.style.display='none'; return } var p=it.pos(); if(!p){ it.el.style.display='none'; return }
      v.copy(p).project(cam); var vis=v.z<1&&v.z>-1&&Math.abs(v.x)<1.1&&Math.abs(v.y)<1.1; it.el.style.display=vis?'':'none';
      if(vis){ it.el.style.left=((v.x+1)/2*w).toFixed(0)+'px'; it.el.style.top=((1-v.y)/2*h).toFixed(0)+'px' } }) } } }
  var LDir=labelLayer(el('lb-dir')), LMon=labelLayer(el('lb-mon'));
  Object.keys(figures).forEach(function(id){ var fg=figures[id]; if(!fg.f.label) return; var c=TONE_CSS[fg.f.tone]||TONE_CSS.grey;
    LDir.add(fg.f.label,'',function(){ return headPos(fg).add(new THREE.Vector3(0,1.6,0)) }).el.style.color=c; LMon.add(fg.f.label,'mon',function(){ return headPos(fg).add(new THREE.Vector3(0,1.2,0)) }).el.style.color=c });
  Object.keys(focusObjs).forEach(function(id){ var fo=focusObjs[id]; if(!fo.f.label) return; var c=TONE_CSS[fo.f.tone]||TONE_CSS.gold;
    LDir.add(fo.f.label,'',function(){ return fo.root.position.clone().add(new THREE.Vector3(0,(fo.f.r||1.5)*1.6+1,0)) }).el.style.color=c; LMon.add(fo.f.label,'mon',function(){ return fo.root.position.clone().add(new THREE.Vector3(0,(fo.f.r||1.5)*1.6+.6,0)) }).el.style.color=c });
  solidLabels.forEach(function(s){ LDir.add(s.text,'solid',function(){ return s.pos }) });
  var camLabels=rigs.map(function(r,i){ return LDir.add(String(SHOTS[i].n||i+1).padStart(2,'0')+' · '+(SHOTS[i].framing||''),'cam',function(){ return r.position.clone().add(new THREE.Vector3(0,2.6,0)) }) });
  if(axisLabelPos) LDir.add('180° 轴线','axis',function(){ return axisLabelPos });
  // 时间轴与规格
  var total=SHOTS.reduce(function(a,s){return a+(s.dur||0)},0), segs=[], box=el('segs'), rows=[].slice.call(document.querySelectorAll('#shotlist .shot'));
  SHOTS.forEach(function(s,i){ var d=document.createElement('div'); d.className='seg'; d.style.flexGrow=(s.dur||1);
    d.innerHTML='<div class="fill"></div><div class="ph"></div><span>'+String(s.n||i+1).padStart(2,'0')+'</span>'; d.onclick=function(){ jump(i) }; box.appendChild(d); segs.push(d) });
  rows.forEach(function(d,i){ d.onclick=function(){ jump(i) } });
  var t=0, playing=true, last=null, cur=-1;
  function jump(i){ t=SHOTS.slice(0,i).reduce(function(a,x){return a+(x.dur||0)},0)+.01; playing=true; el('play').textContent='暂停' }
  el('play').onclick=function(){ playing=!playing; this.textContent=playing?'暂停':'播放' };
  el('re').onclick=function(){ t=0; playing=true; el('play').textContent='暂停' };
  var T={}; ['grid','cams','path','axis','lb','monlb','cut'].forEach(function(k){ T[k]=el('tg-'+k) });
  function meta(i){ var s=SHOTS[i], nn=String(s.n||i+1).padStart(2,'0');
    el('sno').textContent=nn; el('tno').textContent=nn; el('sn').textContent=s.title||''; el('mf').textContent=s.framing||'—';
    el('mfov').textContent=(s.fov||40)+'°'+(s.fovTo?' → '+s.fovTo+'°':''); el('md').textContent=(s.dur||0).toFixed(2)+'s'+(s.pace?' · '+s.pace:'');
    el('mv').textContent=s.move||(s.orbit?'环绕':(s.to?'有运镜':'锁定机位 · 无漂移'));
    var lk=function(x){ return Array.isArray(x)?x.join(', '):String(x) };
    el('mcam').textContent=s.orbit?('圆心　'+s.orbit.center.join(', ')+'\n半径　'+s.orbit.r+'　高度　'+(s.orbit.y!==undefined?s.orbit.y:s.orbit.center[1])+'\n转角　'+s.orbit.from+'° → '+s.orbit.to+'°')
      :('机位　'+(s.cam||[]).join(', ')+(s.to?'\n落点　'+s.to.join(', '):'')+'\n看向　'+lk(s.look||[]));
    el('mi').textContent=s.intent||'—'; el('ml').textContent=s.lens||'—';
    var b=s.beat||{}; el('bk').textContent=b.kind==='line'?'台词':(b.kind==='sfx'?'音效':'节拍'); el('beat').textContent=(typeof b==='string')?b:(b.text||'—');
    el('mh1').textContent=(s.framing||'')+(s.move?' · '+s.move:'');
    rows.forEach(function(d,j){ d.classList.toggle('on',j===i) }); segs.forEach(function(d,j){ d.className='seg'+(j===i?' on':'') });
    markActive(i,bad); camLabels.forEach(function(l,j){ l.el.classList.toggle('on',j===i) });
    var fl=el('flick'); fl.style.opacity=.92; setTimeout(function(){ fl.style.opacity=0 },55);
    if(viewMode==='behind') behindView(camAt(s,0)) }
  var gz=el('gizmo');
  function drawGizmo(){ if(!gz) return; var m=camDir.matrixWorldInverse, ax=[['x','#d26b6b',new THREE.Vector3(1,0,0)],['y','#8fbf7a',new THREE.Vector3(0,1,0)],['z','#6f9bd6',new THREE.Vector3(0,0,1)]], s='';
    ax.map(function(a){ var v=a[2].clone().transformDirection(m); return {n:a[0],c:a[1],x:29+v.x*22,y:29-v.y*22,z:v.z} }).sort(function(p,q){return p.z-q.z}).forEach(function(p){
      s+='<line x1="29" y1="29" x2="'+p.x.toFixed(1)+'" y2="'+p.y.toFixed(1)+'" stroke="'+p.c+'" stroke-width="1.6" opacity=".9"/><circle cx="'+p.x.toFixed(1)+'" cy="'+p.y.toFixed(1)+'" r="6" fill="'+p.c+'"/><text x="'+p.x.toFixed(1)+'" y="'+(p.y+3.2).toFixed(1)+'" font-size="8" text-anchor="middle" fill="#111" font-family="IBM Plex Mono,monospace" font-weight="600">'+p.n+'</text>' });
    gz.innerHTML=s }
  function tick(ts){ if(last===null) last=ts; var dt=Math.min(.05,(ts-last)/1000); last=ts;
    if(playing){ t+=dt; if(t>=total) t=0 }
    var acc=0,i=0,lt=0; for(;i<SHOTS.length;i++){ if(t<acc+(SHOTS[i].dur||0)){ lt=t-acc; break } acc+=(SHOTS[i].dur||0) }
    if(i>=SHOTS.length){ i=SHOTS.length-1; lt=SHOTS[i].dur||0 }
    if(i!==cur){ cur=i; meta(i) }
    var s=SHOTS[i], k=lt/(s.dur||1), c=setState(i,k,dt);
    gazeLines.forEach(function(g){ g.line.visible=g.line.visible&&T.axis.checked }); pathGroup.visible=T.path.checked; axisGroup.visible=T.axis.checked; grid.visible=grid2.visible=edgeLine.visible=T.grid.checked;
    rigs.forEach(function(r,j){ r.visible=(j===i)||T.cams.checked }); paths.forEach(function(p,j){ if(p) p.visible=T.path.checked&&((j===i)||T.cams.checked) });
    if(viewMode==='behind') behindView(c); applyOrbit();
    camMon.aspect=AW/AH; camMon.updateProjectionMatrix(); wallsSolid(); rMon.render(scene,camMon);
    wallsCut(camDir,T.cut.checked); rDir.render(scene,camDir);
    var a=vpDir.getBoundingClientRect(), b=vpMon.getBoundingClientRect();
    camLabels.forEach(function(l,j){ l.hidden=!((j===i)||T.cams.checked) });
    LDir.place(camDir,a.width,a.height,T.lb.checked); LMon.place(camMon,b.width,b.height,T.monlb.checked);
    segs.forEach(function(d,j){ var pc=j<i?100:(j===i?k*100:0); d.querySelector('.fill').style.width=pc+'%'; if(j===i) d.querySelector('.ph').style.left=pc+'%' });
    el('clock').innerHTML=t.toFixed(1).padStart(4,'0')+' <small>/ '+total.toFixed(1)+' s</small>';
    el('mh2').textContent=String(s.n||i+1).padStart(2,'0')+' · '+c.fov.toFixed(0)+'° · '+lt.toFixed(2)+'s';
    el('dirinfo').textContent='机位 '+c.pos.map(function(v){return v.toFixed(0)}).join(', ')+' → 看向 '+c.look.map(function(v){return v.toFixed(0)}).join(', ')+' · 视场 '+c.fov.toFixed(0)+'°';
    drawGizmo(); requestAnimationFrame(tick) }
  applyOrbit(); requestAnimationFrame(tick);
  return {current:function(){ return cur }, k:function(){ var acc=0; for(var i=0;i<cur;i++) acc+=SHOTS[i].dur||0; return clamp((t-acc)/(SHOTS[cur].dur||1),0,1) },
    exportDirector:function(){ save(cDir, ID+'-导演视图.png') }, labelsOn:function(){ return T.monlb.checked }} }

return {renderCells:renderCells, player:player, exportFrame:exportFrame, exportAll:exportAll, exportGrid:exportGrid, exportSvg:exportSvg, camAt:camAt};
})();
if(!PV){ document.querySelectorAll('.needs-webgl').forEach(function(n){ n.textContent='three.js 未能加载：本页需要联网加载 https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js，或把 three.min.js 放到 previz.py 同目录后重渲' }) }
"""

DLBAR = {
    "play": '<div class="w dl"><span class="t">下载</span>'
            '<button onclick="PV&&PV.exportFrame(P.current(),P.k(),P.labelsOn())">当前帧</button>'
            '<button onclick="PV&&PV.exportAll(null,P.labelsOn())">全部帧</button>'
            '<button onclick="PV&&PV.exportGrid(null,P.labelsOn())">宫格图</button>'
            '<button onclick="P&&P.exportDirector()">导演视图</button>'
            '<span class="h">帧图短边 1080。当参考图投喂须先过 control-image 三道门——它没有通用基准段与场域锚句；导演视图与俯视只给人看，勿投喂。</span></div>',
    "grid": '<div class="w dl"><span class="t">下载</span>'
            '<button onclick="PV&&PV.exportGrid(COLS,true)">整张宫格图</button><button onclick="PV&&PV.exportAll(null,true)">拆成单格</button>'
            '<span class="h">整张宫格图作沟通稿与构图依据；当宫格控制图投喂须先过 control-image 三道门——它没有通用基准段与场域锚句</span></div>',
    "keyframes": '<div class="w dl"><span class="t">下载</span>'
                 '<button onclick="PV&&PV.exportAll(function(){return 0},true)">全部关键帧</button><button onclick="PV&&PV.exportGrid(null,true)">拼成宫格图</button>'
                 '<span class="h">关键帧作沟通稿与构图依据；当控制图投喂须先过 control-image 三道门，未过门不进条头【上传清单】</span></div>',
    "plan": '<div class="w dl"><span class="t">下载</span>'
            '<button onclick="exportSvg(\'.plan\',\'0 0 240 300\',1080,ID+\'-站位图.png\')">站位图</button>'
            '<span class="h">代码画的站位精度高于生成，但能否替代生成的站位控制图是待验项；当前只作人用规划 · 勿投喂</span></div>',
    "stage": '<div class="w dl"><span class="t">下载</span>'
             '<button onclick="exportSvg(\'.stagewrap svg\',\'0 0 1000 1000\',1600,ID+\'-场记平面图.png\',\'#0b0d11\')">场记平面图 PNG</button>'
             '<span class="h">总览是工作视图，给人审覆盖用；带机位，不作投喂。</span></div>',
    "cut": '<div class="w dl"><span class="t">下载</span>'
           '<button onclick="PV&&PV.exportAll(null,true)">全部帧</button>'
           '<span class="h">接缝两帧可作沟通稿；投喂前仍须过 control-image 三道门。</span></div>',
}

TPL = """<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 草图预演</title><style>{css}</style></head>
<body class="{cls}" style="--ar:{ar};--cutw:{cutw}">
<header class="w hd"><i class="mk"></i><h1 class="cn">草图预演</h1><span class="sep"></span>
<span class="mode cn">{mode}</span><span class="id mo">{title}</span><span class="chips">{chips}</span>{tools}</header>
{note}
{body}
<footer class="w foot cn">
  <b>草图只验证</b>构图 · 站位 · 姿态 · 走位 · 运镜 · 节奏时长 · 台词时点<span class="sep">|</span>
  <b>不代表</b>布光 · 表演 · 材质质感 · 模型实际输出<br>
  三维是唯一真相源——监视器是它的透视投影、俯视图是它的正交投影、导演视图是同一份数据换个角度看。
  人偶只有体量、姿态与朝向，一盏工作室灯只为分清体块与遮挡，不是布光；光影氛围归分镜图阶段。
  草图丑不等于提示词错，草图顺眼不等于成片稳。
</footer>
{script}
</body></html>"""

MODE_LABEL = {"play": "导演台 · 动态放映", "grid": "宫格预览", "keyframes": "关键帧预览",
              "plan": "站位图", "stage": "场记平面图", "cut": "接缝检查"}

def _chk(ok, t):
    return ('<div class="axmsg %s"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="%s" '
            'stroke-width="2.4" style="flex:0 0 13px;margin-top:2px">%s</svg><span class="cn">%s</span></div>'
            % ("ok" if ok else "no", "#7d9a6f" if ok else "#c97b6b",
               '<path d="M20 6L9 17l-5-5"/>' if ok else '<path d="M12 8v5M12 17h.01"/>', t))

def _three_tag():
    """同目录有 three.min.js 就内嵌——HTML 离线可开；没有就走 cdnjs，打开时需联网。"""
    if os.path.exists(THREE_LOCAL):
        with open(THREE_LOCAL, encoding="utf-8") as f:
            return "<script>%s</script>" % f.read(), "内嵌 three.min.js"
    return '<script src="%s"></script>' % THREE_CDN, "cdnjs 加载 three.js（需联网）"

def build_html(scene, mode="play", cols=None):
    m, shots = scene["meta"], scene["shots"]
    aw, ah = parse_aspect(m.get("aspect", "9:16"))
    axmsg, bad = check_axis(scene)
    bad_idx = [i for i, s in enumerate(shots) if s.get("n", i+1) in bad]
    cuts = check_cuts(scene)
    total = round(sum(s.get("dur", 0) for s in shots), 2)
    title = "%s · %s" % (m.get("id", ""), m.get("title", ""))
    portrait = ah > aw
    chips = [m.get("track") and (m["track"] + " 轨"), m.get("aspect", "9:16"), "%d 镜" % len(shots), "%.1fs" % total, "引擎 " + ENGINE_VERSION]
    chip_html = "".join('<span class="chip">%s</span>' % esc(c) for c in chips if c)
    vh = round(1000*ah/aw)
    tools, note_html, three_src = "", '<div class="w note cn">%s</div>' % esc(m.get("note", "")), ""
    needs_three = mode in ("play", "grid", "keyframes", "cut")

    def cell(i, k, labels=True):
        return '<canvas class="cell" data-i="%d" data-k="%s" data-labels="%s"></canvas>' % (i, k, "1" if labels else "0")

    if mode == "grid":
        n = len(shots); c = cols or max(2, min(4, math.ceil(math.sqrt(n))))    # 6 镜 3 列、9 镜 3 列、16 镜 4 列
        gw = "%dpx" % min(1100, c * (250 if portrait else 360))
        items = []
        for i, s in enumerate(shots):
            items.append('<div class="gitem"><div class="gcell"><span class="no">%d</span>%s</div>'
                         '<div class="gcap"><div class="t cn">%s</div><div class="m"><span class="cn">%s</span><span class="mo">%.2fs</span></div></div></div>'
                         % (s.get("n", i+1), cell(i, 0.5), esc(s.get("title", "")), esc(s.get("framing", "")), s.get("dur", 0)))
        body = ('<div class="w gridwrap" style="--gw:%s"><div class="gimg" style="grid-template-columns:repeat(%d,1fr)">%s</div>'
                '<div class="needs-webgl cn"></div></div>' % (gw, c, "".join(items)))
        init = "if(PV)PV.renderCells();"

    elif mode == "keyframes":
        kw = "196px" if portrait else "300px"; kh = "348px" if portrait else "169px"
        parts = []
        for i, s in enumerate(shots):
            parts.append('<div class="kf"><div class="im">%s</div><div class="t mo">%s</div><div class="n cn">%s</div><div class="d cn">%s</div></div>'
                         % (cell(i, 0.0), esc(s.get("at", "第 %d 帧" % s.get("n", i+1))), esc(s.get("title", "")), esc(s.get("framing", ""))))
            if i < len(shots)-1:
                parts.append('<div class="gap"><div class="ln"></div><div class="v">%.2fs</div></div>' % s.get("dur", 0))
        body = ('<div class="w card" style="--kw:%s;--kh:%s"><h2>关键帧序列 · 帧间数字为该帧到下一帧的时长</h2>'
                '<div class="kfstrip">%s</div><div class="needs-webgl cn"></div></div>' % (kw, kh, "".join(parts)))
        init = "if(PV)PV.renderCells();"

    elif mode == "plan":
        body = ('<div class="w planwrap"><div class="card"><svg class="plan" viewBox="0 0 240 300" style="aspect-ratio:4/5">%s</svg>'
                '<div class="legend">实心圆 = 人所在位置，短针 = 躯干朝向，细虚线 = 视线，粗虚线带空心起点 = 走位路径；长虚线 = 180° 轴线；灰块 = 地标。'
                '<br><b style="color:var(--dim)">本图只画站位。</b>机位、镜号、景别不在此图——一张图干两件事就两件都不成立；要看机位分布用场记平面图。</div></div></div>'
                % render_plan(scene, pure=True))
        init = ""

    elif mode == "stage":
        W, H, svg = render_stage(scene, shots)
        leg = [("扇形", "该机位实际覆盖，张角即视场角"), ("虚线", "视线指向"), ("粗针", "躯干朝向"),
               ("长虚线", "180° 轴线"), ("弧线箭头", "环绕机位的行进方向")]
        body = ('<div class="w stagewrap"><div class="card"><svg viewBox="0 0 %d %d" style="width:100%%;display:block;border-radius:4px">%s</svg>'
                '<div style="display:flex;gap:20px;flex-wrap:wrap;margin-top:14px;padding-top:12px;border-top:1px solid var(--line)">%s</div>'
                '<div class="legend" style="margin-top:10px">垂直俯视——没有遮挡、距离与角度都是真的，所以覆盖看得出来：扇形重叠是冗余，空白是没拍到。'
                '<br><b style="color:var(--dim)">本屏是工作视图，带机位。</b>站位图是交付物，只画站位；要立体地看机位与人的关系，用 play 模式的导演视图。</div></div></div>'
                % (W, H, svg, "".join('<span class="cn" style="font-size:11px;color:#5a606e"><b style="color:#8a8f9c;font-weight:600">%s</b>　%s</span>' % (a_, b_) for a_, b_ in leg)))
        init = ""

    elif mode == "cut":
        rows = []
        p_ax, q_ax = axis_ends(scene)
        for a_n, b_n, deg, moving in cuts:
            i = next(k for k, s in enumerate(shots) if s.get("n", k+1) == a_n)
            A, B = shots[i], shots[i+1]
            jump = deg < 30 and not moving
            ax_ok = True
            if p_ax and q_ax and not A.get("onAxis") and not B.get("onAxis"):
                sa, sb = axis_side(p_ax, q_ax, cam_at(A, 1.0)["pos"]), axis_side(p_ax, q_ax, cam_at(B, 0.0)["pos"])
                ax_ok = not (sa and sb and sa != sb)
            def card(s, idx, k, n):
                return ('<div class="cutf"><div class="im">%s<span class="no mo">%02d</span></div><div class="t cn">%s</div><div class="m cn">%s</div></div>'
                        % (cell(idx, k), n, esc(s.get("title", "")), esc(s.get("framing", ""))))
            rows.append('<div class="cutrow"><div class="cutpair">%s<div class="arr"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" '
                        'stroke="#4c5566" stroke-width="1.8"><path d="M5 12h14M13 6l6 6-6 6"/></svg></div>%s</div><div class="cutchk">%s%s</div></div>'
                        % (card(A, i, 1.0, a_n), card(B, i+1, 0.0, b_n),
                           _chk(ax_ok, "守轴 · 两机位在轴线%s" % ("同侧，反打成立" if ax_ok else "两侧，越轴")),
                           _chk(not jump, "机位夹角 %d°%s" % (deg, " · 低于 30°，会读成跳切" if jump else
                                (" · 低于 30° 但景别、运动或换了被摄者已打断跳切读感" if deg < 30 else " · 超过 30°，不会读成跳切")))))
        body = ('<div class="w card"><h2>逐缝检查 · 出点 → 入点</h2><div>%s</div><div class="needs-webgl cn"></div>'
                '<div class="legend" style="margin-top:14px">机位夹角 = 两台摄影机在被摄者处张开的角度。低于 30° 的切会被读成跳切——这个数二维算不出来，二维没有摄影机、只有裁切窗。</div></div>'
                % "".join(rows))
        init = "if(PV)PV.renderCells();"

    else:                                                     # play：导演台
        rows = []
        for i, s in enumerate(shots):
            rows.append('<div class="shot"><i class="dot"></i><span class="no">%02d</span><div><div class="t cn">%s</div>'
                        '<div class="m"><span class="cn">%s</span><span class="mo">%s°%s</span><span class="mo">%.2fs</span><span class="cn">%s</span></div></div></div>'
                        % (s.get("n", i+1), esc(s.get("title", "")), esc(s.get("framing", "")), s.get("fov", 40),
                           ("→%s°" % s["fovTo"]) if s.get("fovTo") else "", s.get("dur", 0),
                           esc(s.get("move") or ("环绕" if s.get("orbit") else ("有运镜" if s.get("to") else "锁定机位")))))
        checks = _chk(not bad, "轴线 · " + esc(axmsg)) + "".join(
            _chk(not (d < 30 and not mv), "接缝 %02d → %02d · 机位夹角 %d°%s" % (a_, b_, d,
                 "，低于 30° 会读成跳切" if (d < 30 and not mv) else ("，景别、运动或换主体已打断跳切读感" if d < 30 else "")))
            for a_, b_, d, mv in cuts)
        tools = ('<div class="tools"><div class="segbtn" id="views"><button class="on cn" data-v="free">自由环视</button>'
                 '<button class="cn" data-v="top">俯视</button><button class="cn" data-v="behind">机位肩后</button></div></div>')
        note_html = ""
        body = ("""<main class="w main">
  <aside class="side l">
    <section class="card"><h2>镜头列表</h2><div id="shotlist">__ROWS__</div></section>
    <section class="card"><h2>自检</h2><div id="checks">__CHECKS__</div></section>
    <section class="card"><h2>图例</h2><div class="legend cn">
      <i style="background:#f0a238"></i>当前机位与其取景锥 · 锥底即画框，落在被摄者处<br>
      <i style="background:#6b7280"></i>其余机位，编号与镜头表一致<br>
      <i style="background:#e8e6e1;opacity:.6"></i>180° 轴线（地面虚线）<br>
      <i style="background:#87a9c6"></i>视线（人偶之间的细线）· 走位箭头（地面）<br>
      <b>人偶</b>只表示身高、姿态、朝向、站位与遮挡；没有表情、没有服装、没有布光。<br>
      <b>导演视图</b>左键拖拽环视 · 右键或 ⇧ 拖拽平移 · 滚轮缩放。</div></section>
  </aside>
  <section class="stage"><div class="vp" id="vp-dir"><canvas id="c-dir"></canvas><div class="labels" id="lb-dir"></div>
    <div class="hud tl"><span class="k">导演视图</span><span id="vpinfo" class="needs-webgl">透视 · 自由环视</span></div>
    <div class="hud bl" id="dirinfo"></div><div class="hud br cn">左键拖拽 环视 · 右键 / ⇧ 拖拽 平移 · 滚轮 缩放</div>
    <svg class="gizmo" viewBox="0 0 58 58" id="gizmo"></svg></div></section>
  <aside class="side r">
    <div class="mon" id="vp-mon" style="aspect-ratio:__AR__"><canvas id="c-mon"></canvas><div class="labels" id="lb-mon"></div><div id="flick"></div>
      <i class="tick a"></i><i class="tick b"></i><i class="tick c"></i><i class="tick d"></i>
      <div class="tally"><i></i><span id="tno">01</span></div><div class="vig"></div>
      <div class="monhud"><span class="cn" id="mh1"></span><span class="mo" id="mh2"></span></div></div>
    <div class="beat"><span class="k" id="bk">节拍</span><span class="v cn" id="beat"></span></div>
    <div class="card" style="display:flex;flex-direction:column;gap:12px">
      <div class="sn"><span class="no" id="sno">01</span><span class="t cn" id="sn"></span></div>
      <dl class="meta"><div><dt>景别</dt><dd class="cn" id="mf"></dd></div><div><dt>视场角</dt><dd class="mo" id="mfov"></dd></div>
        <div><dt>时长</dt><dd class="mo" id="md"></dd></div><div><dt>运镜</dt><dd class="cn" id="mv"></dd></div></dl>
      <div class="blk"><div class="k">摄影机</div><div class="v mo" id="mcam"></div></div>
      <div class="blk"><div class="k">导演意图</div><div class="v cn" id="mi"></div></div>
      <div class="blk lens"><div class="k">镜头语言 · 原文</div><div class="v cn" id="ml"></div></div>
    </div>
  </aside>
</main>
<div class="w strip">
  <div class="striphd"><span class="lbl">时间轴</span><span class="cn" style="font-size:10.5px;color:#4c5361">段宽即时长比例 · 点击段落跳转</span><span class="clock" id="clock"></span></div>
  <div class="segs" id="segs"></div>
  <div class="bar"><button id="play" class="cn">暂停</button><button id="re" class="cn">重放</button><span class="sp"></span>
    <label class="tg cn"><input type="checkbox" id="tg-grid" checked> 网格</label>
    <label class="tg cn"><input type="checkbox" id="tg-cams" checked> 全部机位</label>
    <label class="tg cn"><input type="checkbox" id="tg-path" checked> 轨迹</label>
    <label class="tg cn"><input type="checkbox" id="tg-axis" checked> 轴线 · 视线</label>
    <label class="tg cn"><input type="checkbox" id="tg-lb" checked> 标签</label>
    <label class="tg cn"><input type="checkbox" id="tg-monlb"> 监视器标签</label>
    <label class="tg cn"><input type="checkbox" id="tg-cut" checked> 墙体剖切</label></div>
</div>""".replace("__ROWS__", "".join(rows)).replace("__CHECKS__", checks).replace("__AR__", "%s/%s" % (aw, ah)))
        init = "var P=PV?PV.player(BAD):null;"

    dl = DLBAR.get(mode, "")
    if needs_three:
        three, three_src = _three_tag()
    else:
        three = ""
    boot = ('<script>var SCENE=%s,AW=%s,AH=%s,OVH=%s,ID=%s,COLS=%s,MODE=%s,BAD=%s;%s</script>%s<script>%s\n%s</script>'
            % (json.dumps(scene, ensure_ascii=False), aw, ah, vh, json.dumps(m.get("id", "previz"), ensure_ascii=False),
               cols or "null", json.dumps(mode), json.dumps(bad_idx), SVG_EXPORT_JS, three,
               STAGE_JS if needs_three else "", init))
    return TPL.format(css=CSS, title=esc(title), chips=chip_html, body=body + dl, script=boot, note=note_html,
                      mode=esc(MODE_LABEL.get(mode, mode)), ar="%s/%s" % (aw, ah), cls=mode + ("" if portrait else " land"),
                      cutw="300px" if portrait else "440px", tools=tools), three_src

def main(argv):
    ap = argparse.ArgumentParser(description="草图预演渲染引擎（三维 · 导演台）")
    ap.add_argument("scene"); ap.add_argument("-o", "--out")
    ap.add_argument("-m", "--mode", default="play",
                    choices=["play", "grid", "keyframes", "plan", "stage", "cut"],
                    help="play=导演台动态放映 grid=宫格 keyframes=关键帧 plan=站位图 stage=场记平面图（俯视，带机位） cut=接缝检查")
    ap.add_argument("--cols", type=int)
    ap.add_argument("--version", action="store_true", help="打印引擎版本后退出；skill 启动前用它核对")
    if "--version" in argv[1:]:
        print("previz %s 导演台三维白模 · three.js r128 · %s" % (ENGINE_VERSION, "内嵌 three.min.js" if os.path.exists(THREE_LOCAL) else "cdnjs（需联网）")); return 0
    a = ap.parse_args(argv[1:])
    scene = load_scene(a.scene)
    health = check_health(scene)
    fatal = [m for f_, m in health if f_]
    if health:
        print("⚠ 场景数据有 %d 处会让自检空转或画错——「没报错」不等于「全绿」：" % len(health))
        for f_, m in health: print("    %s%s" % ("[拦下] " if f_ else "", m))
    if fatal:
        sys.stderr.write("有 %d 处会让引擎崩，已拦在渲染之前——填完再跑，未改动已有产物。\n" % len(fatal))
        return 2
    out = a.out or "%s.%s.html" % (os.path.splitext(a.scene)[0], a.mode)
    html_text, three_src = build_html(scene, a.mode, a.cols)   # 先渲成功，再落盘
    with open(out, "w", encoding="utf-8") as f:
        f.write(html_text)
    msg, bad = check_axis(scene)
    print("草图已生成：%s（引擎 %s · %s · %d 镜 · %.1fs · %s 画幅%s）"
          % (out, ENGINE_VERSION, MODE_LABEL.get(a.mode, a.mode), len(scene["shots"]),
             sum(s.get("dur", 0) for s in scene["shots"]), scene["meta"].get("aspect", "9:16"),
             (" · " + three_src) if three_src else ""))
    print("轴线检查：%s%s" % (msg, "　⚠ 若非刻意越轴，改机位或走合法越轴路径" if bad else ""))
    jc = [(a_, b_, d) for a_, b_, d, mv in check_cuts(scene) if d < 30 and not mv]
    if jc:
        print("⚠ 接缝夹角过小，会读成跳切：")
        for a_, b_, d in jc: print("    镜 %s → 镜 %s：夹角 %d°，低于 30°" % (a_, b_, d))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
