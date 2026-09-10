# -*- coding: utf-8 -*-
"""Chụp thẳng thẻ biểu đồ của TensorBoard ra tệp PNG.

Điều khiển Chrome ở chế độ headless qua DevTools Protocol: mở đúng đường dẫn sâu của
TensorBoard, chờ thẻ biểu đồ dựng xong, nới thẻ ra cho vừa khổ slide rồi cắt đúng
khung của thẻ. Ảnh thu được là điểm ảnh do chính TensorBoard vẽ, không vẽ lại.

Chạy: C:\\Users\\Admin\\miniconda3\\python.exe tb_shot.py
"""
import base64
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.parse
import urllib.request

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(ROOT, "chrome-profile")
SHOTS = os.path.join(ROOT, "shots")
PORT = 9333


# ----------------------------------------------------------- WebSocket tối giản
class WS:
    """Chỉ đủ dùng cho DevTools Protocol: khung văn bản, có che dữ liệu, gộp mảnh."""

    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=90)
        key = base64.b64encode(os.urandom(16)).decode()
        path = u.path + ("?" + u.query if u.query else "")
        req = (f"GET {path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\n"
               "Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        if b"101" not in buf.split(b"\r\n")[0]:
            raise RuntimeError("bắt tay WebSocket hỏng: " + buf[:120].decode("latin1"))
        self.rest = buf.split(b"\r\n\r\n", 1)[1]
        self._id = 0

    def _read(self, n):
        while len(self.rest) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("mất kết nối")
            self.rest += chunk
        out, self.rest = self.rest[:n], self.rest[n:]
        return out

    def send(self, method, **params):
        self._id += 1
        payload = json.dumps({"id": self._id, "method": method,
                              "params": params}).encode()
        n = len(payload)
        head = bytes([0x81])
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(head + mask + masked)
        return self._id

    def _frame(self):
        b0, b1 = self._read(2)
        fin, opcode = b0 & 0x80, b0 & 0x0F
        n = b1 & 0x7F
        if n == 126:
            n = struct.unpack(">H", self._read(2))[0]
        elif n == 127:
            n = struct.unpack(">Q", self._read(8))[0]
        if b1 & 0x80:                       # máy chủ không che, nhưng cứ phòng
            mask = self._read(4)
            data = bytes(c ^ mask[i % 4] for i, c in enumerate(self._read(n)))
        else:
            data = self._read(n)
        return fin, opcode, data

    def recv(self):
        buf, op = b"", None
        while True:
            fin, opcode, data = self._frame()
            if opcode == 0x8:
                raise RuntimeError("máy chủ đóng kết nối")
            if opcode in (0x9, 0xA):        # ping / pong: bỏ qua
                continue
            if op is None:
                op = opcode
            buf += data
            if fin:
                return json.loads(buf.decode())

    def call(self, method, **params):
        want = self.send(method, **params)
        while True:
            msg = self.recv()
            if msg.get("id") == want:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})


# ------------------------------------------------------------------ tiện ích JS
JS_PREPARE = r"""
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const CARD_W = %(w)d, CARD_H = %(h)d;

  // chờ TensorBoard dựng xong thẻ biểu đồ
  let card = null;
  for (let i = 0; i < 80; i++) {
    const cs = [...document.querySelectorAll('card-view')]
      .filter(c => c.getBoundingClientRect().width > 10);
    if (cs.length) { card = cs[0]; break; }
    await sleep(400);
  }
  if (!card) return {err: 'không thấy thẻ biểu đồ nào'};

  // ctf_sac_v1 gồm một lần chạy tiếp từ checkpoint cũ nên trục bước không đơn điệu;
  // bật đúng tuỳ chọn của TensorBoard để nó tách thành hai đoạn thay vì nối thẳng.
  let partition = 'không thấy tuỳ chọn';
  for (const cb of document.querySelectorAll('mat-checkbox')) {
    if (!/Partition non-monotonic/i.test(cb.innerText || '')) continue;
    const inp = cb.querySelector('input');
    partition = inp.checked ? 'đã bật sẵn' : 'vừa bật';
    if (!inp.checked) { inp.click(); await sleep(1500); }
    break;
  }

  // Dọn phần điều khiển của giao diện, giữ lại đúng biểu đồ và bảng chú giải màu.
  // Chỉ ẩn bớt phần tử, không vẽ lại gì — điểm ảnh biểu đồ vẫn do TensorBoard sinh ra.
  const css = document.createElement('style');
  css.textContent = `
    button[aria-label="Fit line chart domains to data"],
    button[aria-label="Pin card"],
    button[aria-label="Toggle full size mode"],
    button[aria-label="More line chart options"],
    button[aria-label="Deselect fob"],
    .extent-edit-button, .fob, .fob-container, line.linked-time-fob,
    tb-data-table-header-cell:nth-child(n+3),
    tb-data-table-content-cell:nth-child(n+3) { display: none !important; }
    tb-data-table-header { display: none !important; }
    tb-data-table-content-row {
      display: flex !important; align-items: center !important; }
    tb-data-table-header-cell, tb-data-table-content-cell {
      flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;
      padding: 2px 10px !important; }
    card-view { box-shadow: none !important; border: 1px solid #e0e0e0 !important; }
  `;
  document.head.appendChild(css);

  // mở hết bảng chú giải để hiện đủ các lần chạy
  const exp = [...card.querySelectorAll('button')]
    .find(b => (b.getAttribute('aria-label') || '') === 'Expand Table');
  if (exp) { exp.click(); await sleep(400); }

  // bỏ mốc chọn bước (đường đứt nét và thẻ số) — chỉ là con trỏ của giao diện
  const hideFob = () => {
    for (const el of card.querySelectorAll('*')) {
      const cn = typeof el.className === 'string'
        ? el.className : (el.className && el.className.baseVal) || '';
      if (/fob|linked-time/i.test(cn)) el.style.setProperty('display', 'none', 'important');
    }
    for (const b of card.querySelectorAll('button')) {
      const al = b.getAttribute('aria-label') || '';
      if (/Table$/.test(al)) b.style.setProperty('display', 'none', 'important');
    }
    for (const b of card.querySelectorAll('.sorting-icon-container')) {
      b.style.setProperty('display', 'none', 'important');
    }
  };
  hideFob();

  // nới thẻ ra cho vừa khổ slide; biểu đồ của TensorBoard tự vẽ lại theo kích thước mới
  const grid = card.parentElement;
  if (grid) {
    grid.style.setProperty('display', 'block', 'important');
    grid.style.setProperty('grid-template-columns', 'none', 'important');
  }
  card.style.setProperty('width', CARD_W + 'px', 'important');
  card.style.setProperty('height', CARD_H + 'px', 'important');
  card.style.setProperty('max-width', 'none', 'important');
  window.dispatchEvent(new Event('resize'));
  await sleep(%(settle)d);

  hideFob();
  card.scrollIntoView({block: 'start'});
  await sleep(600);

  // cắt sát đáy bảng chú giải thay vì theo chiều cao thẻ, tránh khoảng trắng thừa
  const r = card.getBoundingClientRect();
  const rows = [...card.querySelectorAll('tb-data-table-content-row')];
  const legend = rows.map(row => {
    const dot = row.querySelector('tb-data-table-content-cell *');
    const name = (row.innerText || '').trim().split(/\s+/)[0];
    return {name: name, color: dot ? getComputedStyle(dot).backgroundColor : ''};
  });
  const bottom = rows.length
    ? Math.max(...rows.map(e => e.getBoundingClientRect().bottom)) + 14
    : r.bottom;
  return {x: r.x + scrollX, y: r.y + scrollY, w: r.width,
          h: Math.min(r.height, bottom - r.top), partition: partition, legend: legend,
          text: card.innerText.replace(/\s+/g, ' ').slice(0, 300)};
})()
"""


def shot(ws, url, out, tag_w=960, tag_h=700, settle=3000):
    ws.call("Page.navigate", url=url)
    time.sleep(4.0)
    res = ws.call("Runtime.evaluate",
                  expression=JS_PREPARE % {"w": tag_w, "h": tag_h, "settle": settle},
                  awaitPromise=True, returnByValue=True)
    if "value" not in res.get("result", {}):
        raise RuntimeError(json.dumps(res, ensure_ascii=False)[:1200])
    val = res["result"]["value"]
    if "err" in val:
        raise RuntimeError(val["err"])
    clip = {"x": val["x"], "y": val["y"], "width": val["w"], "height": val["h"],
            "scale": 3}
    png = ws.call("Page.captureScreenshot", format="png", clip=clip,
                  captureBeyondViewport=True)["data"]
    with open(out, "wb") as fh:
        fh.write(base64.b64decode(png))
    print(f"  → {os.path.basename(out)}  "
          f"{val['w']:.0f}×{val['h']:.0f} css  ·  {os.path.getsize(out)/1024:.0f} KB")
    print(f"    tách trục không đơn điệu: {val.get('partition')}")
    for e in val.get("legend", []):
        print(f"      màu {e['name']:10s} = {e['color']}")
    print(f"    nội dung thẻ: {val['text'][:160]}")


def main():
    os.makedirs(SHOTS, exist_ok=True)
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE}",
         "--window-size=1700,1100", "--no-first-run", "--no-default-browser-check",
         "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(60):
            try:
                with urllib.request.urlopen(
                        f"http://127.0.0.1:{PORT}/json/list", timeout=2) as r:
                    tabs = json.load(r)
                cand = [t for t in tabs if t.get("type") == "page"]
                if cand:
                    ws_url = cand[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                time.sleep(0.5)
        if not ws_url:
            raise RuntimeError("Chrome không mở được cổng gỡ lỗi")

        ws = WS(ws_url)
        ws.call("Page.enable")
        ws.call("Runtime.enable")
        ws.call("Emulation.setDeviceMetricsOverride", width=1700, height=1100,
                deviceScaleFactor=1, mobile=False)

        jobs = [
            ("football_elo", 6011, "Self-play/ELO", 0.6),
            ("ctf_reward", 6012, "^Environment/Cumulative Reward$", 0.6),
            ("ctr_reward", 6013, "^Environment/Cumulative Reward$", 0.6),
        ]
        for name, port, tag, sm in jobs:
            q = urllib.parse.urlencode({"tagFilter": tag, "smoothing": sm})
            url = f"http://127.0.0.1:{port}/?{q}#timeseries"
            print(f"» {name}  ({url})")
            shot(ws, url, os.path.join(SHOTS, f"tb_{name}.png"))
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
