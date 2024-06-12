# psd2png
# 安装
要想使用这个节点需要安装psd-tools(请先保证是在comfyui的python环境下安装的)
```shell
pip install psd-tools
```
# 节点说明
1. 此节点可以识别psd文件.
2. psd_path默认为C:/example.psd,此路径无任何作用,当它改变后节点返回的图片将以psd_path对应的psd文件为准,否则以上传的psd文件为准.
3. psd文件中最上面的图层序号最大,最下面的图层序号为1.
4. image输出layer_index对应的psd图层图像.当layer_index为0时,image输出psd的全图.
4. top_image输出的是psd的最上面图层的图像.
5. mask输出的对应layer_index的遮罩.
![simple](https://github.com/violet-chen/comfyui-psd2png/blob/master/images/image.png?raw=true)