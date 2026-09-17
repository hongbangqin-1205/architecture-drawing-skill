# Example 1: Business Architecture

## Request

Turn the attached healthcare informatization report into a one-slide editable business architecture blueprint. Use a restrained government-project style and keep only the architecture backbone.

## Extraction Result

```text
Title: 潍坊市卫生健康信息化业务架构图
Formula: 1+2+6

Audience and collaboration:
- 居民、医疗机构、基层卫生机构、公共卫生机构、委办单位

Core capability:
- 卫生健康数据资源中心
- 业务协同与数据共享能力

Application domains:
1. 医疗服务
2. 公共卫生
3. 基层卫生
4. 医疗保障协同
5. 卫生监管
6. 便民服务

Enablers:
- 标准规范体系
- 安全保障体系

Foundation:
- 数据资源
- 应用支撑
- 基础设施
```

## Expected Composition

- One 16:9 slide.
- Title and short subtitle.
- Main application grid centered between enabler rails.
- One platform/capability center.
- Data and infrastructure foundation at the bottom.
- All visible architecture elements remain editable PPT shapes and text boxes.

## Expected Command Shape

```powershell
python scripts/main.py `
  --workspace-dir "C:\work\weifang" `
  --output "C:\work\weifang\outputs\business-architecture.pptx" `
  --presentations-skill-dir "$env:CODEX_HOME\plugins\cache\openai-primary-runtime\presentations\<version>\skills\presentations"
```

Before running, replace the template content arrays in `scripts/build_editable_architecture_ppt.mjs` with the extracted structure above.
