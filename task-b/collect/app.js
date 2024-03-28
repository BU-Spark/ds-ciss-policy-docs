const path = require('node:path');
const fs = require('node:fs');
const fsPromise = require('node:fs/promises');

const axios = require('axios');
const ProxyAgent = require('https-proxy-agent').HttpsProxyAgent;
const cheerio = require('cheerio');
const db = require('better-sqlite3')(path.join(__dirname, './policies.db'));

const config = require(path.join(__dirname, 'config'));

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
    let lastLogTime = Date.now();
    const dir = path.join(__dirname, '../../data/', jArea, ""+jYear);
    await fsPromise.readdir(dir).then(async files => {
        let resultStream, docsDoneCount=0;
        const reqDurations = [], reqRetryCounts = [];
        if(syncToCsv) {
            resultStream = fs.createWriteStream('./category.csv');
            writeToStream(resultStream, 'id,filename,url,type,dt\n');
        }
        const urlReg = /https:\/\/www\.pkulaw\.com\/lar\/\w+\.html/;
        for(file of files) {
            if(Date.now() - lastLogTime > 20*60*1000) {
                const avgDuration = Math.round(reqDurations.reduce((a,b)=>a+b)/reqDurations.length);
                const avgRetryCount = Math.round(reqDurations.reduce((a,b)=>a+b)/reqDurations.length);
                logWithTime(`WIP: ${jArea} ${jYear} Complete ${docsDoneCount}/${files.length} AvgDuration ${avgDuration} AvgRetry `);
                lastLogTime = Date.now();
            }
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
            if(policy && policy.filename && policy.filename === file && policy.type.split('-').length < 2) {
                docsDoneCount += 1;
                continue;
            }
            for(const line of lines) {
                if(!line.includes('原文链接')) {
                    continue;
                }
                const urls = line.match(urlReg);
                if(urls.length <= 0) {
                    continue;
                }
                let reqDuration = 0, reqRetry = false, reqRetryCount = 0;
                const now = Date.now();
                do {
                    reqRetryCount += 1;
                    await axios.get(urls[0], {
                        proxy: false,
                        httpsAgent: new ProxyAgent(`http://${config.proxyIp}:${config.proxyPort}`),
                    }).then(res => {
                        const $ = cheerio.load(res.data);
                        const fields = $('#body1').find('.fields');
                        const types = [];
                        for(const e of fields.find('li:contains("法规类别")').find('a')) {
                            types.push($(e).text());
                        }
                        const dt = fields.find('li:contains("公布日期")').find('div').text().replace("公布日期：", "");
                        if(types.length === 0 || dt.length === 0) {
                            if(fields.length === 0) {
                                reqRetry = true;
                            } else {
                                logWithTime('ERROR: one element missing', jArea, jYear, file);
                            }
                        }
                        if(!reqRetry) {
                            sqlInsertPolicy.run(id, jArea, jYear, file, urls[0], types.join(','), dt);
                            writeToStream(resultStream, `${id},${dir+file},${urls[0]},${types.join(',')}\n`);
                        }
                    }).catch(async err => {
                        // check status code
                        const errCode = err && err.response ? err.response.status : 999;
                        if(errCode === 404) {
                            logWithTime('ERROR: 404 on', jArea, jYear, file);
                            sqlInsertPolicy.run(id, jArea, jYear, file, urls[0], '404-NotFound', '');
                            writeToStream(resultStream, `${id},${dir+file},${urls[0]},404-NotFound,\n`);
                        } else if(errCode === 567) {
                            logWithTime('ERROR: 567 Request Frenquency', jArea, jYear, file);
                            sqlInsertPolicy.run(id, jArea, jYear, file, urls[0], `567-ReqFreq`, '');
                            writeToStream(resultStream, `${id},${dir+file},${urls[0]},567-ReqFreq,\n`);
                            reqRetry = true;
                        } else if (errCode === 502) {
                            reqRetry = true;
                        } else if(err.message.trim().toLowerCase() === 'proxy connection ended before receiving connect response') {
                            reqRetry = true;
                        } else {
                            logWithTime('ERROR: Unknow Error', err);
                            sqlInsertPolicy.run(id, jArea, jYear, file, urls[0], `${errCode}-Unknown`, '');
                            writeToStream(resultStream, `${id},${dir+file},${urls[0]},${errCode}-Unknown,\n`);
                        }
                    });
                    if(reqRetryCount > 4) {
                        logWithTime('ERROR: too many fails', jArea, jYear, file);
                        reqRetry = false;
                    } else if(reqRetry) {
                        await new Promise(resolve => setTimeout(resolve, 400));
                    }
                } while(reqRetry);
                reqDuration = Date.now() - now;
                reqDurations.push(reqDuration);
                reqRetryCounts.push(reqRetryCount);
                break;
            }
            docsDoneCount += 1;
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
    while(job) {
        db.prepare('UPDATE folder SET status=1 WHERE area=? AND year=?;').run(job.area, job.year);
        logWithTime('Start:', job);
        await collectData(job.area, job.year);
        db.prepare('UPDATE folder SET status=2 WHERE area=? AND year=?;').run(job.area, job.year);
        logWithTime('Done:', job);
        job = sqlJobPending.get();
        if(!job) {
            job = sqlJobQueued.get();
        }
    }
    logWithTime("EXIT LOOP");
}

main();
