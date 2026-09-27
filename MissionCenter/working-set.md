<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=e874e805f2e64bf83f188b773979c10fc431e2af1d66419ee08eb4666aee41ab -->
# Active Working Set

- Source of truth: `tasks.md`
- Unfinished working set count: 5

| ID | Title | Priority | Status | Next action | Depends on | Verification | Blocker reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GV-M1 | Great Voyage M1：港口資料、世界地圖 UI 與整合 QA | P0 | In Progress | 完成四港往返、戰鬥結算、交易與箭頭端點驗收，修正剩餘問題 | E8, GV-M1-P3 | 四港／甲板／交易／HUD、60 秒遭遇持續倒數及 Maker 視覺證據齊全；再由主人確認主觀視覺 |  |
| GV-M1-P1 | Phase 1：Data & Geometry | P0 | Review | 重驗四港資料、直線幾何與空域分段；核對世界圖座標 | E8 | 四港與甲板 MapleTile mode／Body／入口、路線正反向與邊界測試有證據 |  |
| GV-M1-P3 | Phase 3：Ports Integration & QA | P0 | In Progress | 補四港完整往返、怪物擊殺與交易回歸；處理驗收缺陷 | GV-M1-P1, GV-M1-P2 | 四港皆可抵達／開商店／再次出航，遭遇倒數與船體保留有 Maker 證據 |  |
| GV-M1-L10 | 校正繁中原文與多語言顯示 | P1 | In Progress | SourceLanguage 已由主人在 Maker 改為 zh-tw；下一步盤點文字元件與動態文案、建立關鍵譯文並於發佈版實測世界語言切換 | GV-M1-P2 | 航圖、商店、60 秒倒數、遭遇在繁中及至少一種其他語言下的截圖與 runtime logs；文字不溢出 |  |
| GV-M1-P2 | Phase 2：World Map UI | P1 | Review | 重驗四港節點、箭頭起終點、視覺層級與提示文字 | GV-M1-P1 | UIBuilder／lint、四港合法目的地及 Maker 截圖證據一致 |  |

## Next Candidates

- E2 — 貿易貨物與價格結算
- P0-T4 — 建立交易貨物與素材規則
- Candidates only; promote to Ready in `tasks.md` before starting.
