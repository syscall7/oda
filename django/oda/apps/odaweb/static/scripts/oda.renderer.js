(function($) {
    function Renderer(odbFile) {

        function cloneDu(du) {
            var clonedDu = $.extend({}, du);
            return clonedDu;
        }

        function createDuFactory(du) {
            return function(instStr, rawBytes) {
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
            return function(instStr, args) {
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


        this.functionTemplate1 = Handlebars.compile(
            '<span class="instruction">; =============== F U N C T I O N ====================================</span>');

        this.functionTemplate2 = Handlebars.compile(
            '<span class="oda-editable function-params function-return" data-function-addr="{{offset}}" data-function-field="retval" contenteditable="true">{{retval}}</span> ' +
            '<span class="oda-editable function-params function-name "  data-function-addr="{{offset}}" data-function-field="name"  contenteditable="true">{{name}}</span> ' +
            '(<span class="oda-editable function-params function-args"   data-function-addr="{{offset}}" data-function-field="args" contenteditable="true">{{args}}</span>)');

        this.labelTemplate = Handlebars.compile('<div style="margin-left:-40px"><span class="oda-editable" contenteditable="true">loc_{{ hex offset }}</span>:</div>');
        this.labelTemplate2 = Handlebars.compile('<div style="margin-left:-40px"><span class="oda-editable" contenteditable="true">{{label}}</span>:</div>');

        this.commentTemplate = Handlebars.compile('<span><span contenteditable="true" data-addr={{offset}}" ' +
        'class="oda-editable comment">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span>');

        this.commentTemplate2 = Handlebars.compile('<span>;<span contenteditable="true" data-addr={{offset}}" ' +
        'class="oda-editable comment">{{comment}}</span></span>');

        this.renderFunction = function(du, func) {
            //console.log('renderFunction', func);
            var createDu = createDuFactory(du);

            var theLines = [
                createDu("", ''),
                createDu(this.functionTemplate1(du), '')
            ];
            for (var i=0;i<du.crossRef.length; i++) {
                theLines.push(createDu('; CODE XREF:<span href="" class="xref-location" data-addr="' +
                    du.crossRef[i].offset + '">0x' + intToHex(du.crossRef[i].offset) + '</span>', ''));
            }
            theLines.push(createDu("",''));
            theLines.push(createDu(this.functionTemplate2($.extend({}, du, func)), ''));
            theLines.push(createDu("", ''));
            return theLines;
        };

        this.renderBranch = function(du) {
            //console.log('renderBranch');
            var createDu = createDuFactoryWithBranch(du, du.branch_label);

            var lines = [
                createDu("", {rawBytes:''})
            ];

            if (odbFile.labels[du.offset]) {
                lines.push(createDu(this.labelTemplate2(odbFile.labels[du.offset]), {rawBytes: ''}));
            } else {
               lines.push(createDu(this.labelTemplate(du), {rawBytes: ''}));
            }

            lines.push(createDu(this.createInstStr(du), {branch:du.branch}));
            return lines;
        };

        this.renderTarget = function(du) {
            var createDu = createDuFactory(du);
            var labelTemplate = Handlebars.compile('<span href="" data-addr="{{ offset }}" class="xref-location"> loc_{{hex offset}} </span>');
            var label = labelTemplate(du.targetRef);

            if (odbFile.functions[du.targetRef.offset]) {
                    label =  '<span href="" data-addr="' + du.targetRef.offset + '" class="xref-location">' + odbFile.functions[du.targetRef.offset].name + "</span>";
            } else if (odbFile.labels[du.targetRef.offset]) {
                label =  '<span href="" data-addr="' + du.targetRef.offset + '" class="xref-location">' + odbFile.labels[du.targetRef.offset].label + "</span>";
            }

            return [createDu(this.createInstStr(du,label))]
        };

        this.createInstStr = function(instr, label) {
            if (label === undefined) {
                label = '';
            }
            var comment = odbFile.comments[instr.offset];
            var renderedComment = this.commentTemplate({offset: instr.offset});
            if (comment) {
   //             console.log("comment", comment);
                renderedComment = this.commentTemplate2({offset: instr.offset, comment: comment.comment})
            }
            return '<table><tr><td class="insn" style="width:400px;">' + instr.instStr + label + '</td><td>' + renderedComment + '</td></tr></table>';
        };

        this.render = function(dus) {
            var rowCounter = 0;

            var data = [];


            for (var i = 0; i < dus.length; i++) {
                var instr = dus[i];

               if (odbFile.functions[instr.offset]) {
                    var funcLines = this.renderFunction(instr, odbFile.functions[instr.offset]);
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
        };

        this.indexRows = function(data, from) {
            console.log("indexRows", from);
            for (var i=0;i<data.length; i++) {
                data[i].index = from + i;
            }
        };
    }

    $.extend(true, window, {Oda: {Renderer: Renderer}});
})(jQuery);
