/*
<html>
  <head>
    <title>Address Bar</title>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script src="http://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.6.0/underscore-min.js"></script>
    <script type="text/javascript">

        $(document).ready(function(){
/*

/* ------------------------------------------------------------------ *
 *                             C L A S S
 * ------------------------------------------------------------------ */
/*
   Defines how the position indicator is drawn.
     r - red
     g - green
     b - blue
     a - alpha (applied to the entire position indicator)
     isUser[optional] - true if this is a collaborating user, false otherwise (defaults to false)
 */
 function ArrowStyle(r, g, b, a, isUser) {

    this.r = r;
    this.g = g;
    this.b = b;
    this.a = a;
    this.isUser = typeof isUser !== 'undefined' ? isUser : false;

    /* -------------------------------------------------------------- *
     *                  P U B L I C   M E T H O D S
     * -------------------------------------------------------------- */

    /* Convert to the fill style used by canvas drawing functions */
    this.toFillStyle = function () {
        return "rgba(" + this.r + "," + this.g + "," + this.b + "," + this.a + ")";
    };
}

/* ------------------------------------------------------------------ *
 *                             C L A S S
 * ------------------------------------------------------------------ */
function Location(posX, vma, style) {

    /* The X pixel offset on the navigation bar */
    this.posX = posX;

    /* The virtual memory address */
    this.vma = vma;

    /* The arrow styling */
    this.style = style;
}

/* ------------------------------------------------------------------ *
 *                             C L A S S
 * ------------------------------------------------------------------ */
function AddressNavBar(canvasId, sects, parcels) {

    /* -------------------------------------------------------------- *
     *              P R I V A T E   P R O P E R T I E S
     * -------------------------------------------------------------- */

    var UID_YOFFSET;
    var UID_HEIGHT;

    var ARROW_YOFFSET;
    var ARROW_HEIGHT;
    var ARROW_WIDTH;
    var ARROW_BOX_WIDTH;

    var BAR_WIDTH;
    var BAR_YOFFSET;
    var BAR_XOFFSET;
    var BAR_HEIGHT;

    var TEXT_YOFFSET;
    var TEXT_WIDTH;
    var TEXT_HEIGHT;
    var TEXT_FONT_SIZE;

    var CANVAS_WIDTH;
    var CANVAS_HEIGHT;
    var INTER_SECTION_GAP = 2;

    var EFFECTIVE_BAR_WIDTH;
    var RUNT_PIXEL_THRESHOLD = 3;
    var RUNT_MIN_WIDTH = 3;

    /* our current position */
    var curArrow = new Location(0, undefined, new ArrowStyle(0, 0, 0, 1.0));

    /* our roaming position */
    var roamArrow = new Location(-1, 0, new ArrowStyle(0, 0, 0, 0.40));

    /* the current position of our collaborating users */
    var userArrows = {};

    // get the canvas and context
    var c = $('#addr-bar-canvas');
    var canvas = c.get(0);
    var ctx = canvas.getContext('2d');

    var sections = sects;
    var sumAddrRanges;

    var dragging = false;

    var onChangeHandlers = [];
    var onDragHandlers = [];
    var onRoamHandlers = [];

    // the number of collaborating users
    var numUsers = 0;

    // force an initial drawing
    resize();

    setSections(sects);
    setParcels(parcels);

    /* -------------------------------------------------------------- *
     *              P R I V A T E   M E T H O D S
     * -------------------------------------------------------------- */

    /* Get the canvas X,Y position */
    function getMousePosition(canvas, evt) {
        var rect = canvas.getBoundingClientRect();
        var coords = {
          x: evt.clientX - rect.left,
          y: evt.clientY - rect.top
        };

        // snap to the nearest section boundary if in between sections
        var posX = Math.floor(coords.x);
        if (!sections) { return null;}

        for (var i = 0; i < sections.length; i++)
        {
            var secWidth = sections[i].width;
            var secPosX = sections[i].posX;

            // if we're clearly in a section
            if (posX < (secPosX + secWidth)) {
                break;
            // else, if we're in the dead space between sections
            } else if (posX < (secPosX + secWidth + INTER_SECTION_GAP)) {
                var leaning = posX - (secPosX + secWidth);

                // snap to whichever side we're closest to
                if (leaning < INTER_SECTION_GAP/2) {
                    coords.x = secPosX + secWidth - 1;
                } else if (i < (sections.length - 1)){
                    coords.x = secPosX + secWidth + INTER_SECTION_GAP;
                } else {
                    // extending beyond last section?
                }
                break;
            }
        }

        return coords;
    }

    /* Convert an X pixel location to an address */
    function pixelToAddr(posX) {

        posX = Math.floor(posX);
        for (var i = 0; i < sections.length; i++)
        {
            var secWidth = sections[i].width;
            var secPosX = sections[i].posX;

            // if we're clearly in a section
            if ( (posX >= secPosX) && (posX < (secPosX + secWidth)) ) {
                var addr = Math.floor(sections[i].vma + ((posX - secPosX) / secWidth)*sections[i].size);
                return addr;
            // else, if we're in the dead space between sections
            } else if (posX < (secPosX + secWidth + INTER_SECTION_GAP)) {
                var leaning = posX - (secPosX + secWidth);

                // snap to whichever side we're closest to
                if (leaning < INTER_SECTION_GAP/2) {
                    return sections[i].vma + sections[i].size - 1;
                } else if (i < (sections.length - 1)){
                    return sections[i+1].vma;
                } else {
                    return -1;
                }
            }
        }
        return -1;
    }

    /* Convert an address to the X pixel location */
    function addrToPixel(addr) {

        var posX = -1;

        for (var i = 0; i < sections.length; i++)
        {
            if ((addr >= sections[i].vma) &&
                (addr < (sections[i].vma + sections[i].size)))
            {
                posX = (addr - sections[i].vma) /
                       sections[i].size *
                       sections[i].width +
                       sections[i].posX;
                break;
            }
        }

        return posX;
    }

    function vmaToSection(vma) {

        for (var i = 0; i < sections.length; i++) {
            if ((vma >= sections[i].vma) &&
                (vma < (sections[i].vma + sections[i].size)))
            {
                return sections[i];
            }
        }

        return undefined;
    }

    /* Internal function called when current position changes */
    function doCurArrowCallbacks() {

        if (dragging) {
            for (var i = 0; i < onDragHandlers.length; i++) {
                onDragHandlers[i](curArrow.vma);
            }

        } else {
            for (var i = 0; i < onChangeHandlers.length; i++) {
                onChangeHandlers[i](curArrow.vma);
            }
        }
    }

    /* Internal function called when current position changes via setting the address */
    function curArrowVmaChanged(newAddr) {

        var xpos = addrToPixel(newAddr);

        if ((0 > xpos) || (newAddr == curArrow.vma)) {
            return;
        }

        curArrow.posX = xpos;
        curArrow.vma = newAddr;

        /* Don't do callbacks when position changes by address, because it means we are being notified via the
           odaapi position broadcast.  Anybody else who cares about our current position will get that broadcast too,
           so we don't have to bother calling them back.

           doCurArrowCallbacks();
         */
    }

    /* Internal function called when current position changes via setting the slider position */
    function curArrowXChanged(newPosX) {

        var addr = pixelToAddr(newPosX);

        if ((0 > addr) || (addr == curArrow.vma)) {
            return;
        }

        curArrow.posX = newPosX;
        curArrow.vma = addr;
        doCurArrowCallbacks();
    }

    canvas.addEventListener('mousedown', function(evt) {
        var pos = getMousePosition(canvas, evt);
        var addr = pixelToAddr(pos.x);

        // we only start a drag if we click on the existing arrow location
        if (addr == curArrow.vma) {
            dragging = true;
        }
        curArrowXChanged(pos.x);
        draw();
    });

    canvas.addEventListener('mouseup', function(evt) {
        var pos = getMousePosition(canvas, evt);
        dragging = false;
        curArrowXChanged(pos.x);
        draw();
    });

    canvas.addEventListener('mouseout', function(evt) {
        var pos = getMousePosition(canvas, evt);
        roamArrow.posX = -1;
        draw();
    });

    canvas.addEventListener('mousemove', function(evt) {
        var pos = getMousePosition(canvas, evt);
        if (!pos) { return; }
        var addr = pixelToAddr(pos.x);

        if ((addr >= 0) && (roamArrow.vma != addr)) {

            for (var i = 0; i < onRoamHandlers.length; i++) {
                onRoamHandlers[i](addr);
            }

            roamArrow.posX = pos.x;
            roamArrow.vma = addr;
            draw();

            if (dragging) {
                curArrowXChanged(pos.x);
                draw();
            }
        }
    });

    /* Runt section calculations - needs to be done on resize or adding sections

       Here's the problem.  We want to show each section in the address bar, but some sections are too small to show
       in their real proportions to the other sections.  For those sections that are too small (runts, whose real pixel
       width is less than RUNT_PIXEL_THRESHOLD), we artificially inflate their width to RUNT_MIN_WIDTH.  This solves one
       problem, but then it skews the rest of the calculations because some sections are not displayed in proportion to
       their actual size.  To deal with that, we introduce EFFECTIVE_BAR_WIDTH, with takes into account the inflation of
       the runt sections as well as the inter-section gap that is displayed between each section.
     */
    function calcRuntSectionSizes() {
        var runtPadding = 0;

        if (undefined != sections) {
            // calculate how much space we need for runt padding
            for (var i = 0; i < sections.length; i++) {
                var width = Math.floor(sections[i].size / sumAddrRanges * BAR_WIDTH);
                if (width < RUNT_PIXEL_THRESHOLD) {
                    runtPadding += RUNT_MIN_WIDTH - width;
                }
            }

            // calculate how much BAR_WIDTH we really have to work with for scaling purposes
            EFFECTIVE_BAR_WIDTH = BAR_WIDTH - runtPadding - (sections.length-1)*INTER_SECTION_GAP;
        } else {
            EFFECTIVE_BAR_WIDTH = BAR_WIDTH;
        }
    }

    // register to re-draw ourselves when browser resizes
    $(window).resize(resize);

    /* called whenver the browser resizes the window */
    function resize() {

        // get the parent container
        var container = $(c).parent();

        // calculate canvas and object dimensions (for when window is resized)
        CANVAS_WIDTH = $(container).width() // use width of parent
        ARROW_WIDTH = 10;
        ARROW_BOX_WIDTH = 20; // the width of the yellow box

        UID_YOFFSET = 0;
        UID_FONT_SIZE = 15;
        UID_HEIGHT = UID_FONT_SIZE + 0;  // no gap needed here, b/c we're not at the bottom of the canvas, so chars like "_" will appear correctly

        ARROW_YOFFSET = UID_YOFFSET + UID_HEIGHT + 2;  // add some space between the usernames and top of arrow
        ARROW_HEIGHT = 8;

        BAR_YOFFSET = ARROW_YOFFSET + ARROW_HEIGHT;
        BAR_HEIGHT = 17;
        BAR_XOFFSET = ARROW_BOX_WIDTH/2;

        TEXT_YOFFSET = BAR_YOFFSET + BAR_HEIGHT;
        TEXT_FONT_SIZE = 15;
        TEXT_HEIGHT = TEXT_FONT_SIZE + 4;  // if we don't have a gap here, characters like "_" don't appear

        CANVAS_HEIGHT = TEXT_YOFFSET + TEXT_HEIGHT;

        BAR_WIDTH = CANVAS_WIDTH - BAR_XOFFSET;
        TEXT_WIDTH = BAR_WIDTH;

        // set canvas height and width
        c.attr('width', CANVAS_WIDTH);
        c.attr('height', CANVAS_HEIGHT);

        calcRuntSectionSizes();

        // redraw now that size has changed
        draw();
    }

    /* main function to draw this entire widget */
    function draw() {

        if (undefined == sections) {
            return;
        }

        // helper function to draw the sections
        function drawSections() {
            var x = BAR_XOFFSET;

            // make a second pass to assign widths to each section
            for (var i = 0; i < sections.length; i++) {

                // calculate the actual width of this section
                var width = Math.floor(sections[i].size / sumAddrRanges * (EFFECTIVE_BAR_WIDTH));

                // if this section is too small to show up, use RUNT_MIN_WIDTH instead
                if (width < RUNT_PIXEL_THRESHOLD) {
                    width = RUNT_MIN_WIDTH;
                }

                // draw section
                ctx.fillStyle = "rgb(0,110,255)";
                ctx.fillRect (x, BAR_YOFFSET, width, BAR_HEIGHT);

                // store some info with each section
                sections[i].width = width;
                sections[i].posX = x;

                x += width + INTER_SECTION_GAP;
            }
        }

        // helper function to draw the parcels
        function drawParcels() {

            if (parcels == undefined) {
                return;
            }

            function getParcelColor(p) {
                if (p.is_code) {
                    return "rgb(0,110,255)";
                } else {
                    return "rgb(53,53,53)";
                }
            }

            $.each(parcels, function(i, p) {
                var start = addrToPixel(p.vma_start);
                var end = addrToPixel(p.vma_end-1);
                var width = end - start;

                ctx.fillStyle = getParcelColor(p);
                ctx.fillRect (start, BAR_YOFFSET, width, BAR_HEIGHT);
            });
        }

        function fitTxtCentered(txt, x, font, h) {
            ctx.font = h.toString() + "px " + font;

            // calculate width of the text to be drawn
            var txtWidth = ctx.measureText(txt).width;

            // move x to the start
            x -= txtWidth/2;

            // if we're on the right side of the bar, draw text to the left of the given position
            if (x+txtWidth > BAR_WIDTH) {
                x -= x+txtWidth - BAR_WIDTH;
            } else if (x < 0) {
                x = 0;
            }

            return x;
        }

        /* helper function to draw text at the given location, which is specified as the lower left hand corner of the text

             txt - the text to draw
             fillStyle - context fill style (i.e., "rgba(1,2,3,0.5)"
             x - horizontal location to draw from (this function auto-corrects whether to draw from the left or right of
                 the given x position, depending on where we're at on the bar)
             y - vertical location to draw from (bottom of the text)
             h - height of the font
             font - name of font to use
             ensureVisible [optional] - ensure that the text is visible on the canvas (default is true)

         */
        function drawTextCentered(txt, fillStyle, x, y, h, font, ensureVisible) {

            ctx.fillStyle = fillStyle;
            ctx.font = h.toString() + "px " + font;

            // if make visible is false or not even passed in to this function
            if (ensureVisible || (typeof ensureVisible == 'undefined')) {
                x = fitTxtCentered(txt, x, font, h);
            } else {
                // nothing to do
            }

            ctx.fillText(txt, x, y);
        }

        // helper function to draw a list of strings centered at the given location
        function drawTextArrayCentered(txtStyleArray, x, y, h, font) {

            var rightToLeft = false;
            var SEPARATOR = " ";
            var start_x;

            txt_joined = $.map(txtStyleArray, function(txtStyle) {
                return txtStyle.txt;
            }).join(SEPARATOR);

            start_x = fitTxtCentered(txt_joined, x, font, h);

            $.each(txtStyleArray, function(i, txtStyle) {

                var txt = txtStyle.txt;
                var style = txtStyle.style;

                if (i != txtStyleArray.length - 1) {
                    txt += SEPARATOR;
                }

                drawTextCentered(txt, style, start_x, y, h, font, false);
                start_x += ctx.measureText(txt).width;
            });
        }

        // helper function to draw a position indicator at the given location using the given coloring
        function drawArrow(arrow) {
            var x = arrow.posX;
            var opacityFactor = arrow.style.a;

            // we only draw the bottom part of the position indicator if its our own current or roaming position
            if (!arrow.style.isUser) {
                // draw the yellow box below the arrow
                ctx.beginPath();
                ctx.rect(x - ARROW_BOX_WIDTH/2, BAR_YOFFSET-1, ARROW_BOX_WIDTH, BAR_HEIGHT+2);
                ctx.fillStyle = "rgba(255,255,0, " + 0.40*opacityFactor + ")";
                ctx.fill();
                ctx.strokeStyle = "rgba(255,255,0, " + 1.0*opacityFactor + ")";
                ctx.stroke();

                // draw the yellow line centered in the box
                ctx.moveTo(x, BAR_YOFFSET);
                ctx.lineTo(x, BAR_YOFFSET+BAR_HEIGHT);
                ctx.strokeStyle = "rgba(255,255,0, " + 1.0*opacityFactor + ")";
                ctx.stroke();
            }

            // draw the triangular arrow
            ctx.strokeStyle = arrow.style.toFillStyle();
            ctx.fillStyle = arrow.style.toFillStyle();
            ctx.beginPath();
            ctx.moveTo(x, BAR_YOFFSET);
            ctx.lineTo(x+ARROW_WIDTH/2, BAR_YOFFSET-ARROW_HEIGHT);
            ctx.lineTo(x-ARROW_WIDTH/2, BAR_YOFFSET-ARROW_HEIGHT);
            ctx.lineTo(x, BAR_YOFFSET);
            ctx.fill();
            ctx.closePath();
        };

        // helper function to draw the collaborating users
        function drawUsers() {

            var usernamesToDraw = [];

            // draw the collaborating user arrows
            $.each(userArrows, function(uid, arrow) {

                // draw the user arrow
                drawArrow(arrow);

                // if we're currently roaming over the position of a collabortaing user, save the username to draw later
                if ((roamArrow.posX >= 0) && (Math.abs(arrow.posX - roamArrow.posX) <= ARROW_WIDTH)) {
                        usernamesToDraw.push({'uid': uid, 'arrow': arrow});
                }
            });

            // if we are hovering over one or more users
            if (!$.isEmptyObject(usernamesToDraw)) {

                // first sort them by position
                usernamesToDraw = usernamesToDraw.sort(function(a,b) {
                    return a.arrow.posX - b.arrow.posX;
                });

                var txtStyleArray = [];
                var usernameXpos = usernamesToDraw[0].arrow.posX;  // center usernames on the first user position

                $.each(usernamesToDraw, function(i, uarrow) {

                    txtStyleArray.push({
                        'txt': uarrow.uid,
                        'style': uarrow.arrow.style.toFillStyle()
                    });
                });

                drawTextArrayCentered(txtStyleArray, usernameXpos, UID_YOFFSET+UID_FONT_SIZE, UID_FONT_SIZE, "Arial");
            }
        }

        // helper function to draw the roaming position indicator
        function drawRoaming() {

            // only draw the roaming arrow and roaming text if the mouse is currently hovering over the address bar
            if (roamArrow.posX >= 0) {

                // draw roaming arrow that is slightly transparent
                drawArrow(roamArrow);

                // draw the roaming address text
                var sec = vmaToSection(roamArrow.vma);
                var secName = sec == undefined ? "unk" : sec.name;
                drawTextCentered(secName + ':0x' + roamArrow.vma.toString(16), "rgb(0,0,0)",
                    roamArrow.posX, TEXT_YOFFSET + TEXT_FONT_SIZE, TEXT_FONT_SIZE, "Monospace");
            }
        }

        // start with a tabula rasa (don't want to draw on top of whatever currently exists) */
        ctx.clearRect (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

        drawSections();
        drawParcels();
        drawUsers();
        drawRoaming();

        // draw the current position indicator last so it's in front of everything else
        drawArrow(curArrow);
    }

    /* -------------------------------------------------------------- *
     *                  P U B L I C   M E T H O D S
     * -------------------------------------------------------------- */

    /* Update the sections represented in this navigation bar */
    function setSections(s) {
        sections = s;
        sumAddrRanges = _.reduce(sections, function(memo, section) {return memo+section.size}, 0);

        calcRuntSectionSizes();
        draw();

        // if this is the first time we are setting up curArrow.vma and we have valid sections
        if ((sections != undefined) && (curArrow.vma == undefined)) {
            var minAddr = _.min(sections, function(section){ return section.vma; }).vma;
            roamArrow.vma = minAddr;
            setAddress(minAddr);
        }
    }
    this.setSections = setSections;

    /* Update the parcels represented in this navigation bar */
    function setParcels(p) {
        parcels = p;
        draw();
    }
    this.setParcels = setParcels;

    /* Set the current address */
    function setAddress(a) {

        if (a != curArrow.vma) {
            var posX = addrToPixel(a);

            if (posX < 0) {
                return false;
            }

            curArrowVmaChanged(a);
            draw();
        }

        return true;
    }
    this.setAddress = setAddress;

    /* Allow event handler registration for onChange of address */
    function onChange(handler) {
        onChangeHandlers.push(handler);
    }
    this.onChange = onChange;

    /* Allow event handler registration for onRoam of address */
    function onRoam(handler) {
        onRoamHandlers.push(handler);
    }
    this.onDrag = onDrag;

    /* Allow event handler registration for onDrag of address */
    function onDrag(handler) {
        onDragHandlers.push(handler);
    }
    this.onRoam = onRoam;

    /* Add a new user whose position we wish to track */
    function addUser(uid) {
        if (userArrows[uid] == undefined) {
            getNewArrowStyle = function () {

                colors = [
                    [119, 79, 189],  // purple
                    [26, 156, 156],  // cyan
                    [193, 16, 170],  // pink
                    [225, 92, 9],    // orange
                    [9, 92, 225],    // blue
                    [225, 194, 9],   // yellow
                    [225, 9, 9],     // red
                    [9, 225, 92]     // green
                ];

                var colorIndex = numUsers % colors.length;
                r = colors[colorIndex][0];
                g = colors[colorIndex][1];
                b = colors[colorIndex][2];

                return new ArrowStyle(r, g, b, 1.0, true);
            };

            numUsers++;
            userArrows[uid] = new Location(0,0, getNewArrowStyle());
        }
    }
    this.addUser = addUser;

    /* Remove a user whose position we no longer wish to track */
    function removeUser(uid) {
        delete userArrows[uid];
        numUsers--;
    }
    this.removeUser = removeUser;

    /* Update a user's current position by virtual memory address */
    function updateUser(uid, vma) {

        /* if nothing changed */
        if (vma == curArrow.vma) {
            return;
        }

        /* convert to pixel offset */
        var x = addrToPixel(vma);

        /* if this is an invalid vma, ignore it */
        if (0 > x) {
            return;
        }

        userArrows[uid].vma = vma;
        userArrows[uid].posX = x;

        draw();
    }
    this.updateUser = updateUser;
}

/* ------------------------------------------------------------------ *
 *                           E X A M P L E
 * ------------------------------------------------------------------ */

/*
// define some sections
var sections = [
    {
        'name' : '.small0',
        'vma' : 0x300000,
        'size' : 0x5,
    },
    {
        'name' : '.small1',
        'vma' : 0x300100,
        'size' : 0x5,
    },
    {
        'name' : '.plt',
        'vma' : 0x400000,
        'size' : 0x500,
    },
    {
        'name' : '.text',
        'vma' : 0x500000,
        'size' : 0x40000,
    },
    {
        'name' : '.text_small',
        'vma' : 0x540000,
        'size' : 0x00050,
    },
    {
        'name' : '.data',
        'vma' : 0x550000,
        'size' : 0x80000,
    },
    {
        'name' : '.small2',
        'vma' : 0x600000,
        'size' : 0x5,
    },
    {
        'name' : '.small3',
        'vma' : 0x800100,
        'size' : 0x5,
    }
];

// instantiate the address nav bar
addrBar = new AddressNavBar('#addr-bar-canvas', sections);
addrBar.onChange(function(a) {
    console.log('My change handler: ' + a.toString(16));
});
addrBar.onDrag(function(a) {
    console.log('My drag handler: ' + a.toString(16));
});
addrBar.setAddress(0x520000);

addrBar.addUser('anthony');
addrBar.updateUser('anthony', 0x560000);

    });
    </script>
    <style type="text/css">canvas { border: 0px solid black; }</style>
  </head>
  <body>
    <div>
        <canvas id="addr-bar-canvas">You need to upgrade your browser to see this!</canvas>
    <div>
  </body>
</html>
*/
