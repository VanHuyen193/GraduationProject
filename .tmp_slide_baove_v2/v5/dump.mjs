import fs from "node:fs";
const R = "v4unz";
const rd = p => fs.readFileSync(`${R}/${p}`, "utf8");
const EMU = 914400;
const pres = rd("ppt/presentation.xml");
const prels = rd("ppt/_rels/presentation.xml.rels");
const relMap = Object.fromEntries([...prels.matchAll(/Id="([^"]+)"[^>]*Target="([^"]+)"/g)].map(m=>[m[1],m[2]]));
const order = [...pres.matchAll(/<p:sldId[^>]*r:id="([^"]+)"/g)].map(m=>relMap[m[1]]);
for (let i=0;i<order.length;i++) {
  const path = "ppt/" + order[i].replace(/^\.\.\//,"");
  const base = path.split("/").pop();
  const rels = rd(`ppt/slides/_rels/${base}.rels`);
  const layout = /Target="\.\.\/slideLayouts\/([^"]+)"/.exec(rels)?.[1];
  const lay = rd(`ppt/slideLayouts/${layout}`);
  const layName = /<p:cSld[^>]*name="([^"]*)"/.exec(lay)?.[1];
  const layRels = rd(`ppt/slideLayouts/_rels/${layout}.rels`);
  const master = /Target="\.\.\/slideMasters\/([^"]+)"/.exec(layRels)?.[1];
  const xml = rd(path);
  console.log(`\n===== SLIDE ${i+1}  [${base}]  layout=${layout} "${layName}"  master=${master}`);
  const shapes = [...xml.matchAll(/<p:(sp|pic|graphicFrame|grpSp)>([\s\S]*?)<\/p:\1>/g)];
  // simpler: split on <p:sp> etc is unreliable for nesting; just list names + offsets + text
  const names = [...xml.matchAll(/<p:cNvPr id="\d+" name="([^"]*)"/g)].map(m=>m[1]);
  console.log("shapes:", names.join(" | "));
  const offs = [...xml.matchAll(/<a:off x="(-?\d+)" y="(-?\d+)"\/><a:ext cx="(\d+)" cy="(\d+)"/g)].map(m=>`(${(m[1]/EMU).toFixed(2)},${(m[2]/EMU).toFixed(2)},${(m[3]/EMU).toFixed(2)}x${(m[4]/EMU).toFixed(2)})`);
  console.log("boxes:", offs.join(" "));
  const txt = [...xml.matchAll(/<a:t>([^<]*)<\/a:t>/g)].map(m=>m[1]).join(" ¶ ");
  console.log("text:", txt.slice(0,1200));
  const imgs = [...rels.matchAll(/Target="\.\.\/media\/([^"]+)"/g)].map(m=>m[1]);
  if (imgs.length) console.log("media:", imgs.join(","));
  const ch = [...rels.matchAll(/Target="\.\.\/charts\/([^"]+)"/g)].map(m=>m[1]);
  if (ch.length) console.log("charts:", ch.join(","));
}
