# Màu nền và thông điệp thương hiệu

## Order 37 — thanh thông tin doanh nghiệp

`.sobi-business-topbar` dùng nền đen `#262626`, chữ trắng và giữ nguyên text, icon, khoảng cách, chiều cao và responsive layout. Rule nằm trong `assets/theme/header-audit.css`, được nạp sau `conversion.css`; token `--sobi-blue` vẫn được giữ cho các thành phần CTA và focus khác.

Cập nhật 17/11/2026, Order 6. Nền cam dùng token `--sobi-orange-dark` trong `conversion.css` chuyển từ `#c04a0b` sang `#e26624` theo yêu cầu thương hiệu. Những nơi dùng token (strip sau hero, thẻ cam kết, các bước quy trình, footer và viền form báo giá) tự nhận cùng sắc độ mới. Gradient cùng nhóm và meta theme-color cũng dùng cam mới; tím, xanh CTA và cam logo giữ các mã hiện hành.

Trang chủ CMS ID 19 giữ cấu trúc Section/Row/Column/Text/Button native UX Builder. Hai cặp thông điệp được chia thành span văn bản, bố trí bằng gap CSS và tự xuống dòng khi thiếu chiều ngang; không còn span `.sobi-top-dot` hoặc dấu `·` trong dòng eyebrow hero. Nội dung là:

- GÓI GHÉM SẢN PHẨM / GỬI TRAO GIÁ TRỊ
- Bao bì giấy cho thương hiệu của bạn / Sản xuất & in theo yêu cầu

Dấu `/` trong danh sách trên chỉ biểu thị hai phần nội dung, không được chèn lên giao diện. Dấu phân cách của metadata bài viết/ngày tháng không thuộc thay đổi này.

Nguồn đang dùng: `website/wp-content/themes/sobi-flatsome/assets/conversion.css`, `assets/sobi.css`, `functions.php` và nội dung native của trang chủ. Nội dung CMS được sửa có giới hạn sau khi sao lưu bản trước và giữ revisions; không seed hoặc nhập lại SQL. Gói comprehensive đồng bộ theme/blueprint/tài liệu; bản HTML demo đồng bộ CSS/nội dung tương ứng, tiếp tục mô phỏng form độc lập.

Đã kiểm chứng WordPress và demo tại 390/768/1440/1920px: nền strip, bốn thẻ cam kết, bốn bước quy trình và footer đều trả RGB(226, 102, 36), không còn dấu chấm ở hai dòng thông điệp và không tràn ngang. PHP functions.php/JavaScript dữ liệu demo đã kiểm tra cú pháp. Không thay thông số form, menu, video hoặc nội dung bài Blog. Dữ liệu đo ở `appearance-verification.json`, ảnh WordPress tại `appearance-desktop.jpg`.
