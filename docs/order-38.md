# Order 38 — Danh mục trang Sản phẩm và header mobile

Cập nhật ngày 26/11/2026 trên WordPress local (Laragon) và bản demo HTML/CSS/JS.

## 1. Thanh danh mục trên trang Sản phẩm

- `/san-pham/` (`core/includes/catalog.php`, shortcode `sobi_catalog`): thanh `nav.sobi-filter` „Nhóm sản phẩm" hiển thị **Tất cả** và đủ 7 danh mục WooCommerce cấp 1, cùng thứ tự và nhãn với menu **Danh mục** trên header: Giấy kraft, Túi giấy & Túi Tết, Hộp giấy & Hộp quà, Bao bì khác, Túi cửa sổ, Túi giấy kraft, Túi Ivory. Danh mục chưa có mẫu vẫn được hiển thị.
- Chọn một danh mục cấp 1 (`?nhom=<slug>`) mở thêm thanh `nav.sobi-filter.sobi-filter--sub` „Danh mục thứ cấp" ngay bên dưới, trong cùng khung `.sobi-filter-stack`. Thanh này gồm **Tất cả** (về danh mục cấp 1) và các danh mục con trực tiếp. Chọn danh mục con giữ cả hai thanh, đánh dấu cấp 1 cha và cấp 2 đang chọn.
- Danh sách sản phẩm bên dưới vẫn lọc theo `nhom`; danh mục cấp 1 gồm cả sản phẩm của danh mục con. Ô tìm kiếm, phân trang và URL cũ giữ nguyên.
- Dữ liệu lấy trực tiếp từ taxonomy `product_cat` (nhãn ưu tiên term meta `sobi_category_menu_label`), nên thêm/sửa danh mục trong **Sản phẩm → Danh mục** sẽ tự cập nhật cả menu và thanh lọc.

## 2. Trang chủ trên mobile (≤ 767 px)

PC và tablet giữ nguyên bố cục.

- Thanh `.sobi-business-topbar` chỉ hiển thị địa chỉ và email trên một dòng; `.sobi-business-delivery` được ẩn trên mobile.
- Dải `.sobi-after-hero` có span `.sobi-after-hero-delivery` (icon + „Giao hàng toàn quốc") bên dưới hai thông điệp hiện có, chỉ hiển thị trên mobile. Nội dung nằm trong UX Block ID 388 trên Laragon; lệnh `infra/order-38-content.php` thêm span một lần và giữ bản cũ trong Revisions.
- Header: hàng 1 gồm logo và nút hotline `.sobi-header-hotline`; hàng 2 gồm ô tìm kiếm `.sobi-header-search` bên trái và nút **Danh mục** bên phải, cùng độ rộng cột với hotline, vừa khung `.sobi-mainbar`. Icon menu `.sobi-mobile-toggle` bị ẩn. CSS ở `header-audit.css`.

## 3. Thẻ quy trình (mọi kích thước màn hình)

`.sobi-steps-row > .col > .col-inner` dùng cùng nền gradient cam như thẻ `.sobi-social-benefits` (`home-audit.css`).

## 4. Bản demo

- Gỡ `.sobi-demo-banner` khỏi 67 trang, CSS `demo.css` và công cụ `tools/export_demo.py`.
- `assets/js/data.js` thêm `catalogGroups` (7 nhóm cấp 1 và danh mục con xuất từ WordPress); `assets/js/demo.js` dựng hai thanh lọc giống WordPress.
- Đồng bộ `sobi.css`, `header-audit.css`, `home-audit.css` và làm mới fingerprint tài nguyên.

## Kiểm chứng

Chrome 440/768/1280 px trên WordPress và demo: số thanh lọc, mục đang chọn và số mẫu khớp nhau giữa hai bản; topbar mobile cao 52 px một dòng; hotline và Danh mục cùng cột 157 px; không tràn ngang; PC/tablet giữ vị trí cũ; thẻ quy trình có gradient cam. PHP lint `catalog.php`, `node --check demo.js`.
