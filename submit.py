# submit_batch.py
import requests
import random
import time
import json
import os
import sys

# ===== 配置 =====
UUID = os.getenv("SUBMIT_UUID", "srRJU1ZQ")  # 建议在 Render 设置环境变量
BASE_URL = "http://zs.csg.sc.cn:92"
SURVEY_URL = f"{BASE_URL}/survey?uuid={UUID}"
APPLY_URL = f"{BASE_URL}/apply"

# 提交次数（建议 1~3，不要过高）
TOTAL_SUBMITS = int(os.getenv("TOTAL_SUBMITS", "3"))

# ===== 生成多样化中文姓名 =====
def generate_fake_name():
    single_surnames = [
        "张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴",
        "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
        "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧"
    ]
    compound_surnames = ["欧阳", "司马", "上官", "诸葛", "夏侯", "皇甫", "慕容", "令狐"]
    given_names_single = ["伟", "芳", "强", "敏", "磊", "娜", "洋", "静", "杰", "涛"]
    given_names_double = [
        "子轩", "梓涵", "浩然", "思琪", "俊杰", "欣怡", "宇航", "梦瑶",
        "文博", "雅婷", "天佑", "诗涵", "嘉豪", "雨桐", "一鸣", "可馨"
    ]
    
    surname = random.choice(single_surnames) if random.random() < 0.9 else random.choice(compound_surnames)
    given = random.choice(given_names_double) if random.random() < 0.6 else random.choice(given_names_single)
    return surname + given

# ===== 生成手机号 =====
def generate_fake_phone():
    prefixes = ["138", "139", "150", "187", "188", "176", "199"]
    return random.choice(prefixes) + "".join(str(random.randint(0, 9)) for _ in range(8))

# ===== 生成身份证号 =====
def generate_fake_id_card():
    year = random.randint(1980, 2005)
    month = f"{random.randint(1, 12):02d}"
    day = f"{random.randint(1, 28):02d}"
    seq = f"{random.randint(100, 999)}"
    check = random.choice(list("0123456789X"))
    return f"440902{year}{month}{day}{seq}{check}"

# ===== 单次提交函数 =====
def submit_once(session, data):
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
        # 尝试解析 JSON
        try:
            resp_json = resp.json()
            message = resp_json.get("message", "无返回消息")
            success = resp_json.get("success", False)
        except:
            message = resp.text[:200]
            success = resp.status_code == 200

        print(f"  ✅ 状态: {resp.status_code} | 响应: {message}")
        return success
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

# ===== 主逻辑 =====
def main():
    print("=" * 60)
    print(f"🚀 开始批量提交任务（共 {TOTAL_SUBMITS} 次）")
    print(f"🎯 目标 UUID: {UUID}")
    print("-" * 60)

    # 初始化会话（只访问一次 survey）
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    try:
        session.get(SURVEY_URL, timeout=10)
        print("✅ 会话初始化成功")
    except Exception as e:
        print(f"⚠️ 会话初始化失败（仍继续提交）: {e}")

    success_count = 0

    for i in range(TOTAL_SUBMITS):
        print(f"\n🔁 第 {i+1}/{TOTAL_SUBMITS} 次提交...")

        # 生成新数据
        data = {
            "uuid": UUID,
            "name": generate_fake_name(),
            "phone": generate_fake_phone(),
            "idCard": generate_fake_id_card(),
            "workYears": random.randint(1, 30)
        }

        # 打印完整数据
        print(f"   📝 姓名: {data['name']}")
        print(f"   📱 手机: {data['phone']}")
        print(f"   🪪 身份证: {data['idCard']}")
        print(f"   💼 工作年限: {data['workYears']} 年")

        # 提交
        if submit_once(session, data):
            success_count += 1

        # 最后一次不等待
        if i < TOTAL_SUBMITS - 1:
            delay = random.randint(10, 20)
            print(f"   ⏳ 等待 {delay} 秒...")
            time.sleep(delay)

    print("\n" + "=" * 60)
    print(f"✅ 批量任务完成！成功: {success_count}/{TOTAL_SUBMITS}")
    if success_count > 1:
        print("⚠️  警告：重复提交可能导致审核失败，请谨慎使用！")
    print("=" * 60)

    # 如果全部失败，退出码为 1（Render 可标记失败）
    if success_count == 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
