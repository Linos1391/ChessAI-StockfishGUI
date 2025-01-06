## Introduction

So you want to make your own templates? Sound good, but that will go with the following issues:
- Approximately 2.5GB of PyTorch.
- Without GPU, the process might be slow and take time.
- The automatic process is not perfect and will require to edit manually.
<br>

With all of that in mind, and you're still with me? Then let's go!

## Preparing

Of course I won't make the training as default feature. Let's install PyTorch first. Visit [PyTorch](https://pytorch.org/get-started/locally/) and install the suitable version. (Don't forget to remove `torchaudio`)

**Eg:** I use Window and Cuda 12.4
```
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```
<br>

Then, we also need pandas:
```
pip3 install pandas
```
After these steps, the training features has been unlocked. But don't go yet, let me give you some tips!

## Pocket Tips

1. The template must be starting chessboard (the initial chessboard before any moves).
2. When add new templates, you must NOT crop it too tight. 
3. It is recommended that the chessboard's background (meaning the color outside of the chessboard) should NOT be gradient.
4. The automatic template maker still has its weakness. You can fix the template yourself (by Photoshop or image editor) and re-train for better result (just don't rename files though).
5. If you have experience with PyTorch, and finding using only two images for one label is too poorly trained. Feel free to add images, just remember to edit `Labels.csv`. Then re-train it until satisfied.
6. I am not a decent coder, but I have tried my best to optimize the code. Any contributions are welcomed, just that I might ask for your contribution's effects if you don't mind.