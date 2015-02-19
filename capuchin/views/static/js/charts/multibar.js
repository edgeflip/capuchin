(function($){
    var plugin = $.chart.prototype;
    $.extend(true, plugin, {
        multibar: function(options){
            options.build_chart = function(data){
                nv.addGraph(function() {
                    var chart = nv.models.multiBarChart();

                    chart.xAxis
                    .tickFormat(function(d) {
                        return d3.time.format(res.date_format)(new Date(d));
                    });

                    chart.yAxis
                    .tickFormat(d3.format(',.1f'));
                    d3.select("#chart"+settings.id+" svg")
                    .datum(data)
                    .transition().duration(500)
                    .call(chart)
                    ;

                    nv.utils.windowResize(chart.update);

                    return chart;
                });
            }
            return $(this).chart(options);
        }
    });
})(jQuery);
