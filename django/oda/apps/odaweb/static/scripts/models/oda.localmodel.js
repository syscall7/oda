(function ($) {
    /***
     * A sample AJAX data store implementation.
     * Right now, it's hooked up to load all Apple-related Hackernews stories, but can
     * easily be extended to support and JSONP-compatible backend that accepts paging parameters.
     */
    function LocalModel(odbFile) {

        // events
        var onDataLoading = new Slick.Event();
        var onDataLoaded = new Slick.Event();
        var onDataCleared = new Slick.Event();


        var data = {length: 0};
        var renderer = new Oda.Renderer(odbFile);

        function loadData() {
            odbFile.loadDu(0, 500, true).success(function (loadedDus) {

                var renderedRows = renderer.render(loadedDus);
                renderer.indexRows(renderedRows, 0);
                for (var i = 0; i < renderedRows.length; i++) {
                    data[i] = renderedRows[i];
                }
                data.length = renderedRows.length;

                onDataLoaded.notify({from: 0, to: data.length});
            });
        }
        loadData();

        function clear() {
            onDataCleared.notify();
        }

        function reloadData() {
            loadData();
        }

        return {
            // properties
            "data": data,

            "getLastFrom": function() { return 0; },

            // methods
            "clear": clear,
            "isDataLoaded": function() {return true;},
            "ensureData": function(from, to, force){
                if (force) { reloadData(); }
            },
            "reloadData": reloadData,

            // events
            "onDataLoading": onDataLoading,
            "onDataLoaded": onDataLoaded,
            "onDataCleared": onDataCleared
        };
    }

    // Slick.Data.RemoteModel
    $.extend(true, window, {Slick: {Data: {LocalModel: LocalModel}}});
})(jQuery);
