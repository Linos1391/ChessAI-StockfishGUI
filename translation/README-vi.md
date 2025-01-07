[English](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/README.md) | [Tiếng Việt](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/translation/README-vi.md)

<div align="center">

# ChessAI

**AI huỷ diệt cờ vua.**

[![][latest-release-shield]][latest-release-url]
[![][latest-commit-shield]][latest-commit-url]
[![][python-shield]][python-url]
[![][stockfish-shield]][stockfish-url]

[latest-release-shield]: https://badgen.net/github/release/Linos1391/ChessAI-StockfishGUI/development?icon=github
[latest-release-url]: https://github.com/Linos1391/ChessAI-StockfishGUI/releases/latest
[latest-commit-shield]: https://badgen.net/github/last-commit/Linos1391/ChessAI-StockfishGUI/main?icon=github
[latest-commit-url]: https://github.com/Linos1391/ChessAI-StockfishGUI/commits/main
[python-shield]: https://img.shields.io/badge/Python-3.10+-yellow
[python-url]: https://www.python.org/downloads/
[stockfish-shield]: https://img.shields.io/badge/Stockfish-16+-green
[stockfish-url]: https://stockfishchess.org/download/

![Icon](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/assets/Icon128.png?raw=true)

![ChessAI](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/assets/ChessAI.png?raw=true)

Ứng dụng này sẽ hỗ trợ bạn phân tích nước đi cờ vua trong cửa sổ phụ.

</div>

# Tính năng

#### Tính năng mới (v1.0.0):

- Cuối cùng nó cũng lên PyPI rồi. Giờ bạn có thể pip install nó!

- Chức năng xén ảnh bây giờ khi di chuột sẽ hiện vị trí chuột.

![features_12](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/assets/features_12.png?raw=true)

- Xin lỗi em, điểm O.P và I.P. Anh không giận gì em đâu. Anh cũng chả hận thù gì người trên cõi đời này. Anh thấy, thế gian giờ thật tươi đẹp biết bao. Trên trời dưới đất, tao mạnh nhất. (PyTorch đã có mặt!!!)

#### Để xem những tính năng cũ, vào [Change Log](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/translation/CHANGELOG-vi.md).

<br>

# Tải xuống

Sau khi tu luyện 7749 ngày, ChessAI đã có mặt trên PyPI!
```
pip3 install chessai-stockfish
```
<br>

Nhưng bên trên là bản mặc định, nghĩa là các tính năng train model chưa được cài sẵn. Nếu muốn có bản hoàn chỉnh, hẫy vào [TRAINING.md](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/translation/TRAINING-vi.md).

<br>

# Cài đặt Stockfish

Đến [trang tải xuống](https://stockfishchess.org/download/) và cài bản Stockfish hỗ trợ máy của bạn.
<br>

Sau đó, cùng khởi động ChessAI nào!
```
chessai
```
<br>

Vì là lần đầu sử dụng, nó sẽ hỏi đường dẫn đến Stockfish.
```
Cannot find setting.json file. Start create new one.
Please paste in path to stockfish:
>> (đường dẫn dán vô đây)
```

<br>

# Bạn dùng Venv/Conda/Docker/...?

Vào đường dẫn của folder ChessAI (nơi `chessai.cmd` đang nằm).
```
cd ...
```
Sau đó tìm OS của bạn.

#### Cho Unix
```
chmod a+x chessai.cmd
echo 'export chessai_path=$PWD
export PATH=$chessai_path:$PATH' >> ~/.bash_profile
source ~/.bash_profile
```

#### Cho Window
```
powershell $old_path = [Environment]::GetEnvironmentVariable('path', 'user'); $new_path = $old_path + ';' + $PWD; [Environment]::SetEnvironmentVariable('path', $new_path,'User');
```

<br>

# Sử dụng

Dùng `chessai`.
```
chessai
```
*Nếu bạn dùng Unix và đang không ở trong environment có ChessAI, dùng `chessai.cmd`.*

<br>

# Giấy phép

[GNU GPLv3](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/LICENSE)

<br>

# Miễn trừ trách nhiệm

Ứng dụng này ban đầu được thiết kế để phân tích những kênh livestream của Chess World Cup và lý do học tập. Làm ơn đừng dùng nó cho bất kỳ mục đích xấu nào. Những thiệt hại trong việc lạm dụng ứng dụng này sẽ không là trách nhiệm của chủ sở hữu.
