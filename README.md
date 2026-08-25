# Plan Feature Tests

[English](README.md) | [繁體中文](README.zh-TW.md)

`plan-feature-tests` is an Agent Skill for creating, reviewing, executing, and resuming resource-bounded feature QA plans. It keeps requirements and test cases traceable, freezes source fingerprints before execution, enforces explicit resource gates, and reports every frozen test ID as `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

The skill follows the open Agent Skills directory format and can be used with Codex, Cursor, Claude Code, and Gemini CLI.

## Contents

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

## Install in Codex

Ask Codex to install the skill from GitHub:

```text
$skill-installer Install plan-feature-tests from https://github.com/cbt36594/plan-feature-tests-skill/tree/main/skills/plan-feature-tests
```

Use it explicitly with:

```text
$plan-feature-tests
```

## Install in Cursor

Cursor discovers personal skills under `~/.cursor/skills/` and `~/.agents/skills/`.

```bash
git clone https://github.com/cbt36594/plan-feature-tests-skill.git
mkdir -p ~/.cursor/skills
cp -R plan-feature-tests-skill/skills/plan-feature-tests ~/.cursor/skills/
```

Invoke it with `/plan-feature-tests`, or let Cursor select it when the request matches its description.

## Install in Claude Code

Claude Code discovers personal skills under `~/.claude/skills/`.

```bash
git clone https://github.com/cbt36594/plan-feature-tests-skill.git
mkdir -p ~/.claude/skills
cp -R plan-feature-tests-skill/skills/plan-feature-tests ~/.claude/skills/
```

Invoke it with `/plan-feature-tests`, or let Claude Code select it when the request matches its description.

## Install in Gemini CLI

Install the skill from its repository path. User scope is the default:

```bash
gemini skills install https://github.com/cbt36594/plan-feature-tests-skill.git --path skills/plan-feature-tests
```

To install it only for the current workspace:

```bash
gemini skills install https://github.com/cbt36594/plan-feature-tests-skill.git --path skills/plan-feature-tests --scope workspace
```

In an active Gemini CLI session, reload and verify discovery:

```text
/skills reload
/skills list
```

Ask Gemini to use the `plan-feature-tests` skill, or make a request that matches its description. Gemini CLI asks for activation consent before loading a skill's resources.

## Validate a generated plan

The bundled validator checks saved Markdown plans and execution reports:

```bash
python3 skills/plan-feature-tests/scripts/validate_test_plan.py PLAN.md --kind plan --require-not-run
python3 skills/plan-feature-tests/scripts/validate_test_plan.py REPORT.md --kind report --plan PLAN.md
```

## License

MIT
