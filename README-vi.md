[English](README.md) | [Tiếng Việt](README-vi.md)

<div align="center">

# ChessAI

**Con AI sẽ huỷ diệt cờ vua.**

[![][chessai-shield]][chessai-url]
[![][python-shield]][python-url]
[![][conda-shield]][conda-url]
[![][stockfish-shield]][stockfish-url]

[chessai-shield]: https://img.shields.io/badge/ChessAI-0.1.1-red
[chessai-url]: https://github.com/Linos1391/ChessAI
[python-shield]: https://img.shields.io/badge/Python-3.12+-yellow
[python-url]: https://www.python.org/downloads/
[conda-shield]: https://img.shields.io/badge/Anaconda-24.7+-grass
[conda-url]: https://www.anaconda.com/download
[stockfish-shield]: https://img.shields.io/badge/Stockfish-16+-green
[stockfish-url]: https://stockfishchess.org/download/

![Icon](assets/Icon128.png)

![ChessAI](assets/ChessAI.png)

Ứng dụng này sẽ hỗ trợ bạn phân tích các nước đi của cờ vua trong cửa sổ phụ.

</div>

## Mục lục

1. [Tính năng](#tính-năng)

2. [Tải xuống](#tải-xuống)

3. [Chuẩn bị Stockfish](#chuẩn-bị-stockfish)

4. [Hoạt động](#hoạt-động)

5. [Giấy phép](#giấy-phép)

6. [Miễn trừ trách nhiệm](#miễn-trừ-trách-nhiệm)

## Tính năng

#### v0.1.0

- Thiết lập ván cờ bằng cơ chế kéo thả.

![features_1](assets/features_1.gif)

- Bàn cơ chơi được.

![features_2](assets/features_2.gif)

- Có thể thay đổi elo.

![features_3](assets/features_3.gif)

- Có thể chơi Chess960.

![features_4](assets/features_4.gif)

#### v0.1.1

- Nước đi tốt nhất dễ nhìn hơn.

![features_5](assets/features_5.gif)

## Tải xuống

###### Bạn có thể dùng [file .exe](https://github.com/Linos1391/ChessAI/releases/tag/main) và chuyển đến [bước tiếp theo](#chuẩn-bị-stockfish).

###### Hoặc làm thủ công theo những bước bên dưới:

1. Lưu thư mục về máy.

```
git clone https://github.com/Linos1391/ChessAI.git
cd ChessAI
```

2. Tải những thư viện Python cần thiết.

```
pip install -r requirements.txt
```

## Chuẩn bị Stockfish

1. Đi đến [trang này](https://stockfishchess.org/download/) và tải Stockfish hỗ trợ thiết bị của bạn.
2. Mở file [ChessAI/setting.json](ChessAI/setting.json).
```
{
    "ChessAI": {
        "Engine": "", <-- Cho địa chỉ của Stockfish vào đây (.exe)
        "Analyse Every Move": false,
        "Elo": 1350
    },
    "Stockfish": {
        "Debug Log File": "",
        "UCI_Chess960": false,
        "Min Split Depth": 0,
        "Threads": 1,
        "Hash": 16
    }
}
```

## Hoạt động

Chạy file [run.py](run.py).

```
python run.py
```

## Giấy phép

[GNU GPLv3](LICENSE)

## Miễn trừ trách nhiệm

Ứng dụng này ban đầu được thiết kế để phân tích những kênh livestream của Chess World Cup và lý do học tập. Làm ơn đừng dùng nó cho bất kỳ mục đích xấu nào. Những thiệt hại trong việc lạm dụng ứng dụng này sẽ không là trách nhiệm của chủ sở hữu.