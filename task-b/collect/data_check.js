const path = require('node:path');
const fs = require('node:fs/promises');

const db = require('better-sqlite3')(path.join(__dirname, 'policies.db'));

const dirData = path.join(__dirname, '../../data');

db.prepare('CREATE INDEX IF NOT EXISTS idx_category_id ON category(id);').run();
db.prepare('CREATE INDEX IF NOT EXISTS idx_category_area ON category(area);').run();
db.prepare('CREATE INDEX IF NOT EXISTS idx_category_filename ON category(filename);').run();

async function checkAllStats() {
    let countMissingLabel = 0, countMissingDT = 0, count404 = 0, countDocs = 0;
    const sqlQueryFolder = db.prepare(`SELECT * FROM folder WHERE area=? and year=?;`);
    const sqlCountFolderLabel = db.prepare(`SELECT count(1) AS cnt FROM category WHERE area=? and year=? and type=?;`);
    const sqlCountFolderDT = db.prepare(`SELECT count(1) AS cnt FROM category WHERE area=? and year=? and dt=?;`);
    await fs.readdir(dirData, { withFileTypes: true }).then(async dirents1 => {
        const regions = dirents1.filter(dirent => dirent.isDirectory()).map(dirent => dirent.name);
        for(region of regions) {
            let countMissingLabelRegion = 0, countMissingDTRegion = 0, count404Region = 0, countDocRegion = 0;
            await fs.readdir(path.join(dirData, region), { withFileTypes: true }).then(async dirents2 => {
                const years = dirents2.filter(dirent => dirent.isDirectory()).map(dirent => dirent.name);
                for(year of years) {
                    if(sqlQueryFolder.all(region, year).length !== 1) {
                        console.warn(`WARNING: ${region} ${year} INCONSISTENT WITH DATABASE\n`);
                    }
                    await fs.readdir(path.join(dirData, region, year)).then(async files => {
                        countDocRegion += files.filter(x => x.endsWith('.txt')).length;
                        countMissingLabelRegion += sqlCountFolderLabel.get(region, year, '').cnt;
                        countMissingDTRegion += sqlCountFolderDT.get(region, year, '').cnt;
                        count404Region += sqlCountFolderLabel.get(region, year, '404-NotFound').cnt;
                    });
                }
            });
            console.log(`${region} has ${countDocRegion} txt documents. Request 404: ${count404Region}. Missing label: ${countMissingLabelRegion}. Missing DT: ${countMissingDTRegion}.`);
            countDocs += countDocRegion;
            countMissingLabel += countMissingLabelRegion;
            countMissingDT += countMissingDTRegion;
            count404 += count404Region;
        }
    });
    console.log(`\nTotal ${countDocs} txt documents. Request 404: ${count404} ~${Math.round(1000*count404/countDocs)/10}%. Missing label: ${countMissingLabel}  ~${Math.round(1000*countMissingLabel/countDocs)/10}%. Missing DT: ${countMissingDT}  ~${Math.round(1000*countMissingDT/countDocs)/10}%.`);
}

async function checkRegion() {
    let countMissingLabel = 0, countMissingDT = 0, count404 = 0, countRecords, countDocs;
    const region = process.argv[2];
    const sqlQueryFile = db.prepare(`SELECT * FROM category WHERE area=? and year=?;`);
    await fs.readdir(path.join(dirData, region), { withFileTypes: true }).then(async dirents => {
        const years = dirents.filter(dirent => dirent.isDirectory()).map(dirent => dirent.name);
        for(year of years) {
            await fs.readdir(path.join(dirData, region, year)).then(async files => {
                files = files.filter(x => x.endsWith('.txt'));
                countDocs = files.length;
                const records = sqlQueryFile.all(region, year);
                countRecords = records.length;
                for(file of files) {
                    const record = records.filter(x => x.filename === file);
                    if(record.length === 0) {
                        console.log(`${region} ${year} ${file} Document Missing`);
                    } else if(record.length > 1) {
                        console.warn(`WARNING: ${region} ${year} ${file} INCONSISTENT WITH DATABASE\n`);
                    } else {
                        if(record[0].type === '404-NotFound') {
                            count404++;
                            console.log(`${region} ${year} ${file} 404 Not Found`);
                        } else {
                            let missingLabel = false, missingDT = false;
                            if(record[0].type === '') {
                                countMissingLabel++;
                                missingLabel = true;
                            }
                            if(record[0].dt === '') {
                                countMissingDT++;
                                missingDT = true;
                            }
                            if(missingLabel && missingDT) {
                                console.log(`${region} ${year} ${file} Missing Label and DT`);
                            } else if(missingLabel || missingDT) {
                                console.log(`${region} ${year} ${file} Missing ${missingLabel ? 'Label' : 'DT'}`);
                            }
                        }
                    }
                }
            });
        }
    });
    console.log(`\n${region} has ${countDocs} txt documents. Pulled ${countRecords} records. Request 404: ${count404}. Missing label: ${countMissingLabel}. Missing DT: ${countMissingDT}.\n`);
}

if(process.argv.length !== 3) {
    console.error('Usage: node data_check.js all|<region>');
    process.exit(1);
} else {
    if(process.argv[2] === 'all') {
        checkAllStats();
    } else {
        checkRegion();
    }
}
