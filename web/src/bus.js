import Vue from 'vue'

export const EVENT_SCROLLED = 'scroller.scrolled'
export const CLOSE_SIDEBAR = 'sidebar.close'

export const NAVIGATE_TO_ADDRESS = 'navigate.to.address'

export const ADDRESS_AT_TOP_CHANGED = 'address.at.top.changed'
export const LIVE_ENTRY_CHANGED = 'live.entry.changed'

export const SHOW_FILE_UPLOAD_MODAL = 'show.file.upload.modal'
export const SHOW_DECOMPILER_WINDOW = 'show.decompiler.window'
export const HIDE_DECOMPILER_WINDOW = 'hide.decompiler.window'
export const SHOW_CONFIGURE_FILE_MODAL = 'show.configure.file.modal'
export const SHOW_SHARING_MODAL = 'show.sharing.modal'
export const SHOW_COMMENT_MODAL = 'show.comment.modal'
export const SHOW_DEFINED_DATA_MODAL = 'show.defined.data.modal'
export const SHOW_FUNCTION_MODAL = 'show.function.modal'
export const SHOW_GOTOADDRESS_MODAL = 'show.gotoaddress.modal'
export const SHOW_FINDBYTES_PANEL = 'show.findbytes.panel'
export const SHOW_SYMBOLS_PANEL = 'show.symbols.panel'
export const SHOW_STRINGS_PANEL = 'show.strings.panel'
export const OPEN_LISTING_TAB = 'open.listing.tab'

export const MODAL_HIDDEN = 'modal.hidden'

export const API_ERROR = 'api.error'

export const bus = new Vue()
