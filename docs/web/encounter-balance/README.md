# 三難度遭遇檢閱工具

遭遇資料已接入遊戲邏輯；Maker Server 邏輯與 Client 跨端快照切片已驗證，完整航程與多怪 sprites 畫面仍待驗。空戰 HP／攻擊／間隔採用固定等級公式，賞金依物種等級級距固定，不受船級與貨值影響。

開啟 encounter-balance.html 可直接使用，不依賴 npm 套件或網路圖片。完整規格見 ../../GreatVoyage-Encounter-Balance-20261011.md。

執行 `node encounter-smoke.cjs` 可驗證分類、船級限制、抽樣與內嵌資料一致性。JSON 是來源；更新時必須同步 HTML 中的 balance-data。

可以測試 T0～T5、13 空域、船上貨物固定估值（現金不計入）、額外誘惑度與三個卡槽；抽樣可以重複同種。每個卡槽加算一次，同款可占多槽。顯示的機率與隻數不代表實機可存活性或戰鬥平衡驗收。

encounter-verification.json 保存離線測試結果；encounter-browser-verification.json 與 encounter-preview.png 保存前版 Chrome 檢閱頁驗證。

2026-10-11：132 種採用，129 種可抽、3 種待校準。巴達雷伊依主人指定，比照泡泡魚採自訂分級 Lv.28／低難度，維持全空域；原作等級仍未知；有效等級 28 固定為 120 HP／12 攻擊與 100 G 賞金。
