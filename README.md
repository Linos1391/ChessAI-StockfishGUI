[English](README.md) | [Tiếng Việt](README-vi.mdS)

<div align="center">

# ChessAI

**The AI that kills chess.**

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

This application will help you analyse chess position as a sub window.

</div>

## Table of contents

1. [Features](#features)

2. [Installing](#installing)

3. [Set up Stockfish](#set-up-stockfish)

4. [Running](#running)

5. [License](#license)

6. [Disclaimer](#disclaimer)

## Features

#### v0.1.0

- Drag&move setup chessboard

![features_1](assets/features_1.gif)

- Playable chessboard

![features_2](assets/features_2.gif)

- Changable elo

![features_3](assets/features_3.gif)

- Able to play Chess960

![features_4](assets/features_4.gif)

#### v0.1.1

- Top moves are easier to located

![features_5](assets/features_5.gif)



## Installing

1. Clone the repositories

```
git clone https://github.com/Linos1391/ChessAI.git
cd ChessAI
```

2. Install the required python packages

```
pip install -r requirements.txt
```

## Set up Stockfish

1. Go to [download page](https://stockfishchess.org/download/) and install Stockfish that support your device
2. Open [ChessAI/setting.json](ChessAI/setting.json) file
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

Run the [run.py](run.py) file

```
python run.py
```

## License

[GNU GPLv3](LICENSE)

## Disclaimer

This application was initially designed for analysing Chess World Cup livestreams and educational purposes. Please don't use this for any unethical reasons. Any damages from abusing this application will not be the responsibility of the author.
