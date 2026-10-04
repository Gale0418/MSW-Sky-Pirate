# Great Voyage UI 素材風格契約

## 目的與範圍

以一套可替換、可追溯的透明 2D 素材，統一 Great Voyage 中仍顯得陽春或使用 generic 裝飾的 UI。涵蓋 HUD 的地點名稱、提示、船艙與互動提示，以及商店、地圖、船舶、改裝／卡片、船艙管理與其他彈窗。商店卡片沿用同一套木質底板與金色邊框語言。

五頁既有主框與已確認合格的主要 CTA 保留為正式視覺基準，不因共用 skin 素材庫建立而盲目覆蓋。本輪已替換 5 個 Close、8 個交易／改裝／貨艙輔助控制、商店出售鈕、Dialog／MarketInsight 兩张面板，以及船體／護盾／裝甲 3 組 gauge；4 個 HUD 也採同系列材質。貨艙依主人新增要求改為 4×3 每頁 12 格，容量與資料規則保留。新增素材是可替換素材庫：依各頁實際元件與版面需求逐項選用，只換確認需要換的部分；不藉機改動不相關玩法、佈局或美術資產。介面文字由遊戲文字元件獨立繪製，不烤進圖片。

## 核心視覺

- **風格**：正視、平面 2D、手繪楓谷式飛空海盜 UI；輪廓清晰、可愛但有份量，適合縮放後仍能閱讀。
- **主材質**：蜂蜜木色作為主要可互動表面；深胡桃木用於內凹文字欄、次級層與外框陰影。
- **邊框與輪廓**：暖黃銅／金色作為主框、按鈕焦點與選取狀態；厚實深棕描邊維持一致輪廓。高光簡化成少量清楚的手繪亮面，不使用寫實金屬反射或繁密紋理。
- **海事點綴**：繩結、鉚釘、指南針可出現在角落或端點；保持小而節制，裝飾不得進入文字安全區，也不得搶過按鈕標籤、數值或卡片內容。
- **方向**：所有 UI 素材正視、無透視、完整置於原生畫布內；不得出現場景、背景、假棋盤格或不屬於單一素材的拼貼。

## 色彩與互動層級

以角色名稱描述共用設計 token；替換或新增素材時沿用同一語意，不各頁私自發明近似色。

| Token | 用途與視覺層級 |
| --- | --- |
| `primaryGold` | 主要金屬框、主要按鈕、目前選取／確認焦點；最醒目的互動層。 |
| `secondaryWood` | 蜂蜜木、深胡桃木兩段木色；主要表面與內凹內容面以明暗區分。 |
| `neutralCream` | 由遊戲文字層繪製的主要文字色，確保在深木內容面上清楚；不得烤入素材。 |
| `disabled` | 降低明度與飽和度的木／金材質狀態；仍須辨識元件輪廓，不用大量透明疊黑讓文字消失。 |
| `toggle` | 開／關狀態以金色焦點或木色凹槽形成明確差異；狀態意義由 UI 元件／文字另行呈現。 |
| `arrow` | 導航箭頭沿用木金框材質；方向輪廓清晰，成對一致，不用文字烘焙方向。 |
| `close` | 關閉鈕使用獨立且易辨識的金框小按鈕；「X」由遊戲 UI 繪製，不烤進圖。 |

## 透明與文字規則

- PNG 使用 RGBA 真透明外部；裝飾元件本體不透明，邊緣只允許自然抗鋸齒 alpha。不得以棋盤格、純色底或帶背景的整頁截圖冒充透明素材。
- 背板內部保持不透明，文字欄應有足夠深色對比。外部透明邊界不能裁掉描邊、鉚釘、繩結或高光。
- 文字、數字、按鍵字樣、狀態圖示、商品圖與可變內容皆保持在獨立遊戲 UI 層。任何生成圖內若出現文字或水印，該版不得直接作為正式素材。
- 每種元件以明確內容安全區標示；動態中文長字串、數字與手機縮放都需在該安全區內驗證。裝飾不得侵入安全區。

## 圖檔與版面驗收契約

每個資產／版本都要在對應 manifest 或驗收紀錄中記錄下列欄位；未知值寫 `null`／`unknown`，不得推測：

1. `path`、資產 key、版本、SHA-256、檔案 bytes、RGBA mode。
2. `nativeCanvas`（原生像素寬高）與 `actualAlphaBbox`（透明外緣內實際 alpha 範圍，座標採半開區間）；保留原 PNG，不拉伸、裁切或非等比扭曲。
3. `layoutWidth`（遊戲內目標寬度／Rect 寬度）、`textSafeArea`（相對素材或原生像素的座標與範圍）、預期縮放方式，以及 UI 上下文／狀態。
4. `importRuid`：尚未匯入時明確記 `null`；匯入後記錄真實 RUID 與來源，不可用假 ID 代替。
5. `finalPrompt`：保存實際生成該版資產的完整最終提示詞，不以摘要取代。
6. `evidence`：生成檢查、alpha／畫布檢查、匯入與 Maker 原生畫面證據分開連結；未做的項目標 `pending`，不將單純生成或靜態檢查寫成實機通過。

版面整合只能依原生畫布比例進行等比縮放；若外部留白影響排版，優先記錄縮放／置中策略並確認安全區，不能直接把原 PNG 拉寬、拉高或剪掉內容。若必須產生新裁切或重繪版本，建立新版本與新雜湊，不覆寫來源。

## 本輪 HUD 與可替換 skin 素材

2026-10-04 manifest 目前收錄十六筆 PNG：十五張用途素材及一張重繪候選。完整 prompt、原生畫布、alpha bbox、RGBA、SHA-256、bytes、RUID 與狀態以 [manifest.json](../assets/ui-reskin/2026-10-04/manifest.json) 為準；十六筆均已透過驗證 HTTPS PUT 匯入，且取得資源 metadata 回查成功的真實 RUID；13 種素材已套入 26 個裝飾節點，PC Maker 原生驗證已完成，Luna 最終修復確認完成：

| Key | 原圖 | 用途 |
| --- | --- | --- |
| `hudLocation` | `hudLocation-v1.png` | 航行地點名稱木牌。 |
| `hudHint` | `hudHint-v1.png` | 窄版動態提示條。 |
| `hudCabin` | `hudCabin-v1.png` | 船艙管理入口按鈕。 |
| `hudInteract` | `hudInteract-v1.png` | 互動提示按鈕與空白按鍵框。 |
| `primaryGold` | `primaryGold-v1.png` | 主要金色行動按鈕皮膚，可依頁面需要替換 generic 主按鈕。 |
| `secondaryWood` | `secondaryWood-v1.png` | 次要深木色按鈕皮膚，可依頁面需要替換 generic 次按鈕。 |
| `creamPanel` | `creamPanel-v1.png` | 淺奶油色資訊／訊息面板皮膚，中心保留動態文字空間。 |
| `roundClose` | `roundClose-v1.png` | 圓形關閉鈕外框；X 由 runtime UI 繪製。 |
| `squareControl` | `squareControl-v1.png` | 方形輔助控制鈕外框；加減或箭頭符號由 runtime UI 繪製。 |
| `gaugeFrame` | `gaugeFrame-v1.png` | 金色細框與深胡桃木凹槽，供三組數值 gauge 共用。 |
| `gaugeHull` | `gaugeHull-v1.png` | 船體狀態的綠色填充條。 |
| `gaugeShield` | `gaugeShield-v1.png` | 護盾狀態的藍色填充條。 |
| `gaugeArmor` | `gaugeArmor-v1.png` | 裝甲狀態的琥珀金色填充條。 |
| `dialogWide` | `dialogWide-v1.png` | Shop Dialog 使用的超寬短資訊橫幅；專用尺寸，不以其他面板拉伸代用。 |
| `marketInfoPanel` | `marketInfoPanel-v1.png` | MarketInsight 使用的寬短雙行資訊面板；專用尺寸，不以其他面板拉伸代用。 |
| `gaugeFrameV2` | `gaugeFrameV2-v1.png` | 採用較厚的 gaugeFrame V2：可見框 275×31.4，固定填色圖片由 255×13 遮罩水平裁切；Maker 0%、50%、10%、100% 填色與完整金框已驗證。 |

### 排版與畫面參考

- [實際套用配置](../../.builder-work/hud-redesign/applied-layout.json)：26 個裝飾節點的真實 RUID、等比畫布、可見尺寸及 offset。279 個原節點 UUID 保留；正式 UI 目前 322 個節點。
- [HUD layout spec](../../.builder-work/hud-redesign/layout-spec.json)：左側地點牌 y=220 避開系統聊天區；船艙可見右緣 x=1676，離系統保留區 24px；船艙點擊高度 88，圖面等比呈現。
- [匯入證據](../../.builder-work/hud-redesign/import-results.json)：16 筆真 RUID、PNG 雜湊與 HTTP200 完成紀錄；舊 PUT403 診斷保留為歷史，根因不作推斷。
- [原有準備評論](../../.builder-work/hud-redesign/critic-round1.md)：素材 alpha 為 1/255 的柔邊不構成本體截斷；後續以靜態幾何與同版 Maker 圖補驗。
- [交接](../../.builder-work/hud-redesign/handoff.md)：最新補記優先於早期停點。

裝飾 Material 關閉 RaycastTarget；原 Button 保留操作範圍、文字透過安全 Label 繪製。互動入口的 E 使用獨立 KeyHint，動態正文不重複 E。兩專用資訊板等比呈現，不拉伸 creamPanel。三條 gauge 的金框固定，填色圖固定原生比例、只改遮罩寬度。

primaryGold、creamPanel、細版 gaugeFrame 留作已匯入素材庫；secondaryWood 已用於出售鈕。既有合格主要 CTA 不盲目替換。本次 PC Maker 原生回歸完成；[R4 凍結畫面](../evidence/2026-10-04/ui-reskin/R4/snapshot.json)保存五頁、長字、按鈕狀態與貨格邊界。[R5 定點回歸](../evidence/2026-10-04/ui-reskin/R5-targeted.json)修正驗收腳本漏傳容量參數的測試錯誤後，build 60 Info、normal 24 Info，沒有 Error／Warning。R4 的一筆測試錯誤原樣保留，不將其稱為零錯誤。Luna 最終修復確認完成，無未解P0／P1／P2；[完成紀錄](../evidence/2026-10-04/ui-reskin/completion.md)保存證據與限制。

## 驗收底線

- 同類元件跨商店、地圖、船舶、改裝／卡片、船艙、HUD 與彈窗共用相同材質語言；商店卡片木底與黃銅金框一致。
- 五頁主框與已確認合格的主要 CTA 保留；逐項處理已盤點的 generic 殘留，不把整頁或所有按鈕概括宣稱已合格。
- 以原生畫面檢查文字／數值安全區、按鈕狀態、透明邊緣、比例、層級與可點區；只看生成圖或資產 metadata 不算 Maker 視覺驗收。
- 每張素材都能由路徑、版本、SHA、prompt、alpha bbox、原生畫布、layout width、安全區、真實 RUID 與證據連回其 UI 用途。

## 貨艙與互動狀態

貨格採4列3行，每頁12格；基礎容量8或10同頁，合法改裝上限18分兩頁。只顯示實際容量，最後頁不產生幽靈格。每格110×84，圖示56×38、標籤94×26；左右木框鈕52×40置於格子下方，單頁隱藏，末頁停用Next。

Material／Label 分別上色：Normal白／奶油金、Hover暖白／亮奶油金、Pressed深金棕／奶油金、Disabled低彩木灰／可讀金灰。動態文字同步Label，裝飾不攔截Raycast；事件訂閱在OnEndPlay解除。

本輪覆蓋PC1920×1080（Maker原生1689×950）；手機與標準GUI實體滑鼠未驗證，事件注入不代表物理點擊。貨量／T1庫存／長文字／gauge fixtures都在client還原，不宣稱購買、改裝或持久化測試。
