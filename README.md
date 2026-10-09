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

## ⚠️ 合规与免责声明（使用前必读）

本工具仅用于检索与下载使用者**已通过所在机构或个人订阅合法取得访问权限**的文献。

**使用者须自行确认并承担以下责任：**

1. **遵守目标网站条款**：Springer、Elsevier/ScienceDirect 等服务条款通常**禁止自动化批量抓取与下载**。本项目不对因使用本工具导致的账号封禁、IP 封锁、订阅终止、机构追责或任何法律责任承担责任。
2. **版权合规**：下载的论文受著作权保护，**不得用于二次分发、批量镜像、商业利用或任何超出合理使用范围的用途**。
3. **优先使用官方 API**：强烈建议改用出版商官方接口（Springer Nature API、Elsevier API）获取元数据与全文，那是合规且稳定的方式。
4. **本项目已知的对抗性行为**：代码中**主动关闭了自动化检测特征**（`--disable-blink-features=AutomationControlled`、剔除 `enable-automation` 开关、注入脚本抹除 `navigator.webdriver`，见 `literature_retriever.py` 第 60-62、74 行），且**未检查目标站点 robots.txt**、未设置请求频率限制（CLI 多标题模式与 GUI 文本区模式**完全无间隔**）。这些行为**很可能违反目标网站的使用条款**，请在使用前自行评估并承担后果。
5. **订阅与登录**：本项目不处理登录/订阅流程，若目标文献需机构权限，请自行确保浏览器会话已获授权。
6. **无担保**：本软件按"现状"提供，不提供任何明示或默示担保，包括但不限于适销性、特定用途适用性与不侵权的担保。

**如你无法接受以上任一条款，请勿使用本工具。**

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

## 开发进度与已知不足

### 已实现

- 双站点检索：Springer（`#query` 搜索框 + `data-track-action` 结果抓取）与 ScienceDirect（`#search-input` + `HeaderSearchButton`）
- 双引擎顺序回退：先 Springer 后 ScienceDirect
- PDF 下载：各站点 4 种选择器依次探测 + `requests` 直取字节流写盘；ScienceDirect 支持按标题推导文件名兜底
- 从文本文件批量读取标题（CLI 与 GUI 均支持）
- CLI 参数完整：位置标题、`-f/--file`、`-d/--download-dir`、`--no-headless`
- Tkinter GUI：多行标题输入、文件选择、下载目录选择、后台线程执行 + 线程安全回写 UI、停止按钮
- 单篇失败不影响整体（逐篇 try/except）；退出时关闭全部浏览器实例
- 日志同时输出到终端与 `retriever.log`

### 未实现 / 已知不足

- **"停止"按钮不能真正停止检索**：只禁用按钮并关闭浏览器，工作线程仍继续执行
- **无 robots.txt 检查、无请求频率控制、无重试与指数退避**
- **无延迟配置项**；CLI 标题模式与 GUI 文本区模式无任何间隔（仅文件模式每篇 `sleep(5)`）
- 无并发控制/队列，纯串行
- 无订阅/登录处理，也无"需要登录"的错误分类，仅笼统记录 error 日志
- 无 PDF 有效性校验（不检查 `Content-Type`），登录页 HTML 可能被当 PDF 存盘
- 无去重、无断点续跑：重复运行会重复下载
- 无元数据导出（`pandas`、`BeautifulSoup` 已 import 但**从未使用**，`requirements.txt` 却强制安装）
- 结果只打印到终端，不写 CSV/JSON
- 选择器硬编码且脆弱，站点改版即失效
- 未使用任何出版商官方 API
- `browser` 参数可传 `'chrome'` 但代码只创建 Edge（参数是假选项）
- 文件名净化不完整（只替换 `/ : *`），跨平台非法字符可能写盘失败
- **无自动化测试**：`test_script.py` 是真实联网下载脚本，无断言、无 pytest 结构
- 兜底下载分支 `return True`（布尔而非路径），调用方会把 `True` 当文件名返回
- GUI 中 `self.retriever` 跨线程读写无锁；完成提示即使在全部失败时也显示"检索完成"

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