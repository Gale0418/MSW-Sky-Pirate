# 2026-10-08 CodeRabbit 與 main 保存紀錄

本次依主人授權保存 Save V1、船艙貨架／金額、維修介面與成交／購船回饋，直接提交到 main。Git 保存是可恢復的開發 checkpoint；Save V1 與八筆相關任務仍為 Review，並未發布新的 Maker 世界版本。

## 外部審查範圍

CodeRabbit CLI 0.7.6，已登入的本機 WSL Ubuntu CLI；使用獨立 review repo 的 main 作比較基準，不在遊戲 repo 建分支或 PR。本時段僅使用兩次 review，低於每小時三次、每次150檔的限制。

第一輪完整讀取 17 個現有遊戲 mLua 腳本、2 份 production-body 測試、3 份較早 Scripts 原型，再加1份上下文，共 **23檔**。除 CommodityCatalog 的215,411 bytes靜態184筆 literal以明示的空 review-only placeholder取代，其餘來源逐 byte匯出；該檔四個方法、索引與選貨邏輯完整保留。完整遊戲仍使用原始資料，沒有把 placeholder回寫。沒有足夠150份有價值來源，不切割或重複檔案湊額度。

排除二進位PNG、大型靜態資料、原生API、UI／model JSON、產生的codeblock、工具快取、帳號設定及私人runtime evidence。排除僅表示不適合語義審查，仍由各自的資源／builder／Native證據驗證。Legacy Scripts未自動掛入Maker。

指令：

```text
coderabbit review --agent --base main --uncommitted -c review-context.md
```

兩輪皆正常完成，exit 0；第一輪 **4 issues（1 major、3 minor）**，修正後複查 **0 issues**。複查輸入為3份修正來源、既有存檔測試及上下文的差異；CLI實際回報10個reviewedFiles（包括鄰近上下文來源）。新建test_git_review_regressions.py當時仍untracked，未列在複查名單；它已納入下述本機測試。CLI自動更新提示不是審查失敗，沒有據此擴大本次工具更新範圍。

原始事件與來源雜湊：[完整審查](reviews/2026-10-08/coderabbit-full.ndjson)、[修正複查](reviews/2026-10-08/coderabbit-focused.ndjson)、[第一輪輸入](reviews/2026-10-08/full-input-manifest.json)、[修正來源](reviews/2026-10-08/fix-source-manifest.json)。manifest記錄原始工作檔byte hash；Git可能按既有設定正規化CRLF。

## 查證與處置

| 嚴重度 | 來源／問題 | 實際修正與證據 |
| --- | --- | --- |
| Major | ProfileStore SyncMarket：只有cycle／bought的補貨紀錄缺pressure／at，schema驗證拒收 | 僅缺省nil時補0，保留錯值拒絕、cycle／bought規則；修正前SyncMarket=false，修正後production-body及Native隔離帳號通過 |
| Minor | ProfileStore離場：ready快取阻止同UID重登入再次收到載入狀態 | 在既有active-session guard內清除；修正前快取殘留ready，修正後重登入通知通過；另測Flush期間新同profile session的loading／ready不被清除 |
| Minor | AbandonVoyage：重建state令cardInventoryRevision歸零，client拒收過舊卡牌快照 | 與船況／經濟一致保留max revision；修正前42變0，修正後保留42，既有50仍保留50；disconnect仍不重建 |
| Minor | Legacy PriceFluctuation：>2000先命中，>4000倍率0.5永遠不可達 | 先判>4000，再判>2000；5000從80修為50，3000／4000仍80，2000仍100 |

四項皆確認根因後最小修改，沒有照審查文字盲目改架構。

## 驗證

```text
python -B -X utf8 -m pytest Tests/test_save_v1_lua.py Tests/test_transaction_feedback.py Tests/test_git_review_regressions.py -q -p no:cacheprovider
```

需pytest、pytest-subtests與lupa。實際 **53 passed、5 subtests passed（0.48s）**。另409個mLua方法／handler body語法檢查、17個codeblock配對、184筆catalog與624個商品／港口成交／恢復／超賣案例通過；body編譯只為syntax將continue適配成break，並不把該轉換當行為測試。

Maker實際stop／clear normal logs／refresh／play／server_main probe／logs／stop。10:36:29的新build為72 Info、0 Warning／Error；本次normal39 Info、0 Warning／Error。正向marker證明SyncMarket僅補貨紀錄與HandleUserLeaveEvent清快取在production方法執行；fake帳號storage=nil，離場前dirty=false、FlushAndWait早退，沒有測試DataStorage寫入。最後map01／edit。可攜摘要見[Native紀錄](reviews/2026-10-08/maker-native-summary.json)，完整原始MCP回應保留本機MissionCenter/evidence/2026-10-08/git-review/。

本輪未對真玩家執行AbandonVoyage（會移圖並發快照）；該修正有本機回歸與Native編譯證據，沒有新增Native行為PASS。也未做真斷線重登入、跨World instance CAS、Native timeout或發布環境bootstrap gate預置。既有S3四席結果為limited，凍結快照保持不動；這次Rabbit修正是其後的新source delta，不宣稱已被S3快照覆蓋。

UI公開截圖見[Save V1驗證](Save-V1-Verification.md)，README與MissionCenter已更新。推送收據會在實際origin/main確認後追加。
