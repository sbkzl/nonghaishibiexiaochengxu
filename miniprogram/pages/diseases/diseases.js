Page({
  data: { list: [], baseUrl: "http://10.91.226.115:8000" },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
    this.loadDiseases()
  },

  loadDiseases() {
    wx.request({
      url: this.data.baseUrl + "/diseases",
      success: (res) => {
        if (res.data.code === 200) {
          const list = res.data.data.map(item => ({ ...item, open: false }))
          this.setData({ list })
        }
      }
    })
  },

  toggle(e) {
    const idx = e.currentTarget.dataset.index
    const key = 'list[' + idx + '].open'
    this.setData({ [key]: !this.data.list[idx].open })
  }
})
