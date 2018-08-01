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

    #M = req.get("numero_trayectorias")
    M=1000
    put = int(req.get("tipo") == "Compra")

    r=float(req.get("tasa_interes"))/100.
    print("S= ",S)
    print("k= ",k)
    print("Tm= ",Tm)
    print("r= ",r)
    print("sigma= ",sigma)
    print("M= ",M)
    print("put= ",put)
    r_f = robjects.r('''black_scholes <- function(S, k, Tm, r, sigma){
        values <- c(1)
        d1 <- (log(S/k) + (r+(sigma^2)/2)*(Tm))/(sigma*sqrt(Tm))
        d2 <- (log(S/k) + (r-(sigma^2)/2)*(Tm))/(sigma*sqrt(Tm))
        
        values[1] <- S*pnorm(d1) - k*exp(-r*Tm)*pnorm(d2)
        values[2] <- k*exp(-r*Tm)*pnorm(-d2)- S*pnorm(-d1)

        values
    }''')

    res= r_f(S,k,Tm,r,sigma)

    montecarlo = robjects.r('''montecarlo_black_scholes <- function(S, k, Tm, r,sigma, M,put){
        cat(S)
        values <- matrix(nrow=M,ncol=2)
        var <- 0
        I_0 <- 0
        if(put == 1){
            I_1 <- max( k - S*exp((r-(sigma^2)/2)*Tm + sigma*sqrt(Tm)*rnorm(1, 0, 1)),0)
        }else{
            I_1 <- max( -k + S*exp((r-(sigma^2)/2)*Tm + sigma*sqrt(Tm)*rnorm(1, 0, 1)),0)
        }
        

        values[1,1] <- 1
        values[1,2] <- I_1


        
        for(i in 2:M){
            if(put == 1){
                h_i <- max( k - S*exp((r-(sigma^2)/2)*Tm + sigma*sqrt(Tm)*rnorm(1, 0, 1)),0)
            }else{
                h_i <- max( -k + S*exp((r-(sigma^2)/2)*Tm + sigma*sqrt(Tm)*rnorm(1, 0, 1)),0)
            }
            I_1 <- I_1 + (h_i -  I_1)/(i+1)
            values[i,1] <- i
            values[i,2] <- I_1
        } 

        values
    }''')

    
    print("y ahora",M)
    montecarlo_res = montecarlo(S,k,Tm,r,sigma,M,put)
    montecarlo_res = (np.asarray(montecarlo_res)).tolist()
    print("Listo: ", montecarlo_res)
    compra=res[0]
    venta=res[1]
    
    if req.get("tipo")=="Compra":
        context = {"data": montecarlo_res, "header_tabla": ["Iteracion", "Valor"],
        "accion": codigo, "resultado": compra,"tipo": "comprar", "fecha":req.get("fecha_compra")
        }
    else:
        context = {"data": montecarlo_res, "header_tabla": ["Iteracion", "Valor"],
        "accion": codigo, "resultado": venta, "tipo": "vender", "fecha":req.get("fecha_compra")
        }
    return render(request,'yahoodata/viewResults.html',context)
