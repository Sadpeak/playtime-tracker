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

int g_iStartTime[MAXPLAYERS+1];

void CreateDBConnection() {
  if (g_iState == CONNECTING || g_iState == CONNECTED) return;

  g_iState = CONNECTING;
  if (SQL_CheckConfig("testing")) {
    Database.Connect(OnDBConnected, "testing");
  } else {
    LogError("playtime tracker support only MySQL database!")
    g_iState = ERROR;
  }
}



public void OnPluginStart()
{
	g_bLoaded = false;
	CreateDBConnection()
	g_hTimer = CreateTimer(60.0, OnMinute, _, TIMER_REPEAT);
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
    `account` int(16) UNSIGNED NOT NULL , \
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
 
 public void OnClientPostAdminCheck(int client) {
  if (!IsFakeClient(client)) {
    g_iStartTime[client] = GetTime();
  }
}

public Action OnMinute(Handle timer) {
	int time = GetTime();
	for (int i = 1; i <= MaxClients; i++) {
		if (!IsFakeClient(i)) {
			if (!g_iStartTime[i]) {
				g_iStartTime[i] = time;
				continue;
			}
			if (time - g_iStartTime[i] >= MAX_TIME_SESSION) {
				WriteSession(i, g_iStartTime[i], time);
				g_iStartTime[i] = time;
			}
		}
	}
}

public void OnClientDisconnect(int client) {
  if (!g_iStartTime[client]) return;

  if (g_bLoaded) {
    int end = GetTime();
    if (end - g_iStartTime[client] >= MIN_TIME_SESSION) {
			WriteSession(client, g_iStartTime[client], end);
    }
  }
  g_iStartTime[client] = 0;
}

public void WriteSession(int client, int start, int end) {
	char name[128], query[512], ip[32];
	int flags = GetUserFlagBits(client);
	int account = GetSteamAccountID(client);
	GetClientIP(client, ip, sizeof(ip));

	if (GetClientName(client, query, sizeof(query))) {
		g_hDatabase.Escape(query, name, sizeof(name));
		FormatEx(query, sizeof(query), "\
			INSERT INTO `testing` (account, name, start, end, flags, ip) \
			VALUES (%d, '%s', %d, %d, %d, '%s');", account, name, start, end, flags, ip
		);
	} else {
		FormatEx(query, sizeof(query), "\
			INSERT INTO `testin` (account, start, end, flags, ip) \
			VALUES (%d, %d, %d, %d, '%s');", account, start, end, flags, ip
		);
	}

	g_hDatabase.Query(OnSessionLogged, query);
}

public void OnSessionLogged(Database database, DBResultSet result, const char[] error, any data) {
  if (!result || error[0]) {
		LogError("[SM] PlaytimeTracker.OnSessionLogged %s", error);
	}
}

public OnPluginEnd() {
	KillTimer(g_hTimer);
	CloseHandle(g_hDatabase);
}