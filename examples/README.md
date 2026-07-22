# Example Workflow

## `basic_artist_translation.json`

这个基础 workflow 演示 V1.6.5 Stable 中最直接的艺术风格翻译流程：

- Artist Style Selector
- SemanticStyleProfile
- Prompt Translation

workflow 使用本项目的 Selector、Semantic Preview、Translator 和 Prompt Merge 节点，并使用 ComfyUI 核心的 `Preview as Text` 节点显示语义预览与最终 Prompt。它不需要模型、LoRA、ControlNet、IPAdapter 或其他第三方节点。

## 使用步骤

1. 安装本节点。
2. 将 `basic_artist_translation.json` 导入 ComfyUI。
3. 在 `Artist Style Selector` 中选择一位画师。
4. 在 `Base Prompt + Style Prompt` 节点中输入基础 Prompt。
5. Queue workflow，查看 `Semantic Preview Output` 与 `Final Prompt Output`。

可以在 `Artist Style Translator` 中切换目标模型和细节级别，也可以在 Semantic Preview 中启用 verbose 模式查看更完整的 `SemanticStyleProfile` 信息。

> 该 workflow 仅用于演示节点使用方式，不包含完整文生图流程。

此示例基于 V1.6.5 Stable，不引用本地绝对路径、不使用测试数据，也不依赖 `develop-v1.6` 分支功能。
