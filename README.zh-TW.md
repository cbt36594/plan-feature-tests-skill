# Plan Feature Tests

[English](README.md) | [繁體中文](README.zh-TW.md)

`plan-feature-tests` 是用來建立、審查、執行及接續功能 QA 計畫的 Agent Skill。它會維持需求與測試案例的雙向追溯，在執行前凍結來源指紋與測試案例集合，設定明確的資源門檻，並將每個凍結案例記錄為 `PASS`、`FAIL`、`BLOCKED` 或 `NOT_RUN`。

這份 Skill 遵循開放的 Agent Skills 目錄格式，可供 Codex、Cursor、Claude Code 與 Gemini CLI 使用。

## 宿主能力

核心流程不依賴特定模型；完整執行需要宿主提供相關檔案、Python 3、程序控制與裝置／瀏覽器工具。請移轉完整 Skill 資料夾；`agents/openai.yaml` 為選用的 Codex 設定。使用 Grok 的 Agent 必須由宿主載入指令並提供工具，僅貼上提示詞不會取得本機專案存取能力。無法讀取週額度時記錄 `Unavailable`，其他預算分開追蹤。無法執行驗證器時，成果須標記 `VALIDATION_NOT_RUN`，不得宣稱已通過驗證或據此執行測試。

## 內容結構

```text
skills/plan-feature-tests/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── spec-completeness-checklist.md
│   └── test-plan-template.md
└── scripts/
    └── validate_test_plan.py
```

## 安裝至 Codex

請 Codex 從 GitHub 安裝 Skill：

```text
$skill-installer Install plan-feature-tests from https://github.com/cbt36594/plan-feature-tests-skill/tree/main/skills/plan-feature-tests
```

明確呼叫 Skill：

```text
$plan-feature-tests
```

## 安裝至 Cursor

Cursor 會從 `~/.cursor/skills/` 與 `~/.agents/skills/` 尋找個人 Skill。

```bash
git clone https://github.com/cbt36594/plan-feature-tests-skill.git
mkdir -p ~/.cursor/skills
cp -R plan-feature-tests-skill/skills/plan-feature-tests ~/.cursor/skills/
```

可使用 `/plan-feature-tests` 呼叫，或讓 Cursor 在需求符合 Skill description 時自動選用。

## 安裝至 Claude Code

Claude Code 會從 `~/.claude/skills/` 尋找個人 Skill。

```bash
git clone https://github.com/cbt36594/plan-feature-tests-skill.git
mkdir -p ~/.claude/skills
cp -R plan-feature-tests-skill/skills/plan-feature-tests ~/.claude/skills/
```

可使用 `/plan-feature-tests` 呼叫，或讓 Claude Code 在需求符合 Skill description 時自動選用。

## 安裝至 Gemini CLI

使用 repository 內的 Skill 路徑安裝；預設為使用者層級：

```bash
gemini skills install https://github.com/cbt36594/plan-feature-tests-skill.git --path skills/plan-feature-tests
```

若只要安裝至目前 workspace：

```bash
gemini skills install https://github.com/cbt36594/plan-feature-tests-skill.git --path skills/plan-feature-tests --scope workspace
```

若 Gemini CLI 已經在執行，請重新載入並確認 Skill 已被發現：

```text
/skills reload
/skills list
```

可以直接要求 Gemini 使用 `plan-feature-tests` Skill，或提出符合 Skill description 的需求。Gemini CLI 在載入 Skill 資源前會要求 activation consent。

## 驗證產生的計畫

Skill 內附的 validator 可檢查已儲存的 Markdown 測試計畫與執行報告：

```bash
python3 skills/plan-feature-tests/scripts/validate_test_plan.py PLAN.md --kind plan --require-not-run
python3 skills/plan-feature-tests/scripts/validate_test_plan.py REPORT.md --kind report --plan PLAN.md
```

## 授權

MIT
