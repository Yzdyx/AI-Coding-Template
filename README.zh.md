# AI Coding Template

[English](README.md) | **简体中文**

面向编码 Agent 和企业级 Agent 应用的单仓库工程模板。内部工作区名称为
`enterprise-agent-platform`。本仓库提供参考实现和工程流程，尚不是完整的生产服务。

| 体系 | 目标 | 主要位置 |
| --- | --- | --- |
| 编码 Agent 工程体系 | 帮助编码 Agent 理解、修改、验证和维护仓库 | `AGENTS.md`、`.agents/`、`.codex/`、`.github/`、`docs/`、`scripts/` |
| 运行时 Agent 应用体系 | 定义业务 Agent、应用和共享平台能力 | `agents/`、`apps/`、`packages/`、`schemas/`、`evals/`、`infra/`、`tests/` |

`AGENTS.md` 约束编码工作；`agents/<name>/agent.yaml` 定义业务 Agent。两者职责分离。

## 按需查找

采用渐进式披露：概览 → 任务索引 → 模块规则 → 具体文件。
先读当前任务的入口，再按需沿链接展开。

| 需求 | 阅读入口 |
| --- | --- |
| 在本仓库开展工作 | [Agent 指令](AGENTS.md) |
| 选择任务相关资料 | [知识索引](docs/index.md) |
| 了解任意目录或文件的用途 | [完整仓库目录与文件说明](docs/repository-map.md) |
| 修改模块边界或依赖 | [系统架构](ARCHITECTURE.md)与[架构索引](docs/architecture/index.md) |
| 理解设计和产品意图 | [设计索引](docs/design-docs/index.md)与[产品索引](docs/product-specs/index.md) |
| 规划和跟踪任务 | [执行计划指南](docs/PLANS.md) |
| 排查事故或安全问题 | [运维索引](docs/operations/index.md)与[安全指南](docs/SECURITY.md) |

完整说明为每个项目目录和文件给出用途，供查找时使用，无须启动时全文加载。
各模块 README 和嵌套 `AGENTS.md` 保存局部细节，修改模块前应继续阅读这些入口。

## 仓库区域

| 区域 | 职责 | 详细清单 |
| --- | --- | --- |
| `.agents/`、`.codex/`、`.github/` | 工程技能、编码 Agent 配置、审查和 CI | [编码工具](docs/repository-map.md#coding-tools) |
| `docs/` | 架构、产品、设计、计划、安全和运维知识 | [文档](docs/repository-map.md#documentation) |
| `agents/` | 研究和客服 Agent 的逻辑、提示词、工具和测试 | [业务 Agent](docs/repository-map.md#business-agents) |
| `apps/` | 管理控制台、HTTP API 和后台 Worker | [应用](docs/repository-map.md#applications) |
| `packages/` | 共享契约、Provider、策略、持久化、观测和评测工具 | [共享包](docs/repository-map.md#shared-packages) |
| `schemas/` | 清单、事件和工具的 JSON 契约 | [Schema](docs/repository-map.md#schemas) |
| `evals/` | 共享数据集、回归套件、安全用例和基线 | [评测](docs/repository-map.md#evaluation) |
| `infra/` | Terraform 环境示例和授权策略 | [基础设施](docs/repository-map.md#infrastructure) |
| `scripts/`、`tests/`、`tooling/` | 仓库检查、契约与离线系统测试、本地工具 | [验证和本地工具](docs/repository-map.md#validation-and-local-tools) |

## 开始使用

在仓库根目录执行下列命令。仓库检查使用 Python 3.10+ 和标准库，无须安装依赖。

```powershell
python scripts/check-architecture.py
python scripts/check-agent-manifests.py
python scripts/check-doc-links.py
python .agents/skills/verify-change/scripts/verify.py --root .
```

TypeScript 工作区在 [package.json](package.json) 中声明使用 Node.js 22+ 和
pnpm 9.12.0。安装依赖或启动应用前，先读目标模块的 README。Python Agent 不属于
pnpm 工作区，使用 `unittest` 测试。

需要可选的本地容器环境时，按[本地开发说明](tooling/local-dev/README.md)检查前置条件并启动。
运行仓库检查不需要启动容器。

## 贡献约定

- 遵循 `Types → Config → Repo → Service → Runtime → UI` 的依赖方向；跨包访问使用
  公开接口，横切能力通过显式 Provider 接口进入。
- 修改前检查适用规则和目标模块。跨模块修改先写执行计划，并明确可修改的文件范围。
- 在完整清单中说明每个项目路径，并从最近的索引或 README 提供入口。路径变化时同步更新导航。
- 代码、提交信息及新增或修改的技术说明使用英文。本文件作为中文翻译，与
  [README.md](README.md) 保持一致；既有中文参考文档继续保留。
- 运行必需检查并报告真实输出。跳过检查不等于通过。
- 凭据和本机覆盖配置不得入库。生产基础设施操作及高风险操作需要人工批准。

完整工作流程和安全要求见 [AGENTS.md](AGENTS.md)。

## 模板边界

- 参考 Provider 包含离线和内存实现，尚不提供生产级持久化和身份认证保证。
- 基础设施环境、评测基线、所有权团队句柄和历史执行计划属于示例，使用前需按实际项目审查。
- [数据库结构文档](docs/generated/db-schema.md) 目前仍是模板，计划中的生成器尚未实现。
  不要手工修改生成资产。
- 工作区声明为 `UNLICENSED`，未附带开源许可证授权。

根据风险和部署需求选择必要结构。小团队可从指令、文档和工程技能开始，再按需采用运行时和基础设施区域。
