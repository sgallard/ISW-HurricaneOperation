from django.shortcuts import render
from datetime import date

from yahoo_quote_download import yqd

# Create your views here.

from django.http import HttpResponse


def index(request):
    return render(request, 'yahoodata/index.html', {})

def getdata(request):
    req = request.POST
    fecha_inicio = "2018-01-01"
    fecha_inicio = ''.join(fecha_inicio.split('-'))

    today = str(date.today())
    fecha_fin = ''.join(today.split('-'))

    codigo = req.get("codigo")

    yqd._cookie = None
    yqd._crumb = None

    print (yqd._cookie)

    yqd._get_cookie_crumb()

    historical_data_raw = yqd.load_yahoo_quote(codigo,fecha_inicio,fecha_fin)
    historical_data = list()

    for x in historical_data_raw[1::]:
        historical_data.append(x.split(','))

    context = {"historical_data": historical_data, "header_tabla": historical_data_raw[0].split(','),
    "accion": codigo
    }

    return render(request,'yahoodata/viewResults.html',context)
