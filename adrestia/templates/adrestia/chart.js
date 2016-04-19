<script>
$(function () {
 Highcharts.setOptions({
        colors: ['#AA3333', '#559955', '#999999']
    });
    $('#delegate-chart').highcharts({
        chart: {
            type: 'bar',
            backgroundColor: 'rgba(255, 255, 255, 0.20)',
/*
            borderColor: '#FF0000',
            borderWidth: 1
*/
        },
        credits: {
            text: 'DearSuperDelegate.com',
            href: '{% url "home" %}'
        },
        tooltip: {
            useHTML: true,
            headerFormat: '<small>{point.key}</small><table>',
            pointFormat: '<tr><td style="color:{series.color}"><b>' +
                         '{series.name}</b></td><td style="text-align:right">' +
                         '<b>{point.y}%</b></td></tr>',
            footerFormat:'</table>'
        },
        title: {
            text: 'Delegate %'
        },
        xAxis: {
            categories: ['Super', 'Pledged']
        },
        yAxis: {
            min: 0,
            title: {
                text: ''
            }
        },
        legend: {
            reversed: true
        },
        plotOptions: {
            series: {
                stacking: 'percent',
            }
        },
        {% autoescape off %}
        series: eval('{{ series_json }}')
        {% endautoescape %}
    });
});
</script>
