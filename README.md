# 楓谷空賊王

**MSW Sky Pirate** 是以 MapleStory Worlds（MSW）與 mLua 製作的空中航海冒險。玩家可在魔法森林、天空之城、玩具城與納希沙漠之間啟航，在航行甲板上經歷短自動空戰，靠港後向商人買賣貨物、購買船舶與配置改裝卡。

目前專案包含四港、航行甲板及入口地圖；六張地圖皆使用 MapleTile（`TileMapMode = 0`）。介面提供新手導覽、航圖、商品／改裝卡市場、船舶與貨艙管理。

- 商品圖鑑共 184 筆，已核實商品才能交易。每港依世界工作階段種子抽取最多 12 項貨架，重開商店保留同一份商品。
- 買入使用設定價格；出售逐件計算個人市場的需求壓力，經過時間後恢復。BOSS 商品採帳號／商品／三小時週期的固定補貨量。
- 個人市場壓力與補貨紀錄使用 `UserDataStorage`，分片批次讀寫、30 秒儲存變更，離線時補存。金錢、貨物與船舶仍為目前遊玩工作階段的狀態，不代表整套進度已永久保存。
- 五款船舶、T1 三通用改裝槽、甲板邊界救援、船體前景與砲彈動畫沿用現有遊戲流程。

主要來源位於 `RootDesk/MyDesk/`，地圖在 `map/`，介面在 `ui/`。Maker 會產生腳本的 `.codeblock` 配對；修改內容後應在編輯模式執行 Refresh，再檢查 build 與 runtime logs。專案 CoreVersion 為 `26.7.0.0`；`.map`／`.model`／`.ui` 使用 MSW 專用 builder 維護。

規格與後續工作見 [M1 設計](docs/GreatVoyage-M1-GDD.md)、[Roadmap](docs/GreatVoyage-Roadmap.md) 與 [Mission Center 任務](MissionCenter/tasks.md)。2026-10-05 的商品價格表與文案文件是當日的資料快照；市場動態成交價以伺服器計算為準。

2026-10-07 的 [CodeRabbit 與離線驗證紀錄](docs/CodeRabbit-Review-20261007.md)涵蓋全部 16 個遊戲腳本（包含既有腳本），外部審查回報 0 issues。Maker 尚未提供工具，本輪未宣稱實機通過；M1 的完整回歸與既有 UI 排版警告仍待驗收。
