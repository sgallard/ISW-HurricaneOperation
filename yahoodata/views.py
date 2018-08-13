from django.shortcuts import render
from datetime import date, datetime
import rpy2
import rpy2.robjects as robjects
import numpy as np
from yahoo_quote_download import yqd
import json

# quandl for financial data
import quandl
# pandas for data manipulation
import pandas as pd
quandl.ApiConfig.api_key = '-gzDw8tzAHNQZzxp8YXX'

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

    
   
    try:
        historical_data_raw = quandl.get('WIKI/'+ codigo,  start_date=fecha_inicio, end_date=fecha_fin)
        print(historical_data_raw)
    except:
        print("No Existe")
        return render(request, 'yahoodata/index.html', {})
    adj = []
    adj = historical_data_raw['Adj. Close'].values.tolist()

    adj = [float(i) for i in adj]
    compra= datetime.strptime(req.get("fecha_compra"), '%Y-%m-%d').date()
    hoy=date.today()    
    Tm = compra - hoy
    Tm=Tm.days/365.
    S = adj[-1]
    k = np.mean(adj)
    sigma = np.std(adj)

    M = int(req.get("puntos"))
    #M=1000

    n_trayectorias = int(req.get("trayectorias"))
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

    trayectorias = list()
    valores_finales = list()

    
    for i in range(n_trayectorias):
        montecarlo_res = montecarlo(S,k,Tm,r,sigma,M,put)
        montecarlo_res = (np.asarray(montecarlo_res))
        montecarlo_res_x = montecarlo_res[:,0].tolist()
        montecarlo_res_y = montecarlo_res[:,1].tolist()

        valor_final = float(montecarlo_res_y[-1])

        montecarlo_res_x = json.dumps(montecarlo_res_x)
        montecarlo_res_y = json.dumps(montecarlo_res_y)

        trayectorias.append(montecarlo_res_y)
        valores_finales.append(valor_final)


        print("Listo: ", valor_final)

    compra=res[0]
    venta=res[1]

    trayectorias = json.dumps(trayectorias)
    valores_finales = np.array(valores_finales)

    


    
    if req.get("tipo")=="Compra":
        context = {"data_x": montecarlo_res_x,"data_y": trayectorias, "cantidad_puntos": M, "cantidad_trayectorias": n_trayectorias,
        "accion": codigo, "resultado": compra,"tipo": "comprar", "fecha":req.get("fecha_compra"),
        "valor_final_montecarlo": np.mean(valores_finales), "error": np.mean(valores_finales) - float(compra),
        "desviacion_valores_finales": np.std(valores_finales)
        }
    else:
        context = {"data_x": montecarlo_res_x,"data_y": trayectorias, "cantidad_puntos": M,"cantidad_trayectorias": n_trayectorias,
        "accion": codigo, "resultado": venta, "tipo": "vender", "fecha":req.get("fecha_compra"),
        "valor_final_montecarlo": np.mean(valores_finales), "error": np.mean(valores_finales) - float(venta),
        "desviacion_valores_finales": np.std(valores_finales)
        }
    return render(request,'yahoodata/viewResults.html',context)
