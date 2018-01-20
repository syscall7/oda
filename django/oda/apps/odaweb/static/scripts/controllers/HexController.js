"use strict";

odaApplication.controller('HexController', function HexController($scope, odbFile) {

    var minAddress = -1;
    var maxAddress = -1

    function convertDisplayUnitsToHexLines(dus)
    {
        var WIDTH = 16;
        var cur_section = "";
        var idx = -1;

        $scope.hexLines = [];


        for (var i = 0; i < dus.length; i++) {

            var du = dus[i];

            // if this du is starting a new section
            if (du.section_name != cur_section)
            {
                // if this isn't the first section and there actually was a previous section
                if (idx != -1) {

                    // pad out last line of the section to WIDTH
                    while ($scope.hexLines[idx].bytes.length < WIDTH) {
                        $scope.hexLines[idx].bytes.push('  ');
                        $scope.hexLines[idx].asc.push('  ');
                    }
                }

                // if the new section start is not 16-byte aligned
                if (du.offset % WIDTH != 0) {

                    // add a new hex line
                    $scope.hexLines.push({
                        name : du.section_name,
                        addr : du.offset,
                        bytes : [],
                        asc : []
                    });
                    idx++;

                    // pad out with leading empty bytes
                    for (var p = 0; p < (du.offset % WIDTH); p++) {
                        $scope.hexLines[idx].bytes.push('  ');
                        $scope.hexLines[idx].asc.push('  ');
                    }
                }
            }

            cur_section = du.section_name;

            // add the raw bytes and ascii representation
            for (var b = 0; b < du.rawBytes.length; b+=2) {

                if ((du.offset+b/2)%WIDTH == 0) {
                    $scope.hexLines.push({
                        name : du.section_name,
                        addr : du.offset+b/2,
                        bytes : [],
                        asc : []
                    });
                    idx++;
                }

                var byte = du.rawBytes.substring(b,b+2);
                var asc = parseInt(byte, 16);
                asc = asc < 32 || asc > 127 ? '.' : String.fromCharCode(asc);
                $scope.hexLines[idx].bytes.push(byte);
                $scope.hexLines[idx].asc.push(asc);
            }
        }

        if (idx != -1) {
            // pad out last line to WIDTH
            while ($scope.hexLines[idx].bytes.length < WIDTH) {
                $scope.hexLines[idx].bytes.push('  ');
                $scope.hexLines[idx].asc.push('  ');
            }
        }
    };

    odbFile.on(ODB_EVENTS.DISPLAY_UNITS_LOADED, function(e){
        $scope.$apply(function(){
            var displayUnits = e.displayUnits;
            convertDisplayUnitsToHexLines(displayUnits);
            if ( displayUnits.length > 0 ) {
                minAddress = displayUnits[0].offset;
                maxAddress = displayUnits[displayUnits.length - 1].offset;
            } else {
                minAddress = 0;
                maxAddress = 0;
            }

        });
    })
});