import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "C:/Users/Admin/Downloads/DoAn/Presentation1.pptx";
const out = "C:/Users/Admin/Documents/GitHub/GraduationProject/.tmp_slide_baove_v2/manual-inventory";

async function saveBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(out, { recursive: true });
const deck = await PresentationFile.importPptx(await FileBlob.load(source));
const inspect = await deck.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  include: "id,slide,name,title,text,textPreview,textChars,textLines,bbox,bboxUnit,isPlaceholder,placeholders,rows,cols,chartType",
  maxChars: 20000,
});
await fs.writeFile(`${out}/template-inspect.ndjson`, inspect.ndjson);
for (let i = 0; i < deck.slides.items.length; i += 1) {
  const slide = deck.slides.items[i];
  await saveBlob(`${out}/source-slide-${String(i + 1).padStart(2, "0")}.png`, await deck.export({ slide, format: "png", scale: 1 }));
  await saveBlob(`${out}/source-slide-${String(i + 1).padStart(2, "0")}.layout.json`, await deck.export({ slide, format: "layout" }));
}
console.log(`slides=${deck.slides.items.length}`);
