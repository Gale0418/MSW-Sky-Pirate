<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=0d9f7c8e91b6d02dc2c6396048c0668fa35d0178ff19f030d828dc28788a9fa9 -->
# Active Working Set

- Source of truth: `tasks.md`
- Unfinished working set count: 5

| ID | Title | Priority | Status | Next action | Depends on | Verification | Blocker reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GV-M1-L10 | 校正繁中原文與多語言顯示 | P1 | In Progress | SourceLanguage 已由主人在 Maker 改為 zh-tw；下一步盤點文字元件與動態文案、建立關鍵譯文並於發佈版實測世界語言切換 | GV-M1-P2 | 航圖、商店、60 秒倒數、遭遇在繁中及至少一種其他語言下的截圖與 runtime logs；文字不溢出 |  |
| GV-M1 | Great Voyage M1：港口資料、世界地圖 UI 與整合 QA | P0 | Blocked | 技術實作、幾何／UIBuilder／MapBuilder 與 Maker build/runtime 快照已完成；等待 PC 視覺與手機實機驗收 | E8, GV-M1-P3 | `Docs/GreatVoyage-M1-GDD.md` 三個 Phase 技術證據齊全，且主人完成視覺／手機測試後才可 Done |  |
| GV-M1-P1 | Phase 1：Data & Geometry | P0 | Review | 技術實作、三圖幾何與 MapBuilder／Maker 快照驗證已完成，交付 review | E8 | 三張地圖 mode／Body／入口／船體幾何結構檢查與 snapshot 證據已存在 |  |
| GV-M1-P3 | Phase 3：Ports Integration & QA | P0 | Blocked | 程式、整合、build/runtime 快照已完成；等待主人 PC 視覺與手機實機測試 | GV-M1-P1, GV-M1-P2 | 雙港／甲板／交易／HUD 回歸證據已記錄；PC 視覺與手機實機通過後才可 closeout |  |
| GV-M1-P2 | Phase 2：World Map UI | P1 | Review | UIBuilder／controller 綁定與靜態驗證已完成，交付 review；Maker build/runtime 快照已補齊 | GV-M1-P1 | UIBuilder／lint、合法目的地狀態與 Maker 快照證據一致；不重做交易 UI |  |

## Next Candidates

- E2 — 貿易貨物與價格結算
- P0-T4 — 建立交易貨物與素材規則
- Candidates only; promote to Ready in `tasks.md` before starting.
