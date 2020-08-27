#include <sourcemod>

public Plugin myinfo = {
	name = "playtime tracker",
	author = "Sadpeak",
	description = "tracker time&date sessions for all player",
	version = "0.1",
	url = "http://steamcommunity.com/id/sadpeak"
};

#define MIN_TIME_SESSION 30
#define MAX_TIME_SESSION 3600
enum {
  NONE = 0,
 	CONNECTING,
 	CONNECTED,
 	ERROR
}

int g_iState;
bool g_bLoaded;
Handle g_hTimer;
Database g_hDatabase; 

//int g_iStartTime[MAXPLAYERS+1];

void CreateDBConnection() {
  if (g_iState == CONNECTING || g_iState == CONNECTED) return;

  g_iState = CONNECTING;
  if (SQL_CheckConfig("testing")) {
    Database.Connect(OnDBConnected, "testing");
  } else {
    LogError("Sessions support only MySQL database!")
    g_iState = ERROR;
  }
}



public void OnPluginStart()
{
CreateDBConnection()
}

public void OnDBConnected (Database hDB, const char[] szError, any data) 
{
if (hDB == null || szError[0]) 
	{
	SetFailState("Database failure: %s", szError); 
	return;
	}

g_hDatabase = hDB;
g_hDatabase.SetCharset("utf8mb4");
hDB.Query(OnTableCreated, "CREATE TABLE IF NOT EXISTS `testing_table` (\
    `id` int(16) NOT NULL PRIMARY KEY AUTO_INCREMENT, \
    `steam_id` varchar(48) NOT NULL, \
    `name` varchar(64) NOT NULL DEFAULT 'unknown', \
    `start` int(16) UNSIGNED NOT NULL, \
    `end` int(16) UNSIGNED NOT NULL, \
    `flags` int(16) UNSIGNED NOT NULL DEFAULT 0 \
    ) DEFAULT CHARSET = utf8mb4;");

}

public void OnTableCreated(Database hDB, DBResultSet result, const char[] error, any data) {
  if (!hDB || error[0]) {
    SetFailState("[SM] Sessions.OnTableCreate %s", error);
    g_iState = ERROR;
    return;
  }
  g_bLoaded = true;
 }