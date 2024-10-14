[English](README.md) | [Tiếng Việt](README-vi.md)

<div align="center">

# ChessAI

**The AI that kills chess.**

[![][chessai-shield]][chessai-url]
[![][python-shield]][python-url]
[![][conda-shield]][conda-url]
[![][stockfish-shield]][stockfish-url]

[chessai-shield]: https://img.shields.io/badge/ChessAI-0.2.0-red
[chessai-url]: https://github.com/Linos1391/ChessAI
[python-shield]: https://img.shields.io/badge/Python-3.12+-yellow
[python-url]: https://www.python.org/downloads/
[conda-shield]: https://img.shields.io/badge/Anaconda-24.7+-grass
[conda-url]: https://www.anaconda.com/download
[stockfish-shield]: https://img.shields.io/badge/Stockfish-16+-green
[stockfish-url]: https://stockfishchess.org/download/

![Icon](assets/Icon128.png)

![ChessAI](assets/ChessAI.png)

This application will help you analyse chess position as a sub-window.

</div>

## Table of contents

1. [Features](#features)

2. [Installing](#installing)

3. [Set up Stockfish](#set-up-stockfish)

4. [Running](#running)

5. [License](#license)

6. [Disclaimer](#disclaimer)

## Features

#### New feature (v0.2.0):

- Finally, we has the vision tab (Still WIP so there will be some errors).

![features_8](assets/features_8.png)

- Choose file or screenshot your chessboard. Then crop it.

**Notice:** The background must one color only (No gradient) and you must not crop it too tight. 

![features_9](assets/features_9.png)

- Make your own custom templates.

![features_10](assets/features_10.png)
#### For old features, visit [Change Log](CHANGELOG.md).

## Installing

#### Option 1: Install [.exe file](https://github.com/Linos1391/ChessAI/releases).

- Open .exe file once for 'setting.json' being made. Then modified it and enjoy.

**Notice:** Your browser may report this file as not usually downloaded. Report its safety will help me a lot!

#### Option 2: Manually install through Github:

1. Clone the repository.

```
git clone https://github.com/Linos1391/ChessAI.git
cd ChessAI
```

2. Install the required python packages.

```
pip install -r requirements.txt
```

## Set up Stockfish

1. Go to [download page](https://stockfishchess.org/download/) and install Stockfish that support your device.
2. Open [ChessAI/setting.json](ChessAI/setting.json) file.
```
{
    "ChessAI": {
        "Engine": "", <-- Put your Stockfish path here (.exe)
        "Analyse Every Move": false,
        "Elo": 1350,
        "Current Template": "Chesscom"
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

Run the [run.py](run.py) file.

```
python run.py
```

## License

[GNU GPLv3](LICENSE)

## Disclaimer

This application was initially designed for analysing Chess World Cup livestreams and educational purposes. Please don't use this for any unethical reasons. Any damages from abusing this application will not be the responsibility of the author.
