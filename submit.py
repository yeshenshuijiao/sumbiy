# submit.py
import requests
import random
import sys
import json

# ===== 配置 =====
UUID = "srRJU1ZQ"  # 你可以后续改成从环境变量读取
BASE_URL = "http://zs.csg.sc.cn:92"
SURVEY_URL = f"{BASE_URL}/survey?uuid={UUID}"
APPLY_URL = f"{BASE_URL}/apply"

# ===== 伪造数据生成器 =====
def generate_fake_name():
    surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄"]
    names = ["伟", "芳", "强", "敏", "磊", "娜", "洋", "静", "杰", "涛"]
    return random.choice(surnames) + random.choice(names)

def generate_fake_phone():
    prefixes = ["138", "139", "150", "187", "188"]
    suffix = "".join(str(random.randint(0, 9)) for _ in range(8))
    return random.choice(prefixes) + suffix

def generate_fake_id_card():
    year = random.randint(1980, 2005)
    month = f"{random.randint(1, 12):02d}"
    day = f"{random.randint(1, 28):02d}"
    seq = f"{random.randint(100, 999)}"
    check = random.choice(list("0123456789X"))
    return f"440902{year}{month}{day}{seq}{check}"

# ===== 主逻辑 =====
def main():
    print("=" * 50)
    print("🚀 开始执行自动提交任务...")
    
    # 生成提交数据
    data = {
        "uuid": UUID,
        "name": generate_fake_name(),
        "phone": generate_fake_phone(),
        "idCard": generate_fake_id_card(),
        "workYears": random.randint(0, 30)
    }

    # 打印即将提交的数据（脱敏：隐藏身份证中间8位、手机号中间4位）
    safe_id = data["idCard"][:6] + "********" + data["idCard"][-4:]
    safe_phone = data["phone"][:3] + "****" + data["phone"][-4:]
    
    print("📤 即将提交的数据（脱敏显示）:")
    print(f"   UUID       : {data['uuid']}")
    print(f"   姓名       : {data['name']}")
    print(f"   手机号     : {safe_phone}")
    print(f"   身份证     : {safe_id}")
    print(f"   工作年限   : {data['workYears']} 年")
    print("-" * 50)

    # 创建会话
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; Render-Cron)"
    })

    try:
        # Step 1: 访问 survey 页面（获取 Cookie）
        print("🔄 正在访问 survey 页面以初始化会话...")
        session.get(SURVEY_URL, timeout=10)
        print("✅ 会话初始化成功")

        # Step 2: 提交表单
        print("📤 正在提交数据到 /apply ...")
        resp = session.post(
            APPLY_URL,
            data=data,
            headers={
                "Referer": SURVEY_URL,
                "Origin": BASE_URL
            },
            timeout=15
        )

        print(f"✅ 提交完成 | HTTP 状态码: {resp.status_code}")
        
        # 尝试解析 JSON 响应，否则截断文本
        try:
            resp_json = resp.json()
            print("📄 服务器响应 (JSON):")
            print(json.dumps(resp_json, ensure_ascii=False, indent=2))
        except:
            preview = resp.text[:300].replace('\n', ' ').strip()
            print(f"📄 服务器响应 (文本预览): {preview}")

    except Exception as e:
        print(f"❌ 提交过程中发生错误: {e}")
        sys.exit(1)  # 让 Render 标记为失败

    print("=" * 50)
    print("✅ 本次任务执行完毕。")

if __name__ == "__main__":
    main()
