"use strict";

odaApplication.controller('NavbarController', function NavbarController($scope, $http, Docker, $modal, $location,
                                                                        fileUpload, AuthService, odbFile,
                                                                        focus){
    $scope.examples = window.examples;

    $scope.a = function() {return true;};

    $scope.loadExample = function(example) {
        window.location = "/odaweb/" + example.short_name;
    };

    $scope.openFile = function() {
        var modalInstance = $modal.open({
          templateUrl: 'uploadFileModal.html',
          controller: 'UploadFileController',
          size: 'lg'
        });

        modalInstance.result.then(function(data){
            console.log('ok', data);

            $scope.configureFile(data);

        });
    };

    $scope.downloadDisassembly = function() {
        window.location = '/odaweb/_download?short_name=' + odbFile.shortName + '&revision=' + odbFile.revision;
    };

    $scope.goToAddressPrompt = function() {
        var modalInstance = $modal.open({
          templateUrl: 'gotoAddressModal.html',
          controller: 'GotoAddressController',
          size: 'md'
        });

        focus("goto");

        modalInstance.result.finally(function(data){
            $("#goto-textbox").blur();
        });

    };

    $scope.findSequence = function() {
        Docker.select(Docker.docks[2]);
    };

    $scope.$on('command.goto', function(event) {
        $scope.goToAddressPrompt();
    });

    $scope.connectedUsers = [];
    $scope.$on('user.connect', function(event, username){
        console.log('user.connect', event, username);
        $scope.$apply(function(){
            $scope.connectedUsers.push({
                username: username,
                color: '#'+Math.floor(Math.random()*16777215).toString(16)
            });

        });
    });

    $scope.$on('user.disconnect', function(event, username) {
        console.log('user.disconnect', event, username);
        $scope.$apply(function(){
            for (var i=$scope.connectedUsers.length-1; i>=0; i--) {
                if ($scope.connectedUsers[i].username === username) {
                    $scope.connectedUsers.splice(i, 1);
                    break;
                }
            }
        });
    });


    $scope.$on('command.open', function(event) {
        $scope.openFile();
    });

    $scope.share = function(){
        odbFile.connectLink().success(function(shareData){
            var modalInstance = $modal.open({
                templateUrl: 'shareLive.html',
                controller: 'ShareLiveController',
                resolve: { shareInfo: function() { return shareData; } },
                size: 'lg'
            });
        });
    };

    var monitorSandbox = function(shortName, revision) {
        var modalInstance = $modal.open({
          templateUrl: 'monitorSandbox.html',
          controller: 'MonitorSandboxController',
          resolve: { fileInfo: function(){return {shortName: shortName, revision:revision};} },
          size: 'lg'
        });
    };

    $scope.configureFile = function(fileData) {
        console.log(fileData);
        var modalInstance = $modal.open({
          templateUrl: 'configureFileModal.html',
          controller: 'ConfigureFileController',
          resolve: { fileData : function() {return fileData;} },
          size: 'lg'
        });

        modalInstance.result.then(function(data){
            if (data.sandbox) {
                monitorSandbox(data.shortName, data.revision);
            } else {
                console.log(data, fileData);
                window.location = "/odaweb/" + fileData.short_name;
            }
        });
    };

    $scope.saveAndRedirect = function() {
        odbFile.save().success(function(data){
            window.location = data.url;
        });
    };

    $scope.loginPage = function() {
        return $http({
            method: 'POST',
            url: '/accounts/logout/'
        }).then(function(){
            window.location = "/accounts/login";
        });
    };

    $scope.createAccount = function() {
        return $http({
            method: 'POST',
            url: '/accounts/logout/'
        }).then(function(){
            window.location = "/accounts/signup";
        });

    };

    $scope.about = function() {
        var modalInstance = $modal.open({
          templateUrl: 'about.html',
          size: 'lg'
        });
    };

    $scope.whatsOda = function() {
        var modalInstance = $modal.open({
          templateUrl: 'whats-oda.html',
          controller: 'WhatsOdaController',
          size: 'lg'
        });
    };
});
