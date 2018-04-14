// ==============================================================
// Bar chart option
// ==============================================================

$(document).ready(function(){

  var route = window.location.href + '/getGraficoBar';
  var token = $("#token").val();

    $.ajax({
      url: route,
      headers: {'X-CSRF-TOKEN': token},
      type:'GET',
      dataType: 'json',

      success:function(val){
          obj = JSON.stringify(val);
          datos= JSON.parse(obj);

          console.log(datos);





          cargarGrafico_Bar(datos.dias);
          cargarGrafico_Doug(datos.mandante);


       $('#select-bar').change(function(){
         if (1==$(this).val()){
           cargarGrafico_Bar(datos.dias);
         }
         else if (2==$(this).val()) {
           cargarGrafico_Bar(datos.meses);
         }
         else {
           cargarGrafico_Bar(datos.Years);
         }
      })

      $('#select-doug').change(function(){
        if (1==$(this).val()){
          cargarGrafico_Doug(datos.mandante);
        }
        else {
          cargarGrafico_Doug(datos.comuna);
        }
     })



      }
    });


});




function cargarGrafico_Bar(datos){



  var myChart = echarts.init(document.getElementById('bar-chart'));

  // specify chart configuration item and data
  option = {
      tooltip : {
          trigger: 'axis'
      },
      legend: {
          data:['Totales','Distribución','Transmisión']
      },
      toolbox: {
          show : true,
          feature : {

              magicType : {show: true, type: ['line', 'bar']},
              saveAsImage : {show: true}
          }
      },
      color: ["#CCCCCC","#55ce63", "#009efb"],
      xAxis : [
          {
              type : 'category',
              data : datos.map(datos => datos.periodo)
          }
      ],
      yAxis : [
          {
              type : 'value'
          }
      ],
      series : [
          {
              name:'Totales',
              type:'bar',
              data: datos.map(datos => datos.totales),
              markPoint : {
                  data : [
                      {type : 'max', name: 'Max'},
                      {type : 'min', name: 'Min'}
                  ]
              },
              markLine : {
                  data : [
                      {type : 'average', name: 'Average'}
                  ]
              }
          },
          {
              name:'Distribución',
              type:'bar',
              data: datos.map(datos => datos.distribucion),
              markPoint : {
                  data : [
                      {type : 'max', name: 'Max'},
                      {type : 'min', name: 'Min'}
                  ]
              },
              markLine : {
                  data : [
                      {type : 'average', name: 'Average'}
                  ]
              }
          },
          {
              name:'Transmisión',
              type:'bar',
              data: datos.map(datos => datos.transmision),
              markPoint : {
                  data : [
                      {type : 'max', name: 'Max'},
                      {type : 'min', name: 'Min'}
                  ]
              },
              markLine : {
                  data : [
                      {type : 'average', name : 'Average'}
                  ]
              }
          }
      ]
  };


  // use configuration item and data specified to show chart
  myChart.setOption(option, true), $(function() {
              function resize() {
                  setTimeout(function() {
                      myChart.resize()
                  }, 100)
              }
              $(window).on("resize", resize), $(".sidebartoggler").on("click", resize)
          });

}




function cargarGrafico_Doug(datos){
  var doughnutChart = echarts.init(document.getElementById('doughnut-chart'));

  // specify chart configuration item and data

  option = {
      tooltip : {
          trigger: 'item',
          formatter: "{a} <br/>{b} : {c} ({d}%)"
      },
      legend: {
          orient : 'vertical',
          x : 'left',
          data: datos.map(datos => datos.name)
      },
      toolbox: {
          show : true,
          feature : {
              saveAsImage : {show: true}
          }
      },
      series : [
          {
              name:'Source',
              type:'pie',
              radius : ['80%', '90%'],
              itemStyle : {
                  normal : {
                      label : {
                          show : false
                      },
                      labelLine : {
                          show : false
                      }
                  },
                  emphasis : {
                      label : {
                          show : true,
                          position : 'center',
                          textStyle : {
                              fontSize : '30',
                              fontWeight : 'bold'
                          }
                      }
                  }
              },
              data:datos
          }
      ]
  };



  // use configuration item and data specified to show chart
  doughnutChart.setOption(option, true), $(function() {
              function resize() {
                  setTimeout(function() {
                      doughnutChart.resize()
                  }, 100)
              }
              $(window).on("resize", resize), $(".sidebartoggler").on("click", resize)
          });



}
