#!/usr/bin/env python3
"""Validate Markdown feature test plans and execution reports."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


TEST_ID_RE = re.compile(r"\bT(\d+)\b")
REQ_ID_RE = re.compile(r"\b(AC|REQ|R)[-_]?(\d+)\b", re.IGNORECASE)
SUPPORT_ID_RE = re.compile(r"\b([SC])(\d+)\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\{\{[^}\n]+\}\}")
VALID_PLAN_STATUSES = {"NOT_RUN", "✅ PASS", "❌ FAIL", "⚠️ BLOCKED"}
VALID_RESULTS = {"✅ PASS", "❌ FAIL", "⚠️ BLOCKED", "NOT_RUN"}
VALID_COVERAGE_STATUSES = {"Covered", "Confirmed Excluded"}
VALID_LOOP_PROGRESS = {"CONTINUE", "REPAIR"}
VALID_LOOP_TERMINAL = {
    "READY_TO_FREEZE",
    "LOOP_LIMIT_REACHED",
    "NEEDS_CONFIRMATION",
    "SCOPE_UNSTABLE",
}


@dataclass
class Table:
    headers: list[str]
    rows: list[list[str]]


@dataclass
class PlanData:
    test_ids: set[str]
    loop_result: str
    plan_version: str
    source_fingerprint: str
    frozen_test_ids: set[str]


def normalize_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("| "))


def split_table_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|") and not value.endswith(r"\|"):
        value = value[:-1]
    return [normalize_cell(cell.replace(r"\|", "|")) for cell in re.split(r"(?<!\\)\|", value)]


def section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(markdown)
    return match.group(1) if match else ""


def parse_first_table(text: str) -> Table | None:
    lines = text.splitlines()
    for index in range(len(lines) - 1):
        if not lines[index].lstrip().startswith("|"):
            continue
        if not re.match(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$", lines[index + 1]):
            continue
        headers = split_table_row(lines[index])
        rows: list[list[str]] = []
        for line in lines[index + 2 :]:
            if not line.lstrip().startswith("|"):
                break
            cells = split_table_row(line)
            if len(cells) == len(headers):
                rows.append(cells)
        return Table(headers, rows)
    return None


def column_index(table: Table, name: str) -> int | None:
    try:
        return table.headers.index(name)
    except ValueError:
        return None


def expand_test_ids(value: str) -> list[str]:
    expanded: list[str] = []
    range_pattern = re.compile(r"T(\d+)\s*[–—-]\s*T?(\d+)")
    consumed: list[tuple[int, int]] = []
    for match in range_pattern.finditer(value):
        start, end = int(match.group(1)), int(match.group(2))
        if end < start or end - start > 1000:
            continue
        width = max(len(match.group(1)), len(match.group(2)))
        expanded.extend(f"T{number:0{width}d}" for number in range(start, end + 1))
        consumed.append(match.span())
    remainder = value
    for start, end in reversed(consumed):
        remainder = remainder[:start] + " " * (end - start) + remainder[end:]
    expanded.extend(f"T{match.group(1)}" for match in TEST_ID_RE.finditer(remainder))
    return expanded


def canonical_requirement(prefix: str, number: str, width: int | None = None) -> str:
    normalized_width = width if width is not None else len(number)
    return f"{prefix.upper()}-{int(number):0{normalized_width}d}"


def expand_requirement_ids(value: str) -> list[str]:
    expanded: list[str] = []
    range_pattern = re.compile(
        r"\b(AC|REQ|R)[-_]?(\d+)(?:\s*[–—]\s*|\s+-\s+)(?:(AC|REQ|R)[-_]?)?(\d+)\b",
        re.IGNORECASE,
    )
    consumed: list[tuple[int, int]] = []
    for match in range_pattern.finditer(value):
        prefix = match.group(1).upper()
        end_prefix = (match.group(3) or prefix).upper()
        start, end = int(match.group(2)), int(match.group(4))
        if prefix != end_prefix or end < start or end - start > 1000:
            continue
        width = max(len(match.group(2)), len(match.group(4)))
        expanded.extend(canonical_requirement(prefix, str(number), width) for number in range(start, end + 1))
        consumed.append(match.span())
    remainder = value
    for start, end in reversed(consumed):
        remainder = remainder[:start] + " " * (end - start) + remainder[end:]
    expanded.extend(
        canonical_requirement(match.group(1), match.group(2)) for match in REQ_ID_RE.finditer(remainder)
    )
    return expanded


def extract_support_ids(value: str) -> list[str]:
    return [f"{match.group(1).upper()}{match.group(2)}" for match in SUPPORT_ID_RE.finditer(value)]


def require_sections(markdown: str, names: list[str], errors: list[str]) -> None:
    for name in names:
        if not section(markdown, name):
            errors.append(f"缺少必要章節：## {name}")


def require_headers(table: Table, headers: list[str], label: str, errors: list[str]) -> bool:
    missing = [header for header in headers if header not in table.headers]
    if missing:
        errors.append(f"{label}缺少欄位：" + ", ".join(missing))
        return False
    return True


def table_items(text: str, key_header: str, value_header: str) -> dict[str, str]:
    table = parse_first_table(text)
    if table is None:
        return {}
    key_col = column_index(table, key_header)
    value_col = column_index(table, value_header)
    if key_col is None or value_col is None:
        return {}
    return {row[key_col]: row[value_col] for row in table.rows if row[key_col]}


def extract_plan_data(markdown: str) -> PlanData:
    test_table = parse_first_table(section(markdown, "測試項目"))
    test_ids: set[str] = set()
    if test_table is not None:
        id_col = column_index(test_table, "ID")
        if id_col is not None:
            test_ids = {row[id_col] for row in test_table.rows if re.fullmatch(r"T\d+", row[id_col])}
    loop_table = parse_first_table(section(markdown, "Completeness Loop"))
    loop_result = ""
    if loop_table is not None:
        result_col = column_index(loop_table, "結果")
        if result_col is not None and loop_table.rows:
            loop_result = loop_table.rows[-1][result_col]
    freeze = table_items(section(markdown, "計畫凍結"), "項目", "內容")
    return PlanData(
        test_ids=test_ids,
        loop_result=loop_result,
        plan_version=freeze.get("Plan 版本", ""),
        source_fingerprint=freeze.get("來源指紋", ""),
        frozen_test_ids=set(expand_test_ids(freeze.get("凍結案例集合", ""))),
    )


def validate_source_ledger(markdown: str, errors: list[str]) -> None:
    table = parse_first_table(section(markdown, "來源盤點"))
    if table is None:
        errors.append("找不到來源盤點表格")
        return
    headers = ["來源 ID", "類型", "位置 / 版本", "內容 / 範圍", "狀態"]
    if not require_headers(table, headers, "來源盤點", errors):
        return
    if not table.rows:
        errors.append("來源盤點沒有來源")
        return
    id_col = column_index(table, "來源 ID")
    assert id_col is not None
    seen: set[str] = set()
    for row_number, row in enumerate(table.rows, start=1):
        for header in headers:
            index = column_index(table, header)
            assert index is not None
            if not row[index]:
                errors.append(f"來源盤點第 {row_number} 筆欄位不可為空：{header}")
        source_id = row[id_col]
        if not re.fullmatch(r"SRC-\d+", source_id):
            errors.append(f"來源 ID 無效：{source_id}")
        elif source_id in seen:
            errors.append(f"來源 ID 重複：{source_id}")
        seen.add(source_id)


def validate_completeness_loop(
    markdown: str, test_ids: set[str], allow_placeholders: bool, errors: list[str]
) -> None:
    table = parse_first_table(section(markdown, "Completeness Loop"))
    if table is None:
        errors.append("找不到 Completeness Loop 表格")
        return
    headers = ["Round", "審查視角", "來源版本 / Hash", "新增需求 / AC", "新增案例", "未解缺口", "結果"]
    if not require_headers(table, headers, "Completeness Loop", errors):
        return
    if len(table.rows) < 2 or len(table.rows) > 3:
        errors.append("Completeness Loop 必須至少 2 輪、最多 3 輪")
        return
    indexes = {header: column_index(table, header) for header in headers}
    assert all(index is not None for index in indexes.values())
    numeric_rows: list[tuple[int, int, int]] = []
    for expected_round, row in enumerate(table.rows, start=1):
        round_value = row[indexes["Round"]]  # type: ignore[index]
        if round_value != str(expected_round):
            errors.append(f"Completeness Loop Round 應依序為 {expected_round}：{round_value}")
        values: list[int] = []
        for header in ("新增需求 / AC", "新增案例", "未解缺口"):
            value = row[indexes[header]]  # type: ignore[index]
            if not re.fullmatch(r"\d+", value):
                if not (allow_placeholders and PLACEHOLDER_RE.search(value)):
                    errors.append(f"Round {expected_round} 的 {header} 必須是非負整數：{value}")
                values.append(-1)
            else:
                values.append(int(value))
        numeric_rows.append((values[0], values[1], values[2]))
        result = row[indexes["結果"]]  # type: ignore[index]
        if expected_round < len(table.rows) and result not in VALID_LOOP_PROGRESS:
            errors.append(f"非最後一輪結果必須是 CONTINUE 或 REPAIR：Round {expected_round}={result}")
    final_result = table.rows[-1][indexes["結果"]]  # type: ignore[index]
    if final_result not in VALID_LOOP_TERMINAL:
        errors.append(f"最後一輪結果無效：{final_result}")
    new_requirements, new_cases, unresolved = numeric_rows[-1]
    if final_result == "READY_TO_FREEZE" and any(value != 0 for value in numeric_rows[-1]):
        errors.append("READY_TO_FREEZE 的最後一輪必須新增需求=0、新增案例=0、未解缺口=0")
    if final_result == "LOOP_LIMIT_REACHED" and len(table.rows) != 3:
        errors.append("LOOP_LIMIT_REACHED 只能出現在第 3 輪")
    if final_result == "LOOP_LIMIT_REACHED" and not any(
        value > 0 for value in (new_requirements, new_cases, unresolved)
    ):
        errors.append("LOOP_LIMIT_REACHED 必須保留第 3 輪新發現的範圍或缺口")
    if final_result == "NEEDS_CONFIRMATION" and unresolved <= 0:
        errors.append("NEEDS_CONFIRMATION 必須有未解缺口")
    if len(table.rows) == 3 and any(value > 0 for value in (new_requirements, new_cases, unresolved)):
        if final_result == "READY_TO_FREEZE":
            errors.append("第 3 輪仍有新增或缺口時不得凍結計畫")

    freeze = table_items(section(markdown, "計畫凍結"), "項目", "內容")
    for key in ("Loop 結果", "Plan 版本", "來源指紋", "凍結案例集合"):
        if not freeze.get(key):
            errors.append(f"計畫凍結缺少項目：{key}")
    if freeze.get("Loop 結果") and freeze["Loop 結果"] != final_result:
        errors.append("計畫凍結的 Loop 結果與最後一輪不一致")
    frozen_ids = set(expand_test_ids(freeze.get("凍結案例集合", "")))
    if final_result == "READY_TO_FREEZE":
        if not allow_placeholders and not freeze.get("Plan 版本"):
            errors.append("READY_TO_FREEZE 必須記錄 Plan 版本")
        if not allow_placeholders and not freeze.get("來源指紋"):
            errors.append("READY_TO_FREEZE 必須記錄來源指紋")
        if frozen_ids != test_ids:
            missing = sorted(test_ids - frozen_ids)
            extra = sorted(frozen_ids - test_ids)
            if missing:
                errors.append("凍結案例集合遺漏：" + ", ".join(missing))
            if extra:
                errors.append("凍結案例集合引用不存在案例：" + ", ".join(extra))
    elif frozen_ids:
        errors.append(f"{final_result} 尚不可凍結測試案例集合")


def validate_resource_gates(markdown: str, errors: list[str]) -> None:
    table = parse_first_table(section(markdown, "資源預算與門檻"))
    if table is None:
        errors.append("找不到資源預算與門檻表格")
        return
    headers = ["類型", "基準 / 來源", "門檻", "觸發動作"]
    if not require_headers(table, headers, "資源預算與門檻", errors):
        return
    type_col = column_index(table, "類型")
    baseline_col = column_index(table, "基準 / 來源")
    threshold_col = column_index(table, "門檻")
    action_col = column_index(table, "觸發動作")
    assert type_col is not None and baseline_col is not None and threshold_col is not None and action_col is not None
    rows: dict[str, list[str]] = {}
    for row in table.rows:
        if row[type_col] in rows:
            errors.append(f"資源預算與門檻類型重複：{row[type_col]}")
        rows[row[type_col]] = row
    for gate in ("週用量", "Build", "重試"):
        if gate not in rows:
            errors.append(f"資源預算與門檻缺少：{gate}")
    if "週用量" in rows:
        baseline = rows["週用量"][baseline_col]
        threshold = rows["週用量"][threshold_col]
        action = rows["週用量"][action_col]
        if "Unavailable" not in baseline and not re.search(r"\b\d+(?:\.\d+)?%", baseline):
            errors.append("週用量基準必須記錄可讀百分比或 Unavailable")
        if "5" not in threshold or "百分點" not in threshold:
            errors.append("週用量門檻必須是每下降 5 個百分點")
        if "詢問" not in action and "確認" not in action:
            errors.append("週用量觸發動作必須要求使用者確認")
    if "Build" in rows:
        threshold = rows["Build"][threshold_col]
        action = rows["Build"][action_col]
        if "5" not in threshold or "分鐘" not in threshold:
            errors.append("Build 門檻必須包含 5 分鐘")
        if "詢問" not in action and "確認" not in action:
            errors.append("Build 超時必須詢問是否延長")
    if "重試" in rows:
        threshold = rows["重試"][threshold_col]
        action = rows["重試"][action_col]
        if "2" not in threshold or "次" not in threshold:
            errors.append("重試門檻必須是最多 2 次")
        if "詢問" not in action and "確認" not in action:
            errors.append("第 3 次重試前必須詢問使用者")


def validate_plan(markdown: str, require_not_run: bool, allow_placeholders: bool) -> list[str]:
    errors: list[str] = []
    require_sections(
        markdown,
        [
            "來源",
            "來源盤點",
            "測試前提",
            "需求覆蓋",
            "測試項目",
            "測試支援與清理計畫",
            "Completeness Loop",
            "計畫凍結",
            "資源預算與門檻",
            "Token / Log 控制",
        ],
        errors,
    )
    validate_source_ledger(markdown, errors)

    test_table = parse_first_table(section(markdown, "測試項目"))
    if test_table is None:
        errors.append("找不到測試項目表格")
        return errors
    test_headers = [
        "ID",
        "需求 / AC",
        "優先級",
        "測試類型",
        "前置條件",
        "操作 / 檢查方式",
        "預期結果",
        "驗證層級",
        "支援 / 清理",
        "Token / Log 控制",
        "狀態",
    ]
    if not require_headers(test_table, test_headers, "測試項目", errors):
        return errors
    if not test_table.rows:
        errors.append("測試項目表格沒有案例")
        return errors

    id_col = column_index(test_table, "ID")
    req_col = column_index(test_table, "需求 / AC")
    priority_col = column_index(test_table, "優先級")
    support_col = column_index(test_table, "支援 / 清理")
    status_col = column_index(test_table, "狀態")
    assert None not in (id_col, req_col, priority_col, support_col, status_col)

    test_ids: set[str] = set()
    case_requirements: dict[str, set[str]] = {}
    case_support: dict[str, set[str]] = {}
    for row_number, row in enumerate(test_table.rows, start=1):
        for header in test_headers:
            index = column_index(test_table, header)
            assert index is not None
            if not row[index]:
                errors.append(f"第 {row_number} 筆案例欄位不可為空：{header}")
        test_id = row[id_col]  # type: ignore[index]
        if not re.fullmatch(r"T\d+", test_id):
            errors.append(f"第 {row_number} 筆案例 ID 無效：{test_id}")
        elif test_id in test_ids:
            errors.append(f"測試案例 ID 重複：{test_id}")
        test_ids.add(test_id)
        requirement_ids = set(expand_requirement_ids(row[req_col]))  # type: ignore[index]
        if not requirement_ids:
            errors.append(f"{test_id} 未映射有效需求 / AC")
        case_requirements[test_id] = requirement_ids
        case_support[test_id] = set(extract_support_ids(row[support_col]))  # type: ignore[index]
        if row[priority_col] not in {"P0", "P1", "P2"}:  # type: ignore[index]
            errors.append(f"{test_id} 優先級無效：{row[priority_col]}")  # type: ignore[index]
        if row[status_col] not in VALID_PLAN_STATUSES:  # type: ignore[index]
            errors.append(f"{test_id} 狀態無效：{row[status_col]}")  # type: ignore[index]
        if require_not_run and row[status_col] != "NOT_RUN":  # type: ignore[index]
            errors.append(f"新計畫案例必須是 NOT_RUN：{test_id}")

    coverage_table = parse_first_table(section(markdown, "需求覆蓋"))
    coverage_requirements: dict[str, set[str]] = {}
    excluded_requirements: set[str] = set()
    if coverage_table is None:
        errors.append("找不到需求覆蓋表格")
    else:
        coverage_headers = ["需求 / AC", "來源與預期", "測試案例", "覆蓋狀態"]
        if require_headers(coverage_table, coverage_headers, "需求覆蓋", errors):
            cov_req_col = column_index(coverage_table, "需求 / AC")
            cov_test_col = column_index(coverage_table, "測試案例")
            cov_status_col = column_index(coverage_table, "覆蓋狀態")
            assert cov_req_col is not None and cov_test_col is not None and cov_status_col is not None
            for row in coverage_table.rows:
                requirements = set(expand_requirement_ids(row[cov_req_col]))
                mapped_tests = set(expand_test_ids(row[cov_test_col]))
                status = row[cov_status_col]
                if not requirements:
                    errors.append(f"需求覆蓋列沒有有效需求 ID：{row[cov_req_col]}")
                if status not in VALID_COVERAGE_STATUSES:
                    errors.append(f"需求覆蓋狀態無效：{status}")
                for requirement in requirements:
                    if requirement in coverage_requirements or requirement in excluded_requirements:
                        errors.append(f"需求覆蓋重複：{requirement}")
                    if status == "Confirmed Excluded":
                        excluded_requirements.add(requirement)
                    else:
                        coverage_requirements[requirement] = mapped_tests
                        if not mapped_tests:
                            errors.append(f"Covered 需求沒有測試案例：{requirement}")
                for test_id in mapped_tests:
                    if test_id not in test_ids:
                        errors.append(f"需求覆蓋表引用不存在的案例：{test_id}")

    for test_id, requirements in case_requirements.items():
        for requirement in requirements:
            if requirement not in coverage_requirements:
                errors.append(f"{test_id} 引用未列入 Covered 的需求：{requirement}")
            elif test_id not in coverage_requirements[requirement]:
                errors.append(f"需求覆蓋表未建立 {requirement} → {test_id} 對應")
    for requirement, mapped_tests in coverage_requirements.items():
        for test_id in mapped_tests:
            if requirement not in case_requirements.get(test_id, set()):
                errors.append(f"{test_id} 未反向引用需求覆蓋中的 {requirement}")

    support_table = parse_first_table(section(markdown, "測試支援與清理計畫"))
    declared_support: set[str] = set()
    support_cases: dict[str, set[str]] = {}
    if support_table is not None:
        support_headers = ["ID", "適用案例", "建立 / 變更內容", "隔離方式", "確認狀態", "清理方式", "清理驗證"]
        if require_headers(support_table, support_headers, "測試支援與清理計畫", errors):
            support_id_col = column_index(support_table, "ID")
            support_test_col = column_index(support_table, "適用案例")
            assert support_id_col is not None and support_test_col is not None
            for row in support_table.rows:
                ids = set(extract_support_ids(row[support_id_col]))
                applicable = set(expand_test_ids(row[support_test_col]))
                if not ids:
                    errors.append(f"測試支援列沒有有效 S/C ID：{row[support_id_col]}")
                for support_id in ids:
                    if support_id in declared_support:
                        errors.append(f"測試支援 / 清理 ID 重複：{support_id}")
                    declared_support.add(support_id)
                    support_cases[support_id] = applicable
                for test_id in applicable:
                    if test_id not in test_ids:
                        errors.append(f"測試支援表引用不存在案例：{test_id}")
    referenced_support = set().union(*case_support.values()) if case_support else set()
    for support_id in sorted(referenced_support - declared_support):
        errors.append(f"案例引用未宣告的測試支援 / 清理 ID：{support_id}")
    for support_id in sorted(declared_support - referenced_support):
        errors.append(f"測試支援 / 清理 ID 未被任何案例引用：{support_id}")
    for test_id, support_ids in case_support.items():
        for support_id in support_ids:
            if support_id in support_cases and test_id not in support_cases[support_id]:
                errors.append(f"{support_id} 的適用案例未列出 {test_id}")

    validate_completeness_loop(markdown, test_ids, allow_placeholders, errors)
    validate_resource_gates(markdown, errors)
    return errors


def summary_count(markdown: str, label: str) -> int | None:
    match = re.search(rf"^- {re.escape(label)}：\s*(\d+)\s*$", markdown, re.MULTILINE)
    return int(match.group(1)) if match else None


def summary_value(markdown: str, label: str) -> str | None:
    match = re.search(rf"^- {re.escape(label)}：\s*(.+?)\s*$", markdown, re.MULTILINE)
    return match.group(1) if match else None


def validate_report(markdown: str, plan_markdown: str | None) -> list[str]:
    errors: list[str] = []
    require_sections(markdown, ["測試前提", "測試結果", "總結"], errors)
    table = parse_first_table(section(markdown, "測試結果"))
    if table is None:
        errors.append("找不到測試結果表格")
        return errors
    headers = ["案例 ID / 範圍", "測試項目", "結果", "驗證內容 / 失敗原因", "下一步"]
    if not require_headers(table, headers, "測試結果", errors):
        return errors
    ids_col = column_index(table, "案例 ID / 範圍")
    result_col = column_index(table, "結果")
    assert ids_col is not None and result_col is not None
    case_results: dict[str, str] = {}
    for row_number, row in enumerate(table.rows, start=1):
        for header in headers:
            index = column_index(table, header)
            assert index is not None
            if not row[index]:
                errors.append(f"第 {row_number} 筆結果欄位不可為空：{header}")
        result = row[result_col]
        ids = expand_test_ids(row[ids_col])
        if not ids:
            errors.append(f"第 {row_number} 筆結果沒有有效案例 ID")
        if result not in VALID_RESULTS:
            errors.append(f"第 {row_number} 筆結果狀態無效：{result}")
        for test_id in ids:
            if test_id in case_results:
                errors.append(f"報告案例 ID 重複或範圍重疊：{test_id}")
            case_results[test_id] = result

    labels = {"PASS": "✅ PASS", "FAIL": "❌ FAIL", "BLOCKED": "⚠️ BLOCKED", "NOT_RUN": "NOT_RUN"}
    actual_counts: dict[str, int] = {}
    for label, result in labels.items():
        reported = summary_count(markdown, label)
        actual = sum(value == result for value in case_results.values())
        actual_counts[label] = actual
        if reported is None:
            errors.append(f"總結缺少 {label} 數量")
        elif reported != actual:
            errors.append(f"{label} 統計不一致：總結 {reported}，案例 {actual}")

    coverage = summary_value(markdown, "執行覆蓋")
    if coverage is None:
        errors.append("總結缺少執行覆蓋")
    else:
        match = re.search(r"(\d+)\s*/\s*(\d+)", coverage)
        executed = actual_counts["PASS"] + actual_counts["FAIL"]
        total = len(case_results)
        if match is None:
            errors.append("執行覆蓋必須包含 executed / total")
        elif (int(match.group(1)), int(match.group(2))) != (executed, total):
            errors.append(
                f"執行覆蓋不一致：總結 {match.group(1)} / {match.group(2)}，案例 {executed} / {total}"
            )

    pass_rate = summary_value(markdown, "通過率")
    if pass_rate is None:
        errors.append("總結缺少通過率")
    else:
        executed = actual_counts["PASS"] + actual_counts["FAIL"]
        if executed == 0:
            if pass_rate.upper() != "N/A":
                errors.append("沒有已執行案例時，通過率必須是 N/A")
        else:
            match = re.fullmatch(r"(\d+(?:\.\d+)?)%", pass_rate)
            expected = actual_counts["PASS"] / executed * 100
            if match is None:
                errors.append("通過率必須是百分比，例如 66.7%")
            elif abs(float(match.group(1)) - expected) > 0.51:
                errors.append(f"通過率不一致：總結 {match.group(1)}%，案例計算 {expected:.1f}%")

    if plan_markdown is None:
        errors.append("執行報告必須提供原始計畫進行案例集合對帳")
        return errors
    plan = extract_plan_data(plan_markdown)
    if plan.loop_result != "READY_TO_FREEZE":
        errors.append(f"原始計畫尚未 READY_TO_FREEZE：{plan.loop_result or 'missing'}")
    report_ids = set(case_results)
    expected_ids = plan.frozen_test_ids or plan.test_ids
    if report_ids != expected_ids:
        missing = sorted(expected_ids - report_ids)
        extra = sorted(report_ids - expected_ids)
        if missing:
            errors.append("報告遺漏凍結案例：" + ", ".join(missing))
        if extra:
            errors.append("報告包含非凍結案例：" + ", ".join(extra))
    premises = table_items(section(markdown, "測試前提"), "項目", "內容")
    if premises.get("Plan 版本") != plan.plan_version:
        errors.append("報告 Plan 版本與凍結計畫不一致")
    if premises.get("來源指紋") != plan.source_fingerprint:
        errors.append("報告來源指紋與凍結計畫不一致")
    return errors


def validate(
    markdown: str,
    kind: str,
    require_not_run: bool,
    allow_placeholders: bool,
    plan_markdown: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if not allow_placeholders:
        placeholders = sorted(set(PLACEHOLDER_RE.findall(markdown)))
        if placeholders:
            errors.append("仍有未填寫 placeholder：" + ", ".join(placeholders[:5]))
    if kind == "plan":
        errors.extend(validate_plan(markdown, require_not_run, allow_placeholders))
    else:
        errors.extend(validate_report(markdown, plan_markdown))
    return errors


def run_self_test() -> int:
    plan = """# 測試計劃：Example
## 來源
ok
## 來源盤點
| 來源 ID | 類型 | 位置 / 版本 | 內容 / 範圍 | 狀態 |
|---|---|---|---|---|
| SRC-001 | Spec | spec-v1 | AC-1 | Locked |
## 測試前提
ok
## 不納入範圍
none
## 需求覆蓋
| 需求 / AC | 來源與預期 | 測試案例 | 覆蓋狀態 |
|---|---|---|---|
| AC-1 | observable | T001-T003 | Covered |
## 測試項目
| ID | 需求 / AC | 優先級 | 測試類型 | 前置條件 | 操作 / 檢查方式 | 預期結果 | 驗證層級 | 支援 / 清理 | Token / Log 控制 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|
| T001 | AC-1 | P0 | API | ready | run | success | Automated | none | focused | NOT_RUN |
| T002 | AC-1 | P1 | State | ready | run | success | Runtime/Device | none | focused | NOT_RUN |
| T003 | AC-1 | P1 | Regression | ready | run | success | Automated | none | focused | NOT_RUN |
## 測試支援與清理計畫
none
## Completeness Loop
| Round | 審查視角 | 來源版本 / Hash | 新增需求 / AC | 新增案例 | 未解缺口 | 結果 |
|---|---|---|---:|---:|---:|---|
| 1 | Spec-first | abc123 | 1 | 3 | 0 | CONTINUE |
| 2 | Code/Failure-first | unchanged | 0 | 0 | 0 | READY_TO_FREEZE |
## 計畫凍結
| 項目 | 內容 |
|---|---|
| Loop 結果 | READY_TO_FREEZE |
| Plan 版本 | v1 |
| 來源指紋 | abc123 |
| 凍結案例集合 | T001-T003 |
## 資源預算與門檻
| 類型 | 基準 / 來源 | 門檻 | 觸發動作 |
|---|---|---|---|
| 週用量 | telemetry or Unavailable | 每下降 5 個百分點 | 詢問是否繼續 |
| Build | monitored command | 5 分鐘 | 停止並詢問是否延長 |
| 重試 | unchanged action | 最多 2 次 | 第 3 次前詢問 |
## Token / Log 控制
focused
"""
    report = """# Example 測試報告
## 測試前提
| # | 項目 | 內容 |
|---|---|---|
| 1 | Plan 版本 | v1 |
| 2 | 來源指紋 | abc123 |
## 測試結果
| 案例 ID / 範圍 | 測試項目 | 結果 | 驗證內容 / 失敗原因 | 下一步 |
|---|---|---|---|---|
| T001-T002 | flow | ✅ PASS | evidence | 無 |
| T003 | error | ❌ FAIL | mismatch | fix |
## 總結
- PASS：2
- FAIL：1
- BLOCKED：0
- NOT_RUN：0
- 執行覆蓋：3 / 3
- 通過率：66.7%
"""
    failures = validate(plan, "plan", True, False) + validate(
        report, "report", False, False, plan
    )
    if failures:
        for failure in failures:
            print(f"SELF-TEST FAIL: {failure}", file=sys.stderr)
        return 1

    expected_requirement_range = ["AC-09", "AC-10", "AC-11", "AC-12"]
    if expand_requirement_ids("AC-09–AC-12") != expected_requirement_range:
        print("SELF-TEST FAIL: requirement range expansion is incorrect", file=sys.stderr)
        return 1

    negative_checks = {
        "invalid priority": plan.replace("| T001 | AC-1 | P0", "| T001 | AC-1 | P3"),
        "unknown requirement": plan.replace("| T001 | AC-1 | P0", "| T001 | AC-2 | P0"),
        "orphan support": plan.replace("| T001 | AC-1 | P0 | API | ready | run | success | Automated | none |", "| T001 | AC-1 | P0 | API | ready | run | success | Automated | S001 / C001 |"),
        "invalid loop freeze": plan.replace("| 2 | Code/Failure-first | unchanged | 0 | 0 | 0 | READY_TO_FREEZE |", "| 2 | Code/Failure-first | unchanged | 0 | 1 | 0 | READY_TO_FREEZE |"),
        "invalid usage baseline": plan.replace("| 週用量 | telemetry or Unavailable |", "| 週用量 | guessed usage |"),
    }
    for label, invalid_plan in negative_checks.items():
        if not validate(invalid_plan, "plan", True, False):
            print(f"SELF-TEST FAIL: {label} was not detected", file=sys.stderr)
            return 1

    four_round_plan = plan.replace(
        "| 2 | Code/Failure-first | unchanged | 0 | 0 | 0 | READY_TO_FREEZE |",
        "| 2 | Code/Failure-first | unchanged | 1 | 1 | 0 | REPAIR |\n"
        "| 3 | Delta audit | changed | 1 | 1 | 0 | REPAIR |\n"
        "| 4 | Extra audit | changed | 0 | 0 | 0 | READY_TO_FREEZE |",
    )
    if not validate(four_round_plan, "plan", True, False):
        print("SELF-TEST FAIL: fourth loop round was not detected", file=sys.stderr)
        return 1

    invalid_report = report.replace("- PASS：2", "- PASS：1")
    if not validate(invalid_report, "report", False, False, plan):
        print("SELF-TEST FAIL: result count mismatch was not detected", file=sys.stderr)
        return 1

    omitted_report = report.replace("| T003 | error | ❌ FAIL | mismatch | fix |\n", "").replace(
        "- FAIL：1\n", "- FAIL：0\n"
    ).replace("- 執行覆蓋：3 / 3", "- 執行覆蓋：2 / 2").replace(
        "- 通過率：66.7%", "- 通過率：100.0%"
    )
    omitted_errors = validate(omitted_report, "report", False, False, plan)
    if not any("報告遺漏凍結案例" in error for error in omitted_errors):
        print("SELF-TEST FAIL: plan/report case mismatch was not detected", file=sys.stderr)
        return 1

    zero_execution_report = """# Blocked 測試報告
## 測試前提
| # | 項目 | 內容 |
|---|---|---|
| 1 | Plan 版本 | v1 |
| 2 | 來源指紋 | abc123 |
## 測試結果
| 案例 ID / 範圍 | 測試項目 | 結果 | 驗證內容 / 失敗原因 | 下一步 |
|---|---|---|---|---|
| T001 | device flow | ⚠️ BLOCKED | no device | connect device |
| T002-T003 | remaining | NOT_RUN | not started | resume later |
## 總結
- PASS：0
- FAIL：0
- BLOCKED：1
- NOT_RUN：2
- 執行覆蓋：0 / 3
- 通過率：N/A
"""
    zero_failures = validate(zero_execution_report, "report", False, False, plan)
    if zero_failures:
        for failure in zero_failures:
            print(f"SELF-TEST FAIL: {failure}", file=sys.stderr)
        return 1
    print("Self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--kind", choices=("plan", "report"))
    parser.add_argument("--plan", type=Path, help="Frozen plan required for report validation")
    parser.add_argument("--require-not-run", action="store_true")
    parser.add_argument("--allow-placeholders", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.path is None or args.kind is None:
        parser.error("path and --kind are required unless --self-test is used")
    if not args.path.is_file():
        print(f"找不到檔案：{args.path}", file=sys.stderr)
        return 2
    if args.kind == "report" and args.plan is None:
        parser.error("--plan is required when --kind report")
    if args.kind == "plan" and args.plan is not None:
        parser.error("--plan can only be used with --kind report")

    markdown = args.path.read_text(encoding="utf-8")
    plan_markdown: str | None = None
    errors: list[str] = []
    if args.plan is not None:
        if not args.plan.is_file():
            print(f"找不到原始計畫：{args.plan}", file=sys.stderr)
            return 2
        plan_markdown = args.plan.read_text(encoding="utf-8")
        plan_errors = validate(plan_markdown, "plan", False, False)
        errors.extend(f"原始計畫：{error}" for error in plan_errors)
    errors.extend(
        validate(markdown, args.kind, args.require_not_run, args.allow_placeholders, plan_markdown)
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid {args.kind}: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
