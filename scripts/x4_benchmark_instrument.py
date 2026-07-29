from pathlib import Path
import os

variant = os.environ.get("X4_BENCH_VARIANT", "UNKNOWN")
p = Path("src/activities/reader/EpubReaderActivity.cpp")
s = p.read_text()


def replace_once(old: str, new: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match, found {count}: {old[:120]!r}")
    s = s.replace(old, new, 1)


replace_once(
    "constexpr float bookmarkProgressEpsilon = 0.0001f;\n",
    "constexpr float bookmarkProgressEpsilon = 0.0001f;\n"
    f"constexpr char X4_BENCH_VARIANT[] = \"{variant}\";\n"
    "uint32_t x4BenchSeq = 0;\n"
    "uint32_t x4BenchActiveSeq = 0;\n"
    "unsigned long x4BenchInputMs = 0;\n"
    "unsigned long x4BenchRenderStartMs = 0;\n"
    "unsigned long x4BenchBwSubmitMs = 0;\n"
    "int x4BenchPageBefore = -1;\n",
)

replace_once(
    "void EpubReaderActivity::pageTurn(bool isForwardTurn) {\n",
    "void EpubReaderActivity::pageTurn(bool isForwardTurn) {\n"
    "  x4BenchActiveSeq = ++x4BenchSeq;\n"
    "  x4BenchInputMs = millis();\n"
    "  x4BenchBwSubmitMs = 0;\n"
    "  x4BenchPageBefore = section ? section->currentPage : -1;\n",
)

replace_once(
    "void EpubReaderActivity::render(RenderLock&& lock) {\n  if (!epub) {\n    return;\n  }\n",
    "void EpubReaderActivity::render(RenderLock&& lock) {\n  if (!epub) {\n    return;\n  }\n"
    "  x4BenchRenderStartMs = millis();\n",
)

replace_once(
    "    ReaderUtils::displayWithRefreshCycle(renderer, pagesUntilFullRefresh, overlapRefresh);\n",
    "    x4BenchBwSubmitMs = millis();\n"
    "    ReaderUtils::displayWithRefreshCycle(renderer, pagesUntilFullRefresh, overlapRefresh);\n",
)

replace_once(
    "  // Only persist when the position actually changed. render() also runs on menu,\n",
    "  const auto x4BenchContentsDoneMs = millis();\n"
    "  const auto x4BenchProgressStartMs = millis();\n"
    "  bool x4BenchDidSave = false;\n"
    "  // Only persist when the position actually changed. render() also runs on menu,\n",
)

replace_once(
    "  if (currentSpineIndex != lastSavedSpineIndex || section->currentPage != lastSavedPage ||\n      section->pageCount != lastSavedPageCount) {\n",
    "  if (currentSpineIndex != lastSavedSpineIndex || section->currentPage != lastSavedPage ||\n      section->pageCount != lastSavedPageCount) {\n"
    "    x4BenchDidSave = true;\n",
)

replace_once(
    "  showPendingSyncSaveError();\n\n  if (pendingScreenshot) {\n",
    "  const auto x4BenchProgressEndMs = millis();\n"
    "  showPendingSyncSaveError();\n\n  if (pendingScreenshot) {\n",
)

replace_once(
    "  if (showDictionaryMessage) {\n    GUI.drawPopup(renderer, tr(STR_DICT_NO_DICT_SET));\n  }\n}\n\nbool EpubReaderActivity::applyDeferredReposition() {\n",
    "  if (showDictionaryMessage) {\n    GUI.drawPopup(renderer, tr(STR_DICT_NO_DICT_SET));\n  }\n\n"
    "  const auto x4BenchRenderDoneMs = millis();\n"
    "  if (x4BenchInputMs != 0 && x4BenchActiveSeq != 0) {\n"
    "    const unsigned long inputToRender = x4BenchRenderStartMs - x4BenchInputMs;\n"
    "    const unsigned long inputToBwSubmit = x4BenchBwSubmitMs ? (x4BenchBwSubmitMs - x4BenchInputMs) : 0;\n"
    "    const unsigned long inputToContentsDone = x4BenchContentsDoneMs - x4BenchInputMs;\n"
    "    const unsigned long progressMs = x4BenchProgressEndMs - x4BenchProgressStartMs;\n"
    "    const unsigned long inputToDone = x4BenchRenderDoneMs - x4BenchInputMs;\n"
    "    LOG_INF(\"BENCH\",\n"
    "            \"variant=%s seq=%lu page_before=%d page_after=%d input_to_render=%lums input_to_bw_submit=%lums \"\n"
    "            \"input_to_contents_done=%lums progress=%lums input_to_done=%lums saved=%d\",\n"
    "            X4_BENCH_VARIANT, (unsigned long)x4BenchActiveSeq, x4BenchPageBefore,\n"
    "            section ? section->currentPage : -1, inputToRender, inputToBwSubmit, inputToContentsDone, progressMs,\n"
    "            inputToDone, x4BenchDidSave ? 1 : 0);\n"
    "    x4BenchInputMs = 0;\n"
    "    x4BenchActiveSeq = 0;\n"
    "  }\n"
    "}\n\nbool EpubReaderActivity::applyDeferredReposition() {\n",
)

p.write_text(s)
print(f"Instrumented {p} for variant {variant}")
