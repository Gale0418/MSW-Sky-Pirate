<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- Deprecated compatibility view: focus.md is generated from tasks.md only and must never be edited or treated as a second lifecycle source. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=a34a2a1c2d729497674ebd6dc33eb5290d304e3d1e222ebe3dbc8ee123462584 -->
# P0 Focus

- Source of truth: `tasks.md`
- Unfinished P0: 21

| ID | Title | Status | Next action | Depends on | Verification |
| --- | --- | --- | --- | --- | --- |
| GV-CARGO-CAPACITY-20261008 | 空位可續買與混裝貨艙 | Review | 已完成受影響本地與 Maker 隔離驗證；發布時補真帳號混裝保存／重登，回退需保留 v2 reader。 | GV-SAVE-DATA | ST-GV-CARGO-MIXED-20261008；78 tests/5 subtests、Native table RPC、商會選賣及船艙第二頁；Rabbit 1 fixed/1 rejected |
| GV-SAVE-V1 | 完整帳號永久存檔 V1 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 |  | 對應子任務的存讀、故障與 Maker 證據 |
| GV-SAVE-DATA | 版本化帳號快照與市場遷移 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 |  | 金錢、貨物成本、五船船況、三槽及卡數守恆；壞檔／未來版本拒絕覆寫 |
| GV-SAVE-LIFE | 單一寫入者與登入離線保存 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 | GV-SAVE-DATA | 寫入失敗／延遲／快速重登不清掉未存更新；載入失敗不發初始資產 |
| GV-SAVE-FLOW | 交易、出航與沉船整合 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 | GV-SAVE-LIFE | 出發前失敗拒絕航行；航行離線回出發港；沉船清貨不得因重登復原 |
| GV-SAVE-QA | 存檔全流程與故障回歸 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 | GV-SAVE-FLOW | 同版 build/runtime、正面 VRF、守恆、成本與故障證據；未驗項明示 |
| GV-M1 | Great Voyage M1：港口資料、世界地圖 UI 與整合 QA | In Progress | 完成四港往返、交易與箭頭端點驗收，修正剩餘問題 | E8, GV-M1-P3 | 四港／甲板／交易／HUD、60 秒自動抵港及 Maker 視覺證據齊全；再由主人確認主觀視覺 |
| GV-M1-P1 | Phase 1：Data & Geometry | Review | 重驗四港資料、直線幾何與空域分段；核對世界圖座標 | E8 | 四港與甲板 MapleTile mode／Body／入口、路線正反向與邊界測試有證據 |
| GV-M1-P3 | Phase 3：Ports Integration & QA | In Progress | 補四港完整往返、無舊事件與交易回歸；處理驗收缺陷 | GV-M1-P1, GV-M1-P2 | 四港皆可抵達／開商店／再次出航，60 秒倒數與船體保留有 Maker 證據 |
| GV-CABIN | 船艙管理介面與後續實體船艙 | In Progress | 先驗收管理、五船買換與三槽，再接新船體及短自動空戰 |  | 船況與貨物來源一致、維修安全、現有四港流程可回歸 |
| GV-CABIN-UI | 小舢板管理介面與伺服器船況 | Review | 依v15凍結資料進行獨立比對；正式評論待四項數值預算 |  | 兩檔 82 methods Lua 編譯、情境 8/8、全 58 項 UI 引用有效；新 UI 無新增 lint 警告；Maker runtime 待驗 |
| GV-CABIN-QA | 管理介面與四港回歸驗收 | In Progress | 依v15凍結資料進行獨立比對；正式評論待四項數值預算 | GV-CABIN-UI | Maker refresh/build/Play、四港航行交易、PC 與手機畫面 |
| GV-EVENTS-OFF | 停用所有舊航行事件與甲板襲擊 | Review | Maker refresh/build/Play 驗證四港自動抵港、無事件/菇菇/舵輪提示且交易與船艙正常 |  | 12/12 直航模擬、3/3 退休邊界案例、船艙 8/8 回歸；UIBuilder validate=[]、58/58 引用有效；runtime 待驗 |
| GV-SHIP-SHOP | 五船購買、換船與專屬加成 | In Progress | 接通四港商人的船舶買賣、獨立船況與伺服器驗證 | GV-CABIN-UI | 真實 RPC 驗證金額不足、重複購買、距離、航行中拒絕、超載拒絕、受損換船與加成不疊加 |
| GV-SHIP-MODS | T1 三通用槽與基礎改裝配置 | In Progress | 驗證三槽配置、拆卸、同卡疊加及最終屬性 | GV-SHIP-SHOP | 位置/航行/持有/槽位/卡 ID 伺服器驗證；超載拒絕；能力從基礎重算；換裝不治療 |
| GV-SHIP-ART | 五款正式船體與動畫引擎尾跡 | In Progress | 確認單船透明素材匯入與原生動畫 RUID，接入實際畫面 |  | 新手及四低級船造型對應正確；引擎持續動畫；甲板與登船點回歸 |
| GV-AIRBATTLE | 短自動空戰與沿途空域怪物 | Review | 審閱砲彈與空戰 PC 畫面；其他船型砲口隨五船對位驗收 | GV-SHIP-SHOP, GV-SHIP-ART | 最新 Maker build／砲彈飛行與命中 HP／勝利續航／沉船清貨／回出發港／重結算拒絕／免費 T0 修理；12 路線程式回歸 |
| GV-SHIP-DECK-BOUNDS | 五船共用甲板邊界、船殼遮擋與離船還原 | Review | Maker MCP 恢復後補額外重新匯入回歸；技術結果待審閱 | GV-SHIP-ART | ST-GV-DECK-BOUNDS-002 已通過；原始 logs 與 ST-GV-DECK-RELOAD-003 限制並存 |
| GV-CARDS-STATE | 改裝卡庫存、交易與有效能力 | Review | 依v15凍結資料進行獨立比對；正式評論待四項數值預算 |  | 金錢／卡數守恆、非法請求拒絕、換裝不治療、超載拒絕、百分比回血／鍋爐、合法敵池 |
| GV-CARDS-UI | 商品商人卡片市場與三槽卡位 | Review | 依v15凍結資料進行獨立比對；正式評論待四項數值預算 |  | UIBuilder lint、UUID綁定、Maker真RPC與卡位／船艙畫面 |
| GV-CARDS-QA | 卡片商店與航行整合驗收 | Review | 依v15凍結資料進行獨立比對；正式評論待四項數值預算 | GV-CARDS-STATE, GV-CARDS-UI, GV-CARDS-ART | build/runtime logs、可重複測試、畫面證據及受影響四港回歸 |
