import Vue from 'vue'

export function toHex (value) {
  if (value !== 0 && !value) return ''
  let stringValue = value.toString(16)
  let s = '000000000' + stringValue
  let bytes = 8
  if (stringValue.length > 8) {
    s = '000000000000000000' + stringValue
    bytes = 16
  }

  return s.substr(s.length - bytes)
}

Vue.filter('hex', function (value) {
  return toHex(value)
})
