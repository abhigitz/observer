var appMod = angular.module('ngOutstandingApp', []);

appMod.controller('ngOrderController', ['$scope', '$http', function($scope, $http) {
    var api = "/api/get_pending_orders_data";
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
    var api = "/api/get_outstanding_pmt_data";
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

appMod.controller('ngFormCController', ['$scope', '$http', function($scope, $http) {
  var api = '/api/get_formC_data';
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

appMod.controller('ngRawMaterialController', ['$scope', '$http', function($scope, $http) {
  var api = '/api/get_rawmaterial_data';
  var postData = null;

  $http.post(api, postData).success(function(data, status, headers, config) {
    $scope.allParts = data["parts"];
    $scope.showVerbatimOnTop = data["showVerbatimOnTop"];
    $scope.statusNote = "";
  }).error(function(data, status, headers, config){
    $scope.statusNote = "There was an error. Thats all there is to it. Please try again after some time";
  });

  $scope.statusNote = "Fetching data...";

}]);

appMod.controller('ngFinishedGoodsController', ['$scope', '$http', function($scope, $http) {
  var api = '/api/get_finished_goods_data';
  var postData = null;

  $http.post(api, postData).success(function(data, status, headers, config) {
    $scope.allModels = data["models"];
    $scope.showVerbatimOnTop = data["showVerbatimOnTop"];
    $scope.statusNote = "";
  }).error(function(data, status, headers, config){
    $scope.statusNote = "There was an error. Thats all there is to it. Please try again after some time";
  });

  $scope.statusNote = "Fetching data...";

}]);

