from django.shortcuts import render
from datetime import date, datetime
import rpy2
import rpy2.robjects as robjects
import numpy as np
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

  
    adj = []
    largo = len(historical_data)
    for i in range(largo-1):
        adj.append(historical_data[i][5])
    adj = [float(i) for i in adj]
    compra= datetime.strptime(req.get("fecha_compra"), '%Y-%m-%d').date()
    hoy=date.today()    
    Tm = compra - hoy
    Tm=Tm.days/365.
    S = float(historical_data[-2][5])
    k = np.mean(adj)
    sigma = np.std(adj)
    r=float(req.get("tasa_interes"))/100.
    print("S= ",S)
    print("k= ",k)
    print("Tm= ",Tm)
    print("r= ",r)
    print("sigma= ",sigma)
    r_f = robjects.r('''black_scholes <- function(S, k, Tm, r, sigma){
        values <- c(1)
        d1 <- (log(S/k) + (r+(sigma^2)/2)*(Tm))/(sigma*sqrt(Tm))
        d2 <- (log(S/k) + (r-(sigma^2)/2)*(Tm))/(sigma*sqrt(Tm))
        
        values[1] <- S*pnorm(d1) - k*exp(-r*Tm)*pnorm(d2)
        values[2] <- k*exp(-r*Tm)*pnorm(-d2)- S*pnorm(-d1)

        values
    }''')
    res= r_f(S,k,Tm,r,sigma)
    compra=res[0]
    venta=res[1]
    
    if req.get("tipo")=="Compra":
        context = {"historical_data": historical_data, "header_tabla": historical_data_raw[0].split(','),
        "accion": codigo, "resultado": compra,"tipo": "comprar", "fecha":req.get("fecha_compra")
        }
    else:
        context = {"historical_data": historical_data, "header_tabla": historical_data_raw[0].split(','),
        "accion": codigo, "resultado": venta, "tipo": "vender", "fecha":req.get("fecha_compra")
        }
    return render(request,'yahoodata/viewResults.html',context)
