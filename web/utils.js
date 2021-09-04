const toJson = data => JSON.parse(JSON.stringify(data))


const timeConverter = (time) => {
   timeH = Math.trunc(time/3600)
   timeM = Math.trunc((time - timeH*3600)/60)
   timeS = time - timeH*3600 - timeM*60
   
   timeH < 10 ? timeH = "0" + timeH : 1
   timeM < 10 ? timeM = "0" + timeM : 1
   timeS < 10 ? timeS = "0" + timeS : 1

   return timeH +':'+ timeM +':'+ timeS
}


const flagsString = flags => {
   
    const alf = 'abcdefghijklmnzopqrst'
    let s = ''
    for (let i = 0; i < alf.length; i++) {
       if (flags & (2 ** i)){
          s += alf[i]
         }       
    }
    return s
}

const toSteamID64 = (steamid)=> {
        const splited = steamid.split(':')
        return 'https://steamcommunity.com/profiles/' + String(BigInt(splited[2]*2)+76561197960265728n + BigInt(splited[1]))
      }


module.exports = { toJson, timeConverter, flagsString, toSteamID64}
