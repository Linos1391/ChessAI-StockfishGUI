:; if [ -z 0 ]; then
  @echo off
  goto :WINDOWS
fi
#UNIX

# -- Add Venv/Conda/Docker/... here. Eg: conda activate ... ; chessai
chessai

exit 0

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

:WINDOWS

REM -- Add Venv/Conda/Docker/... here. Eg: conda activate ... && chessai
chessai