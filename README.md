# 文献检索工具

这个应用程序允许您根据文章标题从Springer和ScienceDirect爬取和下载学术论文。用户界面为中文，但搜索的文章标题是英文的。

## 功能

- 在Springer和ScienceDirect上搜索文章
- 自动下载PDF
- 支持批量处理多篇文章
- 提供命令行和图形用户界面
- 支持从文本文件读取文章标题

## 先决条件

- Python 3.7+
- Microsoft Edge浏览器（用于网络爬取）

## 安装

1. 安装必要的依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

### 命令行界面

1. 使用特定的文章标题运行应用程序：
   ```
   python literature_retriever.py "Article Title 1" "Article Title 2"
   ```

2. 使用包含文章标题的文件运行应用程序（每行一个标题）：
   ```
   python literature_retriever.py -f articles.txt
   ```

3. 指定自定义下载目录：
   ```
   python literature_retriever.py -f articles.txt -d /path/to/download/dir
   ```

4. 在可见模式下运行（非后台模式）：
   ```
   python literature_retriever.py -f articles.txt --no-headless
   ```

### 图形用户界面

运行GUI应用程序：
```
python gui_interface.py
```

在GUI中：
1. 在文本区域输入文章标题（每行一个）或者
2. 选择包含文章标题的文件
3. 设置选项，如下载目录和后台模式
4. 点击"开始检索"开始处理

## 注意事项

- 应用程序使用Selenium与网页交互，因此需要Microsoft Edge浏览器
- 网络爬取可能受到目标网站的速率限制和服务条款的限制
- 由于订阅要求，某些文章可能无法访问
- 请通过不过快的请求来尊重服务器

## 文件

- `literature_retriever.py`: 主要应用程序逻辑
- `gui_interface.py`: 图形用户界面（中文界面，搜索英文文章标题）
- `requirements.txt`: Python依赖项
- `retriever.log`: 应用程序活动的日志文件
- 下载的PDF文件将直接保存在脚本同目录下