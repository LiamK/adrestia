(function () {
'use strict';

/*
var threeWayCalculator = angular.module('threeWayCalculator', ['chart.js']);
*/
var threeWayCalculator = angular.module('threeWayCalculator', ['nvd3','at.multirange-slider']);

threeWayCalculator.filter('percentage', ['$filter', function ($filter) {
	return function (input, decimals) {
	      return $filter('number')(input * 100, decimals) + '%';
	};
}]);

threeWayCalculator.controller('CalculatorCtrl', function ($scope) {
	var electorate_dem = .30;
	var electorate_rep = .26;
	var electorate_ind = .43;

        $scope.electorate = {
           'dem':electorate_dem,
           'rep':electorate_rep,
           'ind':electorate_ind,
	}

	function Candidate(name, est_dem, est_rep, est_ind) {
	    this.name = name;
            this.est = {
	        'est_dem': { 'p':est_dem },
	        'est_rep': { 'p':est_rep },
	        'est_ind': { 'p':est_ind }
	    }
	    this.get_total = function() { 
	        var ret = 
		    this.est.est_dem.p * electorate_dem +
	            this.est.est_rep.p * electorate_rep +
	            this.est.est_ind.p * electorate_ind;
                console.log(this.name, ret);
		return ret
	    }
            this.values = [
	        this.est_dem,
	        this.est_rep,
	        this.est_ind
	    ]
	}
	function Party(name, electorate, est_bernie, est_hillary, est_trump) {
	    this.name = name;
	    this.electorate = electorate;
            this.est = {
	        'est_bernie': { 'p':est_bernie },
	        'est_hillary': { 'p':est_hillary },
	        'est_trump': { 'p':est_trump }
	    }
	    this.get_total = function() { 
	        var ret = 
                    this.electorate * (
		    this.est.est_bernie.p +
	            this.est.est_hillary.p +
	            this.est.est_ind.p)
                console.log(this.name, ret);
		return ret
	    }
	}

	var est_bernie_dem = .39;
	var est_hillary_dem = .49;
	var est_trump_dem = .12;

	var est_bernie_rep = .17;
	var est_hillary_rep = .13;
	var est_trump_rep = .70;

	var est_bernie_ind = .63;
	var est_hillary_ind = .17;
	var est_trump_ind = .20;

        $scope.democrat = new Party('Democrat', electorate_dem,
            est_bernie_dem,
            est_hillary_dem,
            est_trump_dem)

        $scope.republican = new Party('Republican', electorate_rep,
            est_bernie_rep,
            est_hillary_rep,
            est_trump_rep)

        $scope.independent = new Party('independent', electorate_ind,
            est_bernie_ind,
            est_hillary_ind,
            est_trump_ind)



	$scope.bernie = new Candidate('Bernie', 
		est_bernie_dem,
		est_bernie_rep,
		est_bernie_ind
	);
	$scope.hillary = new Candidate('Hillary', 
		est_hillary_dem,
		est_hillary_rep,
		est_hillary_ind
	);
	$scope.trump = new Candidate('Trump', 
		est_trump_dem,
		est_trump_rep,
		est_trump_ind
	);
/*
	$scope.bernie = {
		'd': {'p':est_bernie_dem},
		'r': {'p':est_bernie_repub},
		'i': {'p':est_bernie_indie}
        } 
	$scope.hillary = {
		'd':est_hillary_dem,
		'r':est_hillary_repub,
		'i':est_hillary_indie
        };
	$scope.trump = {
		'd':est_trump_dem,
		'r':est_trump_repub,
		'i':est_trump_indie
        };
*/
/*
	$scope.bernie_total = $scope.bernie.get_total()
	$scope.hillary_total = $scope.hillary.get_total()
	$scope.trump_total = $scope.trump.get_total()
*/


/*
        $scope.data = [
            { key:$scope.bernie.name, value:$scope.bernie.get_total() },
            { key:$scope.hillary.name, value:$scope.hillary.get_total() },
            { key:$scope.trump.name, value:$scope.trump.get_total() }
	];
*/
/*
        $scope.data = function() { return [
            { color:'green', key:$scope.bernie, value:$scope.bernie },
            { color:'blue', key:$scope.hillary, value:$scope.hillary },
            { color:'red', key:$scope.trump, value:$scope.trump }
	]};
*/
	function get_bernie_total() {
            var total;
            for (i = 0; i < $scope.parties.length; i++) {
               total += parties[i].est.est_bernie;
            }
            return total
        }
	function get_hillary_total() {
            var total;
            for (i = 0; i < $scope.parties.length; i++) {
               total += parties[i].est.est_hillary;
            }
            return total
        }
	function get_hillary_total() {
            var total;
            for (i = 0; i < $scope.parties.length; i++) {
               total += parties[i].est.est_hillary;
            }
            return total
        }

        $scope.bernie_total = function() {
		return $scope.democrat.est.est_bernie.p +
		$scope.republican.est.est_bernie.p +
		$scope.independent.est.est_bernie.p;
       }

        $scope.hillary_total = function() {
		return $scope.democrat.est.est_hillary.p +
		$scope.republican.est.est_hillary.p +
		$scope.independent.est.est_hillary.p;
	} 

        $scope.trump_total = function() {
		return $scope.democrat.est.est_trump.p +
		$scope.republican.est.est_trump.p +
		$scope.independent.est.est_trump.p;
        } 

        console.log('wtf', $scope.democrat.est.est_bernie);
        console.log('totals', $scope.bernie_total, $scope.hillary_total, $scope.trump_total);

        $scope.data = function() { return [
            { color:'green', key:$scope.bernie, value:$scope.bernie_total() },
            { color:'blue', key:$scope.hillary, value:$scope.hillary_total() },
            { color:'red', key:$scope.trump, value:$scope.trump_total() }
	]};

        //$scope.$watchGroup(['democrat', 'republican', 'independent'],
        $scope.$watchGroup(['democrat', 'republican', 'independent'],
            function(newValues, oldValues, scope) {
            console.log('reset scope.data')
		$scope.data = [
            { color:'green', key:$scope.bernie, value:$scope.bernie_total() },
            { color:'blue', key:$scope.hillary, value:$scope.hillary_total() },
            { color:'red', key:$scope.trump, value:$scope.trump_total() }
		];
	    }
	);

//	var bernie_dem = electorate_dem * est_bernie_dem;
//	var hillary_dem = electorate_dem * est_hillary_dem;
//	var trump_dem = electorate_dem * est_trump_dem;
//	var bernie_repub = electorate_repub * est_bernie_repub;
//	var hillary_repub = electorate_repub * est_hillary_repub;
//	var trump_repub = electorate_repub * est_trump_repub;
//	var bernie_indie = electorate_indie * est_bernie_indie;
//	var hillary_indie = electorate_indie * est_hillary_indie;
//	var trump_indie = electorate_indie * est_trump_indie;
//
//	var bernie_total = bernie_dem + bernie_repub + bernie_indie;
//	var hillary_total = hillary_dem + hillary_repub + hillary_indie;
//	var trump_total = trump_dem + trump_repub + trump_indie;
//
//	$scope.bernie = {
//		'name':'Bernie',
//		'dem':est_bernie_dem,
//		'repub':est_bernie_repub,
//		'indie':est_bernie_indie,
//		'total':bernie_total
//	}
//	$scope.hillary = {
//		'name':'Hillary',
//		'dem':est_hillary_dem,
//		'repub':est_hillary_repub,
//		'indie':est_hillary_indie,
//		'total':hillary_total
//	}
//	$scope.trump = {
//		'name':'Trump',
//		'dem':est_trump_dem,
//		'repub':est_trump_repub,
//		'indie':est_trump_indie,
//		'total':trump_total
//	}

	$scope.candidates = [
		$scope.bernie,
		$scope.hillary,
		$scope.trump
	]
	$scope.parties = [
		$scope.democrat,
		$scope.republican,
		$scope.independent
	]

	/*
	$scope.$watchCollection("candidates", function(newValue, oldValue) {
	    if (newValue !== oldValue) {
		    for c in $scope.candidates {
			    c.total = c
		    }
	    }
	}

	$scope.labels = [$scope.bernie.name, $scope.hillary.name, $scope.trump.name];
	$scope.data = [$scope.bernie.get_total(), $scope.hillary.get_total(), $scope.trump.get_total()];
	*/
var colors = ['magenta', 'cyan', 'yellow']
$scope.options = {
    chart: {
      type: 'pieChart',
      height: 400,
      width: 700,
      x: function(d) {
        if (d.key.length > 30) {
          return d.key.name.substr(0, 30) + "...";
        } else {
          console.log('x -- d', d)
          console.log('name', d.key.name)
          return d.key.name;
        }
      },
      y: function(d) {
        console.log('y -- d', d)
        console.log('value', d.value, d.value[0])
        return d.value;
      },
      color: function(d,i) {
        console.log('color value', d, i)
        return (d && d.color) || colors[i % colors.length]
      },
      showLabels: true,
      transitionDuration: 500,
      legend: {
        vers: 'furious',
        dispatch: {
          legendMouseover: function(o) {
            if (tooltip.hidden()) {
              var data = {
                series: {
                  key: o.key.name,
                  value: o.value.get_total() * 100 + "%",
                  color: o.color
                }
              };
              tooltip.data(data)
                .hidden(false);
            }
            tooltip.position({
              top: d3.event.pageY,
              left: d3.event.pageX
            })();
          },
          legendMouseout: function(o) {
            tooltip.hidden(true);
          }
        }
      },
      legendPosition: 'right',
      valueFormat: function(d) {
        return d * 100 + "%";
      }
    }
  };
});
/*
threeWayCalculator.config(function (ChartJsProvider) {
	  ChartJsProvider.setOptions({ colours : [ '#00AA00', '#0000DD', '#DD0000', '#46BFBD', '#FDB45C', '#949FB1', '#4D5360'] });
}); 
*/

})();

