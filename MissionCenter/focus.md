<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- Deprecated compatibility view: focus.md is generated from tasks.md only and must never be edited or treated as a second lifecycle source. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=0d9f7c8e91b6d02dc2c6396048c0668fa35d0178ff19f030d828dc28788a9fa9 -->
# P0 Focus

- Source of truth: `tasks.md`
- Unfinished P0: 3

| ID | Title | Status | Next action | Depends on | Verification |
| --- | --- | --- | --- | --- | --- |
| GV-M1 | Great Voyage M1：港口資料、世界地圖 UI 與整合 QA | Blocked | 技術實作、幾何／UIBuilder／MapBuilder 與 Maker build/runtime 快照已完成；等待 PC 視覺與手機實機驗收 | E8, GV-M1-P3 | `Docs/GreatVoyage-M1-GDD.md` 三個 Phase 技術證據齊全，且主人完成視覺／手機測試後才可 Done |
| GV-M1-P1 | Phase 1：Data & Geometry | Review | 技術實作、三圖幾何與 MapBuilder／Maker 快照驗證已完成，交付 review | E8 | 三張地圖 mode／Body／入口／船體幾何結構檢查與 snapshot 證據已存在 |
| GV-M1-P3 | Phase 3：Ports Integration & QA | Blocked | 程式、整合、build/runtime 快照已完成；等待主人 PC 視覺與手機實機測試 | GV-M1-P1, GV-M1-P2 | 雙港／甲板／交易／HUD 回歸證據已記錄；PC 視覺與手機實機通過後才可 closeout |
