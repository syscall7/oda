"use strict";

var GRAPH_TEMPLATE = Handlebars.compile($('#graph-node-template').html());

function RenderDu(odbFile, du) {
    var label = "";

    var instruction = $.extend({
        comment: odbFile.comments[du.offset],
    }, du);

    if (odbFile.labels[instruction.offset]) {
        label += "<tr><td></td><td>"+ odbFile.labels[instruction.offset].label + ":</td></tr>";
    }

    if (instruction.targetRef) {
        if (odbFile.labels[instruction.targetRef.offset]) {
            instruction.targetRefName = odbFile.labels[instruction.targetRef.offset].label;
        } else if (odbFile.functions[instruction.targetRef.offset]){
            instruction.targetRefName = odbFile.functions[instruction.targetRef.offset].name;
        } else {
            instruction.targetRefName = Handlebars.compile("loc_{{hex offset}}")(instruction.targetRef);
        }
    }

    label += GRAPH_TEMPLATE(instruction);

    return label;
}

function DrawGraph(odbFile, graph) {

    $('.graph-view svg').remove();
    $('.graph-view div').remove();
    $('.graph-view').append('<svg><g/></svg>');

    // Create a new directed graph
    var g = new dagreD3.graphlib.Graph().setGraph({});

    var offsets = [];

    console.log("nodes: " + graph.nodes.length + " edges: " + graph.links.length);


    graph.nodes.forEach(function(node){
        var label = '<table class="graph-node">';
        for (var i = 0; i < node.instructions.length; i++) {

            var du = node.instructions[i];

            label += RenderDu(odbFile, du);

            offsets.push(du.offset);
        }
        label += "</table>";

        g.setNode(node.id, {
            label: label,
            labelType: 'html'
        });
    });

    graph.links.forEach(function(link){
        g.setEdge(link.from, link.to, {
            //label: link.from + ' ' + link.to,
            style: LINK_STYLE[link.type],
        });
    });

    var svg = d3.select("svg");

    var inner = svg.select("g");

    // Set up zoom support
    var zoom = d3.behavior.zoom().on("zoom", function () {
        inner.attr("transform", "translate(" + d3.event.translate + ")" +
            "scale(" + d3.event.scale + ")");
    });
    svg.call(zoom);

    svg.attr('width', '100%');
    svg.attr('height', $(window).height()-150);

    // Create the renderer
    var render = new dagreD3.render();

    // Run the renderer. This is what draws the final graph.
    render(inner, g);

    // Center the graph
    var initialScale = Math.max(0.2, 400 / g.graph().height);
    initialScale = Math.min(1.2, initialScale);
    console.log("width/height", g.graph().width, g.graph().height);
    zoom
        .translate([($('#tab-graph').width() - g.graph().width * initialScale) / 2, 20])
        .scale(initialScale)
        .event(svg);




    return offsets;

}

var LINK_STYLE = {
    notTaken: "stroke: #D9534F; stroke-width: 2px; fill: none;",
    taken: "stroke: #5CB85C; stroke-width: 2px; fill: none;",
    unconditional: "stroke: #006eff; stroke-width: 2px; fill: none;"
};

function odaTemplate(id, context) {
    var source = $('#' + id).html();
    var template = Handlebars.compile(source);
    return template(context);
}

odaApplication.run(function (odbFile, editor, addrBar) {

    var showing = false;
    var loadedOffsets = [];
    var activeTab = null;

    var reloadGraph = function(activeRow) {
        if (activeTab== '#tab-graph') {
            showing = true;

            if (!activeRow.isCode) {
                $('.graph-view svg').remove();
                $('.graph-view div').remove();
                $('.graph-view').append(odaTemplate('instruction-graph-data-section', activeRow));
                return;
            }

            for (var i = 0; i < loadedOffsets.length; i++) {
                if (loadedOffsets[i] == activeRow.offset) {
                    return;
                }
            }

            //Loading...
            $('.disassembly-loading').fadeIn(100);

            $('.graph-view svg').remove();
            $('.graph-view div').remove();

            return odbFile.graph(activeRow.offset).success(function (graph) {
                if (graph.links.length > 500) {
                    $('.graph-viewt svg').remove();
                    $('.graph-view div').remove();
                    $('.graph-view').append(odaTemplate('instruction-graph-too-complicated', $.extend(activeRow, {
                        numNodes: graph.nodes.length,
                        numLinks: graph.links.length

                    })));
                } else if (showing) {
                    loadedOffsets = DrawGraph(odbFile, graph);
                }

                $('.graph-active').removeClass('graph-active');
                $("tr[data-addr='" + activeRow.offset + "']").addClass('graph-active');

            }).error(function (data) {
                $('.graph-view').append(odaTemplate('instruction-graph-error', activeRow));
            }).always(function(){
               $('.disassembly-loading').fadeOut(100);
            });
        } else {
            showing = false;
        }


    };

    $('#oda-tabs').on('shown.bs.tab', function(e) {
        activeTab = $(e.target).attr('href');
        reloadGraph(editor.getActiveRowData());
    });

    odbFile.on(ODB_EVENTS.ACTIVE_ADDR_CHANGED, function(e) {
        if (activeTab== '#tab-graph') {
            odbFile.loadDu(e.addr, 1, false).success(function (data) {
                reloadGraph(data[0]);
            });
        }
    });

    /* List of loaded offsets, check this list to see if we need to reload */
   /* var loadedOffsets = [];

    var processing = false;

    editor.activeAddressChanged.subscribe(function(e, args) {
        if (processing) { return; }
        processing = true;
        $('.graph-active').removeClass('graph-active');
        $("tr[data-addr='" + args.offset + "']").addClass('graph-active');

        for (var i=0; i<loadedOffsets.length; i++) {
            if (loadedOffsets[i] == args.offset) {
                processing = false;
                return;
            }
        }

        loadedOffsets = [];
        $('.ui-layout-east svg').remove();
        $('.ui-layout-east div').remove();

        odbFile.graph(args.offset).success(function(graph){
            loadedOffsets = DrawGraph(odbFile, graph);
        }).error(function(data){
            $('.ui-layout-east').append('<div class="alert alert-warning">Instruction graph not available for address 0x' + args.offset.toString(16) + '</div>');
        }).always(function(){
            processing = false;
        });
    });*/

});