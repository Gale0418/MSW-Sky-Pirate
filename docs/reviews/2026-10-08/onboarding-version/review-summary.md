# 新手教學版本號審查

- 範圍：2 檔；Onboarding 程式與 UI。大型美術／音效與其他檔案未送出；隔離 review repo 以 main 的 HEAD 作 baseline。
- CodeRabbit CLI 0.7.6、GitHub 驗證成功；review --agent -t uncommitted --base main -c .review-context.md。
- 已完成 exit 0，review_completed／findings=0，兩檔均列於 reviewedFiles。CodeRabbit raised 0 issues.
- 首次本地前置失敗：隔離 repo 無法自動辨識 base branch；未開始遠端審查，補上 --base main 後成功。
- 本滾動小時連同之前 SaveV1 的 2 檔審查，共 2 輪已完成（另 1 次 base branch 前置失敗）；各輪均未超過 150 檔。
- Native UI 證據見 maker-receipt.json；正式發布／存檔 gate 仍待驗證。
