# ComfyUI-ArtistStyleTranslator

一个完全离线的 ComfyUI 自定义节点：把画师名称或常见别名映射为结构化视觉特征，再转换为适合不同图像模型的自然语言正向提示词。

> A fully offline ComfyUI node that converts built-in structured style profiles into model-adapted visual prompts.

## 当前版本

当前版本为 **V1.3（1.3.0）**。语义引擎已经进入实际提示词生成链路：

```text
Artist Database → Style Engine → Model Adapter → Prompt Builder → ComfyUI Node
```

- `artist_database.py` 保存 20 位演示画师的结构化 Style Profile
- `style_engine.py` 将 Profile 语义化为 Feature，完成稳定排序、去重和 PromptUnit 转换
- `model_adapters.py` 只把已选择的 PromptUnit 转换为不同模型的文本结构
- `prompt_builder.py` 负责查询、通用回退、细节数量选择和安全编排
- `nodes.py` 只维护 ComfyUI 输入输出接口

每个中间 Feature 与 PromptUnit 都保留 `source`、`confidence`、`evidence` 和 `generated_by`。这些字段为未来本地 Ollama、联网来源及用户来源预留；当前生产数据只使用 `builtin`，没有实现或调用任何 Provider。

## 离线与隐私

- 完全离线，不访问或上传任何数据
- 不调用 Ollama、在线 API 或其他模型服务
- 不需要第三方依赖
- 当前仍然只有内置演示数据库
- 不包含缓存、多画师融合或网络数据库功能

## 安装

把项目目录放到：

```text
ComfyUI/custom_nodes/ComfyUI-ArtistStyleTranslator
```

当前便携版环境中的路径：

```text
D:\ComfyUI_portable_TE_v260619\ComfyUI\custom_nodes\ComfyUI-ArtistStyleTranslator
```

重启 ComfyUI 后搜索 `Artist Style Translator`。

## 节点接口

节点分类：`prompt/artist_style`

输入：

- `artist_name`：多行文本，默认 `Yaegashi Nan`
- `target_model`：Generic、Z-Image、FLUX、Qwen-Image 或 Krea，默认 Z-Image
- `detail_level`：Short、Standard 或 Detailed，默认 Standard

输出：

- `result`：可直接连接正向提示词节点的纯文本字符串

如需保留可编辑的基础提示词，可使用同分类下的 `Artist Style Prompt Merge`：将基础提示词填入 `base_prompt`，把 `Artist Style Translator.result` 连接到 `style_prompt`，再把 `final_prompt` 连接到 `CLIPTextEncode.text`。合并节点只负责清理首尾空白并追加文本。

## 模型适配差异

- Generic：中性、通用的逗号视觉短语
- Z-Image：连贯直接、以可观察特征为主的自然短语
- FLUX：强调材质、光影、空间关系和构图的完整句子
- Qwen-Image：明确连接主体、线条、色彩、光影和构图的自然句式
- Krea：优先保留辨识度较高的简短视觉特征

相同画师在不同目标模型下会得到不同的文本结构，而不是仅替换模型名称。相同输入和选项始终得到稳定结果。

## 使用示例

输入：

```text
artist_name: WLOP
target_model: FLUX
detail_level: Standard
```

输出为 1 到 3 个可直接用于图像生成的描述句，不包含画师姓名、署名短语、JSON、Markdown 或复杂权重语法。

未知、空白或未收录名称会使用结构化通用 Profile，不会返回错误文字，也不会把用户输入复制到结果中。

## 测试

```powershell
D:\ComfyUI_portable_TE_v260619\python_embeded\python.exe -m unittest discover -s tests -v
D:\ComfyUI_portable_TE_v260619\python_embeded\python.exe tools\test_node_import.py
```

## 数据用途与局限性

数据库描述仅用于把名称转换为可观察视觉特征。数据是保守的演示资料，不是官方或学术数据库，不包含画师个人信息，也不保证对每位画师的描述完全准确。当前画师、别名和视觉特征覆盖范围有限。

## 许可证

本项目使用 MIT License，详见 `LICENSE`。
