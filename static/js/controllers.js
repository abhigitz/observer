var appMod = angular.module('ngOutstandingApp', []);

appMod.controller('ngOrderController', ['$scope', '$http', function($scope, $http) {
    var api = "/api/get-pending-orders-data";
    var postData = null;

    $http.post(api, postData).success(function(data, status, headers, config) {
        //TODO: prepend ")]}',\n"
        //TODO: use while(1);
        $scope.data = data;
        $scope.statusNote = "";
    }).error(function(data, status, headers, config){
        $scope.statusNote = "There was an error. Thats all there is to it. Please try again after some time";
    });

    $scope.statusNote = "";

}]);

appMod.controller('ngPmtController', ['$scope', '$http', function($scope, $http) {
    var api = "/api/get-outstanding-pmt-data";
    var postData = null;

    $scope.CalculateTotalOutstanding = function() {
        $scope.statusNote = "Churning data...";
        var total = 0;
        for(var i = 0; i< $scope.comps.customers.length; i++) {
            total += $scope.subtotal($scope.comps.customers[i]);
        }
        return "Rs. "+total;
    }

    $http.post(api, postData).success(function(data, status, headers, config) {
        //TODO: prepend ")]}',\n"
        //TODO: use while(1);
        $scope.comps = data;
        $scope.totalOutstanding = $scope.CalculateTotalOutstanding();
        $scope.statusNote = "";
    }).error(function(data, status, headers, config){
      $scope.totalOutstanding = "Fetching data...";
      $scope.statusNote = "There was an error. Thats all there is to it. Please try again after some time";
    });

    $scope.subtotal = function(comp) {
      var total = 0;
      for(var i =0, len = comp.bills.length; i<len; i++) {
        total += parseInt(comp.bills[i]["ba"]);
      }
      return total;
    }
    $scope.totalOutstanding = "Fetching data...";
    $scope.statusNote = "";

}]);

appMod.controller('ngKMPOController', ['$scope', '$http', function($scope, $http) {
  var api = "/api/get-km-pending-po-data";
  var postData = null;

  $http.post(api, postData).success(function(data, status, headers, config) {
    $scope.kmpo = data["kmOrders"];
    $scope.showVerbatimOnTop = data["showVerbatimOnTop"];
    $scope.showVerbatimOnTopDateISO = data["showVerbatimOnTopDateISO"];
    $scope.statusNote = "";
  }).error(function(data, status, headers, config){
    $scope.statusNote = "There was an error. Thats all there is to it. Please try again after some time";
  });

  $scope.statusNote = "Fetching data...";

  $scope.timeDiffInDaysFromNow = function(isoDateAsString) {
    var millisecondsPerDay = 1000 * 60 * 60 * 24;
    var millisBetween = new Date() - new Date(isoDateAsString);
    var days = millisBetween / millisecondsPerDay;
    return Math.floor(days);
  };


}]);

appMod.controller('ngFormCController', ['$scope', '$http', function($scope, $http) {
  var api = '/api/get-formC-data';
  var postData = null;

  $http.post(api, postData).success(function(data, status, headers, config) {
    $scope.allCompsFormC = data["allCompsFormC"];
    $scope.showVerbatimOnTop = data["showVerbatimOnTop"];
    $scope.statusNote = "";
  }).error(function(data, status, headers, config){
    $scope.statusNote = "There was an error. Thats all there is to it. Please try again after some time";
  });

  $scope.statusNote = "Fetching data...";

}]);

