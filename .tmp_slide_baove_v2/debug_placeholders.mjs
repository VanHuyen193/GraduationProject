import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const deck = await PresentationFile.importPptx(await FileBlob.load("C:/Users/Admin/Documents/GitHub/GraduationProject/.tmp_slide_baove_v2/template-starter.pptx"));
const layout = deck.layouts.items.find((item) => item.name === "Title and Content");
const slide = deck.slides.items[1];
slide.setLayout(layout);
console.log(JSON.stringify(slide.placeholders.summary(), null, 2));
console.log(slide.placeholders.items.map((item) => ({ name: item.name, type: item.placeholder?.type, text: item.text?.text ?? "" })));
