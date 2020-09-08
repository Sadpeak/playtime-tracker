#include <sourcemod>

#pragma semicolon 1
#pragma newdecls required

public Plugin myinfo = {
	name = "playtime tracker",
	author = "Sadpeak",
	description = "tracker time&date sessions for all player",
	version = "0.1",
	url = "http://steamcommunity.com/id/sadpeak"
};

enum {
  NONE = 0,
 	CONNECTING,
 	CONNECTED,
 	ERROR
}

int g_iState;
Database g_hDatabase;


void CreateDBConnection() {
  if (g_iState == CONNECTING || g_iState == CONNECTED) return;

  g_iState = CONNECTING;
  if (SQL_CheckConfig("playtime")) {
    Database.Connect(OnDBConnected, "playtime");
  } else {
    
    g_iState = ERROR;
  }
}

void OnDBConnected(Database database, const char[] error, any data) {
  if (!database || error[0]) {
    SetFailState("[SM] Sessions.OnDBConnect: %s", error);
    g_iState = ERROR;
    return;
  }

  g_iState = CONNECTED;
  g_hDatabase = database;

  database.Query(OnTableCreated, "CREATE TABLE IF NOT EXISTS `playtime_tracker` (\
    `steamid` varchar(24) NOT NULL, \
    `name` varchar(64) NOT NULL DEFAULT 'unknown', \
    `start` int(16) UNSIGNED NOT NULL, \
    `end` int(16) UNSIGNED NOT NULL, \
    `flags` int(16) UNSIGNED NOT NULL DEFAULT 0, \
    `ip` varchar(32) NOT NULL DEFAULT 'unknown', \
    `serverip` varchar(32) NOT NULL \
    ) DEFAULT CHARSET = utf8mb4;");
}

public void OnTableCreated(Database database, DBResultSet result, const char[] error, any data) {
  if (!database || error[0]) {
    SetFailState("[SM] OnTableCreate %s", error);
    g_iState = ERROR;
    return;
  }

  database.Query(CharsetHandler, "SET NAMES 'utf8mb4'");
  database.Query(CharsetHandler, "SET CHARSET 'utf8mb4'");
  database.SetCharset("utf8mb4");

}

public void CharsetHandler(Database database, DBResultSet result, const char[] error, any data) {
	if (error[0]) LogError("[SM] CharsetSet: %s", error);
}

public void OnPluginStart() {
	CreateDBConnection();
}


public void OnClientDisconnect(int client) {
	if (IsFakeClient(client) || IsClientSourceTV(client) || IsClientReplay(client) || GetClientTime(client) < 120.0) return;
	
	char sQuery[256], sAuth[32], name[64], ip[33], serverIp[65], name2[128];
	int flags = GetUserFlagBits(client);
	GetClientName(client, name, 64);
	GetClientIP(client, ip, sizeof(ip));
	GetClientAuthId(client, AuthId_Steam2, sAuth, sizeof(sAuth));
	
	ConVar gameIP = FindConVar("ip");
	GetConVarString(gameIP, serverIp, 32);
  
	g_hDatabase.Escape(name, name2, sizeof(name2));
	FormatEx(sQuery, sizeof(sQuery), "INSERT INTO `playtime_tracker`(steamid, name, start, end, flags, ip, serverIp) \
			VALUES('%s', '%s',  %d,  %d,  %d, '%s', '%s'); ", sAuth, name2, GetTime() - RoundToZero(GetClientTime(client)), GetTime(), flags, ip, serverIp);
	g_hDatabase.Query(SQLT_OnClientDisconnect, sQuery);
  
}


public void SQLT_OnClientDisconnect(Handle hOwner, Handle hQuery, const char[] sError, any iUserId) {
	if (!hQuery)LogError("SQLT_OnClientDisconnect: %s", sError);
}