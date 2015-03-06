function truncate(str, maxLength, suffix) {
    if(str.length > maxLength) {
        str = str.substring(0, maxLength + 1);
        str = str.substring(0, Math.min(str.length, str.lastIndexOf(" ")));
        str = str + suffix;
    }
    return str;
}

function flatten(root) {
    var nodes = [];

    function recurse(node) {
        if (node.children) node.children.forEach(recurse);
        else nodes.push({name: node.name, value: node.size});
    }

    recurse(root);
    return {children: nodes};
}

function mouseover(p) {
    var g = d3.select(this).node().parentNode;
    d3.select(g).selectAll("circle").style("display","none");
    d3.select(g).selectAll("text.value").style("display","block");
};

function mouseout(p) {
    var g = d3.select(this).node().parentNode;
    d3.select(g).selectAll("circle").style("display","block");
    d3.select(g).selectAll("text.value").style("display","none");
};

(function( $ ) {
    $.fn.chart = function(options) {
        var settings = $.extend({
            name:"Chart",
            data_url:"/",
            build_chart:build_chart,
            parse_data:parse_data,
            id:parseInt(Math.random()*1000000)
        }, options);

        var interval = false

        this.render = function(columns){
            $(this).append("<div class=\"col-md-"+columns+" dash-chart\"> \
                <h3>"+settings.name+"</h3> \
                <div id=\"chart"+settings.id+"\" class=\"chart\"> \
                    <div class=\"progress\">\
                        <div\
                            class=\"progress-bar progress-bar-info progress-bar-striped active loader\"\
                            role=\"progressbar\"\
                            aria-valuenow=\"20\"\
                            aria-valuemin=\"0\"\
                            aria-valuemax=\"100\"\
                            style=\"width: 5%\">\
                        </div>\
                    </div> \
                    <svg></svg> \
                </div> \
            </div>");
            animate_loader();
            load_data();
        }

        function animate_loader(){
            var per = 5;
            interval = setInterval(function(){
                $("#chart"+settings.id+" .progress .loader").css("width", per+"%");
                if(per < 100) per+=5;
            }, 50);
        }

        function remove_loader(){
            clearInterval(interval);
            $("#chart"+settings.id+" .progress").remove();
        }

        function load_data(){
            var me = this;
            $.get(settings.data_url, function(data, e){
                var d = settings.parse_data(data);
                remove_loader();
                settings.build_chart(settings, d);
            });
        }

        function parse_data(data){
            return data;
        }

        function build_chart(settings, data){
            console.log(data);
            $("#chart"+settings.id).append("Default Chart"+data);
        }

        return this;
    }

}( jQuery ));

(function($){
    $.fn.multibar = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.multiBarChart();

                chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format(data.date_format)(new Date(d));
                });
                chart.yAxis
                .tickFormat(d3.format(',.1f'));
                d3.select("#chart"+settings.id+" svg")
                .datum(data.data)
                .transition().duration(500)
                .call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });
        };
        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.bar = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.discreteBarChart()
                    .x(function(d) { return d.label })
                    .y(function(d) { return d.value })
                    .color(['#4785AB']);

                chart.yAxis
                .tickFormat(d3.format(',.1f'));
                d3.select("#chart"+settings.id+" svg")
                .datum(data.data)
                .transition().duration(500)
                .call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });
        };
        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.horizontal_multibar = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.multiBarHorizontalChart()
                .x(function(d) { return d.label })
                .y(function(d) { return d.value })
                .margin({top: 30, right: 20, bottom: 50, left: 175})
                .showValues(true)           //Show bar value next to each bar.
                .tooltips(true)             //Show tooltips on hover.
                .transitionDuration(350)
                .showControls(false);        //Allow user to switch between "Grouped" and "Stacked" mode.

                chart.yAxis
                .tickFormat(d3.format(',.0f'));

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data)
                .transition().duration(500)
                .call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });
        };
        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.horizontal_percent_multibar = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.multiBarHorizontalChart()
                .x(function(d) { return d.label })
                .y(function(d) { return d.value })
                .margin({top: 30, right: 20, bottom: 50, left: 175})
                .showValues(true)           //Show bar value next to each bar.
                .tooltips(true)             //Show tooltips on hover.
                .transitionDuration(350)
                .showControls(false)        //Allow user to switch between "Grouped" and "Stacked" mode.
                .showLegend(false);

                chart.showYAxis(false);
                chart.valueFormat(d3.format('p'));

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data)
                .transition().duration(500)
                .call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });
        };
        return $(this).chart(options);
    };
})(jQuery);

(function($){
    $.fn.pie = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.pieChart()
                .x(function(d) { return d.label })
                .y(function(d) { return d.value })
                .showLabels(true)     //Display pie labels
                .labelThreshold(.05)  //Configure the minimum slice size for labels to show up
                .labelType("percent") //Configure what type of data to show in the label. Can be "key", "value" or "percent"
                .donut(true)          //Turn on Donut mode. Makes pie chart look tasty!
                .donutRatio(0.35)     //Configure how big you want the donut hole size to be.
                ;

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data)
                .transition().duration(350)
                .call(chart);

                nv.utils.windowResize(chart.update);

                return chart;
            });
        };
        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.lineplusarea = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.multiChart()
                    .margin({top: 30, right: 60, bottom: 50, left: 70});

                //Format x-axis labels with custom function.
                chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format(data.date_format)(new Date(d))
                });

                // Get normalised data for chart
                var seriesData = data.data;

                // Get max values for each axis
                var minY1 = 0;
                var minY2 = 0;
                var maxY1 = 0;
                var maxY2 = 0;
                var highestMinX = 0;
                var highestMaxX = 0;
                for(var i = 0; i < seriesData.length; i++) {
                    var _axis = seriesData[i].yAxis;
                    var _values = seriesData[i].values;
                    var extent = d3.extent(_values, function(d) { return d.x });
                    if(extent[0] > highestMinX) {
                        highestMinX = extent[0];
                    }
                    if(extent[1] > highestMaxX) {
                        highestMaxX = extent[1];
                    }
                    // Walk values and set largest to variables
                    for(var j = 0; j < _values.length; j++) {
                        // For maxY1
                        if(_axis == 1) {
                            if(_values[j].y > maxY1) {
                                maxY1 = _values[j].y;
                            }
                        }
                        // For maxY2
                        if(_axis == 2) {
                            if(_values[j].y > maxY2) {
                                maxY2 = _values[j].y;
                            }
                        }
                    }
                }
                var diffY1 = maxY1 - minY1;
                var diffY2 = maxY2 - minY2;
                // Set min, max values of axis
                chart.yDomain1([minY1, maxY1+Math.ceil(diffY1/6)]);
                chart.yDomain2([minY2, maxY2+Math.ceil(diffY2/6)]);

                chart.xAxis.domain([highestMinX, highestMaxX]);

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data)
                .call(chart);

                nv.utils.windowResize(chart.update);
                return chart
            });
        };

        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.manylines = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.multiChart()
                    .margin({top: 30, right: 60, bottom: 50, left: 70})
                    .tooltipContent(function (key, x, val, graph) {
                        if(key == "Benchmark Engagement %") {
                            return "Benchmark Engagement";
                        } else {
                            return data.data.messages[x];
                        }
                    });

                //Format x-axis labels with custom function.
                chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format(data.date_format)(new Date(d))
                });

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data.points)
                .call(chart);

                nv.utils.windowResize(chart.update);
                return chart
            });
        };

        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.lineplusbar = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.linePlusBarChart()
                .x(function(d) { return d.x })   //We can modify the data accessor functions...
                .y(function(d) { return d.y })   //...in case your data is formatted differently.

                //Format x-axis labels with custom function.
                chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format(data.date_format)(new Date(d))
                });

                chart.y1Axis
                .tickFormat(d3.format(',.2f'));

                chart.y2Axis
                .tickFormat(d3.format(',.2f'));

                chart.bars.forceY([0]);

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data)
                .call(chart);

                nv.utils.windowResize(chart.update);
                return chart
            });
        };
        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.stackedline = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph(function() {
                var chart = nv.models.stackedAreaChart()
                .x(function(d) { return d.x })   //We can modify the data accessor functions...
                .y(function(d) { return d.y })   //...in case your data is formatted differently.
                .useInteractiveGuideline(true)    //Tooltips which show all data points. Very nice!
                .transitionDuration(500);

                //Format x-axis labels with custom function.
                chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format(data.date_format)(new Date(d))
                });

                chart.yAxis
                .tickFormat(d3.format(',.2f'));

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data)
                .call(chart);

                nv.utils.windowResize(chart.update);
                return chart
            });
        };
        return $(this).chart(options);
    };
})(jQuery);

(function($){
    $.fn.usa = function(options){
        options.build_chart = function(settings, data){
            var width = "100%",
            height = "100%";

            var projection = d3.geo.albersUsa()
            .scale(800)
            .translate([$("#chart"+settings.id).width() / 2, $("#chart"+settings.id).height() / 2]);

            var path = d3.geo.path()
            .projection(projection);

            var svg = d3.select("#chart"+settings.id+" svg")
            .attr("width", width)
            .attr("height", height);

            var radius = d3.scale.sqrt()
            .domain([0, 300])
            .range([0, 15]);

            d3.json("/static/json/us.json", function(error, us) {
                svg.insert("path", ".graticule")
                .datum(topojson.feature(us, us.objects.land))
                .attr("class", "land")
                .attr("d", path);

                svg.insert("path", ".graticule")
                .datum(topojson.mesh(us, us.objects.counties, function(a, b) { return a !== b && !(a.id / 1000 ^ b.id / 1000); }))
                .attr("class", "county-boundary")
                .attr("d", path);

                svg.insert("path", ".graticule")
                .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
                .attr("class", "state-boundary")
                .attr("d", path);

                data.data.forEach(function(d) {
                    var p = projection([+d.lng, +d.lat]);
                    if (p){
                        d.x = Math.round(p[0]);
                        d.y = Math.round(p[1]);
                        var c = svg.append("circle")
                        .attr("cx", d.x)
                        .attr("cy", d.y)
                        .attr("class", "bubble")
                        .attr("r", function() { return radius(d.count); });

                        c.append("title").text(function(){
                            return d.name+": "+d.count;
                        })
                    }
                });
            });
        };
        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.vertical_circle = function(options){
        options.build_chart = function(settings, data){
            var date_format = data.date_format;
            var data = data.data;
            var margin = {top: 20, right: 200, bottom: 0, left: 20},
            width = $("#chart"+settings.id).width()-200,
            height = $("#chart"+settings.id).height();

            var c = d3.scale.category20c();

            var x = d3.scale.linear()
            .range([0, width]);

            for(var i in data){
                var max = d3.max(data[i].articles, function(array){
                    return array[0];
                })
                var min = d3.min(data[i].articles, function(array){
                    return array[0];
                })
                var max_count = d3.max(data[i].articles, function(array){
                    return array[1];
                })
                var ticks = [];
                for(var a in data[i].articles){
                    ticks.push(data[i].articles[a][0]);
                }
                break;
            }

            var xAxis = d3.svg.axis()
            .scale(x)
            .orient("top")
            .tickValues(ticks)
            .tickFormat(function(d) {
                return d3.time.format(date_format)(new Date(d))
            });

            var svg = d3.select("#chart"+settings.id+" svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .style("margin-left", margin.left + "px")
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            for(var i in data){
                var max = d3.max(data[i].articles, function(array){
                    return array[0];
                })
                var min = d3.min(data[i].articles, function(array){
                    return array[0];
                })
                break;
            }

            x.domain([min, max]);
            var xScale = d3.scale.linear()
            .domain([min, max])
            .range([0, width]);

            svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + 0 + ")")
            .call(xAxis);

            var max_count = 0
            for(var i in data){
                for(var a in data[i].articles){
                    var art = data[i].articles[a];
                    max_count = art[1] > max_count ? art[1] : max_count;
                }
            }

            for (var j = 0; j < data.length; j++) {
                var g = svg.append("g").attr("class","journal");

                var circles = g.selectAll("circle")
                .data(data[j]['articles'])
                .enter()
                .append("circle");

                var text = g.selectAll("text")
                .data(data[j]['articles'])
                .enter()
                .append("text");

                var rScale = d3.scale.linear()
                .domain([0, max_count])
                .range([1, 15]);

                circles
                .attr("cx", function(d, i) { return xScale(d[0]); })
                .attr("cy", j*20+20)
                .attr("r", function(d) { return rScale(d[1]); })
                .style("fill", function(d) { return c(j); });

                text
                .attr("y", j*20+25)
                .attr("x",function(d, i) { return xScale(d[0])-5; })
                .attr("class","value")
                .text(function(d){ return d[1]; })
                .style("fill", function(d) { return c(j); })
                .style("display","none");

                g.append("text")
                .attr("y", j*20+25)
                .attr("x",width+20)
                .attr("class","label")
                .text(truncate(data[j]['name'],30,"..."))
                .style("fill", function(d) { return c(j); })
                .on("mouseover", mouseover)
                .on("mouseout", mouseout);
            };

        };
        return $(this).chart(options);
    };
})(jQuery);

(function($){
    $.fn.word_bubble = function(options){
        options.build_chart = function(settings, data){
            width = $("#chart"+settings.id).width(),
            height = $("#chart"+settings.id).height();
            var bleed = 0;
            var pack = d3.layout.pack()
            .sort(null)
            .size([width, height + bleed * 2])
            .padding(2);

            var svg = d3.select("#chart"+settings.id+" svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(0," + -bleed + ")");

            var node = svg.selectAll(".node")
            .data(pack.nodes(flatten(data.data))
            .filter(function(d) { return !d.children; }))
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

            node.append("circle")
            .attr("r", function(d) { return d.r; })
            .attr("class", "circle");

            node.append("text")
            .text(function(d) { return d.name; })
            .style("font-size", function(d) { return Math.min(2 * d.r, (2 * d.r - 8) / this.getComputedTextLength() * 12) + "px"; })
            .attr("dy", ".35em")
            .attr("class", "word-bubble");

        };
        return $(this).chart(options);
    };
})(jQuery);
