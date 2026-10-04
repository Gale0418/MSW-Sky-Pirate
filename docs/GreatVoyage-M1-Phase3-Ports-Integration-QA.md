# Great Voyage M1 Phase 3 — Ports Integration & QA

## 目標與邊界

把 Phase 1 的資料／幾何與 Phase 2 的世界地圖 UI 串成四港 ↔ 甲板整合驗收，保護交易、HUD 與船體。2026-10-02 主人要求停用全部舊航行事件，加入船艙管理與五船買換，船體完成後接短自動空戰。下方 9 月甲板戰紀錄只代表歷史行為。

## 本 Phase 需要參照的技能

- `msw-general`：`references/platform.md`、`references/workspace.md`、`references/troubleshooting.md`、`references/verify-checklist.md`。
- `msw-ui-system`：`references/runtime-patterns.md`（HUD／狀態回饋檢查）。
- `msw-combat-system`：`references/hp-gauge.md`、`references/projectile.md`（只有既有甲板戰回歸需要時才讀，不擴張戰鬥）。
- Mission Center：煙霧測試格式與 `tasks.md` 單一真實來源。

## 任務清單

- 🟡 四港往返整合 smoke：四港各完成登船、世界地圖、甲板、抵港、商店與再次出航；航行狀態以 UserId 分離，啟航由 Server 重新驗證 origin／靠船條件。
- 🟡 交易與 HUD 回歸：四港各有三種地方商品，顯示金幣、貨艙與錯誤提示；需以 Maker 證明買入後跨港賣出獲利。
- 🟡 船艙管理與停用舊事件：甲板可站立、依可調基礎航程抵港、HUD 顯示百分比，沒有舊隨機事件或菇菇生成；船況與貨物來自伺服器，T0 可免費修理。程式已有，Maker 待驗。
- 🟡 五船購買換船：四港商人兼營船舶買賣，每型一艘、獨立船況；RPC 驗證身分／位置／航行狀態。2026-10-02 Maker 真 Client RPC 已驗證四船各扣 500 G、重複不扣款、容量相等可換、超載拒絕與各船獨立損傷。2026-10-03 森林港按 E 開店→船商入口事件→Card2 選船→獨立 Close 事件通過；畫面不透底、價格及 buff 可讀、ShipModal.Enable=false。其餘四港回歸與主人視覺仍待驗。
- 🟡 T1 三槽改裝：每船獨立三槽，允許同卡重複；火力每卡 +5%、航速每卡 +5%、貨艙每卡 +1。從船型基礎重算，不累乘；只可在港商人附近改裝，卸除貨艙卡不可造成超載，換裝不補血。2026-10-03 擴為29張圖鑑／20張可用，購買庫存、拆卸返還、T1維修與額外能力已實作。9張前置卡逐項列入Roadmap且禁止販售；最終Maker買/賣、裝卸返還、T1維修報價12G、航行卡面唯讀與cargo1/9到天空港通過；CodeRabbit5minor及1測試可攜性issue已修，完整評論預算待核准。
- 🟡 改裝卡市場與卡面：2026-10-03 商品商人增加改裝卡購買／出售，T1三槽從庫存安裝；29卡與空槽已由image生成且取得正式RUID。Lua庫存守恆、跨玩家投影、百分比能力及12路線回歸通過；修正版Maker市場/空槽/三槽/載貨/航行畫面已驗；最新build60Info、normal69Info、0Error/0Warning。15組卡片、23項UI及12路線mock全通過，四子任務進Review，證據upgrade-cards-qa.md。
- 🟡 五款船體與原生動畫尾跡：五款船身與前舷素材已匯入並掛接五圖；2026-10-02 Maker 已逐船檢查同一甲板中點的下半身遮擋，引擎實測 13 次換幀事件、11 個不同幀。港口登船點、兩端行走與主人視覺驗收仍待完成。
- ✅ 五船共用甲板行走限制：2026-10-03 改成 CustomFoothold 來源折線的相連兩端牆。Maker 左移7秒停 x=-3.920、右移9秒停 x=-0.040，皆 grounded=true；兩端朝外跳與落地通過。Server 強制移到 y=-5 後有 recovered log，離船 block/ignore 還原 false/false。保存後來源6點、派生5段且同組前後相連；證據見 MissionCenter/evidence/2026-10-03/deck-and-shop-runtime.json。最後額外 refresh 重跑遇 MCP 工具清單失聯，未列通過。
- ✅ 短自動空戰技術驗證：每段空域的百分比中點觸發，Server管理每玩家戰鬥／0.6秒砲彈飛行與命中，Client只畫動畫。最終Maker build41Info／0Error／0Warning、runtime0Error／0Warning；蝙蝠砲擊時序、森林→天空抵港、低血量沉船清貨返回出發港、重結算拒絕與免費T0三層修理通過。改動前另完成四港全循環及跨港買賣；最終版Lua12路線回歸通過。證據：MissionCenter/evidence/2026-10-03/airbattle-projectile-runtime.json、airbattle-runtime-qa.md。GV-AIRBATTLE進入Review，其他船型砲口與主人PC視覺仍待審閱，不代表M1完成。
- 🟡 Build/runtime 與錯誤分類：refresh → build logs → Play → runtime logs → stop；本輪舊事件停用，不再要求辨識事件卡。2026-10-02 船商試玩 build 為 32 Info、無 Error/Warning；測試 probe 的 nil 欄位串接錯誤已識別，不作遊戲功能通過證據。介面修正後需重新驗證航程與乾淨 runtime。
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
