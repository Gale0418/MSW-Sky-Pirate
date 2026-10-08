<!-- Generated materialized view. Do not edit directly; rebuild from canonical MissionCenter files. -->
<!-- mission-center-derived schema=1.0 fingerprint-format=sha256-v2-lf source-fingerprint=56c5e8a66e19cb3ac609b93f08757939863e9facdad6968b4dcd83b7ae42072a -->
# Active Working Set

- Source of truth: `tasks.md`
- Unfinished working set count: 6

| ID | Title | Priority | Status | Next action | Depends on | Verification | Blocker reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GV-M1 | Great Voyage M1：港口資料、世界地圖 UI 與整合 QA | P0 | In Progress | 完成四港往返、交易與箭頭端點驗收，修正剩餘問題 | E8, GV-M1-P3 | 四港／甲板／交易／HUD、60 秒自動抵港及 Maker 視覺證據齊全；再由主人確認主觀視覺 |  |
| GV-SAVE-V1 | 完整帳號永久存檔 V1 | P0 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 |  | 對應子任務的存讀、故障與 Maker 證據 |  |
| GV-SAVE-DATA | 版本化帳號快照與市場遷移 | P0 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 |  | 金錢、貨物成本、五船船況、三槽及卡數守恆；壞檔／未來版本拒絕覆寫 |  |
| GV-SAVE-LIFE | 單一寫入者與登入離線保存 | P0 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 | GV-SAVE-DATA | 寫入失敗／延遲／快速重登不清掉未存更新；載入失敗不發初始資產 |  |
| GV-SAVE-FLOW | 交易、出航與沉船整合 | P0 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 | GV-SAVE-LIFE | 出發前失敗拒絕航行；航行離線回出發港；沉船清貨不得因重登復原 |  |
| GV-SAVE-QA | 存檔全流程與故障回歸 | P0 | Review | S3 limited：已知 10 項完成處置；補正式 bootstrap 閘門預置、跨 WorldInstance CAS 與實際斷線保存證據；參照 S3 ledger。 | GV-SAVE-FLOW | 同版 build/runtime、正面 VRF、守恆、成本與故障證據；未驗項明示 |  |

## Next Candidates

- E2 — 貿易貨物與價格結算
- P0-T4 — 建立交易貨物與素材規則
- Candidates only; promote to Ready in `tasks.md` before starting.
