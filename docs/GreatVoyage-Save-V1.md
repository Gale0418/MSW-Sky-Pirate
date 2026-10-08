# Great Voyage 永久存檔 V1

2026-10-08 主人核准草案後進入實作；任務狀態以 MissionCenter/tasks.md 為準。

最新 checkpoint：S3四席評論與Rust八筆驗證完成，outcome為limited，八筆任務保留Review。下文S3 pending屬凍結輸入當時紀錄；後續Git審查4項有效問題已修、複查0 issues，詳見[本輪紀錄](CodeRabbit-Review-20261008.md)。正式bootstrap預置、跨World instance與真斷線驗證仍待完成。

- ✅ E1：版本化帳號快照：金錢、貨物數量／成本、所有船況、使用中船、未裝卡與三槽、個人市場壓力／大巴商品補貨；遷移既有市場且不刪舊鍵。
- ✅ E2：載入完成閘門、單一寫入者、dirty generation、定時背景保存、出航前確認、抵港／沉船／UserLeaveEvent 保存。
- ✅ E3：損壞／未來版本／讀寫失敗、快速重登、卡數與貨艙守恆、本地測試及 Maker 真正存讀。
- ✅ 追加：船艙透明金額框與粗體金屬色數字，沿用即時金額來源。
- ✅ S3 Native UI checkpoint：袋沿用 `GoldCoinPouch_v2`；所有金額（含0）使用直立 `GoldMapleCoin_v1.png`，14個UI節點共用，SHA d75219c45cc5a122c3444197b2faa0fb0efccafe9af01ad7837b29ab649e419b、RUID eb464db009c04b028b6a97f5bcf68713；S3舊coin v2引用數量0。貨艙固定 HullWall_v1.png 背景（1448×1086 RGB，SHA `34f1c7dc3474c9bbb96da8deb05cf9b96381936ae03973ac77a128096e7bc24c`，RUID `05ed9097173b49be8dc6b7d012b25c79`），搭配透明 CargoRack_v7.png（1448×1086 RGBA，SHA `0cf91cf6acce60b63f4e6309f6afb7aa7544d621b3be83fa46191d54577b0f18`，RUID `34ee90ba1c3d45b88272eb5dbbbd83fc`，Allowed）。Interior 540×405 at (0,40)，Rack 520×390 at (0,-45)，grid 510×310 at (0,40)；12格四欄 x=-156/-52/52/156、三列 y=30/-54/-138，cell72×72，icon70×52 at (0,10)，label78×20 at (0,-26)。18格 UUID 保留，359 entities、lint 0 errors／46既有 warnings。正確 ID `commodity_forest_54` 的 client-only fixture Native 顯示12/12三層承托、無重疊，測後恢復2/8與10,000金。維修板手顯示370×64；港口 T0 production repair cost 0 成功，海上 disabled fixture inconclusive。詳見 [v7 Native 收據](../MissionCenter/evidence/2026-10-08/save-v1/native-ui-s3-v7.json)；獨立 S3 council review pending，正式生命週期維持 Review。

## 已核准語意

單一精簡 JSON 原子保存資產與個人市場，先量測最壞 UTF-8 體積與 Credit，再考慮拆分。航行中沿用出發前完整安全快照；斷線重登回出發港，不重播戰鬥或發獎。抵港與沉船結算更新快照；已結算沉船必須保留貨物損失。儲存失敗保留 dirty，載入失敗不能用初始資產覆寫。

## 驗收與界線

正常保存採 Async，不在每幀／傷害 tick 存 DB；離線採 AndWait。JSON 僅包含持久欄位，衍生船屬性按現有公式重算且不免費補血。避免過期回呼與不同 instance 舊寫入覆蓋；不能用 revision 數字冒充 compare-and-set。所有持久變更包含市場與金錢守恆。

保留既有 UI／地圖／戰鬥行為與 Environment/config。無 Maker 正面證據不得標實機通過；單一 Maker 無法證明真實跨 instance 競態。模擬專家觀點屬決策分析，與獨立審查證據分開。

v7 Native 截圖：12/12 貨艙 `maker_play_20261008_085509_379.png`、商會 `maker_play_20261008_085547_531.png`、還原船艙／維修 `maker_play_20261008_085634_940.png`。Normal 48 Info／0 Warning／0 Error；build 72 Info／0 Warning／0 Error 為08:06既有script build，並非此次UI變更的新build。錯誤商品ID探針已在收據標為rejected diagnostic。獨立 S3 council review、Published gate prerequisite仍pending；跨World instance race仍unknown。

以上代表實作與本地驗證；正式生命週期仍為 Review。[完整驗證與限制](Save-V1-Verification.md)。
