# 永久存檔 V1 接手與原生前置證據

2026-10-08；本紀錄是接手授權與 API 前置測試，不代表存檔功能已完成驗收。

主人回覆「允許接手（建議）」：允許以 Gemini 完成回執取代未放行的 `may_handoff_write` 旗標，接手已核准的存檔與船艙金額 UI。

橋接 request `gv-save-v1-20261008-writer-01`、cascade `3d670ef2-50ce-42bc-96a7-e5112d3c288b` 回報 COMPLETED／DONE、無檔案修改、`remote_may_resume=false`；原 `may_handoff_write=false` 未篡改。此例外僅適用本次接手，不形成通用繞過規則。

Maker `server_main` 實際執行隔離測試鍵 `GV_Save_V1_CASProbe_20261008_01`：

| 動作 | 原生結果 |
|---|---|
| 讀不存在鍵 | code=0、value=nil |
| Update 預期空字串，寫入 probe-v1 | code=1000002；無法建立不存在鍵 |
| Set probe-v1 | code=0 |
| Update 預期 probe-v1，寫入 probe-v2 | code=0、value=probe-v2 |
| 再用舊 probe-v1 嘗試 stale-writer | code=2000000、value=probe-v2 |
| 最後讀回 | code=0、value=probe-v2 |

既有帳號採 compare-and-set 防止舊寫入覆蓋。原生 Update 無法建立新鍵，首次建立需 Set＋exact readback；仍有跨 instance 同時首次建立的限制，單一 Maker 不足以驗證該競態。未重置任何原有玩家存檔。
