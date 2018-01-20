"use strict";

odaApplication.run(function($rootScope, $modal, odbFile, editor){
    $rootScope.$on('command.comment', function(event, line){
        editor.focusActive('.comment');
    });

    $rootScope.$on('command.dataToCode', function(event,data){
        if (data.isCode) {
            return;
        }

        odbFile.makeCode(data.offset);
    });


    $rootScope.$on('command.codeToData', function(event, data){
        if (!data.isCode) {
            return;
        }

        odbFile.makeData(data.offset);
    });

    /*$rootScope.$on('command.undefine', function(event,data){
        if (data.isCode) {
            return;
        }

        odbFile.undefineOp(data.offset);
    });*/

    $rootScope.$on("command.makeFunction", function(event, data) {
        if (!data.isCode) {
            return;
        }

        var scope = $rootScope.$new(true);

        var offset = data.offset
        var hex = intToHex(offset);

        scope.odbFile = odbFile;

        var existingFunc = odbFile.functions[offset];

        scope.data = {
            function: {
                name: 'FUNCTION_' + hex,
                retval: 'unknown',
                args: 'unknown'
            }
        };
        scope.data.offsetHex = hex;
        scope.data.modify = (existingFunc != null);

        if(existingFunc != null) {
            scope.data.function.name = existingFunc.name;
            scope.data.function.retval = existingFunc.retval;
            scope.data.function.args = existingFunc.args;
        }

        var modalInstance = $modal.open({
          templateUrl: 'makeFunction.html',
          controller: 'MakeFunctionController',
          size: 'lg',
          scope: scope
        });

        modalInstance.result.then(function(funcDef){
            if (existingFunc != null) {
                console.log('update function', existingFunc);
                odbFile.updateFunction(offset, scope.data.function.name,
                    scope.data.function.retval, scope.data.function.args);
            } else {
                console.log('create function', funcDef);

                odbFile.createFunction(offset, scope.data.function.name,
                    scope.data.function.retval, scope.data.function.args);
            }

        });
    });

    $rootScope.$on('command.deleteStructType', function(event, index){

        odbFile.deleteStructType(index);
    });

    $rootScope.$on("command.makeStructType", function(event, data) {
        var scope = $rootScope.$new(true);

        scope.odbFile = odbFile;

        scope.data = {
            structData: {
                name: 'StructName',
                is_packed: true
            }
        };

        var modalInstance = $modal.open({
          templateUrl: 'makeStructType.html',
          controller: 'MakeStructTypeController',
          size: 'lg',
          scope: scope
        });

        modalInstance.result.then(function(structDef){
            console.log('create structure type');
            odbFile.addStructType(scope.data.structData.name);
        });
    });

    $rootScope.$on("command.makeStructVariable", function(event, data) {

        var scope = $rootScope.$new(true);

        var offset = data.offset;

        scope.odbFile = odbFile;
        scope.structTypes = odbFile.structTypes;

        scope.data = {
            structData: {
                offset: offset,
                name: 'StructVarName',
                type: odbFile.structTypes[0].name,
                types: odbFile.structTypes
            }
        };

        var modalInstance = $modal.open({
          templateUrl: 'makeStructVariable.html',
          controller: 'MakeStructVariableController',
          size: 'lg',
          scope: scope
        });

        modalInstance.result.then(function(structDef){
            console.log('create structure variable');
            odbFile.addStructVariable(scope.data.structData.offset, scope.data.structData.name, scope.data.structData.type);
        });
    });
});
