"use strict";

var branchFormatter = function (row, cell, value, columnDef, dataContext) {
    return value;
};

var offsetFormatter = function (row, cell, value, columnDef, dataContext) {
    var hex = ("000000000000000" + value.toString(16)).substr(-8);
    return ":" + hex;
};

var instStrFormatter = function (row, cell, value, columnDef, dataContext) {
    return value;
};

function InstructionTableNavigationHandler(instructionTable) {

    $('#editor').on('click', '.xref-location', function (event) {
        var offset = $(this).data('addr');
        instructionTable.gotoAddress(offset);
    });



}

function InstallFunctionHandlers(odbFile) {

    $('#editor').on('focus', '.function-params', function(event){
        console.log('focus', event);
    });

    $('#editor').on('blur', '.function-params', function(){
        var offset = parseInt($(this).data('function-addr'));
        var func = odbFile.functions[offset];
        var value = $(this).text();
        var modifiedField = $(this).data('function-field');

        if (modifiedField == 'name') {
            func.name = value;
        } else if (modifiedField == 'retval') {
            func.retval = value;
        } else if (modifiedField == 'args') {
            func.args = value;
        }

        odbFile.updateFunction(func.offset, func.name, func.retval, func.args);

    });

    $('#editor').on('blur', '.comment', function(){
        var offset = parseInt($(this).data('addr'));
        var comment = $(this).text();
        odbFile.addComment(offset, comment);
    });

    odbFile.on(ODB_EVENTS.DISPLAY_UNITS_LOADING, function(event) {
        $('.disassembly-loading').fadeIn(100);
    });
    odbFile.on(ODB_EVENTS.DISPLAY_UNITS_LOADED, function(event) {
        $('.disassembly-loading').fadeOut();
    });
};

function InstructionTable(odbFile) {
    InstallFunctionHandlers(odbFile);

    var columns = [
        //{id: "num", name: "#", field: "index", width: 80},
        {
            id: "branch",
            name: "branch",
            formatter: branchFormatter,
            field: "branch",
            width: 120,
            cssClass: 'cell-branch'
        },
        {
            id: "section_name", name: "section_name", field: "section_name",
            cssClass: 'cell-section', width: 140
        },
        {
            id: "offset", name: "offset", field: "offset", cssClass: 'cell-offset',
            width: 80, formatter: offsetFormatter
        },
        {id: "rawBytes", name: "rawBytes", field: "rawBytes", cssClass: 'cell-rawbytes', width: 160},

        {id: "instStr", name: "instStr", field: "instStr", width: 1500, formatter: instStrFormatter},
        // {id: "opcode", name: "opcode", field: "opcode", width: 60},
        // {id: "operands", name: "operands", field: "operands", width: 200}
    ];

    var options = {
        rowHeight: 15,
        editable: false,
        enableAddRow: false,
        enableCellNavigation: true,
        enableColumnReorder: false
    };

    var loader;

    this.activeAddressChanged = new Slick.Event();

    var activeAddress = null;

    function gotoAddressRemote(address) {

        if (activeAddress == address) {
            return;
        }


        activeAddress = address;

        odbFile.vmaToLda(address, function (line) {

            this.activeAddressChanged.notify({offset:activeAddress});

            console.log('GOTO ADDRESS', '0x' + address.toString(16), address, line);

            var renderedRange = grid.getRenderedRange();

            for (var i = renderedRange.top; i < renderedRange.bottom; i++) {
                var item = grid.getDataItem(i);
                if (item) {
                    if (item.offset == address) {
                        grid.setActiveCell(i, 0);
                        return;
                    }
                }
            }

            grid.setActiveCell(parseInt(line), 0);
            loader.clear();
            grid.scrollRowToTop(Math.max(0, (parseInt(line)-5)));

        }.bind(this));
    }

    function gotoAddressLocal(address) {
        for (var i=0; i<grid.getData().length; i++) {
            var rowOffset = grid.getDataItem(i).offset;
            if (rowOffset >= address) {
                grid.setActiveCell(i, 0);
                grid.scrollRowToTop(Math.max(0, (i-5)));
                break;
            }
        }
    }

    if (odbFile.displayUnitsLength < 500) {
        loader = new Slick.Data.LocalModel(odbFile);
        this.gotoAddress = gotoAddressLocal;
    } else {
        loader = new Slick.Data.RemoteModel(odbFile);
        this.gotoAddress = gotoAddressRemote;
    }
    var grid = new Slick.Grid("#editor", loader.data, columns, options);

    $(".slick-header-columns").css("height", "0px");
    grid.resizeCanvas();

    //var selectionModel = new Slick.RowSelectionModel();
    //grid.setSelectionModel(selectionModel);

    this.onViewportChanged = new Slick.Event();

    var that = this;

    grid.onViewportChanged.subscribe(function (e, args) {
        var vp = grid.getViewport();
        loader.ensureData(vp.top, vp.bottom);

        //grid.setActiveCell(vp.top+5, 0);

        that.onViewportChanged.notify(vp);

    });

    loader.onDataCleared.subscribe(function (e, args) {
        console.log('onDataCleared');

        grid.invalidateAllRows();

    });

    grid.onKeyDown.subscribe(function (e, args) {
        if ($(e.target).hasClass('oda-editable')) {
            console.log('grid,keyDown', e, args);

            if (e.keyCode == 13) {
                $(e.target).blur();
            }

            e.stopPropagation();
        }
    });

    loader.onDataLoaded.subscribe(function (e, args) {
        for (var i = args.from; i < args.to; i++) {
            grid.invalidateRow(i);
        }

        grid.updateRowCount();
        grid.render();

        var activeCell = grid.getActiveCell();
        if (activeCell == null) {
            grid.setActiveCell(0,0);
        }
        var activeRowData = grid.getDataItem(grid.getActiveCell().row);
        if (activeRowData != null) {
            this.activeAddressChanged.notify({offset:activeRowData.offset});
        }

    }.bind(this));

    // load the first page
    grid.onViewportChanged.notify();

    this.onDataLoaded = loader.onDataLoaded;

    this.onDataLoading = loader.onDataLoading;

    this.reload = function() {
        console.log('reload');
        var lastFrom = loader.getLastFrom();
        //loader.clear();

        var vp = grid.getViewport();
        var top = lastFrom != null ? lastFrom : vp.top;
        loader.ensureData(top, vp.bottom, true);

    };

    this.getActiveRowData = function() {
        var activeCell = grid.getActiveCell();
        if (activeCell != null && grid.getDataItem(activeCell.row) != null) {
            var activeRowData = grid.getDataItem(activeCell.row);
            return activeRowData;
        }
        return null;
    };

    this.getOdbFile = function () {
        return odbFile;
    };

    grid.onActiveCellChanged.subscribe(function(e, args) {
        var activeRowData = grid.getDataItem(args.row);
        //console.log("ACTIVE CELL CHANGED", activeRowData, e, args);
        if (activeRowData != null) {
            activeAddress = activeRowData.offset;
            this.activeAddressChanged.notify({offset:activeRowData.offset});
        }
    }.bind(this));

    this.focusActive = function(selector) {
        console.log(selector);
        $('#editor .active').find(selector).focus();
    };

    this.setActiveCellFromEvent = function(event) {
        var cell = grid.getCellFromEvent(event);
        grid.setActiveCell(cell.row, 0);
        return cell;
    };

    return this;
}

function CreateInstructionTable(odbFile) {

    var instructionTable = new InstructionTable(odbFile);

    var navHandler = new InstructionTableNavigationHandler(instructionTable);

    return instructionTable;

    /*var indicators = new Array();

    instructionTable.onDataLoading.subscribe(function (e, args) {
        if (indicators.length == 0) {
            loadingIndicator = $("<span class='loading-indicator'><label>Buffering...</label></span>").appendTo(document.body);
            var $g = $("#myGrid");

            loadingIndicator
                .css("position", "absolute")
                .css("top", $g.position().top + $g.height() - loadingIndicator.height() / 2)
                .css("left", $g.position().left + $g.width() / 2 - loadingIndicator.width() / 2);

            loadingIndicator.show();
            indicators.push(loadingIndicator);
        }
        else
            indicators.push(null);
    });

    instructionTable.onDataLoaded.subscribe(function (e, args) {
        var i = indicators.pop();
        if (i != null)
            i.fadeOut();
    });*/
};
