# Great Voyage M1 Phase 3 — Ports Integration & QA

## 目標與邊界

把 Phase 1 的資料／幾何與 Phase 2 的世界地圖 UI 串成四港 ↔ 甲板整合驗收，保護交易、HUD、船體與甲板戰成果。2026-09-25 主人修訂航程規則：遭遇不暫停 60 秒倒數；未擊敗怪物但撐到終點也能抵港。

## 本 Phase 需要參照的技能

- `msw-general`：`references/platform.md`、`references/workspace.md`、`references/troubleshooting.md`、`references/verify-checklist.md`。
- `msw-ui-system`：`references/runtime-patterns.md`（HUD／狀態回饋檢查）。
- `msw-combat-system`：`references/hp-gauge.md`、`references/projectile.md`（只有既有甲板戰回歸需要時才讀，不擴張戰鬥）。
- Mission Center：煙霧測試格式與 `tasks.md` 單一真實來源。

## 任務清單

- 🟡 四港往返整合 smoke：四港各完成登船、世界地圖、甲板、抵港、商店與再次出航；航行狀態以 UserId 分離，啟航由 Server 重新驗證 origin／靠船條件。
- 🟡 交易與 HUD 回歸：四港各有三種地方商品，顯示金幣、貨艙與錯誤提示；需以 Maker 證明買入後跨港賣出獲利。
- 🟡 甲板戰回歸：甲板可站立；菇菇襲擊時倒數持續，擊敗怪物可清除事件，未擊敗也能於 60 秒後抵港且怪物被清理；Attack→Hit／船體受擊仍須單獨驗證。
- 🟡 Build/runtime 與錯誤分類：refresh → build logs → Play → runtime logs → stop；七區各有辨識事件卡，跨空域不強制抽牌。2026-09-25 Maker 已驗證森林→天空的倒數持續與存活抵港；其餘路線及貨物／船損保存仍待驗證。
- 🟡 使用者 PC 視覺驗收：主人確認四港及甲板辨識、船體輪廓／前後景遮擋、foothold 可站立、世界地圖可讀性與 NPC 互動提示；不能由代理代簽。
- ⬜ 手機基本點按檢查（非 M1 關閉前置）：MSW 自動適配仍不保證點按熱區與字級；PC 優先，本項保留為後續實機檢查，不得宣稱已通過。
- ⬜ 缺陷收斂與 closeout：將失敗／pending 項目連回唯一任務，更新 smoke-tests、As-built、Roadmap 與 M1 GDD；完成準則是沒有未追蹤的範圍外修補。

## 依賴與狀態規則

- 依賴：Phase 1、Phase 2；所有自動 smoke 通過後才能進行使用者驗收。
- `⬜` 未開始；`🟡` 已實作但等待 logs 或使用者測試；`✅` 僅在實作與對應證據都存在時使用。
- 玩家 PC 視覺與手機點按即使代理認為合理，也必須等待主人實測；手機結果不阻擋 PC 優先 M1 的技術驗收。

## 新港地圖（M1 第二波）

> 2026-09-01；本節只記錄 `map_ludus_port`／`map_nihal_port` 的地圖結構交接。地圖由 MapBuilder 的 MapleTile 模板建立，未修改既有森林港、天空港、航行甲板，也未在本次變更觸碰腳本、UI、model 或 `Global/SectorConfig.config`。

| 地圖 | 結構狀態 | EntryKey | TileMapMode / CoreVersion | Entity / root foothold / CustomFoothold / Portal | 後續狀態 |
| --- | --- | --- | --- | --- | --- |
| 玩具城港 `map_ludus_port.map` | ✅ builder validation PASS | `map://map_ludus_port` | `0` / `26.7.0.0` | `14 / 34 / 2 / 2` | 🟡 Maker refresh／註冊、視覺與實機待驗 |
| 納希沙漠港 `map_nihal_port.map` | ✅ builder validation PASS | `map://map_nihal_port` | `0` / `26.7.0.0` | `14 / 34 / 2 / 2` | 🟡 Maker refresh／註冊、視覺與實機待驗 |

兩圖均具備 `SpawnLocation`、`Portal` + `GV_ArrivalPortal`、`GV_PlayerShip`、`GV_PlayerShipFront`、`GV_DockFoothold`、港口商人、`GV_ShopInteractPoint`、`GV_WorldMapEntrance` 與 `GV_ShipBoardInteractPoint`。兩張圖的 entity UUID/path/componentNames 通過 builder 的唯一性與一致性檢查；Maker build logs 已讀取，未新增 map 結構錯誤。由於本代理禁止修改 SectorConfig，實際世界入口註冊仍需後續在 Maker／世界設定流程完成後再驗證。

## 驗證證據格式

每次記錄：測試名稱、操作／指令、預期、實際觀察、Pass／Fail／User-test pending、日期、MissionCenter task ID、run type。失敗不得刪除舊證據，只追加修正後結果。

## 第三波整合交接（2026-09-01）

- `sky` 是天空之城港唯一 canonical portId；`victoria` 僅保留為舊資料 alias，空域 `victoria` 維持原識別。
- `map_ludus_port`／`map_nihal_port` 已納入 Server 抵達分派；抵達後回到港口，可再次靠船出航與使用資料驅動商店。
- 甲板流程（2026-09-25 規則更新）：Server `StartVoyage` 驗證後傳送至 `map_airship_deck`；`AdvanceVoyage` 依 Server 實際時間推進 60 秒，事件期間照常前進；甲板舵輪可處理非戰鬥事件，擊退菇菇會清除襲擊，未擊退則抵港時結算並清理怪物。航線、貨物與船損仍按 UserId 保存。
- 七區（`forest_wind`、`victoria`、`aqua`、`ludus`、`nihal`、`orbis_highwind`、`ellinia_cloud`）各有至少一張不需新怪物資產的辨識事件卡；`open_sea` 可無事件，擦過 `ludus` 時允許預期事件量為 0。
- 兩張新圖與三張 UI 均為只讀檢查範圍；若需結構修正，交回 MapBuilder／UIBuilder 代理，不直接改檔。

## 第三波靜態驗證證據（2026-09-01）

- JSON 結構檢查：`map_ludus_port.map`、`map_nihal_port.map`、`GreatVoyageAdventure.ui`、`GreatVoyageHUD.ui`、`GreatVoyageRouteDesk.ui` 均可解析；兩張新圖 `EntryKey`／`TileMapMode` 分別為 `map://map_ludus_port`／`map://map_nihal_port`、`0`。
- 腳本檢查：`git diff --check` 無 whitespace error；Server 請求方法沒有 `any` 跨空間參數，且航程／貨物／受擊／事件 RPC 以引擎注入的 `senderUserId` 鎖定請求者；航程快照由 Server 以目標玩家 RPC 推送，ClientOnly 只讀本地投影；`victoria` 未作港口資料鍵，只出現在 alias／空域／事件卡。
- Maker（2026-09-01 當時快照）：當時環境未提供可呼叫的 Maker MCP，故當時未宣稱 build/runtime 通過。2026-09-25 已補森林→天空之城 refresh／build／Play／runtime／stop 及遭遇倒數實測（`ST-GV-M1-VOYAGE-002`）；四港完整回歸與 PC 主觀視覺仍待驗，手機點按是非阻塞後續項。
