from django.shortcuts import render
from django.http import HttpResponse
from .steam import steamid_to_commid
import os
import mysql.connector


database = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'db': os.getenv("DB_NAME"),
}

filters = {
    'admin': lambda flags: flags & 1064962,
    'moder': lambda flags: flags & 131072,
}

def get_time(seconds):
    h = seconds // 3600
    m = (seconds - (h * 3600)) // 60
    s = seconds - (h * 3600) - (m * 60)

    return '%s:%s:%s' % (
        ('0' if h < 10 else '') + str(h),
        ('0' if m < 10 else '') + str(m),
        ('0' if s < 10 else '') + str(s)
    )


def get_flag_str(flags):
    alf, s = 'abcdefghijklmnzopqrst', ''
    for i in range(len(alf)):
        if flags & (2 ** i):
            s += alf[i]
    return s


def get_role(flags):
    if flags & 16384:
        return 'Основатель'
    if flags & 131072:
        return 'Модератор'
    if flags & 2:
        return 'Администратор'
    return 'Игрок'


def get_ip(server):
    if server == 'public':
        return os.getenv("IP_PUBLIC")
    if server == 'awp':
        return os.getenv("IP_AWP")
    if server == 'arena':
        return os.getenv("IP_ARENA")
    if server == 'all':
        return ' '


def home_stats(request):
    return render(request, 'stats_home.html')


def stats_arena(request):
    return stats('arena', request)


def stats_public(request):
    return stats('public', request)


def stats_awp(request):
    return stats('awp', request)


def stats_all(request):
    return stats('all', request)


def stats(server, request):
    role_key = request.GET.get('role', 'all')

    connection = mysql.connector.connect(**database)
    assert connection, "Connection failed"

    cursor = connection.cursor()
    cursor2 = connection.cursor()
    cursor3 = connection.cursor()
    cursor4 = connection.cursor()
    context = {'stats': []}
    statsAll, statsDay, statsWeek, statsMonth = [], [], [], []

    def online_day(steamid):
        for val in statsDay:
            if val['steamid'] == steamid:
                return val['timeDay']

    def online_week(steamid):
        for val in statsWeek:
            if val['steamid'] == steamid:
                return val['timeWeek']

    def online_month(steamid):
        for val in statsMonth:
            if val['steamid'] == steamid:
                return val['timeMonth']
    
    queryAll = (
        "SELECT steamid, name, GROUP_CONCAT(DISTINCT name SEPARATOR '\n') AS names, SUM(end - start) AS total, COUNT(*) AS sessions, flags FROM `playtime_tracker` {} {} GROUP BY steamid ORDER BY total DESC")
    queryDay = ("SELECT steamid, SUM(end - start) AS totalDay FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)) {} {} GROUP BY steamid ORDER BY totalDay DESC")
    queryWeek = ("SELECT steamid, SUM(end - start) AS totalWeek FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 WEEK)) {} {} GROUP BY steamid ORDER BY totalWeek DESC")
    queryMonth = ("SELECT steamid, SUM(end - start) AS totalMonth FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP , INTERVAL 1 MONTH)) {} {} GROUP BY steamid ORDER BY totalMonth DESC")

    whichServer = "serverip='{}'".format(get_ip(server))
    if server == 'all':
        cursor.execute(queryAll.format(' ', ' '))
    else:
        cursor.execute(queryAll.format('WHERE', whichServer))

    for (steamid, name, names, total, sessions, flags) in cursor:
        statsAll.append({
            'steamid': steamid,
            'name': name,
            'names': names,
            'timeAll': total,
            'sessions': sessions,
            'flags': flags,
            'url': steamid_to_commid(steamid),
            'role': get_role(flags),
        })
    cursor.close()

    if server == 'all':
        cursor2.execute(queryDay.format(' ', ' '))
    else:
        cursor2.execute(queryDay.format('AND', whichServer))

    for (steamid, totalDay) in cursor2:
        statsDay.append({
            'steamid': steamid,
            'timeDay': get_time(totalDay),
        })
    cursor2.close()

    if server == 'all':
        cursor3.execute(queryWeek.format(' ', ' '))
    else:
        cursor3.execute(queryWeek.format('AND', whichServer))

    for (steamid, totalWeek) in cursor3:
        statsWeek.append({
            'steamid': steamid,
            'timeWeek': get_time(totalWeek),
        })
    cursor3.close()

    if server == 'all':
        cursor4.execute(queryMonth.format(' ', ' '))
    else:
        cursor4.execute(queryMonth.format('AND', whichServer))

    for (steamid, totalMonth) in cursor4:
        statsMonth.append({
            'steamid': steamid,
            'timeMonth': get_time(totalMonth),
        })
    cursor4.close()

    context['roles'] = [
        {'key': 'all', 'text': 'Все', 'class': 'active' if role_key == 'all' else ''},
        {'key': 'moder', 'text': 'Модератор',
            'class': 'active' if role_key == 'moder' else ''},
        {'key': 'admin', 'text': 'Администратор',
            'class': 'active' if role_key == 'admin' else ''}
    ]

    filter_f = filters.get(role_key)

    for stat in statsAll:

        if filter_f is None or filter_f(stat['flags']):

            if stat['flags'] & 2 == 0 and stat['timeAll'] < 3600:
                continue

            context['stats'].append({
                'steamid': stat['steamid'],
                'name': stat['name'],
                'names': stat['names'],
                'timeAll': get_time(stat['timeAll']),
                'sessions': stat['sessions'],
                'flags': get_flag_str(stat['flags']),
                'url': stat['url'],
                'role': stat['role'],
                'timeDay': online_day(stat['steamid']),
                'timeWeek': online_week(stat['steamid']),
                'timeMonth': online_month(stat['steamid']),
            })

    connection.close()
    context['server'] = server
    return render(request, 'stats.html', context)