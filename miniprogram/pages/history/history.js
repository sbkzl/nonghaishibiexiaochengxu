Page({
  data: { list: [], baseUrl: "http://10.91.226.115:8000" },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
    this.loadHistory()
  },

  loadHistory() {
    wx.request({
      url: this.data.baseUrl + "/history",
      success: (res) => {
        if (res.data.code === 200) {
          const list = res.data.data.map(item => ({
            ...item,
            confidence: (parseFloat(item.confidence) * 100).toFixed(1) + '%',
            fix_url: item.image_url.replace('http://127.0.0.1:8000', this.data.baseUrl)
          }))
          this.setData({ list })
        }
      }
    })
  },

  previewImage(e) {
    wx.previewImage({ urls: [e.currentTarget.dataset.url] })
  },

  deleteItem(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: "确认删除",
      content: "确定要删除这条识别记录吗？",
      success: (res) => {
        if (res.confirm) {
          wx.request({
            url: this.data.baseUrl + "/history/" + id,
            method: "DELETE",
            success: () => {
              wx.showToast({ title: "删除成功" })
              this.loadHistory()
            }
          })
        }
      }
    })
  }
})
