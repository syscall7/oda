odaApplication.controller('OptionsViewController', function OptionsViewController($scope, $http, $window, odbFile) {

    var arch = odbFile.binary.arch;
    $scope.optionsTemplate = function() {
        var view = '/odaweb/optionsview?arch=' + arch
        return view;
    };

    $scope.$on('platformOptionsChanged', function(event, options){
        console.log(options);
        arch = options.arch.trim();
    });
});
