function truncate(str, maxLength, suffix) {
    if(str.length > maxLength) {
        str = str.substring(0, maxLength + 1);
        str = str.substring(0, Math.min(str.length, str.lastIndexOf(" ")));
        str = str + suffix;
    }
    return str;
}

d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
        this.parentNode.appendChild(this);
    });
};

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

function multiChart() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var margin = {top: 30, right: 20, bottom: 50, left: 60},
      color = d3.scale.category20().range(),
      width = null, 
      height = null,
      showLegend = true,
      tooltips = true,
      tooltip = function(key, x, y, e, graph) {
        return '<h3>' + key + '</h3>' +
               '<p>' +  y + ' at ' + x + '</p>'
      },
      x,
      y,
      yDomain1,
      yDomain2
      ; //can be accessed via chart.lines.[x/y]Scale()

  //============================================================
  // Private Variables
  //------------------------------------------------------------

  var x = d3.scale.linear(),
      yScale1 = d3.scale.linear(),
      yScale2 = d3.scale.linear(),

      lines1 = nv.models.line().yScale(yScale1),
      lines2 = nv.models.line().yScale(yScale2),

      bars1 = nv.models.multiBar().stacked(false).yScale(yScale1),
      bars2 = nv.models.multiBar().stacked(false).yScale(yScale2),

      stack1 = nv.models.stackedArea().yScale(yScale1),
      stack2 = nv.models.stackedArea().yScale(yScale2),

      xAxis = nv.models.axis().scale(x).orient('bottom').tickPadding(5),
      yAxis1 = nv.models.axis().scale(yScale1).orient('left'),
      yAxis2 = nv.models.axis().scale(yScale2).orient('right'),

      legend = nv.models.legend().height(30),
      dispatch = d3.dispatch('tooltipShow', 'tooltipHide');

  var showTooltip = function(e, offsetElement) {
    var left = e.pos[0] + ( offsetElement.offsetLeft || 0 ),
        top = e.pos[1] + ( offsetElement.offsetTop || 0),
        x = xAxis.tickFormat()(lines1.x()(e.point, e.pointIndex)),
        y = ((e.series.yAxis == 2) ? yAxis2 : yAxis1).tickFormat()(lines1.y()(e.point, e.pointIndex)),
        content = tooltip(e.series.key, x, y, e, chart);

    nv.tooltip.show([left, top], content, undefined, undefined, offsetElement.offsetParent);
  };

  function chart(selection) {
    selection.each(function(data) {
      var container = d3.select(this),
          that = this;

      chart.update = function() { container.transition().call(chart); };
      chart.container = this;

      var availableWidth = (width  || parseInt(container.style('width')) || 960)
                             - margin.left - margin.right,
          availableHeight = (height || parseInt(container.style('height')) || 400)
                             - margin.top - margin.bottom;

      var dataLines1 = data.filter(function(d) {return !d.disabled && d.type == 'line' && d.yAxis == 1})
      var dataLines2 = data.filter(function(d) {return !d.disabled && d.type == 'line' && d.yAxis == 2})
      var dataBars1 = data.filter(function(d) {return !d.disabled && d.type == 'bar' && d.yAxis == 1})
      var dataBars2 = data.filter(function(d) {return !d.disabled && d.type == 'bar' && d.yAxis == 2})
      var dataStack1 = data.filter(function(d) {return !d.disabled && d.type == 'area' && d.yAxis == 1})
      var dataStack2 = data.filter(function(d) {return !d.disabled && d.type == 'area' && d.yAxis == 2})

      var series1 = data.filter(function(d) {return !d.disabled && d.yAxis == 1})
            .map(function(d) {
              return d.values.map(function(d,i) {
                return { x: d.x, y: d.y }
              })
            })

      var series2 = data.filter(function(d) {return !d.disabled && d.yAxis == 2})
            .map(function(d) {
              return d.values.map(function(d,i) {
                return { x: d.x, y: d.y }
              })
            })

      x   .domain(d3.extent(d3.merge(series1.concat(series2)), function(d) { return d.x } ))
          .range([0, availableWidth]);

      var wrap = container.selectAll('g.wrap.multiChart').data([data]);
      var gEnter = wrap.enter().append('g').attr('class', 'wrap nvd3 multiChart').append('g');

      gEnter.append('g').attr('class', 'x axis');
      gEnter.append('g').attr('class', 'y1 axis');
      gEnter.append('g').attr('class', 'y2 axis');
      gEnter.append('g').attr('class', 'lines1Wrap');
      gEnter.append('g').attr('class', 'lines2Wrap');
      gEnter.append('g').attr('class', 'bars1Wrap');
      gEnter.append('g').attr('class', 'bars2Wrap');
      gEnter.append('g').attr('class', 'stack1Wrap');
      gEnter.append('g').attr('class', 'stack2Wrap');
      gEnter.append('g').attr('class', 'legendWrap');

      var g = wrap.select('g');

      if (showLegend) {
        legend.width( availableWidth / 2 );

        g.select('.legendWrap')
            .datum(data.map(function(series) { 
              series.originalKey = series.originalKey === undefined ? series.key : series.originalKey;
              series.key = series.originalKey + (series.yAxis == 1 ? '' : ' (right axis)');
              return series;
            }))
          .call(legend);

        if ( margin.top != legend.height()) {
          margin.top = legend.height();
          availableHeight = (height || parseInt(container.style('height')) || 400)
                             - margin.top - margin.bottom;
        }

        g.select('.legendWrap')
            .attr('transform', 'translate(' + ( availableWidth / 2 ) + ',' + (-margin.top) +')');
      }


      lines1
        .width(availableWidth)
        .height(availableHeight)
        .interpolate("monotone")
        .color(data.map(function(d,i) {
          return d.color || color[i % color.length];
        }).filter(function(d,i) { return !data[i].disabled && data[i].yAxis == 1 && data[i].type == 'line'}));

      lines2
        .width(availableWidth)
        .height(availableHeight)
        .interpolate("monotone")
        .color(data.map(function(d,i) {
          return d.color || color[i % color.length];
        }).filter(function(d,i) { return !data[i].disabled && data[i].yAxis == 2 && data[i].type == 'line'}));

      bars1
        .width(availableWidth)
        .height(availableHeight)
        .color(data.map(function(d,i) {
          return d.color || color[i % color.length];
        }).filter(function(d,i) { return !data[i].disabled && data[i].yAxis == 1 && data[i].type == 'bar'}));

      bars2
        .width(availableWidth)
        .height(availableHeight)
        .color(data.map(function(d,i) {
          return d.color || color[i % color.length];
        }).filter(function(d,i) { return !data[i].disabled && data[i].yAxis == 2 && data[i].type == 'bar'}));

      stack1
        .width(availableWidth)
        .height(availableHeight)
        .color(data.map(function(d,i) {
          return d.color || color[i % color.length];
        }).filter(function(d,i) { return !data[i].disabled && data[i].yAxis == 1 && data[i].type == 'area'}));

      stack2
        .width(availableWidth)
        .height(availableHeight)
        .color(data.map(function(d,i) {
          return d.color || color[i % color.length];
        }).filter(function(d,i) { return !data[i].disabled && data[i].yAxis == 2 && data[i].type == 'area'}));

      g.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');


      var lines1Wrap = g.select('.lines1Wrap')
          .datum(dataLines1)
      var bars1Wrap = g.select('.bars1Wrap')
          .datum(dataBars1)
      var stack1Wrap = g.select('.stack1Wrap')
          .datum(dataStack1)

      var lines2Wrap = g.select('.lines2Wrap')
          .datum(dataLines2)
      var bars2Wrap = g.select('.bars2Wrap')
          .datum(dataBars2)
      var stack2Wrap = g.select('.stack2Wrap')
          .datum(dataStack2)

      var extraValue1 = dataStack1.length ? dataStack1.map(function(a){return a.values}).reduce(function(a,b){
        return a.map(function(aVal,i){return {x: aVal.x, y: aVal.y + b[i].y}})
      }).concat([{x:0, y:0}]) : []
      var extraValue2 = dataStack2.length ? dataStack2.map(function(a){return a.values}).reduce(function(a,b){
        return a.map(function(aVal,i){return {x: aVal.x, y: aVal.y + b[i].y}})
      }).concat([{x:0, y:0}]) : []

      yScale1 .domain(yDomain1 || d3.extent(d3.merge(series1).concat(extraValue1), function(d) { return d.y } ))
              .range([0, availableHeight])

      yScale2 .domain(yDomain2 || d3.extent(d3.merge(series2).concat(extraValue2), function(d) { return d.y } ))
              .range([0, availableHeight])

      lines1.yDomain(yScale1.domain())
      bars1.yDomain(yScale1.domain())
      stack1.yDomain(yScale1.domain())

      lines2.yDomain(yScale2.domain())
      bars2.yDomain(yScale2.domain())
      stack2.yDomain(yScale2.domain())

      if(dataStack1.length){d3.transition(stack1Wrap).call(stack1);}
      if(dataStack2.length){d3.transition(stack2Wrap).call(stack2);}

      if(dataBars1.length){d3.transition(bars1Wrap).call(bars1);}
      if(dataBars2.length){d3.transition(bars2Wrap).call(bars2);}

      if(dataLines1.length){d3.transition(lines1Wrap).call(lines1);}
      if(dataLines2.length){d3.transition(lines2Wrap).call(lines2);}
      


      xAxis
        .ticks( availableWidth / 100 )
        .tickSize(-availableHeight, 0);

      g.select('.x.axis')
          .attr('transform', 'translate(0,' + availableHeight + ')');
      d3.transition(g.select('.x.axis'))
          .call(xAxis);

      yAxis1
        .ticks( availableHeight / 36 )
        .tickSize( -availableWidth, 0);


      d3.transition(g.select('.y1.axis'))
          .call(yAxis1);

      yAxis2
        .ticks( availableHeight / 36 )
        .tickSize( -availableWidth, 0);

      d3.transition(g.select('.y2.axis'))
          .call(yAxis2);

      g.select('.y2.axis')
          .style('opacity', series2.length ? 1 : 0)
          .attr('transform', 'translate(' + x.range()[1] + ',0)');

      legend.dispatch.on('stateChange', function(newState) { 
        chart.update();
      });
     
      dispatch.on('tooltipShow', function(e) {
        if (tooltips) showTooltip(e, that.parentNode);
      });

    });

    return chart;
  }


  //============================================================
  // Event Handling/Dispatching (out of chart's scope)
  //------------------------------------------------------------

  lines1.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  lines1.dispatch.on('elementMouseout.tooltip', function(e) {
    dispatch.tooltipHide(e);
  });

  lines2.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  lines2.dispatch.on('elementMouseout.tooltip', function(e) {
    dispatch.tooltipHide(e);
  });

  bars1.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  bars1.dispatch.on('elementMouseout.tooltip', function(e) {
    dispatch.tooltipHide(e);
  });

  bars2.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  bars2.dispatch.on('elementMouseout.tooltip', function(e) {
    dispatch.tooltipHide(e);
  });

  stack1.dispatch.on('tooltipShow', function(e) {
    //disable tooltips when value ~= 0
    //// TODO: consider removing points from voronoi that have 0 value instead of this hack
    if (!Math.round(stack1.y()(e.point) * 100)) {  // 100 will not be good for very small numbers... will have to think about making this valu dynamic, based on data range
      setTimeout(function() { d3.selectAll('.point.hover').classed('hover', false) }, 0);
      return false;
    }

    e.pos = [e.pos[0] + margin.left, e.pos[1] + margin.top],
    dispatch.tooltipShow(e);
  });

  stack1.dispatch.on('tooltipHide', function(e) {
    dispatch.tooltipHide(e);
  });

  stack2.dispatch.on('tooltipShow', function(e) {
    //disable tooltips when value ~= 0
    //// TODO: consider removing points from voronoi that have 0 value instead of this hack
    if (!Math.round(stack2.y()(e.point) * 100)) {  // 100 will not be good for very small numbers... will have to think about making this valu dynamic, based on data range
      setTimeout(function() { d3.selectAll('.point.hover').classed('hover', false) }, 0);
      return false;
    }

    e.pos = [e.pos[0] + margin.left, e.pos[1] + margin.top],
    dispatch.tooltipShow(e);
  });

  stack2.dispatch.on('tooltipHide', function(e) {
    dispatch.tooltipHide(e);
  });

    lines1.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  lines1.dispatch.on('elementMouseout.tooltip', function(e) {
    dispatch.tooltipHide(e);
  });

  lines2.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  lines2.dispatch.on('elementMouseout.tooltip', function(e) {
    dispatch.tooltipHide(e);
  });

  dispatch.on('tooltipHide', function() {
    if (tooltips) nv.tooltip.cleanup();
  });



  //============================================================
  // Global getters and setters
  //------------------------------------------------------------

  chart.dispatch = dispatch;
  chart.lines1 = lines1;
  chart.lines2 = lines2;
  chart.bars1 = bars1;
  chart.bars2 = bars2;
  chart.stack1 = stack1;
  chart.stack2 = stack2;
  chart.xAxis = xAxis;
  chart.yAxis1 = yAxis1;
  chart.yAxis2 = yAxis2;
  chart.legend = legend;
  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.x = function(_) {
    if (!arguments.length) return getX;
    getX = _;
    lines1.x(_);
    bars1.x(_);
    return chart;
  };

  chart.y = function(_) {
    if (!arguments.length) return getY;
    getY = _;
    lines1.y(_);
    bars1.y(_);
    return chart;
  };

  chart.yDomain1 = function(_) {
    if (!arguments.length) return yDomain1;
    yDomain1 = _;
    return chart;
  };

  chart.yDomain2 = function(_) {
    if (!arguments.length) return yDomain2;
    yDomain2 = _;
    return chart;
  };

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) return color;
    color = _;
    legend.color(_);
    return chart;
  };

  chart.showLegend = function(_) {
    if (!arguments.length) return showLegend;
    showLegend = _;
    return chart;
  };

  chart.tooltips = function(_) {
    if (!arguments.length) return tooltips;
    tooltips = _;
    return chart;
  };

  chart.tooltipContent = function(_) {
    if (!arguments.length) return tooltip;
    tooltip = _;
    return chart;
  };

  return chart;
}

function DumpObjectIndented(obj, indent)
{
  var result = "";
  if (indent == null) indent = "";

  for (var property in obj)
  {
    var value = obj[property];
    if (typeof value == 'string')
      value = "'" + value + "'";
    else if (typeof value == 'object')
    {
      if (value instanceof Array)
      {
        // Just let JS convert the Array to a string!
        value = "[ " + value + " ]";
      }
      else
      {
        // Recursive dump
        // (replace "  " by "\t" or something else if you prefer)
        var od = DumpObjectIndented(value, indent + "  ");
        // If you like { on the same line as the key
        //value = "{\n" + od + "\n" + indent + "}";
        // If you prefer { and } to be aligned
        value = "\n" + indent + "{\n" + od + "\n" + indent + "}";
      }
    }
    result += indent + "'" + property + "' : " + value + ",\n";
  }
  return result.replace(/,\n$/, "");
}

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

                if(settings['height']) {
                    var chartSelector = '#chart'+settings.id;
                    d3.select(d3.select(chartSelector + ' svg').node().parentNode)
                    .classed('dash-chart', false);

                    d3.select(chartSelector + ' svg')
                    .classed('dash-chart', false)
                    .style('height', settings['height'] + 'px');
                }
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

                var chartSelector = '#chart'+settings.id;
                d3.selectAll(chartSelector + ' .tick line').style('display', 'none');
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
                    .color(function(d) { return '#4785AB'; });

                if( settings.showTooltip ) {
                    chart.tooltipContent(function (key, x, val, graph) {
                        return data.data.messages[x];
                    });
                } else {
                    chart.tooltips(false);
                }

                if( settings.yformat ) {
                    chart.yAxis.tickFormat(d3.format(settings.yformat));
                } else {
                    chart.yAxis.tickFormat(d3.format(',.1f'));
                }

                if( settings.yShowMaxMin ) {
                    chart.yAxis.showMaxMin(true);
                } else {
                    chart.yAxis.showMaxMin(false);
                }
                d3.select("#chart"+settings.id+" svg")
                .datum(data.data.points)
                .transition().duration(500)
                .call(chart);
                var chartSelector = '#chart'+settings.id;
                d3.selectAll(chartSelector + ' .tick line').style('display', 'none');
                d3.selectAll(chartSelector + ' path.domain')[0].forEach(function(d,i) {
                    d3.select(d).style('display', 'none');
                });

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
                .tooltips(false)             //Show tooltips on hover
                .transitionDuration(350)
                .showControls(false);        //Allow user to switch between "Grouped" and "Stacked" mode.
                chart.showYAxis(false);
                if( settings.hideLegend ) {
                    chart.showLegend(false);
                }
                if( settings.valueFormat ) {
                    chart.valueFormat(d3.format(settings.valueFormat));
                }
                var chartSelector = '#chart'+settings.id;
                d3.select('#chart'+settings.id+' svg')
                .datum(data.data)
                .transition().duration(500)
                .call(chart);
                d3.selectAll(chartSelector + ' .tick line').style('display', 'none');

                if (!settings.hideLegend) {
                    d3.selectAll(chartSelector + ' .nv-series')[0].forEach(function(d,i) {
                      // select the individual group element
                      var group = d3.select(d);
                      // create another selection for the circle within the group
                      var circle = group.select('circle');
                      // grab the color used for the circle
                      var color = circle.style('fill');
                      // remove the circle
                      circle.remove();
                      // replace the circle with a path
                      group.append('path')
                        // match the path data to the appropriate symbol
                        .attr('d', d3.svg.symbol().type('square').size(160))
                        .attr('class', 'nv-legend-symbol')
                        // make sure the fill color matches the original circle
                        .style('fill', color);
                    });
                    d3.select(chartSelector + " .nv-legend")
                      .attr("transform", "translate(" + settings.legend_x + "," + settings.legend_y + ")");
                }

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
                .tooltips(false)             //Show tooltips on hover.
                .transitionDuration(350)
                .showControls(false)        //Allow user to switch between "Grouped" and "Stacked" mode.
                .showLegend(false);

                chart.showYAxis(false);
                chart.valueFormat(d3.format('p'));

                var chartSelector = '#chart'+settings.id;
                d3.select(chartSelector + ' svg')
                .datum(data.data)
                .transition().duration(500)
                .call(chart);
                d3.selectAll(chartSelector + ' .tick line').style('display', 'none');

                d3.selectAll(chartSelector + ' .nv-series')[0].forEach(function(d,i) {
                  // select the individual group element
                  var group = d3.select(d);
                  // create another selection for the circle within the group
                  var circle = group.select('circle');
                  // grab the color used for the circle
                  var color = circle.style('fill');
                  // remove the circle
                  circle.remove();
                  // replace the circle with a path
                  group.append('path')
                    // match the path data to the appropriate symbol
                    .attr('d', d3.svg.symbol().type('square').size(160))
                    .attr('class', 'nv-legend-symbol')
                    // make sure the fill color matches the original circle
                    .style('fill', color);
                });
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
                .donut(true)
                .donutRatio(0.20)
                .color(["#CC3A17", "#4785AB", "#8561A9", "#006A3B", "#87C440", "#363738", "#F5871F", "#A0CAE2"])
                ;

                var h = 250;
                var r = h/2;
                var arc = d3.svg.arc().outerRadius(r);
                var chartSelector = '#chart'+settings.id;
                d3.select(chartSelector +' svg')
                .datum(data.data)
                .transition().duration(350)
                .call(chart);

                //d3.selectAll(chartSelector + ' .nv-label text')
                //.attr("transform", function(d) {
                    //d.innerRadius = -250;
                    //d.outerRadius = r;
                    //return "translate(" + arc.centroid(d) + ")";}
                //)
                //.attr("text-anchor", "middle")
                d3.selectAll(chartSelector + ' .nv-label text').style('display', 'none');
                d3.selectAll(chartSelector +' .nv-slice')
                .on("mouseover", function(d) {
                    var orig_color = d3.select(this).attr("fill");
                    d3.select(this).attr("orig_color", orig_color);
                    d3.select(this).attr("fill", "#EEC03C");
                    var match = d3.selectAll(chartSelector + ' .nv-label text').filter(function(text, i) { return text['data']['label'] == d['data']['label'] });
                    match.text("");
                    match.append('svg:tspan').attr('x', 0).attr('dy', 0).attr('class', 'pie-hover-text').text(d['data']['label']);
                    match.append('svg:tspan').attr('x', 0).attr('dy', 15).attr('class', 'pie-hover-text').text(d['data']['percent']);
                    match.style('display', 'inline');
                }).on("mouseout", function(d) {
                    var match = d3.selectAll(chartSelector + ' .nv-label text').filter(function(text, i) { return text['data']['label'] == d['data']['label'] });
                    var node = match.node();
                    while(node.lastChild) {
                        node.removeChild(node.lastChild);
                    }
                    var orig_color = d3.select(this).attr("orig_color");
                    d3.select(this).attr("fill", orig_color);
                    match.style('display', 'none');
                });

                // All of our manual tweaks will be for naught if they click the legend
                for (var property in chart.legend.dispatch) {
                        chart.legend.dispatch[property] = function() { };
                }

                if (!settings.pie_x) {
                    settings.pie_x = 0;
                }
                if (!settings.pie_y) {
                    settings.pie_y = 0;
                }
                d3.select(chartSelector + ' .nv-pie')
                  .attr("transform", "translate(" + settings.pie_x + "," + settings.pie_y + ")");
                d3.selectAll(chartSelector + ' .nv-series')[0].forEach(function(d,i) {
                  // select the individual group element
                  var group = d3.select(d);
                  // create another selection for the circle within the group
                  var circle = group.select('circle');
                  // grab the color used for the circle
                  var color = circle.style('fill');
                  // remove the circle
                  circle.remove();
                  // replace the circle with a path
                  group.append('path')
                    // match the path data to the appropriate symbol
                    .attr('d', d3.svg.symbol().type('square').size(160))
                    .attr('class', 'nv-legend-symbol')
                    // make sure the fill color matches the original circle
                    .style('fill', color);
                });
                d3.select(chartSelector + " .nv-legend")
                  .attr("transform", "translate(-175,275)");
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
                var chart = multiChart()
                    .margin({top: 30, right: 60, bottom: 50, left: 70})
                    .tooltipContent(function (key, x, val, graph) {
                        return data.data.messages[key][graph.pointIndex];
                    });

                //Format x-axis labels with custom function.
                chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format(data.date_format)(new Date(d))
                })
                .showMaxMin(false);

                if(options['height']) {
                    chart.height(options['height']);
                }

                // Get normalised data for chart
                var seriesData = data.data.points;

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

                var chartSelector = '#chart'+settings.id;
                d3.select(chartSelector + ' svg')
                .datum(data.data.points)
                .call(chart);

                d3.select(chartSelector + ' .lines1Wrap')
                .moveToFront();

                d3.select(chartSelector + ' .lines2Wrap')
                .moveToFront();

                d3.select(chartSelector + " .legendWrap")
                  .attr("transform", "translate(" + settings.legend_x + "," + settings.legend_y + ")");
                d3.selectAll(chartSelector + ' path.domain')[0].forEach(function(d,i) {
                    d3.select(d).style('display', 'none');
                });
                d3.selectAll(chartSelector + ' .nv-series')[0].forEach(function(d,i) {
                  // select the individual group element
                  var group = d3.select(d);
                  // create another selection for the circle within the group
                  var circle = group.select('circle');
                  // grab the color used for the circle
                  var color = circle.style('fill');
                  // remove the circle
                  circle.remove();
                  // replace the circle with a path
                  group.append('path')
                    // match the path data to the appropriate symbol
                    .attr('d', d3.svg.symbol().type('square').size(160))
                    .attr('class', 'nv-legend-symbol')
                    // make sure the fill color matches the original circle
                    .style('fill', color);
                });

                d3.selectAll(chartSelector + " .nv-axisMaxMin")[0].forEach(function(d,i) {
                    d3.select(d).style('display', 'none');
                });

                // All of our manual tweaks will be for naught if they click the legend
                for (var property in chart.legend.dispatch) {
                        chart.legend.dispatch[property] = function() { };
                }
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
                var chart = multiChart()
                    .margin({top: 30, right: 60, bottom: 50, left: 70})
                    .tooltipContent(function (key, x, val, graph) {
                        if(key == "Benchmark %") {
                            return "Benchmark Engagement";
                        } else {
                            return data.data.messages[key][graph.pointIndex];
                        }
                    });

                if(!data.data) {
                    return chart;
                }

                //Format x-axis labels with custom function.
                chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format(settings.date_format)(new Date(d))
                })
                .showMaxMin(false);
                //.tickValues(data.data.points[2].values.map(function(d) { return d.x }));

                chart.yAxis1.showMaxMin(false);

                d3.select('#chart'+settings.id+' svg')
                .datum(data.data.points)
                .call(chart);

                var chartSelector = '#chart'+settings.id;

                d3.selectAll(chartSelector + ' path.domain')[0].forEach(function(d,i) {
                    d3.select(d).style('display', 'none');
                });

                d3.selectAll(chartSelector + ' .nv-series')[0].forEach(function(d,i) {
                  // select the individual group element
                  var group = d3.select(d);
                  // create another selection for the circle within the group
                  var circle = group.select('circle');
                  // grab the color used for the circle
                  var color = circle.style('fill');
                  // remove the circle
                  circle.remove();
                  // replace the circle with a path
                  group.append('path')
                    // match the path data to the appropriate symbol
                    .attr('d', d3.svg.symbol().type('square').size(160))
                    .attr('class', 'nv-legend-symbol')
                    // make sure the fill color matches the original circle
                    .style('fill', color);
                });
                d3.select(chartSelector + " .legendWrap")
                  .attr("transform", "translate(" + settings.legend_x + "," + settings.legend_y + ")");
                // All of our manual tweaks will be for naught if they click the legend
                for (var property in chart.legend.dispatch) {
                        chart.legend.dispatch[property] = function() { };
                }
                if(settings.has_circles) {
                    d3.selectAll(chartSelector + " circle.nv-point")[0].forEach(function(d,i) {
                        d3.select(d).style('stroke-opacity', '1');
                        d3.select(d).style('stroke-width', '4px');
                    });
                } else {
                    d3.selectAll(chartSelector + " circle.nv-point")[0].forEach(function(d,i) {
                        d3.select(d).style('display', 'none');
                    });
                }
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
    $.fn.choropleth = function(options){
        options.build_chart = function(settings, data){
            var width = $("#chart"+settings.id).width();
            var height = $("#chart"+settings.id).height();
            var projection = d3.geo.albersUsa()
            .scale(width)
            .translate([width / 2, height / 1.5]);

            var path = d3.geo.path()
            .projection(projection);

            var svg = d3.select("#chart"+settings.id+" svg")
            .attr("width", width)
            .attr("height", height);

            var usersById = d3.map();
            var namesById = d3.map();

            var quantize = d3.scale.quantize()
                .domain([0, 10])
                .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));

            data.data.forEach(function(d) {
                usersById.set(d.id, d.users);
                namesById.set(d.id, d.name);
            });


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

                svg.append("g")
                      .attr("class", "counties")
                        .selectAll("path")
                        .data(topojson.feature(us, us.objects.counties).features)
                        .enter().append("path")
                        .attr("class", function(d) { return quantize(usersById.get(d.id)); })
                        .attr("d", path)
                        .on("mouseover", function(d) {
                            var xPosition = d3.mouse(this)[0];
                            var yPosition = d3.mouse(this)[1] - 30;
                            svg.append("text")
                                .attr("id", "map_tooltip")
                                .attr("x", xPosition)
                                .attr("y", yPosition)
                                .attr("class", "overhead-popover")
                                .text(namesById.get(d.id) + " Audience: " + d3.round(usersById.get(d.id), 1) + " per 100,000");
                            d3.select(this)
                            .style("stroke", "#363738");
                        })
                        .on("mouseout", function(d) {
                            d3.select("#map_tooltip").remove();
                            d3.select(this)
                            .style("stroke", "none");
                        })
                    ;
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

(function($){
    $.fn.sparkline = function(options){
        options.build_chart = function(settings, data){
            nv.addGraph({
             generate: function() {
                 var chart = nv.models.sparkline()
                 .width(100)
                 .height(80)
                 .color(["#4785AB"])
                 d3.select('#chart'+settings.id+' svg')
                 .datum(data.data)
                 .call(chart);
                 return chart;
             }
            });
        };
        return $(this).chart(options);
    };
})(jQuery);


(function($){
    $.fn.list = function(settings){
        $(this).append("<div class=\"col-md-"+settings.columns+" dash-chart\"> \
            <h3>"+settings.name+"</h3> \
            <p><a href=\"https://www.facebook.com/topic/Jon-Hamm/112468628768413\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Jon Hamm</a></p> \
            <p><a href=\"https://www.facebook.com/topic/Germanwings/108639032494132\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Germanwings</a></p> \
            <p><a href=\"https://www.facebook.com/topic/Big-Crunch/104023519633436\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Big Crunch</a></p> \
            <p><a href=\"https://www.facebook.com/topic/Jesse-Eisenberg/104376719599635\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Jesse Eisenberg</a></p> \
            <p><a href=\"https://www.facebook.com/topic/Triassic/109285719089300\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Triassic</a></p> \
            <p><a href=\"https://www.facebook.com/topic/J-K-Rowling/112585118757481/\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>J.K. Rowling</a></p> \
            <p><a href=\"https://www.facebook.com/topic/New-York-Yankees/113063165374299\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>New York Yankees</a></p> \
            <p><a href=\"https://www.facebook.com/topic/Tataouine/107750969247738\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Tataouine</a></p> \
            <p><a href=\"https://www.facebook.com/topic/Vietnam-Womens-Memorial/102916926429233\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Vietnam Women&#39;s Memorial</a></p> \
            <p><a href=\"https://www.facebook.com/topic/Phil-Robertson/107609529268893\"><img class=\"trending\" src=\"/static/img/fb-trending.png\"></img>Phil Robertson</a></p> \
        </div>");
    };
})(jQuery);
