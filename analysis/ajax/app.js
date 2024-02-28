const fs = require('fs');
const axios = require('axios');
const cheerio = require('cheerio');
const db = require('better-sqlite3')('./policies.db');

const dir = '../../data/shanghai/2022/';
const queryPolicy = db.prepare('SELECT filename FROM category WHERE id = ?;');
const insertPolicy = db.prepare('INSERT OR IGNORE INTO category VALUES(?,?,?,?);');

fs.readdir(dir, async (err, files) => {
    if(err) {
        console.log(err);
        return;
    }
    const resultStream = fs.createWriteStream('./category.csv');
    resultStream.write('id,filename,url,type\n');
    const urlReg = /https:\/\/www\.pkulaw\.com\/lar\/\w+\.html/;
    for(file of files) {
        const data = fs.readFileSync(`../../data/shanghai/2022/${file}`, 'utf-8');
        const lines = data.split('\n');
        let id = '';
        for(line of lines) {
            if(line.includes('【法宝引证码】')) {
                const contents = line.split('【法宝引证码】');
                if(contents.length > 1) {
                    id = contents[1].trim();
                    break;
                }
            }
        }
        const policy = queryPolicy.get(id);
        if(policy != undefined && policy.filename === dir+file) {
            continue;
        }
        let reqTime = 0;
        for(const line of lines) {
            if(line.includes('原文链接')) {
                const urls = line.match(urlReg);
                if(urls.length > 0) {
                    const now = Date.now();
                    await axios.get(urls[0]).then(res => {
                        const $ = cheerio.load(res.data);
                        const fields = $('.fields');
                        const li = fields.find('li:contains("法规类别")');
                        const type = li.find('a').text();
                        insertPolicy.run(id, dir+file, urls[0], type);
                        resultStream.write(`${id},${dir+file},${urls[0]},${type}\n`);
                    }).catch(err => {
                        // check status code
                        if(err.response.status === 404) {
                            insertPolicy.run(id, dir+file, urls[0], '404-NotFound');
                            resultStream.write(`${id},${dir+file},${urls[0]},404-NotFound\n`);
                        } else {
                            console.log(err.response);
                            insertPolicy.run(id, dir+file, urls[0], `${err.response.status}-Unknown`);
                            resultStream.write(`${id},${dir+file},${urls[0]},${err.response.status}-Unknown\n`);
                        }
                    });
                    reqTime = Date.now() - now;
                    console.log(`Request Time: ${reqTime}ms`);
                }
            }
            await new Promise(resolve => setTimeout(resolve, Math.max(20, Math.ceil(400 - (reqTime / 2)))));
        }
    }
});
