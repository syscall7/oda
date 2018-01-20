import {bus, EVENT_SCROLLED} from '../bus'
import $ from 'jquery'

export function Scroller (viewportLineHeight) {
  var subPixelscrollTop = 0
  var topInstrLength = 1

  this.setTop = function (lineNumber) {
    subPixelscrollTop = lineNumber * viewportLineHeight
    $('.disassembly-scroll').scrollTop(Math.floor(subPixelscrollTop))
    bus.$emit(EVENT_SCROLLED, {scrollTop: Math.floor(subPixelscrollTop)})
  }

  this.accumulate = function (movement) {
    if ((subPixelscrollTop - movement / topInstrLength) < 0) {
      if (subPixelscrollTop !== 0) {
        subPixelscrollTop = 0
      } else {
        // Scrolling up when we're at the top
        return
      }
    } else {
      subPixelscrollTop = Math.max(0, subPixelscrollTop - movement / topInstrLength)
    }
    // TODO: MINs
    // TODO: Because this only deals with situation where a multiline du is on the
    // TOP line, it's behaves 'incorrectly' when scrolling fast (because lines below the top
    // line are not property accounted for
    $('.disassembly-scroll').scrollTop(Math.floor(subPixelscrollTop))

    bus.$emit(EVENT_SCROLLED, {scrollTop: Math.floor(subPixelscrollTop)})
  }

  this.setTopInstructionLength = function (length) {
    topInstrLength = length
  }

  $('.disassembly-scroll').scroll(function () {
    var newScrollTop = $('.disassembly-scroll').scrollTop()
    if (newScrollTop === Math.floor(subPixelscrollTop)) {
      // We Already Know
      return
    }
    subPixelscrollTop = newScrollTop
    bus.$emit(EVENT_SCROLLED, {scrollTop: newScrollTop})
  })

  this.numLinesShown = function () {
    return Math.floor($('.disassembly-viewport').height() / viewportLineHeight + 1)
  }

  $('.disassembly-viewport').on('wheel', function (event) {
    let wheelEvent = event.originalEvent
    this.accumulate(-wheelEvent.deltaY)
    event.preventDefault()
  }.bind(this))
}
