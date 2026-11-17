# Danh mục thứ cấp trong demo — Order 8

Demo đã bổ sung 17 trang dưới `san-pham/`, tổng cộng 60 HTML. Mega menu trên toàn bộ trang dẫn đến danh mục riêng; CTA trong trang mới dẫn đến Liên hệ và điền sẵn loại bao bì/nội dung. Tìm kiếm toàn site đã có 17 trang mới.

Nội dung được xuất từ Page native UX Builder trên WordPress local. Không ghi đè thân bài 43 trang demo cũ hoặc dữ liệu sản phẩm/Blog. Các trang hộp/carton dùng khối thông tin khi chưa có ảnh đúng sản phẩm.

Công cụ `tools/export_demo.py --only san-pham/<slug>/` có thể xuất riêng trang và cập nhật menu dùng chung. URL CSS/JS có hash để tránh giữ cache cũ. Xuất toàn bộ không có `--only` sẽ thay nội dung các trang demo bằng bản CMS hiện tại; hãy xem diff trước khi commit.

Kết quả: 102 lượt trình duyệt (17 trang × 3 viewport × WordPress/demo), không tràn ngang hay ảnh hỏng được phát hiện; 34 lượt CTA điền sẵn đúng loại bao bì. Xem `subcategory-verification.json` và `static-verification.json`.
