odaApplication.controller('RuntimeDumpController', function SymbolsController($scope, $http, $window, odbFile, odaSession) {
    $scope.results = odbFile.runtimeReport;
});