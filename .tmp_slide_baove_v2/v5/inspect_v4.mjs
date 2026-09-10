import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "C:/Users/Admin/Downloads/DoAn/Slide_BaoVe_DoAnTotNghiep_v4.pptx";
const out = "C:/Users/Admin/Documents/GitHub/GraduationProject/.tmp_slide_baove_v2/v5/v4-inspect";

async function saveBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(out, { recursive: true });
const deck = await PresentationFile.importPptx(await FileBlob.load(source));
console.log("slides=", deck.slides.items.length);
console.log("layouts=", deck.layouts.items.map(l => l.name).join(" | "));
const inspect = await deck.inspect({
  kind: "slide,textbox,shape,image,table,chart,notes,layout",
  include: "id,slide,name,title,text,textPreview,textChars,textLines,bbox,bboxUnit,isPlaceholder,placeholders,rows,cols,chartType",
  maxChars: 200000,
});
await fs.writeFile(`${out}/v4-inspect.ndjson`, inspect.ndjson);
await saveBlob(`${out}/v4-montage.webp`, await deck.export({ format: "webp", montage: true, scale: 1 }));
