'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const engine = require('./encounter-engine.js');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'encounter-balance.json'), 'utf8'));
const source = JSON.parse(fs.readFileSync(path.join(__dirname, 'encounter-source-classification.json'), 'utf8'));
assert.deepEqual(data.classificationAssignments, source.assignments);
assert.equal(Object.keys(source.assignments).length, 300);
assert.equal(data.monsters.length, 132);
assert.equal(data.monsters.filter(m => m.enabled).length, 129);
for (const m of data.monsters) {
  assert.equal(m.area, source.assignments[m.packId]);
  assert.ok(!['__noair', '__outside', '__unassigned'].includes(m.area));
  assert.ok(fs.existsSync(path.join(__dirname, m.thumbnail)));
  const override = m.balanceOverride;
  const effectiveLevel = override && override.authority === 'user' && Number.isInteger(override.level) && override.level >= 1
    ? override.level : m.originalLevel;
  const expectedHp = Number.isInteger(effectiveLevel) && effectiveLevel >= 1
    ? Math.max(12, Math.min(3000, Math.floor(120 * (effectiveLevel / 28) ** 1.35 + 0.5))) : 0;
  const expectedAttack = Number.isInteger(effectiveLevel) && effectiveLevel >= 1
    ? Math.max(2, Math.min(240, Math.floor(12 * (effectiveLevel / 28) ** 1.15 + 0.5))) : 0;
  const expectedBounty = !Number.isInteger(effectiveLevel) || effectiveLevel < 1 ? 0
    : effectiveLevel <= 30 ? 100 : effectiveLevel <= 50 ? 500
      : effectiveLevel <= 100 ? 2500 : effectiveLevel <= 150 ? 10000 : 40000;
  assert.equal(m.combatStats.effectiveLevel, Number.isInteger(effectiveLevel) ? effectiveLevel : null);
  assert.equal(m.hp, expectedHp);
  assert.equal(m.attack, expectedAttack);
  assert.equal(m.attackInterval, 2);
  assert.equal(m.bounty, expectedBounty);
  assert.equal(m.maxHp, m.hp);
  assert.equal(m.attackDamage, m.attack);
  assert.equal(m.attackIntervalSeconds, m.attackInterval);
}
const badda = data.monsters.find(m => m.packId === 'mob/8642102.img');
const bubble = data.monsters.find(m => m.packId === 'mob/2230109.img');
assert.equal(badda.originalLevel, null);
assert.equal(badda.referenceLevel, null);
assert.equal(badda.balanceOverride.authority, 'user');
assert.equal(badda.balanceOverride.level, bubble.originalLevel);
assert.equal(badda.band, bubble.band);
assert.equal(badda.area, '__allair');
assert.equal(data.monsters.filter(m => m.balanceOverride).length, 1);
const cargoLevels = [0, 12000, 50000, 500000, 5000000, 200000000, 2147483647, 9999999999];
const cardSets = [[], ['lure'], ['stealth'], ['fog'], ['monster_bait'], ['magic_resonator'],
  ['stealth', 'stealth', 'stealth'], ['lure', 'lure', 'lure'], ['monster_bait', 'magic_resonator', 'lure']];
let cases = 0, samples = 0;
for (const area of data.areas.map(a => a.id)) for (let tier = 0; tier <= 5; tier++) {
  const base = { area, tier, cargoValue: 0, temptation: 0, cards: [], fogActive: true };
  const normal = engine.prepare(data, base);
  const cuteFish = normal.probabilities.find(m => m.packId === badda.packId);
  assert.ok(cuteFish && cuteFish.encounterLevel === 28 && cuteFish.originalLevel === null);
  assert.equal(cuteFish.probability, normal.probabilities.find(m => m.packId === bubble.packId).probability);
  const rich = engine.prepare(data, { ...base, cargoValue: 2147483647, temptation: 100 });
  const hidden = engine.prepare(data, { ...base, cards: ['stealth'] });
  const lure = engine.prepare(data, { ...base, cards: ['lure'] });
  assert.ok(hidden.chance <= normal.chance + 1e-12);
  assert.ok(hidden.expectedCount <= normal.expectedCount + 1e-12);
  assert.ok(lure.chance >= normal.chance - 1e-12);
  assert.ok(lure.expectedCount >= normal.expectedCount - 1e-12);
  assert.ok(rich.chance >= normal.chance - 1e-12);
  if (tier === 1) assert.equal(rich.difficulty.mid + rich.difficulty.high, 0);
  const lastCounts = new Map();
  for (const cards of cardSets) for (const temptation of [0, 25, 50, 100]) {
    let previous = null;
    for (const cargoValue of cargoLevels) {
      const p = engine.prepare(data, { ...base, cards, temptation, cargoValue });
      cases++;
      assert.ok(p.chance >= 0 && p.chance <= .95);
      assert.ok(Number.isSafeInteger(p.minimum) && Number.isSafeInteger(p.maximum));
      assert.ok(p.minimum >= 0 && p.maximum >= p.minimum);
      const sum = p.probabilities.reduce((a, m) => a + m.probability, 0);
      assert.ok(Math.abs(sum - (p.probabilities.length ? 1 : 0)) < 1e-10);
      for (const m of p.probabilities) {
        assert.ok(m.enabled && Number.isInteger(m.encounterLevel));
        assert.ok(m.encounterLevel <= data.ships[tier].maxLevel);
        assert.ok(m.area === area || m.area === '__allair');
        assert.ok(m.probability > 0 && m.probability <= 1 + 1e-10);
      }
      if (previous) {
        assert.ok(p.chance >= previous.chance - 1e-12, 'cargo chance monotonic ' + JSON.stringify({ tier, area, cards, temptation, cargoValue }));
        assert.ok(p.minimum >= previous.minimum && p.maximum >= previous.maximum, 'cargo count monotonic');
      }
      const key = cards.join(',') + ':' + cargoValue;
      const before = lastCounts.get(key);
      if (before) {
        assert.ok(p.chance >= before.chance - 1e-12, 'temptation chance monotonic');
        assert.ok(p.minimum >= before.minimum && p.maximum >= before.maximum, 'temptation count monotonic');
      }
      lastCounts.set(key, p);
      previous = p;
    }
  }
  const random = engine.seededRandom(1234);
  for (let i = 0; i < 1000; i++) {
    const wave = engine.sample(rich, random);
    samples++;
    assert.equal(wave.total, wave.active.length + wave.queued.length);
    assert.ok(wave.active.length <= rich.onScreen);
    for (const m of [...wave.active, ...wave.queued]) assert.ok(m.encounterLevel <= rich.maxLevel);
  }
}
const baseline = { area: 'victoria', tier: 1, cargoValue: 0, temptation: 0, cards: [], fogActive: false };
assert.equal(engine.prepare(data, { ...baseline, cards: ['lure', 'lure', 'lure'] }).cardFactor, 2.5);
assert.equal(engine.prepare(data, { ...baseline, cards: ['stealth', 'stealth', 'stealth'] }).cardFactor, .1);
assert.equal(engine.prepare(data, { ...baseline, cash: 50000 }).chance,
  engine.prepare(data, baseline).chance);
assert.ok(engine.prepare(data, { ...baseline, cargoValue: 50000 }).chance > engine.prepare(data, baseline).chance);
const empty = engine.prepare({ ...data, monsters: [] }, baseline);
assert.equal(empty.chance, 0);
assert.deepEqual(engine.sample(empty, engine.seededRandom(1)), { total: 0, active: [], queued: [] });
const injected = { ...data, monsters: data.monsters.concat([{ ...data.monsters[0],
  packId: 'unknown-test', area: '__allair', enabled: true, originalLevel: null }]) };
assert.ok(!engine.prepare(injected, baseline).probabilities.some(m => m.packId === 'unknown-test'));
for (const override of [{ level: 28, authority: 'source' }, { level: NaN, authority: 'user' }, { level: -1, authority: 'user' }]) {
  const testData = { ...data, monsters: [{ ...badda, balanceOverride: override }] };
  assert.equal(engine.prepare(testData, baseline).probabilities.length, 0);
}
for (const bad of [{ tier: 6 }, { cargoValue: -1 }, { cargoValue: NaN }, { cargoValue: Infinity }, { temptation: 101 }, { cards: ['bad'] },
  { cards: ['lure', 'lure', 'lure', 'lure'] }, { area: 'bad' }]) assert.throws(() => engine.prepare(data, { ...baseline, ...bad }));
// Monte Carlo checks verify the expected distribution, beyond checking the formula against itself.
const model = engine.prepare(data, { ...baseline, tier: 5, area: 'ludus', cargoValue: 200000000, temptation: 35 });
const rng = engine.seededRandom(20261011);
let encounters = 0, total = 0;
const counts = { low: 0, mid: 0, high: 0 };
for (let i = 0; i < 20000; i++) {
  const wave = engine.sample(model, rng);
  if (wave.total) encounters++;
  total += wave.total;
  for (const m of [...wave.active, ...wave.queued]) counts[m.band]++;
}
assert.ok(Math.abs(encounters / 20000 - model.chance) < .02);
assert.ok(Math.abs(total / 20000 - model.expectedCount) < .15);
for (const band of ['low', 'mid', 'high']) assert.ok(Math.abs(counts[band] / total - model.difficulty[band]) < .02);
const html = fs.readFileSync(path.join(__dirname, 'encounter-balance.html'), 'utf8');
const embedded = JSON.parse(html.match(/id="balance-data">([\s\S]*?)<\/script>/)[1]);
assert.deepEqual(embedded, data);
assert.ok(!html.includes('id="cash"'));
assert.ok(!html.includes('現金＋'));
assert.equal(engine.prepare(data, { ...baseline, cash: 999999999, cargoValue: 0 }).chance,
  engine.prepare(data, { ...baseline, cargoValue: 0 }).chance);
assert.ok(!html.includes('__BALANCE_DATA__'));
for (const file of ['encounter-engine.js', 'encounter-review.js']) new (require('node:vm').Script)(fs.readFileSync(path.join(__dirname, file), 'utf8'));
const result = { status: 'PASS', cases, randomSamples: samples + 20000,
  userOverride: { name: badda.name, originalLevel: badda.originalLevel, encounterLevel: badda.balanceOverride.level, area: badda.area },
  adopted: 132, ready: 129, sourceAssignments: 300, excluded: 168,
  monteCarlo: { expectedChance: model.chance, observedChance: encounters / 20000,
    expectedCount: model.expectedCount, observedCount: total / 20000 },
  scope: 'Offline algorithm and embedded data; no MSW runtime verification.' };
fs.writeFileSync(path.join(__dirname, 'encounter-verification.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
