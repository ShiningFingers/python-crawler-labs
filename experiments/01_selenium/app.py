from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 模拟数据库中的日志数据（生成 25 条数据，用于测试翻页）
MOCK_DATA = []
for i in range(1, 26):
    MOCK_DATA.append({
        "id": i,
        "create_time": f"2026-10-20 15:00:{i:02d}",
        "channel": "梦网",
        "sign_name": "闲云旅游",
        "template_name": "集信达验证码",
        "app_name": "TMS",
        "cost": f"{i % 10 + 10}",
        "status": "成功" if i % 4 != 0 else "失败"
    })

@app.route('/')
def index():
    return render_template('index.html')

# 模拟 AJAX 接口，接收前端传来的筛选条件和分页参数
@app.route('/api/logs', methods=['GET'])
def get_logs():
    sign_name = request.args.get('sign_name', '')
    app_name = request.args.get('app_name', '')
    page = int(request.args.get('page', 1))
    page_size = 15 # 每页15条，和PPT中描述的一致

    # 1. 过滤数据
    filtered_data = []
    for row in MOCK_DATA:
        if sign_name and sign_name not in row['sign_name']: continue
        if app_name and app_name not in row['app_name']: continue
        filtered_data.append(row)

    # 2. 计算分页
    total = len(filtered_data)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = filtered_data[start:end]
    
    # 3. 模拟网络延迟（关键：体现动态网页需要等待）
    import time
    time.sleep(0.5)

    return jsonify({
        "code": 200,
        "msg": "success",
        "total": total,
        "data": page_data
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)