# 貨艙續買與混裝修正｜2026-10-08

使用者在購買一件後仍有七個空位，卻被「先賣出再進貨」拒絕。根因是 BuyGood 在市場讀取前後都拒絕任何非空貨艙。

現在每件占一格，可在剩餘容量內續買同種或混裝不同商品。伺服器在可能讓出執行權的市場讀取後，重新驗證當前容量、位置、航程與玩家狀態；金額、BOSS 庫存和商品上架驗證保留。滿艙或超量失敗不扣錢、不改貨物。

## 貨物與存檔

- 貨物保存為依購買順序排列的 lots，每批記錄商品 ID、件數和單件進貨成本；相鄰且同價的同商品可合併。
- 金錢與貨艙總數依同一次交易更新。出售頁列出各商品，出售數量以選中商品的持有量為上限，其餘商品保留；成本依選中商品的 FIFO 批次計算。
- 船艙逐件展開批次，保留每頁十二格與第二頁偏移；舊快捷 SellCargo/SellCargoQuantity 沿用首種貨物的語意，現代商會使用明確商品 ID。
- 完整貨物清單透過帶經濟版本的 Client table RPC 同步；較舊回執不覆寫較新清單。同一版本不在每次航程刷新時重送清單，明確請求則重送。
- 帳號 schemaVersion 升至 2，但仍使用原有 gv_profile_v1 儲存鍵。v1 先完整驗證，再於記憶體遷移；原始 raw 仍是 CAS 比對基準，載入不因遷移自行標 dirty。後續合法更新才寫 v2。
- 空 lots 明確編碼為 JSON 陣列 []；空卡庫存仍為物件 {}。未知版本、無效批次、非連續索引、總量不一致與超載全部拒絕。

## CodeRabbit

沿用使用者的程式碼上傳授權，於約 11:22 啟動一次完整隔離審查。輸入十個程式／測試檔與一個上下文檔，共十一檔；大型資料 literal、美術、原生 API、UI JSON 與產生檔事先排除。沒有為湊 150 檔建立假程式。這是該 rolling hour 的第三次，未超過每小時三次上限。

CLI exit 0，完成回應列出兩項 minor：

| 建議 | 查證 | 處置 |
| --- | --- | --- |
| AdjustQuantity 在 VoyageState 未就緒時讀取 nil | 新增行為測試重現 LuaError | 有效，前置 guard 修復，回歸通過 |
| 未知商品的 false sentinel 會被當成商品 | 現有程式已用 cargoItems[index] or nil，新增未知商品測試通過 | 排除；保留格位、不顯示未知圖示、不崩潰 |

本輪沒有額外外部複查，也不宣稱兔子回報零 issues。原始結果：[coderabbit.ndjson](reviews/2026-10-08/cargo-mixed/coderabbit.ndjson)。[審查輸入](reviews/2026-10-08/cargo-mixed/review-input-manifest.json) 與 [修復後來源](reviews/2026-10-08/cargo-mixed/final-source-manifest.json) 分別保留雜湊；外部審查之後的差異僅為已查證 guard 與兩項測試。

## 實際驗證

本地三組既有回歸，加上交易與 UI 新測試：78 tests、5 subtests 通過。417 個 mLua method/handler body 語法通過；continue 僅於離線語法檢查替換，不能代表行為。184 商品與 624 商品／港口定價、恢復、库存及超賣案例通過。

Maker refresh → Play → 原生執行 → logs → Stop 已實際完成：

- 同種連買兩次、再混裝第二種，總量三件、剩餘五格；滿艙拒絕且金額／件數不變。
- 選中第二種出售後，第一種兩件仍保留；FIFO 三件成本為 350。
- 正式編碼器原生 v2 混裝、空 [] 與 v1 遷移讀回通過。
- 真 Server → Client table RPC 保留十四件與兩批；較舊版本不能覆寫。
- 原生商會出售頁列兩種商品，選中第二種的數量限制為一件；船艙第二頁兩圖示、件數與混裝摘要通過。
- Client 投影備份後還原，沒有測試買賣 RPC 或測試 DataStorage 寫入；交易探針使用隔離 fake state/market。啟動時既有正常生命週期照常運作。
- 最後新 build 11:32:14：66 Info、0 Warning/Error；正常 logs 39 Info、0 Warning/Error。最後為 map01/edit。

首次原生 probe 直接對含空表物件 JSONEncode，碰到 LEA-3001 的測試探針錯誤；改用正式 EncodeProfile 建立 v1 測資後，遷移檢查通過。失敗與成功原始證據皆在本地保留，沒有把首次探針當成 PASS。[原生摘要](reviews/2026-10-08/cargo-mixed/maker-native-summary.json)。

## 界線與收尾

修正已實作且上述受影響檢查通過，任務記為 Review checkpoint。未測發布環境真斷線／重登混裝，未把隔離 probe 當成真人滑鼠買賣或跨 World instance 驗證。Save V1 八項原有 Review 狀態、bootstrap gate 前置及跨 instance CAS 待辦保持。

v2 存檔寫入後，舊的僅支援 v1 版本會拒絕讀取；發布／回退需保留能讀 v2 的版本，不能直接回退舊 schema。現有金錢、舊貨物與 CAS 基準不重置。

本輪沒有修改結構化 UI、美術或地圖。工作樹中使用者／Maker 另有既存修改，採逐檔提交，不將這些未審修改混入本次修正。

Retro：容量限制應以貨艙總件數與當下船況計算；允許續買時也必須一併處理成本批次、存檔格式、指定商品出售和客戶端完整投影，避免只移除拒買條件就覆寫舊貨物。
