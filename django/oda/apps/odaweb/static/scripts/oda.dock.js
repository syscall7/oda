"use strict";

odaApplication.service('Docker', function(odbFile) {
    var master = odbFile.oda_master;

    this.docks = [];
    if (master.binary.liveMode) {
        this.docks.push({
            icon: 'fa-briefcase',
            template: 'live_entry.html'
        });
        this.activeDock = this.docks[0];
    } else {
        this.docks.push({
            icon: 'fa-list',
            template: 'symbols.html'
        }, {
            icon: 'fa-font',
            template: 'strings.html'
        }, {
            icon: 'fa-search',
            template: 'find_results.html'
        }, {
            icon: 'fa-text-width',
            template: 'structform.html'
        });
        this.activeDock = this.docks[0];
    }

    /*this.docks.push({
        icon: 'fa-th-large',
        template: '/static/templates/sections.html'
    });*/

    this.select = function(thing) { this.activeDock = thing; };
    this.clear = function(thing) { this.activeDock = null; };
});

odaApplication.controller('DockMenuController', function DockMenuController($scope, $http, $window, Docker) {

    $scope.isActive = function(dock) {
        return Docker.activeDock == dock;
    };
    $scope.Docker = Docker;

});

odaApplication.controller('DockController', function DockController($scope, $http, $window, Docker) {

    $scope.isActive = function(dock) {
        return Docker.activeDock == dock;
    };
    $scope.Docker = Docker;

});