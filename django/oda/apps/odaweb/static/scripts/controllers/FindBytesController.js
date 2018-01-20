"use strict";

odaApplication.controller('FindBytesController', function FindBytesController($scope, odbFile) {

    //http://stackoverflow.com/questions/18716113/scope-issue-in-angularjs-using-angularui-bootstrap-modal
    $scope.data = {
        search_pattern: null,
        results: null,
        searchHelp: 'To search for ASCII strings, use <b>double quotes</b>, as in:<br>' +
                    '&nbsp;&nbsp;&nbsp;&nbsp;"this is some long string to find"<br><br>' +
                    'To search for a sequnce of hex bytes, use one of the following formats:<br><br>' +
                    '&nbsp;&nbsp;&nbsp;&nbsp;00 01 02 03 de ad be ef<br>' +
                    '&nbsp;&nbsp;&nbsp;&nbsp;00010203deadbeef<br>'
    };

    $scope.find = function(bytes)  {
        //odaStatus.setStatus("Searching....");
        odbFile.find(bytes).success(function(data){
            //odaStatus.setStatus("Done searching");
            $scope.data.results = data;
            $scope.$apply();
        }).error(function(data, status){
        });
    };

    /*
    $scope.FindBytesPrompt = function FindBytesPrompt() {
        var bytes = bootbox.prompt("Bytes to Find:<br>" + $scope.searchHelp,
            function(result) {
                if ((result != null) && (result != "") ) {
                    $rootScope.search_pattern = bytes;
                    find(bytes);
                }
            }
        );
    };
    */

    $scope.setPosition = function(position) {
        odbFile.setActiveAddr(position);
    };

    /*odaApi.shortcut("ctrl f", function() {
        $("#sidebar-find-btn").trigger("click");
        $("#search-pattern").focus();
    }, true); */
});

