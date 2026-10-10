# Daily Log

- Last organized: 2026-10-10

## 2026-08-14
- 完成 MissionCenter 0.3.1 契約遷移與歷史 Done 驗證債務正規化；未補造 Pass。

## 2026-10-03

- 12:37 卡片技術驗收完成，四項子任務進Review：29張圖鑑/20有效/9缺前置，30真RUID；商品商人卡店、買賣未裝庫存、返還/三槽、T1收費維修與百分比能力已接。最終Maker build60Info、normal69Info、0Error/0Warning；森林→天空cargo1/cap9、fire/speed/cargo、575G保留，航行3卡面可見但按鈕停用，抵港modalOpen=false。已stop/save。
- 修復實機航行卡面消失與CodeRabbit初輪5minor；focused新增測試路徑可攜性1major亦修，三支harness改用__file__/Path UTF-8-SIG，不依Temp MCP helper。從非專案cwd跑15組卡片、23項UI、12條空戰路線全PASS。兩輪外部原始NDJSON保留，未追加第三次或宣稱零issue；早期probe錯誤/真畫面失敗均保留。48項來源/PNG/證據/截圖以sha256封存。完整評論critic_full預算缺，未派代理、不記Done，M1仍進行。

- 11:58 改裝卡擴充驗收中：29張圖鑑／20張有效、9張前置鎖定；30張PNG均1024×1536 RGBA且sha唯一／四角透明，全部取得正式RUID。新增實體卡片庫存、商品商人入口、購買／出售／安裝／拆卸、T1付費維修、百分比再生與鍋爐及新空戰遭遇控制。
- 11:54 Maker本輪61Info/0Error/0Warning build，normal43Info/0Error/0Warning；真ButtonClickEvent→Client RPC已證明買fire×2/speed×1/cargo×1、真商品藥草×1、購買/切換森芽、同一庫存視窗火力→航速替換返還、連續三槽speed/fire/cargo及貨艙1/9。pending=-1且底層shipModal=false；空格Entity關閉。字級／入口遮擋仍在修，未把這版畫面當最終Pass。
- 初輪錯誤保留在upgrade-cards-before-fix-runtime.json：root測試probe用了不存在的sessions/PublishEconomySnapshot，已改實際GetOrCreateState/PublishSnapshot；這是probe錯誤，不能抹除或記成遊戲通過。另一實際pending缺陷與分頁殘圖已修並有新正向證據。Play測試資金1200僅temporaryfixture，未操作DataStorage。
- Python/Lua mock15組卡片檢查及強制遇敵12路線/延遲砲彈回歸通過；兩種測試均不冒充Maker12趟或真多人驗收。審查與PC最終視覺仍待完成，M1仍進行中。

- 10:27 船艙同頁新增目前船名、T1三槽卡片與貨物／有效容量；UIBuilder修復底板透底、字色對比及貨物圖示疊字。T0空貨艙、T1真商人購買切船配置、買入藥草×2與最終刷新受損T1／航行甲板查看通過。最新build42Info/0Error/0Warning，最終normal46Info/0Error/0Warning；已stop/save，測試fixture僅本次Play。證據cards-and-cargo-ui-runtime.json與cards-and-cargo-final-runtime.json。
- 重新完整讀取「三槽改裝設計」兩回合，Roadmap補12張性能／功能候選表及遭遇控制清單；正式配置仍為fire/speed/cargo，未把候選、卡片購買庫存或客運／接舷等前置系統宣稱完成。T1維持三通用。M1仍進行中。

- 09:12 後續驗收：重啟後 Maker 工具恢復。修正不存在的 UserComponent 為 PlayerComponent.UserId，真Client空戰快照與視覺可見。四港森林→天空→玩具城→納希→森林完整循環、E商人、跨港賣貨利潤31/32/20G及免費修船通過。原始MCP logs保存於 airbattle-four-port-runtime.json。
- 依主人砲彈提問，改為Server發射序列→0.6秒飛行→命中才扣血；保留原本同時攻擊玩家先結算，避免新增一輪傷害改壞T0路線平衡。最終Lua 12路線、唯一命中、延遲、沉船、離船及Client隔離通過，模擬最長91秒。
- 最新Maker build 41 Info／0 Error／0 Warning；首次跨檔刷新短暫讀到舊UI簽名，重新觸發State編譯後消失。最終runtime 0 Error／0 Warning；砲彈飛行截图及HP120→100時序、勝利續航、低血量沉船cargo=0回Sky、重結算拒絕、免費修滿100/20/40且金幣不變均有實機證據，見 airbattle-projectile-runtime.json。測試Timer自動清除，已stop/save。
- GV-AIRBATTLE從In Progress移至Review。M1仍在進行；五船港口／砲口對位、全世界圖箭頭、受損T1管理畫面、多語言與主人PC主觀視覺仍待驗。下方tools=[]與PendingMCP是較早歷史狀態，已由本次證據更新。
- 短自動空戰已接入 Server State/Data 與 Client 狀態／三個動畫 view。每段空域以百分比中點觸發，戰鬥凍結航程，勝利續航，沉船清貨回出發港。
- Lua mock：四檔語法、12 條有向航線逐段交戰／唯一抵港、沉船重結算拒絕／T0 免費修理、延遲傷害與致死補算、离船先取消、Client 玩家隔離與穩定結果文案通過。證據：evidence/2026-10-03/airbattle-static-qa.md。
- Maker 仍回 tools=[]；使用者確認已啟用／顯示已連線。唯讀診斷確認官方 stdio 入口及本地 bridge 存在，但不足以確認工具註冊；未知 owner 的背景程序保留。未宣稱新空戰 build/runtime 或四港實機回歸通過。
- M1 與 GV-AIRBATTLE 保持進行中；下一步是恢复 Maker 工具後 refresh/build/Play、空戰畫面與四港買賣驗收。


## 2026-10-04

- 10:18 GV-UI-ALIGN-20261004：五頁實機對齊與六項修復收斂完成，S3四席closure及正式Rust validator通過；煙霧測試與[成品圖集](evidence/2026-10-04/ui-alignment/completion.md)已保存，只將本Task由Review轉Done。既有中斷audit與完整M1狀態保留。Maker已stop。
- 17:29 GV-UI-RESKIN-20261004：style contract 更新至 13 張透明素材，連結離線 HUD preview、layout-spec 與 upload-after-restart 診斷；逐頁列明 5 頁 Close、4 個交易+/−、Dialog／MarketInsight 純色板及船體／護盾／裝甲 gauge 待換。主框與合格主要 CTA 保留，shared skins 不做整批覆蓋。13 張皆 generated-not-imported、RUID=null；root 重啟後兩次 world_info 顯示 Maker 未執行。PUT 403 回報 No AWSAccessKey was presented；長度相符，presign 有簽名參數，未找到截斷證據，原因調查 pending；任務維持 In Progress，無 Maker 驗收宣稱。
- 17:35 GV-UI-RESKIN-20261004：manifest 增至15張，新增 Shop Dialog 專用 `dialogWide` 與 MarketInsight 專用 `marketInfoPanel`；不可將 `creamPanel` 拉伸代替，`gaugeFrameV2` 生成中但未保存。離線 preview 與 layout-spec.json 已連結。S3 PUT 403診斷pending；重啟後Maker仍未重連、production未套用、asset critic未完整閉環；任務維持 In Progress，等待新對話 handoff。
- 17:37 GV-UI-RESKIN-20261004：root 建立 [handoff](../.builder-work/hud-redesign/handoff.md)；manifest 有 16 筆（15用途素材＋`gaugeFrameV2-v1.png` 重繪候選，未驗）。[critic-round1](../.builder-work/hud-redesign/critic-round1.md) 已記尚未修問題，尚不能宣稱無 P0/P1 或完成評論閉環。使用者暫停本輪並開新對話；交接回報新對話可連 map01 Edit，本輪未匯入／未套production／未原生驗收，任務保持 In Progress。

- 2026-10-04 19:04：GV-UI-RESKIN-20261004完成：16透明PNG已匯入回查，13種26Material／322nodes，四HUD與五頁元件翻新，貨艙4×3每頁12，保留原容量。R4十五張原生圖、R5正確參數定點回歸、Luna一對一最終確認無未解P0/P1/P2；Maker已stop。R4測試probe Error保留，R5 build60/normal24全Info。Rust已依序committed InProgress→Review→Done，current completion passport通過。來源與證據：evidence/2026-10-04/ui-reskin/completion.md；風格：design/ui-material-style.md。未驗Mobile／GUI實體滑鼠／交易持久化；184商品與M1各任務狀態保留。

- 2026-10-04 23:46｜GV-FEEDBACK-20261004：五項截圖回饋與四港商人server落下修復完成、本地受影響驗證通過；正式critic_full預算尚待回覆，狀態Review、未Done。正式發布UI擷取兩次逾時，沒有發布/填問卷/改公開地區。checkpoint見evidence/2026-10-04/screenshot-feedback/checkpoint.md。

## 2026-10-05

- 16:04｜網頁上架收尾：公開狀態、全發布地區、世界問卷9歲以上、繁中／英文名稱描述公告及YouTube社群已填與回查。類型／代表圖、30秒實錄與遊戲內報名仍待完成；Chrome圖片file chooser失敗，未宣稱上傳。保存[收尾證據](evidence/2026-10-05/publishing-closeout/closeout.md)。本輪無Maker執行／公開版本實玩驗證，遊戲Review狀態保留。

- 17:12｜使用者Maker再發布後回查：空賊王封面代表圖片成功、官方預設4圖已移除；世界最後發布17:10、問卷9歲以上。公開類型仍「-」、影片未登記且YouTube公開頻道無影片。已更新收尾紀錄及新公開頁證據；正式競賽提交尚未完成。

## 2026-10-07

- 17:29｜依主人授權完成全 16 遊戲腳本 CodeRabbit 隔離審查（含舊腳本、排除大型資料／產生檔），1 次／0 issues；358 body 語法及 624 商品／港口案例通過。README 更新四港、動態市場與保存範圍，.builder-work 排除；main 提交／上傳待最後 Git 檢查。Maker MCP tools=[]，本輪實機未驗，既有M1/Review/Blocked不前進。[紀錄](../docs/CodeRabbit-Review-20261007.md)。
- 17:33｜40 檔 checkpoint `7e1f806e430d3c3c778d151add35598a29711ea7` 已一般推送 origin/main；git ls-remote 與 GitHub connector 確認遠端同 SHA，工作目錄乾淨。收尾回執另以文件提交保存；全程無新專案分支／PR，Maker 與既有 M1 驗收仍未宣稱完成。


## 2026-10-08

- 10:39｜依主人授權直接保存main：CodeRabbit完整23檔（17現有mLua、2測試、3舊原型、1上下文）提出1 major／3 minor，四項確認根因後修正；單次聚焦複查0 issues，兩次review均exit0，未超每小時3次／每次150檔。大型資源／資料literal／產生檔先排除，未湊假檔。[可公開紀錄與原始回應](../docs/CodeRabbit-Review-20261008.md)。
- 10:39｜保存前驗證53 tests＋5 subtests、409 body syntax、184商品與624交易案例通過；Maker新build10:36:29共72 Info，normal39 Info，0 Warning／Error；隔離market缺省欄位與leave快取正向marker通過、無測試DataStorage寫入，已回map01/edit。Abandon revision本輪未做Native行為／未真斷線；有production-body回歸。S3來源保持凍結，Rabbit為其後delta；Save八筆Review及正式bootstrap／跨instance待辦維持。README與公開UI三張截圖同步保存，推送尚待Git收據。

- 10:44｜61檔checkpoint `f8ad28eaaf98610e0dbf52781b5f4a5183efcd2e` 已一般推送origin/main，push exit0；git ls-remote與GitHub connector讀main確認同SHA，工作樹乾淨。全程無新增遊戲分支／PR、無force push。此上傳回執另以文件提交保存，Save八筆Review與正式發布限制維持。[提交](https://github.com/Gale0418/MSW-Sky-Pirate/commit/f8ad28eaaf98610e0dbf52781b5f4a5183efcd2e)。
- 11:35｜GV-CARGO-CAPACITY-20261008：修正買一件後還有空位卻拒買；容量內同種續買／混裝、FIFO成本、指定商品出售、schema2兼容v1及原raw CAS已整合。78 tests＋5 subtests、417語法、184商品／624案例通過；Maker隔離買賣、JSON／v1遷移、真Client table RPC、商會選賣及船艙第二頁正向marker；新build66Info／normal39Info，0Warning/Error，還原投影後stop/map01 edit。Rabbit第三次rolling-hour review十一輸入檔、exit0，2minor中1重現修正、1反證排除；無額外重審。README／公開證據同步，狀態Review；發布真重登、bootstrap／跨instance仍待。[紀錄](../docs/Cargo-Mixed-Verification-20261008.md)。

- 13:35｜GV-SAVE-QA／GV-SAVE-LIFE：依正式服截圖與GitHub skill完成首次讀取NotFound 1000002、gate後重讀及建檔前取消修正；不清檔、不自動Set OPEN、不擴大Set/CAS ack。補setup持續提示／30秒polling、loading圖片／卡槽／船況與pager清理。90 tests／13 subtests、167 bodies通過；Maker refresh回not running，正式SERVER／DB未核驗。Rabbit三輪2 minor皆查證修正（setup polling／clone test assertion）、第二輪0 issues；第三輪後單一測試斷言已重跑90/13通過，未第4輪；維持Review。[診斷](../docs/Published-Save-Diagnosis-20261008.md)。

- 15:27｜GV-SAVE-QA／GV-SAVE-LIFE：已收到正式 13:43 missing/code0 與 15:06 uncertain/code0；補初讀 code0＋nil→setup、先前未知 claim 仍 uncertain/no-resend、失敗 phase／去識別化 valueKind。95 tests／24 subtests 通過，兩檔 CodeRabbit 0 issues／exit0（本時段一次）；README與診斷更新。13:51舊版 Maker Refresh/Play 讀既有 revision25與Maker-only OPEN有實際MCP；本次Maker未執行，新增程式native及正式首次保存重登仍待，Review不前進。無正式DB寫入／自動OPEN／counter bootstrap。[診斷與審查](../docs/Published-Save-Diagnosis-20261008.md)。

- 15:43｜GV-SAVE-QA／GV-SAVE-LIFE：Maker恢復，同世界map01/edit；15:38 Refresh成功、build66Info/0Warning/Error，15:41 server_main 五個假gate診斷案例全pass=true，runtime37Info/0Warning/Error，stop後build66Info，已回edit。正式15:37仍缺phase/valueKind，主人確認操作Maker發布；發布時點／版本未獨立核驗，已請從本次Refresh版再發布並重進。native補驗完成但正式首次建檔、DB維護仍未做，Review保留。[原生回執](../docs/reviews/2026-10-08/published-save/gate-150647/maker-1541-receipt.json)。

### 2026-10-08 15:55 — GV-SAVE-QA：教學版本辨識

- Timestamp：2026-10-08T15:55:00+08:00
- Change：右下新增淡金小字 `v2026.10.08.1`，登入紀錄共用 Onboarding.buildVersion；既有 15 個 UI entity 保持原值，新增 1 個 Modal 子節點。
- Reason：使用者希望直接辨認 Maker 發布的新版本，避免以等待時間推測正式服是否更新。
- Impact：Maker 原生 VRF initial/started 皆 pass=true，文字 fits=true、rightMargin=40/bottomMargin=28；遮罩關閉且控制恢復。build 66 Info/runtime 35 Info、0 Warning/Error，已 stop 回 edit。此證據不取代 SERVER SaveV1 的正式初始化驗收，GV-SAVE-QA 保留 Review。
- Review：隔離審查只送 Onboarding.mlua 與 Onboarding.ui 共 2 檔，CodeRabbit exit 0／review_completed／0 issues；首次 base branch 前置失敗經 --base main 修正，沒有重送其他大檔。任務中心 sync 已完成、doctor status=pass（既有 legacy completion passport 警告保留）。

### 2026-10-08 17:40 — GV-SAVE-QA：首次上線維護初始化

- Timestamp：2026-10-08T17:40:49+08:00
- Change：正式16:57新版已確認 gate 缺值，依主人「直接更新」授權啟用限定本世界／creator 的一次性維護 helper，版本 v2026.10.08.2；維護版封鎖普通載入／首建，僅 confirmed missing gate 可 Set OPEN 一次並精確回讀，既有值／未知結果不覆寫或重送。
- Reason：自訂 bootstrap 門沒有正式預置；Maker與正式 DataStorage 分開，重複發布不會補資料。
- Impact：114 tests／31 subtests 通過；Maker build68 Info、runtime44 Info、0Warning/Error，原生註冊、owner 比對、Maker 拒絕正式操作、維護隔離／CLIENT setup／版本、六個 production-body 假 storage 情境 positive pass，已 Stop。正式 ReleaseOnly 分頁、初始化寫入／保存重登尚未執行，維持 Review。公開維護授權不宣稱 Private 或跨 instance 鎖成立。
- Review：CodeRabbit 首輪只實際收到三個 tracked 檔、1 minor；script-mode 測試發現順序已查證修正，直接執行57 tests全部通過；第二輪已將兩個新檔納入 staging，五檔複查 complete／exit0／0 issues；本時段兩輪，未第三輪。
- Unfinished：使用者從已 Refresh Maker 發布維護版、重登取得 exact OPEN 回執後，停用維護 helper 並發布一般版，再驗正式交易／重登。
- Evidence：[去識別化 Maker 回執](../docs/reviews/2026-10-08/published-save/maintenance-1657/maker-receipt.json)、[正式服診斷與操作](../docs/Published-Save-Diagnosis-20261008.md)。


### 2026-10-08 18:18 — GV-SAVE-QA：單一正常版直接建檔

- Timestamp：2026-10-08T18:18:27+08:00
- Change：主人要求直接修、不要多版本；撤除 bootstrap gate 與維護載入鎖，helper僅空 Logic 相容 entry。v2026.10.08.3 只需發布正常版一次，不再要求 Maintenance／OPEN 回執。confirmed missing 才直建、遷移後重讀、exact Set 回讀才 ready；既有存檔 raw CAS 保留，未知首次 Set 在同 instance 快取內不重送。
- Reason：17:53 正式服仍同步中且完全無 Maintenance 訊息；前次維護流程增加登入阻塞，已撤下而非繼續要求初始化門。
- Impact：80 tests／10 subtests通過；Maker 66 build Info／42 runtime Info、0Warning/Error，隔離原生新key建檔／保存／清快取重讀、既有revision27、真 client 船艙10,600／1/8空位7／船體100/100皆 positive，已Stop。正式發布後交易保存重登仍待，保留Review；不宣稱缺鍵Set跨instance原子建立。
- Review：CodeRabbit本輪五檔單次review_completed／0 issues；本小時第三次，未追加重審，大素材／Native API／產生檔／無關UI排除。README、診斷與兩份存檔文件同步目前方案。
- Evidence：[審查与原生回執](../docs/reviews/2026-10-08/published-save/direct-first-create/review-summary.md)。


## 2026-10-10

- 15:30｜依主人授權準備直接保存／推送 main，不建立遊戲分支或 PR。README 更新 13 港／15 地圖、185 商品中 160 現役／25 退役，以及 21 億造船與材料規劃的實作界線。全量本地測試發現舊 LoadForPlayer fixture 未注入 RefreshOpenPorts，正在以 production 方法補驗。將把全部現有與較早的 mLua／Lua／Python 測試送 CodeRabbit；大型地圖、UI、圖片、Native API、產生檔及私有證據排除，不湊假 150 檔。實際審查結果及推送回執稍後補入，既有 Review／Blocked 與未發布驗收狀態維持。

- 15:56｜main 保存前驗證完成：CodeRabbit完整32檔提出1 Major issue，先production-body重現再修過期市場列／48KB換入前檢查；追到caller補MarkDirty結果、買賣同步失敗取消與單列復原。5檔差異連同關聯程式9檔複審0 issues，兩輪exit0／review_completed；本時段共2次，未湊假150檔。88 tests＋10 subtests、十三港UTF-8大小界線與diff check通過。修正後Maker正向prune／stock／拒絕不換帳號／MarkDirty false→true／cleanup，build73／runtime45全Info、0Warning/Error，已stop。README與[審查紀錄](../docs/CodeRabbit-Review-20261010.md)同步；正式重登與跨instance待驗、M1／Save既有狀態不前進。
