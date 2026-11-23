Page({
  data: {
    recommend: {},
    baseUrl: "http://10.91.226.115:8000"
  },
  onShow() {
    this.loadRecommend()
  },
  loadRecommend() {
    wx.request({
      url: this.data.baseUrl + "/recommend",
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({ recommend: res.data.data })
        }
      }
    })
  },
  goDetect() { 
    wx.switchTab({ url: '/pages/detect/detect' }) 
  },
  goDiseases() { 
    wx.switchTab({ url: '/pages/diseases/diseases' }) 
  },
  goHistory() { 
    wx.switchTab({ url: '/pages/history/history' }) 
  },
  goStats() { 
    wx.switchTab({ url: '/pages/stats/stats' }) 
  }
})
