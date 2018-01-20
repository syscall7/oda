<template>
  <div class="container" style="padding:30px;">
    <div class="row">
      <div class="span9 file-info-group">
        <table class="file-info-table table">
          <tr>
            <td class="file-info-label">Project:</td>
            <td>{{ projectName }}</td>
          </tr>
          <tr>
            <td class="file-info-label">File:</td>
            <td>{{ binary.name }}</td>
          </tr>
          <tr>
            <td class="file-info-label">Format:</td>
            <td>
              <ul>
                <li v-for="d in binary.desc">
                  {{ d }}
                </li>
              </ul>
            </td>
          </tr>
          <tr>
            <td class="file-info-label">Size:</td>
            <td>{{ binary.size }}</td>
          </tr>
          <tr>
            <td class="file-info-label">MD5:</td>
            <td>{{ binary.md5 }}</td>
          </tr>
          <tr>
            <td class="file-info-label">SHA-1:</td>
            <td>{{ binary.sha1 }}</td>
          </tr>
        </table>
      </div>

    </div>

    <div class="row">
      <div class="span9">&nbsp;</div>
    </div>

    <div class="row">

      <div class="span3 file-info-group">
        <table class="file-info-table">
          <tr>
            <td id="known-malware"
                class="file-info-label"
                data-placement="right"
                data-title="Malware Lookup"
                data-html="true"
                data-trigger="hover"
                data-delay='{"show":100,"hide":2000}'
                data-content="If 'yes', this binary is known malware based on Cymru's <a href='http://www.team-cymru.org/Services/MHR/'>Malware Hash Registry</a>.  If 'no', it might still be malware.  Good luck determining that on your own!">
              Known Malware: {{ binary.malware }}
            </td>
          </tr>
          <tr>
            <td id="known-benign"
                class="file-info-label"
                data-placement="right"
                data-title="Benign Lookup"
                data-html="true"
                data-trigger="hover"
                data-delay='{"show":100,"hide":2000}'
                data-content="If 'yes', this binary is known to be harmless based on the <a href='http://www.nsrl.nist.gov/'>National Software Reference Library</a>.  If 'no', it still might be harmless.  Good luck determining that on your own!">
              Known Benign: {{ binary.benign }}
            </td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
  import {mapState} from 'vuex'

  export default {
    name: 'FileInfo',
    data () {
      return {}
    },
    computed: mapState(['projectName', 'binary'])
  }
</script>

<style scoped>
  .file-info-label {
    vertical-align: top;
    color: #093C83;
  }
  .file-info-table {
    font-family: monospace;
    font-size: 14px;
    line-height: 14px;
    color: dimgrey;
  }
</style>

