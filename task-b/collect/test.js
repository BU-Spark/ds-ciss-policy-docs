const fs = require('fs');
const path = require('node:path');
const axios = require('axios');
const cheerio = require('cheerio');
const db = require('better-sqlite3')(path.join(__dirname, './policies.db'));

const url = 'https://www.pkulaw.com/lar/07f795f96a47fd4720da2929809ece44bdfb.html';

// axios.get(url).then(res => {
//     fs.writeFileSync('pkulaw1.html', res.data);
// });

const $ = cheerio.load(fs.readFileSync('pkulaw1.html', 'utf-8'));
console.log($('#body1'));
// console.log($('.fields').contents())
// const fields = $('.fields');
// const type = fields.find('li:contains("法规类别")').find('a').text();
// const dt = fields.find('li:contains("公布日期")').find('div').text().replace("公布日期：", "");
