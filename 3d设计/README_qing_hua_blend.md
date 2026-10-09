# 清 + 华 双视角布尔模型

打开 Blender，切换到 Scripting，打开 `create_qing_hua_blend.py`，点击 Run Script。

脚本会生成并保存：

- `qing_hua_boolean_editable.blend`：可编辑工程
- `qing_hua_boolean.stl`：最终切片模型（若 Blender 版本支持 STL 导出）

Outliner 中保留了四个步骤：母体立方体、正面清裁切结果、侧面华裁切结果、最终结果。模型使用连续布尔相交：立方体 ∩ 清字体积 ∩ 华字体积。
