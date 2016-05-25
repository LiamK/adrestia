(function () {
  'use strict';

  angular.module('myApp.directives')
    .directive('d3Parsets', ['$window', '$timeout', function($window, $timeout) {
    return {
      restrict: 'EA',
      scope: {
        data: "=",
        totals: "=",
        electorate: "="
      },
      link: function(scope, iElement, iAttrs) {
        var d3 = $window.d3;
        var svgWrap = d3.select(iElement[0])
          .append("svg")
          .attr("width", "100%");

        // on window resize, re-render d3 canvas
        window.onresize = function() {
          return scope.$apply();
        };
        scope.$watch(function(){
            return angular.element(window)[0].innerWidth;
          }, function(){
            return scope.render(scope.data);
          }
        );

        var get_totals = function(newVals) {
          var bernie_total = 0,
              hillary_total = 0,
              trump_total = 0;

          if (newVals) {
            for (var i=0; i<newVals.length; i++) {
              var row = newVals[i];
              if (row['Candidate'] == 'Bernie') {
                bernie_total += row['Count']*scope.electorate[row['Party']]/100
              }
              if (row['Candidate'] == 'Hillary') {
                hillary_total += row['Count']*scope.electorate[row['Party']]/100
              }
              if (row['Candidate'] == 'Trump') {
                trump_total += row['Count']*scope.electorate[row['Party']]/100
              }
            }
          }
          return [{ key: "Vote Percent",
                    values: [
  	                   { 'label': 'Bernie', 'value': bernie_total },
  	                   { 'label': 'Hillary', 'value': hillary_total },
  	                   { 'label': 'Trump', 'value': trump_total }
                    ]
                 }]
        };

        // watch for data changes and re-render
        scope.$watch('data', function(newVals) {
          scope.totals = get_totals(newVals);
          return scope.render(scope.data);
        }, true);



        // define render function
        scope.render = function(data){
          // remove all previous items before render
          svgWrap.selectAll("*").remove();

          // setup variables
          var width = d3.select(iElement[0])[0][0].offsetWidth - 20,
            height = width *0.55;

          // set the height based on the calculations above
          svgWrap.attr('height', height);

          //set current function for d3.parsets
          function categoryTooltipFormat(d) {
            return "<h4>"+d.name + "<br>" + d3.round(d.count,2)+"%</h4>";
          }

          function tooltipFormat(d) {
            var count = d.count,
              path = [],
              party, sign;
            if (d.dimension == "Party") {
              party = d.name;
            }
            while (d.parent) {
              if (d.name) path.unshift(d.name);
              d = d.parent;
            }
            if (party == undefined) {
              party = path[0];
              sign = " > "
            } else {
              sign = " < "
            }
            return "<h4>"+path.join(sign) + "<br>" + d3.round((count*100/scope.electorate[party]), 2)+"%</h4>";
          }

          function valueAccessor(d) {
            return d["Count"]*scope.electorate[d["Party"]]/100;
          }

          var chart = $window.d3.parsets()
            .dimensions(["Party", "Candidate"])
            .value(valueAccessor)
            .width(width)
            .height(height)
            .spacing(30)
            .tension(0.75)
            .tooltip(tooltipFormat)
            .categoryTooltip(categoryTooltipFormat);

          var vis = svgWrap.append("svg")
            .attr("width", chart.width())
            .attr("height", chart.height());
          vis.datum(data).call(chart);

        };
      }
    };
  }]);
}());
