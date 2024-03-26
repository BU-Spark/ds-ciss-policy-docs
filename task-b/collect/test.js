const fs = require('fs');
const path = require('node:path');
const db = require('better-sqlite3')(path.join(__dirname, './policies.db'));

const url = 'https://www.pkulaw.com/lar/07f795f96a47fd4720da2929809ece44bdfb.html';

// axios.get(url).then(res => {
//     fs.writeFileSync('pkulaw.html', res.data);
// });

// const html = fs.readFileSync('pkulaw.html', 'utf-8');
// const $ = cheerio.load(html);
// const fields = $('.fields');
// const li = fields.find('li:contains("法规类别")');
// const result = li.find('a').text();
// console.log(result);
const a = [];
a.push(8);
a.push(4);
a.push(6);
a.push(3);
console.log(a, a.length, a.reduce((a,b)=>a+b));
