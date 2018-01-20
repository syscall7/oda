odaApplication.controller('SectionsController', function SectionsController($scope, $http, $window, odbFile) {

    $scope.sections = odbFile.sections;

    var labels = ['label-success', 'label-warning', 'label-info', 'label-inverse'];
    var label_index = 0;
    var flagLabelMap = [];

    $scope.getFlagLabel = function(flag) {
        var label;

        if (flagLabelMap[flag] == undefined) {
            flagLabelMap[flag] = labels[label_index];
            label_index = (label_index+1) % labels.length;
        }

        label = flagLabelMap[flag];

        //console.log("logging up ", flag, label);
        return label;
    }

    $scope.getFlagText = function(flag) {
        //return flag;
        var s = flag.split('_');
        return s[s.length-1];
    };

    $scope.setPosition = function(position) {
        // give focus to the disassembly tab
        $('#oda-tabs a[href="#tab-disassembly"]').tab('show');

        // move into position
        odbFile.setActiveAddr(position);
    }
});

