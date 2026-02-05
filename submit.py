# submit_10_threads.py
import requests
import random
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== 配置 =====
UUID = os.getenv("SUBMIT_UUID", "srRJU1ZQ")
BASE_URL = "http://zs.csg.sc.cn:92"
SURVEY_URL = f"{BASE_URL}/survey?uuid={UUID}"
APPLY_URL = f"{BASE_URL}/apply"

# 提交总次数（建议 ≤10）
TOTAL_TASKS = min(int(os.getenv("TOTAL_SUBMITS", "10")), 20)  # 最多 20 次防误配
MAX_WORKERS = 5  # Render 安全并发数（即使你想要 10 线程，并发执行仍限 5）

success_count = 0

# ===== 数据生成函数 =====
def generate_fake_name():
    surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
    given_single = ["伟", "芳", "强", "敏", "磊", "娜", "静", "杰", "涛", "明"]
    given_double = ["子轩", "梓涵", "浩然", "思琪", "俊杰", "欣怡", "宇航", "梦瑶"]
    surname = random.choice(surnames)
    given = random.choice(given_double) if random.random() < 0.6 else random.choice(given_single)
    return surname + given

def generate_fake_phone():
    prefixes = ["138", "139", "150", "187", "188"]
    return random.choice(prefixes) + "".join(str(random.randint(0, 9)) for _ in range(8))

def generate_fake_id_card():
    year = random.randint(1985, 2000)
    month = f"{random.randint(1, 12):02d}"
    day = f"{random.randint(1, 28):02d}"
    seq = f"{random.randint(100, 999)}"
    check = random.choice("0123456789X")
    return f"440902{year}{month}{day}{seq}{check}"

# ===== 单次提交任务 =====
def submit_task(task_id):
    global success_count
    try:
        # 创建独立会话
        with requests.Session() as session:
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # Step 1: 访问 survey 获取 Cookie
            session.get(SURVEY_URL, timeout=8)
            
            # Step 2: 生成伪造数据
            data = {
                "uuid": UUID,
                "name": generate_fake_name(),
                "phone": generate_fake_phone(),
                "idCard": generate_fake_id_card(),
                "workYears": random.randint(1, 30)
            }
            
            # Step 3: 提交 apply
            resp = session.post(
                APPLY_URL,
                data=data,
                headers={
                    "Referer": SURVEY_URL,
                    "Origin": BASE_URL
                },
                timeout=12
            )
            
            # 解析响应
            try:
                result = resp.json()
                message = result.get("message", "")
                success = result.get("success", False)
            except:
                message = resp.text[:150].replace('\n', ' ')
                success = resp.status_code == 200
            
            # 打印结果
            status = "✅" if success else "❌"
            print(f"[{task_id:2d}] {status} {data['name']} | {message}")
            
            return success
            
    except Exception as e:
        print(f"[{task_id:2d}] ❌ 异常: {str(e)[:80]}")
        return False

# ===== 主函数 =====
def main():
    print("=" * 60)
    print(f"🚀 启动批量提交任务")
    print(f"   总任务数: {TOTAL_TASKS}")
    print(f"   并发线程: {MAX_WORKERS}（安全限制）")
    print(f"   目标 UUID: {UUID}")
    print("-" * 60)
    
    start_time = time.time()
    results = []
    
    # 使用线程池执行（最多 5 个并发）
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        futures = [executor.submit(submit_task, i + 1) for i in range(TOTAL_TASKS)]
        
        # 收集结果
        for future in as_completed(futures):
            results.append(future.result())
    
    duration = time.time() - start_time
    total_success = sum(results)
    
    print("-" * 60)
    print(f"✅ 任务完成! 成功: {total_success}/{TOTAL_TASKS} | 耗时: {duration:.1f} 秒")
    
    if total_success > 1:
        print("⚠️  警告：重复提交可能导致审核失败，请谨慎使用！")
    print("=" * 60)

if __name__ == "__main__":
    main()
