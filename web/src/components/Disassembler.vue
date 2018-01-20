<template>
  <div>
    <div class="loading" v-if="loading">
      <Loading></Loading>
    </div>

    <div v-if="notFound">
      <NotFound></NotFound>
    </div>

    <div class="hello" v-if="!loading && !notFound">
      <MenuBar></MenuBar>
      <div style="position:absolute; top:60px; left: 20px; right: 20px; height: 20px;">
        <AddressBar></AddressBar>
      </div>
      <div
        style="border-top: 1px solid #c0c0c0; border-bottom: 1px solid #c0c0c0; position: absolute; top: 120px; right: 0px; bottom: 20px; left: 0px; ">
        <SplitBox splitX="400">
          <div slot="left">
            <div v-if="liveMode">
              <LiveEntry></LiveEntry>
            </div>
            <div v-else>
              <FileSidebar></FileSidebar>
            </div>
          </div>

          <div slot="center">
            <!-- <b-card no-body class="here">
              <b-tabs card>
                <b-tab title="Tab 1" active>
                  <div style="position:absolute; left:0;right:0;top:32px;bottom:0;">
                    <Listing></Listing>
                  </div>
                </b-tab>
                <b-tab title="Graph">
                  <br>I'm the graph
                </b-tab>
                <b-tab title="Hex">
                  <br>I'm the hex
                </b-tab>
                <b-tab title="Sections">
                  <br>I'm the sections
                </b-tab>
                <b-tab title="File Info">
                  <br>I'm the file info
                </b-tab>
              </b-tabs>
            </b-card>  -->

            <b-tabs style="margin-left:5px;" v-model="tabIndex">
              <b-tab title="Disassembly" active>
                <div style="position:absolute; left:0;right:0;top:45px;bottom:0;">
                  <Listing></Listing>
                </div>
              </b-tab>
              <b-tab title="Graph">
                <div style="position:absolute; left:0;right:0;top:45px;bottom:0;">
                  <GraphView :visible="graphVisible"></GraphView>
                </div>
              </b-tab>
              <b-tab title="Hex">
                <HexView></HexView>
              </b-tab>
              <b-tab title="Sections">
                <div style="position:absolute; top:42px; left:0; right:0; bottom:0; overflow: scroll;">
                  <Sections></Sections>
                </div>
              </b-tab>
              <b-tab title="File Info">
                <div style="position:absolute; top:32px; left:0; right:0; bottom:0; overflow: scroll;">
                  <FileInfo></FileInfo>
                </div>
              </b-tab>
            </b-tabs>

            <!-- <SplitBox splitX="600">
              <div slot="left">
                <Listing></Listing>
              </div>
            </SplitBox>  -->
          </div>
          <div slot="right">
            <Decompiler></Decompiler>
          </div>
        </SplitBox>
      </div>
      <StatusBar></StatusBar>
    </div>

    <UploadFileModal></UploadFileModal>
    <ConfigureUploadModal></ConfigureUploadModal>
    <SharingModal></SharingModal>
    <CommentModal></CommentModal>
    <GotoAddressModal></GotoAddressModal>
    <EditFunctionModal></EditFunctionModal>
    <DefinedDataModal></DefinedDataModal>
  </div>
</template>

<script>
  import MenuBar from '@/components/MenuBar'
  import SplitBox from '@/components/SplitBox'
  import Listing from '@/components/Listing'
  import AddressBar from '@/components/AddressBar'
  import FileSidebar from '@/components/FileSidebar'

  import LiveEntry from './sidebar/LiveEntry'
  import Decompiler from './Decompiler'

  import Sections from '@/components/tabs/Sections'
  import FileInfo from '@/components/tabs/FileInfo'
  import HexView from '@/components/tabs/HexView'
  import GraphView from '@/components/tabs/GraphView'

  import UploadFileModal from '@/components/modals/UploadFileModal'
  import ConfigureUploadModal from '@/components/modals/ConfigureUploadModal'
  import SharingModal from '@/components/modals/SharingModal'
  import CommentModal from '@/components/modals/CommentModal'
  import GotoAddressModal from './modals/GotoAddressModal'
  import Loading from './Loading'
  import EditFunctionModal from './modals/EditFunctionModal'
  import DefinedDataModal from './modals/DefinedDataModal'
  import NotFound from './NotFound'

  import StatusBar from './StatusBar'

  import * as types from '@/store/mutation-types.js'

  import {mapState} from 'vuex'
  import {copyOdaMaster, canEdit} from '../api/oda'
  import {OPEN_LISTING_TAB, bus} from '../bus'

  export default {
    name: 'HelloWorld',
    data () {
      return {
        notFound: null,
        loading: true,
        tabIndex: 0,
        graphVisible: false
      }
    },
    components: {
      MenuBar,
      SplitBox,
      Listing,
      AddressBar,
      FileSidebar,
      FileInfo,
      Sections,
      HexView,
      LiveEntry,
      UploadFileModal,
      ConfigureUploadModal,
      GraphView,
      SharingModal,
      StatusBar,
      CommentModal,
      Decompiler,
      Loading,
      GotoAddressModal,
      EditFunctionModal,
      DefinedDataModal,
      NotFound
    },
    computed: mapState([
      'liveMode'
    ]),
    created () {
      // fetch the data when the view is created and the data is
      // already being observed
      this.fetchData()

      bus.$on(OPEN_LISTING_TAB, () => { this.tabIndex = 0 })
    },
    watch: {
      // call again the method if the route changes
      '$route': 'fetchData',
      tabIndex () {
        this.graphVisible = (this.tabIndex === 1)
      }
    },
    methods: {
      async fetchData () {
        this.loading = true
        let shortName = this.$route.params.shortName
        let own = null
        try {
          own = await canEdit(shortName)
        } catch (e) {
          this.loading = false
          this.notFound = true
          return
        }
        if (!own) {
          let copiedShortName = null
          try {
            copiedShortName = await copyOdaMaster(shortName)
          } catch (e) {
            this.notFound = true
            return
          }
          this.$router.replace('/odaweb/' + copiedShortName)
          return
        }
        // this.$store.commit(types.SET_SHORTNAME, {shortName: '3AxQibd5'})
        this.$store.commit(types.SET_SHORTNAME, {shortName: shortName})
        await this.$store.dispatch('loadOdbFile')
        this.loading = false
        this.notFound = false
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  > > > .nav-link {
    padding: 3px 18px;
    font-size: 14px;
  }

  >>> .nav-tabs {
    padding-top: 2px;
    padding-left: 6px;
  }

  >>> .nav-item a {
    color: #b5b5b5;
  }

  >>> .card-header {
    padding: 0.15rem 1.25rem 0.75rem 1.25rem;
  }

</style>
