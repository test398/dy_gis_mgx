# README

## 相关性公式

$r = \frac{\sum [(x_i - \bar{x})(y_i - \bar{y})]}{\sqrt{\sum (x_i - \bar{x})^2 \times \sum (y_i - \bar{y})^2}}$

## prompt

修改 engineering_ml_cable_scoring.py 参考文件的方法
，训练数据在数据/data 文件夹，可以取一部分为训练集一部分为测试集，测试的指标是 Readme.md 文件的相关性公式，该公式评分要 0.8 以上才算合格。评分标准文件夹下的人工评分.csv 是标签，然后测试的相关性指标 x 是人工评分 y 是机器评分

写一个测试函数，
