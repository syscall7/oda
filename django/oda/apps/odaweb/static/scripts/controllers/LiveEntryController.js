odaApplication.controller('LiveEntryController', function LiveEntryController($scope, $http, $window, odbFile) {

    $scope.oda_master = odbFile.oda_master;

    $scope.resizeTextArea = function() {
        textAreaHeight = $(window).height() - $('#hex').offset().top - $('#statusBar').height() - 20;
        $('#hex').css('height',textAreaHeight + 'px');
    };
    $scope.resizeTextArea();

    angular.element(document).ready(function () {

        /* attach a resize handler */
        $(window).resize(function(){
            $scope.resizeTextArea();
        });

        /* run the resize function now that the document is ready */
        $scope.resizeTextArea();
    });

    $scope.liveEntryText = odbFile.binary.text;



    var updateText = _.debounce(function() {
        odbFile.setLiveEntryText($scope.liveEntryText);
        /*.then(function(){
            $scope.entryError = null;
        }).catch(function(ex ){
            $scope.entryError = ex;
        }); */
    }, 350);

    $scope.liveEntryChange = function() {
        updateText();
    };

    $scope.options = {
        architecture: $scope.oda_master.binary.options.architecture,
        endian: $scope.oda_master.binary.options.endian,
        base_address: "" + $scope.oda_master.binary.options.base_address
    };

    if ($scope.options.base_address.lastIndexOf('0x', 0) !== 0) {
        $scope.options.base_address = '0x' + $scope.options.base_address;
    }

    odbFile.on(ODB_EVENTS.LIVE_ENTRY_UPDATE, function(){
         $scope.$apply(function(){$scope.entryError = null;});
    });

    odbFile.on(ODB_EVENTS.ERROR, function(error){
        if (error.code == ODB_ERRORS.LIVE_ENTRY_FAILED) {
            $scope.$apply(function(){$scope.entryError = error;});

        }
    });

    $scope.optionsUpdated = function(reload) {
        console.log('optionsUpdated', $scope.options);

        var computeSelected = function(platformOptions) {
            var selected = [];
            for (var i=0; i<platformOptions.length; i++) {
                if (platformOptions[i].selectedValue != 'DEFAULT') {
                    selected.push(platformOptions[i].selectedValue);
                }
            }
            return selected;
        };

        var options = {
            architecture: $scope.options.architecture,
            base_address: $scope.options.base_address,
            endian: $scope.options.endian,
            selected_opts: computeSelected($scope.options.platformOptions)
        };
        console.log('selecteod OPTIOSN', options);

        var p = odbFile.setOptions(options);

        if (reload) {
            p.success(function(){
                window.location.href = '/odaweb/' + odbFile.shortName + '/' + odbFile.revision;
            });
        }
    };


    /** Platform Options Portion **/
    $scope.architectures = window.system.architectures;
    $scope.endians = window.system.endians;

    var updateArchitectureOptions = function() {
        $http.get('/odaweb/api/disassembler/0/options/?arch=' + $scope.options.architecture).success(function(data){
            console.log('OPTIONS', data);
            $scope.options.platformOptions = data.options;
            $.each($scope.options.platformOptions, function(i, po){
                po.selectedValue = null;

                for(var i=0; i<po.values.length; i++) {
                    for (var j=0; j<odbFile.binary.options.selected_opts; j++) {
                        if (po.values[i] == odbFile.binary.options.selected_opts[j]) {
                            po.selectedValue = po.values[i];
                        }
                    }
                }

                if (po.selectedValue == null) {
                    po.selectedValue = 'DEFAULT'
                }
            });
        });
    };

    $scope.changeBaseAddress = function(base_address) {
        $scope.optionsUpdated(true);
    };

    updateArchitectureOptions();

    $scope.$watch('options.architecture', function(){
        updateArchitectureOptions()
    });


});