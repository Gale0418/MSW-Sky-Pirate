# 2026-10-10 CodeRabbit 與 main 保存驗證

## 摘要

依使用者授權保存十三港、航圖、靠泊與登船範圍、貨物整理、造船材料／21 億價格設計，以及本次查證修正，直接提交並推送 origin/main。未建立遊戲分支或 PR；GitHub 保存不等於發布 MSW 世界。

## 已完成

- 完整審查實際 32 檔：19 個完整 mLua、3 個較早 Lua 原型、6 個 Python 測試、README、材料規格、金錢盤點與審查上下文。185 商品 literal 原樣送審；大型圖像、地圖／模型／UI 的序列化資料、Native API、產生檔、快取及私有證據排除，沒有拆檔或假湊 150 檔。
- CodeRabbit CLI 0.7.6，兩次 review 均 exit 0／review_completed；完整審查提出 **1 Major issue**，修正差異為 5 檔，複審回報連同關聯程式 **9 檔、0 issues**。本輪共 2 次，保留每小時第 3 次額度。
- 確認市場列累積可能超過存檔限制：先以 production-body 回歸重現過期列未清與超限仍修改帳號，再清理已恢復壓力／過期 BOSS 庫存，保留有效行情與當期已購數。先驗證原輸入，使用行情既有 UTC 時鐘與政策，future at 保持原語意。
- 換入帳號前由正式 EncodeProfile 檢查 **48,000 UTF-8 bytes**；拒絕時 profile、revision、generation、dirty 不變。十三港大小測試以每港 40 列確認可編碼、每港 100 列確認超限返回 nil。
- 主代理核對 caller 後追加修正：MarkDirty 回傳是否接受；BOSS 買入／出售先同步行情，失敗復原該商品列並取消，不扣款、增款、改貨物或送成功回饋。兩個 production-body 回歸先重現錯扣款／錯入帳，再確認修復。
- 舊測試 fixture 補入實際 RefreshOpenPorts／IsLegacyPort，驗四港擴成十三港、缺原四港仍拒絕、原 raw CAS 保留。最新全套 **88 tests＋10 subtests** 通過；git diff --check 通過。

## 驗證

| 範圍 | 實際結果 | 證據 |
| --- | --- | --- |
| 港口／目錄 Maker checkpoint | 13 登船點可近拒遠、11 商人路徑、185 全表／160 現役、無退役品上架、FIFO 成本 6000；build 71／runtime 56，0 Warning／Error | [唯讀原生回執](reviews/2026-10-10/git-checkpoint/maker-receipt.json) |
| 修正後 Maker | 已清兩個過期列、保留兩個有效列／BOSS bought=2；大小拒絕不改帳號，MarkDirty false→true 與 fixture cleanup 正向；build 73／runtime 45，0 Warning／Error，已 stop | [修正後回執](reviews/2026-10-10/git-checkpoint/maker-post-review-receipt.json) |
| CodeRabbit | 完整 32 檔 1 issue 已修；複審實際 9 檔 0 issues | [完整原始回應](reviews/2026-10-10/git-checkpoint/rabbit-full.ndjson)、[複審原始回應](reviews/2026-10-10/git-checkpoint/rabbit-focused.ndjson) |
| 輸入一致性 | 完整與聚焦清單保存 bytes／SHA-256；複審 9 個原始程式與專案逐 byte 相同 | [完整清單](reviews/2026-10-10/git-checkpoint/review-input-manifest.json)、[複審清單](reviews/2026-10-10/git-checkpoint/review-focused-manifest.json) |

## 未完成與限制

水世界與埃德爾斯坦交易商人仍待配置。T2–T5、造船／任務 NPC、新價格、賞金、掉落與遭遇曲線仍是候選規格，沒有把草案宣稱為 production。Save V1／M1 的既有任務狀態保留；正式重登、跨 instance CAS、真斷線與實體鼠鍵驗收未由本輪取代。

原生修正探針使用一次性記憶體帳號，測大小拒絕時暫設 1-byte 上限並立即復原；實際 48,000-byte 邊界由 Python／Lua 測試覆蓋。探針沒有 DataStorage 寫入，正常遊戲啟動仍會載入 Maker 帳號。買賣取消有 production-body 回歸，本輪未以實體鼠鍵重走。CLI 回傳版本更新提示僅作狀態資料，本輪沒有修改工具安裝。

## 回顧

審查涵蓋舊程式且保留真實商品資料，才看見擴港與存檔體積的相互影響。修正新拒絕條件時必須追到交易 caller，不能只讓中央方法回傳 false。

## 上傳回執

README、MissionCenter 與本紀錄於提交前更新。遠端 commit 與 main 同步結果以後續 GitHub／git ls-remote 回查為準；不以本文件預先宣稱推送完成。
