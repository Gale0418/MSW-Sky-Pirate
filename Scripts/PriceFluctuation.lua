-- PriceFluctuation.lua
-- 負責處理物價浮動邏輯

local PriceFluctuation = {}

-- 根據庫存量來影響價格 (供需法則)
-- amount 越多，價格越低；amount 越少，價格越高
function PriceFluctuation:CalculatePrice(basePrice, amount)
    local priceModifier = 1.0
    
    if amount < 100 then
        priceModifier = 1.5
    elseif amount < 500 then
        priceModifier = 1.2
    elseif amount > 4000 then
        priceModifier = 0.5
    elseif amount > 2000 then
        priceModifier = 0.8
    end
    
    -- 加入隨機波動 (-5% ~ 5%) 讓市場看起來更活
    local randomMod = 1 + (math.random(-5, 5) / 100)
    
    local finalPrice = math.floor(basePrice * priceModifier * randomMod)
    return math.max(1, finalPrice) -- 確保價格不低於 1
end

-- 更新所有城市的物價
function PriceFluctuation:UpdateAllPrices(cityTradeManager)
    for cityName, cityData in pairs(cityTradeManager.Cities) do
        for itemName, itemData in pairs(cityData.inventory) do
            itemData.currentPrice = self:CalculatePrice(itemData.basePrice, itemData.amount)
        end
    end
end

return PriceFluctuation
