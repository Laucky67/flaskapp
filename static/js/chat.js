// 当文档加载完毕时绑定发送按钮的点击事件
// 基本的fetch GET请求
var host_ip
fetch('/get_ip')
  .then(response => {
    // 检查HTTP状态码是否在200-299之间（成功范围）
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    // 如果是JSON格式的数据，则返回一个Promise，解析为JSON对象
    return response.json();
  })
  .then(data => {
    console.log(data);
    host_ip = data.ip;
    // 在这里处理从服务器获取到的数据
    // data 是一个JavaScript对象或数组，取决于服务器响应的内容
  })
  .catch(error => {
    console.error('There was an error!', error);
    // 在这里处理任何网络错误、超时错误或其他抛出的异常
  });

image_user_url = host_ip+"/static/用户.png"
image_chat_url = host_ip+"/static/地球.png"
document.addEventListener('DOMContentLoaded', function() {
  const sendButton = document.getElementById('sendButton');
  sendButton.addEventListener('click', function() {
    const textInput = document.getElementById('textInput');
    const text = textInput.value;
    if (text.trim() !== '') {
      // 构建请求体
      const requestBody = JSON.stringify( {'input':text} );
      // 发送POST请求
      fetch('/chatbot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: requestBody
      }).then(response => {
        if (!response.ok) {
          throw new Error('Error sending message');
        }
        return response.json(); // 解析JSON响应
      }).then(data => {
        // 将用户消息添加到聊天历史
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.innerHTML += `
          <li class="d-flex flex-row mb-4">
            <img src = "/static/用户.png" alt="avatar" class="rounded-circle d-flex align-self-start me-3 shadow-1-strong" width="60">
            <div class="card w-100">
              <div class="card-header d-flex justify-content-between p-3">
                <p class="fw-bold mb-0">用户</p>
                <p class="text-muted small mb-0"><i class="far fa-clock"></i> Just Now</p>
              </div>
              <div class="card-body">
                <p class="mb-0">${text}</p>
              </div>
            </div>
          </li>
        `;
        // 将API的回复添加到聊天历史
        chatHistory.innerHTML += `
          <li class="d-flex justify-content-between mb-4">
            <div class="card w-100">
              <div class="card-header d-flex justify-content-between p-3">
                <p class="text-muted small mb-0"><i class="far fa-clock"></i> Just Now</p>
                <p class="fw-bold mb-0">智能地理助手</p>
              </div>
              <div class="card-body">
                <p class="mb-0">${data.response}</p>
              </div>
            </div>
            <img src="/static/地球.png" alt="avatar" class="rounded-circle d-flex align-self-start ms-3 shadow-1-strong" width="60">
          </li>
        `;
        // 清空输入框
        textInput.value = '';
      }).catch(error => {
        alert('发送消息失败，请重试。');
      });
    }
  });
});