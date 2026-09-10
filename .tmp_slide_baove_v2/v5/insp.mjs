import fs from "node:fs";
const R = "C:/Users/Admin/Documents/GitHub/GraduationProject/.tmp_slide_baove_v2/v5/v4unz";
const rd = p => fs.readFileSync(`${R}/${p}`, "utf8");
const pres = rd("ppt/presentation.xml");
console.log("sldSz:", /<p:sldSz[^>]*>/.exec(pres)?.[0]);
console.log("masters:", [...pres.matchAll(/<p:sldMasterId[^>]*r:id="([^"]+)"/g)].map(m=>m[1]).join(","));
const prels = rd("ppt/_rels/presentation.xml.rels");
console.log(prels.split("><").filter(s=>s.includes("slideMaster")).join("\n"));
// theme list
for (const f of fs.readdirSync(`${R}/ppt/theme`)) {
  const t = rd(`ppt/theme/${f}`);
  const name = /<a:theme[^>]*name="([^"]*)"/.exec(t)?.[1];
  const clr = [...t.matchAll(/<a:(dk1|lt1|dk2|lt2|accent1|accent2|accent3|accent4|accent5|accent6|hlink|folHlink)>\s*<a:(?:srgbClr val|sysClr[^>]*lastClr)="([0-9A-Fa-f]{6})"/g)].map(m=>`${m[1]}=${m[2]}`).join(" ");
  const maj = /<a:majorFont>\s*<a:latin typeface="([^"]*)"/.exec(t)?.[1];
  const min = /<a:minorFont>\s*<a:latin typeface="([^"]*)"/.exec(t)?.[1];
  console.log(`${f} :: ${name} :: ${maj}/${min} :: ${clr}`);
}
