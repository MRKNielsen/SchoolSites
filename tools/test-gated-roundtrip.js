// test-gated-roundtrip.js -- round-trip test for a gated page: encrypt like tools/staff-crypt.html, then run the
// page's own unlock script against a stub DOM.
// Usage: node tools/test-gated-roundtrip.js year7-science/forces/solutions.html year7-science/forces/solutions-payload.html
// Uses a throwaway password; it never reads or writes the real blob.
const fs = require('fs'), { webcrypto } = require('crypto'); const crypto = webcrypto;
const [shellPath, payloadPath] = process.argv.slice(2);
const shell = fs.readFileSync(shellPath, 'utf8'), payload = fs.readFileSync(payloadPath, 'utf8');
const b64 = a => Buffer.from(a).toString('base64');
async function derive(pw, salt, iter, use) {
  const k = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), {name: 'PBKDF2'}, false, ['deriveKey']);
  return crypto.subtle.deriveKey({name: 'PBKDF2', salt, iterations: iter, hash: 'SHA-256'}, k, {name: 'AES-GCM', length: 256}, false, [use]);
}
async function encrypt(plain, pw) {
  const raw = crypto.getRandomValues(new Uint8Array(32));
  const ck = await crypto.subtle.importKey('raw', raw, {name: 'AES-GCM'}, false, ['encrypt']);
  const piv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt({name: 'AES-GCM', iv: piv}, ck, new TextEncoder().encode(plain));
  const salt = crypto.getRandomValues(new Uint8Array(16)), kiv = crypto.getRandomValues(new Uint8Array(12));
  const wct = await crypto.subtle.encrypt({name: 'AES-GCM', iv: kiv}, await derive(pw, salt, 250000, 'encrypt'), raw);
  return 'var BLOB = ' + JSON.stringify({v: 2, iv: b64(piv), ct: b64(new Uint8Array(ct)), keys: [{role: 'staff', salt: b64(salt), iv: b64(kiv), ct: b64(new Uint8Array(wct)), iter: 250000}]}) + ';';
}
function run(script, pw) {
  const el = {}; let submit;
  const mk = id => (el[id] = el[id] || {id, textContent: '', innerHTML: '', value: '', style: {}, focus() {},
    addEventListener(ev, fn) { if (ev === 'submit') submit = fn; }});
  const document = {getElementById: mk, querySelector: () => null, body: {dataset: {}}};
  const window = {scrollTo() {}};
  new Function('document', 'window', 'crypto', 'atob', 'TextEncoder', 'TextDecoder', script)(
    document, window, crypto, s => Buffer.from(s, 'base64').toString('binary'), TextEncoder, TextDecoder);
  ['lock', 'content', 'err', 'pw'].forEach(mk); mk('pw').value = pw;
  return submit({preventDefault() {}}).then(() => el);
}
(async () => {
  const script = shell.slice(shell.lastIndexOf('<script>') + 8, shell.lastIndexOf('</script>'));
  const placeholder = /var BLOB = \{[^\n]*?\};/.exec(script)[0];
  let el = await run(script, 'anything');
  console.log('placeholder blob ->', JSON.stringify(el.err.textContent));
  const blob = await encrypt(payload, 'test-only-password');
  const s2 = script.replace(placeholder, blob);
  el = await run(s2, 'wrong');
  console.log('wrong password  ->', JSON.stringify(el.err.textContent), '| lock hidden:', el.lock.style.display === 'none');
  el = await run(s2, 'test-only-password');
  console.log('right password  -> payload identical:', el.content.innerHTML === payload, '| lock hidden:', el.lock.style.display === 'none', '| err:', JSON.stringify(el.err.textContent));
})();
