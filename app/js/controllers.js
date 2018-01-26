'use strict';

/* Controllers */
var susyandsteve = angular.module('susyandsteve', []);

susyandsteve.controller('playersController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/players').success(function(data) {
      $scope.event = data.event;
      $scope.players = data.players;
     });
    $scope.orderProp = 'name';
    $scope.year = new Date().getFullYear();
  }]);

susyandsteve.controller('restaurantController', ['$scope', '$http',
  function($scope, $http) {
    $http.get('/restaurants?output=json').success(function(data) {
      $scope.restaurants = data.restaurants;
    });   
    $scope.orderProp = 'Name';
  }]);
