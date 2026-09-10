# -*- coding: utf-8 -*-
"""Dò cấu trúc DOM của thẻ biểu đồ TensorBoard để biết cần ẩn/mở những phần nào."""
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tb_shot import WS, CHROME, PROFILE, PORT  # noqa

JS = r"""
(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  let card = null;
  for (let i = 0; i < 60; i++) {
    const cs = [...document.querySelectorAll('card-view')]
      .filter(c => c.getBoundingClientRect().width > 10);
    if (cs.length) { card = cs[0]; break; }
    await sleep(400);
  }
  if (!card) return {err: 'no card'};
  await sleep(2500);
  const desc = el => el.tagName.toLowerCase() +
      (el.id ? '#' + el.id : '') +
      (el.className && el.className.baseVal === undefined && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\s+/).join('.') : '');
  const btns = [...card.querySelectorAll('button')].map(b => ({
      sel: desc(b), al: b.getAttribute('aria-label'), txt: b.innerText.trim().slice(0, 24),
      r: [Math.round(b.getBoundingClientRect().x), Math.round(b.getBoundingClientRect().y)]}));
  const heads = [...card.querySelectorAll('tb-data-table-header-cell')].map(h => ({
      sel: desc(h), txt: h.innerText.trim().slice(0, 20)}));
  const rows = [...card.querySelectorAll('tb-data-table-content-row')].map(r => r.innerText.replace(/\s+/g,' ').slice(0,60));
  const cells = [...card.querySelectorAll('tb-data-table-content-cell')].slice(0, 12).map(c => ({sel: desc(c), txt: c.innerText.trim().slice(0,16)}));
  const chips = [...card.querySelectorAll('*')].filter(e => e.children.length === 0 &&
      /^\d{6,7}$/.test((e.innerText||'').trim())).map(e => desc(e.parentElement) + ' > ' + desc(e));
  return {btns, heads, rows, cells, chips,
          tableH: (card.querySelector('tb-data-table')||{}).clientHeight};
})()
"""


def main():
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE}",
         "--window-size=1700,1100", "--no-first-run", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(60):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=2) as r:
                    tabs = [t for t in json.load(r) if t.get("type") == "page"]
                if tabs:
                    ws_url = tabs[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                time.sleep(0.5)
        ws = WS(ws_url)
        ws.call("Page.enable")
        ws.call("Runtime.enable")
        ws.call("Emulation.setDeviceMetricsOverride", width=1700, height=1100,
                deviceScaleFactor=1, mobile=False)
        ws.call("Page.navigate",
                url="http://127.0.0.1:6013/?tagFilter=%5EEnvironment%2FCumulative+Reward%24"
                    "&smoothing=0.6#timeseries")
        time.sleep(4)
        res = ws.call("Runtime.evaluate", expression=JS, awaitPromise=True,
                      returnByValue=True)
        print(json.dumps(res["result"]["value"], ensure_ascii=False, indent=1))
    finally:
        proc.terminate()


main()
