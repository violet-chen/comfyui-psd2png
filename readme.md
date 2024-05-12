# psd2png
注:要想使用这个节点需要安装psd-tools
```shell
pip install psd-tools
```
此节点可以识别psd文件.
psd文件中最上面的图层序号最大,最下面的图层序号为1.
image输出layer_index对应的psd图层图像.
top_image输出的是psd的最上面图层的图像(隐藏的也可以输出).
mask输出的是psd的最上面图层的遮罩.