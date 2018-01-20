"use strict";

var ODB_EVENTS = {
    CHANGED : 'odb.changed',
    LOADED : 'odb.loaded',
    PARCELS_RELOADED: 'odb.parcelReload',
    LIVE_ENTRY_UPDATE: 'odb.liveentryupdate',
    DISPLAY_UNITS_LOADING: 'odb.displayUnits.loading',
    DISPLAY_UNITS_LOADED: 'odb.displayUnitsLoaded',
    ACTIVE_ADDR_CHANGED: 'odb.active_addr_changed',
    ERROR : 'odb.error'
};


var ODB_ERRORS = {
    LIVE_ENTRY_FAILED: 'odb.errorcode.liveentry'
};

var Section = function(sectionDescriptor) {
    $.extend(this,sectionDescriptor);

    this.isCode = function() {
        for (var i=0; i<this.flags.length; i++) {
            if (this.flags[i].name == 'SEC_CODE') {
                return true;
            }
        }
        return false;
    };

    this.isData = function() {
        return !this.isCode();
    };

    return this;


};

var OdbFile = function(oda_master) {

    this.oda_master = oda_master;

    this.binary = oda_master.binary;

    this.functions = [];

    this.labels = [];

    this.sections = [];

    this.parcels = [];

    this.comments = [];

    this.symbols = [];

    this.displayUnitsLength = -1;

    this.shortName = null;

    this.revision = 0;

    this.strings = [];

    this.structTypes = [];

    this.structFieldTypes = [];
    
    this.runtimeReport = null;

    this.activeAddr = 0;


    this.load = function () {
        this.shortName = this.oda_master.short_name;

        var loadq = $.get('/odaweb/api/load', {
            short_name: this.shortName,
            revision: this.revision
        }).success(function(data){
            for (var i = 0; i < data.functions.length; i++) {
                this.functions[data.functions[i].offset] = data.functions[i];
            }

            for (var i = 0; i < data.labels.length; i++) {
                this.labels[data.labels[i].offset] = data.labels[i];
            }

            for (var i=0; i<data.comments.length; i++) {
                this.comments[data.comments[i].offset] = data.comments[i];
            }

            this.sections = data.sections;

            this.parcels = data.parcels;

            this.symbols = data.symbols;

            this.strings = data.strings;

            this.structTypes = data.structTypes;

            this.structFieldTypes = data.structFields;

            this.displayUnitsLength = data.displayUnits.size;

            //this.runtimeReport = data;

        }.bind(this));

        $.when(loadq).done(function (data) {
            this._signal(ODB_EVENTS.LOADED, this);
        }.bind(this));
    };

    this.reloadParcels = function() {
        var pq = $.get('/odaweb/api/parcels/', {
            short_name: this.shortName,
            revision: this.revision
        }).success(function (data) {
            this.parcels = data;
            this._signal(ODB_EVENTS.PARCELS_RELOADED, {
            });
        }.bind(this));
    };

    this.reloadStructFieldTypes = function() {
        var structfieldtypesq = $.get('/odaweb/api/cstructfieldtypes/', {
            short_name: this.shortName,
            revision: this.revision
        }).success(function(data) {
            this.structFieldTypes = data;
        }.bind(this));
    };

    this.setActiveAddr = function(addr) {
        if (addr == this.activeAddr) {
            return;
        }

        this.activeAddr = addr;

        this._signal(ODB_EVENTS.ACTIVE_ADDR_CHANGED, {
            addr: addr
        });
    };

    this.getActiveAddr = function() {
        return this.activeAddr;
    }

    this.duLength = function(callback) {
        $.get('/odaweb/api/displayunits/1/size/', {
            short_name: this.shortName,
            revision: this.revision
        }).success(function (data) {
            this.displayUnitsLength = data;
            callback(data);
        }.bind(this));
    };

    this.loadDu = function (addr, numUnits, logical) {
        var args = {
            short_name: this.shortName,
            revision: this.revision,
            addr: addr,
            units: numUnits
        };
        if (logical) {
            args.logical = true;
        }

        this._signal(ODB_EVENTS.DISPLAY_UNITS_LOADING, {
            duNum: addr,
            numUnits: numUnits
        });

        return $.get('/odaweb/api/displayunits/', args).done(function(data){
            if (data.length == 0) {
                throw "NO DATA RETURNED";
            }
            this._signal(ODB_EVENTS.DISPLAY_UNITS_LOADED, {
                duNum: addr,
                numUnits: numUnits,
                displayUnits: data
            });
        }.bind(this));
    };

    this.graph = function(addr) {
        return $.get('/odaweb/api/graph', {
            short_name: this.shortName,
            revision: this.revision,
            addr: addr
        });
    };

    this.vmaToLda = function (vma, callback) {
        $.get('/odaweb/api/displayunits/1/vmaToLda', {
            short_name: this.shortName,
            revision: this.revision,
            vma: vma
        }).done(callback);
    };

    this.makeData = function (vma, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log('makeData', vma);

        var apply = function() {
             this._signal(ODB_EVENTS.CHANGED, {
                addr: vma,
                action: 'makeData',
                remote: remote,
                data: {
                    offset: vma
                }
            });

            this.reloadParcels();

        }.bind(this);

        if (!remote) {
            $.get('/odaweb/api/displayunits/1/makeData/', {
                short_name: this.shortName,
                revision: this.revision,
                vma: vma
            }).success(apply);
        } else {
            apply();
        }

    };

    this.makeCode = function (vma, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log('makeCode', vma);

        var apply = function() {
             this._signal(ODB_EVENTS.CHANGED, {
                addr: vma,
                action: 'makeCode',
                remote: remote,
                data: {
                    offset: vma
                }
            });

            this.reloadParcels();

        }.bind(this);

        if (!remote) {

            $.get('/odaweb/api/displayunits/1/makeCode/', {
                short_name: this.shortName,
                revision: this.revision,
                vma: vma
            }).success(apply)
        } else {
            apply();
        }

    };

    /*
    this.undefineOp = function (vma, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log('undefine', vma);

        var delCommentApply = function() {
            delete this.comments[vma];
            this._signal(ODB_EVENTS.CHANGED, {
                addr: vma,
                action: 'undefine',
                remote: remote,
                data: {
                    offset: vma
                }
            });

            this.reloadParcels();

        }.bind(this);

        if (!remote) {

            if ( this.comments[vma] )
            {
                $.ajax({
                    type : "DELETE",
                    url : '/odaweb/api/comments/1/',
                    data : {
                        short_name: this.shortName,
                        revision: this.revision,
                        vma: vma
                    },
                    success : delCommentApply});
            }
        } else {
            delCommentApply();
        }

    };
    */

    this.addComment = function (offset, comment, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log("Comment", offset, comment);

        var apply = function() {
            this.comments[offset] = {
                comment: comment,
                offset: offset,
                remote: remote
            };


            this._signal(ODB_EVENTS.CHANGED, {
                addr: offset,
                action: 'insertComment',
                remote: remote,
                data: {
                    comment: comment,
                    offset: offset
                }
            });

        }.bind(this);

        if (!remote) {
            $.post("/odaweb/api/comments/",{
                short_name: this.shortName,
                revision: this.revision,
                comment: comment,
                offset: offset
            }).success(apply);
        } else {
            apply();
        }

    };

    this.deleteStructType = function (structindex, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log("DeleteStruct", structindex);

        var apply = function() {
            this.structTypes.splice(structindex, 1);

            this.reloadStructFieldTypes();

            this._signal(ODB_EVENTS.CHANGED, {
                action: 'deleteStruct',
                remote: remote,
                data: {
                    structindex: structindex
                }
            });


        }.bind(this);

        if (!remote) {

            $.ajax({
                type : "DELETE",
                url : '/odaweb/api/cstructs/' + structindex + '/',
                data : {
                    short_name: this.shortName,
                    revision: this.revision
                },
                success : apply});
        } else {
            apply();
        }

    };

    this.addStructType = function (name, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log("AddStruct", name);

        var apply = function() {
            this.structTypes[this.structTypes.length] = {
                name: name,
                is_packed: true,
                fields : []
            };

            this.reloadStructFieldTypes();

            this._signal(ODB_EVENTS.CHANGED, {
                action: 'addStruct',
                remote: remote,
                data: {
                    name: name,
                    is_packed: true,
                    fields : []
                }
            });

        }.bind(this);

        if (!remote) {
            $.post("/odaweb/api/cstructs/",{
                short_name: this.shortName,
                revision: this.revision,
                'name' : name,
                'is_packed' : true
            }).success(apply);
        } else {
            apply();
        }

    };

    this.addStructVariable = function (offset, name, type, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log("AddStructVariable", name);

        var apply = function() {

            this._signal(ODB_EVENTS.CHANGED, {
                action: 'addStructVariable',
                remote: remote,
                data: {
                    offset: offset,
                    name: name,
                    type: type
                }
            });

            this.reloadParcels();

        }.bind(this);


        if (!remote) {
            $.post("/odaweb/api/definedData/",{
                short_name: this.shortName,
                revision: this.revision,
                'type_kind': 'struct',
                'type_name': type,
                'var_name' : name,
                'vma' : offset,
            }).success(apply);
        } else {
            apply();
        }

    };

    this.modifyStructType = function (structindex, fieldtypes, fieldnames, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log("ModifyStruct", structindex);

        var newfields = [];
        var numFields = fieldtypes.length;
        for (var i = 0; i < numFields; i++) {
            newfields[i] = {
                name: fieldnames[i],
                type: fieldtypes[i]
            }
        }

        var apply = function() {
            this.structTypes[structindex].fields = newfields;

            this._signal(ODB_EVENTS.CHANGED, {
                action: 'modifyStruct',
                remote: remote,
                data: {
                    structindex: structindex,
                    fields : newfields
                }
            });


        }.bind(this);

        if (!remote) {
            $.get("/odaweb/api/cstructs/" + structindex + '/modify/',{
                short_name: this.shortName,
                revision: this.revision,
                'field_types' : fieldtypes,
                'field_names' : fieldnames
            }).success(apply);
        } else {
            apply();
        }

    };

    this.setOptions = function(options){
        var p = $.ajax({
            url: '/odaweb/api/options/'+this.binary.id+"/",
            type: 'PATCH',
            data: {
                options: options,
                short_name: this.shortName,
                revision: this.revision
            }
        }).success(function(data) {
            console.log(data);
            this._signal(ODB_EVENTS.LIVE_ENTRY_UPDATE, {
                addr: 0,
                action: 'liveEntryChanged'
            });

        }.bind(this));


        return p;
    };

    this.connectLink = function() {
         var p = $.post("/odaweb/api/share",{
            short_name: this.shortName,
            revision: this.revision
         });

        return p;
    };

    this.save = function() {
        var p = $.post("/odaweb/_save",{
            short_name: this.shortName,
            revision: this.revision
        });

        return p;
    };

    var lastDecompilerResults = null;
    this.decompile = function(addr) {
        if (lastDecompilerResults != null && addr > lastDecompilerResults.start && addr < lastDecompilerResults.end) {
            var deferred = $.Deferred();
            return deferred.resolve(lastDecompilerResults);
        }

        return $.get('/odaweb/api/decompiler', {
            short_name: this.shortName,
            revision: this.revision,
            addr: addr
        }).then(function(decompilerData) {
            lastDecompilerResults = decompilerData;
            return decompilerData;
        });
    };

    this.createFunction = function(offset, name, retval, args, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log('Create Function', offset, name, retval, args);

        var apply = function() {
            this.functions[offset] = {
                retval: retval,
                args: args,
                offet: offset,
                name: name
            };

            this.symbols.push({
                name: name,
                offset: offset,
                type: 'T'
            });

            this._signal(ODB_EVENTS.CHANGED, {
                addr: offset,
                action: 'createFunction',
                remote: remote,
                data: {
                    offset: offset,
                    name: name,
                    retval: retval,
                    args: args
                }
            });
        }.bind(this);

        if (!remote) {
            $.post('/odaweb/api/displayunits/1/makeFunction/', {
                short_name: this.shortName,
                revision: this.revision,
                offset: offset,
                name: name,
                retval: retval,
                args: args
        }).success(apply);
        } else {
            apply();
        }
    };

    this.updateFunction = function(offset, name, retval, args, remote) {
        if(typeof(remote)==='undefined') remote = false;

        console.log('Update Function', offset, name, retval, args);

        var func = this.functions[offset];

        func.name = name;
        func.retval = retval;
        func.args = args;

        var symbols = $.grep(this.symbols, function(s) { return s.offset == offset });
        $.each(symbols, function(i, symbol){ symbol.name = name; });

        var apply = function() {
            this._signal(ODB_EVENTS.CHANGED, {
                addr: offset,
                action: 'updateFunction',
                remote: remote,
                data: {
                    offset: offset,
                    name: name,
                    retval: retval,
                    args: args
                }
            });
        }.bind(this);

        if (!remote) {
        $.ajax({
            url: '/odaweb/api/functions/'+this.binary.id+"/",
            type: 'PATCH',
            data: {
                short_name: this.shortName,
                revision: this.revision,
                offset: offset,
                name: name,
                retval: retval,
                args: args
            }
        }).success(apply);
        } else {
            apply();
        }
    };

    this.find = function(bytes) {
        var results =  $.get('/odaweb/api/find/', {
            short_name: this.shortName,
            revision: this.revision,
            bytes: bytes
            });
        return results;
    };

    this.getSection = function(sectionName) {
        for (var i=0; i<this.sections.length; i++) {
            if (this.sections[i].name == sectionName) {
                return new Section(this.sections[i]);
            }
        }
        return null;
    }

    this.setLiveEntryText = function(liveEntryText) {

        if (!liveEntryText) {
            return;
        }

        $.ajax({
            url: '/odaweb/api/binarystrings/'+this.binary.id+"/",
            type: 'PATCH',
            data: {
                binary_string: liveEntryText.replace(/\s/g, ''),
                short_name: this.shortName,
                revision: this.revision
            }
        }).success(function() {
            this._signal(ODB_EVENTS.LIVE_ENTRY_UPDATE, {
                addr: 0,
                action: 'liveEntryChanged'
            });
        }.bind(this)).error(function(){
            this._signal(ODB_EVENTS.ERROR, {
                code: ODB_ERRORS.LIVE_ENTRY_FAILED,
                message: 'Failed To Disassemble. Did you include non hexadecimal characters (0-9A-F)?'
            });
        }.bind(this));


        /*var deferred = $q.defer();

        $http({
            method: 'PATCH',
            url: '/odaweb/api/binarystrings/'+this.binary.id+"/",
            data: {

            }
        }).success(function(data){
            this._signal('liveEntryText', { });
            deferred.resolve(data);
        }.bind(this)).error(function(){
            deferred.reject("Use only hex characters!");
        });
        return deferred.promise;*/
    };

    this.callbacks = {};
    this.on = function (name, handler) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].add(handler);

    };
    this._signal = function (name, data) {
        if (!this.callbacks[name]) {
            this.callbacks[name] = $.Callbacks();
        }
        this.callbacks[name].fire(data);
    };

};

OdbFile.setOptionsFor = function(shortName, revision, options) {
    return $.ajax({
        url: '/odaweb/api/options/'+"1"+"/",
        type: 'PATCH',
        data: {
            options: options,
            short_name: shortName,
            revision: revision
        }
    });

};