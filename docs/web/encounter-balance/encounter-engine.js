(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.GVEncounter = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const bands = ['low', 'mid', 'high'];
  function amount(value, name) {
    if (!Number.isSafeInteger(value) || value < 0) throw new Error(name + '須為非負安全整數');
    return value;
  }
  function factor(sum) { return Math.max(0.1, 1 + sum); }
  function encounterLevel(monster) {
    const custom = monster.balanceOverride;
    return custom && custom.authority === 'user' && Number.isSafeInteger(custom.level)
      ? custom.level : monster.originalLevel;
  }
  function prepare(data, input) {
    const ship = data.ships.find(s => s.tier === input.tier);
    if (!ship) throw new Error('船級必須為 T0～T5');
    const cargoValue = amount(input.cargoValue, '貨物估值');
    const temptation = input.temptation;
    if (!Number.isFinite(temptation) || temptation < 0 || temptation > 100) throw new Error('誘惑度須在 0～100');
    if (!data.areas.some(a => a.id === input.area)) throw new Error('未知空域');
    if (!Array.isArray(input.cards) || input.cards.length > 3) throw new Error('目前只支援三個通用槽');
    const sums = { general: 0, fog: 0, wildlife: 0, magic: 0 };
    for (const id of input.cards) {
      if (!id) continue;
      const card = data.cards.find(c => c.id === id);
      if (!card) throw new Error('未知遭遇卡：' + id);
      sums[card.channel] += card.delta;
    }
    const general = factor(sums.general) * (input.fogActive ? factor(sums.fog) : 1);
    const pressure = Math.log2(1 + cargoValue / ship.cargoReference);
    const attraction = 1 + temptation / 100;
    // 先硬過濾，再做權重；財富、誘惑、卡片及全空域池都不能越級。
    const allowed = data.monsters.filter(m => m.enabled && Number.isInteger(encounterLevel(m))
      && encounterLevel(m) >= 1 && encounterLevel(m) <= ship.maxLevel
      && (m.area === input.area || m.area === '__allair'));
    const weighted = [];
    const shift = 1 + pressure * 0.1 + temptation / 200;
    for (let i = 0; i < bands.length; i++) {
      const band = bands[i];
      if (ship.weights[i] <= 0) continue;
      const local = allowed.filter(m => m.band === band && m.area === input.area);
      const shared = allowed.filter(m => m.band === band && m.area === '__allair');
      const bandWeight = ship.weights[i] * Math.pow(shift, i);
      for (const group of [{ list: local, share: shared.length ? data.localShare : 1 },
        { list: shared, share: local.length ? data.sharedShare : 1 }]) {
        if (!group.list.length) continue;
        for (const monster of group.list) weighted.push({ monster,
          baseWeight: bandWeight * group.share / group.list.length,
          familyFactor: factor(sums[monster.family] || 0) });
      }
    }
    const baseTotal = weighted.reduce((sum, r) => sum + r.baseWeight, 0);
    const modifiedTotal = weighted.reduce((sum, r) => sum + r.baseWeight * r.familyFactor, 0);
    const familyMean = baseTotal ? modifiedTotal / baseTotal : 1;
    const cardFactor = general * familyMean;
    const hazard = (1 + pressure * 0.35) * attraction * cardFactor;
    const chance = weighted.length ? Math.min(0.95, 1 - Math.pow(1 - ship.chance, hazard)) : 0;
    const countFactor = (1 + pressure * 0.35) * (1 + temptation / 200) * Math.sqrt(cardFactor);
    const minimum = weighted.length ? Math.max(1, Math.floor(ship.count[0] * countFactor)) : 0;
    const maximum = weighted.length ? Math.max(minimum, Math.ceil(ship.count[1] * countFactor)) : 0;
    const probabilities = weighted.map(r => ({ ...r.monster, encounterLevel: encounterLevel(r.monster),
      probability: r.baseWeight * r.familyFactor / modifiedTotal }));
    const difficulty = Object.fromEntries(bands.map(b => [b, probabilities.filter(m => m.band === b)
      .reduce((sum, m) => sum + m.probability, 0)]));
    return { tier: ship.tier, maxLevel: ship.maxLevel, area: input.area, cargoValue, pressure,
      temptation, cardFactor, chance, minimum, maximum, onScreen: ship.onScreen,
      expectedCount: chance * (minimum + maximum) / 2, difficulty, probabilities,
      warning: weighted.length ? '' : '沒有符合船級的當地或全空域怪物，本次不生成。' };
  }
  function randomValue(random) {
    const value = random();
    if (!Number.isFinite(value) || value < 0 || value >= 1) throw new Error('亂數須在 [0,1)');
    return value;
  }
  function drawEnemy(prepared, random) {
    const roll = randomValue(random);
    let cumulative = 0;
    for (const monster of prepared.probabilities) {
      cumulative += monster.probability;
      if (roll < cumulative) return monster;
    }
    return prepared.probabilities[prepared.probabilities.length - 1];
  }
  function sample(prepared, random) {
    if (!prepared.probabilities.length || randomValue(random) >= prepared.chance) return { total: 0, active: [], queued: [] };
    const count = prepared.minimum + Math.floor(randomValue(random) * (prepared.maximum - prepared.minimum + 1));
    const enemies = Array.from({ length: count }, () => drawEnemy(prepared, random));
    return { total: count, active: enemies.slice(0, prepared.onScreen), queued: enemies.slice(prepared.onScreen) };
  }
  function seededRandom(seed) {
    let state = seed >>> 0;
    return function () {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ value >>> 15, value | 1);
      value ^= value + Math.imul(value ^ value >>> 7, value | 61);
      return ((value ^ value >>> 14) >>> 0) / 4294967296;
    };
  }
  return { prepare, sample, seededRandom };
});
