/* eslint-disable */

import Handlebars from 'handlebars'
import store from '../store'

function cloneDu(du) {
  var clonedDu = Object.assign({}, du)
  return clonedDu;
}

function createDuFactory(du) {
  return function (instStr, rawBytes) {
    var cloned = cloneDu(du);
    cloned.instStr = instStr;

    //cloned.branch = '';

    if (rawBytes !== undefined) {
      cloned.rawBytes = rawBytes;
    }
    return cloned;
  };
}

function createDuFactoryWithBranch(du, branch) {
  return function (instStr, args) {
    var duFactory = createDuFactory(du);
    var cloned = duFactory(instStr);
    if (args.branch) {
      cloned.branch = args.branch;
    } else {
      cloned.branch = branch;
    }

    if (args.rawBytes !== undefined) {
      cloned.rawBytes = args.rawBytes
    }

    return cloned;
  };
}

var intToHex = function(value){
  var stringValue = value.toString(16);
  var s = "000000000" + stringValue;
  return s.substr(s.length-8);

};

Handlebars.registerHelper("hex", intToHex);

Handlebars.registerHelper("pad", function(value, length) {
  var counter = length - value.length;
  for(var i=0; i<counter; i++) {
    value = value.concat("&nbsp;");
  }
  return value;
});

Handlebars.registerHelper("formatSectionOffset", function(section, vma, length) {
  var value = section + ":" + intToHex(vma);
  var counter = length - value.length;
  for(var i=0; i<counter; i++) {
    value = "&nbsp;".concat(value);
  }
  return value;
});

class OdaRenderer {
  constructor() {
    this.store = store

    this.functionTemplate1 = Handlebars.compile(
      '<span class="instruction">; =============== F U N C T I O N ====================================</span>');

    this.functionTemplate2 = Handlebars.compile(
      '<span class="oda-editable function-params function-return" data-function-addr="{{vma}}" data-function-field="retval" contenteditable="true">{{retval}}</span> ' +
      '<span class="oda-editable function-params function-name "  data-function-addr="{{vma}}" data-function-field="name"  contenteditable="true">{{name}}</span> ' +
      '(<span class="oda-editable function-params function-args"   data-function-addr="{{vma}}" data-function-field="args" contenteditable="true">{{args}}</span>)');

    this.labelTemplate = Handlebars.compile('<div><span class="oda-editable" contenteditable="true">loc_{{ hex vma }}</span>:</div>');
    this.labelTemplate2 = Handlebars.compile('<div><span class="oda-editable" contenteditable="true">{{label}}</span>:</div>');

    this.commentTemplate = Handlebars.compile('<span><span data-addr={{vma}}" ' +
      'class="oda-editable comment">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span>');

    this.commentTemplate2 = Handlebars.compile('<span> ; <span data-addr={{vma}}" ' +
      'class="oda-editable comment">{{comment}}</span></span>');

  }

  functions() {
    return store.getters.functionsByAddress
  }

  comments() {
    let c = store.getters.commentsByAddress
    return c
  }

  labels() {
    return {}
  }

  render(dus) {
    try {
      //TODO load functions
      var functions = this.functions()
      var rowCounter = 0;

      var data = [];

      for (var i = 0; i < dus.length; i++) {
        var instr = dus[i];

        if (functions[instr.vma]) {
          var funcLines = this.renderFunction(instr, functions[instr.vma]);
          data.push.apply(data, funcLines);
          rowCounter += funcLines.length;
        }

        if (instr.isBranch) {
          var branchDus = this.renderBranch(instr);
          data.push.apply(data, branchDus);
          rowCounter += branchDus.length;
        }
        else if (instr.targetRef) {
          var targetRender = this.renderTarget(instr);
          data.push.apply(data, targetRender);
          rowCounter += targetRender.length;
        }
        else {
          instr.instStr = this.createInstStr(instr);
          data[rowCounter] = instr;
          rowCounter += 1;
        }
      }

      return data;
    } catch (e) {
      console.log(e)
    }
  }

  renderBranch(du) {
    //console.log('renderBranch');
    var labels = this.labels()
    var createDu = createDuFactoryWithBranch(du, du.branch_label);

    var lines = [
      createDu("", {rawBytes: ''})
    ];

    if (labels[du.vma]) {
      lines.push(createDu(this.labelTemplate2(labels[du.vma]), {rawBytes: ''}));
    } else {
      lines.push(createDu(this.labelTemplate(du), {rawBytes: ''}));
    }

    lines.push(createDu(this.createInstStr(du), {branch: du.branch}));
    return lines;
  }

  renderFunction(du, func) {
    var functions = this.functions()
    //console.log('renderFunction', func);
    var createDu = createDuFactory(du);

    var theLines = [
      createDu("", ''),
      createDu(this.functionTemplate1(du), '')
    ];
    for (var i = 0; i < du.crossRef.length; i++) {
      theLines.push(createDu('; CODE XREF:<span href="" class="xref-location" data-addr="' +
        du.crossRef[i].vma + '">0x' + intToHex(du.crossRef[i].vma) + '</span>', ''));
    }
    theLines.push(createDu("", ''));
    theLines.push(createDu(this.functionTemplate2(Object.assign({}, du, func)), ''));
    theLines.push(createDu("", ''));
    return theLines;
  }

  renderTarget(du) {
    var functions = this.functions()
    var labels = this.labels()
    var createDu = createDuFactory(du);
    var labelTemplate = Handlebars.compile('<span href="" data-addr="{{ vma }}" class="xref-location"> loc_{{hex vma}} </span>');
    var label = labelTemplate(du.targetRef);

    if (functions[du.targetRef.vma]) {
      label = '<span href="" data-addr="' + du.targetRef.vma + '" class="xref-location">' + functions[du.targetRef.vma].name + "</span>";
    } else if (labels[du.targetRef.vma]) {
      label = '<span href="" data-addr="' + du.targetRef.vma + '" class="xref-location">' + labels[du.targetRef.vma].label + "</span>";
    }

    return [createDu(this.createInstStr(du, label))]
  }



  createInstStr(instr, label) {
    if (label === undefined) {
      label = '';
    }
    var comment = this.comments()[instr.vma];
    var renderedComment = this.commentTemplate({vma: instr.vma});
    if (comment) {
      //             console.log("comment", comment);
      renderedComment = this.commentTemplate2({vma: instr.vma, comment: comment.comment})
    }
    return '<table><tr><td class="insn" style="">' + instr.instStr + label + '</td><td>' + renderedComment + '</td></tr></table>';

  }

  indexRows(data, from) {
    console.log("indexRows", from);
    for (var i=0;i<data.length; i++) {
      data[i].index = from + i;
    }
  }
}

export default new OdaRenderer()
