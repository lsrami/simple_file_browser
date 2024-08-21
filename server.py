from flask import Flask, send_from_directory, render_template_string, request
import os

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# 定义文件根目录
ROOT_DIRECTORY = "./"

# 定义要显示的文件夹列表
VISIBLE_FOLDERS = ["", "exp_sherpa_onnx_stream", "exp_sherpa_onnx", "其他目录"]  # 修改为你想显示的文件夹名称

# HTML 模板
HTML_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <title>文件浏览器</title>
  </head>
  <body>
    <div class="container mt-4">
      <h1>文件浏览器</h1>
      <p>当前路径: {{ current_path }}</p>
      <div class="mb-3">
        <a href="{{ url_for('dir_listing', req_path='') }}" class="btn btn-primary">返回根目录</a>
        <button onclick="window.history.back();" class="btn btn-secondary">后退</button>
      </div>
      <ul class="list-group">
        {% for name, path in directories %}
        <li class="list-group-item">
          <a href="{{ url_for('dir_listing', req_path=path) }}">{{ name }}/</a>
        </li>
        {% endfor %}
        {% for name, path in files %}
        <li class="list-group-item">
          <a href="{{ url_for('dir_listing', req_path=path) }}">{{ name }}</a>
        </li>
        {% endfor %}
      </ul>
    </div>
    <footer class="footer mt-4">
      <div class="container">
        <p class="text-muted text-center">Copyright © 2024 timekettle all rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""

def is_path_allowed(req_path):
    # 检查路径是否在允许的文件夹列表中
    for folder in VISIBLE_FOLDERS:
        if req_path == folder or req_path.startswith(f"{folder}/"):
            return True
    return False

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def dir_listing(req_path):
    # 修正路径拼接逻辑，确保路径正确
    abs_path = os.path.join(ROOT_DIRECTORY, req_path)

    # 输出调试信息
    print(f"req {req_path}")
    print(f"abs {abs_path}")

    # 检查路径是否被允许访问
    if not is_path_allowed(req_path):
        return "403 禁止访问", 403

    # 返回 404 如果路径不存在
    if not os.path.exists(abs_path):
        return "404 未找到", 404

    # 检查是否为文件并提供下载
    if os.path.isfile(abs_path):
        return send_from_directory(os.path.dirname(abs_path), os.path.basename(abs_path))

    # 获取目录内容
    files = []
    directories = []
    for item in os.listdir(abs_path):
        item_path = os.path.join(req_path, item)
        full_item_path = os.path.join(ROOT_DIRECTORY, item_path)
        if os.path.isdir(full_item_path):
            if req_path == '' and item not in VISIBLE_FOLDERS:
                continue  # 忽略不在 VISIBLE_FOLDERS 列表中的文件夹
                # directories.append(('禁止访问 ' + item, item_path))
            else:
                directories.append((item, item_path))
        else:
            files.append((item, item_path))

    return render_template_string(HTML_TEMPLATE, files=files, directories=directories, current_path=req_path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
