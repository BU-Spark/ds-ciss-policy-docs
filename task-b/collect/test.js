const fs = require('fs');
const path = require('node:path');

const axios = require('axios');
const cheerio = require('cheerio');
const ProxyAgent = require('https-proxy-agent').HttpsProxyAgent;
const db = require('better-sqlite3')(path.join(__dirname, './policies.db'));

const config = require(path.join(__dirname, 'config'));

const url = 'https://www.pkulaw.com/lar/07f795f96a47fd4720da2929809ece44bdfb.html';
const proxyRotate = new ProxyAgent(`http://${config.proxyIp}:${config.proxyPort}`);

// for(const i of [1]) {
//     axios.get(url, {
//         proxy: false,
//         httpsAgent: proxyRotate,
//     }).then(res => {
//         // fs.writeFileSync('pkulaw1.html', res.data);
//         const $ = cheerio.load(res.data);
//         const fields = $('#body1').find('.fields');
//         let elements = [];
//         for(const e of fields.find('li:contains("法规类别")').find('a')) {
//             elements.push($(e).text());
//         }
//         console.log(elements, elements.join(','));
//     }).catch(err => {
//         console.log(i, (err && err.response ? err.response.status : err));
//     });
// }

// const $ = cheerio.load(fs.readFileSync('pkulaw0.html', 'utf-8'));
// const fields = $('#body1').find('.fields');
// let elements = [];
// for(const e of fields.find('li:contains("法规类别")').find('a')) {
//     elements.push($(e).text());
// }
// const dt = fields.find('li:contains("公布日期")').find('div').text().replace("公布日期：", "");
// console.log(fields.length, elements, elements.join(','), dt);

// console.log(db.exec('SELECT COUNT(CASE type WHEN "" THEN 1 ELSE NULL END) AS no_type, COUNT(CASE dt WHEN "" THEN 1 ELSE NULL END) AS no_dt, COUNT(1) AS count_all FROM category WHERE area="GuangXi" and year=2021;'));
console.log(db.prepare('SELECT COUNT(CASE type WHEN \'\' THEN 1 ELSE NULL END) AS no_type, COUNT(CASE dt WHEN \'\' THEN 1 ELSE NULL END) AS no_dt, COUNT(1) AS count_all FROM category WHERE area=? and year=?;').get('GuangXi', 2021));
