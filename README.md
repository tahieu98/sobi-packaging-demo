# Sobi Packaging — demo HTML/CSS/JavaScript

[**Xem demo online**](https://tahieu98.github.io/sobi-packaging-demo/) · [Repository](https://github.com/tahieu98/sobi-packaging-demo)

Bản mô phỏng giao diện công khai, dựng từ nội dung website Sobi hiện có ngày 17/11/2026. Mở `index.html` trực tiếp bằng Chrome hoặc dùng preview bên dưới. Không cần WordPress, PHP, MySQL, npm hay bước build để xem demo.

## Mở bản demo

```sh
cd sobi-packaging-demo
python3 tools/serve.py
```

Mở http://localhost:4173/. Dừng bằng Ctrl+C trong cửa sổ Terminal đang chạy server. Nếu cổng đã có preview của phiên Codex này, mở URL trực tiếp; không cần chạy thêm server. Có thể chọn cổng khác bằng `python3 tools/serve.py --port 4174`.

Nhấp đúp `Start-Demo.command` để mở preview bằng Terminal trên macOS. Server thử nghiệm có hỗ trợ byte-range cho MP4. Cũng có thể mở `index.html` trực tiếp; clipboard và một số tính năng media có thể bị trình duyệt giới hạn ở địa chỉ file.

## Nội dung và tương tác

60 tệp HTML gồm 17 trang danh mục thứ cấp, các trang thông tin, 9 chi tiết mẫu túi, 18 bài Blog, 3 chuyên mục, trang tìm kiếm, 404 và hai trang mẫu cũ vốn đang public tại nguồn. Bản đồ đầy đủ ở `docs/content-manifest.json`.

- Header/mobile menu, danh mục 4 tab, điều khiển bằng phím/Escape, link social và nút về đầu trang.
- Trang Sản phẩm: tìm tên/mã, tìm không dấu, lọc nhóm, phân trang 8 mẫu/trang và trạng thái rỗng.
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
- `assets/js/data.js`: dữ liệu công khai của sản phẩm/bài viết/trang.
- `tools/serve.py`: preview tùy chọn; `tools/export_demo.py`: công cụ tái xuất tùy chọn, cần beautifulsoup4 và website nguồn đang chạy.
- `docs/github-pages-costs.md`: nghiên cứu chi phí và các phương án xuất bản.
- `docs/pages-workflow.yml.example`: workflow GitHub Pages mẫu, chưa được kích hoạt.

Đường dẫn tương đối hỗ trợ đặt toàn bộ demo tại root hoặc dưới `/sobi-packaging/` trên GitHub Pages. Mọi liên kết nội bộ trỏ đến tệp HTML, không gọi WordPress REST/admin-post. Không đưa thông tin đăng nhập, SQL, private quote files hoặc Flatsome parent vào thư mục này.

## Ghi nhận khi chuyển đổi

Trang Blog nguồn có phần danh sách trống tại thời điểm xuất lần đầu (hiện đã được sửa ở WordPress), trong khi ba chuyên mục vẫn trả đủ 18 bài. Demo dựng danh sách Blog bằng chính các thẻ bài viết công khai đó.

Lần xuất ban đầu thiếu thông tin liên hệ trong header/footer. Ngày 21/11/2026, cả 60 trang HTML đã nhận email, địa chỉ, hotline và liên kết mạng xã hội từ phần công khai của WordPress local.

Đợt rà soát ngày 21/11/2026 đồng bộ header, footer và liên hệ nhanh trên 60 trang. Trang chủ có nút báo giá nhanh, hiệu ứng ở phần chữ của thẻ mẫu túi và bốn bước quy trình. Cả hai form báo giá dùng gợi ý nhập từ website nguồn.

Chạy `python tools/export_demo.py --sync-audit` để cập nhật các phần này từ các trang công khai tại `sobi-packaging.test`. Lệnh `python tools/export_demo.py --contacts-only` làm mới riêng thông tin liên hệ trong các thành phần dùng chung. Hai lệnh cần Python 3.10 trở lên và beautifulsoup4.

Các trang Sample Page/Hello world cũ được giữ để tránh thiếu nội dung public, nhưng không đưa vào menu chính/danh sách Blog 18 bài. Nội dung/thông số mẫu vẫn là dữ liệu demo của dự án nguồn.

Đây là bản copy độc lập. Website XAMPP, database và gói bàn giao không bị sửa. Bản demo được quản lý trong repository public riêng `tahieu98/sobi-packaging-demo`. Repository WordPress `tahieu98/sobi-packaging` tiếp tục private; dữ liệu/backend của website thật không được đưa sang đây.

## Kết quả kiểm tra

Đối soát bố cục cập nhật ngày 17/11/2026: [báo cáo so với WordPress](docs/layout-parity.md), gồm lỗi icon mũi tên, grid trang Liên hệ, bảng kraft, form và caption video; 30 cặp đo ở desktop/tablet/mobile cùng các khác biệt còn lại của bản demo.

- Order 8: 60 tệp HTML trả HTTP 200; đã kiểm tra 5.274 tham chiếu local, không có đích bị thiếu. 17 trang danh mục mới được kiểm tra trên WordPress/demo ở 390/768/1440px; xem [chi tiết](docs/subcategory-pages.md).
- 12 trang đại diện × 390/768/1440 px: 36/36 lượt có một H1, không tràn ngang và không có ảnh hỏng được phát hiện.
- Đã thử menu/tab/Escape, menu mobile, tìm/lọc/phân trang/empty state, gallery, prefill sản phẩm, form báo giá/reset, chọn PNG/chặn TXT, FAQ, bình luận thử và copy link.
- Đã kiểm tra đường dẫn project `/sobi-packaging/` và 404 lồng nhiều cấp. MP4 có cùng SHA256 với nguồn; request byte-range trả HTTP 206 đúng độ dài.
- Báo cáo: `docs/static-verification.json`, `docs/browser-verification.json`; ảnh `docs/screenshots/home-desktop.jpg`.
- Chưa nghiệm thu trên Safari/thiết bị vật lý; video Facebook/YouTube bên ngoài phụ thuộc dịch vụ và kết nối. Quản trị WordPress/UX Builder, lưu database, email/CRM và xử lý file phía server thuộc website gốc, không nằm trong demo frontend.


## GitHub Pages

Repository này chỉ chứa demo. GitHub Pages phục vụ các tệp static từ nhánh `main`, thư mục gốc (`/`); không chạy WordPress/PHP hoặc công cụ Python. Đường dẫn public là https://tahieu98.github.io/sobi-packaging-demo/.

Khi cần cập nhật demo: sửa tệp, kiểm tra, commit và `git push origin main`. GitHub tự dựng lại Pages sau khi nhánh `main` được cập nhật. Đây là luồng riêng với repository WordPress và không triển khai vào XAMPP. Không cần npm, Git LFS, workflow custom hoặc dịch vụ video trả phí cho bản hiện tại.
