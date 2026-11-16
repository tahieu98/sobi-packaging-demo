# GitHub Pages và video 16 MB — nghiên cứu ngày 17/11/2026

## Kết luận cho dự án này

Lưu mã HTML/CSS/JavaScript và video 16 MB bằng Git trong repository `tahieu98/sobi-packaging` không phát sinh một khoản phí riêng chỉ vì có video. GitHub Pages cũng không có cơ chế tính tiền theo từng lượt phát MP4 thông thường. Tuy nhiên, lưu mã trên GitHub và xuất bản một website bằng GitHub Pages là hai việc khác nhau.

Repository `tahieu98/sobi-packaging` hiện là **private**. GitHub Pages ở repository public có trên GitHub Free; Pages từ repository private cần GitHub Pro/Team/Enterprise phù hợp. Vì vậy chưa thể kết luận host demo tại repository private hiện tại là miễn phí nếu chưa biết gói tài khoản đang dùng. Phiên làm việc này không thay đổi gói hoặc kiểm tra thông tin thanh toán của tài khoản.

Website Pages từ repository private trên gói cá nhân thông thường vẫn là website public. Repository private không đồng nghĩa với link demo có mật khẩu hoặc chỉ chủ tài khoản xem được.

## Dung lượng video và giới hạn

File thực tế: `assets/media/2026/11/sobi-san-xuat-1080p.mp4`, **16.681.088 byte**, tương đương khoảng **16,68 MB / 15,91 MiB**.

| Hạng mục | Giới hạn/chính sách từ GitHub | Đối chiếu demo |
| --- | --- | --- |
| Một tệp Git thông thường | Cảnh báo trên 50 MiB; chặn trên 100 MiB | MP4 15,91 MiB nằm dưới cả hai |
| Upload tệp qua trình duyệt | Tối đa 25 MiB/tệp | MP4 hiện tại nằm dưới giới hạn |
| Website Pages đã xuất bản | Không lớn hơn 1 GB | Demo hiện chỉ khoảng vài chục MB; xem manifest/checks cho số đo |
| Băng thông Pages | Soft limit 100 GB/tháng | Cần theo dõi khi demo có nhiều lượt xem |
| Build Pages | Soft limit 10 build/giờ; có ngoại lệ cho custom Actions workflow | Cập nhật thủ công demo thông thường không cần build dày |

Nếu chỉ tính tải đầy đủ video, 100 GB tương đương xấp xỉ 6.000 lượt tải file này. Đây là ước lượng, không phải số lượt xem bảo đảm: ảnh/CSS/JS cũng tốn băng thông; cache, byte-range, thời gian xem và các request làm số thực tế khác nhau. Autoplay có thể tiêu thụ băng thông dù khách không bấm video.

Khi vượt soft limit, GitHub có thể giới hạn phục vụ, trả 429 hoặc liên hệ đề nghị giảm tải/chuyển CDN; tài liệu không mô tả khoản overage tự động theo lượt xem Pages. Không nên hiểu con số 100 GB là gói trả thêm không giới hạn. GitHub Actions, Git LFS, Codespaces hoặc dịch vụ CDN có chính sách tính phí riêng nếu sử dụng vượt phần được bao gồm hoặc bật dịch vụ trả phí. Demo này không cần Git LFS, Codespaces hay dịch vụ video trả phí; không dùng các dịch vụ đó chỉ để chứa MP4 16 MB.

## Phương án triển khai

1. **Muốn chi phí hosting demo bằng 0 trên GitHub Free:** tạo một repository public riêng chỉ chứa demo, ví dụ `sobi-packaging-demo`, và bật Pages từ `main` / root. Cách này giữ repository WordPress hiện tại private. Chỉ public tài nguyên đã được phép chia sẻ.
2. **Muốn giữ đúng repository private `tahieu98/sobi-packaging`:** sử dụng gói tài khoản hỗ trợ Pages từ private repository. Nếu tài khoản đã có gói phù hợp, việc thêm demo và MP4 không tự tạo một phí video riêng; nếu chưa có thì có phí gói theo bảng giá áp dụng cho tài khoản.
3. **Không đổi quyền/gói GitHub:** có thể giữ demo local để duyệt trước, hoặc đánh giá hosting static khác có kết nối private repository. Free tier của mỗi nhà cung cấp có điều kiện và quota riêng, không mặc định miễn phí vô hạn.

Không cần đổi repository chứa mã nguồn WordPress sang public để trình bày demo. Phương án được chọn sau khi duyệt bản demo: tạo repository public riêng `tahieu98/sobi-packaging-demo`; repository WordPress hiện tại tiếp tục private.

## Đưa demo vào cùng repository khi được yêu cầu xuất bản

Giữ cấu trúc nguồn hiện tại; chép demo vào một thư mục riêng, chẳng hạn `static-demo/`, thêm thư mục này vào allowlist `.gitignore`, rồi commit trên một nhánh riêng. Không ghi đè `website/`.

Mẫu `docs/pages-workflow.yml.example` có thể được chép vào `.github/workflows/demo-pages.yml` trong repository khi chuẩn bị publish. Nó triển khai riêng `static-demo/`, dùng GitHub Actions chính thức và trigger thủ công. Trước lúc dùng, kiểm tra gói Pages của repository private, quyền Actions/Pages, source Pages là GitHub Actions và quyền sử dụng các tài nguyên được công khai. Không cấu hình paid runner hoặc quota trả phí chỉ để chạy mẫu này.

Nếu dùng repository public riêng chỉ chứa demo, phương án đơn giản là deploy `main` / root qua Settings → Pages, không cần workflow hoặc build/npm. File `.nojekyll` đã có sẵn.

GitHub Pages phù hợp trình bày demo frontend; tài liệu giới hạn việc dùng Pages như dịch vụ miễn phí để vận hành kinh doanh online/e-commerce hoặc trang chủ yếu phục vụ giao dịch thương mại/SaaS. Không dùng bản demo này để nhận thông tin nhạy cảm hoặc đơn hàng thật. Khi chuyển sang site kinh doanh, cần chọn hosting và backend phù hợp với WordPress/form nghiệp vụ.

## Nguồn chính thức

- [About GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages): static hosting; điều kiện public/private theo gói; website công khai.
- [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits): dung lượng, băng thông, giới hạn build và xử lý khi vượt quota.
- [About large files on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github): 25 MiB qua browser; cảnh báo 50 MiB/chặn 100 MiB qua Git.
- [GitHub's plans](https://docs.github.com/en/get-started/learning-about-github/githubs-plans): Pages trong private repository theo gói.
- [GitHub pricing](https://github.com/pricing): tham khảo gói/dịch vụ trả phí hiện hành; số tiền cuối tùy tài khoản, kỳ thanh toán và thuế.

Chính sách/giá có thể thay đổi. Các kết luận trên dựa trên trang tài liệu chính thức đã đọc trong ngày nghiên cứu, không phải một cam kết thanh toán thay GitHub.


## Phương án đã chọn

Người dùng đã chọn tạo repository demo riêng: https://github.com/tahieu98/sobi-packaging-demo. Pages dùng `main` / root; URL dự kiến là https://tahieu98.github.io/sobi-packaging-demo/. Không sử dụng Git LFS hoặc workflow custom. Quota và điều kiện ở trên vẫn áp dụng; việc tạo repository không đăng ký gói trả phí.
