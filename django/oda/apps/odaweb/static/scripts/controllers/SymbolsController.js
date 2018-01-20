"use strict";

odaApplication.controller('SymbolsController', function SymbolsController($scope, $http, $window, odbFile) {

    $scope.symbols = odbFile.symbols;

    $scope.isDefined = function(symbol) {
        if (symbol.offset != 0)
            return true;
        else
            return false;

    };

    odbFile.on(ODB_EVENTS.CHANGED, function(){
        $scope.$apply();
    });

    $scope.setPosition = function(position) {
        console.log('set position', position);
        odbFile.setActiveAddr(position);
    };
});