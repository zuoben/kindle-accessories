import fs from 'node:fs';
const pages = ['kindle-paperwhite', 'kindle-case', 'kindle-paperwhite-case', 'faq', 'about', 'privacy', 'contact', 'affiliate-disclosure'];
for (const p of pages) {
  const html = fs.readFileSync(`dist/${p}/index.html`, 'utf8');
  const main = html.match(/<main[\s\S]*?<\/main>/)[0].replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<svg[\s\S]*?<\/svg>/g, ' ').replace(/<[^>]+>/g, ' ');
  console.log(p.padEnd(22), main.split(/\s+/).filter(Boolean).length, 'words');
}
