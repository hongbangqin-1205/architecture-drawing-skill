# Test Cases

## Case 1: Dense Report To Business Architecture

Input: a long DOCX report with many projects and implementation details.

Expected:

- The output retains only the architecture backbone.
- The slide uses concise labels and aligned groups.
- The result is one editable 16:9 PPTX slide.
- The preview does not reproduce report paragraphs.

## Case 2: Reference Image To Technical Blueprint

Input: a screenshot with left layer labels, central module bands, and a right sidebar.

Expected:

- The reference image is translated into editable regions rather than embedded.
- Layer labels, module cells, connectors, and sidebar are native PPT objects.
- Shared column boundaries and spacing are visually regular.
- The blueprint uses a restrained blue/cyan accent palette.

## Case 3: Data-Structure Matrix

Input: a data architecture description with application domains, open APIs, governance libraries, and data sources.

Expected:

- The diagram uses the `应用层 -> 开放层 -> 治理层 -> 数据源` reading order.
- Each application-domain group contains no more than four short data items.
- Data sources and external systems remain distinguishable from internal capabilities.

## Case 4: Editable Package Check

Input: a generated PPTX.

Expected:

- The file imports successfully through `@oai/artifact-tool`.
- Package integrity and layout geometry validators pass.
- Font policy includes the selected East Asian font.
- `ppt/media/` contains no primary diagram image for a pure shape diagram.

## Case 5: Text Fit And Crop

Input: the generated preview and layout inspection output.

Expected:

- No text extends outside its module, title frame, layer rail, or sidebar box.
- No bottom content is cropped.
- Connectors do not cross labels or module text.
