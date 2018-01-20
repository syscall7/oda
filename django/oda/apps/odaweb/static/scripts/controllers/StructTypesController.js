"use strict";

odaApplication.controller('StructTypesController', function StructTypesController($scope, $rootScope, $http, $modal, odbFile, odaSession) {

    $scope.structTypes = odbFile.structTypes;
    $scope.structFieldTypes = odbFile.structFieldTypes;
    $scope.obdfile = odbFile;

    $scope.createStruct = function() {
        $rootScope.$broadcast('command.makeStructType');
    };

    $scope.deleteStructType = function (index) {
        $rootScope.$broadcast('command.deleteStructType',index);
    };

    $scope.openStructEditor = function(struct,index) {

        var modalInstance = $modal.open({
          templateUrl: 'openStructEditorModal.html',
          controller: 'StructEditorController',
          size: 'md',
          resolve: {
              structure: function () {
                return struct;
              },
              fieldTypes: function () {
                var typesClone = $scope.obdfile.structFieldTypes.slice(0);
                var arrayLength = typesClone.length;
                for (var i = 0; i < arrayLength; i++) {
                    if (typesClone[i].name == struct.name) {
                        // Can't reference ourself
                        typesClone.splice(i, 1);
                        break;
                    }
                }

                return typesClone;
              },
              obdFile: function () {
                return $scope.obdfile;
              },
              structIndex: function () {
                return index;
              }

            }
          }
        );

        modalInstance.result.then(function(data){
            console.log(data);
        });
    };
});

odaApplication.controller('StructEditorController', function($scope, $modalInstance, structure, fieldTypes, obdFile, structIndex){

    //http://stackoverflow.com/questions/18716113/scope-issue-in-angularjs-using-angularui-bootstrap-modal
    $scope.data = {
        name: structure.name,
        fields : structure.fields,
        fieldTypes : fieldTypes
    };

    $scope.ok = function () {

        var structFieldNames = [];
        var structFieldTypes = [];

        var numFields = $scope.data.fields.length;
        for (var i = 0; i < numFields; i++) {
            structFieldNames[i] = $scope.data.fields[i].name;
            structFieldTypes[i] = $scope.data.fields[i].type;
        }

        obdFile.modifyStructType(structIndex, structFieldTypes, structFieldNames);
        $modalInstance.close({
        });

    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.addField = function(name,type) {
        var field = { name: name, type: type};
        $scope.data.fields.push(field);
    };

    $scope.deleteField = function(index) {
        $scope.data.fields.splice(index,1);
    };
});
