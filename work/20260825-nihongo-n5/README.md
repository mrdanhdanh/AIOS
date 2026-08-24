# NHẬP MÔN TIẾNG NHẬT N5

Website tĩnh học tiếng Nhật trình độ N5, chạy hoàn toàn offline trên trình duyệt,
không phụ thuộc thư viện ngoài (vanilla HTML/CSS/JS).

## Nội dung
- **Hiragana / Katakana**: bảng chữ cái đầy đủ (cơ bản, dakuten, ghép).
- **Chào hỏi**: câu giao tiếp hàng ngày kèm romaji và nghĩa.
- **Số đếm**: 0–10, chục, trăm, nghìn.
- **Từ vựng**: màu sắc, gia đình, đồ ăn, thời gian, động từ, tính từ.
- **Ngữ pháp**: 10 điểm ngữ pháp N5 cốt lõi.
- **Kiểm tra**: trắc nghiệm nhiều lựa chọn, chấm điểm trực tiếp.

## Cách chạy
Mở trực tiếp `index.html` bằng trình duyệt, hoặc phục vụ cục bộ:

```bash
python -m http.server 8000 --directory work/20260825-nihongo-n5
# truy cập http://localhost:8000
```

## Cấu trúc
```
work/20260825-nihongo-n5/
  index.html        # giao diện chính
  css/style.css     # giao diện
  js/data.js        # nội dung học (N5_DATA)
  js/app.js         # logic hiển thị & kiểm tra
  README.md
```

Được tạo tự động bởi AIOS Planner (không tham khảo source cũ).
