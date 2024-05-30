uploadButton1 = document.getElementById("upload1")
uploadButton2 = document.getElementById("upload2")
uploadButton3 = document.getElementById("upload3")
// 改变图像
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
      fetch('/upload', {
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
// 实现上传按钮
uploadButton1.addEventListener("click", function() {
    console.log("uploadButton1")
    uploadFile("near-infrared", "imageInput1")
})
uploadButton2.addEventListener("click", function() {
    uploadFile("DEMImage","imageInput2")
})

uploadButton3.addEventListener("click", function(){
    uploadFile("slopeImage","imageInput3")
})
function  changeState(clickId){
    clickButton = document.getElementById(clickId)
     if (clickButton.classList.contains('active')) {
        clickButton.classList.remove('active');
        clickButton.classList.add('link-dark');
      } else {
        clickButton.classList.add('active');
        clickButton.classList.remove('link-dark');
      }

    if (clickId === "siderButton1"){
        let otherButton1 = document.getElementsByClassName("siderButton2")
        let otherButton2 = document.getElementsByClassName("siderButton3")
        otherButton1.classList.remove()
        otherButton2.class = "nav-link link-dark"
    }
    else if (clickId === "siderButton2"){
        let otherButton1 = document.getElementsByClassName("siderButton1")
        let otherButton2 = document.getElementsByClassName("siderButton3")
        otherButton1.class = "nav-link link-dark"
        otherButton2.class = "nav-link link-dark"
    }
    else if (clickId === "siderButton3"){
        let otherButton1 = document.getElementsByClassName("siderButton1")
        let otherButton2 = document.getElementsByClassName("siderButton2")
        otherButton1.class = "nav-link link-dark"
        otherButton2.class = "nav-link link-dark"
    }
}



// 更换url的拓展名
function replaceFileExtension(url, newExtension) {
    // 使用正则表达式找到文件扩展名并替换它
    return url.replace(/\.[^.]+$/, `.${newExtension}`);
}

// 多模态图像处理
function multimodingImage(){
    // 获取图像的url
    let image_near_infrared_src = document.getElementById("near-infrared").src
    let image_DEM_src = document.getElementById("DEMImage").src
    let image_slope_src = document.getElementById("slopeImage").src
    // 更换后缀名
    let Tif_near_infrared_src = replaceFileExtension(image_near_infrared_src, "tif")
    let Tif_DEM_src = replaceFileExtension(image_DEM_src, "tif")
    let Tif_slope_src = replaceFileExtension(image_slope_src, "tif")
    // 打包数据
    let data = {
        "near-infrared": Tif_near_infrared_src,
        "DEMImage": Tif_DEM_src,
        "slopeImage": Tif_slope_src
    }
    console.log("data:",data)
    // 假设 data 是一个已经定义的 JavaScript 对象，包含要发送的数据

    let multi_Promise = fetch('/multimoding', {
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
      return parsedData; // 假设返回的数据对象有一个 url 属性
    })
    .catch(error => {
      // 处理错误
      console.error('Error:', error);
      throw error; // 重新抛出错误，以便外部代码可以捕获
    });

    // 使用 multi_Promise
    multi_Promise.then(result => {
        console.log('-_---------result:',result)
        let landChart = echarts.init(document.getElementById('chart1'));
        // 处理获取到的 URL
        let url = result.resultUrl
        let data = result.sum_dict
        let chatText =result.chatResult
        console.log('chatResult:', chatText)
        console.log('resultUrl:', url);
        console.log('data:', data)
        changeImage(url,"111")
        // 修改要素的内容
        document.getElementById('cardText').innerText = chatText;
        let dataList = []  // 重组数据源
        for (let key in data){
            dataList.push({"name":key,"value":data[key]})
        }
        let option = {
            tooltip: {
                trigger: 'item'
            },
            legend: {
                orient: 'vertical',
                left: 'left',
            },
            series: [
                {
                    name: '访问来源',
                    type: 'pie',
                    radius: '50%',
                    data: dataList,  // 使用数据
                    itemStyle: {
                        color: function (params) {
                            // 根据每个扇区的数据项返回不同的颜色
                            let colorList = [
                                '#FFF0F5', '#C71585', '#2F4F4F'
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
                }
            ]
        };
        landChart.setOption(option)

    }).catch(error => {
      // 处理可能发生的任何错误
      console.error('Promise error:', error);
    });
}
// 开始运行
startButton = document.getElementById("startButton")
startButton.addEventListener("click", function (){
    multimodingImage()
})


// 将数据显示到地图上
let mapButton = document.getElementById("mapButton")
mapButton.addEventListener("click", function (){
    let image = document.getElementById("111")
    let input = document.getElementById("InputLocation")
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


