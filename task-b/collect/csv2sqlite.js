const fs = require('fs');
const db = require('better-sqlite3')('./policies.db');

const createTable = `
    CREATE TABLE IF NOT EXISTS category(
        id STRING UNIQUE PRIMARY KEY,
        filename STRING,
        url STRING,
        type STRING
    );`;
db.exec(createTable);

// read category.csv and store all records to database
const data = fs.readFileSync('./category-bkp.csv', 'utf-8');
const lines = data.split('\n').slice(1);
const insert = db.prepare('INSERT OR IGNORE INTO category VALUES(?, ?, ?, ?);');
for(line of lines) {
    const fields = line.split(',');
    if(fields.length === 4) {
        insert.run(fields[0], fields[1], fields[2], fields[3]);
    }
}
