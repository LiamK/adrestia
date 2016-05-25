(function () {
  'use strict';

  angular.module('myApp.controllers', ['nvd3'])
    .controller('ParsetsCtrl', ['$scope', function ($scope) {
      $scope.election = dataJSON.data;
      $scope.electorate = dataJSON.percentOfElectorate;
      $scope.party = [1,2,3];

      $scope.totals =  [
          { key: "",
            values: [
                { 'label': 'Bernie', 'value': 0 },
                { 'label': 'Hillary', 'value': 0 },
                { 'label': 'Trump', 'value': 0 }
              ]
          }
        ]

      $scope.$watch('totals', function(newVals) {
        $scope.totals = newVals;
      }, true);

      $scope.options = {
          chart: {
                type: 'multiBarHorizontalChart',
                showControls: false,
                showLegend: false,
                //color: ["#2f107a", "#07586f", "#b35d06"],
                //http://paletton.com/#uid=74i1W0km6lR2qrsccoMu+mqUFfi
                barColor: ["#2f107a", "#07487f", "#b35d06"],
                //height: 350,
                margin : {
                    top: 20,
                    right: 20,
                    bottom: 50,
                    left: 55
                },
                x: function(d){return d.label;},
                y: function(d){return d.value;},
                showValues: false,
                valueFormat: function(d){
                    return d3.format(',.2f')(d);
                },
                duration: 500,
                xAxis: {
                    //axisLabel: 'Candidate'
                },
                yAxis: {
                    axisLabel: 'Percent of Total Popular Vote',
                    axisLabelDistance: -5
                },
                tooltip: {
                    contentGenerator: function(d) {
                        return '<span>'+d.data.label+'</span>' +
                               '<span>&nbsp;'+d3.format(',.2f')(d.data.value)+'%</span>';
                    }
                }
            }
        };
    }]);

}());
