from django.shortcuts import render
from django.http import HttpResponse
from .steam import steamid_to_commid
import os
import mysql.connector

# 'http://steamcommunity.com/profiles/' + str(steamid_to_commid('STEAM_0:0:158483103'))

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
            print(i, alf[i])
            s += alf[i]
    print(s)
    return s


def home_stats(request):
    return render(request, 'stats_home.html')


def stats_arena(request):
    return render(request, 'stats.html', {'server': 'arena'})


def stats_public(request):
    return render(request, 'stats.html', {'server': 'public'})


def stats_awp(request):
    return render(request, 'stats.html', {'server': 'awp'})


def stats_all(request):
    connection = mysql.connector.connect(**database)
    assert connection, "Connection failed"

    cursor = connection.cursor()

    # query = ("SELECT steamid, GROUP_CONCAT(DISTINCT name), SUM(end - start) AS total FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)) GROUP BY steamid ORDER BY total DESC LIMIT 10")
    queryAll = (
        "SELECT steamid, name, SUM(end - start) AS total FROM `playtime_tracker` GROUP BY steamid ORDER BY total DESC")
    queryDay = ("SELECT steamid, SUM(end - start) AS total FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)) GROUP BY steamid ORDER BY total DESC")
    queryWeek = ("SELECT steamid, SUM(end - start) AS total FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 WEEK)) GROUP BY steamid ORDER BY total DESC")
    queryMONTH = ("SELECT steamid, SUM(end - start) AS total FROM `playtime_tracker` WHERE start > UNIX_TIMESTAMP(DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 MONTH)) GROUP BY steamid ORDER BY total DESC")

    cursor.execute(queryAll)

    for (steamid, name, total) in cursor:
        pass
    cursor.close()
    connection.close()
    return render(request, 'stats.html', {'server': 'all'})
