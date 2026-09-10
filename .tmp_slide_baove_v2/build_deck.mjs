import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const root = "C:/Users/Admin/Documents/GitHub/GraduationProject/.tmp_slide_baove_v2";
const input = `${root}/template-starter.pptx`;
const output = `${root}/bao-ve-do-an-hoan-chinh.pptx`;
const previewDir = `${root}/final-preview`;
const layoutDir = `${root}/final-layout`;

async function saveBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

function toParagraphs(text) {
  return text.split("\n").map((line) => {
    if (line.startsWith("• ")) {
      return { bulletCharacter: "", runs: [line] };
    }
    return { bulletCharacter: "", runs: [line || " "] };
  });
}

const slides = [
  {
    layout: "Title Slide",
    title: "HỌC TĂNG CƯỜNG\nUNITY ML-AGENTS",
    body: "ĐỒ ÁN TỐT NGHIỆP\nĐề tài: Học tăng cường để tối ưu hóa khả năng tương tác của AI trong game\nVăn Thị Minh Huyền — 22010329\nGVHD: ThS. Nguyễn Văn Sơn | Đại học Phenikaa — 2026",
    source: "Đồ_án_tốt_nghiệp/main.tex",
  },
  {
    layout: "Title and Content",
    title: "Bài toán đặt ra",
    body: "• Thuật toán RL đã được đóng gói trong nhiều thư viện.\n• Phần khó là đặc tả môi trường 3D: quan sát, hành động, reward và cơ chế game.\n• Môi trường sai thường không báo lỗi — nó âm thầm dạy agent một hành vi sai.\n\nMục tiêu là tạo môi trường vừa học được, vừa kiểm chứng được.",
    source: "Đồ_án_tốt_nghiệp/sec_abstract.tex; sec6.tex",
  },
  {
    layout: "Title and Content",
    title: "Mục tiêu và đóng góp",
    body: "• Xây dựng 3 môi trường RL ba chiều trên Unity ML-Agents.\n• Kiểm chứng bằng 5 thuật toán: PPO, SAC, MA-POCA, MAPPO và DQN.\n• Đóng gói môi trường, 15 cấu hình và Editor tools để tái sử dụng.\n• Xây ứng dụng demo nạp trực tiếp các mô hình ONNX đã huấn luyện.",
    source: "Đồ_án_tốt_nghiệp/sec7.tex",
  },
  {
    layout: "Title and Content",
    title: "Quy trình triển khai",
    body: "Unity Environment  →  ML-Agents Trainer  →  TensorBoard  →  ONNX  →  Ứng dụng demo\n\n• MAPPO và DQN được bổ sung dưới dạng trainer mở rộng.\n• Kết quả huấn luyện được xuất tự động để số liệu, biểu đồ và demo luôn thống nhất.",
    source: "Đồ_án_tốt_nghiệp/sec5.tex; sec6_5_app.tex",
  },
  {
    layout: "Section Header",
    title: "Bốn nguyên tắc thiết kế",
    body: "1. Bám theo quỹ đạo lời giải mẫu.\n2. Ưu tiên reward sự kiện hoặc thế năng; tránh cộng dồn vô kiểm soát.\n3. Giữ tổng reward phụ nhỏ hơn reward mục tiêu.\n4. Sửa cơ chế hoặc curriculum trước khi tăng hệ số reward.",
    source: "Đồ_án_tốt_nghiệp/sec5.tex, mục 3.1.4",
  },
  {
    layout: "Title and Content",
    title: "Football Table",
    body: "• 60 quan sát: bóng, 4 thanh gạt đội nhà và 4 thanh gạt đối thủ.\n• 8 hành động liên tục: trượt và xoay cho mỗi thanh gạt.\n• Reward: +5 ghi bàn; −1 thủng lưới; −1/3000 mỗi bước.\n• Tỉ lệ +5/−1 làm mọi cơ hội ghi bàn đều đáng thử; phạt thời gian tối đa chỉ bằng 1.",
    source: "Đồ_án_tốt_nghiệp/sec5.tex, mục 3.3",
  },
  {
    layout: "Title and Content",
    title: "Capture The Flag",
    body: "• 61 quan sát = 5 cờ logic + 7 tia cảm biến × 8 giá trị; 7 hành động rời rạc.\n• Reward nhóm +1 khi cùng đến đích; +0,5 mỗi lần vượt cổng; PBRS κ = 0,01.\n• Các reward theo bước chuẩn hóa theo N = 100.000 để không lấn reward mục tiêu.\n• Ân hạn cửa 1 giây không đủ để một agent tự vượt cổng → phải phối hợp thật.",
    source: "Đồ_án_tốt_nghiệp/sec5.tex, mục 3.4",
  },
  {
    layout: "Title and Content",
    title: "Cross The Road",
    body: "• 132 quan sát = tọa độ agent/đích + 21 tia cảm biến × 6 giá trị.\n• 4 hành động rời rạc: đứng yên, trái, phải, tiến.\n• Reward: +1 đến đích; −0,025 va chạm; curiosity 0,02.\n• Phạt −0,025 đặt ngưỡng thành công ở 2,4%, tránh chính sách đứng yên vĩnh viễn.",
    source: "Đồ_án_tốt_nghiệp/sec5.tex, mục 3.5",
  },
  {
    layout: "Title and Content",
    title: "Thiết kế thực nghiệm",
    body: "• 5 thuật toán × 3 môi trường = 15 lần huấn luyện.\n• Ngân sách: Football 1,60M | Capture The Flag 1,70M | Cross The Road 2,00M bước.\n• Trong từng môi trường, các thuật toán dùng cùng ngân sách.\n• Nghiệm thu: học được • phân biệt được • không tạo lối tắt.",
    source: "Đồ_án_tốt_nghiệp/sec5.tex; sec6.tex",
  },
  {
    layout: "Title and Content",
    title: "Kết quả Football Table",
    body: "• Bốn thuật toán self-play tăng ELO từ 36 đến 64 điểm.\n• Kết quả cuối: MAPPO 1260 | PPO 1259 | SAC 1254 | MA-POCA 1237.\n• ELO khởi tạo xấp xỉ 1200; cơ chế self-play hoạt động đúng.\n• Tuy nhiên dải ELO hẹp → chưa phân biệt rõ hiệu năng nhóm dẫn đầu.",
    source: "Đồ_án_tốt_nghiệp/sec6.tex; sec7.tex",
  },
  {
    layout: "Title and Content",
    title: "Kết quả Capture The Flag",
    body: "• PPO, MA-POCA, MAPPO và DQN đạt 0,800–0,840.\n• SAC dừng ở 0,183; reward dao động và episode chạm trần thời gian.\n• Entropy SAC sụp rồi bật về cực đại; curiosity cao hơn hẳn nhóm còn lại.\n• Thất bại này phù hợp với bài toán hợp tác có reward nhóm và curriculum.",
    source: "Đồ_án_tốt_nghiệp/sec6.tex; sec7.tex",
  },
  {
    layout: "Title and Content",
    title: "Cross The Road",
    body: "• SAC dẫn đầu với reward cuối 0,846; DQN đạt 0,336.\n• MAPPO đạt 0,835; phổ kết quả rộng hơn hai môi trường còn lại.\n• Cùng ngân sách bước: SAC mất khoảng 139 phút, PPO khoảng 48 phút.\n• Hiệu quả mẫu phụ thuộc cả cấu hình cập nhật và chi phí tính toán.",
    source: "Đồ_án_tốt_nghiệp/sec6.tex; sec7.tex",
  },
  {
    layout: "Section Header",
    title: "Thông điệp chính",
    body: "Cùng SAC: 0,846 ở Cross The Road nhưng 0,183 ở Capture The Flag.\n\nChênh lệch giữa các môi trường lớn hơn chênh lệch giữa các thuật toán trong cùng môi trường.",
    source: "Đồ_án_tốt_nghiệp/sec7.tex",
  },
  {
    layout: "Title and Content",
    title: "Ứng dụng demo",
    body: "• Nạp trực tiếp 15 mô hình ONNX vào Unity.\n• Ba chế độ: người chơi, agent tự chơi và chơi cùng agent.\n• Tab THÔNG SỐ và SO SÁNH đọc tự động kết quả training.\n• Quan sát hành vi thực tế giúp phát hiện lỗi đặc tả mà reward curve có thể che giấu.",
    source: "Đồ_án_tốt_nghiệp/sec6_5_app.tex; sec7.tex",
  },
  {
    layout: "Title and Content",
    title: "Hạn chế và hướng phát triển",
    body: "• Mỗi tổ hợp hiện có một seed → chưa đủ cơ sở thống kê cho chênh lệch nhỏ.\n• Football Table và Capture The Flag cần tăng độ khó để tăng độ phân giải.\n• Kiểm chứng giả thuyết SAC–CTF bằng replay buffer tách theo bài học.\n• Lặp lại 15 thí nghiệm trên nhiều seed; mở rộng DreamerV3 hoặc QMIX.",
    source: "Đồ_án_tốt_nghiệp/sec7.tex",
  },
  {
    layout: "Title Slide",
    title: "KẾT LUẬN",
    body: "Ba môi trường 3D, 15 cấu hình huấn luyện và ứng dụng demo đã được đóng gói để tái sử dụng.\n\nĐầu tư vào đặc tả, reward và kiểm chứng môi trường là điều kiện để RL trong game đáng tin cậy.\n\nXin cảm ơn Hội đồng!",
    source: "Đồ_án_tốt_nghiệp/sec7.tex",
  },
];

const deck = await PresentationFile.importPptx(await FileBlob.load(input));
if (deck.slides.items.length !== slides.length) {
  throw new Error(`Expected ${slides.length} starter slides, received ${deck.slides.items.length}.`);
}

const layouts = new Map(deck.layouts.items.map((layout) => [layout.name, layout]));
for (let i = 0; i < slides.length; i += 1) {
  const spec = slides[i];
  const slide = deck.slides.items[i];
  const layout = layouts.get(spec.layout);
  if (!layout) throw new Error(`Missing template layout: ${spec.layout}`);
  slide.setLayout(layout);
  slide.placeholders.getItem("title").text = spec.title;
  const bodyType = spec.layout === "Title Slide"
    ? "subtitle"
    : spec.layout === "Title and Content"
      ? "content placeholder 2"
      : "body";
  slide.placeholders.getItem(bodyType).text = toParagraphs(spec.body);
  slide.placeholders.getItem("dateTime").text = "2026";
  slide.placeholders.getItem("footer").text = "Đồ án tốt nghiệp";
  slide.placeholders.getItem("slideNumber").text = String(i + 1);
  slide.speakerNotes.textFrame.setText(`[Sources]\n- Nội bộ: ${spec.source}\n[/Sources]`);
  slide.speakerNotes.setVisible(true);
}

await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });
for (let i = 0; i < deck.slides.items.length; i += 1) {
  const slide = deck.slides.items[i];
  const n = String(i + 1).padStart(2, "0");
  await saveBlob(`${previewDir}/slide-${n}.png`, await deck.export({ slide, format: "png", scale: 1 }));
  await saveBlob(`${layoutDir}/slide-${n}.layout.json`, await deck.export({ slide, format: "layout" }));
}
await saveBlob(`${root}/final-montage.webp`, await deck.export({ format: "webp", montage: true, scale: 1 }));
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(output);
console.log(output);
