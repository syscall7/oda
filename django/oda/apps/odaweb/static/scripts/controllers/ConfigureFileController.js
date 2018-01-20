"use strict";

odaApplication.controller('ConfigureFileController', function($scope, $modalInstance, $http, fileData) {

    console.log('ConfigureFileController', fileData);

    $scope.loading = false;

    $scope.data = {
        fileData: fileData,
        sandbox: false
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.ok = function () {

        $scope.loading = true;

        var computeSelected = function(platformOptions) {
            var selected = [];
            for (var i=0; i<platformOptions.length; i++) {
                if (platformOptions[i].selectedValue != 'DEFAULT') {
                    selected.push(platformOptions[i].selectedValue);
                }
            }
            return selected;
        };

        var options = computeSelected($scope.options.platformOptions);
        console.log('options', options);

        var options = {
            architecture: $scope.options.architecture,
            base_address: $scope.options.base_address,
            endian: $scope.options.endian,
            selected_opts: computeSelected($scope.options.platformOptions)
        };

        OdbFile.setOptionsFor(fileData.short_name, fileData.revision, options)
            .success(function(){
            $modalInstance.close({
                sandbox: $scope.data.sandbox,
                shortName: fileData.short_name,
                revision: fileData.revision

            });
        });
    };

    var arch = fileData.arch;
    $scope.optionsTemplate = function() {
        var view = '/odaweb/optionsview?arch=' + arch
        return view;
    };

    $scope.architectureLocked = (arch != 'UNKNOWN!');

    $scope.options = {
        architecture: fileData.arch,
        endian: 'DEFAULT'
    };

    $scope.optionsUpdated = function() {
        console.log($scope.options);
    };

    /* determine if we support running the file in the sandbox */
    $scope.runtimeSupported = function() {
        var enabled = false;
        /* TODO: Add other targets that will run in the Windows XP VM */
        /* Disable all targets for now until we enable support for sandboxing
        if (fileData.target == 'pei-i386') {
            enabled = true;
        }
        */
        return enabled;
    };

    $scope.architectures = window.system.architectures;
    $scope.endians = window.system.endians;

    var updateArchitectureOptions = function() {
        $http.get('/odaweb/api/disassembler/0/options/?arch=' + $scope.options.architecture).success(function(data){            console.log('OPTIONS', data);
            $scope.options.platformOptions = data.options;
            $.each($scope.options.platformOptions, function(i, po){
                po.selectedValue = 'DEFAULT'
            });
        });
    };
    updateArchitectureOptions();

    $scope.$watch('options.architecture', function(){
        updateArchitectureOptions()
    });


    /** Platform Options Portion **/
    /*$http.get('/odaweb/api/disassembler/0/architectures/').success(function(data){
        $scope.architectures = data.architectures
        $scope.endians = data.endians
    });
    var updateArchitectureOptions = function() {
        $http.get('/odaweb/api/disassembler/0/options/?arch=' + $scope.options.architecture).success(function(data){
            console.log('OPTIONS', data);
            $scope.options.platformOptions = data.options;
            $.each($scope.options.platformOptions, function(i, po){
                po.selectedValue = 'DEFAULT'
            });
        });
    };
    updateArchitectureOptions();*/
});