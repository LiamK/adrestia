(function () {
  'use strict';

  angular.module('myApp.directives')
    .directive('d3Slider', ['$window', function($window) {
      return {
        restrict: 'EA',
        scope: {
          data: "=",
          party: "="
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

          // watch for data changes and re-render
          scope.$watch('data', function(newVal) {
            return scope.render(newVal);
          }, true);

          // define render function
          scope.render = function(dataTotal){
            var data;
            if (scope.party == 1) {data = dataTotal.slice(0,3)}
            else if (scope.party == 2) {data = dataTotal.slice(3,6)}
            else if (scope.party == 3) {data = dataTotal.slice(6,9)}
            // remove all previous items before render
            svgWrap.selectAll("*").remove();

            // setup variables
            var widthParent = d3.select(iElement[0])[0][0].offsetWidth - 20,
              heightParent = widthParent *0.15;

            // set the height based on the calculations above
            svgWrap.attr('height', heightParent/1.5);

            var margin = {top: 15, right: 15, bottom: 10, left: 15},
              width = widthParent - margin.left - margin.right,
              height = heightParent - margin.top - margin.bottom;

            var x = d3.scale.linear()
              .domain([0, 100])
              .range([0, width]);
            var brush = d3.svg.brush()
              .x(x)
              .extent([data[0].Count, 100-data[2].Count])
              .on("brushstart", brushstart)
              .on("brush", brushmove)
              .on("brushend", brushend);

            var svg = svgWrap.append("svg")
              .attr("width", width + margin.left + margin.right)
              .attr("height", height + margin.top + margin.bottom)
              .append("g")
              .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	    /* scale on bottom of slider */
	    /*
            svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + height/4 + ")")
              .call(d3.svg.axis().scale(x).orient("bottom"));
            */

            var brushg = svg.append("g")
              .attr("class", "brush")
              .call(brush);

            var text1 = svg.append("text")
              .attr("class", "text-svg")
              .attr("text-anchor", "middle")
              .attr("dy", 0.06*width)
              .attr("dx", width*0.15);

            var text2 = svg.append("text")
              .attr("class", "text-svg")
              .attr("text-anchor", "middle")
              .attr("dy", 0.06*width)
              .attr("dx", width*0.5);

            var text3 = svg.append("text")
              .attr("class", "text-svg")
              .attr("text-anchor", "middle")
              .attr("dy", 0.06*width)
              .attr("dx", width*0.85);

            brushg.insert("rect",".extent")
              .attr("class", "party")
              .attr("x",0)
              .attr("width", data[0].Count*width/100);

            brushg.selectAll(".resize").append("image")
              .attr("class", "icon")
              .attr("xlink:href", "/static/threeway/app/css/images/bookmark.svg")
              .attr("y", -0.0175*width)
              .attr("x", -0.043*width)
              .attr("width", 0.085*width)
              .attr("height", 0.055*width);

            brushg.selectAll("rect")
              .attr("height", height/4);

            brushg.select("rect.background")
              .style({visibility: "visible"});

            brushstart();
            brushmove();

            function brushstart() {
              svg.classed("selecting", true);
            }

            function brushmove() {
              var extent = brush.extent();
              brushg.select("rect.party")
                .attr("width",extent[0]*width/100);
              data[0].Count = extent[0];
              data[1].Count = extent[1]-extent[0];
              data[2].Count = 100-extent[1];
              text1.text(data[0].Candidate+": "+d3.round(data[0].Count,2)+"%");
              text2.text(data[1].Candidate+": "+d3.round(data[1].Count,2)+"%");
              text3.text(data[2].Candidate+": "+d3.round(data[2].Count,2)+"%");
            }

            function brushend() {
              svg.classed("selecting", !d3.event.target.empty());
              scope.$apply();
            }

          };

        }
      };
    }]);
}());
