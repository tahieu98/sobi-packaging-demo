# Bố cục hero trang chủ

Điều chỉnh ngày 17/11/2026 trong bản demo HTML. CSS nằm ở `assets/css/demo.css`, nạp sau CSS giao diện gốc; công cụ export giữ nguyên tệp override này.

Trên PC từ 1181px, hero nằm trong khung căn giữa rộng tối đa 1600px. Khi màn hình hẹp hơn, khung chừa tối thiểu 40px mỗi bên. Hai cột bằng nhau, cách nhau 40px và căn giữa theo chiều dọc. Cột chữ sử dụng toàn bộ chiều rộng được chia, thay cho giới hạn 680px trước đây tạo khoảng trống lớn ở giữa.

Bố cục áp dụng theo class `.sobi-hero-video`, `.sobi-hero-layout` và `.sobi-hero-copy`, không phụ thuộc ID ngẫu nhiên của CMS. Ở tablet/mobile, video tiếp tục nằm trên nội dung theo bố cục một cột hiện có.

Đã đo bảy chiều rộng nội dung thực tế, từ 375 đến 2545px: không tràn ngang, lề ngoài bằng nhau; ở PC hai cột bằng nhau và khoảng cách đúng 40px. Ví dụ tại chiều rộng nội dung 1905px (viewport 1920px có scrollbar), mỗi cột 780px và hai lề đều 152,5px. Dữ liệu đo tại `hero-layout-verification.json`, ảnh desktop tại `screenshots/home-desktop.jpg`.
