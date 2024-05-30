
uploadButton4 = document.getElementById("upload4")
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
// 实现上传按钮
uploadButton4.addEventListener("click", function(){
    uploadFile("rgbImage","imageInputRgb")
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


// 调用土地利用分类函数
function multimodingImageRgb(){
    // 获取链接
    let image = document.getElementById("rgbImage")
    // 形成数据
    let data = {
        imageUrl: image.src
    }
    // 发起请求
     let rgbPromise = fetch('/classify', {
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
      return {"url":parsedData.resultUrl,"data":parsedData.sum_dict,"chatResult":parsedData.chatResult}; // 返回的数据对象的 url 属性
    })
    .catch(error => {
      // 处理错误
      console.error('Error:', error);
      throw error; // 重新抛出错误，以便外部代码可以捕获
    });

    // 使用 multi_Promise
    rgbPromise.then(result => {
        console.log("___________________result:",result)
        // 定义echarts的对象
        let landChart = echarts.init(document.getElementById('chart1'));
        // 处理获取到的 URL
        let url = result.url
        let chatText = result.chatResult
        data = result.data
        console.log('resultUrl:', url);
        console.log('data:', data)
        console.log('chatResult:', chatText)
        let dataList = []  // 重组数据源
        for (let key in data){
            dataList.push({"name":key,"value":data[key]})
        };
        // 显示分析的结果
        document.getElementById("cardText").innerText = chatText

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
                    name: '数据：',
                    type: 'pie',
                    radius: '50%',
                    data: dataList,  // 使用数据
                    itemStyle: {
                        color: function (params) {
                            // 根据每个扇区的数据项返回不同的颜色
                            let colorList = [
                                '#ffd700','#b41e1e' ,'#000000','#228b22','#0000ff', '#646464','#ffffff','#dcdcdc'
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
        changeImage(url,"222")
    }).catch(error => {
      // 处理可能发生的任何错误
      console.error('Promise error:', error);
    });

}
// 开始运行
startButton = document.getElementById('startButtonRgb')
startButtonRgb.addEventListener("click", function (){
    multimodingImageRgb()
})


// 将数据显示到地图上
let mapButton = document.getElementById("mapButton")
mapButton.addEventListener("click", function (){
    let image = document.getElementById("222")
    let input = document.getElementById("InputLocation1")
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




