
import math
import os
import random
import shutil
import sys
import time

FPS = 20
CYCLE = 20.0          
ASPECT = 2.0
RAMP = ".:-=+*#%@"
LEVELS = 12

# timeline within each cycle, in seconds
GROW = (0.0, 3.0)     
RISE = (2.4, 4.2)     
SPLIT = (4.0, 4.8)    
DROP = 4.8            
UNFURL = (4.6, 9.5)   
CENTER = (6.4, 9.5)   
SWAY = (9.0, 11.0)    
SHED = 16.0

STEM_LEN = 2.2
PETAL_LEN = 1.4
PETAL_AZ = 0.55
SEPAL_AZ = PETAL_AZ + math.pi / 4
BUD_H, BUD_R = 0.75, 0.3

PETAL = ([58, 94, 136, 172, 178, 214, 220, 220, 221, 227, 228, 229], 0.28, 0.62, 0.4)
SEPAL = ([22, 22, 28, 28, 64, 70, 70, 106, 107, 113, 149, 150], 0.2, 0.8, 0.0)
POD = ([22, 28, 64, 70, 76, 106, 112, 113, 149, 150, 155, 193], 0.25, 0.75, 0.0)
STEM, SOIL, ANTHER, FILAMENT = 70, 94, 214, 186
ESC = ["\x1b[38;5;%dm" % i for i in range(256)]

_rng = random.Random(3)
STAMENS = [(_rng.uniform(0, math.tau), _rng.uniform(0.8, 1.15), _rng.random())
           for _ in range(90)]


def clamp01(x):
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def phase(t, span):
    return clamp01((t - span[0]) / (span[1] - span[0]))


def ease(x):
    x = clamp01(x)
    return x * x * (3.0 - 2.0 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def normalize(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    return (v[0] / n, v[1] / n, v[2] / n)


LIGHT = normalize((-0.4, 1.0, -0.5))


def make_xf(origin, psi, scale):
    """Local -> world: tilt by psi in the x-y plane, scale, then move."""
    c, s = math.cos(psi), math.sin(psi)
    ox, oy, oz = origin

    def xf(x, y, z):
        return (ox + scale * (c * x + s * y), oy + scale * (c * y - s * x), oz + scale * z)
    return xf


def stem_curve(S, nod, sway, n):
    crook = min(0.5, S * 0.4)

    def psi(s):
        return (0.08 * math.sin(math.tau * s / STEM_LEN) + sway * (s / S) ** 2
                + nod * ease((s - (S - crook)) / crook))

    ds = S / (n - 1)
    x = y = 0.0
    pts = [(0.0, 0.0)]
    for i in range(n - 1):
        a = psi((i + 0.5) * ds)
        x += math.sin(a) * ds
        y += math.cos(a) * ds
        pts.append((x, y))
    return pts, psi(S)


def sepal_grid(xf, s, gamma, tau, n):
    th = SEPAL_AZ + s * math.pi
    ch, sh = math.cos(th), math.sin(th)
    cg, sg = math.cos(gamma), math.sin(gamma)
    dx, dy, dz = 0.5 * tau * ch, -3.0 * tau * tau, 0.5 * tau * sh
    grid = []
    for i in range(n):
        u = 0.02 + 0.97 * i / (n - 1)
        rad = BUD_R * math.sin(math.pi * u ** 0.8) ** 0.8
        y = BUD_H * u - 0.04
        row = []
        for j in range(n):
            a = (-0.52 + 1.04 * j / (n - 1)) * math.pi
            r, w = rad * math.cos(a), rad * math.sin(a)
            r2 = 0.05 + (r - 0.05) * cg + y * sg
            y2 = (0.05 - r) * sg + y * cg
            x, yy, z = xf(r2 * ch - w * sh, y2, r2 * sh + w * ch)
            row.append((x + dx, yy + dy, z + dz))
        grid.append(row)
    return grid


def petal_grid(xf, k, L, phib, bend, cup, widthf, crumple, nu, nv):
    th = PETAL_AZ + k * math.pi / 2
    ct, st = math.cos(th), math.sin(th)
    du = 0.96 / (nu - 1)
    r, y = 0.06, 0.03
    grid = []
    for i in range(nu):
        u = 0.02 + i * du
        phi = phib - bend * u
        sp, cp = math.sin(phi), math.cos(phi)
        hw = L * widthf * 0.52 * math.sin(math.pi * u ** 1.6) ** 0.5
        row = []
        for j in range(nv):
            v = -1.0 + 2.0 * j / (nv - 1)
            w = v * hw
            off = (cup * w * w / L + crumple * 0.08 * L * u
                   * math.sin(u * 11 + v * 5 + k * 2.1) * math.cos(v * 9 - u * 7 + k))
            rr = r - off * cp
            row.append(xf(rr * ct - w * st, y + off * sp, rr * st + w * ct))
        grid.append(row)
        r += L * du * sp
        y += L * du * cp
    return grid


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        dist, elev, az, target = 7.5, 0.75, 0.25, (0.0, 1.6, 0.0)
        pos = (dist * math.cos(elev) * math.sin(az), target[1] + dist * math.sin(elev),
               -dist * math.cos(elev) * math.cos(az))
        fwd = normalize(tuple(b - a for a, b in zip(pos, target)))
        right = normalize((fwd[2], 0.0, -fwd[0]))
        up = (fwd[1] * right[2] - fwd[2] * right[1],
              fwd[2] * right[0] - fwd[0] * right[2],
              fwd[0] * right[1] - fwd[1] * right[0])
        self.cam, self.fwd, self.right, self.up = pos, fwd, right, up

        xs, ys = [], []
        for i in range(24):
            a = math.tau * i / 24
            for rad, y in ((0.4, 0.0), (1.7, STEM_LEN - 0.1), (1.7, STEM_LEN + 0.9)):
                p = self._view((rad * math.cos(a), y, rad * math.sin(a)))
                xs.append(p[0] / p[2])
                ys.append(p[1] / p[2])
        k = min((h - 1) / (max(ys) - min(ys)), (w - 2) / ((max(xs) - min(xs)) * ASPECT))
        self.ky, self.kx = k, k * ASPECT
        self.cx = w / 2 - self.kx * (max(xs) + min(xs)) / 2
        self.cy = h / 2 + self.ky * (max(ys) + min(ys)) / 2
        self.cpu = self.kx / dist

    def _view(self, p):
        d = (p[0] - self.cam[0], p[1] - self.cam[1], p[2] - self.cam[2])
        return (sum(a * b for a, b in zip(d, self.right)),
                sum(a * b for a, b in zip(d, self.up)),
                sum(a * b for a, b in zip(d, self.fwd)))

    def clear(self):
        n = self.w * self.h
        self.z, self.ch, self.col = [0.0] * n, [" "] * n, [0] * n

    def project(self, p):
        x, y, z = self._view(p)
        if z < 0.5:
            return None
        return self.cx + self.kx * x / z, self.cy - self.ky * y / z, 1.0 / z

    def plot(self, p, color, ch, bias=0.0):
        q = self.project(p)
        if q:
            sx, sy = int(q[0] + 0.5), int(q[1] + 0.5)
            if 0 <= sx < self.w and 0 <= sy < self.h:
                i = sy * self.w + sx
                if q[2] + bias > self.z[i]:
                    self.z[i], self.ch[i], self.col[i] = q[2] + bias, ch, color

    def mesh(self, grid, material, edge=None, clip=False):
        colors, amb, dif, glow = material
        w, h, z, chs, cols = self.w, self.h, self.z, self.ch, self.col
        ox, oy, oz = self.cam
        rx, ry, rz = self.right
        ux, uy, uz = self.up
        fx, fy, fz = self.fwd
        lx, ly, lz = LIGHT
        top = len(grid) - 1
        for i, row in enumerate(grid):
            prev, nxt = grid[max(i - 1, 0)], grid[min(i + 1, top)]
            last = len(row) - 1
            for j, (px, py, pz) in enumerate(row):
                if clip and py < 0.0:
                    continue
                dx, dy, dz = px - ox, py - oy, pz - oz
                zc = dx * fx + dy * fy + dz * fz
                if zc < 0.5:
                    continue
                ooz = 1.0 / zc
                sx = int(self.cx + 0.5 + self.kx * (dx * rx + dy * ry + dz * rz) * ooz)
                sy = int(self.cy + 0.5 - self.ky * (dx * ux + dy * uy + dz * uz) * ooz)
                if not (0 <= sx < w and 0 <= sy < h):
                    continue
                idx = sy * w + sx
                if ooz <= z[idx]:
                    continue
                a1, a0 = nxt[j], prev[j]
                b1, b0 = row[min(j + 1, last)], row[max(j - 1, 0)]
                ax, ay, az = a1[0] - a0[0], a1[1] - a0[1], a1[2] - a0[2]
                bx, by, bz = b1[0] - b0[0], b1[1] - b0[1], b1[2] - b0[2]
                nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
                ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
                d = (nx * lx + ny * ly + nz * lz) / ln
                if nx * dx + ny * dy + nz * dz > 0.0:
                    d = -d
                lum = amb + dif * d if d > 0.0 else amb - glow * d
                if edge:
                    lum *= edge[j]
                lvl = min(LEVELS - 1, int(lum * (LEVELS - 1) + 0.5))
                z[idx], cols[idx] = ooz, colors[lvl]
                chs[idx] = RAMP[lvl * len(RAMP) // LEVELS]

    def stem(self, pts):
        proj = [self.project((x, y, 0.0)) for x, y in pts]
        last_row = None
        for p0, p1 in zip(proj, proj[1:]):
            if not (p0 and p1):
                continue
            ang = math.atan2((p0[1] - p1[1]) * ASPECT, p1[0] - p0[0]) % math.pi
            ch = "-/|\\-"[int((ang + math.pi / 8) / (math.pi / 4))]
            row = int(p0[1] + 0.5)
            if ch == "|" and row == last_row:
                continue
            last_row = row
            sx, sy = int(p0[0] + 0.5), row
            if 0 <= sx < self.w and 0 <= sy < self.h:
                i = sy * self.w + sx
                if p0[2] > self.z[i]:
                    self.z[i], self.ch[i], self.col[i] = p0[2], ch, STEM

    def frame(self):
        out, w = [], self.w
        for y in range(self.h):
            row = self.ch[y * w:(y + 1) * w]
            end = len("".join(row).rstrip())
            out.append("\x1b[%d;1H" % (y + 1))
            last = -1
            for x in range(end):
                c = row[x]
                if c != " " and self.col[y * w + x] != last:
                    last = self.col[y * w + x]
                    out.append(ESC[last])
                out.append(c)
            out.append("\x1b[K")   # clear the rest of the line
        return "".join(out)


def draw(cv, t):
    cv.clear()
    for i in range(-8, 9):
        cv.plot((i * 0.06, 0.0, (i % 3) * 0.04), SOIL, "_.,~"[i % 4])

    S = lerp(0.05, STEM_LEN, 1.0 - (1.0 - phase(t, GROW)) ** 3)
    nod = 2.6 * (1.0 - ease(phase(t, RISE)))
    breeze = 0.015 + 0.05 * ease(phase(t, SWAY))
    sway = breeze * (math.sin(t * 1.3) + 0.4 * math.sin(t * 2.9 + 1.0))
    pts, psi = stem_curve(S, nod, sway, max(12, int(S * cv.cpu) + 8))
    cv.stem(pts)
    tip = (pts[-1][0], pts[-1][1], 0.0)
    head = make_xf(tip, psi, lerp(0.5, 1.0, ease(phase(t, (0.0, 4.0)))))

    if t < DROP + 1.5:
        tau = max(0.0, t - DROP)
        gamma = 0.5 * ease(phase(t, SPLIT)) + 3.0 * tau
        n = max(8, int(BUD_H * cv.cpu) + 4)
        for s in (0, 1):
            cv.mesh(sepal_grid(head, s, gamma, tau, n), SEPAL, clip=True)

    opening = 0.12
    if t >= SPLIT[0]:
        for k in range(4):
            inner = k % 2
            e = ease(phase(t, (UNFURL[0] + 0.5 * inner, UNFURL[1] + 0.4 * inner)))
            L = lerp(0.6, PETAL_LEN, e) * (0.9 if inner else 1.0)
            phib = lerp(0.12, 1.38, e) - 0.12 * e * inner
            if inner:
                opening = phib
            xf, fall = head, t - SHED - 0.6 * k
            if fall > 0.0:
                th = PETAL_AZ + k * math.pi / 2
                phib += 1.5 * fall
                xf = make_xf((tip[0] + 0.6 * fall * math.cos(th), tip[1] - 2.5 * fall * fall,
                              0.6 * fall * math.sin(th)), psi, 1.0)
            nu = max(8, int(L * cv.cpu) + 4)
            nv = max(8, int(L * cv.cpu * 1.2) + 4)
            edge = [1.0 - 0.35 * abs(-1.0 + 2.0 * j / (nv - 1)) ** 5 for j in range(nv)]
            grid = petal_grid(xf, k, L, phib, lerp(0.85, 0.55, e), lerp(1.3, 0.45, e),
                              lerp(0.6, 1.0, e), 0.3 + 0.7 * (1.0 - e) ** 1.3, nu, nv)
            cv.mesh(grid, PETAL, edge=edge, clip=True)

    if t >= CENTER[0]:
        c = ease(phase(t, CENTER))
        ps = lerp(0.5, 1.25, c)
        hp, rp = 0.26 * ps, 0.12 * ps
        nt = max(10, int(rp * math.tau * cv.cpu * 1.2))
        pod = []
        for i in range(8):
            f = i / 7
            rr = rp * (0.35 + 0.65 * math.sin(math.pi * f * 0.85) ** 0.7) * (1.0 - f ** 6)
            pod.append([head(rr * math.cos(a), hp * (f + 0.15 * f ** 6), rr * math.sin(a))
                         for a in (math.tau * j / nt for j in range(nt + 1))])
        cv.mesh(pod, POD)

        for a, rj, hj in STAMENS:
            rr = (0.08 + 0.29 * c) * rj
            floor = 0.06 + max(0.0, rr - 0.06) / math.tan(max(opening, 0.3))
            yy = max(0.06 + 0.17 * c * hj, floor)
            ca, sa = math.cos(a), math.sin(a)
            cv.plot(head(rr * 0.6 * ca, yy * 0.55, rr * 0.6 * sa), FILAMENT, "'")
            cv.plot(head(rr * ca, yy, rr * sa), ANTHER, "o" if hj > 0.5 else "*", 1e-4)


def main():
    if os.name == "nt":
        os.system("")  # handling ANSI on Windows 10+
    out = sys.stdout
    out.write("\x1b[?1049h\x1b[?25l\x1b[2J")
    try:
        cv, size, start = None, None, time.perf_counter()
        while True:
            now = time.perf_counter()
            cur = shutil.get_terminal_size()
            if cur != size:
                size = cur
                cv = Canvas(max(20, cur.columns - 1), max(10, cur.lines))
                out.write("\x1b[2J")
            draw(cv, (now - start) % CYCLE)
            out.write(cv.frame() + "\x1b[0m")
            out.flush()
            time.sleep(max(0.0, 1.0 / FPS - (time.perf_counter() - now)))
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        out.flush()


if __name__ == "__main__":
    main()
