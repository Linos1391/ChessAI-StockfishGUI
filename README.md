<div align="center">

# ChessAI

**The AI that kills chess.**

[![][python-shield]][python-url]
[![][conda-shield]][conda-url]
[![][stockfish-shield]][stockfish-url]

[python-shield]: https://img.shields.io/badge/Python-3.12+-yellow
[python-url]: https://www.python.org/downloads/
[conda-shield]: https://img.shields.io/badge/Anaconda-24.7+-grass
[conda-url]: https://www.anaconda.com/download
[stockfish-shield]: https://img.shields.io/badge/Stockfish-16+-green
[stockfish-url]: https://stockfishchess.org/download/








![Icon](assets/Icon128.png)

![ChessAI](assets/ChessAI.png)



This application will help you analyse chess position as a sub window.

</div>


## Features

- Drag & Move setup chessboard

![features_1](assets/features_1.gif)

- Playable chessboard

![features_2](assets/features_2.gif)

- Changable elo

![features_3](assets/features_3.gif)

- Able to play Chess960

![features_4](assets/features_4.gif)

## Installing

Clone the repositories

```
git clone https://github.com/Linos1391/ChessAI.git
cd ChessAI
```

Install the required python package

```
pip install -r requirements.txt
```

## Setup Stockfish

- Go to [download page](https://stockfishchess.org/download/) and install Stockfish that support your device
- Open [setting.json](ChessAI/setting.json) file
```
{
    "ChessAI": {
        "Engine": "", <-- Put your Stockfish path here (.exe)
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

## Running

Run the [ChessGUI.py](ChessAI/ChessGUI.py) file

```
python ChessAI/ChessGUI.py
```

## License

[GNU GPLv3](LICENSE)
