# 正式伺服器存檔載入診斷

2026-10-08。對應任務 GV-SAVE-QA／GV-SAVE-LIFE，維持 Review。

## 目前修正：單一正常遊戲版直接建檔

17:53 使用者仍卡同步中，且完全沒有 Maintenance 訊息；使用者要求撤除多版本維護流程，直接修復目前首次上線。已移除自訂全世界 gate、claim/release 及普通載入的維護鎖。舊 helper 僅保留空 Logic 宣告供 Maker 既有 entry 相容，不執行任何維護、計時或 storage 操作。

LoadForPlayer 使用 UserDataStorage(ProfileCode)：既有資料嚴格解碼／載入；首讀 confirmed missing（code0+nil 或 NotFound1000002+nil）才遷移舊市場、建立並驗證預設資料。送 Set 前再讀一次，若已有 profile 改為載入且不覆寫；仍 confirmed missing 才送一次 Set，必須精確回讀相同 payload 才 ready。讀取錯誤／矛盾資料不建檔；Set 結果未知在同 instance 帳號快取內不重送，晚到 exact payload 可恢復。後續保存仍用原始 raw CAS。這是直接初始化，沒有宣稱 missing-key Set 為跨 instance 原子 create-if-absent。

Maker 實際 Refresh／Play：66 build Info、42 runtime Info，均 0 Warning／Error。QA prefix 的新 key 建檔 firstCreate=true、實際保存 saved=true、清快取後重讀 reloaded=true；既有正常 profile revision27 載入；真 client 船艙 shipPanelReady=true、金額10,600、貨艙1/8、空位7、船體100/100，版本 v2026.10.08.3。已 Stop 回 edit。[去識別化原生回執](reviews/2026-10-08/published-save/direct-first-create/maker-receipt.json)。

**發布步驟只剩一份正常版：**從已 Refresh 的 Maker 按發布／更新世界一次，完成後回大廳重登；購買商品、等背景保存再重登確認金額與貨物。正式環境尚未由工具發布或驗證，保留 Review。下方 gate／Maintenance 初始化步驟皆為已撤下方案的歷史紀錄，不適用目前版本。

## 歷史診斷紀錄（目前方案已取代）

## 已觀察

使用者確認 12:58 截圖來自正式伺服器：金額為 —、三層船況 0/0、貨艙同步中、底部顯示連線暫時忙碌。附帶兩行 [CLIENT] merchant closed／ShipUI opened 是一般操作紀錄，不包含存檔失敗原因。這些 placeholder 表示尚未取得可用的伺服器資產投影，不能推論存檔已遺失或被清空。

## 存檔原因與安全修正

### GitHub skill 找到的先行問題

上游 [MSW-Git DataStorage skill](https://github.com/MSW-Git/msw-ai-coding-plugins-official/blob/96133b2991d71b66bbe1e2494d28e4cc4bf57f82/plugins/msw-maker-base-skill/skills/msw-scripting/references/datastorage.md#L440-L483) 明文 GetAndWait 的新 key 回 1000002 NotFound。舊 Store 的首讀與 gate 後重讀把所有非零 code 都判 retry，僅 code0＋nil 能走 first-create；因此正式新帳號可能在抵達 gate 前就被擋。這是已查證的程式／文件差異；後續正式 SERVER 日誌見下方時間序列。已修正為只接受 confirmed NotFound＋nil，其他 error／throw 或 NotFound帶資料仍 fail-closed；精確 Set/CAS 回讀成功條件保持 code0。建檔前取消也接受 confirmed NotFound＋nil 以釋放自己的 gate；已嘗試 Set、未知回應與矛盾資料仍不可走此釋放。

本地相關技能與上游 96133b2991d71b66bbe1e2494d28e4cc4bf57f82（2026-10-06 23:06:27Z）內容一致，無需重裝。GVSaveV1Bootstrap 是專案自訂跨初始化 CAS 保護，不是 MSW 官方首次建檔前置。


LoadForPlayer 先讀 UserDataStorage(ProfileCode) 的 GVSaveV1_<ProfileCode>。既有非 nil profile 直接驗證／載入；只有不存在的 profile（成功讀取但 raw=nil，或已確認 NotFound＋nil）的首次建立路徑會 ClaimBootstrapGate。該閘門要求維護者預置 GlobalDataStorage GVSaveV1Bootstrap 的 gate 字串為 OPEN。確認 gate NotFound 會拒絕建檔；非零 API code 的舊處理把它歸為 retry，畫面因此只能顯示忙碌。既有驗證紀錄僅證明 Maker gate 已預置，正式環境預置一直未驗。確認 NotFound 處理後仍需核驗此路徑，後續已收到正式 SERVER 日誌；目前仍缺獨立 DB 唯讀與初始化證據，不能宣稱已修復正式服。

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


## 13:43／13:51／15:06 後續證據

- **13:43 正式服（使用者提供）**：`GVSaveV1Bootstrap gate 未預置; state=missing code=0`。代表當時程式走到專案首次建檔 gate 保護分支，玩家沒有拿到初始資產；不是一般 ShipUI opened 造成。尚未獨立核對該 instance 的發布版本。
- **13:51–13:53 Maker（實際 MCP）**：Refresh 成功、build 66 Info／0 Warning／0 Error；Play 載入既有 profile revision=25，伺服器探針確認 prefix=GVSaveV1、notFoundCode=1000002、gateKey=gate，Maker-only gate code0／OPEN；已 Stop 回編輯。這是前一版 `6809717` 的 Maker 證據，不涵蓋下面新增程式，也不能代替正式 DB。未公開 ProfileCode／token／payload。
- **15:06 正式服（使用者提供）**：`bootstrap gate claim failed state=uncertain code=0`。`code=0` 本身只表示最後一次 API 回應成功；既可能是初次 read 成功但 nil，也可能是未知 CAS 後 reconcile 成功但沒有看見 owner。原訊息沒有 phase/valueKind，不能只憑這一行判定已搶鎖、保存成功或資料遺失。

本次小修把**尚未嘗試 claim 的 code0＋nil** 歸入 missing/setup，保持原有 30 秒退避且不寫 gate/profile；**已嘗試但未確認的 claim** 保持 uncertain/retry，包括後續 code0＋nil。每個失敗訊息新增 `phase=token/handle/read/prior-claim/cas/reconcile` 與白名單 `valueKind=nil/empty/open/owner/busy/other`，不輸出原始值。精確 code0＋owner 的持鎖確認、profile Set 與原始 raw CAS 成功條件保留。

新訊息的判讀方式：

| 新版日誌 | 處置 |
|---|---|
| `state=missing code=0 phase=read valueKind=nil` | 初次讀取沒有 gate 值，維持 setup；核對正式 storage 與安全維護初始化。 |
| `state=uncertain ... phase=prior-claim` | 前次 claim 尚未確認，不重送；核對 gate 與延遲請求。 |
| `state=uncertain ... phase=reconcile` | CAS 後未確認 owner，最後 read code0 不等於 CAS 成功；維持 no-write。 |
| `valueKind=busy/empty/other` | 不能改寫為 OPEN；先查維護與既有 writer。 |

已對照上游 skill，沒有可直接安全補上首次「不存在 key 的 create-if-absent」方案。Sortable Increase 雖有官方計數用途說明，但本專案已有併發 IncreaseAsync 回傳重複 1 的隔離反例；不能據此假定跨 instance 唯一 owner，因此未引入計數器自動初始化，也未自動 Set OPEN。維護方案仍要求唯一操作者、其他 instances 停止、延遲中的舊 claim/write 已排除，且 code0＋nil 的正式缺值語義已核對；任何未知 Set 結果不可直接重送。正式維護執行入口目前尚未驗證可用，沒有執行正式 DB 寫入。

同一組回歸測試更新為 **95 passed／24 subtests passed**。新增初讀 code0＋nil、prior-claim＋nil、未知 CAS 後 reconcile 的三組目標案例先在舊碼失敗，再於修正後通過；另驗 token/handle throw、分類白名單與日誌不洩漏 token/raw。CodeRabbit 本輪只送兩個小檔案，0 issues／complete／exit0；資產與 Native API 排除。原始回應與來源雜湊見 [15:06 診斷審查](reviews/2026-10-08/published-save/gate-150647/review-summary.md)。

本次 Maker MCP 回報 `Maker is not running`；已請使用者開啟 Maker，尚未收到恢復回覆。新增變更的 Refresh／native build／Play 與正式服首次保存／重登均仍待驗，任務維持 Review。Git commit/push 不會自動更新 Maker 發布版本。


## 15:38–15:43 Maker 恢復與發布版本核對

使用者補充 15:37:59 正式服仍是舊 `uncertain code=0`，沒有新版 phase/valueKind，並確認操作的是 Maker「發布／更新世界」。本地 HEAD 為 f04727a；該版失敗 warning 已在第 660 行帶兩個欄位。正式日誌缺欄位支持「該次登入未執行新版分支」的推論，尚不能分辨發布前尚未 Refresh、不同發布來源或舊 instance。

15:38 MCP 確認同一世界 map01/edit，Stop／Clear／Refresh 成功；build 66 Info、0 Warning／Error，normal 空。15:41 server_main 執行五個假 gate 隔離案例：初讀 code0＋nil、初讀 NotFound＋nil、prior-claim＋nil、未知 CAS 後 reconcile nil／other，全數 positive pass=true；初讀 missing 不 CAS，prior-claim 不重送，reconcile 仍 uncertain。Maker startup 正常讀到既有 revision25；此資料不代表正式存檔。runtime 37 Info、0 Warning／Error；Stop 後 build 仍 66 Info，已回 map01/edit。詳見 [去識別化原生回執](reviews/2026-10-08/published-save/gate-150647/maker-1541-receipt.json)。

本次完成的是 f04727a 的 native 編譯／隔離診斷驗證，尚未發布或寫正式 DB。已告知使用者從這份 Refresh 後的 Maker 再發布，等待右下完成通知，再退出世界至大廳重進，以新版 phase/valueKind 判斷實際版本。[官方 Release World](https://maplestoryworlds-creators.nexon.com/ko/docs?postId=1321) 的官方搜尋索引說明發布時間依世界容量而異；沒有採用固定等待分鐘數。正式 bootstrap 初始化、首次保存／重登、跨 instance CAS 與實際斷線仍維持待驗。

## 15:54：登入教學顯示版本

依使用者要求，在新手教學 Modal 下新增 VersionLabel；右下錨點、距右 40／底 28 UI px、22 px 淡金字、不接收 Raycast。既有 15 個 UI entity 經 builder 比對未變，版本由 Onboarding.buildVersion 單一來源提供，值為 `v2026.10.08.1`，CLIENT 登入紀錄同步印出。原生 probe 正面證據確認文字完整、正確顯示與 RequestStart 後隱藏／控制恢復；build 66 Info、runtime 35 Info，均 0 Warning/Error。已 stop 回 edit；回執見 [onboarding-version/maker-receipt.json](reviews/2026-10-08/onboarding-version/maker-receipt.json)。

重新發布完成後，離開世界回大廳再登入，先看教學右下角與 CLIENT build 紀錄；它只識別客戶端教學程式，不單獨證明 SaveV1 的伺服器程式或正式 gate 已更新。正式首次建檔仍維持 Review，需接續唯讀 gate 核對與有維護窗口的安全初始化。


## 16:57：新版正式服確認缺少 bootstrap gate

使用者看到教學版本號，且同次 SERVER warning 為 `state=missing code=0 phase=read valueKind=nil`（Store:698）。因此本次已確認正式伺服器執行新版診斷分支；後續不再以發布延遲解釋這次失敗。它代表首次建檔前讀到自訂 gate 缺值，尚未發放初始資產，也不表示既有 profile 被清空。

使用者確認世界公開、認為尚無其他玩家，接著明確要求「直接更新」。依這份初次上線授權，已啟用固定維護版 `GreatVoyageSaveMaintenance`，限定 Maker 世界資訊與實際 PlayerComponent 核對一致的創作者帳號。這不是 Private 已確認的宣稱，不再把改私人當作使用者批准前置。

維護版封鎖所有普通 Store 載入／首建，指定創作者進入後核對 Environment.IsPublishedPlay、WorldId、本地單人、完整 instance 分頁只有本 instance、Store 無既有 writer。只對 code0／NotFound 加 nil 的 gate 缺值，送出最多一次 Set OPEN，再精確回讀；既有 OPEN 不寫、BUSY／空字串／其他值／錯誤拒寫。每次原生等待後重查本地狀態；分頁失敗與原生例外停止，Set 例外僅允許一次回讀，結果未知不重送。helper 沒有 Client RPC，沒有 UserDataStorage 呼叫，日誌不輸出 UserId／ProfileCode／gate token。

[WorldInstanceService](https://maplestoryworlds-creators.nexon.com/en/apiReference/Services/WorldInstanceService) 的 ReleaseOnly 清單是快照，不是鎖；因此這是一份只用於目前初次上線的固定維護版，不應留作日後一般登入自動初始化器。任何其他 instance 都拒絕寫入；發布前退出舊遊戲連線，維護回執成功後立即撤下 helper 並發布一般版。公開世界與舊 instance／延遲請求的風險沒有被描述成已消除。Chrome 官方操作本次逾時，Maker MCP 只能操作 Maker，本次未點擊正式發布或寫正式 DB。

### 本輪驗證

- 回歸指令增加 `Tests/test_save_maintenance_lua.py`，共 **114 passed／31 subtests passed**。包含正式方法內容、native Environment／UserEntities.Values mock、完整分頁、第二頁／分頁失敗、owner 離開／新玩家進入、重入、既有 writer、錯世界／帳號、Get／Set／回讀例外及 BUSY token 不洩漏。
- Maker 實際 Stop／Clear／Refresh／Play／logs／Stop：build 68 Info、runtime 44 Info、0 Warning／Error。原生註冊與 Maker 不初始化、creator ID 比對、普通載入不建立帳號、CLIENT setup 與 `v2026.10.08.2` label 正向證據通過；六個 production-body 假 storage 案例 pass=true。這些案例沒有存取正式 DataStorage，也沒有執行正式 ReleaseOnly instance 清單。詳見 [Maker 回執](reviews/2026-10-08/published-save/maintenance-1657/maker-receipt.json)。
- 首輪驗收探針誤用無效測試 UserId 與不存在的 GetPlayerLoadStatus，導致兩個探針 Error；改為有效登入 UserId／既有 clientLoadStatus 後重新完成清空日誌的完整 cycle，最終 0 Error。未把前一輪錯誤隱藏成生產通過。

- CodeRabbit 首輪實際只有三檔、1 minor（script-mode discovery），查證修正後直接執行 57 tests 通過；納入兩個新檔後的五檔複查完成／exit0／0 issues。兩輪都已完成，未第3輪；詳見 [本輪審查](reviews/2026-10-08/published-save/maintenance-1657/review-summary.md)。

### 正式執行

1. 從本次 Refresh 的 Maker 發布／更新世界，完成後退出所有舊連線，再進入新 `v2026.10.08.2`。此版為維護用途，船艙／商會暫時不發放資產。
2. 取得 SERVER `[VRF][SaveV1][Maintenance] gate OPEN confirmed by exact readback`（或 gate already OPEN）。只有這兩種是可以撤下維護版的確認回執。其他 refused／indeterminate 要先查原因，不重登或重發初始化來猜測成功。
3. 收到回執後，把 helper 的 enabled 與 initialRolloutAuthorized 停用，遞增版本、Refresh／驗證並再發布一般版；最後買賣、等待保存、重登核對金錢／貨物／船況。未完成這一步前 GV-SAVE-QA 維持 Review，不能宣稱正式存檔已修復。
