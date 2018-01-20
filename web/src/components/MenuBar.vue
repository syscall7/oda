<template>
  <div class="oda-menu-bar" style="position: absolute; height: 31px; left: 0px; top: 34px; right: 0px;">
    <div class="oda-mbar-cont" id="q2">
      <div class="basic fakehbox aligncenter menubar" style="padding : 0 5px 0 50px;position:static" id="q4">
        <b-dropdown id="ddown1" no-caret variant="link">
          <template slot="button-content">
            File
          </template>
          <b-dropdown-item @click="uploadFile()">Upload File <i class="menu-icon fa fa-upload"></i></b-dropdown-item>
          <b-dropdown-item @click="downloadDisassembly()">Download Disassembly  <i class="menu-icon fa fa-download"></i></b-dropdown-item>
          <b-dropdown-item @click="liveMode()">Live Mode <i class="menu-icon fa fa-play-circle"></i></b-dropdown-item>
        </b-dropdown>
        <b-dropdown id="ddown1" no-caret variant="link">
          <template slot="button-content">
            Edit
          </template>
          <b-dropdown-item @click="gotoAddresss">Goto Address <span class="menu-icon">(ctrl-g)</span></b-dropdown-item>
          <b-dropdown-item @click="findBytes">Find Sequence Of Bytes <span class="menu-icon">(ctrl-f)</span></b-dropdown-item>
        </b-dropdown>
        <b-dropdown id="ddown1" no-caret variant="link">
          <template slot="button-content">
            View
          </template>
          <b-dropdown-item @click="showSymbols">Symbols</b-dropdown-item>
          <b-dropdown-item @click="showStrings">Strings</b-dropdown-item>
          <b-dropdown-item @click="showDecompiler">Decompiler</b-dropdown-item>
        </b-dropdown>
        <b-dropdown id="ddown1" no-caret variant="link">
          <template slot="button-content">
            Help
          </template>
          <b-dropdown-item v-b-modal="'whats-oda'">What's ODA?</b-dropdown-item>
          <b-dropdown-item>Tutorial</b-dropdown-item>
          <b-dropdown-item v-b-modal="'about-oda'">About</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <b-modal id="whats-oda" size="lg" title="What's ODA?" ok-only>
      <div>
        <img src="../assets/oda.png" style="float:left"/>
        <b>ODA</b> stands for <b>O</b>nline <b>D</b>is<b>A</b>ssembler.  <b>ODA</b> is a general purpose machine code disassembler
        that supports a myriad of machine architectures.  Built on the shoulders of libbfd and libopcodes (part of
        binutils), <b>ODA</b> allows you to explore an executable by dissecting its sections, strings,
        symbols, raw hex, and machine level instructions.

        <p><p>You can use it for a variety of purposes such as:

        <ul>
          <li>Malware analysis</li>
          <li>Vulnerability research</li>
          <li>Visualizing the control flow of a group of instructions</li>
          <li>Disassembling a few bytes of an exception handler that is going off into the weeds</li>
          <li>Reversing the first few bytes of a Master Boot Record (MBR) that may be corrupt</li>
          <li>Debugging an embedded systems device driver</li>
          <li>Satisying your own intellectual curiosity (Does there exist some sequence of bytes that disassembles to the same logical operation for two separate platforms?)</li>
        </ul>

        <p><p>See the <a href="http://blog.onlinedisassembler.com/blog/?p=44">tutorial</a> for an overview of <b>ODA</b>'s features.

        <p><p><b>ODA</b> is a BETA release that is limited by the resource constraints of the server on which it is
        hosted and the spare time of its creators.  If you find <b>ODA</b> useful, have a feature request, or want to
        comment in any way, please <a href="mailto:admin@onlinedisassembler.com">drop us a line!</a>

        <h4>Supported Architectures</h4>
        <ul style="height:200px;overflow: scroll;">
          <li v-for="arch in architectures">{{ arch }}</li>
        </ul>

      </div>
    </b-modal>

    <b-modal id="about-oda" size="lg" title="About Oda" ok-only>
      <div>
        <p class="float-left"><img src="/static/oda.png"></p>
        <b>ODA</b> is the creation of Anthony DeRosa, Tom Keeley, and Bill Davis
        <p></p>
        Version: 4.0.0<br>
        Release Date: 1/20/2017
      </div>
    </b-modal>

  </div>
</template>


<script>
  import { mapState } from 'vuex'
  import {
    bus,
    SHOW_FILE_UPLOAD_MODAL,
    SHOW_DECOMPILER_WINDOW,
    SHOW_GOTOADDRESS_MODAL,
    SHOW_FINDBYTES_PANEL, SHOW_SYMBOLS_PANEL, SHOW_STRINGS_PANEL
  } from '../bus'
  export default {
    name: 'MenuBar',
    data () {
      return {
      }
    },
    computed: mapState([
      'shortName', 'revision', 'architectures'
    ]),
    methods: {
      liveMode: function () {
        this.$router.push({path: '/odaweb/strcpy_x86'})
      },
      downloadDisassembly: function () {
        window.location = '/odaweb/_download?short_name=' + this.shortName + '&revision=' + this.revision
      },
      uploadFile () {
        bus.$emit(SHOW_FILE_UPLOAD_MODAL)
      },
      showDecompiler () {
        bus.$emit(SHOW_DECOMPILER_WINDOW)
      },
      gotoAddresss () {
        bus.$emit(SHOW_GOTOADDRESS_MODAL)
      },
      findBytes () {
        bus.$emit(SHOW_FINDBYTES_PANEL)
      },
      showSymbols () {
        bus.$emit(SHOW_SYMBOLS_PANEL)
      },
      showStrings () {
        bus.$emit(SHOW_STRINGS_PANEL)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .oda-mbar-cont {
    position: relative;
    /*overflow: hidden;*/
    padding: 0 74px 0 22px;
    margin: 0;
    height: 25px;
    background: #252525;
    box-shadow: 0 1px 0 0 #353535 inset;
    border-bottom: 1px solid #000000;
    border-top: 1px solid #000000;
  }

  .oda-menu-btn {
    height: 100%;
    box-sizing: border-box;
    overflow: visible;
    cursor: default;
    position: relative;
    display: inline-block;
    font-family: Tahoma, Arial;
    font-size: 12px;
    line-height: 14px;
    color: #cecece;
    padding: 4px 7px 4px 7px;
    text-shadow: #292a2b 0px 1px 0px;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
  }

  .oda-menu-btn:hover {
    background-color: #333333;
    box-shadow: 1px -1px 0 0 #000000, -1px 0 0 0 #000000, 0 1px 0 0 rgba(255, 255, 255, 0.15) inset;
    color: #d4d4d4;
  }

  >>> .dropdown .btn {
    padding: 0px 5px;
  }

  >>> .btn-link {
    color: #bbb;
  }

  >>> .dropdown-menu {
    font-size: 85%;
  }

  >>> .dropdown .dropdown-menu .dropdown-item:focus {
    outline: none;
  }

  >>> .dropdown-item {
    padding-right: 50px;
  }

  .menu-icon {
    position: absolute;
    right: 10px;

  }
</style>
