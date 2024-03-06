const fs = require('fs');
const axios = require('axios');
const cheerio = require('cheerio');

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

console.log(__dirname);
