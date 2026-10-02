import sharp from 'sharp';
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#faf6ee"/>
<rect x="80" y="90" width="230" height="450" rx="26" fill="#1d1b18"/>
<rect x="104" y="116" width="182" height="340" rx="8" fill="#faf6ee"/>
<g stroke="#bdb39d" stroke-width="6" stroke-linecap="round"><path d="M124 156h140M124 184h120M124 212h140M124 240h100M124 268h140M124 296h110"/></g>
<path d="M286 90v110l-34-24-34 24V90z" fill="#9a3b1f" transform="translate(-6 0)"/>
<text x="380" y="270" font-family="Georgia, serif" font-size="104" font-weight="700" fill="#1d1b18">Dogear</text>
<text x="384" y="340" font-family="Georgia, serif" font-size="40" fill="#4a453d">Independent Kindle buying guides</text>
<text x="384" y="420" font-family="Arial, sans-serif" font-size="30" fill="#9a3b1f">Kindle Paperwhite  ·  Kindle cases</text>
</svg>`;
await sharp(Buffer.from(svg)).png().toFile('public/og-default.png');
console.log('og ok');
