## Giới thiệu

Vậy bạn muốn làm một template cho riêng mình? Nghe hay đấy, nhưng sẽ có vài vấn đề phát sinh như sau:
- Khoảng 2.5GB của PyTorch.
- Không có GPU, quá trình chạy sẽ rất chậm.
- Trình xử lý tự động vẫn chưa hoàn chỉnh và sẽ cần chỉnh sửa thủ công.
<br>

Dù vậy, bạn vẫn muốn tiếp tục? Vậy thì đi thôi!

## Chuẩn bị

Dĩ nhiên tôi sẽ không cho khả năng train model thành tính năng mặc định. Đầu tiên thì tải PyTorch. Đến [PyTorch](https://pytorch.org/get-started/locally/) và tải phiên bản phù hợp với máy. (Đừng quên bỏ `torchaudio` ra)

**Ví dụ:** Tôi dùng Window và Cuda bản 12.4
```
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```
<br>

À, và cần pandas nữa:
```
pip3 install pandas
```
Sau những bước kể trên, tính năng train model đã được mở khoá. Nhưng đừng đi vội, để tôi cho bạn vài mẹo này!

## Mẹo bỏ túi

1. Template phải là bàn cờ khởi đầu (cái bàn lúc mới vô, chưa đi quân nào hết).
2. Khi thêm template mới, KHÔNG được xén quá sát.
3. Hình nền của bàn cờ (tức là cái mày bên ngoài bàn cờ, không phải bên trong) KHÔNG nên là dạng gradient (kiểu màu sắc chuyển dần từ màu này sang màu kia).
4. Trình làm template tự động vẫn còn khuyết điểm. Bạn có thể tự chỉnh template (dùng Photoshop hay sao đó) và train lại để có model tốt hơn (chỉ là đừng đổi tên file nhé).
5. Nếu bạn có kinh nghiệm với PyTorch, và thấy dùng hai ảnh cho một nhãn tên là quá sơ sài. Cứ thoải mái thêm ảnh vào theo ý thích, nhớ chỉnh `Labels.csv`. Sau đó train lại đến khi nào vừa ý.
6. Tôi không phải là coder đỉnh nóc kịch trần gì cả, nhưng tôi đã cố hết sức để code chỉnh chu nhất có thể. Mọi đóng góp đều được đón nhận, có thể tôi sẽ hỏi cái contribution đó làm gì nhé.
