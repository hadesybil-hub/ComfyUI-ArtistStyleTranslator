# ComfyUI-ArtistStyleTranslator

ComfyUI-ArtistStyleTranslator 是一个基于 `SemanticStyleProfile` 的艺术风格翻译节点。它将画师名称或别名解析为结构化、可观察的视觉特征，再生成适合不同图像模型的提示词。

## 🚀 Quick Start

最快体验方式：使用 `examples/basic_artist_translation.json`。

该 Workflow 展示：

- Artist Style Selector
- SemanticStyleProfile Preview
- Artist Style Translator
- Prompt Merge

## Examples

| Workflow                                 | Description                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------ |
| `examples/basic_artist_translation.json` | Official basic workflow demonstrating the complete Artist Style Translator pipeline. |

## 当前版本

**V1.6.5 Stable**

`main` 分支用于 V1.6.5 稳定版本；V1.7 的开发工作保留在 `develop-v1.6` 分支，不属于当前稳定版本。

## 核心流程

```text
Artist Style Selector
↓
ArtistStyleResolver
↓
SemanticStyleProfile
↓
Translator
↓
Prompt Merge
```

## 稳定版本功能

- Artist Style Selector
- Semantic Style Profile
- Preview Formatter
- Prompt Translation
- ComfyUI 节点集成

所有提示词都由语义风格数据经过 Resolver、Style Engine 和模型适配流程生成。语义字段描述可观察的视觉属性，不直接使用画师姓名或 `in the style of` 署名短语作为提示词。

## ComfyUI 节点

- `Artist Style Selector`
- `Artist Style Translator`
- `Artist Style Translator Advanced`
- `Semantic Profile Preview`
- `Artist Style Prompt Merge`

节点分类：`prompt/artist_style`

支持的目标模型：Generic、Z-Image、FLUX、Qwen-Image 和 Krea。

支持的细节级别：Short、Standard 和 Detailed。

## 安装

将项目目录放入：

```text
ComfyUI/custom_nodes/ComfyUI-ArtistStyleTranslator
```

重启 ComfyUI 后即可搜索上述节点。

## 基本用法

1. 使用 `Artist Style Selector` 选择内置画师，或向 Translator 输入画师名称。
2. Translator 通过 `ArtistStyleResolver` 获取 `SemanticStyleProfile`。
3. 选择目标模型和细节级别，生成对应的风格提示词。
4. 使用 `Artist Style Prompt Merge` 将风格提示词与基础提示词合并。
5. 如需检查解析后的语义信息，使用 `Semantic Profile Preview`。

未知、空白或未收录名称会使用安全的结构化回退，不会把用户输入直接复制到最终提示词。

## 开发方向

V1.7 正在 `develop-v1.6` 分支开发：

- Artist Knowledge Base
- Semantic Artist Profiles
- 可验证画师知识体系

这些 V1.7 功能不属于 `main` 分支的 V1.6.5 稳定功能。

## 测试

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'D:\ComfyUI_portable_TE_v260619\python_embeded\python.exe' -m unittest discover -s tests -v
& 'D:\ComfyUI_portable_TE_v260619\python_embeded\python.exe' tools\test_node_import.py
```

## 许可证

本项目使用 MIT License，详见 `LICENSE`。
