# Sobi Packaging — demo HTML/CSS/JavaScript

[**Xem demo online**](https://tahieu98.github.io/sobi-packaging-demo/) · [Repository](https://github.com/tahieu98/sobi-packaging-demo)

Bản mô phỏng giao diện công khai của Sobi Packaging, cập nhật giao diện danh mục và thẻ sản phẩm theo Order 33 và Order 35 ngày 24/11/2026, cùng nền thanh thông tin doanh nghiệp theo Order 37 ngày 25/11/2026. Order 38 (26/11/2026): trang Sản phẩm có thanh danh mục hai cấp theo menu Danh mục, header/topbar mobile mới, thẻ quy trình gradient cam và không còn banner demo. Mở `index.html` trực tiếp bằng Chrome hoặc dùng preview bên dưới. Không cần WordPress, PHP, MySQL, npm hay bước build để xem demo.

## Mở bản demo

```sh
cd sobi-packaging-demo
python3 tools/serve.py
```

Mở http://localhost:4173/. Dừng bằng Ctrl+C trong cửa sổ Terminal đang chạy server. Nếu cổng đã có preview của phiên Codex này, mở URL trực tiếp; không cần chạy thêm server. Có thể chọn cổng khác bằng `python3 tools/serve.py --port 4174`.

Nhấp đúp `Start-Demo.command` để mở preview bằng Terminal trên macOS. Server thử nghiệm có hỗ trợ byte-range cho MP4. Cũng có thể mở `index.html` trực tiếp; clipboard và một số tính năng media có thể bị trình duyệt giới hạn ở địa chỉ file.

## Nội dung và tương tác

Order 40 xuất 17 danh mục WooCommerce và 33 mẫu sản phẩm, gồm 24 mẫu demo và chín mẫu có sẵn. Các danh mục và mẫu mới có thumbnail, mô tả và thông tin quy cách minh họa. Trang sản phẩm dùng `san-pham/{slug}/index.html`, danh mục con đi theo đường dẫn cha. Các đường dẫn cũ có trang chuyển hướng. [Manifest](docs/content-manifest.json).

Order 41 hiển thị một nhóm thẻ có ảnh cho danh mục con trên trang cha. Dòng **Danh mục con của…** nằm ngay trên nhóm thẻ. [Bao bì khác](bao-bi-khac/index.html) · [Túi giấy](tui-giay/index.html).

- Header/mobile menu, menu danh mục WooCommerce, điều khiển bằng phím/Escape, link social và nút về đầu trang.
- Trang Sản phẩm: tìm tên/mã, tìm không dấu, thanh danh mục cấp 1 (7 nhóm như menu Danh mục) và cấp 2 khi chọn nhóm, phân trang 8 mẫu/trang và trạng thái rỗng. Dữ liệu nhóm ở `catalogGroups` trong `assets/js/data.js`.
- Danh mục cấp cha có cột lọc trên PC, bảng lọc trên tablet và mobile, lưới 4/3/2 cột, sắp xếp và chế độ danh sách. Bộ lọc dùng dữ liệu catalogue đã xuất và chạy trong trình duyệt.
- Chi tiết mẫu: phóng ảnh, thông số, FAQ, chia sẻ/copy link, CTA điền sẵn tên mẫu.
- Giấy kraft: các anchor, bảng so sánh cuộn ngang trong khung và FAQ đóng/mở.
- Blog: 18 bài, lọc chuyên mục, tìm nội dung, phân trang 6 bài/trang, mục lục, bài liên quan và chia sẻ.
- Video MP4 homepage dùng file local; có controls, poster, autoplay tắt tiếng và fallback. Video mạng xã hội chỉ tải sau bấm, cần Internet và khả năng truy cập nền tảng tương ứng.
- Form báo giá: 12 loại bao bì, 34 tỉnh/thành, kích thước/số lượng, tổng hợp nhu cầu, prefill theo ứng dụng/sản phẩm, kiểm tra file (3 file, 8 MiB/file, 20 MiB tổng), consent và kết quả thử.
- Bình luận thử xuất hiện ngay trong phiên xem trên các bài Blog; không đăng lên website thật.

Form báo giá chỉ dựng bản tóm tắt trên thiết bị, không gửi email/lead/file đến Sobi, không lưu database và không giữ dữ liệu sau khi tải lại. Bình luận thử cũng không được đăng hoặc lưu lâu dài. Không mô phỏng khu vực wp-admin/UX Builder: đây là demo frontend công khai.

## Cấu trúc

- `index.html`, các thư mục route: trang HTML có sẵn nội dung.
- `assets/css/base.css`: grid/nút/form/accordion độc lập, thay runtime của parent theme.
- `assets/theme/`: CSS/ảnh/font/icon do dự án Sobi đang dùng; font kèm giấy phép OFL.
- `assets/media/`: media công khai được trang tham chiếu, bao gồm MP4.
- `assets/js/sobi.js`: tương tác giao diện từ dự án, đã bỏ gửi báo giá đến server.
- `assets/js/demo.js`: bộ lọc/tìm/phân trang/form/bình luận mô phỏng.
- `assets/js/category-archive.js` lọc danh mục từ URL và dữ liệu xuất từ WooCommerce. Có thể kết hợp **Kiểu túi giấy** và **Ngành hàng**. [Xem ví dụ Kraft và nông sản](tui-giay/index.html?kieu=tui-kraft&nganh=nong-san-trai-cay-hat).
- `assets/js/data.js`: dữ liệu công khai của sản phẩm/bài viết/trang.
- `tools/serve.py` mở bản xem trước. `tools/export_demo.py --sync-catalogue --catalogue-routes routes.json` đồng bộ catalogue từ website WordPress đang chạy và cần beautifulsoup4. Tạo `routes.json` bằng chế độ `export` của migration Order 40 trong repo WordPress. Các chức năng nhập và biên tập chạy trong CMS WordPress.
- `docs/github-pages-costs.md`: nghiên cứu chi phí và các phương án xuất bản.
- `docs/pages-workflow.yml.example`: workflow GitHub Pages mẫu, chưa được kích hoạt.

Đường dẫn tương đối hỗ trợ đặt toàn bộ demo tại root hoặc dưới `/sobi-packaging/` trên GitHub Pages. Mọi liên kết nội bộ trỏ đến tệp HTML, không gọi WordPress REST/admin-post. Không đưa thông tin đăng nhập, SQL, private quote files hoặc Flatsome parent vào thư mục này.

## Ghi nhận khi chuyển đổi

Trang Blog nguồn có phần danh sách trống tại thời điểm xuất lần đầu (hiện đã được sửa ở WordPress), trong khi ba chuyên mục vẫn trả đủ 18 bài. Demo dựng danh sách Blog bằng chính các thẻ bài viết công khai đó.

Lần xuất ban đầu thiếu thông tin liên hệ trong header/footer. Ngày 21/11/2026, cả 60 trang HTML đã nhận email, địa chỉ, hotline và liên kết mạng xã hội từ phần công khai của WordPress local.

Đợt rà soát ngày 21/11/2026 đồng bộ header, footer và liên hệ nhanh trên 60 trang. Trang chủ có nút báo giá nhanh, hiệu ứng ở phần chữ của thẻ mẫu túi và bốn bước quy trình. Cả hai form báo giá dùng gợi ý nhập từ website nguồn.

Order 24 cập nhật dải thông điệp, form viền cam, bố cục tablet, ba CTA tím và thanh liên hệ mobile ghim ở đáy trên toàn site. [Chi tiết thiết kế và kiểm chứng](docs/order-24.md)

Chạy `python tools/export_demo.py --sync-audit` để cập nhật các phần này từ các trang công khai tại `sobi-packaging.test`. Lệnh `python tools/export_demo.py --contacts-only` làm mới riêng thông tin liên hệ trong các thành phần dùng chung. Hai lệnh cần Python 3.10 trở lên và beautifulsoup4.

Order 32 đồng bộ 35 trang catalogue và sản phẩm, gồm danh mục Túi giấy kraft, phụ kiện điện thoại, F&B và các mẫu SDD02, TCS02, SM01. Danh mục cấp cha lấy nhóm lọc từ dữ liệu công khai hiện có tại thời điểm xuất. Các lựa chọn giá phụ thuộc bảng giá WooCommerce.

Order 33 cập nhật viền khối giới thiệu, nút Zalo, tiêu đề và các nhóm trong bộ lọc. Thẻ danh mục con xếp ảnh bên trái ở mọi kích thước. Danh mục liên quan hiển thị ảnh có sẵn và đổi màu khi tương tác. Trang chủ, Sản phẩm, danh mục cha, danh mục thứ cấp và chi tiết dùng chung kiểu thẻ sản phẩm.

Order 35 đổi trạng thái tương tác của thẻ danh mục con sang nền cam và chữ tím. Trạng thái này áp dụng cho hover, focus và chạm. Dòng Xem danh mục được bỏ khỏi các thẻ danh mục con.

Order 36 bỏ chú thích dưới banner video Trang chủ. Trình phát dùng đường dẫn MP4 tương đối trong bản demo và phát được trên GitHub Pages, máy chủ thử nghiệm và khi mở trực tiếp `index.html`.

Chạy `python tools/export_demo.py --sync-catalogue` để tái xuất từ WordPress local. Chế độ này đọc các trang, ảnh và mã giao diện công khai qua HTTP rồi lưu thành HTML, CSS và JavaScript.

Các trang Sample Page/Hello world cũ được giữ để tránh thiếu nội dung public, nhưng không đưa vào menu chính/danh sách Blog 18 bài. Nội dung/thông số mẫu vẫn là dữ liệu demo của dự án nguồn.

Đây là bản copy độc lập. Website XAMPP, database và gói bàn giao không bị sửa. Bản demo được quản lý trong repository public riêng `tahieu98/sobi-packaging-demo`. Repository WordPress `tahieu98/sobi-packaging` tiếp tục private; dữ liệu/backend của website thật không được đưa sang đây.

## Kết quả kiểm tra

Order 33 đã kiểm tra 67 trang và các liên kết tài nguyên dưới đường dẫn project. Chrome được dùng để kiểm tra bộ lọc, sắp xếp, chế độ danh sách, hộp thoại mobile và hiệu ứng thẻ bằng chuột, bàn phím và chạm ở các chiều rộng từ 320 đến 1440 px.

Order 32 đã kiểm tra các tuyến catalogue ở 8 độ rộng trên Chrome, từ 320 đến 1.440 px. Đã thử bộ lọc, sắp xếp, menu, FAQ, phóng ảnh và điền sẵn nội dung báo giá dưới đường dẫn project.

Xem [kết quả Order 24](docs/order-24.md#tái-xuất-và-kiểm-chứng) cho bố cục và tương tác trang chủ. Báo cáo ngày 17/11/2026 ghi lại 30 cặp đo desktop, tablet và mobile, gồm icon mũi tên, grid Liên hệ, bảng kraft, form và caption video. [Báo cáo so với WordPress](docs/layout-parity.md)

- Order 8: 60 tệp HTML trả HTTP 200; đã kiểm tra 5.274 tham chiếu local, không có đích bị thiếu. 17 trang danh mục mới được kiểm tra trên WordPress/demo ở 390/768/1440px; xem [chi tiết](docs/subcategory-pages.md).
- 12 trang đại diện × 390/768/1440 px: 36/36 lượt có một H1, không tràn ngang và không có ảnh hỏng được phát hiện.
- Đã thử menu/tab/Escape, menu mobile, tìm/lọc/phân trang/empty state, gallery, prefill sản phẩm, form báo giá/reset, chọn PNG/chặn TXT, FAQ, bình luận thử và copy link.
- Đã kiểm tra đường dẫn project `/sobi-packaging/` và 404 lồng nhiều cấp. MP4 có cùng SHA256 với nguồn; request byte-range trả HTTP 206 đúng độ dài.
- Báo cáo: `docs/static-verification.json`, `docs/browser-verification.json`; ảnh `docs/screenshots/home-desktop.jpg`.
- Chưa nghiệm thu trên Safari/thiết bị vật lý; video Facebook/YouTube bên ngoài phụ thuộc dịch vụ và kết nối. Quản trị WordPress/UX Builder, lưu database, email/CRM và xử lý file phía server thuộc website gốc, không nằm trong demo frontend.


## GitHub Pages

Repository này chỉ chứa demo. GitHub Pages phục vụ các tệp static từ nhánh `main`, thư mục gốc (`/`); không chạy WordPress/PHP hoặc công cụ Python. Đường dẫn public là https://tahieu98.github.io/sobi-packaging-demo/.

Khi cần cập nhật demo: sửa tệp, kiểm tra, commit và `git push origin main`. GitHub tự dựng lại Pages sau khi nhánh `main` được cập nhật. Đây là luồng riêng với repository WordPress và không triển khai vào XAMPP. Không cần npm, Git LFS, workflow custom hoặc dịch vụ video trả phí cho bản hiện tại.
