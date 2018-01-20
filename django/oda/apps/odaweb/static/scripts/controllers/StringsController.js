odaApplication.controller('StringsController', function StringsController($scope, $http, $window, odbFile) {

    $scope.strings = odbFile.strings;

    $scope.setPosition = function(position) {
        console.log('set position', position);
        odbFile.setActiveAddr(position);
    }
});