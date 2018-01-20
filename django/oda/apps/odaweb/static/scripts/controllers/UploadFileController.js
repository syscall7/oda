"use strict";

odaApplication.controller('UploadFileController', function($scope, $modalInstance, fileUpload){

    //http://stackoverflow.com/questions/18716113/scope-issue-in-angularjs-using-angularui-bootstrap-modal
    $scope.data = {
        projectName: null
    };

    $scope.$watch('uploadFile', function() {
        if ($scope.uploadFile && $scope.data.projectName == null) {
            $scope.data.projectName = $scope.uploadFile.name;
        }
    });



    $scope.ok = function () {
        $scope.loading = true;

        fileUpload.uploadFileToUrl( $scope.uploadFile, $scope.data.projectName, '/odaweb/_upload')
            .success(function(data){
            $modalInstance.close(data);
        }).error(function(data){
            // default error message
            var err_msg = 'There was a problem with the upload.  Maximum upload size is 256KB.';
            if (data.error) {
                err_msg = data.error;
            }
            $scope.loading = false;
            $scope.error = err_msg;
        });

        /* $modalInstance.close({
            projectName: $scope.data.projectName,
            uploadFile: $scope.uploadFile
        }); */
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

});