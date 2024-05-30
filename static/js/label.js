let isSendingCoordinates = true; // 初始状态允许发送坐标

$(document).ready(function() {
    // 获取图像元素
    let imgElement = document.getElementById('clickable-image');

    // 添加点击事件监听器
    imgElement.addEventListener('click', function(event) {
        if (isSendingCoordinates) {
            // 计算相对于图像的坐标
            var rect = imgElement.getBoundingClientRect();
            var x = event.clientX - rect.left;
            var y = event.clientY - rect.top;

            // 发送坐标到后端
            $.ajax({
                type: 'POST',
                url: '/get_pixel_coordinates',
                data: JSON.stringify({ point_x: x, point_y: y }),
                contentType: 'application/json',
                success: function(response) {
                    console.log("Coordinates sent successfully.");
                },
                error: function(xhr, status, error) {
                    console.error("Error sending coordinates:", error);
                }
            });
        }
    }, false);

    // 添加停止发送坐标按钮的点击事件监听器
    $('#coordinates-button').on('click', function() {
        isSendingCoordinates = false;
        stopSendingCoordinates();
    });

    // 添加发送整数按钮的点击事件监听器
    $('#send-int').on('click', function() {
        var value = $(this).data('value');
        sendIntValue(value);
    });

    // 添加自动按钮的点击事件监听器
    $('#auto-button').on('click', function() {
        sendAutoSignal();
    });

    function stopSendingCoordinates() {
        let image = document.getElementById("clickable-image")
        let image_url = image.src
        $.ajax({
            type: 'POST',
            url: '/finish_sending_points',
            data: JSON.stringify({ image_url: image_url }), // 发送图像URL到后端
            contentType: 'application/json', // 指定内容类型为JSON
            success: function(response) {
                console.log("Finish signal sent successfully.");
                // 可选地，隐藏或禁用按钮，防止重复发送
                $('#coordinates-button').hide();
                // 假设response中包含了新的图像URL
                console.log(response.path)
                image.src = response.path; // 更新图像元素的src属性为新URL
                // 显示按钮
                setTimeout(function() {
                    $('#coordinates-button').show();
                    isSendingCoordinates = true; // 设置为true，以便再次发送坐标
                }, 5000); // 5秒后显示按钮
            },
            error: function(xhr, status, error) {
                console.error("Error sending finish signal:", error);
            }
        });
    }

    function sendIntValue(value) {
        $.ajax({
            type: 'POST',
            url: '/send_int_value',
            data: JSON.stringify({ value: value }),
            contentType: 'application/json',
            success: function(response) {
                console.log("Integer value sent successfully.");
            },
            error: function(xhr, status, error) {
                console.error("Error sending integer value:", error);
            }
        });
    }

    function sendAutoSignal() {
        let image = document.getElementById("clickable-image")
        let image_url = image.src
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ image_url: image_url }), // 发送图像URL到后端
            url: '/auto_signal',
            success: function(response) {
                console.log("Finish signal sent successfully.");
                // 可选地，隐藏或禁用按钮，防止重复发送
                $('#coordinates-button').hide();
                // 假设response中包含了新的图像URL
                console.log(response.path)
                image.src = response.path; // 更新图像元素的src属性为新URL
                // 显示按钮
                setTimeout(function() {
                    $('#coordinates-button').show();
                    isSendingCoordinates = true; // 设置为true，以便再次发送坐标
                }, 5000); // 5秒后显示按钮
            },
            error: function(xhr, status, error) {
                console.error("Error sending finish signal:", error);
                // 可以考虑在这里添加用户反馈
            }
        });
    }
});

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
    uploadFile("clickable-image","imageInputRgb")
})