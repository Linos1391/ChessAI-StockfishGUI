"""Setup file for PyPI"""

import pathlib
import setuptools

setuptools.setup(
    name="chessai-stockfish",
    version="1.0.3",
    description="A sub-window GUI for Stockfish. \
(Contributions are welcomed, but I might won't touch this any sooner)",
    long_description=pathlib.Path('README.md').read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Linos",
    project_urls={
        "Source": "https://github.com/Linos1391/ChessAI-StockfishGUI",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Natural Language :: English",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Console",
        "Environment :: GPU :: NVIDIA CUDA",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pygubu",
        "stockfish",
        "Pillow",
        "PyScreeze",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["chessai = ChessAI.main:main"]},
)
