steamid64ident = 76561197960265728


def commid_to_steamid(commid):
    steamid = []
    steamid.append('STEAM_0:')
    steamidacct = int(commid) - steamid64ident

    if steamidacct % 2 == 0:
        steamid.append('0:')
    else:
        steamid.append('1:')

    steamid.append(str(steamidacct // 2))

    return ''.join(steamid)


def steamid_to_commid(steamid):
	sid_split = steamid.split(':')
	commid = int(sid_split[2]) * 2

	if sid_split[1] == '1':
		commid += 1

	commid += steamid64ident
	return commid