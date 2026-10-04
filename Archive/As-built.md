# Great Voyage As-built（截至 2026-10-03）

> 本文件是 M1 的 brownfield 起點，不取代 `MissionCenter/` 的任務真實來源。目前狀態依現有工作樹與2026-10-03 Maker證據；下方2026-09-01歷史基線僅記錄當時三圖盤點。


## 目前實作狀態（2026-10-03，M1 未完成）

- 四港森林／天空／玩具城／納希與飛行甲板已接，地圖維持 MapleTile。四港循環、各港商品商人與跨港買賣有當日 Maker 證據。
- 一艘T0／四艘T1船、獨立船況、三通用槽、五款船體及原生引擎動畫已接；共用甲板邊界／前舷遮擋有Maker實測，所有船全部港口對位仍待收斂。
- 舊隨機事件、舵輪結算與菇菇襲擊已退休；新飛行怪空戰採Server發射序列與0.6秒命中，勝利續航、沉船清貨返回出發港。
- 改裝圖鑑29張，其中20張有效，9張缺前置玩法而禁止販售/安裝；卡面及空槽30PNG已取得RUID。G/卡/船/貨物均是遊玩期間狀態，永久經濟存檔另在Roadmap。
- 商品店新增卡片市場；買賣未安裝庫存、安裝消耗、替換/拆卸返還；庫存與已裝總上限99，三槽允許持有足夠副本後重複卡。卡數與G由Server驗證。
- T0四港免費維修；T1付費，修理卡影響真成本。配裝不補血、超載拆卡/換船拒絕；再生和鍋爐以航程百分比結算。
- 本輪程式不變量及12條有怪/無怪路線模擬通過；Maker已有真卡片買入、替換、三槽與載貨證據，最後排版、航行三槽唯讀及貨物保留到天空港已通過；build60Info/normal69Info無Error或Warning。完整評論仍待預算，四項卡片子任務進Review。實際多人及手機尚未驗。
- M1仍有世界圖全部箭頭、五船港口對位、多語言、玩家PC視覺與獨立完整評論待驗；不能由本輪卡片功能推定整個里程碑完成。

## 歷史基線（2026-09-01，以下不作目前場景清單）

## 已存在的可玩基線

- 世界定位：楓之谷風格的空中航海冒險。
- 已完成的主循環：港口探索 → 靠近自製船啟航 → 世界地圖選目的地 → 進入航行甲板 → 抵達另一港 → NPC 對話與藥水交易。
- 已完成且保留回歸保護：E8 三場景探索、跨圖航行、甲板中繼、雙港 NPC 商店；MissionCenter 既有記錄標示 E8／GV-T1～GV-T4 Done。
- 既有 HUD、交易、航線與甲板戰邏輯屬於前一個垂直切片成果；M1 文件只規劃資料／幾何、世界地圖 UI、港口整合與 QA 的下一段工作。

## 三張地圖盤點

三張檔案的 `EntryKey`、`CoreVersion` 與根 `MapComponent.TileMapMode` 均已確認如下：

| 地圖 | EntryKey | TileMapMode | 結構與現況 |
| --- | --- | ---: | --- |
| `map/map_forest_port.map` | `map://map_forest_port` | `0`（MapleTile） | 66 個實體；森林背景／多層 TileMap／Foothold；森林商人「艾琳」；`GV_PlayerShip`、`GV_PlayerShipFront` 與船體自訂 foothold；Portal。 |
| `map/map_orbis_port.map` | `map://map_orbis_port` | `0`（MapleTile） | 53 個實體；天空城背景／多層 TileMap／Foothold；天空商人「露米」；可攀爬物件；`GV_PlayerShip`、`GV_PlayerShipFront` 與船體自訂 foothold；Portal。 |
| `map/map_airship_deck.map` | `map://map_airship_deck` | `0`（MapleTile） | 39 個實體；多層 TileMap／Foothold；四個 Portal；`GV_PlayerShip`、`GV_PlayerShipFront` 與甲板自訂 foothold；SpawnLocation。 |

M1 延續 MapleTile（側視、重力、`RigidbodyComponent`／Foothold）基線；不在文件任務中切換 `TileMapMode`，也不假設可以用矩形地圖規則替代現有 foothold。

## 系統現況

### 交易

- 已有雙港正式藥水交易：紅／藍／橘藥水、金幣、貨艙容量、買賣與錯誤提示。
- 既有證據記錄藍藥水天空城 80G → 森林 100G 的交易路徑。
- 價格與貨物規則仍有後續擴充空間；E2、P0-T4、AC-T7 在既有 MissionCenter 中仍是 backlog，不在本 M1 隱含承諾為完成。

### HUD／世界地圖 UI

- `GreatVoyageHUD` 已在既有垂直切片中重驗，包含港口／航線／交易相關互動。
- 世界地圖與目的地選擇是既有流程的一部分；M1 的 UI 工作重點是把港口資料與地圖按鈕狀態更明確地資料驅動化，不重做既有交易 UI。
- UI 仍須遵守 `.ui` builder、client-only 與既有 UUID 綁定規則；本次只寫計畫，不直接修改 `.ui`。

### 甲板戰

- 甲板有船體分層、可站立 foothold、怪物空降與玩家 Attack→Hit 護船的既有垂直切片成果。
- 既有任務記錄為 3 隻橘菇菇、船體／護盾受擊與結算；正式空戰／離船空戰仍是 backlog（B-T1）。
- M1 只要求港口→甲板→港口的整合回歸，不擴張成新的怪物、技能或空戰系統。

## 已知限制與風險

- 本次未執行 Maker refresh、build、Play 或 screenshot；文件中的已完成描述沿用既有 MissionCenter 證據，不能視為本輪新驗證。
- 視覺驗收（船體輪廓、遮擋層、NPC／港口辨識、世界地圖可讀性）保留給使用者在 Maker 中實機確認。
- 手機實機驗收（觸控命中區、橫向畫面、字級與安全區、交易／世界地圖可操作性）保留給使用者測試；不得由自動化或 PC 截圖代替。
- 三張地圖目前均為 MapleTile；任何改圖型都會牽動 Body、重力、foothold 與移動驗證，M1 明確排除。
- 舊 MissionCenter 有歷史 Done 驗證債務（`legacy-done-audit.json`）；M1 新任務不得沿用無證據的 Done，必須留下對應 smoke／使用者驗收記錄。

## M1 邊界

M1 只承接三個互不重疊的工作面：

1. Data & Geometry：港口／航線／幾何契約與三張現有地圖的資料對齊。
2. World Map UI：目的地選擇、港口狀態與回饋的 UI 資料綁定。
3. Ports Integration & QA：雙港整合、甲板回歸、build/runtime、視覺與手機實機驗收。

任何新港口、更多貨物、角色成長、技能書商店、高難離船空戰，均移至 Roadmap Backlog，不能在 M1 Phase 清單中偷偷膨脹。
