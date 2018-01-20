import Q from 'q'

class DuWindow {
  constructor (start, dus) {
    this.start = start
    this.dus = dus
  }

  containsRange (ldu, number) {
    if (ldu > this.start && (ldu + number) < (this.start + this.dus.length)) {
      return true
    }
    return false
  }

  getInstructions (ldu, number) {
    return this.dus.slice(ldu - this.start, ldu - this.start + number)
  }
}

export class DuWindowManager {
  constructor (odbFile) {
    var self = this
    this.odbFile = odbFile
    this.odbFile.getInstructions(0, 50).then(function (dus) {
      self.currentWindow = new DuWindow(0, dus)
    })
  }

  getInstructions (ldu, number) {
    if (this.currentWindow && this.currentWindow.containsRange(ldu, number)) {
      var dus = this.currentWindow.getInstructions(ldu, number)
      return Q.resolve(dus)
    }
    return this.odbFile.getInstructions(ldu, number)
  }

  getInstruction (ldu) {
    return this.odbFile.getInstruction(ldu)
  }
}
