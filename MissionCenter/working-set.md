<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=cb9543ca8390025eb704a678d317a604851e8cc0dcffda9de5fc86a0cd36dcee -->
# Active Working Set

- Source of truth: `tasks.md`
- Unfinished working set count: 6

| ID | Title | Priority | Status | Next action | Depends on | Verification | Blocker reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GV-M1 | Great Voyage M1：港口資料、世界地圖 UI 與整合 QA | P0 | In Progress | 完成四港往返、交易與箭頭端點驗收，修正剩餘問題 | E8, GV-M1-P3 | 四港／甲板／交易／HUD、60 秒自動抵港及 Maker 視覺證據齊全；再由主人確認主觀視覺 |  |
| GV-M1-P1 | Phase 1：Data & Geometry | P0 | Review | 重驗四港資料、直線幾何與空域分段；核對世界圖座標 | E8 | 四港與甲板 MapleTile mode／Body／入口、路線正反向與邊界測試有證據 |  |
| GV-M1-P3 | Phase 3：Ports Integration & QA | P0 | In Progress | 補四港完整往返、無舊事件與交易回歸；處理驗收缺陷 | GV-M1-P1, GV-M1-P2 | 四港皆可抵達／開商店／再次出航，60 秒倒數與船體保留有 Maker 證據 |  |
| GV-CABIN | 船艙管理介面與後續實體船艙 | P0 | In Progress | 先驗收管理、五船買換與三槽，再接新船體及短自動空戰 |  | 船況與貨物來源一致、維修安全、現有四港流程可回歸 |  |
| GV-CABIN-UI | 小舢板管理介面與伺服器船況 | P0 | Review | 依v15凍結資料進行獨立比對；正式評論待四項數值預算 |  | 兩檔 82 methods Lua 編譯、情境 8/8、全 58 項 UI 引用有效；新 UI 無新增 lint 警告；Maker runtime 待驗 |  |
| GV-CABIN-QA | 管理介面與四港回歸驗收 | P0 | In Progress | 依v15凍結資料進行獨立比對；正式評論待四項數值預算 | GV-CABIN-UI | Maker refresh/build/Play、四港航行交易、PC 與手機畫面 |  |

## Next Candidates

- E2 — 貿易貨物與價格結算
- P0-T4 — 建立交易貨物與素材規則
- Candidates only; promote to Ready in `tasks.md` before starting.
