<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=625acd244555ec70edf0ab28aeba49a62874013f8a08dad129877bf3397b70e1 -->
# Mission Brief

- Last organized: 2026-10-12
- Source fingerprint: `625acd244555ec70edf0ab28aeba49a62874013f8a08dad129877bf3397b70e1`
- Source of truth: `tasks.md`
- Project: MSW Great Voyage
- North Star: 楓之谷風格的空中航海冒險；以既有三場景原型為基線，完成 Great Voyage M1 四港、直航多空域航圖、地方商品貿易、甲板遭遇與整合 QA。
- Cycle: Great Voyage M1

## Today's Summary · 2026-10-12
- Timestamp：2026-10-12T01:15:15+08:00｜GV-ENCOUNTER-RUNTIME-20261012
- Change：接入129種固定戰力怪與混編隊伍、擊殺賞金及滿錢包保留，建立T0～T5戰力／維修曲線；同步README及遭遇規格。
- Reason：主人要求弱怪少賞金、強怪多賞金，且只由貨物價值吸引怪物，現金不掉落不應引怪。
- Impact：每100距離持續檢查、尾段折算、Server防重結算；107 tests／10 subtests、22,464條件／98,000抽樣通過。Maker Server邏輯與Client跨端快照切片通過，build87／最終runtime58全Info，0 Warning／Error，Timer清除且已stop。高階材料造船／NPC、BOSS、全航程畫面及正式服仍待後續；不改任務生命週期。
- Evidence：[串接與限制](../docs/GreatVoyage-Encounter-Runtime-20261012.md)、[Maker收據](../docs/reviews/encounter-runtime-maker-20261012.json)。
- 最終補記：107 tests／10 subtests、22,464條件／98,000抽樣通過。CodeRabbit 8檔1 minor已查證修正並補正負向回歸；Maker Server混編／固定賞金與Client跨端Timer快照通過，build87／最終runtime58全Info、0 Warning／Error。前輪夾具與時序診斷保留，Timer清除、已stop回edit。全航程與多怪sprites／正式服未驗；收據見 ../docs/reviews/encounter-runtime-maker-20261012.json。
- Timestamp：2026-10-12T02:47:49+08:00｜GV-COMBAT-FEEDBACK-20261012
- Change：加入原 UID 獨立飛行與固定直線砲擊、溫和命中、±10% 傷害／5%×1.5 爆擊、原生傷害字與頭頂 MISS，129 種怪物各用同官方 pack hit1，活怪約0.3秒後還原、死怪延後回收；DIY砲台保留後續規劃。
- [TRUNCATED] 9 additional items require canonical file access.

## Relevant Guardrails (0)
- None

## Read Next Only When Needed
- Current work (6 items) → `working-set.md`
- Modify task lifecycle/order → `tasks.md`
- Need rationale/evidence → `decisions.md`, `notes.md`, `smoke-tests.md`
- Brief/working set stale or truncated → run `mission_maintenance.py sync` and open canonical files
