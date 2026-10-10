# 全專案金流與價格唯讀稽核（2026-10-10）

> 整合建議：本附件只提供金流風險與價格研究，不應取代本輪材料規格。材料價格、配方與消耗方式請以 [GreatVoyage-Ship-Materials-20261010.md](../GreatVoyage-Ship-Materials-20261010.md) 作為本輪草案指標；該草案的材料總價與取得難度應和船舶現金造價分開評估。T5 2,147,483,647 G 與整數 G 定價為已定案事項；T2 500,000、T3 5,000,000、T4 200,000,000 G 僅是候選值。

範圍：RootDesk/**/*.mlua 全 19 個腳本；另讀 ProfileStore 使用的 MSW UserDataStorage.d.mlua 型別簽章與腳本存檔規範。未讀 .ui、.map、.model，未呼叫 Maker，也未修改遊戲檔。行號以本次稽核工作樹為準。

## 主要結論

現行金流由伺服器持有 GreatVoyageVoyageState 的帳號狀態，永久金額為 core.money；可見收入只有出售貨物與出售未安裝改裝卡。航行沒有費用，戰鬥／怪物流程未找到發錢程式。主要支出是商品、船、改裝卡與維修。

目前 ProfileStore 將金額限制為 2,147,483,647（signed int32 最大值）；存檔的金額是 JSON 數值，DataStorage API 實際保存字串。已定案的 T5 價格正好等於目前程式上限，因此持有該金額時，售貨或卡片出售會被拒絕，直到玩家先花錢。這是現行程式／存檔限制的稽核結果，不是未來設計約束；未來若擴充錢包上限，需另行驗證資料型別、ProfileStore 驗證與所有交易路徑。

需要先平衡的風險是跨港商品套利。現役已核實商品 commodity_edelstein_389（700,000 G）在尼哈爾需求倍率 5.0，單件無壓力報價 3,500,000 G。BOSS 商品購買補貨與售出壓力分開記在各港市場；售出壓力能分散到多個港口。若商品被抽進艾德斯坦貨架，可分別構造「尼哈爾單港一次賣 10 件」與「在 9 個需求港分散出售」兩個理論情境：前者淨利 13.825M G，後者淨利 9.38M G。兩者使用不同的市場壓力分布，9.38M 不是全局最高值，也不是持續套利上界。補貨量每週期隨機 1–10，貨架抽選，且玩家要先有足夠本金。

目前 materialUse 只是商品標籤；GetShipbuildingMaterials() 只篩選並回傳目錄，未找到消耗材料造船或以材料修理的正式金流機制。因此材料仍依一般貨物買賣規則結算。

## 金流來源、支出與狀態

| 類型 | 程式位置 | 實際行為 |
|---|---|---|
| 新帳號本金 | RootDesk/MyDesk/GreatVoyageVoyageData.mlua:634-637；RootDesk/MyDesk/Persistence/GreatVoyageProfileStore.mlua:282-291 | GetStartingMoney() 回傳 12,000；首次存檔以此建立 core.money。既有玩家載入 profile.core.money，不重發本金。 |
| 貨物買入（sink） | RootDesk/MyDesk/GreatVoyageVoyageState.mlua:1440-1487 | 伺服器確認港口商人、現役貨架、容量、航行狀態與餘額；支出 good.price × quantity，並把實際買價存進 FIFO lot。BOSS 貨另受來源港每三小時補貨限制。 |
| 貨物出售（source） | RootDesk/MyDesk/GreatVoyageVoyageState.mlua:1490-1557 | 伺服器確認持有量與港口後重新報價；按 FIFO 移除貨物批次，將市場報價總額加進 state.money。removal.cost 只用於 profit 日誌，不作最低售價保護，因此能低於歷史買入成本出售。 |
| 船舶購買（sink） | RootDesk/MyDesk/GreatVoyageVoyageState.mlua:540-565；RootDesk/MyDesk/GreatVoyageVoyageData.mlua:174-195 | T0 小風帆 0 G；現有四艘 T1 各 50,000 G。已持有船不能重複購買；未見船舶出售／回收金額。伺服器只從船舶目錄取得價格。 |
| 改裝卡買入（sink） | RootDesk/MyDesk/GreatVoyageVoyageState.mlua:660-698；RootDesk/MyDesk/GreatVoyageVoyageData.mlua:197-236 | 每次 1–99 張，依每港伺服器抽出的清單驗證；同卡最多 99 張（含裝船卡）。目錄標價 30–110 × 經濟倍率 100，即 3,000–11,000 G。 |
| 改裝卡出售（source） | RootDesk/MyDesk/GreatVoyageVoyageState.mlua:758-783 | 只能出售未安裝庫存，單次 1–99 張；售價為目錄 sellPrice × 100，目前約為買價一半（貨艙卡 1,700/3,500 等非整半值）。收入前檢查 int32 上限。可以回售但沒有買賣套利。 |
| 船舶維修（sink） | RootDesk/MyDesk/GreatVoyageVoyageState.mlua:785-840；RootDesk/MyDesk/GreatVoyageVoyageData.mlua:279-288 | T0 免費；其他船按缺失船體／護盾／裝甲總點數 × 0.5 × 卡片維修倍率 × 100，向上取整。T1 無卡完整修理約 9,600–10,800 G。維修卡倍率相加，公式底限為 0.25（GreatVoyageVoyageState.mlua:250-292）。 |
| 航行費／戰鬥收入／任務收入 | GreatVoyageVoyageState.mlua 航行與遭遇流程；GreatVoyageDeckRaid.mlua、GreatVoyageDeckMushroom.mlua | 19 個 mLua 全文搜尋未找到航行扣錢、戰鬥發錢、任務獎金或怪物直接掉錢程式。戰利品材料／商品來源尚未接到金流。這是程式搜尋結果，沒有做遊戲內實測。 |
| 舊 Phase 0 本地錢包 | RootDesk/MyDesk/Phase0VoyagePrototype.mlua:10,49-75,120-174 | 另有 property integer money，重設為 12,000；舊船體／護盾升級與整備在 ClientOnly 本地扣款，不是 ProfileStore 永久帳號金額。貨物買賣入口轉呼叫正式伺服器 State（同檔 267-289）。若此原型 UI 對一般玩家仍可操作，畫面會出現與正式帳號不同步的測試錢包。 |

錢包快照與畫面只做展示：GreatVoyageVoyageState.mlua:23,889-941 把伺服器金額投影給本人；HUD 在 GreatVoyageHUDController.mlua:107 顯示，商店按鈕在 GreatVoyageAdventureController.mlua:3004-3027,3140-3155 預覽／禁用操作。客戶端市場 quote 是展示投影（GreatVoyagePlayerMarket.mlua:79-100）；伺服器成交會重讀市場並重新計算，不能靠舊 UI quote 鎖定成交價。

## 商品價格、跨港報價與套利

商品基價與各港 demand 都在 RootDesk/MyDesk/Economy/GreatVoyageCommodityCatalog.mlua:6-204。現役商品透過該檔 GetForPort()（226-256）按來源港抽選上架，最多 12 項或來源目錄的 60%。GreatVoyageVoyageData.mlua:348-355 的固定售價是來源港 0.8 × 基價，其他港則為 demand × 基價；買價保持基價，不隨 demand 變動。

GreatVoyageMarketPricing.mlua:4-17,41-81 依商品層級逐件壓低售價：一般商品容量 60、恢復 7,200 秒、底價倍率 0.8；starter 容量 120、恢復 1,800 秒、底價 1.2；BOSS 容量 10、恢復 28,800 秒、底價 0.5（starter boss 例外為 1.2）。每賣一件增加 1/capacity 壓力，報價從 demand 基價線性降到 min(demand, floorMultiplier)。每帳號、每港、每商品各自記錄售出壓力。

最高現役已核實情境：

- commodity_edelstein_389「特殊型能源核心（S級）」在目錄第 184 行，基價 700,000 G、來源艾德斯坦、BOSS 商品。尼哈爾 demand 5.0；來源港買一件花 700,000 G，尼哈爾零壓力首件報 3,500,000 G，淨利 2,800,000 G。
- 在尼哈爾同一市場一次賣 10 件且起始壓力為 0，逐件倍率為 5.00、4.55、4.10、3.65、3.20、2.75、2.30、1.85、1.40、0.95；售額 20,825,000 G，成本 7,000,000 G，淨利 13,825,000 G。第 10 件本身已低於成本；賣完壓力達 1，後續價格降至 0.5 倍附近，會虧損。
- 這不是可持續的單港價格。GetBossStock（同檔 83-100）每 10,800 秒週期依帳號與商品雜湊抽出 1–10 件，平均 5.5、上限 10；ConsumeBossStock（103-118）把 cycle/bought 記在買入來源港，出售壓力另存於出售港。艾德斯坦有 13 個現役已核實來源商品，每次貨架抽 8 個，因此 row 389 不保證每期上架。
- 各需求港的壓力記錄彼此獨立。理論上可在壓力已恢復的 9 個獲利港各賣 1 件，再於尼哈爾賣第二件。按最大 10 件補貨、所有目標港起始壓力為 0 算，售額約 16,380,000 G，成本 7,000,000 G，淨利約 9,380,000 G／週期。BOSS 壓力 0.1 會在 3 小時內完全恢復（完整壓力恢復需 8 小時）；每趟基礎航程 60 秒（GreatVoyageVoyageState.mlua:6,1136-1139），腳本沒有航行費或燃料扣款。這是有條件可重複的套利模型；實際數字受該帳號隨機補貨量、貨架抽選、船艙容量與航行流程限制。T0 容量 8（GreatVoyageVoyageData.mlua:176-185），T1 行商號容量 10。
- commodity_leafre_351「太初精髓」第 163 行，基價 700,000 G、一般商品、森林 demand 2.0。壓力容量 60、恢復 2 小時；10 件一次裝船、同市場零壓力起售，首批淨利約 6.9M G。後續收益由到訪間隔與壓力恢復決定；此計算未將抽貨架視為必定供貨。
- 目前 700,000 G 的材料／BOSS 商品高於 T2 船價候選 500,000 G。未先確定造船配方總投入就調材料價格，可能讓一件稀有料本身跨越低階船價。最高 demand 5.0 是明確套利壓力測試案例。

## FIFO、調價與存檔影響

- 每次買貨新增 { id, quantity, buyPrice } lot。GreatVoyageVoyageData.mlua:20-110 的 CopyCargo/AddCargo/RemoveCargo 保留每批實際買價，只合併相鄰同商品同價批次；出售按 FIFO 成本計算日誌利潤。
- 售價不是買入時的快照。SellCargoInternal 依當前 catalog good.price、當前港 demand 和當前壓力重新算售額；removal.cost 不設最低收入。因此改同 ID 材料基價會立即改變新買價與舊貨未來銷售報價，但既有批次 buyPrice 不會改：提價使舊貨利潤增加，降價則可能使舊貨虧損。這是調價時最大的存貨套利／財產價值風險。
- 市場存檔只含 pressure/at/cycle/bought，不存基價版本；調價後壓力百分比會沿用，由新基價乘上舊壓力曲線。客戶端 quote 不鎖價，伺服器不使用客戶端傳入的 quote。
- ProfileStore schema 2 保存 core.money 和 cargo.lots[]（GreatVoyageProfileStore.mlua:11,163-233,252-265）。歷史 buyPrice 必須在 1..2,147,483,647；商品 ID 必須仍存在且 verified。保留舊 ID 是存檔相容條件。僅調價不需改 schema；不要為改新價覆寫玩家歷史成本。
- ProfileStore 將整份 JSON payload 限制為 48,000 bytes（GreatVoyageProfileStore.mlua:14,539-543,740-755）。MSW UserDataStorage API 與 DataStorageItem.Value 的簽章以 string 傳值，未声明貨幣專屬上限；msw-scripting/references/datastorage.md:49-58 的 DataStorage Credit 規範以每 4,000 bytes 計一個 credit（向上取整），這是用量刻度而非最大 payload。接近專案 48 KB 門檻時，單次 Get/Set 可達約 12 credits。
- 市場購買上限檢查在 GreatVoyageVoyageState.mlua:1476-1479（交易總額 ≤ int32 且餘額足夠）；出售在 1543-1552（交易總額及加回餘額不可超限）；卡片出售在 773-777。Profile 金額及 lot 成本驗證在 GreatVoyageProfileStore.mlua:165-171,197-220。
- T5=2,147,483,647 G 可在現行 ProfileStore 限制內保存及購買（剛好持有上限時購買同價船會歸零），但高於目前限制的商品價格或交易總額不能成交；餘額到頂也無法再出售。T4 200M 僅為候選值，和已定案 T5 的倍率不代表已採用的船級比例。未來修理費也受目前限制；GetRepairQuote 沒有額外 clamp。現有船不會接近此值，T5 能力值還未定。錢包擴容是獨立的未來驗證事項，不應因此下修已定案 T5 價格。

## 現行材料售價分布

GetShipbuildingMaterials() 篩出的現役且已核實材料有 106 筆，基價範圍 1,000–700,000 G；價格由 catalog 中既有商品基價決定，尚未以船級或配方成本歸一。代表性級距：

| materialUse | 筆數 | 基價範圍 |
|---|---:|---:|
| 船體補強 | 19 | 1,000–80,000 G |
| 帆布與繩索 | 19 | 2,000–50,000 G |
| 魔法裝置 | 9 | 6,500–700,000 G |
| 高階強化 | 6 | 28,000–190,000 G |
| 進階裝置 | 4 | 35,000–250,000 G |
| BOSS 核心 | 3 | 200,000–450,000 G |
| 動力核心 | 4 | 45,000–700,000 G |

同一用途類別內已有一個數量級以上的跨度；這可以代表稀有度，但若未來同類材料投入量相近，玩家會自然選低價替代品。配方需明確指定材料用途，否則這些 price tiers 不會自然變成打造進度。

## 材料調價原則（本次不改任何價格）

1. 先定每個船級配方與材料數量，再反推材料籃子的總成本。把材料成本占船價 25–40%、其餘以現金構成 sink 僅視為研究候選，本輪不採用：主人要求 T5 金幣造價與材料另計，主建議應是收取船舶現金費，並另外消耗配方材料。材料數量、價格與取得難度依本輪材料草案評估；不要把材料價格綁定到尚未定案的 T2/T3/T4 候選船價。
2. 配方內分層：木材、纖維、普通金屬等大量基礎料維持低單價；加工件／船體補強料中價；導航、動力與 BOSS 核心等稀有料依實際取得難度定價。各船級與配方數量仍待草案定案；避免一箱普通材料等於一艘低階船。
3. 材料跨港 demand 應能帶來差價，但不能比造船材料 sink 更快印錢。5.0 倍 BOSS demand 是現行壓力測試案例；GetPolicy 的底價只限制壓力後報價，擋不住首批高倍率利潤。
4. 保留穩定商品 ID，將 buyPrice 視為歷史成本。調價後新交易採新基價，但先接受舊存貨因此產生短期利得／損失；不要把玩家貨艙批次成本一律改成新價。
5. 現行程式的新船價、材料總額、修理費和出售收入都受 signed int32 上限限制；T5 已定案為 2,147,483,647 G，不建議因此下修。未來錢包擴容時，另行驗證金額型別、存檔驗證、交易加減與修理報價。

## 尚未實作／本輪限制

- T2、T3、T4、T5 船型與價格未出現在 GetShipCatalog()；T5 2,147,483,647 G 為已定案價格，T2 500,000、T3 5,000,000、T4 200,000,000 G 僅為候選值，均非現行遊戲資料。
- 造船材料消耗、材料打造、怪物貨物掉落、戰利品現金、航行費、船隻出售與交易費均未找到正式伺服器實作。
- EconomyScale 為 100；卡價與修理使用它，但 GetShipCatalog() 的 50,000 G 船價是直接常數，沒有乘倍率。GetEconomyScale() 第 640 行註解說船、卡、維修共用倍率，與船價實作不一致；未來調倍率前須修註解或統一規則。
- 未讀 Maker build/play 或帳號 DataStorage，未驗證線上存檔餘額、庫存或輪替貨架種子。

## 涉及檔案索引

- RootDesk/MyDesk/Economy/GreatVoyageCommodityCatalog.mlua：商品基價與 demand（6-204）；現役材料篩選（207-224）；港口貨架抽選（226-256）。
- RootDesk/MyDesk/Economy/GreatVoyageMarketPricing.mlua：價格壓力政策與逐件報價（4-81）；BOSS 週期庫存（83-118）。
- RootDesk/MyDesk/Economy/GreatVoyagePlayerMarket.mlua：帳號市場快取及客戶端 quote projection（38-100）；資料 writer 由 ProfileStore 管理。
- RootDesk/MyDesk/GreatVoyageVoyageData.mlua：FIFO 成本（20-110）；船價及卡價（174-236）；維修公式（279-288）；固定買賣價（342-355）；本金與倍率（634-642）。
- RootDesk/MyDesk/GreatVoyageVoyageState.mlua：伺服器交易與正式金額 mutation（540-840、1440-1557）；航程時間（6、1136-1139）。
- RootDesk/MyDesk/Persistence/GreatVoyageProfileStore.mlua：schema、int32/payload 檢查、FIFO 買價、profile 建立／存取（11-14、163-233、282-330、539-543、740-755）。
- RootDesk/MyDesk/Phase0VoyagePrototype.mlua：舊本地錢包及舊成本（10、49-75、120-174）；交易轉呼叫正式伺服器（267-289）。
- RootDesk/MyDesk/UI/GreatVoyageAdventureController.mlua、RootDesk/MyDesk/UI/GreatVoyageHUDController.mlua：錢包展示與 quote preview，非權威結算。
- Environment/NativeScripts/Misc/UserDataStorage.d.mlua、Environment/NativeScripts/Misc/DataStorageItem.d.mlua：存取值型別為 string；未聲明貨幣專屬上限。
