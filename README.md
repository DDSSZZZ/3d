# 双视角立体汉字：清 / 华

本仓库包含一个用 Python 标准库生成的双视角立体汉字概念模型。目标是从正面观察“清”，从与正面垂直的侧面观察“华”。

> **当前状态：生成器已提交；STL 的可打印性仍需切片软件或网格修复工具进行最终确认。** 脚本输出的 SVG 是按笔画参数绘制的示意投影，并非从 STL 网格计算出的真实投影。

## 目录

- `3d-upload/make_dual_view.py`：生成 STL、两张 SVG 示意图和 JSON 参数报告。
- `3d-upload/validate_output.py`：检查输出文件是否存在、STL 三角面是否可解析、是否存在退化三角面，以及包围盒和三角面数量。
- `.github/workflows/generate-model.yml`：在推送相关文件或手动触发时运行生成和检查，并将结果作为 GitHub Actions artifact 保存。

## 本地运行（Windows PowerShell）

在仓库根目录运行：

```powershell
python .\3d-upload\make_dual_view.py
python .\3d-upload\validate_output.py
```

脚本会在 `3d-upload/` 目录中生成：

- `qing_hua_integrated.stl`：ASCII STL 模型
- `projection_qing.svg`：正面“清”的示意投影
- `projection_hua.svg`：侧面“华”的示意投影
- `projection_check.json`：设计参数和三角面数量

只使用 Python 标准库，无需安装第三方 Python 包。

## 在 GitHub 上生成模型

1. 打开仓库的 **Actions** 页面。
2. 选择 **Generate and validate 3D model** 工作流。
3. 点击 **Run workflow**。
4. 等待工作流完成后，在该次运行页面的 **Artifacts** 区域下载 `qing-hua-model-output`。

每次运行都会重新生成文件，并执行基础结构检查。Actions artifact 是运行产物，不会自动提交回仓库的 Git 历史。

## 重要限制

基础检查不等同于专业网格修复或打印认证。当前建模器将多个挤出笔画和底座组合到同一个 STL 中，没有执行真正的布尔并集，也没有证明网格封闭、无自交或流形。打印前请在 Blender、Meshmixer、PrusaSlicer 或其他网格/切片工具中检查并预览切片。

若要发布最终成品，应在通过网格检查和切片预览后，再将 STL 作为正式 release 或项目附件发布。
