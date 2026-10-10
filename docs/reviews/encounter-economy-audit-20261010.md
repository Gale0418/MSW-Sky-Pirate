# 航程戰鬥與經濟盤點（2026-10-10）

> 唯讀研究附件，供後續遭遇設計與主代理整合。只讀取 RootDesk/MyDesk 的 .mlua、docs 與 Archive 規劃／As-built；沒有呼叫 Maker 或網路研究，沒有修改遊戲檔。路線分段數值依 VoyageData 的港口座標、多邊形優先權與 SplitRoute 幾何算法在本地重算（640×472 地圖比例）；小數四捨五入至 0.1。

## 現況速覽

- 四個已開放港口 forest/sky/ludus/nihal 的直航每一方向均用港口地圖座標直接連線；地圖比例是 640×472。路程長短只影響顯示進度與遭遇點位置，基礎航程一律 60 秒；T1 齒輪船 54 秒、行商船 66 秒，普通 T1 船 60 秒。航速卡與速度改裝按槽位相加後改時間（durationMultiplier=船型倍率/速度倍率）；鍋爐另改前段速度。來源：[GreatVoyageVoyageData.mlua](../../RootDesk/MyDesk/GreatVoyageVoyageData.mlua#L128)（港口座標、L358–416空域）、[GreatVoyageVoyageState.mlua](../../RootDesk/MyDesk/GreatVoyageVoyageState.mlua#L1120)（出航鎖定航程，L1617–1658推進）。
- 七個命名空域：forest_wind、victoria、aqua、ludus、nihal、orbis_highwind、ellinia_cloud；多邊形外落入 open_sea。多空域共用物種；目前資料不是每區多怪池，也沒有 BOSS。forest_wind/victoria/ellinia_cloud→stirge 蝙蝠，aqua/open_sea→bubble_fish 泡泡魚，ludus→yellow_plane 黃色戰鬥機，nihal→kiyo 禿鷹，orbis_highwind→star_pixie 星光精靈。來源：VoyageData L358–416。
- 五種敵人目前全為 120 HP、2 秒一次攻擊；單發傷害依序 8/10/12/14/16。玩家是伺服器模擬的自動砲擊：每秒 20×cannonMultiplier 傷害，砲彈飛行 0.6 秒；沒有實際彈藥扣款。單敵普通倍率通常約 7.6 秒被擊敗；空戰至多 15 秒的時限內按事件順序結算，沉船會清貨返回出發港。這代表目前是「每空域一場單敵空戰」，不是甲板上同屏刷怪。來源：VoyageData L399–416、VoyageState L1249–1388；舊甲板遭遇入口已停用，見 [GreatVoyageDeckRaid.mlua](../../RootDesk/MyDesk/GreatVoyageDeckRaid.mlua#L14)。

## 四港直航的實際遭遇頻率

目前觸發點固定在每個幾何 segment 中點，每段最多觸發一戰，獨立抽 0.65 × 遭遇卡 modifier。實作沒有把 segment 長度或該區 risk 帶進機率；risk 目前只用在航線預覽的 expectedEncounter 欄位。因此極短的 6.8m ludus 段也會跟長 144m 的 open_sea 段一樣抽 65%。下表「實際期望戰數」與「至少一戰」是無改裝卡時依現有程式推算；它們取決於幾何段數而非預覽期望值。

| 直航（反向距離相同） | 路程 | 空域段（段長） | 段數 | 實際期望戰數 | 至少一戰機率 | 預覽 risk 加權期望事件數* |
|---|---:|---|---:|---:|---:|---:|
| 森林↔天空 | 230.4 | victoria 86.3；open_sea 144.2 | 2 | 1.30 | 87.8% | 1.00 |
| 森林↔玩具城 | 222.5 | victoria 69.1；aqua 104.8；ludus 48.7 | 3 | 1.95 | 95.7% | 1.00 |
| 森林↔納希 | 382.3 | victoria 73.2；aqua 144.0；ludus 62.6；nihal 102.5 | 4 | 2.60 | 98.5% | 1.03 |
| 天空↔玩具城 | 135.1 | open_sea 90.1；ludus 45.0 | 2 | 1.30 | 87.8% | 1.00 |
| 天空↔納希 | 250.8 | open_sea 88.5；ludus 6.8；open_sea 76.8；nihal 78.7 | 4 | 2.60 | 98.5% | 0.39 |
| 玩具城↔納希 | 161.6 | ludus 53.9；nihal 107.7 | 2 | 1.30 | 87.8% | 1.00 |

* 現有預覽以 max(1, round(Σ段長×risk/100)) 算事件數，故天空↔納希預覽 1、實際抽戰期望 2.6；森林↔天空也顯示 1、實際期望 1.3。每段 65% 下，兩、三、四段至少一戰分別 87.75%、95.71%、98.50%。空域 risk 值為森林風廊 .08、維多利亞 .16、水世界 .24、玩具城 .31、納希 .36、天空高風 .12、艾利涅 .20、開放空域 .05。直航段表依 VoyageData L358–395 多邊形及 L503–539 的 priority 切割算法計算；trigger/chance 在 VoyageState L1177–1198，預覽在 VoyageData L562–580。

四港直航實際不會經過 forest_wind、orbis_highwind、ellinia_cloud，但這些定義與怪物池已存在，後續新增目的港才會覆蓋。sky↔nihal 會因 ludus 多邊形切出一小段，現制將它當完整遭遇機會。

## 遭遇卡接線與疊加風險

卡片欄位列在 VoyageData L197–219；每船最多三槽。CalculateShipUpgrades 對三槽同欄位做加總，接著 GetSegmentEncounterChance 將適用 modifier 類別相乘並把最終機率 clamp 在 10%–95%（VoyageState L238–292、L1186–1198）。

| 卡 ID／名稱 | 欄位及每張效果 | 當前作用範圍／限制 |
|---|---|---|
| stealth 靜音螺旋槳 | encounterMultiplier=-0.40；速度懲罰 -0.10 | 每張將基礎遭遇率乘以 0.60，另降低速度；三張同槽效果合併成 -120%，機率再被下限 10% 托住，航程變慢。 |
| lure 誘敵信標 | encounterMultiplier=+0.50 | 每張乘以 1.50；三張使 65%×2.5 後被上限壓成 95%。 |
| fog 雲海偽裝 | fogEncounterMultiplier=-0.30 | 只適用 open_sea/aqua/*wind/*cloud；每張乘 0.70。 |
| monster_bait 飛怪誘餌 | monsterEncounterMultiplier=+0.35 | 只適用 stirge/kiyo 池；每張乘 1.35。 |
| magic_resonator 魔力共鳴器 | magicEncounterMultiplier=+0.50 | 只適用 star_pixie；每張乘 1.50。 |
| giant_lure 巨型誘餌 | 無 modifier、available=false | 描述是引來巨型飛行生物，但前置「巨型飛行敵人事件」未開放，伺服器禁止購買/安裝。 |

同欄位跨槽是相加後乘一次，例如 lure + stealth 各一張得到 1 + .50 - .40 = 1.10，然後基礎 .65×1.10；fog/monster/magic 是分開的情境欄位，會再與通用倍率相乘。這套接線只有在機率函式呼叫一次時安全。擴充群怪後不可把 lure 同時乘一次遭遇機率、再乘一次敵人數量；也不可先把 monster_bait 合入全域遭遇倍率，再按種類重乘。建議機率修飾卡只修飾「是否觸發」，船級＋財富只修飾「觸發率、敵數與敵人強度」；每個 modifier 欄位只讀取一次。

## 船隻、裝備、修理與財富基準

- 起始金幣 12,000 G；小風帆 T0 價格 0、耐久三層 100/20/40、貨艙 8、砲擊倍率 1、維修免費。四艘 T1 每艘 50,000 G；基礎三層 120/24/48、貨艙 8，森芽船體上限 +20%、赤帆砲擊 +10%、齒輪航程 -10%、行商貨艙 +25%（8→10）且航程 +10%。來源：VoyageData L174–185、L634–641。
- 三槽可裝同卡，所有改裝數值按卡欄位累加；火力卡每張 +5%，高爆火藥 +20% 並承受傷害 +10%；目前沒有「無炮時降低敵人強度」的支路，敵人 HP/攻擊完全不看火力倍率，只影響玩家多久打完。每場空戰沒有彈藥費。來源：VoyageData L200–219；VoyageState L1257–1287。
- T1 維修費是每點缺失船體／護盾／裝甲 50 G，三層全空最高 9,600 G；模組化甲板每張 -25% 修理費、高壓傳動每張 +50%，修理倍率最小 0.25。T0 免費維修形成清楚的失敗保護。來源：VoyageData L279–288，VoyageState L785–812。
- 建議用航戰啟動當刻的 W = max(0, money) + Σ(貨物數量×catalog good.price) 作為財富快照；使用穩定 catalog 參考價，不用購入批次成本、客戶端報價或受市場壓力影響的 sell quote，避免囤積便宜批次被低估或價格波動改變威脅。現況 cargo 保存 FIFO lots（quantity、id、buyPrice），貨艙上限為 8/10 格；不是貨艙每格都代表相同價值。來源：VoyageData L20–110；ProfileStore L197–231。

## T0–T5 造價與收益時間級距

目前目錄只有 T0 小風帆與四艘各 50,000 G 的 T1 船；森芽、赤帆、齒輪、行商是四種同級定位，不能把它們稱為 T1–T4。新增目標 T5=9,999,999,999 G，約為一艘現有 T1 價格的 200,000 倍；現有 T2–T5 造價與收入階梯尚不存在。

現役四港商品掃描中最高的有效現行商品是玩具城 Boss 商品黑暗塔奇昂，250,000 G/件；基礎貨艙 8 件，行商船 10 件。以初始市場壓力為 0、賣到納希 demand=4、Boss floor=0.5 的報價公式估算，8 件首批售價合計約 5.55m G，成本 2m，毛利約 3.55m；價格壓力每售一件上升 0.1，該批之後還需等壓力恢復（8 小時 policy），Boss 貨源每 profile 每 3 小時僅 1–10 件。這是公式推演的理論上限例，不是穩定每趟收入或實機收益。單靠此例約需 2,817 批完整且無既有壓力的 8 件盈利交易才到 10b；壓力、貨架抽選、庫存與航行間隔會使實際時間更長。若一般賞金均值採 120 G/隻，純現金賞金則需約 83,333,334 隻擊殺才能累積到 10b；財富成長擴大敵群且能存活時，收入會加速，不能用固定 DPS 假設換算真實遊玩時數。

這代表 10b 應明確定位為極長期的終局船體成本，並同步定義 T2–T5 的造價、單趟補給／修理回收、敵數成長與可持續 G/小時級距；如果設計目標是數十小時內買到，現有貿易和 80–180 G 普通賞金遠遠不夠，需有隨風險成長的任務／素材交易或明確的大型獵怪收益。這是進度選擇，不應靠高財富獵怪上限或個人遞減處罰去控制。

## 跑商收益的實際約束

商品不是固定每港全上架：CommodityCatalog 以伺服器 session seed 為每港商品抽出最多 12 筆、約 60% 候選；只有 verified 且未 retired 商品能上架。買入按 good.price，出售按 origin 0.8 倍或目的港 demand 倍率，再依市場 pressure 從 baseline 往 floor 逐件下修。普通商品 pressure 容量 60、恢復 7,200 秒、最低倍率最多到 0.8；starter 容量 120、恢復 1,800 秒、floor 1.2；Boss 商品容量 10、恢復 28,800 秒、Boss-stock 每帳號每商品每 3 小時穩定抽 1–10 件。FIFO lots 使混裝每種商品都按自己的購入成本算損益。來源：[CommodityCatalog.mlua](../../RootDesk/MyDesk/Economy/GreatVoyageCommodityCatalog.mlua#L197)、[MarketPricing.mlua](../../RootDesk/MyDesk/Economy/GreatVoyageMarketPricing.mlua#L4)、[GreatVoyageVoyageData.mlua](../../RootDesk/MyDesk/GreatVoyageVoyageData.mlua#L348)、[GreatVoyageVoyageState.mlua](../../RootDesk/MyDesk/GreatVoyageVoyageState.mlua#L1438)。

可持續跑商收益不能用「每趟固定 x%」描述：商品貨架抽樣、目的港 demand、同帳號市場 pressure、貨艙容量與 Boss stock 都會改變實收。森林產綠水靈液體基價 3,000 G，目的港納希 demand 2.0、基準 6,000 G；森林產木材基價 3,000 G、天空 demand 1.2、基準 3,600 G；市場壓力會使普通商品向 0.8 倍基價下修，第一例壓到 2,400 G 時只剩 -600 G/件。實際能否買到還要抽中當期貨架。財富越高遭遇越多是使用者指定的風險回饋，不應把活著刷賞金列成漏洞；為避免賞金失控，固定單隻賞金與素材供應價，不將掉落乘財富或改裝倍率。

## 存檔與重複結算風險

ProfileStore schemaVersion=2 的 profile 驗證／序列化欄位包含安全港、money、cargo 與 FIFO lots、activeShipId、各船耐久／槽位、cardInventory、markets；沒有 bounty、loot ledger、ammo、airBattle 或 durable voyage ID。BuildRuntimeProfile 明寫只收斂安全資產，不保存航程、戰鬥或衍生 stats（ProfileStore L163–265）。VoyageState 目前給一趟產生 transient voyageSequence，戰鬥 id 是 playerId+sequence+battleCount；FinalizeAirBattle 用記憶體的 battle.settled 防同一物件重入，PersistSettledVoyage 只在抵港或沉船持久化。這能防當前單次流程重入，不能單獨當未來賞金的持久防重帳本。

建議把每趟唯一 id 寫入出航 durable snapshot（例如 profile revision 遞增的 voyage id），每次擊殺事件用 profileCode|voyageId|segmentIndex|waveIndex|enemyIndex 當 claim key。伺服器先在該玩家狀態鎖住該 kill，再用現有單一 ProfileStore CAS 一次原子寫入「金幣／素材＋已領 claim id」；重試必須先 readback，已存在 id 就回傳同一收據且不重發。不要將賞金先加進非 durable 狀態，再由另一個獨立寫入重加；不要只用可重建的 playerId 或目前 server memory 作唯一鍵。航次沉船時再按玩法定義已殺敵獎勵保留規則，避免「成功抵港與沉船各領一次」。

高收益活著獵怪是被指定的玩法；真正要擋的是相同 kill/event 的重放、重複 RPC、保存結果不明後重試重發、抵港/沉船競態重領。失敗風險要明確列出船體修理、丟失貨物與可能的未交付戰利品；如果保留已擊殺戰利品，需讓它在沉船結算中只有單一歸屬。

## 可落地的擴充公式（建議起始參數，需實作後平衡）

保留按空域分池並擴充為每個空域自己的 common/elite/boss pool；現有五隻作素材，不應把「同空域一直出同一隻」當成已完成多樣怪池。BOSS 使用獨立最高威脅階級，明確標示出現率、波數與強度。所有戰鬥由伺服器抽選並鎖定，不讀客戶端宣稱的金額／敵數。

定義：T 為船級（T0=0、T1=1，往後按正式船級編號）；W 為上節戰鬥開始時計算的持有財富 G；wealthScore = log10(1 + W / 100000)，S=T+wealthScore。高財富沒有封頂、每日限制或個人遞減；對數曲線是讓 10b 持有者仍可玩、同時財富繼續增加風險與敵數的平滑增長，不是收益懲罰。每段風險率採長度與空域 risk 的 hazard：baseHazard = 0.35 × (segmentLength / 100) × (airspaceRisk / 0.20)，p = 1 - exp(-baseHazard × (1 + 0.10×S) × cardMultiplier)。cardMultiplier 只由現有 general/terrain/species modifier 各取一次後相乘；最終 p 可依遊戲保護需要夾在合理下限與上限。這讓 6.8m 段不會與 144m 段同機率，也讓高危空域及高財富增加旅程風險。

每個成功觸發的遭遇總敵數 N = 1 + floor(S)，不封頂或個人遞減；隨船級或持有財富上升而不會下降。例：T0、W=12k 起始仍為 1 隻；T5、W=10b 時為 11 隻。這避免把 10b 換成 20 萬隻敵人，同時沒有最終敵數上限；若未來財富高於此，S 和敵數仍會繼續增長。同屏只生成 4 隻，剩餘數量分波排隊，所有敵人都必須出戰、計賞金與掉落，不能以同屏上限截斷總數。若需要控制 server 模擬工作量，逐 tick 限制每玩家結算事件數並延後排隊，不能刪敵／刪獎勵。敵人血量與攻擊只依空域敵種階級、BOSS 階級與 S 的緩慢線性係數上調（例如 HP = baseHP×(1+0.05×S)、damage=baseDamage×(1+0.025×S)），永遠不依玩家砲擊倍率下降；玩家無炮或低傷害不會抽到更少怪或比較軟的怪。若單位 HP/DPS 太高，提供逃跑/投降等明確風險選擇，不偷偷降低遭遇量。

**初始相對賞金與掉落範例：**一般怪單隻固定 80–180 G（依現有攻擊值排序；stirge 80、star_pixie 100、bubble_fish 120、yellow_plane 150、kiyo 180）；每隻 25% 機率掉固定材料一份，供應價 100–300 G，材料可做後續造船/改裝用途。Elite 賞金約同區普通怪 2 倍、材料掉率 50%；Boss 賞金 600 G、必掉一份 500 G 固定價核心素材。所有單位獎勵不乘船級、財富、lure 或火力；錢變多只能靠多殺怪且成功存活。這使單隻回報遠低於 T1 三層全修 9,600 G，遇戰受到的傷害成本與沉船貨物損失仍能吃掉多趟獎勵；實際 DPS/船體迴圈需再用玩法測試校準。

賞金貨幣現況不是泛稱的引擎限制，而是程式明確實作限制：ProfileStore 驗證 core.money ≤ 2,147,483,647（L171），Buy/Sell 檢查交易總額與餘額不超過此值，售卡及存檔整數驗證也使用相同上限；VoyageState 金額快照仍使用 integer 參數。T5 9,999,999,999 是舊 cap 的約 4.66 倍，現行實作會拒絕或阻止到達，不能只新增一筆船價。要先端到端遷移 Profile schema、讀寫驗證、存檔 readback、買賣與賞金 RPC 金額型別、加減法溢位檢查。JSONEncode 有序列化金額欄位，但本次唯讀審核沒有證明 mLua integer／number 或 Maker JSON 在 10b 的引擎界線；不要把程式 cap 誤稱為 MapleStory 金幣歷史上限。若官方文件與 runtime probe 確認 number 能精確保存此整數，可統一以 number 搭配整數性檢查；否則持久化為十進位字串並用一致的精確貨幣運算 helper，避免浮點或 32-bit 截斷。

## 審核結論

現有結構已有適合掛接的 server airspace、species、battle sequence、market lots 與 profile CAS，但敵人池、BOSS、群怪數、賞金、掉落、彈藥費與持久擊殺收據都尚未存在。最值得先解的平衡錯位是：目前風險資料只改 UI 預覽、不改戰鬥機率；遭遇以「切成幾段」而非暴露距離決定；財富尚未參與敵人強度；而每個空域的單一物種缺少玩法多樣性。新規則可按「risk × distance × wealth/ship tier」抽遭遇，按 tier+wealth 決定完整敵數，使用固定 per-kill 小額回報，並將 claim id 與資產同一次 CAS 寫入。
