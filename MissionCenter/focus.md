<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- Deprecated compatibility view: focus.md is generated from tasks.md only and must never be edited or treated as a second lifecycle source. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=e874e805f2e64bf83f188b773979c10fc431e2af1d66419ee08eb4666aee41ab -->
# P0 Focus

- Source of truth: `tasks.md`
- Unfinished P0: 3

| ID | Title | Status | Next action | Depends on | Verification |
| --- | --- | --- | --- | --- | --- |
| GV-M1 | Great Voyage M1：港口資料、世界地圖 UI 與整合 QA | In Progress | 完成四港往返、戰鬥結算、交易與箭頭端點驗收，修正剩餘問題 | E8, GV-M1-P3 | 四港／甲板／交易／HUD、60 秒遭遇持續倒數及 Maker 視覺證據齊全；再由主人確認主觀視覺 |
| GV-M1-P1 | Phase 1：Data & Geometry | Review | 重驗四港資料、直線幾何與空域分段；核對世界圖座標 | E8 | 四港與甲板 MapleTile mode／Body／入口、路線正反向與邊界測試有證據 |
| GV-M1-P3 | Phase 3：Ports Integration & QA | In Progress | 補四港完整往返、怪物擊殺與交易回歸；處理驗收缺陷 | GV-M1-P1, GV-M1-P2 | 四港皆可抵達／開商店／再次出航，遭遇倒數與船體保留有 Maker 證據 |
