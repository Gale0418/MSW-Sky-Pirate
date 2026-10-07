# CodeRabbit 審查與 Git checkpoint

日期：2026-10-07（Asia/Taipei）。使用者已授權上傳程式碼至 CodeRabbit，直接在 main 儲存與推送，不建立 PR 或專案分支。

## 審查結果

CodeRabbit CLI 0.7.6 已登入，以隔離 Git 資料夾的 main 基準執行：

```text
coderabbit review --agent --base main --uncommitted -c review-context.md
```

本輪使用 1 次審查；遵守每小時最多 3 次、每次最多 150 檔。納入全部 16 個有效 mLua 腳本，包含未變更的舊腳本；只在審查副本把副檔名改為 `.lua`，保留 MSW 語法並提供引擎說明。大型商品資料 literal 以審查專用空表替代，其快取、索引、抽樣與全部方法仍保留。生產商品資料未刪改。

排除地圖與 UI 的大型序列化資料、`.codeblock`／原生定義、二進位素材、研究快照、暫存 builder 與產生檔。沒有把檔案拆碎或塞入無關內容湊 150 檔。

實際完成事件為 `{"type":"complete","status":"review_completed","findings":0}`；`reviewedFiles` 列出 16 個腳本副本及 `review-context.md`。**CodeRabbit raised 0 issues.** 無外部建議需要查證或修復，未耗用第二／第三次掃描。另執行 `coderabbit review findings` 時回報 `No stored review findings found for this scope`，因此結果依本次串流完成事件，不宣稱 CLI 有保存可回查的 findings。

審查腳本：Economy 的 CommodityCatalog、MarketPricing、PlayerMarket；BackdropController、DeckMushroom、DeckRaid、PlayerAttack、VoyageData、VoyageState、Phase0VoyagePrototype；ShipVisual 的 DeckBounds、VisualClient；UI 的 AdventureController、HUDController、Onboarding、RouteDeskController。名稱均保留 `GreatVoyage`／`GVShip` 前綴與原來源路徑。

## 本地驗證

- Python／Lupa 對 358 個方法與事件處理器 body 編譯成功；僅語法檢查時將 mLua `continue` 轉成 Lua `break`，不把該轉換當行為測試。16 組 `.mlua`／`.codeblock` 配對存在。
- 實際執行商品資料與方法：184 筆商品、唯一 ID、正價、四港貨架重開一致、只含已核實產地商品且最多 12 項。
- 624 組已核實商品／港口案例：報價不修改輸入、逐件價格不增加、需求恢復、BOSS 庫存 1–10、超量拒買、耗盡後拒買。未核實商品報價無效。
- MapBuilder 讀取六張地圖，`TileMapMode` 皆為 0，CoreVersion 為 `26.7.0.0`。
- 四個 UI 的 UIBuilder `validate()` 均為 `[]`；專用 lint 0 errors。Adventure 為 83 warnings（HEAD 基線 81）、Onboarding 為 3 warnings；HUD 與 RouteDesk 無 warnings。這些靜態排版警告未冒充實際畫面缺陷或實機通過。
- 舊 `.builder-work/commodity-economy/verify_economy_changes.py` 因精確提示文字已變更而失敗，保留此觀察；未改寫舊測試偽造 Pass。新測試直接執行當前生產方法。

本輪 helper、manifest、完整 lint 與測試輸出保存在本機 `.tmp/git-review-20261007/`，不納入 Git；`.builder-work/` 加入 ignore，避免研究及本機診斷資料混入提交。

## 限制與待辦

官方 Maker MCP 完成 initialize，但 `tools/list` 回傳 `[]`，無可用 refresh／build logs／Play／runtime logs。因此本輪沒有執行或宣稱 Maker 實機驗證；新市場存檔與跨世界一致性、真人多人、PC 點擊／手機、UI 靜態警告仍需實機回歸。既有 M1／QA／Review／Blocked 狀態保留，不將這次 Git checkpoint 當成整個遊戲驗收完成。

README 已更新四港、個人市場與保存範圍；Mission Center 保存本輪結果並同步衍生視圖。直接推送 main 是本次 Git 交付目標，遠端結果於收尾回查。
