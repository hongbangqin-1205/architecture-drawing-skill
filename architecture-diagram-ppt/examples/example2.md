# Example 2: Technical Or Data-Structure Blueprint

## Request

Use the supplied blueprint image as a layout reference, but generate an editable PowerPoint rather than embedding the image.

## Layout Translation

```text
Main canvas
+----------------------+----------------------+
| Layer labels         | Regular module grid  |  Right sidebar
| 前端展现             | Web / H5 / signature |  运维管理
| 接入层               | routing / auth        |  监控预警
| 业务支撑             | services / queues     |  CI/CD
| 数据底座             | compute / databases   |  弹性伸缩
| 支撑环境             | cloud / VPC / storage |
+----------------------+----------------------+
```

For a data-structure diagram, replace the center with:

```text
应用层 -> 开放层 -> 治理层 -> 数据源
```

Use equal-height cells, shared column boundaries, thin straight connectors, and a single blue/cyan accent family. Keep layer labels, module cells, arrows, and sidebars as native shapes.

## Acceptance Checks

- The reference image is not embedded as the slide body.
- `ppt/media/` contains no primary diagram image. A zero media count is expected for a pure shape diagram.
- The slide is 16:9 and all text remains inside its parent shape.
- The rendered preview has no clipping, overlap, or cropped bottom.
- Layer order and labels are readable without relying on the source screenshot.
