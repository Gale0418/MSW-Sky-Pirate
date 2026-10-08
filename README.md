# 楓谷空賊王

**MSW Sky Pirate** 是以 MapleStory Worlds（MSW）與 mLua 製作的空中航海冒險。玩家可在魔法森林、天空之城、玩具城與納希沙漠之間啟航，在航行甲板經歷短自動空戰，靠港後向商人交易、購買船舶與配置改裝卡。

目前專案包含四港、航行甲板及入口地圖；六張地圖皆使用 MapleTile（`TileMapMode = 0`）。介面提供新手導覽、航圖、商品／改裝卡市場、船舶與貨艙管理。

- 商品圖鑑共 184 筆，僅已核實商品可交易。各港依世界工作階段種子抽取最多 12 項貨架，重開商店仍保留同一份商品。
- 貨艙每件占一格，有空位可續買同種或混裝不同商品；商會可選各種商品出售，成本依進貨批次 FIFO 保留。帳號格式 schema 2 相容讀取 v1，保留舊貨物與金額。詳見 [續買與混裝修正](docs/Cargo-Mixed-Verification-20261008.md)。
- 買入使用設定價格；出售逐件計算個人市場需求壓力，並隨時間恢復。BOSS 商品採帳號／商品／三小時週期固定補貨。
- Save V1 以版本化帳號快照保存金錢、貨物數量與成本、所有船況、使用中船、未裝卡與三個改裝槽，以及個人市場壓力和補貨紀錄；並遷移既有市場資料。一般變更每 30 秒背景儲存，程式另設離場保存處理。
- 出航前保存安全快照，抵港與沉船先保存結算；重新連線回到出發港，不重播戰鬥或獎勵，已結算沉船的貨物損失會保留。
- 船艙與商會金額使用錢袋、金屬數字與直立楓葉幣。貨艙採木牆背景與透明貨架；Maker 原生 UI checkpoint 以測試貨物確認 12 格分三層承托、沒有重疊。成功買賣有音效回饋；購船成功另有慶祝音效與視覺效果，失敗、重買或重登不慶祝。
- 五款船舶、T1 三通用改裝槽、甲板邊界救援、船體前景與砲彈動畫沿用既有遊戲流程。

主要來源位於 `RootDesk/MyDesk/`，地圖在 `map/`，介面在 `ui/`。Maker 會產生腳本的 `.codeblock` 配對；修改內容後應在編輯模式執行 Refresh，再檢查 build 與 runtime logs。`Environment/config` 宣告的 `CoreVersion` 為 `26.10.0.0`；唯讀的 `Global/WorldConfig.config` 仍記為 `26.7.0.0`。地圖與模型、介面設定使用 MSW 專用 builder 維護。

規格與後續工作見 [M1 設計](docs/GreatVoyage-M1-GDD.md)、[Roadmap](docs/GreatVoyage-Roadmap.md)、[Save V1 規格](docs/GreatVoyage-Save-V1.md)、[完整驗證與限制](docs/Save-V1-Verification.md) 與 [Mission Center 任務](MissionCenter/tasks.md)。2026-10-05 的商品價格表與文案文件是當日資料快照；市場動態成交價以伺服器計算為準。

正式服首次建檔另需本專案自訂的 `GVSaveV1Bootstrap/gate=OPEN` 維護設定；缺值會保護資產並拒絕建檔。Maker 的測試結果不能證明正式環境已完成此設定。15:06 正式服回報 `uncertain code=0`，新版已區分初讀缺值與未知 claim，並補上 phase/valueKind 診斷；95 項本地測試與 24 個子案例通過、兩檔 CodeRabbit 0 issues，新版於 15:41 通過 Maker 原生編譯與 5 個隔離診斷案例；16:57 正式服已確認新版，但自訂 gate 仍缺值，首次建檔待初始化。缺值提示、載入畫面與核驗步驟見 [正式服載入診斷](docs/Published-Save-Diagnosis-20261008.md)。

Save V1 目前維持 **Review**。本地測試與 Maker 存讀、貨艙及介面 checkpoint 有紀錄；正式環境仍須在維護窗口預置 bootstrap gate，跨 World instance 的 CAS 競態與真實網路斷線也尚無驗證證據，因此不代表存檔總體驗收或遊戲發布完成。細節與限制見 [Save V1 驗證紀錄](docs/Save-V1-Verification.md)。

2026-10-07 的 [CodeRabbit 與離線驗證紀錄](docs/CodeRabbit-Review-20261007.md) 是既有歷史審查，涵蓋 16 個遊戲腳本並記錄 0 issues；當時 Maker 工具不可用，未宣稱實機通過。2026-10-08 完整審查涵蓋 23 檔，4 issues 均查證修正，修正後複查 0 issues；53 項測試與 5 個子案例通過，Maker 隔離市場／離場探針通過。範圍、原始回應與未驗界線見[本輪審查紀錄](docs/CodeRabbit-Review-20261008.md)。

### 登入版本辨識

新手教學右下角顯示淡金色小字版本 `v2026.10.08.2`，開始冒險後會跟著教學遮罩隱藏；同次登入的 CLIENT 紀錄包含 `[Onboarding] shown; build=v2026.10.08.2`。版本由 `RootDesk/MyDesk/UI/GreatVoyageOnboarding.mlua` 的 `buildVersion` 統一提供，發布新版時請遞增尾碼。本維護版 Maker Refresh／原生驗收已通過，登入版本文字核對成功；正式服需在 Maker 再發布、等完成通知後離開世界並重登核對。此標記辨認客戶端教學程式版本，存檔伺服器仍要另外核對 `[SERVER] [SaveV1]` 診斷與 gate 設定。


### 正式服首次建檔維護

16:57 的正式服新版日誌已確認自訂 `GVSaveV1Bootstrap/gate` 缺值。依主人授權直接準備 `v2026.10.08.2` 一次性維護版：`GreatVoyageSaveMaintenance` 已啟用，限定本世界與創作者帳號，只在單人／唯一 instance、確認 gate 不存在時寫一次 `OPEN` 並精確回讀。已有 OPEN 不重寫；BUSY、空值字串、錯誤、結果未知均不覆寫或重送；不讀寫玩家存檔。維護版暫停普通載入，回讀成功後須停用 helper 並再次發布一般版，才開放存檔。

本地 **114 tests／31 subtests** 通過；CodeRabbit 首輪 1 minor 已查證修正，五檔複查 0 issues（兩輪）；Maker build 68 Info、runtime 44 Info，0 Warning／Error，註冊、維護隔離、版本文字與六個假 storage 情境皆有正面紀錄；已 Stop 回 edit。ReleaseOnly instance 清單尚未在正式服執行，清單只是快照，不能當作跨 instance 鎖。正式服仍需從 Refresh 後的 Maker 發布維護版、退出舊連線並重新登入，將 `[SaveV1][Maintenance]` 回執核對後撤下維護版；未知寫入不可以重登重試。詳細操作與待驗項見 [正式服診斷](docs/Published-Save-Diagnosis-20261008.md) 與 [Maker 回執](docs/reviews/2026-10-08/published-save/maintenance-1657/maker-receipt.json)。
