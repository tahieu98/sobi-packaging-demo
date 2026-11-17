# Đối soát bố cục demo với WordPress

Ngày 17/11/2026. Đối chiếu bản GitHub Pages, bản HTML local và WordPress tại `http://sobi-packaging.test/`. Source WordPress local, worktree và hai nhánh GitHub `main` / `codex/sobi-development` cùng commit `a3de8531c235c434af226e05aa544795e9cb9f54` khi kiểm tra. Bản WordPress không bị chỉnh trong lần đối soát này.

## Những lỗi đã sửa trong demo

| Thành phần | Nguyên nhân | Chỉnh sửa / kết quả |
| --- | --- | --- |
| Mũi tên `.sobi-category-control .icon-angle-down` | Demo dùng ký tự Unicode `⌄`, phụ thuộc hình dáng và đường căn font hệ điều hành | Thay bằng SVG mask tự dựng, có khung kích thước và tâm cố định; tâm icon trùng tâm nút khi đóng/mở. Chiều rộng nút desktop 230,45px, tương đương bản gốc. |
| Các icon tìm kiếm, menu, điện thoại, phóng ảnh, play… | Cùng phụ thuộc ký tự thay thế | Dùng cùng cơ chế SVG, giữ `currentColor` và trạng thái xoay của CSS Sobi. Không sao chép bộ font icon của Flatsome. |
| Hai cột trang Liên hệ | CSS độc lập thiếu `.medium-5/7` và `.large-5/7` | Bổ sung grid 12 cột ở các breakpoint đang dùng. Khung báo giá ở viewport 1440px trở về rộng 734,16px, trước đó giãn thành 1280px. |
| Bảng so sánh giấy kraft | `td/th` thừa kế line-height thân bài, khác primitive của bản gốc | Khôi phục line-height riêng cho bảng. Chiều cao bảng desktop từ 406,66px về 373,77px, bằng WordPress. |
| Form báo giá | Thiếu khoảng cách legend, nhịp label và padding input của nguồn | Bổ sung các primitive tương ứng, giữ vùng nhập nội dung demo đủ cao để sử dụng. |
| Chú thích video hero | Quy tắc `figcaption` chung của demo ép về 14px | Cho caption video kế thừa 16px như WordPress; chiều cao media hero mobile khớp lại với bản gốc. |

Thay đổi giao diện nằm trong `assets/css/base.css` và `assets/css/demo.css`. CSS thiết kế Sobi trong `assets/theme/sobi.css` / `conversion.css` vốn đã khớp source WordPress; lỗi chính nằm ở lớp CSS thay thế parent theme. Head của 43 HTML được bổ sung mã SHA256 rút gọn trong URL stylesheet để tránh cache CSS cũ trên GitHub Pages; exporter cũng sinh URL có phiên bản. Không xuất lại hoặc thay nội dung CMS.

## Phạm vi kiểm chứng

- Đo 10 trang đại diện ở ba viewport 390, 768 và 1440px trên cùng một tab trình duyệt: Trang chủ, Sản phẩm, chi tiết SGD01, Giấy kraft, Blog, bài chuẩn bị logo, Liên hệ, Về Sobi, Quy trình, In theo yêu cầu. Tổng cộng 30 cặp đối chiếu, không phát hiện tràn ngang toàn trang ở demo.
- Kích thước grid/card Sản phẩm, bố cục chi tiết mẫu, bảng kraft, thân bài Blog và cột Liên hệ khớp các vùng được đo trong bản gốc. Chênh lệch dưới 1px do làm tròn được chấp nhận; không tuyên bố mọi pixel của toàn bộ website giống hệt.
- Đã thử mở/đóng mega menu, cuộn chuột riêng danh sách bên phải, phóng/đóng ảnh, mở FAQ và mở tìm kiếm. Khi cuộn menu phải từ 0 lên 78,5px, cột trái giữ nguyên vị trí y=278,68px và trang nền không cuộn.
- Kiểm tra lại toàn bộ 43 HTML và 3.803 tham chiếu local: không có đích bị thiếu; các trang trả HTTP 200. MP4 trả byte-range 206, 1024 byte đúng yêu cầu và SHA256 trùng nguồn.
- Số đo trước/sau: [layout-parity-measurements.json](layout-parity-measurements.json). Ảnh trước sửa: [catalogue](screenshots/parity-catalogue-before.jpg). Ảnh demo local sau sửa: [desktop](screenshots/parity-catalogue-desktop.jpg), [mobile](screenshots/parity-catalogue-mobile.jpg).

## Khác biệt còn được ghi nhận

- Demo có banner nhận diện, số hotline và các kênh social; Settings của WordPress local hiện chưa xuất đủ các mục này ở header/footer. Vì vậy vị trí tuyệt đối của nội dung và chiều cao footer mobile khác nhau (hàng social thêm 44px).
- Form demo có thông báo mô phỏng và textarea tối thiểu 100px. Form cao hơn nguồn khoảng 112–163px tùy viewport. Đây là khác biệt của trải nghiệm demo; dữ liệu không gửi vào backend thật.
- Hero ở mobile/tablet còn chênh khoảng 29–31px tổng chiều cao, chủ yếu do phần tử clearfix của `.row` trong parent WordPress tạo thêm một khoảng gap 28px, cùng chênh nhỏ chiều cao nút. Độ rộng hai khối và kích thước media đã được đối soát; demo không nhập cả runtime parent chỉ để tái tạo phần khoảng trống này.
- **Thứ tự bài Blog khác nguồn:** nhiều bài có cùng timestamp đến giây; demo trước đây thu thập từ từng chuyên mục rồi sắp theo ngày. Trang Blog nguồn hiện đã có danh sách sau khi cấu hình CMS được sửa. Khác thứ tự/tiêu đề trong mỗi hàng khiến grid Blog ở 768px chênh khoảng 27px; kích thước thẻ và typography tương ứng không bị lỗi. Chưa thay dữ liệu hoặc thứ tự biên tập trong lần sửa CSS này.

Kiểm tra giao diện dùng trình duyệt Chromium của Codex; chưa xác nhận Safari hoặc thiết bị vật lý. Kiểm tra HTTP tất cả các trang không đồng nghĩa với đối soát thị giác từng trang ở mọi kích thước.
