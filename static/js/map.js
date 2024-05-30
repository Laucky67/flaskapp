// 存放地理位置坐标数据
var imageLocation = []

// 定义地图控件
let overviewMapControl = new ol.control.OverviewMap({
      className: 'ol-overviewmap ol-custom-overviewmap',
      layers: [
        new ol.layer.Tile({
         title: "高德地图",
          // 使用高德
         source: new ol.source.XYZ({
                url: 'https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}&lang=zh_cn&scl=1&sv=7&key=ce2bc8663af5253256250118e9455e5a',
                crossOrigin: 'anonymous',
                attributions: '© 高德地图'
            })
        })

      ],
      collapsed: false
    });

// 定义一个ol地图
let map = new ol.Map({
    target: 'map',
    layers: [
        new ol.layer.Tile({
            source: new ol.source.XYZ({
                title: "高德道路地图",
                url: 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}&lang=zh_cn&scl=1&sv=7&key=ce2bc8663af5253256250118e9455e5a', // 高德地图矢量图源URL
                crossOrigin: 'anonymous',
                attributions: '© 高德地图'
            })
        }),
        new ol.layer.Tile({
            source: new ol.source.XYZ({
                title: "高德卫星地图",
                url: 'https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}&lang=zh_cn&scl=1&sv=7&key=ce2bc8663af5253256250118e9455e5a', // 高德地图矢量图源URL
                crossOrigin: 'anonymous',
                attributions: '© 高德地图'
            })
        })

    ],
    view: new ol.View({
        center: ol.proj.fromLonLat([100.25, 29.25]), // 北京的经纬度坐标
        projection: 'EPSG:3857',
        zoom: 10 // 地图的初始缩放级别
    }),
    // 添加控件
   controls: ol.control.defaults.defaults({
        // 在默认控件的基础上添加自定义控件
        attributionOptions: {
            collapsible: false
        }
    }).extend([
        // 添加比例尺控件
        new ol.control.ScaleLine(),
        // 添加缩放滑块控件
        new ol.control.ZoomSlider(),
        // 添加全屏控件
        new ol.control.FullScreen(),
        overviewMapControl
    ])
});

// 修改图像,显示图像
function uploadImage(url,imageId){
    var img = document.getElementById(imageId);
    var imgSrc = img.getAttribute('src');
    img.src = url;

};

// 显示range的实时数字
document.addEventListener('DOMContentLoaded', function() {
  var range = document.getElementById('high_k');
  var valueDisplay = document.getElementById('rangeValue_high');
  range.addEventListener('input', function() {
    valueDisplay.textContent = this.value;
  });
});
document.addEventListener('DOMContentLoaded', function() {
  var range = document.getElementById('low_k');
  var valueDisplay = document.getElementById('rangeValue_low');
  range.addEventListener('input', function() {
    valueDisplay.textContent = this.value;
  });
});
document.addEventListener('DOMContentLoaded', function() {
  var range = document.getElementById('mid_k');
  var valueDisplay = document.getElementById('rangeValue_mid');
  range.addEventListener('input', function() {
    valueDisplay.textContent = this.value;
  });
});
document.addEventListener('DOMContentLoaded', function() {
  var range = document.getElementById('log_k');
  var valueDisplay = document.getElementById('rangeValue_log');
  range.addEventListener('input', function() {
    valueDisplay.textContent = this.value;
  });
});
document.addEventListener('DOMContentLoaded', function() {
  var range = document.getElementById('gamma_k');
  var valueDisplay = document.getElementById('rangeValue_gamma');
  range.addEventListener('input', function() {
    valueDisplay.textContent = this.value;
  });
});


// 将元素添加到处理流程中并在容器中显示
var listProcess = Array();
var processValue = Array()
function addBadge(processName,value= 0) {
  var badgeContainer = document.getElementById("processStream");
  listProcess.push(processName)
    processValue.push(value)
  // 创建一个新的徽章
  var newBadge = document.createElement('div');
  newBadge.className = "badge rounded-pill bg-secondary";
  newBadge.textContent = processName;

  // 将徽章添加到徽章容器中
  badgeContainer.appendChild(newBadge);
  console.log(listProcess)

}

function uploadFile() {
      var formData = new FormData(document.getElementById('uploadForm'));
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
          var imageUrl = data.url; // 从JSON对象中获取URL
          var location = data.location
          imageLocation = location
          console.log("location:",location)
          console.log(imageUrl);
          raw_png_location = imageUrl
        //var extent = ol.proj.transformExtent([73, 12.2, 135, 54.2], 'EPSG:4326', 'EPSG:3857');
          //var extent = location
          uploadImage(imageUrl, 'rawImage')
          uploadImage(imageUrl, 'rawImage2')
        map.addLayer(
          new ol.layer.Image({
            source: new ol.source.ImageStatic({
                title:"数据图层",
                url: imageUrl,
                projection: 'EPSG:3857',
                imageExtent: location //映射到地图的范围
            })
          })
        )
        console.log("mapLayers:",map.getLayers());
        console.log('File uploaded successfully');
        console.log(location)

        // 设置地图的中心点
        var newCenter= [location[0], location[1]]; // 将经纬度转换为地图的投影坐标系
        console.log(newCenter)
        // 更新地图的中心
        map.getView().setCenter(newCenter);
      }).catch(error => {
        console.log('Error:', error);
      });
      // 获取地图的所有图层
        var layers = map.getLayers();
        // 获取图层集合中的图层数量
        var numberOfLayers = layers.getLength();

    }


// 开始图像处理流程
const startProcess = async function (processList, valueList, imageUrl) {
    // 存放数据
     const data = {
        processList: processList,
        paramenters: valueList,
        rawUrl: imageUrl
    };
    try {
        const response = await fetch("/preprocessing", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        console.log("Received data:", result);
        // 在这里处理返回的图片地址，例如将其设置为某个元素的src属性
        resultimage = document.getElementById("resultImage")
        resultimage.src = result.resultUrl;
        return result.resultUrl

    }catch (error) {
        console.error("Error calling submitData:", error);
        return "error"
    }

};
// 开始图像处理
function replaceFileExtension(url, newExtension) {
    // 使用正则表达式找到文件扩展名并替换它
    const newUrl = url.replace(/\.[^\.]+$/, `.${newExtension}`);
    return newUrl;
}

button_start_imageProcess = document.getElementById("startImageProcess")
button_start_imageProcess.addEventListener("click", function () {
    procedure = document.getElementById("procedure")
    rawPng = document.getElementById("rawImage")
    rawUrlPng = rawPng.src
    rawUrlTif = replaceFileExtension(rawUrlPng, "tif")
    console.log(rawUrlTif)
    const myPromise = new Promise((resolve, reject) => {
    // 异步操作
        console.log("开始处理图像");
        startProcess(listProcess, processValue, rawUrlTif)
    });
    myPromise.then(result => {
            console.log(result); // 输出result
        }).catch(error => {
            console.log(error);
        });
})

// 将预处理完成后的图像显示到地图上
display_button = document.getElementById("display_preProcess_image");
display_button.addEventListener("click", function(){
    const resultImage = document.getElementById("resultImage");
    const imageUrl = resultImage.src;
    console.log('图像地址：', imageUrl);
    // 添加新图层
    const imageLayer_P = new ol.layer.Image({
        source: new ol.source.ImageStatic({
            url: imageUrl,
            projection: 'EPSG:3857',
            imageExtent: imageLocation
        })
    });
    map.addLayer(imageLayer_P);

});

// 智能处理部分
// fetch 异步提交表单数据
async function textProcess(string, url) {
  // 构建请求选项
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ string: string, url: url }) // 将字符串和图像地址转换为JSON格式的字符串
  };

  try {
    // 使用fetch发送请求
    const response = await fetch('/semantic_analysis', options);
    // 确保响应状态码是OK的
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    // 解析JSON响应
    const result = await response.json();
    // 打印处理后的字符串
    console.log(result.resultUrl);
    // 返回处理后的字符串
    return {"resultUrl":result.resultUrl,"process":result.process,"parameters":result.parameters};
  } catch (error) {
    // 处理错误
    console.error('Error sending string to backend:', error);
    throw error;
  }
}

// 请对该图像进行一次卷积核大小为5的高通滤波，然后进行一次线性拉伸,然后再进行一次卷积核为3的低通滤波
// 监听按钮的点击事件
document.addEventListener('DOMContentLoaded', (event) => {
  // 确保DOM完全加载后再获取元素和添加事件监听器
  const loadButton = document.getElementById('textSubmit');
  loadButton.addEventListener('click', function() {
  let textarea = document.getElementById("floatingTextarea2");
  let text = textarea.value;
  console.log('Text content:', text);
  let url = document.getElementById("rawImage2").src;
  let tifUrl = replaceFileExtension(url, 'tif')
  // 加载图案显示
  //const spinner = document.getElementById('spinner1');
  // 调用函数并传递一个字符串
  textProcess(text, tifUrl).then(result => {
      let resultUrl = result.resultUrl
      let operations = result.process
      let params = result.parameters
      console.log('Process:', operations)
      console.log('Parameters:', params)
      console.log('Processed string:', resultUrl);
      uploadImage(resultUrl, 'resultImage2');
      //spinner.style.display = 'none'; // 加载完成后隐藏图案
      let tableBody  = document.getElementById("myTable")
      operations.forEach((operation, index) => {
            const row = document.createElement("tr");
            const cellOperation = document.createElement("td");
            const cellParam = document.createElement("td");

            cellOperation.textContent = operation;
            cellParam.textContent = params[index];

            row.appendChild(cellOperation);
            row.appendChild(cellParam);
            tableBody.appendChild(row);
        });


      }).catch(error => {
        console.error('Error sending string to backend:', error);
        //spinner.style.display = 'none'; // 加载完成后隐藏图案
      });
    });
});

// 清空ProcessStream处理流程框的内容
let clearButton = document.getElementById("clear_image")
clearButton.addEventListener("click", function() {
    // 获取包含badge的容器元素
    var container = document.getElementById('processStream');

    // 查找容器中所有的badge元素
    var badges = [...container.querySelectorAll('.badge.rounded-pill.bg-secondary')];
    console.log(badges)

    // 遍历badge元素数组，并从容器中移除它们
    badges.forEach(function(badge) {
        badge.parentNode.removeChild(badge);
    });
})


// 下载图像的请求
 // 获取按钮元素并添加点击事件监听器
document.getElementById('save_preProcess_image').addEventListener('click', function() {
    let image_url = document.getElementById("resultImage").src
    let new_url = replaceFileExtension(image_url, "tif")
    let request_url = "/download_image/"+new_url
    // 使用JavaScript的fetch API发送GET请求到Flask后端
    fetch(request_url)
        .then(response => {
            // 如果响应的状态码是200，则将响应的数据转换为Blob
            if (response.status === 200) {
                return response.blob();
            } else {
                throw new Error('网络请求错误');
            }
        })
        .then(blob => {
            // 创建一个临时的URL指向Blob对象
            const url = window.URL.createObjectURL(blob);
            // 创建一个a标签用于触发下载
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            // 设置下载的文件名
            a.download = 'image.png';
            // 将a标签添加到文档中并触发点击事件
            document.body.appendChild(a);
            a.click();
            // 释放创建的URL对象
            window.URL.revokeObjectURL(url);
            // 从文档中移除a标签
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('发生错误:', error);
        });
});
// // 其他网页传递信息的操作
// document.addEventListener('DOMContentLoaded', (event) => {
//     // 获取div中存放的内容
//     let url = document.getElementById('urlSpan').textContent;
//     let location = document.getElementById('locationSpan').textContent;
//     let bool = document.getElementById("bool").textContent;
//     bool = bool.replace(/\s+/g, '').replace(/\n+/g, '');
//     console.log(bool)
//     if( bool === "a")
//     {
//         // 去除字符串中的换行符、制表符（如果有）和首尾空格
//         let str = location.replace(/\s+/g, '').replace(/\n+/g, '');
//         // 去除数字前面的引号
//         str = str.replace(/"\s*([0-9\.]+)\s*"/g, '$1');
//         // 解析字符串为JSON数组
//         let  arr = JSON.parse(str);
//         // 去除换行和制表符
//         let url_exp = url.replace(/\s+/g, '').replace(/\n+/g, '');
//         // 输出数组
//         console.log('图像地址：', url_exp);
//         console.log('图像位置：', str);
//         // 添加新图层
//         const imageLayer_result = new ol.layer.Image({
//             source: new ol.source.ImageStatic({
//                 url: url_exp,
//                 projection: 'EPSG:3857',
//                 imageExtent: arr
//             }),
//             opacity:0.5
//         });
//         console.log(imageLayer_result)
//         map.addLayer(imageLayer_result);
//         let newCenter= [arr[0], arr[1]]; // 将经纬度转换为地图的投影坐标系
//         map.getView().setCenter(newCenter);
//         console.log(map.getLayers())
//     }
//
// });

var layerSwitcher = new ol.control.LayerSwitcher({
    reverse: true,
    groupSelectStyle: 'group',
    tipLabel: '图层管理器'
});

map.addControl(layerSwitcher)
// 实现显示/隐藏全部图层功能
      function toggleAllLayersVisibility() {
        var layers = map.getLayers().getArray();
        var allLayersVisible = layers.every(function(layer) {
          return layer.getVisible();
        });
        layers.forEach(function(layer) {
          layer.setVisible(!allLayersVisible);
        });
      }

      // 添加删除图层的功能
      function removeLayer(layer) {
        map.removeLayer(layer);
      }

      // 添加信息显示按钮的功能
      function showLayerInfo(layer) {
        alert(layer.get('title') + ' - ' + layer.getVisible());
      }

      // 更新图层切换器，以添加删除按钮和信息显示按钮
      layerSwitcher.renderPanel = function() {
        var panel = document.createElement('div');
        panel.className = 'ol-layerswitcher ol-unselectable ol-control';

        var button = document.createElement('button');
        button.innerHTML = '全部显示/隐藏';
        button.addEventListener('click', toggleAllLayersVisibility);
        panel.appendChild(button);

        ol.control.LayerSwitcher.prototype.renderPanel.call(this, panel);

        // 为每个图层添加删除按钮和信息显示按钮
        var layers = this.getMap().getLayers().getArray();
        layers.forEach(function(layer) {
          var div = document.createElement('div');
          var removeButton = document.createElement('button');
          removeButton.innerHTML = '删除';
          removeButton.addEventListener('click', function() {
            removeLayer(layer);
          });
          div.appendChild(removeButton);

          var infoButton = document.createElement('button');
          infoButton.innerHTML = '信息';
          infoButton.addEventListener('click', function() {
            showLayerInfo(layer);
          });
          div.appendChild(infoButton);

          panel.appendChild(div);
        });

        return panel;
      };

      layerSwitcher.panel = layerSwitcher.renderPanel();

      // 更新地图
      map.render();
