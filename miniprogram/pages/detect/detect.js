Page({
  data: {
    previewImg: "",
    loading: false,
    resultData: null,
    baseUrl: "http://10.91.226.115:8000"
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 4 })
    }
  },

  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      success: (res) => {
        this.setData({ previewImg: res.tempFiles[0].tempFilePath, resultData: null })
      }
    })
  },

  submitDetect() {
    if (!this.data.previewImg) return
    this.setData({ loading: true })
    wx.uploadFile({
      url: this.data.baseUrl + "/upload",
      filePath: this.data.previewImg,
      name: "file",
      success: (res) => {
        const json = JSON.parse(res.data)
        if (json.code === 200) {
          this.setData({ resultData: json.data })
          wx.showToast({ title: "识别成功" })
        } else {
          wx.showToast({ title: json.msg || "识别失败", icon: "none" })
        }
      },
      fail: () => {
        wx.showToast({ title: "连接后端失败", icon: "none" })
      },
      complete: () => this.setData({ loading: false })
    })
  }
})
