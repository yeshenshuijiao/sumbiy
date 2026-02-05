# submit.py
import requests
import random
import sys

# ===== 配置 =====
UUID = "srRJU1ZQ"  # 替换为你的 UUID
BASE_URL = "http://zs.csg.sc.cn:92"
SURVEY_URL = f"{BASE_URL}/survey?uuid={UUID}"
APPLY_URL = f"{BASE_URL}/apply"

# ===== 伪造数据生成器 =====
def generate_fake_name():
    surnames = ["张", "李", "王", "刘", "陈"]
    names = ["伟", "芳", "强", "敏", "磊"]
    return random.choice(surnames) + random.choice(names)

def generate_fake_phone():
    prefixes = ["138", "139", "150", "187", "188"]
    return random.choice(prefixes) + "".join(str(random.randint(0, 9)) for _ in range(8))

def generate_fake_id_card():
    year = random.randint(1980, 2005)
    month = f"{random.randint(1, 12):02d}"
    day = f"{random.randint(1, 28):02d}"
    seq = f"{random.randint(100, 999)}"
    check = random.choice(list("0123456789X"))
    return f"440902{year}{month}{day}{seq}{check}"

# ===== 主逻辑 =====
def main():
    print("🔄 初始化会话...")
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; Render-Cron)"
    })

    # Step 1: 访问 survey 页面（获取 Cookie）
    try:
        session.get(SURVEY_URL, timeout=10)
        print("✅ 会话初始化成功")
    except Exception as e:
        print(f"⚠️ Survey 页面访问失败: {e}")

    # Step 2: 构造数据并提交
    data = {
        "uuid": UUID,
        "name": generate_fake_name(),
        "phone": generate_fake_phone(),
        "idCard": generate_fake_id_card(),
        "workYears": random.randint(0, 30)
    }

    try:
        resp = session.post(
            APPLY_URL,
            data=data,
            headers={
                "Referer": SURVEY_URL,
                "Origin": BASE_URL
            },
            timeout=15
        )
        print(f"✅ 提交完成 | 状态码: {resp.status_code}")
        print(f"响应预览: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ 提交失败: {e}")
        sys.exit(1)  # Cron Job 遇到非 0 退出码会标记为失败

if __name__ == "__main__":
    main()
