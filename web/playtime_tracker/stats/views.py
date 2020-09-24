from django.shortcuts import render
from django.http import HttpResponse
from .steam import steamid_to_commid
import os
import mysql.connector

# 'http://steamcommunity.com/profiles/' + str(steamid_to_commid('STEAM_0:0:158483103'))
# list = []
# tuple = ()
# dict = {}
database = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'db': os.getenv("DB_NAME"),
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
            # print(i, alf[i])
            s += alf[i]
    # print(s)
    return s


def get_role(flags):
    if flags & 16384:
        return 'Основатель'
    if flags & 1064960:
        return 'Гл.Администратор'
    if flags & 131072:
        return 'Модератор'
    if flags & 2:
        return 'Администратор'
    return 'Игрок'


def home_stats(request):
    return render(request, 'stats_home.html')


def stats_arena(request):
    return render(request, 'stats.html', {'server': 'arena'})


def stats_public(request):
    return render(request, 'stats.html', {'server': 'public'})


def stats_awp(request):
    return render(request, 'stats.html', {'server': 'awp'})


def stats_all(request):
    return stats('all', request)


def stats(server, request):
    connection = mysql.connector.connect(**database)
    assert connection, "Connection failed"

    cursor = connection.cursor()
    cursor2 = connection.cursor()
    cursor3 = connection.cursor()
    cursor4 = connection.cursor()
    context = {'stats': []}
    statsAll, statsDay, statsWeek, statsMonth = [], [], [], []
    # query = ("SELECT steamid, GROUP_CONCAT(DISTINCT name), SUM(end - start) AS total FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)) GROUP BY steamid ORDER BY total DESC LIMIT 10")
    queryAll = (
        "SELECT steamid, name, SUM(end - start) AS total, COUNT(*) AS sessions, flags FROM `playtime_tracker` GROUP BY steamid ORDER BY total DESC")
    queryDay = ("SELECT steamid, SUM(end - start) AS totalDay FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)) GROUP BY steamid ORDER BY totalDay DESC")
    queryWeek = ("SELECT steamid, SUM(end - start) AS totalWeek FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 WEEK)) GROUP BY steamid ORDER BY totalWeek DESC")
    queryMonth = ("SELECT steamid, SUM(end - start) AS totalMonth FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 MONTH)) GROUP BY steamid ORDER BY totalMonth DESC")

    cursor.execute(queryAll)

    for (steamid, name, total, sessions, flags) in cursor:
        statsAll.append({
            'steamid': steamid,
            'name': name,
            'timeAll': get_time(total),
            'sessions': sessions,
            'flags': get_flag_str(flags),
            'url': steamid_to_commid(steamid),
            'role': get_role(flags),
        })
    cursor.close()

    cursor2.execute(queryDay)

    for (steamid, totalDay) in cursor2:
        statsDay.append({
            'timeDay': get_time(totalDay),
        })
    cursor2.close()

    cursor3.execute(queryWeek)

    for (steamid, totalWeek) in cursor3:
        statsWeek.append({
            'timeWeek': get_time(totalWeek),
        })
    cursor3.close()

    cursor4.execute(queryMonth)

    for (steamid, totalMonth) in cursor4:
        statsMonth.append({
            'timeMonth': get_time(totalMonth),
        })
    cursor4.close()

    for a, d, w, m in zip(statsAll, statsDay, statsWeek, statsMonth):
        context['stats'].append({
            'steamid': a['steamid'],
            'name': a['name'],
            'timeAll': a['timeAll'],
            'sessions': a['sessions'],
            'flags': a['flags'],
            'url': a['url'],
            'timeDay': d['timeDay'],
            'timeWeek': w['timeWeek'],
            'timeMonth': m['timeMonth'],
            'role': a['role'],
        })
    connection.close()
    context['server'] = server
    return render(request, 'stats.html', context)
