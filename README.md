# 楓谷空賊王

**MSW Sky Pirate** 是以 MapleStory Worlds（MSW）與 mLua 製作的空中航海冒險。玩家可在魔法森林、天空之城、玩具城與納希沙漠之間啟航，在航行甲板經歷短自動空戰，靠港後向商人交易、購買船舶與配置改裝卡。

目前專案包含四港、航行甲板及入口地圖；六張地圖皆使用 MapleTile（`TileMapMode = 0`）。介面提供新手導覽、航圖、商品／改裝卡市場、船舶與貨艙管理。

- 商品圖鑑共 184 筆，僅已核實商品可交易。各港依世界工作階段種子抽取最多 12 項貨架，重開商店仍保留同一份商品。
- 買入使用設定價格；出售逐件計算個人市場需求壓力，並隨時間恢復。BOSS 商品採帳號／商品／三小時週期固定補貨。
- Save V1 以版本化帳號快照保存金錢、貨物數量與成本、所有船況、使用中船、未裝卡與三個改裝槽，以及個人市場壓力和補貨紀錄；並遷移既有市場資料。一般變更每 30 秒背景儲存，程式另設離場保存處理。
- 出航前保存安全快照，抵港與沉船先保存結算；重新連線回到出發港，不重播戰鬥或獎勵，已結算沉船的貨物損失會保留。
- 船艙與商會金額使用錢袋、金屬數字與直立楓葉幣。貨艙採木牆背景與透明貨架；Maker 原生 UI checkpoint 以測試貨物確認 12 格分三層承托、沒有重疊。成功買賣有音效回饋；購船成功另有慶祝音效與視覺效果，失敗、重買或重登不慶祝。
- 五款船舶、T1 三通用改裝槽、甲板邊界救援、船體前景與砲彈動畫沿用既有遊戲流程。

主要來源位於 `RootDesk/MyDesk/`，地圖在 `map/`，介面在 `ui/`。Maker 會產生腳本的 `.codeblock` 配對；修改內容後應在編輯模式執行 Refresh，再檢查 build 與 runtime logs。`Environment/config` 宣告的 `CoreVersion` 為 `26.10.0.0`；唯讀的 `Global/WorldConfig.config` 仍記為 `26.7.0.0`。地圖與模型、介面設定使用 MSW 專用 builder 維護。

規格與後續工作見 [M1 設計](docs/GreatVoyage-M1-GDD.md)、[Roadmap](docs/GreatVoyage-Roadmap.md)、[Save V1 規格](docs/GreatVoyage-Save-V1.md)、[完整驗證與限制](docs/Save-V1-Verification.md) 與 [Mission Center 任務](MissionCenter/tasks.md)。2026-10-05 的商品價格表與文案文件是當日資料快照；市場動態成交價以伺服器計算為準。

Save V1 目前維持 **Review**。本地測試與 Maker 存讀、貨艙及介面 checkpoint 有紀錄；正式環境仍須在維護窗口預置 bootstrap gate，跨 World instance 的 CAS 競態與真實網路斷線也尚無驗證證據，因此不代表存檔總體驗收或遊戲發布完成。細節與限制見 [Save V1 驗證紀錄](docs/Save-V1-Verification.md)。

2026-10-07 的 [CodeRabbit 與離線驗證紀錄](docs/CodeRabbit-Review-20261007.md) 是既有歷史審查，涵蓋 16 個遊戲腳本並記錄 0 issues；當時 Maker 工具不可用，未宣稱實機通過。2026-10-08 完整審查涵蓋 23 檔，4 issues 均查證修正，修正後複查 0 issues；53 項測試與 5 個子案例通過，Maker 隔離市場／離場探針通過。範圍、原始回應與未驗界線見[本輪審查紀錄](docs/CodeRabbit-Review-20261008.md)。
