const path = require('node:path');
const fs = require('node:fs');
const fsPromise = require('node:fs/promises');
const axios = require('axios');
const cheerio = require('cheerio');
const db = require('better-sqlite3')(path.join(__dirname, './policies.db'));

const sqlQueryPolicy = db.prepare('SELECT filename, type FROM category WHERE id=? and area=? and year=?;');
const sqlInsertPolicy = db.prepare('INSERT OR IGNORE INTO category VALUES(?,?,?,?,?,?,?);');

const syncToCsv = false;

async function writeToStream(stream, str) {
    if(syncToCsv) {
        stream.write(str);
    }
}

async function logWithTime(...args) {
    console.log(new Date().toISOString().slice(0,-5), ...args)
}

// async function collectData(folder) {
async function collectData(jArea, jYear) {
    const dir = path.join(__dirname, '../../data/', jArea, ""+jYear);
    await fsPromise.readdir(dir).then(async files => {
        const resultStream = fs.createWriteStream('./category.csv');
        writeToStream(resultStream, 'id,filename,url,type,dt\n');
        const urlReg = /https:\/\/www\.pkulaw\.com\/lar\/\w+\.html/;
        for(file of files) {
            const data = fs.readFileSync(path.join(dir, file), 'utf-8');
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
            const policy = sqlQueryPolicy.get(id, jArea, jYear);
            if(policy != undefined && policy.filename === file && isNaN(policy.type.split('-')[0])) {
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
                            const type = fields.find('li:contains("法规类别")').find('a').text();
                            const dt = fields.find('li:contains("公布日期")').find('div').text().replace("公布日期：", "");
                            sqlInsertPolicy.run(id, jArea, jYear, file, urls[0], type, dt);
                            writeToStream(resultStream, `${id},${dir+file},${urls[0]},${type}\n`);
                        }).catch(err => {
                            // check status code
                            if(err.response.status === 404) {
                                sqlInsertPolicy.run(id, jArea, jYear, file, urls[0], '404-NotFound', '');
                                writeToStream(resultStream, `${id},${dir+file},${urls[0]},404-NotFound,\n`);
                            } else {
                                logWithTime(err.response);
                                sqlInsertPolicy.run(id, jArea, jYear, file, urls[0], `${err.response.status}-Unknown`, '');
                                writeToStream(resultStream, `${id},${dir+file},${urls[0]},${err.response.status}-Unknown,\n`);
                            }
                        });
                        reqTime = Date.now() - now;
                    }
                }
                await new Promise(resolve => setTimeout(resolve, Math.max(20, Math.ceil(400 - (reqTime / 2)))));
            }
        }
    });
}

async function main() {
    const sqlJobPending = db.prepare('SELECT area, year FROM folder WHERE status=1;');
    const sqlJobQueued = db.prepare('SELECT area, year FROM folder WHERE status=0;');
    let job = sqlJobPending.get();
    if(!job) {
        job = sqlJobQueued.get();
    }
    do {
        db.prepare('UPDATE folder SET status=1 WHERE area=? AND year=?;').run(job.area, job.year);
        logWithTime('WIP: ', job);
        await collectData(job.area, job.year);
        db.prepare('UPDATE folder SET status=2 WHERE area=? AND year=?;').run(job.area, job.year);
        logWithTime('Complete Job:', job.area, job.year);
        job = sqlJobPending.get();
        if(!job) {
            job = sqlJobQueued.get();
        }
    } while(job);
    logWithTime("EXIT LOOP");
}

main();
