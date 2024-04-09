const path = require('node:path');
const db = require('better-sqlite3')(path.join(__dirname, './policies.db'));

const createTableFolder = `
    CREATE TABLE IF NOT EXISTS folder(
        area STRING,
        year INTEGER,
        status INTEGER,      -- 0: queued, 1: pending, 2: completed; for dual 10: queued, 11: pending
        UNIQUE(area, year) ON CONFLICT IGNORE
    );`;
db.exec(createTableFolder);

const createTableCate = `
    CREATE TABLE IF NOT EXISTS category(
        id STRING,
        area STRING,
        year INTEGER,
        filename STRING,
        url STRING,
        type STRING,
        dt STRING,
        UNIQUE(id, area, year) ON CONFLICT IGNORE
    );`;
db.exec(createTableCate);

if(process.argv.length < 5) {
    console.error('Usage: node manage.js add|remove <folder> <year>');
    process.exit(1);
}
if(process.argv[2] === 'add') {
    const result = db.prepare('INSERT INTO folder VALUES(?, ?, 0);').run(process.argv[3], process.argv[4]);
    if(result.changes === 0) {
        console.error('Folder Conflict:', result);
    } else {
        console.log('Success');
    }
} else if(process.argv[2] === 'remove') {
    const result = db.prepare('DELETE FROM folder WHERE area=? AND year=?;').run(process.argv[3], process.argv[4]);
    if(result.changes === 0) {
        console.error('Folder Not Found:', result);
    } else {
        console.log('Success');
    }
} else {
    console.error('Usage: node manage.js add|remove <folder> <year>');
    process.exit(1);
}
