# Mega-menu danh mục sản phẩm

Cập nhật 17/11/2026, Order 7. Khung dropdown giới hạn chiều cao theo phần viewport còn lại bên dưới nút Danh mục (chừa 16px đáy), tối đa 70vh. Khung ngoài không cuộn. Hai vùng `.sobi-mega-choices` và `.sobi-mega-content` cuộn dọc độc lập khi nội dung vượt chiều cao; danh mục ngắn đứng nguyên khi cuộn sản phẩm. Overscroll được giữ trong từng vùng.

Ở chiều rộng ≤700px, danh mục nằm thành hai cột phía trên, vùng danh mục giới hạn 160px/40% khung; sản phẩm cuộn phía dưới. Điều khiển phím mũi tên/Home/End giữ focus trong danh mục, không kéo trang nền. Khi đổi danh mục, danh sách chi tiết trở về đầu. Vùng sản phẩm có tên truy cập và nhận focus để cuộn bằng bàn phím. Escape/đóng ngoài tiếp tục hoạt động.

Nguồn: theme `assets/conversion.css` và `assets/sobi.js`. Không thay mapping sản phẩm, nội dung CMS hoặc form báo giá. Không có JavaScript, bố cục fallback dùng cơ chế cuộn toàn menu cũ để nội dung vẫn truy cập được.

Kiểm chứng: demo ở 390/700/768/1180/1440px và viewport cao 650px; menu nằm gọn trong màn hình, sản phẩm cuộn riêng. Fixture tạm 24 danh mục xác minh cuộn danh mục và phím End không dịch chuyển trang nền; fixture được xóa sau kiểm tra. Trên WordPress đã kiểm tra cuộn sản phẩm giữ nguyên tọa độ cột danh mục, đổi tab/reset, mở lại đúng focus và Escape. Ảnh tại `mega-menu-desktop.jpg`; số đo tại `mega-menu-verification.json`.
