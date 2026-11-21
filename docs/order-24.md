# Order 24 — Giao diện demo tĩnh

Cập nhật ngày **21/11/2026** từ WordPress Laragon. Bản xuất gồm Trang chủ và các thành phần dùng chung trên 60 tệp HTML. [Demo đang phát](https://tahieu98.github.io/sobi-packaging-demo/)

## Giao diện và mã nguồn

| Thành phần | Giao diện và vị trí mã |
| --- | --- |
| Dải thông điệp dưới banner | `index.html` chứa hai thông điệp và hai icon, gồm **Sản xuất & in theo yêu cầu nhãn hiệu**. `assets/theme/home-audit.css` căn hai dòng theo chiều rộng và thêm vạch tím từ 768 px. Hai icon dùng mask trong `assets/css/base.css`, tương ứng với icon túi giấy và nhãn trong WordPress. |
| Form báo giá | `.sobi-quote` dùng viền cam 2 px ở cả `index.html` và `lien-he/index.html`. Từ 768 đến 1199 px, ảnh và chữ giới thiệu ở Trang chủ chia đôi hàng, form full width phía dưới. `assets/theme/conversion.css` định kiểu form và CTA. |
| Nút tư vấn và footer | **Gửi yêu cầu tư vấn** trỏ tới `lien-he/index.html` và rộng bằng hai thẻ lợi ích. **Nhận báo giá** ở footer rộng 200 px khi đủ bốn icon 44 px với khoảng cách 8 px. Hai nút và nút gửi form dùng tím `#2d1947` chữ trắng. |
| Liên hệ nhanh | Thanh dưới dùng `assets/theme/quick-contact.css`, luôn hiện dưới 768 px, kể cả trên vùng form. Màu tím, chữ và icon chức năng trắng, điểm nhấn cam khi tương tác. Logo Messenger và Zalo tải từ `assets/theme/icons/`. `assets/theme/quick-contact.js` xử lý cụm desktop. |

## Tái xuất và kiểm chứng

Chạy `python tools/export_demo.py --sync-audit` khi WordPress nguồn tại `http://sobi-packaging.test/` đang chạy. Lệnh lấy header, footer, liên hệ nhanh, nội dung Trang chủ và gợi ý form Liên hệ từ HTTP công khai. Lệnh cập nhật asset Sobi, bao gồm logo Messenger, và gắn mã SHA256 rút gọn vào URL CSS/JS. Nội dung chính của các trang biên tập khác được giữ trong HTML hiện có. [Công cụ xuất](../tools/export_demo.py)

`assets/js/demo.js` mô phỏng kết quả báo giá trong trình duyệt và hỗ trợ điền sẵn loại bao bì, ứng dụng hoặc tên mẫu. WordPress dùng CMS và xử lý báo giá phía máy chủ. Các URL điều hướng và tài nguyên của demo dùng đường dẫn tương đối để chạy ở thư mục dự án GitHub Pages.

- Kiểm tra tĩnh ở preview xác nhận 60 tệp HTML, 5.456 tham chiếu nội bộ hợp lệ và MP4 trùng với nguồn Laragon. Preview trả HTTP 206 cho yêu cầu byte-range.
- Chromium kiểm tra tại 320, 390, 549, 767, 768, 849, 1024, 1194, 1200 và 1440 px. Mép nút tư vấn khớp cụm thẻ và mép nút footer khớp hàng icon. Thanh mobile hiển thị khi mở trang, khi chuyển đến form và trên sáu route đại diện với JavaScript bật và tắt.
- Đã kiểm tra điền sẵn tại Liên hệ và gửi thử trên Trang chủ. Trình duyệt hiển thị kết quả mô phỏng mà không phát sinh yêu cầu gửi form.

Xem [hướng dẫn mở demo](../README.md) và [báo cáo bố cục của các đợt trước](layout-parity.md).
