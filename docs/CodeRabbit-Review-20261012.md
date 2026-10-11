# 2026-10-12 CodeRabbit 與 main 保存驗證

本次保存人工分類的129種合法空戰怪、貨物價值引怪／混編遭遇與固定賞金、T0～T5戰力／維修資料、獨立飛行／原UID直線砲擊、溫和命中、浮動傷害／爆擊，以及原生傷害字／頭頂MISS和各物種受擊表情。直接提交main，不建立遊戲分支或PR；GitHub保存不等於發布MSW世界。

## 審查

- CodeRabbit CLI 0.7.6，已登入；完整審查39檔（19完整mLua、11測試、3舊Lua原型、4試算頁程式、README／上下文）。程式逐byte複製，沒有拆檔或假湊150；未改且2026-10-10已全量審過的236KB商品表、大型圖片／地圖／模型／UI序列化／Native API／產生檔與私人證據排除。
- 首輪exit0／review_completed，提出1 minor issue：test_encounter_data.py的Docs路徑與實際docs不符。先新增filesystem casing回歸，修前1 failed，再改小寫路徑；修後完整133 tests／21 subtests通過。
- 聚焦複審只有1個差異檔，Rabbit實際連同相關程式審查5檔，exit0／review_completed／0 issues。本輪總共2次，未追加第三次；較早遭遇切片審查已超過rolling-hour時窗。CLI更新提示僅屬外部狀態，本輪未修改工具安裝。
- 唯讀Luna盤點確認README沒有將高階船／材料造船NPC與Boss說成已上線；公開證據一個帳號識別值共42處已遮罩（36欄位與6訊息），原始副本保留ignored本機暫存；本機工具命令改可攜寫法，截圖標示local-only，不假稱圖片已公開。

## 驗證

完整Python回歸133 tests／21 subtests；node docs/web/encounter-balance/encounter-smoke.cjs的22,464條件／98,000抽樣通過。遊戲production在本次審查後未修改；前一輪Maker定點證據保留：頭頂MISS build73／normal72全Info，森林船同時投影校準build73／normal66全Info，均0Warning／Error，已stop並還原fixture／玩家／船。前輪probe錯誤保留，不能把累積log說成0Error。

## 證據

- [完整39檔輸入與SHA-256](reviews/2026-10-12/git-checkpoint/review-input-manifest.json)
- [完整原始回應](reviews/2026-10-12/git-checkpoint/rabbit-full.ndjson)、[查證與修正](reviews/2026-10-12/git-checkpoint/rabbit-dispositions.json)
- [複審差異SHA-256](reviews/2026-10-12/git-checkpoint/review-focused-manifest.json)、[複審原始回應](reviews/2026-10-12/git-checkpoint/rabbit-focused.ndjson)
- [去識別化範圍](reviews/2026-10-12/git-checkpoint/public-evidence-redaction.json)、[砲擊原生收據](reviews/projectile-targeting-maker-20261012.json)
- [空戰回饋規格](GreatVoyage-Projectile-Targeting-20261012.md)、[遭遇串接](GreatVoyage-Encounter-Runtime-20261012.md)

## 限制

現可購仍為既有免費T0與四款50,000G的T1；T2～T5材料造船、任務／造船NPC、掉落與黑暗天堂等特殊Boss尚未開。正式服重登、多人／跨instance、全航程、手機、129種逐一原生畫面仍待驗；本輪只有測試與文件修正，不冒稱重新跑Maker。既有M1／Save與其他任務生命週期保留。

## 上傳

README與MissionCenter已於提交前同步。189檔 checkpoint [`21fca7c`](https://github.com/Gale0418/MSW-Sky-Pirate/commit/21fca7c2da8da2247c055d2cac4156030a4af4c2) 已一般推送origin/main（exit0），git ls-remote與GitHub connector確認同SHA、當時工作目錄乾淨。無新遊戲分支／PR、無force push；[上傳回執](reviews/2026-10-12/git-checkpoint/push-receipt.json)另以文件提交保存。
