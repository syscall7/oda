'use strict';

var odaApplication = angular.module('odaApp');

odaApplication.run(function($rootScope, $modal, odbFile, editor){
    var decompile = function(addr) {
        console.log('Decompile' + addr);
        odbFile.decompile(addr).then(function(data){
            $('#decompiler-window').html('<pre>' + data.source + '</pre>');
        });
    };

    odbFile.on(ODB_EVENTS.ACTIVE_ADDR_CHANGED, function(e) {
        decompile(e.addr);
    });

    decompile(0);
});