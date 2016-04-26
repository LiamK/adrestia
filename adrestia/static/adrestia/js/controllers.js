(function () {
'use strict';

var threeWayCalculator = angular.module('threeWayCalculator', ['chart.js']);

threeWayCalculator.filter('percentage', ['$filter', function ($filter) {
	return function (input, decimals) {
	      return $filter('number')(input * 100, decimals) + '%';
	};
}]);

threeWayCalculator.controller('CalculatorCtrl', function ($scope) {
	var electorate_dem = .30;
	var electorate_repub = .26;
	var electorate_indie = .43;

	var est_bernie_dem = .3975;
	var est_hillary_dem = .4924;
	var est_trump_dem = .11;
	var est_bernie_repub = .19;
	var est_hillary_repub = .19;
	var est_trump_repub = .60;
	var est_bernie_indie = .4570;
	var est_hillary_indie = .09;
	var est_trump_indie = .2590;

	var bernie_dem = electorate_dem * est_bernie_dem;
	var hillary_dem = electorate_dem * est_hillary_dem;
	var trump_dem = electorate_dem * est_trump_dem;
	var bernie_repub = electorate_repub * est_bernie_repub;
	var hillary_repub = electorate_repub * est_hillary_repub;
	var trump_repub = electorate_repub * est_trump_repub;
	var bernie_indie = electorate_indie * est_bernie_indie;
	var hillary_indie = electorate_indie * est_hillary_indie;
	var trump_indie = electorate_indie * est_trump_indie;

	var bernie_total = bernie_dem + bernie_repub + bernie_indie;
	var hillary_total = hillary_dem + hillary_repub + hillary_indie;
	var trump_total = trump_dem + trump_repub + trump_indie;

	$scope.bernie = {
		'name':'Bernie',
		'dem':est_bernie_dem,
		'repub':est_bernie_repub,
		'indie':est_bernie_indie,
		'total':bernie_total
	}
	$scope.hillary = {
		'name':'Hillary',
		'dem':est_hillary_dem,
		'repub':est_hillary_repub,
		'indie':est_hillary_indie,
		'total':hillary_total
	}
	$scope.trump = {
		'name':'Trump',
		'dem':est_trump_dem,
		'repub':est_trump_repub,
		'indie':est_trump_indie,
		'total':trump_total
	}

	$scope.candidates = [
		$scope.bernie,
		$scope.hillary,
		$scope.trump
	]

	$scope.labels = [$scope.bernie.name, $scope.hillary.name, $scope.trump.name];
	$scope.data = [$scope.bernie.total, $scope.hillary.total, $scope.trump.total];
});
threeWayCalculator.config(function (ChartJsProvider) {
	  ChartJsProvider.setOptions({ colours : [ '#00AA00', '#0000DD', '#DD0000', '#46BFBD', '#FDB45C', '#949FB1', '#4D5360'] });
}); 

})();

