odaApplication.controller('MonitorSandboxController', function($scope, $interval, $http, fileInfo) {
    var checking;
    var UPDATE_INTERVAL = 3000;
    $scope.elapsedSeconds = 0;
    $scope.job_status = null;

    $http.post('/odaweb/api/sandbox/1/submit/', {
        short_name: fileInfo.shortName,
        revision: fileInfo.revision
    }).success(function(job){
        checking = $interval(function(){
            console.log('checking...');

            if (!$scope.jobDone()) {
                $scope.elapsedSeconds += UPDATE_INTERVAL;
            }

            $http.get('/odaweb/api/sandbox/1/status/', {
                params: {
                    short_name: fileInfo.shortName,
                    revision: fileInfo.revision
                }
            }).success(function(response) {
                $scope.job_status = response.status

            });
        }, UPDATE_INTERVAL);
    });

    $scope.jobDone = function() {
        var done = false;
        if ($scope.job_status) {
            done = $scope.job_status.status == "reported";
        }
        return done;
    };

    $scope.continue = function () {
        window.location = "/odaweb/" + fileInfo.shortName;
    };

});