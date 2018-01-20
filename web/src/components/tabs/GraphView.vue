<template>
  <div style="position:absolute;left:0; right:0; top:0; bottom:0; overflow:hidden">
    <div id="tab-graph" class="graph-view" style="position:absolute;left:0; right:0; top:0; bottom:0; overflow:hidden">
    </div>
    <div style="position:absolute; right: -10px; top:-10px; z-index:1000" v-if="loading">
      <img src="../../assets/loading.gif" style="height:64px;">
    </div>
  </div>
</template>

<script>
  /* eslint-disable */
  import $ from 'jquery'
  import {graph} from '../../api/oda'
  var Handlebars = require('../../../node_modules/handlebars/dist/handlebars')

  var GRAPH_TEMPLATE = Handlebars.compile($('#graph-node-template').html());

  var LINK_STYLE = {
    notTaken: "stroke: #D9534F; stroke-width: 2px; fill: none;",
    taken: "stroke: #5CB85C; stroke-width: 2px; fill: none;",
    unconditional: "stroke: #006eff; stroke-width: 2px; fill: none;"
  };

  var intToHex = function(value){
    if (value === undefined) { return 'undefined' }
    var stringValue = value.toString(16);
    var s = "000000000" + stringValue;
    return s.substr(s.length-8);
  };

  Handlebars.registerHelper("hex", intToHex);

  var loadedOffsets = [];

  function RenderDu(du) {
    var odbFile = {
      comments: {},
      labels: {},
      functions: {}
    }
    var label = "";

    var instruction = $.extend({
      comment: odbFile.comments[du.vma],
    }, du);

    if (odbFile.labels[instruction.vma]) {
      label += "<tr><td></td><td>"+ odbFile.labels[instruction.vma].label + ":</td></tr>";
    }

    if (instruction.targetRef) {
      if (odbFile.labels[instruction.targetRef.vma]) {
        instruction.targetRefName = odbFile.labels[instruction.targetRef.vma].label;
      } else if (odbFile.functions[instruction.targetRef.vma]){
        instruction.targetRefName = odbFile.functions[instruction.targetRef.vma].name;
      } else {
        instruction.targetRefName = Handlebars.compile("loc_{{hex vma}}")(instruction.targetRef);
      }
    }

    label += GRAPH_TEMPLATE(instruction);

    return label;
  }

  function DrawGraph(graph) {

    $('.graph-view svg').remove();
    $('.graph-view div').remove();
    $('.graph-view').append('<svg><g/></svg>');

    // Create a new directed graph
    var g = new dagreD3.graphlib.Graph().setGraph({});

    var vmas = [];

    console.log("nodes: " + graph.nodes.length + " edges: " + graph.links.length);


    graph.nodes.forEach(function(node){
      var label = '<table class="graph-node">';
      for (var i = 0; i < node.instructions.length; i++) {

        var du = node.instructions[i];

        label += RenderDu(du);

        vmas.push(du.vma);
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

    var windowHeight = $(window).height()-150
    svg.attr('width', '100%');
    svg.attr('height', windowHeight);

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

    return vmas;

  }

  function odaTemplate(id, context) {
    var source = $('#' + id).html();
    var template = Handlebars.compile(source);
    return template(context);
  }

  function reloadGraph(activeRow) {
    if (!activeRow.isCode) {
      $('.graph-view svg').remove();
      $('.graph-view div').remove();
      $('.graph-view').append(odaTemplate('instruction-graph-data-section', activeRow));
      return Promise.resolve(0);
    }

    for (var i = 0; i < loadedOffsets.length; i++) {
      if (loadedOffsets[i] == activeRow.vma) {
        return Promise.resolve();
      }
    }

    //Loading...
    $('.disassembly-loading').fadeIn(100);

    $('.graph-view svg').remove();
    $('.graph-view div').remove();

    return graph(activeRow.vma).then(function (graph) {
      if (graph.links.length > 500) {
        $('.graph-view svg').remove();
        $('.graph-view div').remove();
        $('.graph-view').append(odaTemplate('instruction-graph-too-complicated', $.extend(activeRow, {
          numNodes: graph.nodes.length,
          numLinks: graph.links.length
        })));
      } else {
        loadedOffsets = DrawGraph(graph);
      }

      $('.graph-active').removeClass('graph-active');
      $("tr[data-addr='" + activeRow.vma + "']").addClass('graph-active');

    }).catch(function (data) {
      $('.graph-view').append(odaTemplate('instruction-graph-error', activeRow));
    }).finally(function () {
      $('.disassembly-loading').fadeOut(100);
    });
  }

  export default {
    name: 'GraphView',
    data () {
      return {
        loading: true
      }
    },
    props: ['visible'],
    watch: {
      visible(newValue) {
        this.redraw()
      },
      selectedAddress(newAddress, oldAddress) {
        this.redraw()
      }
    },
    computed: {
      selectedAddress () {
        return this.$store.getters.selectedAddress
      }
    },
    methods: {
      redraw () {
        let self = this
        if (this.visible) {
          this.loading = true
          reloadGraph({
            isCode: true,
            vma: this.selectedAddress
          }).finally(() => {
            self.loading = false
          })
        }
      }
    }
  }
</script>

<style>
  /** Graph **/
  .graph-node {
    color: black;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  }

  .graph-node td {
    padding-left: 5px;
    text-align: left;
  }

  .graph-active {
    background-color: #FFB;
  }

  .node rect {
    stroke: #333;
    fill: #fff;
  }

  .edgePath path {
    stroke: #333;
    fill: #333;
    stroke-width: 1.5px;
  }
</style>
