# 空戰砲擊、命中與受擊回饋

更新：2026-10-12。實作 checkpoint；本機回歸及 Maker 定點切片已核對，不代表全航程或正式服驗收。

## 現行行為

每隻怪以 UID 保留自己的實體與平滑飛行路徑。擊殺主目標不會把其他怪瞬移至它的位置；同屏外的怪仍按既有隊列加入。炮彈在離膛前鎖定原 UID 的預計身體中心，固定起點、終點和角度，0.6 秒直線飛行；途中不追蹤或轉向。原生動畫 frame 的尺寸、pivot 與 PPU 決定身體中心，載入失敗有有限重試。

Server 在每次發射依序判定命中、±10% 傷害浮動與爆擊，數值四捨五入為整數，抵達時才套用該次已決定的傷害。MISS 只有命中抽選，不再抽傷害或爆擊、不扣血、不領賞。Client 只讀同次快照的 UID、命中、傷害與爆擊結果；波次與炮擊資料共用單一 serial 快照，過期回應不會覆蓋新戰況。

| 配置 | 初版數值 |
| --- | --- |
| 一般怪基礎命中 | 92% |
| 靈活怪基礎命中 | 82% |
| 大型怪基礎命中 | 96% |
| 船級加成 | T0～T5 每級 +2 個百分點 |
| 穩定炮架 | 每張 +5 個百分點，實際命中最高 99% |
| 傷害浮動 | 基準 × 0.9～1.1 |
| 基礎爆擊 | 5%，傷害 ×1.5 |

靈活／大型分類採明確 packId 清單，未列者使用一般值，不按未知翻譯猜分類。T0 基準 20 傷害，普通命中 18～22；T5 基準 4,000，普通命中 3,600～4,400。爆擊與命中分開判定，未來戰鬥 profile 可設 100% 爆擊；卡片爆擊加成與 DIY 砲台配置介面尚未接入。

命中使用 MSW 原生 DamageSkin 顯示 Server 的整數傷害，爆擊傳入原生 critical 標記；MISS 使用原生 Miss 文字，依同 UID 的實際位置與官方動畫最高 frame 邊界放在頭頂上方；缺少 view 時沿用原 UID 飛行路徑。傷害字使用獨立錨點，怪物被擊倒後仍能播完，1.2 秒或離圖時回收，最多保留 16 個。MISS 炮彈從身體外側通過，不在怪身上播爆炸。

129 種啟用怪物各有同官方 pack 的 hit1，命中時只播放原 UID 自己的受擊表情約 0.3 秒，再還原主動畫；MISS 不播。致命目標保留到受擊表情結束後再回收。受擊資源逐 pack 證據見 [官方受擊素材表](reviews/monster-hit-clips-20261012.json)；126 筆經官方 batch API、3 筆經既有官方 pack 快取核對，沒有缺漏或借用其他物種的臉。

## 驗證

- 本機完整回歸：`python -m pytest Tests -q`，132 tests／21 subtests 通過。覆蓋多 UID 保持位置、不同砲口／frame rate 的固定直線、原目標切換、延遲／過期快照、防重、MISS、18～22 浮傷、0%／100% 爆擊、大小怪頭頂座標／實際 WorldPosition／同 UID fallback、原生 DamageSkin 參數、錨點回收、hit1 還原／死亡 TTL 與波次預載快取。Native 邊界使用 stub；[本機版本收據](reviews/projectile-targeting-local-20261012.json) 保留正式檔雜湊。
- 唯讀 Luna 覆核：命中／浮傷／爆擊、原生 DamageSkin 與新增 MISS 頭頂定位邏輯未發現具體問題；此為靜態覆核，不是原生畫面證據。
- Maker followup／supplement 切片已確認同 UID 直線端點、普通 105／爆擊 154 傷害與 HP 一致、強制 MISS 傷害 0／HP 不變／無賞金，原生 normal／critical／Miss 文字呼叫與 hit1 預載 2/2；活怪 0.4 秒後還原並繼續飛行，死怪與 1.2 秒傷害錨點回收。build 75 Info／0 Warning／Error；normal 累積 315 筆保留兩個已修測試 probe API 錯誤，並非零 Error 回合。短暫文字未成功截入圖，不能當作逐像素畫面驗收。新增頭頂 MISS 原生切片確認泡泡魚 topOffset=1.065／赤翼龍=2.445、實際 view 與 UID303 fallback 的 Y 誤差均小於 1e-7，原生 Miss anchor／DamageSkinComponent 有效，fixture／Timer／玩家與船狀態已還原；本輪 build 73 Info／normal 72 Info、0 Warning／Error。[Maker 原始收據](reviews/projectile-targeting-maker-20261012.json) 保留所有歷史診斷。

- 森林船砲口另以鎖定同一 forest RUID、截圖前後一致的投影核對：起點約 (518.7,416.3)，黑色砲口中心約 (522,419)，起點落在砲口內，保留現有 offset。此前不同時點投影與截圖造成約 32px 誤判，另一次還原後圖是 T0，均保留診斷；不是逐像素吻合或所有船種砲口驗收。本輪 build 73 Info／normal 66 Info、0 Warning／Error，已還原並 stop。

## 限制與後續

全航程、正式服重登、多人／跨 instance 與手機實機尚未驗；129 種資源對照不等於逐種原生畫面驗收。T2～T5 仍是戰力與修費資料，材料造船／NPC 及黑暗天堂等特殊 BOSS 未實作。DIY 砲台的高火力、高射速、高射程與狙擊配置記於 [Roadmap Backlog](GreatVoyage-Roadmap.md)，本次未新增完整製造／裝配玩法。
