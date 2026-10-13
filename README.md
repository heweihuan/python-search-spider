# 商品搜索爬虫

基于 Python + Selenium 的多平台商品搜索爬虫，支持淘宝、京东等平台的商品信息采集，可导出 CSV 文件。

> 本项目仅用于 Python 自动化、数据采集与网页解析学习，请勿用于商业用途或高频采集。

## 功能特点

- 支持淘宝、京东等多平台商品搜索
- 可自定义搜索关键词、采集条数、店铺数量
- 自动提取商品标题、价格、店铺、商品链接、商品图片
- 结果自动导出为 `search_results.csv`
- 支持 `--demo` 离线演示模式，无需登录即可验证程序
- 异常自动捕获，遇到反爬、登录失败、页面变化时不会直接崩溃
- 内置随机等待，降低请求频率

## 技术栈

- Python 3
- Selenium
- Chrome 浏览器
- CSV 文件导出

## 运行环境

- Windows / macOS / Linux
- Python 3.8 及以上
- Chrome 浏览器
- Selenium 4.6 及以上

## 安装依赖

```bash
pip install selenium -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 运行方式

### 交互模式

```bash
python product_search_selenium.py
```

运行后按提示选择平台、输入关键词、设置采集条数和店铺数即可。

### 离线演示

```bash
python product_search_selenium.py --demo
```

该模式不需要登录，也不会真实访问电商平台，适合先验证环境是否正常。

### 命令行参数

```bash
python product_search_selenium.py --site taobao --kw 蓝牙耳机 --num 10 --shops 5
```

## 输出结果

运行完成后，会在项目目录下生成：

```text
search_results.csv
```
<img width="800" height="745" alt="爬虫运行结果截图" src="https://github.com/user-attachments/assets/b2ca6ed0-6cb2-4a16-a138-061a6d33afb5" />

CSV 中包含：

- 商品标题
- 价格
- 店铺名称
- 商品链接
- 商品图片链接

## 注意事项

- 首次运行需要安装 Chrome 浏览器。
- 真实采集时可能需要扫码登录淘宝或京东。
- 请遵守目标网站的使用规则，不要高频采集。
- 本项目不包含破解验证码、绕过付费接口、批量攻击网站等功能。

## 作者

- 姓名：何伟桓
- GitHub：https://github.com/heweihuan/python-search-spider
- 邮箱：3389620005@qq.com
- 电话：18320217764

