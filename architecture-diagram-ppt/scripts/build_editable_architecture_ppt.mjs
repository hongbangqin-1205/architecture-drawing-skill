// Template script for building an editable architecture diagram PPT.
// Adapt paths, content, and dimensions for the current task before running.
//
// Required environment variables:
//   WORKSPACE_DIR
//   PRESENTATIONS_SKILL_DIR
//   FINAL_PPTX
//   RUNTIME_PYTHON
// Optional:
//   PPT_FONT, RUNTIME_NODE, RUNTIME_NODE_MODULES, RUNTIME_BIN_DIR

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const workspaceDir = process.env.WORKSPACE_DIR;
const skillDir = process.env.PRESENTATIONS_SKILL_DIR;
const finalPptx = process.env.FINAL_PPTX;
const runtimePython = process.env.RUNTIME_PYTHON;

if (!workspaceDir || !skillDir || !finalPptx || !runtimePython) {
  throw new Error("Set WORKSPACE_DIR, PRESENTATIONS_SKILL_DIR, FINAL_PPTX, and RUNTIME_PYTHON.");
}

const { importRuntimeModule } = await import(
  pathToFileURL(path.join(skillDir, "container_tools", "runtime_helpers.mjs")).href,
);
const { Presentation, PresentationFile, FileBlob } = await importRuntimeModule("@oai/artifact-tool");
const { resolvePresentationFont, finalizePresentation } = await import(
  pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href,
);

const fontFamily = resolvePresentationFont({ fontFamily: process.env.PPT_FONT || "Microsoft YaHei" });
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const slide = presentation.slides.add();
slide.background.fill = "#F8FAFC";

const colors = {
  ink: "#0F172A",
  muted: "#526174",
  border: "#CBD5E1",
  connector: "#94A3B8",
  blue: "#2563EB",
  blueSoft: "#EFF6FF",
  blueLine: "#93C5FD",
  green: "#0F766E",
  orange: "#D97706",
  slate: "#475569",
};

function addText(name, text, left, top, width, height, opts = {}) {
  if (width <= 0 || height <= 0) throw new Error(`Invalid text frame for ${name}`);
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: fontFamily,
    fontSize: opts.fontSize ?? 18,
    bold: opts.bold ?? false,
    color: opts.color ?? colors.ink,
    alignment: opts.alignment ?? "center",
    verticalAlignment: opts.verticalAlignment ?? "middle",
    autoFit: "shrinkText",
    wrap: "square",
    lineSpacing: opts.lineSpacing ?? 1.08,
    insets: opts.insets ?? { top: 2, right: 4, bottom: 2, left: 4 },
  };
  return shape;
}

function addRect(name, left, top, width, height, opts = {}) {
  if (width <= 0 || height <= 0) throw new Error(`Invalid rect frame for ${name}`);
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left, top, width, height },
    fill: opts.fill ?? "#FFFFFF",
    line: { style: "solid", fill: opts.line ?? colors.border, width: opts.lineWidth ?? 1.1 },
    borderRadius: opts.radius ?? 8,
  });
}

function addBox(key, left, top, width, height, title, subtitle, opts = {}) {
  addRect(`${key}-surface`, left, top, width, height, {
    fill: opts.fill ?? "#FFFFFF",
    line: opts.line ?? colors.border,
    radius: opts.radius ?? 8,
  });
  addRect(`${key}-accent`, left, top, 5, height, {
    fill: opts.accent ?? colors.blue,
    line: opts.accent ?? colors.blue,
    radius: 3,
  });

  const compact = height <= 52;
  const titleTop = top + (compact ? 4 : 6);
  const titleHeight = subtitle ? (compact ? 22 : 26) : Math.max(14, height - 12);
  const bodyTop = top + (compact ? 27 : 34);
  const bodyHeight = Math.max(12, height - (compact ? 31 : 38));

  addText(`${key}-title`, title, left + 16, titleTop, width - 32, titleHeight, {
    fontSize: opts.titleSize ?? 18,
    bold: true,
  });
  if (subtitle) {
    addText(`${key}-subtitle`, subtitle, left + 20, bodyTop, width - 40, bodyHeight, {
      fontSize: opts.bodySize ?? 13.5,
      color: opts.bodyColor ?? colors.muted,
    });
  }
}

function addLineSegment(name, left, top, width, height) {
  addRect(name, left, top, width, height, {
    fill: colors.connector,
    line: colors.connector,
    lineWidth: 0,
    radius: 0,
  });
}

function addLayerLabel(key, label, top, height, opts = {}) {
  const left = opts.left ?? 24;
  const width = opts.width ?? 52;
  const fill = opts.fill ?? "#0EA5E9";
  addRect(`${key}-layer-label`, left, top, width, height, {
    fill,
    line: fill,
    radius: 2,
  });
  addText(`${key}-layer-text`, label, left + 4, top + 4, width - 8, height - 8, {
    fontSize: opts.fontSize ?? 15,
    bold: true,
    color: "#FFFFFF",
    lineSpacing: 1.02,
  });
}

function addCell(key, text, left, top, width, height, opts = {}) {
  addRect(`${key}-cell`, left, top, width, height, {
    fill: opts.fill ?? "#F8FBFF",
    line: opts.line ?? "#93C5FD",
    radius: opts.radius ?? 0,
    lineWidth: opts.lineWidth ?? 1,
  });
  addText(`${key}-text`, text, left + 4, top + 2, width - 8, height - 4, {
    fontSize: opts.fontSize ?? 13,
    bold: opts.bold ?? false,
    color: opts.color ?? "#0B4F8A",
    lineSpacing: 1.02,
  });
}

function addBandTitle(name, text, left, top, width, height, opts = {}) {
  addRect(`${name}-band`, left, top, width, height, {
    fill: opts.fill ?? "#EAF6FF",
    line: opts.line ?? "#93C5FD",
    radius: 0,
  });
  addText(`${name}-title`, text, left, top + 1, width, 22, {
    fontSize: opts.fontSize ?? 13,
    bold: true,
    color: opts.color ?? "#075985",
  });
}

function addDarkCell(key, text, left, top, width, height) {
  addRect(`${key}-dark`, left, top, width, height, {
    fill: "#075FAE",
    line: "#075FAE",
    radius: 0,
  });
  addText(`${key}-dark-text`, text, left + 4, top + 2, width - 8, height - 4, {
    fontSize: 12.5,
    bold: true,
    color: "#FFFFFF",
  });
}

function addSidebarItem(key, title, body, left, top, width, height) {
  addRect(`${key}-surface`, left, top, width, height, {
    fill: "#FFFFFF",
    line: "#FFFFFF",
    radius: 6,
  });
  addText(`${key}-title`, title, left + 6, top + 10, width - 12, 22, {
    fontSize: 13.5,
    bold: true,
    color: "#0B83BF",
  });
  if (body) {
    addText(`${key}-body`, body, left + 6, top + 32, width - 12, height - 38, {
      fontSize: 12,
      color: colors.muted,
    });
  }
}

// Replace this sample blueprint content with task-specific architecture content.
addText("title", "技术架构图", 110, 14, 1060, 34, { fontSize: 28, bold: true });
addText("subtitle", "左侧分层 · 中央能力矩阵 · 右侧运维管理", 110, 48, 1060, 24, {
  fontSize: 15,
  color: "#64748B",
});

const canvasLeft = 86;
const canvasTop = 86;
const canvasWidth = 1040;
const canvasHeight = 604;
addRect("main-canvas", canvasLeft, canvasTop, canvasWidth, canvasHeight, {
  fill: "#FFFFFF",
  line: "#0284C7",
  lineWidth: 1.4,
  radius: 4,
});

addLayerLabel("frontend", "前端\n展现", 102, 68);
addLayerLabel("access", "接入\n层", 190, 68);
addLayerLabel("support", "业务\n支撑", 278, 76);
addLayerLabel("data", "数据\n底座", 374, 170);
addLayerLabel("env", "支撑\n环境", 568, 74);

[
  ["VUEJS", 118],
  ["Html5", 376],
  ["Webpack模块化", 634],
  ["数字签名", 892],
].forEach(([label, x], index) => addCell(`front-${index + 1}`, label, x, 112, 220, 28));

addLineSegment("line-front-access", 638, 145, 4, 20);
addText("line-front-access-label", "http/https", 650, 146, 100, 18, {
  fontSize: 11,
  color: "#64748B",
  alignment: "left",
});

[
  ["负载均衡", 118],
  ["路由管理", 316],
  ["协议转换", 514],
  ["安全认证", 712],
  ["入侵检测", 910],
].forEach(([label, x], index) => addCell(`access-${index + 1}`, label, x, 208, 170, 28));

[
  ["spring cloud\n微服务框架", 118],
  ["消息队列\nKafka", 316],
  ["任务调度\nQuartz", 514],
  ["数据持久层\nMyBatis", 712],
  ["数据库连接池\nDruid", 910],
].forEach(([label, x], index) => addCell(`support-${index + 1}`, label, x, 304, 170, 42, {
  fontSize: 12,
}));

addBandTitle("compute", "计算层", 118, 386, 970, 74);
addDarkCell("compute-flink", "Flink流式计算框架", 128, 424, 465, 26);
addDarkCell("compute-spark", "Spark并行计算框架", 603, 424, 475, 26);

addBandTitle("data-layer", "数据层", 118, 478, 970, 104);
[
  ["关系型数据库\n海量数据库", 128],
  ["MPP数据库 Doris", 344],
  ["内存数据库\nRedis", 560],
  ["分布式文件系统\nHDFS", 776],
  ["对象存储 Minio", 950],
].forEach(([label, x], index) => addDarkCell(`data-${index + 1}`, label, x, 530, index === 4 ? 128 : 178, 36));

[
  ["云主机", 118],
  ["VPC", 280],
  ["弹性IP", 442],
  ["负载均衡", 604],
  ["对象存储", 766],
  ["...", 928],
].forEach(([label, x], index) => addDarkCell(`env-${index + 1}`, label, x, 608, 140, 28));
addText("env-title", "多云环境", 540, 584, 160, 22, {
  fontSize: 13,
  bold: true,
  color: "#075985",
});

addLineSegment("line-env-data-left", 360, 584, 4, 28);
addLineSegment("line-env-data-left-head", 354, 580, 16, 4);
addLineSegment("line-env-data-right", 762, 584, 4, 28);
addLineSegment("line-env-data-right-head", 756, 580, 16, 4);

const sidebarLeft = 1152;
addRect("ops-sidebar", sidebarLeft, 86, 104, 604, {
  fill: "#0EA5E9",
  line: "#0EA5E9",
  radius: 8,
});
addText("ops-title", "运维管理", sidebarLeft + 10, 104, 84, 26, {
  fontSize: 14,
  bold: true,
  color: "#FFFFFF",
});
addSidebarItem("ops-monitor", "监控预警", "Prometheus", sidebarLeft + 16, 156, 72, 92);
addSidebarItem("ops-cicd", "CI/CD", "Jenkins", sidebarLeft + 16, 290, 72, 92);
addSidebarItem("ops-scale", "弹性伸缩", "kubernetes", sidebarLeft + 16, 424, 72, 92);

addLineSegment("line-sidebar-1", 1126, 220, 24, 4);
addLineSegment("line-sidebar-2", 1126, 506, 24, 4);

slide.speakerNotes.textFrame.setText("Editable architecture diagram generated from structured source material.");

const stagingDir = path.join(workspaceDir, ".codex-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
await fs.mkdir(path.dirname(finalPptx), { recursive: true });
const candidatePath = path.join(stagingDir, "editable-architecture-candidate.pptx");
const receiptPath = path.join(stagingDir, "editable-architecture.validation.json");
await fs.rm(receiptPath, { force: true });
await fs.rm(finalPptx, { force: true });
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

await finalizePresentation({
  explicitTotalSlideCount: 1,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
  workspaceDir,
  candidatePath,
  finalPath: finalPptx,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  fontPolicy: {
    basis: "design",
    families: [fontFamily],
    scriptFonts: { ea: fontFamily },
  },
  verifyArtifactToolImport: true,
  receiptPath,
});

const finalDeck = await PresentationFile.importPptx(await FileBlob.load(finalPptx));
const preview = await finalDeck.slides.getItem(0).export({ format: "png", scale: 1 });
await fs.writeFile(finalPptx.replace(/\.pptx$/i, "-preview.png"), new Uint8Array(await preview.arrayBuffer()));

console.log(finalPptx);
process.exit(0);
