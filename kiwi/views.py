from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone, dateformat

from django.core.cache import cache

import requests
import json

from django.views.decorators.csrf import csrf_exempt

FLY_API = 'https://api.skypicker.com/flights?'
CHECK_FLY = 'https://booking-api.skypicker.com/api/v0.1/check_flights?'
HEADERS = {
    'Content-Type': 'application/json'
}
DIRECTIONS = {
    'ALA': 'Алматы',
    'TSE': 'Астана',
    'MOW': 'Москва',
    'LED': 'С-Петербург',
    'CIT': 'Шымкент',
}
CURRENCY = {
    'EUR': 'Евро',
    'USD': 'Доллар',
    'RUB': 'Рубль',
    'KZT': 'Тенге'
}


def index(request):

    context = {
        'directions': DIRECTIONS,
        'currency': CURRENCY
    }

    return render(request, 'kiwi/index.html', context=context)


def getflys(request):

    date_from = dateformat.format(timezone.now(), 'd/m/Y')
    date_to = dateformat.format(
        timezone.now() + timezone.timedelta(days=31), 'd/m/Y'
    )

    data = []
    if cache.get(request.GET.get('from') + '_' + request.GET.get('to') + '_' + request.GET.get('curr')) is None:

        url = f"fly_from={request.GET.get('from')}&fly_to={request.GET.get('to')}&date_from={date_from}&date_to={date_to}&partner=picky&curr={request.GET.get('curr')}&v=3&sort=price"
        html = requests.get(FLY_API + url, headers=HEADERS)
        print(url)
        for item in html.json()['data'][:10]:
            data.append({
                'price': item['price'],
                'booking_token': item['booking_token'],
                'cityFrom': item['cityFrom'],
                'cityTo': item['cityTo'],
                'fly_duration': item['fly_duration'],
                'countryFrom': item['countryFrom'],
                'airlines': item['airlines']
            })

        cache.set(
            request.GET.get('from') + '_' + request.GET.get('to') +
            '_' + request.GET.get('curr'),
            data,
            86400
        )

    context = cache.get_or_set(
        request.GET.get('from') + '_' + request.GET.get('to') +
        '_' + request.GET.get('curr'),
        data,
        86400
    )

    return JsonResponse(json.dumps(context), safe=False)


@csrf_exempt
def checkfly(request):

    url = CHECK_FLY + """v=2&booking_token=""" + request.POST.get(
        'token') + """&bnum=3&pnum=2&affily=picky_{market}&currency=USD&adults=1&children=0&infants=1"""
    html = requests.get(url, headers=HEADERS)

    return JsonResponse(html.json(), safe=False)
