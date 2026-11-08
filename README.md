# 莲生灵光体 · Liansheng Lingguangti

由莲生设计的手写风格开源字体。当前版本 **2.2.9**，支持 **400–650 可变字重**，可免费用于个人及商业项目。

## 安装

下载 `fonts/LianshengLingguangti-2.2.9-Variable.ttf`，双击安装到 macOS 字体册或 Windows 字体设置。支持可变字体的应用可调节字重。

## 源文件与构建

本仓库提供可编辑的 TrueType 轮廓母版、完整的当前版本构建脚本与依赖锁定版本。母版位于 `dist/liansheng-2.2.8/`，可使用 FontForge 等字体编辑器修改；它是 2.2.9 的构建输入，提供本版本所需的轮廓数据。

使用 Python 3.10 或更新版本：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python build-lingguang-2.2.9.py
```

结果输出到 `dist/lingguang-2.2.9/`。构建会测量、校正笔画并生成可变字体和字体压缩包，运行可能需要数分钟。脚本内含字符映射、字距、名称及字重轴检查。字体时间戳和压缩包时间可能变化，不承诺逐字节相同。

## 正式发布

版本 2.2.9，支持中文、英文、数字及常用符号，提供 400–650 可变字重。构建验证见 `BUILD-VERIFICATION.md`。

## 版权与授权

莲生的原创贡献：Copyright © 2026 莲生。字库沿用的上游笔画数据来自 Make Me a Hanzi，其 graphics 数据衍生自文鼎字体，因此本字体及衍生字形依 **Arphic Public License** 分发，请阅读 `LICENSE`、`LICENSE-zh_CN.txt` 及 `vendor/` 中的原始声明。免费商用不等于放弃版权；修改、再分发须保留授权和版权声明，标明修改内容与日期并遵循原授权。

网站上的《莲生灵光体开源许可证》仅适用于明确另行发布且有权独立授权的原创内容，不替代本仓库字体的上游授权。为避免许可冲突，本次发布字体与构建材料统一按随附 Arphic Public License 提供；第三方文件保留原许可。仓库不包含上游 LGPL 词典数据，保留其来源说明作为来源记录。

## English

A free handwritten-style variable font by Liansheng, version 2.2.9, weight range 400–650. Install the TTF in `fonts/`. The editable TrueType outline master in `dist/liansheng-2.2.8/` is the input to the current build; this repository does not reconstruct every glyph from the earliest sketches. Run the commands above with Python 3.10+. Outputs are placed in `dist/lingguang-2.2.9/`.

The font derives from Make Me a Hanzi graphics and upstream Arphic fonts. The font and covered derivative materials are distributed under the accompanying Arphic Public License, including its conditions for modification and redistribution. Copyright © 2026 莲生 (Liansheng) for original contributions; upstream notices remain intact. The separate license displayed on the local website does not replace these terms.

## 反馈

请通过 GitHub Issues 提交字符、字重和截图，便于复现问题。
