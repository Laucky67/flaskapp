uploadButton5 = document.getElementById("upload5")
uploadButton6 = document.getElementById("upload6")


function changeImage(url,imageId){
    const img = document.getElementById(imageId);
    console.log(img)
    img.src = url;
}
// 上传图像
function uploadFile(imageId,uploadForm) {
      let image_input = document.getElementById(uploadForm);
      let file = image_input.files[0];
      const formData = new FormData();
      formData.append('file',file)
      fetch('/upload_RGB', {
        method: 'POST',
        body: formData
      }).then(response => {
        if (!response.ok) {
          throw new Error('Error uploading file');
        }
        return response.json(); // 解析JSON响应
      }).then(data => {
        // 服务器返回的JSON对象包含一个'url'键
          let imageUrl = data.url; // 从JSON对象中获取URL
          let location = data.location
          imageLocation = location
          console.log(imageUrl);
          changeImage(imageUrl, imageId)
        console.log('File uploaded successfully');
        console.log(location)

      }).catch(error => {
        console.log('Error:', error);
      });

    }


uploadButton5.addEventListener("click", function() {
    uploadFile("imageTerrainRecognition", "imageInputMultimode")
})

uploadButton6.addEventListener("click", function() {
    uploadFile("imageClassify", "imageInputClassify")
})


function overlayAnalysis(){
    // 获取链接
    let image1 = document.getElementById("imageTerrainRecognition")
    let image2 = document.getElementById("imageClassify")
    // 形成数据
    let data = {
        multimodingUrl: image1.src,
        classifyUrl: image2.src
    }
    // 发起请求
     let rgbPromise = fetch('/overlayAnalysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json(); // 返回一个解析 JSON 的 Promise
    })
    .then(parsedData => {
      // 解析后的数据在这里处理
      console.log('Success:', parsedData);
      return {"url":parsedData.resultUrl,"data":parsedData.class_count,"chatResult":parsedData.chatResult}; // 返回的数据对象的 url 属性
    })
    .catch(error => {
      // 处理错误
      console.error('Error:', error);
      throw error; // 重新抛出错误，以便外部代码可以捕获
    });

    // 使用 multi_Promise
    rgbPromise.then(result => {
        // 定义echarts的对象
        let landChart = echarts.init(document.getElementById('chart1'));
        let landChartBar = echarts.init(document.getElementById('chart2'));
        // 处理获取到的 URL
        let url = result.url
        let data = result.data
        let text = result.chatResult
        document.getElementById("cardText").innerText = text
        console.log('resultUrl:', url);
        console.log('data:', data)
        let dataList = []  // 重组数据源
        let nameList = []  // 重组数据源
        let valueList = []  // 重组数据源
        dataList = Object.keys(data).map(key => ({ name: key, value: data[key] }));
        nameList = Object.keys(data);
        valueList = Object.values(data);
        console.log('dataList:', dataList)
        console.log('nameList:', nameList)
        console.log('valueList:', valueList)
        let option = {
            title: { text: '综合分析结果', left: 'center' },
            tooltip: { trigger: 'item' },
            legend: { orient: 'vertical', left: 'button' },
            series: [{
                name: '数据：',
                type: 'pie',
                radius: '50%',
                data: dataList,
                itemStyle: {
                        color: function (params) {
                            // 根据每个扇区的数据项返回不同的颜色
                            let colorList = [
                                '#DC143C', '#cbc0ff', '#FFD700','#000000','#0000FF','#dcdcdc'
                            ];
                            return colorList[params.dataIndex];
                        }
                    },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        let option2 = {
                              title: {
                                text: '综合分析结果',
                                left: 'center'
                              },
                              xAxis: {
                                  type: 'category', // 假设x轴是类目轴
                                  data: nameList,
                                  axisLabel: {
                                    show: true, // 是否显示标签
                                    rotate: 45, // 标签旋转的角度，例如设置为45度
                                    color: '#333', // 标签的字体颜色
                                    fontWeight: 'normal', // 标签的字体粗细
                                    verticalAlign: 'middle', // 文字垂直对齐方式，默认是'middle'
                                },

                              },
                              yAxis: {
                                min: 0, // y轴最小值，如果不设置，则自动计算
                                max: 250000, // y轴最大值，如果不设置，则自动计算
                                splitNumber: 6, // 坐标轴的分割段数，默认为5
                              },
                              series: [
                                {
                                  name: '数据：',
                                  type: 'bar',
                                  data: valueList,
                                  itemStyle: {
                                    barBorderRadius: 5,
                                    borderWidth: 1,
                                    borderType: 'solid',
                                    borderColor: '#73c0de',
                                    shadowColor: '#5470c6',
                                    shadowBlur: 3
                                  },
                                  backgroundStyle: {
                                    color: 'rgba(220, 220, 220, 0.8)'
                                  },
                                  emphasis: {
                                    itemStyle: {
                                        shadowBlur: 10,
                                        shadowOffsetX: 0,
                                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                                    }
                                  }

                                }
                              ]
                            };

        landChart.setOption(option)
        landChartBar.setOption(option2)
        // 自动触发饼图图标
        let currentIndex = -1;

        setInterval(function() {
          var dataLen = option.series[0].data.length;
          // 取消之前高亮的图形
          landChart.dispatchAction({
            type: 'downplay',
            seriesIndex: 0,
            dataIndex: currentIndex
          });
          currentIndex = (currentIndex + 1) % dataLen;
          // 高亮当前图形
          landChart.dispatchAction({
            type: 'highlight',
            seriesIndex: 0,
            dataIndex: currentIndex
          });
          // 显示 tooltip
          landChart.dispatchAction({
            type: 'showTip',
            seriesIndex: 0,
            dataIndex: currentIndex
          });
        }, 1000);
        changeImage(url,"resultimage")
    }).catch(error => {
      // 处理可能发生的任何错误
      console.error('Promise error:', error);
    });

}

startBuuton = document.getElementById("startAnalysis")
startBuuton.addEventListener("click",function (){
    overlayAnalysis()
})

// 将数据显示到地图上
// 将数据显示到地图上
let mapButton = document.getElementById("mapButton")
mapButton.addEventListener("click", function (){
    let image = document.getElementById("resultImage")
    let input = document.getElementById("InputLocation2")
    let location
    if(input.value.trim().length ===0 ){

        location = 0
    }
    else {
        location = input.value
    }
    let url = image.src
    console.log("url:",url)
    fetch('/map_show', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'url': url,'location':location})
            })
            .then(data => {
                console.log('Success:', data)

                console.log('Redirecting to:', data.redirected)
                window.location.href = '/map2'; // 跳转到重定向URL

            })
            .catch(error => console.error('Error:', error));

})


