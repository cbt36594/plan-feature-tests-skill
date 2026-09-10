# Test Plan and Report Templates

## Contents

- Pre-test confirmation
- Test plan
- Execution report
- Template rules

## Pre-Test Confirmation

```md
## 測試前確認清單

| # | 類型 | 需要確認的內容 | 影響範圍 | 建議處理 |
|---|---|---|---|---|
| 1 | 測試基準 | {{spec/design/code difference}} | {{requirement and test IDs}} | {{recommended source of truth}} |
| 2 | 測試支援 | {{temporary mock, hook, account, or device change}} | {{test IDs}} | {{isolation and cleanup}} |
| 3 | 資源門檻 | {{usage/build/time extension}} | {{next stage or test IDs}} | {{continue/narrow/stop}} |
```

Resolve requirement ambiguity before executing affected cases. Record confirmed decisions under `測試前提`, confirmed exclusions under `不納入範圍`, and remaining execution barriers as `⚠️ BLOCKED` only after confirmation.

## Test Plan

```md
# 測試計劃：{{功能名稱}}

## 來源

| # | 項目 | 內容 |
|---|---|---|
| 1 | 開發文件 | {{path/title/version}} |
| 2 | 設計 / 截圖 | {{path/version/none}} |
| 3 | 實作範圍 | {{branch/commit/files/none}} |

## 來源盤點

| 來源 ID | 類型 | 位置 / 版本 | 內容 / 範圍 | 狀態 |
|---|---|---|---|---|
| SRC-001 | Spec | {{path/version/hash}} | {{requirements or exclusions}} | Locked |
| SRC-002 | Code | {{branch/commit/diff fingerprint}} | {{entry points/modules}} | Locked |

## 測試前提

| # | 項目 | 內容 |
|---|---|---|
| 1 | 專案 / 模組 | {{project/module}} |
| 2 | Branch / Commit | {{branch/commit}} |
| 3 | Build variant / Flavor | {{variant/flavor}} |
| 4 | 測試帳號 / 環境 | {{redacted account/environment}} |
| 5 | 裝置 / 平台 | {{device/screen size/OS/browser}} |
| 6 | 測試基準 | {{confirmed source of truth}} |
| 7 | 證據規則 | {{required level, retention, redaction}} |
| 8 | 清理基準 | {{repository/device/backend baseline}} |

## 不納入範圍

| 需求 ID | 項目 | 原因 | 確認依據 |
|---|---|---|---|
| {{EX-1}} | {{excluded behavior}} | {{reason}} | {{user/spec decision}} |

## 需求覆蓋

| 需求 / AC | 來源與預期 | 測試案例 | 覆蓋狀態 |
|---|---|---|---|
| AC-1 | {{observable requirement}} | T001 | Covered |

## 測試項目

| ID | 需求 / AC | 優先級 | 測試類型 | 前置條件 | 操作 / 檢查方式 | 預期結果 | 驗證層級 | 支援 / 清理 | Token / Log 控制 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|
| T001 | AC-1 | P0 | API | {{precondition}} | {{smallest executable action}} | {{observable outcome}} | Automated | S001 / C001 | {{focused command/log filter}} | NOT_RUN |

## 測試支援與清理計畫

| ID | 適用案例 | 建立 / 變更內容 | 隔離方式 | 確認狀態 | 清理方式 | 清理驗證 |
|---|---|---|---|---|---|---|
| S001 / C001 | T001 | {{fixture/mock/hook/package/device state}} | {{test/debug/non-production boundary}} | {{confirmed/not needed}} | {{exact cleanup}} | {{baseline check}} |

## Completeness Loop

| Round | 審查視角 | 來源版本 / Hash | 新增需求 / AC | 新增案例 | 未解缺口 | 結果 |
|---|---|---|---:|---:|---:|---|
| 1 | Spec-first inventory | {{source fingerprint}} | 1 | 1 | 0 | CONTINUE |
| 2 | Code/Failure-first audit | unchanged | 0 | 0 | 0 | READY_TO_FREEZE |

## 計畫凍結

| 項目 | 內容 |
|---|---|
| Loop 結果 | READY_TO_FREEZE |
| Plan 版本 | {{plan version}} |
| 來源指紋 | {{combined source fingerprint}} |
| 凍結案例集合 | T001 |

## 資源預算與門檻

| 類型 | 基準 / 來源 | 門檻 | 觸發動作 |
|---|---|---|---|
| 週用量 | 宿主可讀的週額度百分比、供應商、時間與重設窗口；否則 Unavailable | 每下降 5 個百分點 | 停止下一大型階段，回報進度並詢問是否繼續；不得用估算冒充 |
| 宿主能力 | 檔案、Python 3、Git／版本來源、程序監控與安全中斷、裝置／瀏覽器；各列 Available / Unavailable / Not Required | 依案例所需能力 | 缺少能力先解決受影響範圍；驗證器未執行標記 VALIDATION_NOT_RUN |
| Build | command、target、開始與最後進度時間 | 2 分鐘無進度提醒；5 分鐘停止 | 安全中斷並詢問是否延長；已知長 build 先取得授權 |
| 重試 | 相同 build/test/device flow | 最多 2 次 | 第 3 次前詢問；不穩定結果記 FAIL/flaky |
| 讀取 | 每輪新讀檔案 | 超過 20 個新檔 | 擴大前說明範圍與成本 |
| 工具輸出 | 單次結果 | 約 8,000 output tokens | 改讀 summary、聚焦範圍或 failure snippet |
| Runtime 批次 | 裝置 / runtime cases | 10 cases 或 15 分鐘 | 回報 checkpoint，再進下一批 |

## Token / Log 控制

| # | 類型 | 控制方式 |
|---|---|---|
| 1 | Completeness loop | Round 1 建 ledger；Round 2/3 聚焦 fingerprint delta、未解缺口與尚未檢查的相關呼叫路徑；遵守讀檔門檻 |
| 2 | Build / Unit test | 指定 module、variant、class 或 method；先讀 summary / failure snippet |
| 3 | Instrumentation | 指定 test class / method；先讀 structured result |
| 4 | Runtime log | 只抓 package、tag、keyword 或 request ID；遮罩 secrets / PII |
| 5 | UI evidence | 只在證明畫面狀態或 layout 問題時截圖 / 錄影 |
```

## Execution Report

```md
# {{功能名稱}} 測試報告

## 測試前提

| # | 項目 | 內容 |
|---|---|---|
| 1 | 專案 / 模組 | {{project/module}} |
| 2 | Branch / Commit | {{branch/commit}} |
| 3 | Variant / 環境 | {{variant/environment}} |
| 4 | 裝置 / 平台 | {{device/OS/browser}} |
| 5 | 測試基準 | {{confirmed source of truth}} |
| 6 | Plan 版本 | {{same frozen plan version}} |
| 7 | 來源指紋 | {{same frozen source fingerprint}} |

## 測試結果

| 案例 ID / 範圍 | 測試項目 | 結果 | 驗證內容 / 失敗原因 | 下一步 |
|---|---|---|---|---|
| T001 | {{what was tested}} | ✅ PASS | {{one-sentence redacted evidence}} | 無 |
| T002 | {{what was tested}} | ❌ FAIL | {{one-sentence cause}} | {{fix or retest}} |
| T003 | {{what was tested}} | ⚠️ BLOCKED | {{remaining execution barrier}} | {{unblock action}} |

## 實際測試參數

| 案例 ID | 參數 / 設定 | 實際值 | 來源 / 與計畫差異 |
|---|---|---|---|
| T001 | {{artifact, environment, initial state, fixture, command arguments, timeout/retry limits}} | {{actual value; N/A or NOT_CAPTURED with reason where necessary}} | {{runtime/config source and any drift}} |

## 完整測試流程

| 步驟 | 時間 / 時區 | 案例 ID | 實際操作 / 指令 / UI 選擇器 | 輸入參數 | 觀察結果 | 證據 |
|---|---|---|---|---|---|---|
| 1 | {{captured timestamp, or not recorded}} | T001 | {{actual setup/build/install/navigation/trigger/wait/retry/assertion/cleanup action}} | {{actual input}} | {{observed outcome, including failed attempts}} | {{valid attachment or log reference}} |

## Request / Response（不適用時標示 N/A）

| 案例 ID / Correlation | 擷取位置 | Method / 完整 Endpoint | Headers | 實際 Request Body | HTTP 狀態 | 實際 Response Body | 業務判定 |
|---|---|---|---|---|---|---|---|
| {{case and request ID}} | {{application/interceptor/network/server}} | {{observed method and URL}} | {{full captured headers or attachment}} | {{full body or attachment}} | {{observed status}} | {{full body or attachment}} | {{business code/message; separate from transport}} |

涉及加密或轉換時，分別附上實際序列化明文、送出 body 與解密後 response。保留原始欄位名稱及型別；預期結構或混淆對照另列，不改寫實際證據。

## 測試 Log

| 案例 ID | 擷取指令 / 篩選範圍 | 時間窗 / 時區 | 完整 Log 路徑 | 關鍵事件與行號 | 擷取限制 |
|---|---|---|---|---|---|
| {{case}} | {{process/tag/request filter}} | {{start/end}} | {{retained local attachment}} | {{failure, recovery, dispatch, response}} | {{none, truncation, automatic masking, or NOT_CAPTURED reason}} |

附上可讀的關鍵 log 原文；長篇內容以完整附件提供。標示證據可見性與保留方式，以及任何未擷取或被工具自動遮罩的值。流程摘要與原始 log 必須明確區別。

## 資源門檻事件（觸發時加入）

| # | 類型 | 門檻 | 當下狀態 | 使用者決定 |
|---|---|---|---|---|
| 1 | Build | 5 分鐘 | {{command/progress}} | {{extend/narrow/stop}} |

## 清理結果

| 清理 ID | 項目 | 結果 | 驗證 |
|---|---|---|---|
| C001 | {{temp/mock/package/device/backend state}} | {{removed/restored/not created}} | {{baseline proof}} |

## 保留證據（可選）

| 案例 ID | 證據 | 用途 |
|---|---|---|
| T001 | {{small redacted attachment/path}} | {{what it proves}} |

## 總結

- PASS：{{n}}
- FAIL：{{n}}
- BLOCKED：{{n}}
- NOT_RUN：{{n}}
- 執行覆蓋：{{executed}} / {{total}} ({{percent}})
- 通過率：{{PASS / (PASS + FAIL), or N/A}}
- 結論：{{one sentence}}
```

## Template Rules

- Resolve resources relative to the Skill root and invoke the resolved validator path with Python 3. Keep this directory's references and scripts available together.
- Preserve exact headings, column names, IDs, and status tokens; localize only narrative content.
- Record applicable host capabilities and concrete limitations. If validation cannot run, label the artifact `VALIDATION_NOT_RUN`, explain why, and supply the command for a capable host. Do not claim validated handoff or execute from an unvalidated plan.
- Weekly telemetry is host-dependent. Other quota windows and task token budgets require separate labels and agreed gates; `/status` and `/usage` are examples only. Unavailable weekly telemetry does not by itself block work under other gates.
- Launch builds only when progress monitoring and safe deadline enforcement are available; otherwise resolve the execution arrangement first.

- Run two or three completeness rounds. Never add a fourth round without explicit user approval.
- Freeze a plan only when the last round is `READY_TO_FREEZE`, adds zero requirements and cases, and has zero unresolved gaps.
- Use exact weekly telemetry for 5-percentage-point gates; record `Unavailable` rather than estimating when telemetry cannot be read.
- Keep premise and confirmation tables numbered.
- Preserve the exact frozen test-ID set from plan through report. Validate the report with `--plan`.
- Count underlying cases, not grouped rows. Use `✅ PASS`, `❌ FAIL`, `⚠️ BLOCKED`, and `NOT_RUN` consistently.
- Treat intermittent behavior as FAIL and describe it as flaky.
- Do not mark runtime behavior PASS with static evidence.
- Resolve product ambiguity before execution; do not hide it as BLOCKED.
- Keep evidence task-scoped and valid after cleanup. Honor the user's authorized visibility and retention requirements; requested reports and logs are deliverables, not disposable temporary files. State any masking or capture limits explicitly.
- Include actual parameters, the full ordered procedure, and applicable request/response and log evidence. Mark unavailable evidence NOT_CAPTURED rather than inventing values; N/A requires an applicability reason.
- Distinguish HTTP transport, business response, UI, and persistence. A business rejection is FAIL even with HTTP 200. Restore repository, device, account, network, and backend state to the approved baseline and identify any remaining cleanup barrier.
