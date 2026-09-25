# Notes

## 2026-09-25 M1 現況覆蓋提醒

- 下方同日「SourceLanguage=ko／WorldConfig 未修改」是修改前的歷史快照，**現值為 `zh-tw`**；繁中原文啟動回歸通過，但其他語言未測。
- M1 現有魔法森林、天空之城、玩具城、納希沙漠四港與甲板，並非下方舊決策中的雙港／三圖。森林→天空之城航程已實測遭遇菇菇時 60 秒倒數繼續，不擊殺仍抵港；完整四港往返及擊殺結算仍待驗。
- 另一份 Gemini 視覺審查提到「雙長方形港口、黑底藍粉商店、缺關閉 X」，與 2026-09-25 Maker 截圖不符；現畫面已有四個圓形港口徽章及木框象牙底商店與 X，故不把這些過期描述列為待修 Bug。可保留其圖層、文字對比、點擊區建議供後續實測。

## 2026-09-25 MSW／GitHub 技能及本地化查核

- 官方技能庫：https://github.com/MSW-Git/msw-ai-coding-plugins-official 。本地已具 general、scripting、UI、search、sprite RUID、painter、packages、combat、avatar、DefaultPlayer、behaviourtree、planning；GitHub 額外 `maplestory-skill-maker` 偏特定玩家技能架構，暫不直接移植。
- 官方功能套件：https://github.com/MSW-Git/MSWPackages 。有 UI 資源包及通用 shop／inventory／dialog 等；現有商店是地方貨物／價差／貨艙系統，先讀套件 README 再決定是否引用視覺素材或整合。
- 自動翻譯官方說明：https://maplestoryworlds-creators.nexon.com/ko/docs/?postId=1072 。需要正確 `SourceLanguage`、支援文字元件的 `AllowAutomaticTranslation`、發佈語言設定及玩家選擇；不是所有 UI 字串無條件自動翻。2025-04-23 官方更新確認繁中可選作 SourceLanguage：https://maplestoryworlds-creators.nexon.com/en/community/5479/5488/2838585 。
- 本地事實：`Global/WorldConfig.config` 第 20 行為 `ko`；`RootDesk/MyDesk/UI/GreatVoyageAdventureController.mlua` 等動態寫入繁中 UI 文案；專案未找到 `.localedataset` 或 `.csv`。因此遊戲多語言尚未完成驗收。下一步在 Maker 校正原文語言，建立／套用譯文資料，逐頁實測航圖、商店、倒數、遭遇及文字溢出。
- GitHub `SkillTranslator`、`skill-i18n` 類工具主要翻 Agent SKILL 文件；Crowdin skills 有翻譯流程但非 MSW 即插即用。本輪未安裝任何第三方技能。
- 2026-09-25 電腦操作續查：`sky.list_apps()` 找到唯一 `MapleStory Worlds-楓谷空賊王` 視窗（msw.exe）；`get_window_state` 擷取連續兩次回報 `SetIsBorderRequired failed: 不支援此種介面 (0x80004002)`。依 computer-use 復原規則停止 UI 輸入；WorldConfig 未修改，需主人於 Maker 手動設為繁體中文，或電腦擷取介面修復後續辦。
- 2026-09-25 原文設定更新：主人回覆 OK 後，唯讀確認 `Global/WorldConfig.config:20` 已為 `zh-tw`。Maker 當前在 `map_forest_port` 編輯模式；refresh 成功，build logs 10 筆皆 Info（舊時間戳 17:53，無 Error），Play 後 normal logs 565 筆皆 Info，包含 VoyageData SelfTest、Adventure 與 HUD 初始化；已 stop。這只驗證設定落盤和啟動回歸，沒有證明自動翻譯或其他語言 UI 正確。

# Open questions

- 官方素材庫中可用飛空船、甲板、天空背景、巴洛古或空賊相關素材需要進 Maker 實際確認。
- 交易貨物買低賣高要如何接到目前金幣/雲海結晶循環？
- 下一步要先做正式 HUD/UI，還是先補交易資料表？
- 本機已找到 MSW Maker MCP 入口：C:\Users\USER\AppData\Local\Nexon\MapleStory Worlds\MakerMCP\msw-maker-mcp.bat。
- Codex config 已加入 mcp_servers.msw_maker，並備份為 C:\Users\USER\.codex\config.toml.bak-msw-20260709-103130。
- 目前 Codex session 已能看到並使用 MSW Maker MCP 工具。
- MSW Maker MCP 已確認可操作 efresh、play、stop、logs、screenshot、keyboard_input、xecute_script。
- Phase 0 第一版已採用 Maker 內 @Logic 按鍵文字流程，不先做完整 UI。
- Antigravity 重新開啟後可 discover；Gemini review 建議將 `math.random` 改為 `_UtilLogic:RandomIntegerRange`，並將整數狀態改為 `integer`，已套用並重新通過 Maker MCP 驗證。

## 2026-07-14 A+C 決策與工具備註

- A+C 已選；高難度離船空戰只入 backlog。
- Orange Mushroom 真實動畫 RUID 已找到，但本地無 native model Entry ID；需在 Maker 執行 Add to Workspace / Copy Entry ID。
- apply_patch 因 Windows unelevated split writable roots 失效；官方 elevated 全域設定待主人明確二次批准。

## 2026-07-14 自製初始船 v2

- imagegen 產製原創楓谷感小艇：移除螺旋槳、桅杆置中、帆放大；透明 PNG：MissionCenter/assets/starter-airship-v2.png。
- MSW SpriteRUID：753b0027bfc44c33a0267cd11379bc91。
- MapBuilder 已套用 scale 0.35、近水平 deck foothold、水晶／玩家／菇菇座標；runtime 可逆停用 foothold-6400 renderer 後，截圖 maker_play_20260714_025715_666.png 視覺通過（完整小艇、人物在甲板、舊巨艦消失），永久 Enable=false 亦已 snapshot 通過。
- 最終 stop→refresh→build→screenshots 因 Codex usage limit 阻擋，解鎖時間 2026-07-20 03:15 Asia/Taipei；任務狀態已 Completed / Full Pass：永久 map refresh；build logs kind=build status ok count=0；normal logs status ok count=171 errorCount=0；Play 截圖 maker_play_20260714_080450_215.png；BeginRaid 截圖 maker_play_20260714_081054_505.png；08:10:47 spawned×3、08:10:59 raid complete。AC-T7/B-T1 backlog 保留。

# Research log

| Pre-search idea | Source | Adopted insight | License status |
| --- | --- | --- | --- |
| 比賽是否允許 AI 與此題材 | https://maplestoryworlds.nexon.com/events/zh-tw/2026globalcontest | 競賽頁明確允許 AI；評分重視 IP 詮釋、完成度、永續性 | 官方活動頁，僅作需求參考 |
| 玩家能否支援楓谷式走跳/甲板戰 | https://maplestoryworlds-creators.nexon.com/docs?postId=750 | 官方有 RigidbodyComponent、踏板、Map Layer 等楓谷式移動概念 | 官方文件，僅作 API/概念參考 |
| 是否能做移動踏板或船甲板概念 | https://maplestoryworlds-creators.nexon.com/docs?postId=579 | 官方 Moving Foothold 支援動態踏板；後續可研究但不進 Phase 0 | 官方文件，僅作 API/概念參考 |
| 是否能做船砲/遠程攻擊 | https://maplestoryworlds-creators.nexon.com/docs?postId=934 | 官方有遠距離發射體消滅怪物範例；可支撐後續砲台或甲板戰 | 官方文件，僅作 API/概念參考 |


## 2026-07-14 航線桌／交易板 UI 驗收

- 已透過 maker_list_maplestory_maps 確認 MSWM 內有 7,948 筆 MapleStory 地圖目錄；航線桌視覺採 MSW 資源庫的世界地圖 RUID 081dcd59d4dc40dc96650b74bb9b650e，並疊加節點路線 RUID e048a72dcf704cc19bdec16d2ca8f74d。
- 交易板沒有找到乾淨完整的 NPC 買賣視窗；未採用含韓文警告／強化率素材，改用黑色交易底板＋SHOP 徽章 3e3f2ccc5c8343a88ec12abc05e36d40、水平商品列 da3b13dcfef246f0ba3085a8377cc46a、藍粉漸層內容板 d43a5420174143f89436880277f7800e，保留既有買／賣／數量按鈕綁定。
- UIBuilder 產生並驗證 ui/GreatVoyageRouteDesk.ui，清除暫時 root 裝飾節點後 ui_lint: clean。

## 2026-07-14 官方港口／航行背景與音訊

- Maker 官方地圖索引：魔法森林／Ellinia = `101000000`；天空之城／Orbis = `200000000`。
- 已確認資源庫沒有乾淨的「單張完整港口全景」；因此採官方圖層組合，避免假稱為完整原圖：魔法森林樹線 `bd1e5fadbd1a46e9ada8cd8959bc2dab`、天空之城 Orbis 地圖條 `10ceca7d063e48f09f76b1f5517ca57b`。
- 飛行背景使用官方天空／雲層資源：`35dbcbb0c21a42af8f25cc8c717328e3`、`fea861416a8e4ff59afe27171b0b0aa1`。
- 港口 BGM：`f500d59150d34bda86f562510f696213`（OGG，72.829 秒）；飛行雲海音訊：`f4f42aa653be4fa7b159aae8d6dd1128`（OGG，17.424 秒）。
- 以 map-scoped `GreatVoyageBackdropController` 掛在 `GV_SkyBackdrop`，透過 `SpriteRendererComponent`／`SoundComponent` 切換圖層與音訊；未修改 `Global/`、`Environment/` 或手寫 `.codeblock`。

## 2026-07-15 Maker MCP 掛載檢查

- ALL_TOOLS 未列出任何 msw_maker／maker_refresh_workspace 工具。
- MCP resources 只有一般 Codex connectors，沒有 MSW Maker server。
- 此阻塞屬工具未掛載，不是 workspace 授權問題。
- 恢復後第一個動作必須是 refresh；第二個動作檢查 build logs；第三個動作才可 Play GreatVoyageHUD。

## 2026-07-15 Maker MCP 恢復與地圖切換重驗

- Maker MCP 已恢復；refresh 成功，兩次 build logs 均為 0。
- 初次 Play 發現 6 個 LEA-3021：官方匯入裝飾 Entity 誤掛 SpawnLocationComponent；以 MapBuilder 移除元件後保留 Transform／Sprite／RUID，重驗 runtime 0 Error。
- GreatVoyageHUD 初始化完成；地圖狀態依序出現 official scenes initialized port=forest、flight start target=sky、arrived port=sky。
- 三場景截圖保存於 MissionCenter/evidence/2026-07-15/；飛行截圖使用 Play Test 臨時延長計時，stop 後狀態已清除，未修改正式腳本。

## 2026-08-05 新三場景 Wave 1 交接點

- 已建立 `map/map_forest_port.map`、`map/map_airship_deck.map`、`map/map_orbis_port.map`，皆由 MapleTile 模板建立並匯入官方場景。
- 自製初始船 v2 已配置於三圖，RUID `753b0027bfc44c33a0267cd11379bc91`；港口縮放 0.18，甲板圖縮放 0.35。官方航行地圖巨型飛船的可見 MapObject／TileMap 圖層已停用，待 Play 截圖確認。
- 三張地圖皆已清理為單一 SpawnLocation，磁碟解析無重複 Entity Path；結構檢查不能代替 runtime。
- 編輯畫面證據：`MissionCenter/evidence/2026-08-05/wave1_forest_edit.png`、`wave1_airship_edit.png`、`wave1_orbis_edit.png`。
- 當前阻塞：兩個 Maker MCP 端點均回報 `Maker is not running`；系統同時可見 Maker 行程與多個 `MakerMCP_run.exe` 行程，推定為本對話 MCP bridge/session 未重新註冊。換新 Codex 對話後第一步必須 `maker_get_current_map`，成功才依序 refresh → build logs → Play 截圖。
- Wave 1 尚未通過，因此尚未召喚嚴格評審；不要跳到 GV-T2 實作。

## 2026-08-05 GV-T1 Maker 重新掛載結果

- `maker_get_current_map` 成功：`map01`、Edit mode；MapBuilder 確認三張目標圖皆為 MapleTile（`TileMapMode=0`）。
- `refresh_workspace` 成功；build logs `count=0`。
- 魔法森林 Play runtime 無 Error，但舊 GreatVoyageHUD／RouteDesk 預設顯示，遮住大部分場景；QA 暫時關閉兩個 UI root 並向右步行後，仍只看見官方巨型飛船，未取得自製初始船 v2 完整可辨識的通過畫面。
- 新證據：`wave1_forest_play_ui_obstructed.png`、`wave1_forest_play_ui_hidden.png`、`wave1_forest_play_walk_right.png`。依中途失敗規則已 Stop，未續跑飛行甲板與天空城；GV-T1 維持 Blocked。

## 2026-08-06 E8 Wave 1 通過

- Maker 指定順序成功：get_current_map → refresh → build logs 0。
- 三圖皆 MapleTile（TileMapMode=0），方向鍵實走通過；證據位於 MissionCenter/evidence/2026-08-05/ 的 wave1b 系列。
- 魔森與天空城玩家船 RUID 753b0027bfc44c33a0267cd11379bc91 已調整到可辨識碼頭位置與顯示層；飛行甲板恢復官方飛船場景。
- 舊 Phase0/DeckRaid 全域熱鍵移除；甲板四個舊 Portal 三層停用；舊 HUD/RouteDesk 預設透明且不攔 Raycast。
- Terra 最終複審：PASS — 無剩餘批評。Antigravity 視覺審查判定可進下一波，後續 UI 應補港口／目的地文字，甲板底部背景斷層列為視覺 polish。

### 2026-08-06 商店／對話套件研究

| Pre-search idea | Source | Adopted insight | License status |
| --- | --- | --- | --- |
| 優先採官方 shop package | https://github.com/MSW-Git/MSWPackages/tree/main/shop-package | 套件實際是 WorldShop／付費商品流程，不適合本地金幣與貨艙買低賣高；不採用 | 官方 GitHub，僅研究 |
| 優先採官方 dialog package | https://github.com/MSW-Git/MSWPackages/tree/main/dialog-package | 可借鑑打字機與選項流程，但整包含 Alpha1 範例且擴張面過大；本案採近距情境式小對話，不整包匯入 | MIT；僅借鑑概念 |

## 2026-08-06 E8 Wave 2 通過

- GreatVoyageAdventureController 與 GreatVoyageAdventure.ui 接通靠船提示、世界地圖、鍵盤 E/Enter/Escape、甲板中繼與抵港。
- 魔森／天空城自製初始船 v2 固定 RUID 753b0027bfc44c33a0267cd11379bc91，港口 scale 恢復 0.18 並調整朝向；不再以過大比例混入官方背景。
- Maker 實走完成 sky→deck→forest，並有 forest→deck→sky 日誌；build count=0、runtime 全 Info。
- Terra 最終 PASS — 無剩餘批評；Antigravity 視覺／UX PASS（request 724dbcf9-4178-4bf2-9c53-3f69c51654b7）。

## 2026-08-06 E8 Wave 3 與最終驗收通過

- 兩港商人改為可步行位置，互動採真正 2D 距離；天空城登船點 (4.0,-1.43)、魔森登船點 (1.2,-0.83)，避免上下平台隔空互動。
- 虛構貨物全部撤除，改用楓谷正式紅色藥水／藍色藥水／橘色藥水；官方 item sprite RUID 分別為 234aca1a4ce946119b68e3717991e775、7e9b39b73f4945b1a8d77db6c99a6946、2debf574d6d04f7083e980dbc8f462d9。
- 商店 UI 依主人參考圖採圖示商品列、商人對話、金幣、貨艙、選取、數量與買賣回饋；UIBuilder lint clean。
- Maker 最終 build count=0；runtime count=155、nonInfo=0；藍色藥水跨港交易 120→132G。
- Terra 第三輪 PASS — 無剩餘批評；Antigravity 視覺終審 PASS（request 75ab1ea7-3e62-4abe-89b7-0be414032bcb）。

## 2026-08-06 E8 船體／梯子回歸修正

- 主人手動調整的天空城大船構圖已重建並落盤：GV_PlayerShip Position=(0.95,2.91)、三圖 Scale=(0.40,0.40,1)，RUID 維持 753b0027bfc44c33a0267cd11379bc91。
- GreatVoyageAdventureController 不再使用絕對登船世界座標；改由船 WorldPosition 加上依 Scale 換算的港口相對偏移，因此船移動或改大小後互動點同步。
- 天空城 MapObject_17 新增 ClimbableComponent；Maker 實測按住 ↑ 後角色 y=-1.429→0.068。
- 飛行甲板隱藏原版飛船所有 SpriteRenderer、保留碰撞，並以自繪船置中；魔森停用原版船 MapObject_1、移除 npc-5097、保留森林商人．艾琳。
- 最終 build=0、runtime nonInfo=0；Terra：PASS — 無剩餘批評。證據：MissionCenter/evidence/E8_ship_follow_fix/。
