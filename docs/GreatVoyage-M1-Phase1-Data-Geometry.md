# Great Voyage M1 Phase 1 — Data & Geometry

## 目標與邊界

把魔法森林、天空之城、玩具城、納希沙漠四港與航行甲板散落於地圖／邏輯的識別資訊整理成一致契約，並確認船體、登船點、甲板 foothold 與 Portal 幾何能支撐四港間往返。本 Phase 不新增 UI、不修改交易規則或戰鬥內容；新增港口地圖由 Phase 3 整合。

## 本 Phase 需要參照的技能

- `msw-general`：`references/platform.md`、`references/entity.md`、`references/authoring.md`、`references/builder-protocol.md`、`references/builder-protocol-map.md`。
- `msw-scripting`：`references/verify-checklist.md`（若實作代理需要調整資料存取）。
- `msw-planning`：`references/msw-mapping.md`（維持系統對照）。

## 任務清單

- 🟡 建立港口與航線契約：唯一 port／route id、顯示名、起點／目的地、啟航條件與回程關係；完成準則是四港間合法直航與反向航線資料可互相追溯，且未把交易價格混入幾何資料。森林↔天空是已驗證樣本，不是完整四港證據。
- ⬜ 對齊五張地圖的結構索引：記錄四港與甲板的根地圖、TileMapMode、入口 Portal、SpawnLocation、船體前／後景與 NPC／foothold entity；完成準則是每張地圖都有可重複的檢查輸出。
- ⬜ 定義船體幾何契約：船 Transform、前景遮擋順序、可站立 CustomFoothold 與登船互動點的相對關係；完成準則是實作代理能依同一欄位判斷「靠船」與「甲板可站立」。
- 🟡 定義跨圖航行狀態契約：來源港、目的港、目前航線、甲板中繼與抵達港的合法狀態轉移；完成準則是非法目的地／非靠船狀態都有明確拒絕原因。
- ⬜ 執行結構驗證與交接：refresh 後檢查五張地圖均為 MapleTile、動態實體使用正確 Body，並核對四港的地圖座標與可行走路線；完成準則是結構／build 證據與變更摘要存入對應 MissionCenter 任務。

## 依賴與禁止事項

- 依賴：`Archive/As-built.md`、既有 E8／GV-T1～GV-T4 成果；Phase 1 完成後 Phase 2 才能綁定 UI 狀態。
- 禁止：直接修改 `.map`／`.model`／`.mlua` 的代理若未載入對應技能與 builder；本文件作者不執行資產修改。
- 不得把使用者視覺或手機實機測試標成自動通過；這些驗收由 Phase 3 統一追蹤。

## 驗證

自動／Maker：MapBuilder 讀取三張地圖的 mode、入口與船體幾何，refresh → build logs；預期無 mode／Body 漂移。

使用者：不在本 Phase 自行宣稱視覺通過；主人於 Phase 3 以 Maker 截圖與手機實機確認。
