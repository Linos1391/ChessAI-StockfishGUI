[English](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/README.md) | [Tiếng Việt](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/translation/README-vi.md)

<div align="center">

# ChessAI

**The AI that kills chess.**

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

This application will help you analyse chess position as a sub-window.

</div>

# Features

#### New feature (v1.0.0):

- Project is uploaded to PyPI. Now you can pip install it!

- Hovering on cropping canvas now show your mouse's location.

![features_12](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/assets/features_12.png?raw=true)

- Sorry O.P & I.P points, I'm not even angry over you right now. I bear no grudge against anyone. It's just that the world feels so, so wonderful right now. Throughout Heaven and Earth, I choose to learn PyTorch myself.

#### For old features, visit [Change Log](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/CHANGELOG.md).

<br>

# Installing

I've grown up and made a PyPI for you guys!
```
pip3 install chessai-stockfish
```
<br>

But above is default edition, which mean training features are not allowed yet. If you want the full edition, visit [TRAINING.md](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/TRAINING.md).

<br>

# Set up Stockfish

Go to [download page](https://stockfishchess.org/download/) and install Stockfish that support your device.
<br>

After that, let's start our ChessAI.
```
chessai
```
<br>

Because of first use, it will ask for Stockfish's path.
```
Cannot find setting.json file. Start create new one.
Please paste in path to stockfish:
>> (your path goes here)
```

<br>

# But you use Venv/Conda/Docker/...?

Go to your ChessAI directory (where `chessai.cmd` is stored).
```
cd ...
```
Then find your OS below.

#### For Unix
```
chmod a+x chessai.cmd
echo 'export chessai_path=$PWD
export PATH=$chessai_path:$PATH' >> ~/.bash_profile
source ~/.bash_profile
```

#### For Window
```
powershell $old_path = [Environment]::GetEnvironmentVariable('path', 'user'); $new_path = $old_path + ';' + $PWD; [Environment]::SetEnvironmentVariable('path', $new_path,'User');
```

**Notice:** Don't forget to configurate `chessai.cmd` file to fit your needs.

<br>

# Running

Use `chessai`.
```
chessai
```
*If you are using Unix and currently not in the environment where ChessAI is stored, use `chessai.cmd`.*

<br>

# License

[GNU GPLv3](https://github.com/Linos1391/ChessAI-StockfishGUI/blob/main/LICENSE)

<br>

# Disclaimer

This application was initially designed for analysing Chess World Cup livestreams and educational purposes. Please don't use this for any unethical reasons. Any damages from abusing this application will not be the responsibility of the author.
