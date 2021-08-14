const mysql = require('mysql');
const express = require('express')
require('dotenv').config()

const { toJson, timeConverter, flagsString, toSteamID64} = require('./utils')

const con = mysql.createConnection({
  host: process.env.HOST,
  user: process.env.USER,
  password: process.env.PASSWORD,
  database: process.env.DATABASE
});

const server = {
   awp: "46.174.49.54:27229",
   public: "185.137.235.41:27015",
   arena: "46.174.48.105:27015"
}
// const querryTotal = `SELECT steamid, name, GROUP_CONCAT(DISTINCT name SEPARATOR '\n') AS names, SUM(end - start) AS total, COUNT(*) AS sessions, GROUP_CONCAT(DISTINCT flags SEPARATOR '\n') AS flags FROM \`playtime_tracker\`  GROUP BY steamid ORDER BY total DESC LIMIT 5`



const app = express()
const port = 80

app.set('view engine', 'ejs')

app.get('/search', (req, res) => {

   if(!req.query.steamid)
   res.render('search')

   if(req.query.steamid){
      
   const reqSteamid = req.query.steamid.replace('STEAM_0', 'STEAM_1')
   
   let querryT = `SELECT steamid, name, GROUP_CONCAT(DISTINCT name SEPARATOR ' | ') AS names, SUM(end - start) AS total, COUNT(*) AS sessions, GROUP_CONCAT(DISTINCT flags SEPARATOR '|') AS flags FROM \`playtime_tracker\` WHERE steamid = "${reqSteamid}"`
   let querryD = `SELECT SUM(end - start) AS totalDay FROM \`playtime_tracker\` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP , INTERVAL 1 DAY)) AND steamid = "${reqSteamid}"`
   let querryW = `SELECT SUM(end - start) AS totalWeek FROM \`playtime_tracker\` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP , INTERVAL 1 WEEK)) AND steamid = "${reqSteamid}"`
   let querryM = `SELECT SUM(end - start) AS totalMonth FROM \`playtime_tracker\` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP , INTERVAL 1 MONTH)) AND steamid = "${reqSteamid}"`
   
   if(req.query.server){
         querryT += ` AND serverip="${server[req.query.server]}"`
         querryD += ` AND serverip="${server[req.query.server]}"`
         querryW += ` AND serverip="${server[req.query.server]}"`
         querryM += ` AND serverip="${server[req.query.server]}"`
      }
   
   let stats = {}

   con.query(querryW, function (err, result, fields) { stats.totalWeek = timeConverter(toJson(result)[0].totalWeek) })
   con.query(querryM, function (err, result, fields) { stats.totalMonth = timeConverter(toJson(result)[0].totalMonth) })
   con.query(querryD, function (err, result, fields) { stats.totalDay = timeConverter(toJson(result)[0].totalDay) })
   
   con.query(querryT, function (err, result, fields) {
      result = toJson(result)
      stats.total = timeConverter(result[0].total)
      stats.flags = flagsString(result[0].flags.split('|').pop())
      stats.steamLink = toSteamID64(result[0].steamid)
      stats.sessions = result[0].sessions
      stats.name = result[0].name
      stats.names = result[0].names
      stats.steamid = result[0].steamid

      console.log(req.query)
      res.render('searchRes', {res: stats})
          
   
   });
}

})


app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`)
})

