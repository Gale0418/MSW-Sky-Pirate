# 正式伺服器存檔載入診斷

2026-10-08。對應任務 GV-SAVE-QA／GV-SAVE-LIFE，維持 Review。

## 已觀察

使用者確認 12:58 截圖來自正式伺服器：金額為 —、三層船況 0/0、貨艙同步中、底部顯示連線暫時忙碌。附帶兩行 [CLIENT] merchant closed／ShipUI opened 是一般操作紀錄，不包含存檔失敗原因。這些 placeholder 表示尚未取得可用的伺服器資產投影，不能推論存檔已遺失或被清空。

## 存檔原因與安全修正

### GitHub skill 找到的先行問題

上游 [MSW-Git DataStorage skill](https://github.com/MSW-Git/msw-ai-coding-plugins-official/blob/96133b2991d71b66bbe1e2494d28e4cc4bf57f82/plugins/msw-maker-base-skill/skills/msw-scripting/references/datastorage.md#L440-L483) 明文 GetAndWait 的新 key 回 1000002 NotFound。舊 Store 的首讀與 gate 後重讀把所有非零 code 都判 retry，僅 code0＋nil 能走 first-create；因此正式新帳號可能在抵達 gate 前就被擋。這是已查證的程式／文件差異，仍沒有本次正式 DB code。已修正為只接受 confirmed NotFound＋nil，其他 error／throw 或 NotFound帶資料仍 fail-closed；精確 Set/CAS 回讀成功條件保持 code0。建檔前取消也接受 confirmed NotFound＋nil 以釋放自己的 gate；已嘗試 Set、未知回應與矛盾資料仍不可走此釋放。

本地相關技能與上游 96133b2991d71b66bbe1e2494d28e4cc4bf57f82（2026-10-06 23:06:27Z）內容一致，無需重裝。GVSaveV1Bootstrap 是專案自訂跨初始化 CAS 保護，不是 MSW 官方首次建檔前置。


LoadForPlayer 先讀 UserDataStorage(ProfileCode) 的 GVSaveV1_<ProfileCode>。既有非 nil profile 直接驗證／載入；只有不存在的 profile（成功讀取但 raw=nil，或已確認 NotFound＋nil）的首次建立路徑會 ClaimBootstrapGate。該閘門要求維護者預置 GlobalDataStorage GVSaveV1Bootstrap 的 gate 字串為 OPEN。確認 gate NotFound 會拒絕建檔；非零 API code 的舊處理把它歸為 retry，畫面因此只能顯示忙碌。既有驗證紀錄僅證明 Maker gate 已預置，正式環境預置一直未驗。確認 NotFound 處理後仍需核驗此路徑，但尚無該次正式 SERVER 日誌或 DB 讀取證據，故不能定案。

本輪將 missing gate 分類 setup，30 秒退避期間保留該狀態；UI 明示「存檔服務尚未初始化，請聯絡管理員；資產已保護。」真正重新載入或 ready 會清除舊 failure 狀態。busy／unknown claim／服務異常仍 retry；壞檔仍 blocked。新增 SERVER warning 的 state／code 與正確 storage 名稱，排除身份、token、raw 及 payload。未增加自動 Set OPEN，未重設或覆寫玩家資料。

## 正式環境核驗步驟

1. 確認此次正式世界的發布版本、World scope 與程式版本；Git push 不是 Maker Publish。先取得同次登入的 [SERVER] [SaveV1] warning，分辨 profile read code、missing gate 或 busy。
2. 在正式世界資料管理環境唯讀核對 GVSaveV1Bootstrap/gate；同時確認是否已有帳號 profile。Maker／正式環境不能以本地測試的 gate 結果互相代替。[官方 GlobalDataStorage 文件](https://maplestoryworlds-creators.nexon.com/en/apiReference/Misc/GlobalDataStorage)。
3. **只有確認缺 gate 且所有 World instances 已停止的維護窗口**，才由維護者一次預置 OPEN 並回讀核驗。既有 OPEN 不重寫；BUSY 或未知值不得直接改 OPEN，先排除延遲 claim／profile write。保留 profile、舊市場 shards 與版本紀錄。
4. 發布本輪明確診斷訊息；正式服新登入須取得 money／ship／cargo，交易後保存再重登確認。未完成前保留 Review。若已有 profile，缺 gate 不是充分解釋，改查 GetAndWait code、解碼／版本與綁定結果。

## 白色遮擋

Ship／Future 背景共用帳戶 RUID 3b8d213aa521408faa8af20d585e90d2，資源服務 metadata 成功，CDN 64px 縮圖實際呈現羊皮紙金框；只能排除縮圖本身是白色，尚未證明正式 texture 的載入或發布狀態。UIBuilder 比對背景節點與 HEAD 一致，另確認 RefreshShipPanel 在載入 early-return 前啟用 Preview 與內容面板，早退未清掉 placeholder。已在該分支隱藏預覽／三卡槽／船況填條，數值顯示 —，貨艙分頁關閉；ready 分支恢復。空 Sprite overlay 均 alpha0，沒有證據可把 account metadata not-found 當作公用素材失效。正式白板是否完全消失仍須復驗。

## 驗證

本輪 production-body 回歸指令：

```text
C:/Users/USER/miniconda3/python.exe -X utf8 -m pytest Tests/test_save_v1_lua.py Tests/test_cargo_ui.py Tests/test_cargo_transactions.py Tests/test_transaction_feedback.py Tests/test_git_review_regressions.py -q
```

結果 **90 passed、13 subtests passed**；涵蓋 missing setup、cooldown 保留且不讀寫 profile、測試閘門開放後恢復 ready、busy／crashed owner fail-closed、既有 profile 略過 gate、QA prefix 日誌符合上游 1000002 契約的首次建檔與 gate 後重讀、矛盾回應不寫、四狀態 UI 訊息、29/30秒重試與 ready→loading→ready 控制恢復。兩個受影響 mLua 檔 167 production method bodies Lua 語法通過；不涵蓋 native mLua annotation 或平台 build。git diff --check 通過。

Maker refresh_workspace 實際回報 Maker is not running，故本輪沒有 native build／Play 或正式伺服器修復宣稱。CodeRabbit 第一輪四檔增量提出 1 minor（setup 自動 polling 遺漏），查證修正；第二輪包含 NotFound／載入 UI 修正的複查 0 issues；第三輪針對取消建檔的兩檔增量提出 1 minor（測試斷言誤查原 store），查證修正並重跑通過；三輪均 complete／exit0，未執行第四輪。不沿用先前審查作本輪結果。正式 SERVER 訊息與 DB 唯讀核驗仍待取得。

本地紅／綠證據：首次初始化與缺閘門兩個正向案例在舊 Store 失敗，修正後通過；建檔前取消的 NotFound 正向案例亦先失敗後通過。NotFound 帶 raw 的 retry/no-write 是原有安全守則，初測一度期待 blocked，已更正，不列為生產缺陷。完整回歸、紅綠紀錄與逐輪來源見 [審查摘要](reviews/2026-10-08/published-save/review-summary.md)。
