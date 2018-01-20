(function ($) {
    /***
     * A sample AJAX data store implementation.
     * Right now, it's hooked up to load all Apple-related Hackernews stories, but can
     * easily be extended to support and JSONP-compatible backend that accepts paging parameters.
     */
    function RemoteModel(odbFile) {

        // private
        var PAGESIZE = 500; // if this is too big, API will generate 400 errors
        var data = {length: 0};
        var searchstr = "apple";

        // events
        var onDataLoading = new Slick.Event();
        var onDataLoaded = new Slick.Event();
        var onDataCleared = new Slick.Event();

        var isProcessing = false;

        var first = null;
        var last = null;

        var renderer = new Oda.Renderer(odbFile);

        function init() {
        }


        function isDataLoaded(from, to) {
            for (var i = from; i <= to; i++) {
                if (!data[i] || data[i] == null) {
                    return false;
                }
            }

            return true;
        }

        function clear() {
            console.log("CLEAR");
            for (var key in data) {
                delete data[key];
            }
            data.length = 0;

            first = null;
            last = null;
            onDataCleared.notify();
        }

        function inLoadedRange(num) {
            if (first == null || last == null) {
                return false;
            }
            if (num > first && num < last) {
                return true;
            }
            return false;
        }

        function ajaxEnsureData(from, to, forceReload) {
            var NUM_UNITS_BEFORE = 200;

            console.log('ensuredata', from, to, forceReload);

            if (forceReload) {
                first = null;
                last = null;
            }

            if (isProcessing) {
                return;
            }
            if (!forceReload && isDataLoaded(Math.max(0,from - 75), to + 125) ) {
                return;
            }

            isProcessing = true;
            console.log('ajaxEnsureData', from, to);
            var startRow = Math.max(0, from - NUM_UNITS_BEFORE );
            var numRows = PAGESIZE;
            var pivot = (from >= NUM_UNITS_BEFORE ? NUM_UNITS_BEFORE : from);

            console.log(" Math.abs(startRow - last)",  first, last, startRow);

            var retval = null;

            if (inLoadedRange(startRow)) {

                var offset = data[last - 1].offset;
                console.log('append: ', offset.toString(16));

                retval = odbFile.loadDu(offset, numRows, false).success(onSuccessAppend)
                    .error(function () {
                        onError(from)
                    }).then(function(){isProcessing=false;});

            }/* else if (inLoadedRange(startRow + numRows)) {
                ///TODO: This needs to be adjusted by start - (additional lines)
                //    the problem is that after we've rendered the lines it may have
                //    accidentally rewritten some lines after the range, we means we
                //    need to adjust the start

                console.log("append-beginning: THIS NEEDS TO BE FIXED UP");
                retval = $.get('/odaweb/api/displayunits/', {
                    short_name: odbFile.shortName,
                    revision:  odbFile.revision,
                    addr: startRow,
                    logical: true,
                    units: numRows
                }).success(function(data) {
                    onSuccess(data, startRow, pivot);
                }).error(function () {
                        onError(fromPage)
                    }).then(function(){isProcessing=false;});
            } */ else {

                console.log("getting", startRow, numRows);
                retval = odbFile.loadDu(startRow, numRows, true).success(function(data) {
                    clear();
                    onSuccess(data, startRow, pivot);
                }).error(function () {
                        onError(from)
                    }).then(function(){isProcessing=false;});
            }

            onDataLoading.notify();

            return retval;
        }

        var ensureData = _.debounce(ajaxEnsureData, 250);

        function onError(fromPage) {
            i = indicators.pop();
            if (i != null)
                i.fadeOut();
            alert("error loading page " + fromPage);
        }

        var lastFrom = null;

        function onSuccess(resp, start, pivot) {
            console.log("Start: " + start + " Pivot:" + pivot);

            var beforeBlock = resp.slice(0, pivot);
            var afterBlock = resp.slice(pivot);

            var from = start + pivot;

            lastFrom = from;

            console.log("displayUnitsLength",odbFile.displayUnitsLength);
            data.length = Math.max(350, odbFile.displayUnitsLength); //Math.min(parseInt(resp.hits)); // limitation of the API

            var renderedRows = renderer.render(afterBlock);
            renderer.indexRows(renderedRows, from);
            for (var i=0; i<renderedRows.length; i++) {
                data[from + i] = renderedRows[i];
            }

            var to = from + renderedRows.length;

            if (last == null || last < (renderedRows.length + from)) {
                last = renderedRows.length + from;
                console.log("Setting last", last);
            }

            var beforeRenderedRows = renderer.render(beforeBlock);
            renderer.indexRows(beforeRenderedRows, from - beforeRenderedRows.length);
            for (var i=0; i<beforeRenderedRows.length; i++) {
                data[from - i - 1] = beforeRenderedRows[beforeRenderedRows.length - i - 1];
            }
            if (first == null || first > from-beforeRenderedRows.length) {
                first = from-beforeRenderedRows.length;
                console.log("setting first", first);
            }

            onDataLoaded.notify({from: from, to: to});
        }

        function onSuccessAppend(resp) {
            var from = last - 1;
            //data.length = Math.min(parseInt(resp.hits)); // limitation of the API

            if (first == null || first > from) {
                first = from;
                console.log("setting first", first);
            }

            var renderedRows = renderer.render(resp);
            renderer.indexRows(renderedRows, from);
            for (var i=0; i<renderedRows.length; i++) {
                data[from + i] = renderedRows[i];
            }

            var to = from + renderedRows.length;

            if (last == null || last < (renderedRows.length + from)) {
                last = renderedRows.length + from;
                console.log("Setting last", last);
            }

            onDataLoaded.notify({from: from, to: to});
        }


        function reloadData(from, to) {
            for (var i = from; i <= to; i++)
                delete data[i];

            ensureData(from, to);
        }

        init();

        return {
            // properties
            "data": data,

            "getLastFrom": function() { return lastFrom; },

            // methods
            "clear": clear,
            "isDataLoaded": isDataLoaded,
            "ensureData": ensureData,
            "reloadData": reloadData,

            // events
            "onDataLoading": onDataLoading,
            "onDataLoaded": onDataLoaded,
            "onDataCleared": onDataCleared
        };
    }

    // Slick.Data.RemoteModel
    $.extend(true, window, {Slick: {Data: {RemoteModel: RemoteModel}}});
})(jQuery);
