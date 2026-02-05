# submit.py
import requests
import random
import sys
import json
import os

# ===== 配置 =====
UUID = os.getenv("SUBMIT_UUID", "srRJU1ZQ")  # 建议在 Render 后台设置 SUBMIT_UUID
BASE_URL = "http://zs.csg.sc.cn:92"
SURVEY_URL = f"{BASE_URL}/survey?uuid={UUID}"
APPLY_URL = f"{BASE_URL}/apply"

# ===== 生成多样化中文姓名（含三字、复姓）=====
def generate_fake_name():
    single_surnames = [
        "张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴",
        "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
        "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧",
        "程", "曹", "袁", "邓", "许", "傅", "沈", "曾", "彭", "吕"
    ]
    compound_surnames = [
        "欧阳", "司马", "上官", "诸葛", "夏侯", "皇甫", "尉迟", "公孙",
        "慕容", "令狐", "端木", "东方", "南宫", "西门", "百里", "申屠",
        "赫连", "宇文", "长孙", "澹台"
    ]
    given_names_single = [
        "伟", "芳", "强", "敏", "磊", "娜", "洋", "静", "杰", "涛",
        "明", "丽", "勇", "艳", "军", "鹏", "霞", "刚", "颖", "波"
    ]
    given_names_double = [
        "子轩", "梓涵", "浩然", "思琪", "俊杰", "欣怡", "宇航", "梦瑶",
        "文博", "雅婷", "天佑", "诗涵", "嘉豪", "雨桐", "一鸣", "可馨",
        "志强", "慧敏", "建国", "秀英", "海燕", "国强", "小红", "大伟",
        "星辰", "若曦", "景辰", "依诺", "书桓", "安然", "睿哲", "瑾萱"
    ]
    
    surname = random.choice(single_surnames) if random.random() < 0.9 else random.choice(compound_surnames)
    given = random.choice(given_names_double) if random.random() < 0.6 else random.choice(given_names_single)
    return surname + given

# ===== 生成手机号 =====
def generate_fake_phone():
    prefixes = ["138", "139", "150", "187", "188", "176", "199"]
    suffix = "".join(str(random.randint(0, 9)) for _ in range(8))
    return random.choice(prefixes) + suffix

# ===== 生成伪造身份证号 =====
def generate_fake_id_card():
    year = random.randint(1980, 2005)
    month = f"{random.randint(1, 12):02d}"
    day = f"{random.randint(1, 28):02d}"
    seq = f"{random.randint(100, 999)}"
    check = random.choice(list("0123456789X"))
    return f"440902{year}{month}{day}{seq}{check}"

# ===== 主逻辑 =====
def main():
    print("=" * 60)
    print("🚀 开始执行自动提交任务...")

    # 生成完整伪造数据
    data = {
        "uuid": UUID,
        "name": generate_fake_name(),
        "phone": generate_fake_phone(),
        "idCard": generate_fake_id_card(),
        "workYears": random.randint(0, 30)
    }

    # 直接打印原始数据（无脱敏）
    print("📤 提交的原始数据:")
    print(f"   UUID       : {data['uuid']}")
    print(f"   姓名       : {data['name']}")
    print(f"   手机号     : {data['phone']}")
    print(f"   身份证号   : {data['idCard']}")
    print(f"   工作年限   : {data['workYears']} 年")
    print("-" * 60)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    try:
        # Step 1: 访问 survey 页面获取会话 Cookie
        print("🔄 正在访问 survey 页面以初始化会话...")
        session.get(SURVEY_URL, timeout=10)
        print("✅ 会话初始化成功")

        # Step 2: 提交表单
        print("📤 正在向 /apply 提交数据...")
        resp = session.post(
            APPLY_URL,
            data=data,
            headers={
                "Referer": SURVEY_URL,
                "Origin": BASE_URL
            },
            timeout=15
        )
        print(f"✅ HTTP 状态码: {resp.status_code}")

        # Step 3: 解析并美化响应（自动显示中文）
        try:
            resp_json = resp.json()
            print("📄 服务器响应（已解码中文）:")
            print(json.dumps(resp_json, ensure_ascii=False, indent=2))
        except ValueError:
            preview = resp.text[:300].replace('\n', ' ').strip()
            print(f"📄 原始响应预览: {preview}")

    except Exception as e:
        print(f"❌ 提交失败: {e}")
        sys.exit(1)  # 非零退出 → Render 标记为失败

    print("=" * 60)
    print("✅ 本次任务执行完毕。")

if __name__ == "__main__":
    main()
