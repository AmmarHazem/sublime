import requests
from django.shortcuts import render
from django.http import JsonResponse
import datetime
# import json


API_URL = 'http://127.0.0.1:7000'


def session_reservation(request):
    return render(request, 'session_reservation.html', {'date' : request.GET.get('date'), 'from' : request.GET.get('from'), 'to' : request.GET.get('to')})


def service_price_list_item(request, uuid):
    res = requests.get(f'{API_URL}/api/service-providers/{uuid}/')
    data = res.json()
    service = None
    item_id = request.GET.get('item_id')
    for item in data['provider_price_list']['items']:
        if item['uuid'] == item_id:
            service = item
    duration = (service.get('duration') or '00:15:00').split(':')
    schedules = data.get('schedules', [])[0]
    start_hour = int(schedules['start_time'].split(':')[0])
    end_hour = int(schedules['end_time'].split(':')[0])
    start_minute = int(schedules['start_time'].split(':')[1])
    end_minute = int(schedules['end_time'].split(':')[1])
    date_obj = datetime.datetime.strptime(request.GET.get('date'), '%d-%m-%Y') # or datetime.date.today()
    day_delta = datetime.timedelta(days = 1)
    if request.GET.get('next'):
        date_obj += day_delta
    elif request.GET.get('prev'):
        date_obj -= day_delta
    i = 0
    while not str(date_obj.weekday() + 1) in schedules['repeat_days'] and i < 7:
        date_obj += day_delta
        print('---- off day')
    start_time = datetime.datetime(year = date_obj.year, month = date_obj.month, day = date_obj.day, hour = start_hour, minute = start_minute)
    end_time = datetime.datetime(year = date_obj.year, month = date_obj.month, day = date_obj.day, hour = end_hour, minute = end_minute)
    session_duration = datetime.timedelta(hours = int(duration[0]), minutes = int(duration[1]))
    sessions = []
    while start_time < end_time:
        start = start_time.strftime('%I:%M %p')
        start_time = start_time + session_duration
        end = start_time.strftime('%I:%M %p')
        sessions.append((start, end))
    return render(request, 'includes/sessions.html', {'sessions' : sessions, 'date' : date_obj.strftime('%d-%m-%Y')})


def home(request):
    cxt = {
        'api_url' : API_URL,
    }
    try:
        res = requests.get(f'{API_URL}/api/service-providers/')
        cxt['providers'] = res.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, ValueError):
        print('--- ConnectionError  ConnectTimeout')
        cxt['providers'] = {}
    return render(request, 'pages/home.html', cxt)


def provider_details(request, uuid):
    cxt = {
        'api_url' : API_URL,
    }
    try:
        res = requests.get(f'{API_URL}/api/service-providers/{uuid}/')
        cxt['provider'] = res.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, ValueError):
        print('--- ConnectionError  ConnectTimeout')
        cxt['providers'] = {}
    return render(request, 'pages/provider_detail.html', cxt)
