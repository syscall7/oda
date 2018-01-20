import $ from 'jquery'

/* eslint-disable */

class Branch {

  constructor(from, to, type) {
    this.type = type;
    this.srcAddr = from;
    this.targetAddr = to;
    this.branchDown = this.srcAddr <= this.targetAddr;
    this.startAddr = this.branchDown ? this.srcAddr : this.targetAddr;
    this.stopAddr = this.branchDown ? this.targetAddr : this.srcAddr;
    this.span = this.stopAddr - this.startAddr;
    this.column = null;
  }

  /* -------------------------------------------------------------- *
   *                  S T A T I C   M E T H O D S
   * -------------------------------------------------------------- */
  static compareBySpan(a, b) {
    let comparison = 0;
    if (a.span > b.span) {
      comparison = 1;
    } else if (b.span > a.span) {
      comparison = -1;
    }

    return comparison;
  }

  /* -------------------------------------------------------------- *
   *                  P U B L I C   M E T H O D S
   * -------------------------------------------------------------- */
  overlaps(other) {
    let ret = false

    if ((this.stopAddr > other.startAddr) &&
      (this.startAddr < other.stopAddr)) {
      ret = true
    }

    return ret;
  }

  spans(addr) {
    return (addr >= this.startAddr) && (addr <= this.stopAddr);
  }

  isSource(addr) {
    return this.startAddr == addr;
  }

  isTarget(addr) {
    return this.targetAddr == addr;
  }

  isSibling(b) {
    return this.targetAddr == b.targetAddr;
  }
}

/* ------------------------------------------------------------------ *
 *                             C L A S S
 * ------------------------------------------------------------------ */
export class BranchLinePanel {

  constructor (canvasId, branches) {

    this.ROW_HEIGHT = 1.0*15;
    this.LINE_WIDTH = 2.0;
    this.COL_WIDTH = 1.0*10*2;
    this.COL1_OFFSET = 5.0;
    this.ROW1_OFFSET = 0.0;

    this.branches = [];
    this.maxColAssigned = 0;
    this.hoveredBranches = new Set([]);
    this.highlightedBranches = new Set([]);
    this.highlightedAddr = null;

    // get the canvas and context
    this.c = $(canvasId);
    this.canvas = this.c.get(0);
    this.ctx = this.canvas.getContext('2d');

    // add mouse handlers
    this.canvas.branchPanel = this; // have to set to access this class
    this.canvas.addEventListener('mousedown', this.mouseDown);
    this.canvas.addEventListener('mouseup', this.mouseUp);
    this.canvas.addEventListener('mouseout', this.mouseOut);
    this.canvas.addEventListener('mousemove', this.mouseMove);

    this.DEFAULT_STYLE = "#adadad";
    this.DEFAULT_LN_WIDTH = 1;

    this.HOVER_STYLE = "#87baff";
    this.HOVER_LN_WIDTH = 2;

    this.HIGHLIGHT_STYLE = "#004ac1";
    this.HIGHLIGHT_LN_WIDTH = 3;

    // register to re-draw ourselves when browser resizes
    var self = this
    window.addEventListener('resize', _.debounce(() => {self.resize()}, 250))

    // force an initial drawing
    this.setBranches(branches);
    this.resize();
  }

  /* -------------------------------------------------------------- *
   *              P R I V A T E   P R O P E R T I E S
   * -------------------------------------------------------------- */


  /* -------------------------------------------------------------- *
   *              P R I V A T E   M E T H O D S
   * -------------------------------------------------------------- */
  /* Get the canvas X,Y position */
  getMousePosition(canvas, evt) {
    let rect = this.canvas.getBoundingClientRect();
    let coords = {
      x: evt.clientX - rect.left,
      y: evt.clientY - rect.top
    };

    return coords;
  }

  /* Convert the position to a column */
  posToCol(pos) {
    let col = Math.floor(
      (this.CANVAS_WIDTH - pos.x - this.COL1_OFFSET) /
      this.COL_WIDTH);
    return col;
  }

  /* Convert the position to a row */
  posToRow(pos) {
    let row = Math.floor(pos.y/this.ROW_HEIGHT);
    return row;
  }

  /* Get the branch(es) at given position sharing same target */
  getBranchesAtPos(pos) {
    let col = this.posToCol(pos);
    let row = this.posToRow(pos);
    let br = null;
    let brs = new Set([]);

    /* FIRST PASS */

    /* find the branch occupying this column and this address */
    for (var i = 0, len = this.branches.length; i < len; i++) {
      let b = this.branches[i];
      if ((b.column == col) && b.spans(row)) {
        br = b;
        break;
      }
    }

    /* if there was no branch, look branch at this address */
    if (br == null) {
      for (var i = 0, len = this.branches.length; i < len; i++) {
        let b = this.branches[i];
        if ((b.startAddr == row) || (b.stopAddr == row)) {
          br = b;
        }
      }
    }

    /* SECOND PASS */
    if (br != null) {

      /* find all branches that share the same target address */
      for (var i = 0, len = this.branches.length; i < len; i++) {
        let b = this.branches[i];
        if (b.targetAddr == br.targetAddr) {
          brs.add(b);
        }
      }
    }

    return brs;
  }

  mouseDown(evt) {
    let pos = this.branchPanel.getMousePosition(this, evt);
    if (!pos) { return; }

    let brs = this.branchPanel.getBranchesAtPos(pos);
    if (!brs) { return; }

    this.branchPanel.highlightByAddr(brs.values().next().value.targetAddr);
  }

  mouseUp(evt) {
    let pos = this.branchPanel.getMousePosition(this, evt);
    if (!pos) { return; }
  }

  mouseOut(evt) {
    let pos = this.branchPanel.getMousePosition(this, evt);
    if (!pos) { return; }
  }

  mouseMove(evt) {
    let pos = this.branchPanel.getMousePosition(this, evt);
    if (!pos) { return; }

    let brs = this.branchPanel.getBranchesAtPos(pos);
    if (!brs) { return; }

    this.branchPanel.hoveredBranches = brs;

    // console.log("MouseMove", pos, brs);

    this.branchPanel.draw();
  }

  /* called whenver the browser resizes the window */
  resize() {

    // get the parent container
    let container = $(this.c).parent();

    this.CANVAS_HEIGHT = $(container).height(); // use height of parent
    this.CANVAS_WIDTH = 125;

    // set canvas height and width
    this.c.attr('width', this.CANVAS_WIDTH);
    this.c.attr('height', this.CANVAS_HEIGHT);

    // redraw now that size has changed
    this.draw();
  }

  /* main function to draw this entire widget */
  draw() {

    this.ctx.clearRect (0, 0, this.CANVAS_WIDTH, this.CANVAS_HEIGHT);

    // sort branches based on span (so short, inner branches appear in inner columns)
    this.branches.sort(Branch.compareBySpan);

    // assign columns
    for (var i = 0, len = this.branches.length; i < len; i++) {
      let b = this.branches[i];

      // initialize assigned column to null
      b.column = null;

      // assign it a column
      this.setFreeColumn(b);
    }

    // draw each line that is not hovered/highlighted
    for (var i = 0, len = this.branches.length; i < len; i++) {
      let style = this.DEFAULT_STYLE;
      let width = this.DEFAULT_LN_WIDTH;
      let b = this.branches[i];
      if (!this.highlightedBranches.has(b) && !this.hoveredBranches.has(b)) {
        this.drawLine(this.branches[i], style, width);
      }
    }

    // do hovered and highlighted next so they are drawn over top the others
    this.hoveredBranches.forEach(function(b) {
      this.drawLine(b, this.HOVER_STYLE, this.HOVER_LN_WIDTH);
    }, this);

    this.highlightedBranches.forEach(function(b) {
      this.drawLine(b, this.HIGHLIGHT_STYLE, this.HIGHLIGHT_LN_WIDTH);
    }, this);

  }

  /* function to draw the given branch line */
  drawLine(b, style, width) {

    let startY = b.startAddr * this.ROW_HEIGHT + this.ROW_HEIGHT/2;
    let stopY = b.stopAddr * this.ROW_HEIGHT + this.ROW_HEIGHT/2;
    let targetY = b.branchDown ? stopY : startY;

    this.ctx.lineWidth = width;
    this.ctx.fillStyle = style;
    this.ctx.strokeStyle = style;

    this.ctx.beginPath();
    this.ctx.moveTo(this.CANVAS_WIDTH, startY);
    this.ctx.lineTo(this.CANVAS_WIDTH - b.column*this.COL_WIDTH - this.COL_WIDTH/2 - this.COL1_OFFSET, startY);
    this.ctx.lineTo(this.CANVAS_WIDTH - b.column*this.COL_WIDTH - this.COL_WIDTH/2 - this.COL1_OFFSET, stopY);
    this.ctx.lineTo(this.CANVAS_WIDTH, stopY);
    this.ctx.stroke();

    this.drawArrow(targetY, style);
  }

  /* helper function to draw an arrow at the given location using the given coloring */
  drawArrow(y, style) {
    let x = this.CANVAS_WIDTH;
    let ARROW_WIDTH = 8;
    let ARROW_HEIGHT = 8;

    this.ctx.fillStyle = style;
    this.ctx.strokeStyle = style;

    this.ctx.beginPath();
    this.ctx.moveTo(x, y);
    this.ctx.lineTo(x-ARROW_WIDTH, y-ARROW_HEIGHT/2);
    this.ctx.lineTo(x-ARROW_WIDTH, y+ARROW_HEIGHT/2);
    this.ctx.lineTo(x, y);
    this.ctx.fill();
    this.ctx.closePath();
  };


  setFreeColumn(b) {
    // list of columns used by overalapping branches
    let columnsUsed = [];

    // list of branches that share a target addr with this branch
    let siblingBranches = [];

    let freeColumn = null;

    // for all the other branches
    for (let i = 0, len = this.branches.length; i < len; i++) {
      let c = this.branches[i];

      // skip ourself
      if (b == c) {
        continue;
      }

      // if the column has been allocated and the two branches overlap
      if ((c.column != null) && c.overlaps(b)) {

        // if they are siblings, we want to use this column if there are no other conflicts
        if (b.isSibling(c)) {

          freeColumn = c.column;

          // track sibling branches
          siblingBranches.push(c);

          // else, we can't use this column, so add it to the used list
        } else {
          let usedColumn = c.column;

          if (columnsUsed.indexOf(usedColumn) < 0) {
            columnsUsed.push(usedColumn);
          }
        }
      }
    }

    // if we already have been assigned a column and we have siblings
    if ((b.column != null) && (siblingBranches.length > 0)) {

      let sibCols = [];

      // get unique list of siblings' columns
      for (let i = 0, len = siblingBranches.length; i < len; i++) {
        let col = siblingBranches[i].column;
        if (sibCols.indexOf(col) < 0) {
          sibCols.push(col);
        }
      }

      // if they all agree with each other and with us, there's nothing to do
      if ((sibCols.length == 1) && (sibCols[0] == b.column)) {
        return;
      }
    }

    // if we didn't find a sibling match or the sibling column is in the used list
    if ((freeColumn == null) || (columnsUsed.indexOf(freeColumn) > -1 )) {

      // TODO: Limit the number of columns displayed?

      // assign to next column
      freeColumn = this.maxColAssigned+1;

      // check if there are any free columns in the address range of the branch span
      for (let col = 0, len = this.maxColAssigned+1; col < len; col++) {
        // if we found a free column
        if (columnsUsed.indexOf(col) < 0) {
          freeColumn = col;
          break;
        }
      }

      // must set tag before updating siblings
      b.column = freeColumn;

      // update all siblings
      for (let i = 0, len = siblingBranches.length; i < len; i++) {
        let sib = siblingBranches[i];

        // recursively resolve column conflicts among siblings
        this.setFreeColumn(sib);
      }
    }

    this.maxColAssigned = Math.max(this.maxColAssigned, freeColumn);
    b.column = freeColumn;
  }

  /* -------------------------------------------------------------- *
   *                  P U B L I C   M E T H O D S
   * -------------------------------------------------------------- */

  /* Update the branches represented in this panel */
  setBranches(b) {
    this.branches = [];
    this.hoveredBranches = new Set([]);
    for (var i = 0, len = b.length; i < len; i++) {
      this.branches.push(new Branch(b[i]['from'], b[i]['to'], b[i]['type']));
    }

    /* need to re-highlight based on new branches */
    if (this.highlightedAddr != null) {
      this.highlightByAddr(this.highlightedAddr);
    }
  }

  /* Highlight the branch line associated with the given address */
  highlightByAddr(addr) {
    this.highlightedBranches = new Set([]);
    this.highlightedAddr = addr;

    /* FIRST PASS */
    let firstPass = [];
    /* Find all branches that have a source or target at this address */
    for (var i = 0, len = this.branches.length; i < len; i++) {
      let b = this.branches[i];
      if ((b.srcAddr == addr) || (b.targetAddr == addr)) {
        firstPass.push(b);
        this.highlightedBranches.add(b);
      }
    }

    /* SECOND PASS */
    /* Find all siblings of branches found in the first pass */
    for (var i = 0, len = this.branches.length; i < len; i++) {
      let b = this.branches[i];
      for (var j = 0, len2 = firstPass.length; j < len2; j++) {
        if (b.isSibling(firstPass[j])) {
          this.highlightedBranches.add(b);
          break;
        }
      }
    }

    this.draw();
  }

}
