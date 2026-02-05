# submit_500_safe.py
import requests
import random
import time
import os
import gc

# ===== 配置 =====
UUID = os.getenv("SUBMIT_UUID", "srRJU1ZQ")
BASE_URL = "http://zs.csg.sc.cn:92"
SURVEY_URL = f"{BASE_URL}/survey?uuid={UUID}"
APPLY_URL = f"{BASE_URL}/apply"

TOTAL_TASKS = min(int(os.getenv("TOTAL_SUBMITS", "500")), 500)  # 最多 500
MAX_WORKERS = 5  # 并发数
BATCH_SIZE = MAX_WORKERS  # 每批 5 个

# 全局计数
success_count = 0
completed_count = 0

# ===== 数据生成 =====
def generate_fake_name():
    surnames = ["张", "李", "王", "刘", "陈"]
    given = ["伟", "芳", "子轩", "浩然", "静", "杰"]
    return random.choice(surnames) + (random.choice(given) if random.random() < 0.7 else random.choice("明丽"))

def generate_fake_phone():
    return random.choice(["138", "139"]) + "".join(str(random.randint(0,9)) for _ in range(8))

def generate_fake_id_card():
    y = random.randint(1990, 2000)
    m = f"{random.randint(1,12):02d}"
    d = f"{random.randint(1,28):02d}"
    return f"440902{y}{m}{d}{random.randint(100,999)}X"

# ===== 单次提交 =====
def submit_once(task_id):
    global success_count, completed_count
    try:
        with requests.Session() as session:
            session.headers.update({"User-Agent": "Mozilla/5.0"})
            session.get(SURVEY_URL, timeout=6)
            
            data = {
                "uuid": UUID,
                "name": generate_fake_name(),
                "phone": generate_fake_phone(),
                "idCard": generate_fake_id_card(),
                "workYears": random.randint(1, 20)
            }
            
            resp = session.post(APPLY_URL, data=data, headers={"Referer": SURVEY_URL}, timeout=8)
            result = resp.json()
            success = result.get("success", False)
            
            with open("/dev/null", "w"):  # 模拟轻量日志
                pass
                
            if success:
                success_count += 1
            completed_count += 1
            
            # 每 10 次打印一次进度（减少 I/O）
            if task_id % 10 == 0 or task_id == TOTAL_TASKS:
                print(f"[{task_id}/{TOTAL_TASKS}] 进度: {completed_count} 完成, {success_count} 成功")
            
            return success
    except Exception:
        completed_count += 1
        return False

# ===== 主函数 =====
def main():
    print(f"🚀 开始 {TOTAL_TASKS} 次提交（5 线程并发）")
    print("⚠️  注意：Render 可能在 100 次左右因资源不足终止！")
    print("-" * 50)
    
    start_time = time.time()
    
    for i in range(0, TOTAL_TASKS, BATCH_SIZE):
        batch_ids = list(range(i + 1, min(i + BATCH_SIZE + 1, TOTAL_TASKS + 1)))
        
        # 顺序执行（避免线程开销，实际更稳定）
        for tid in batch_ids:
            submit_once(tid)
            time.sleep(0.3)  # 微延迟，防瞬时压力
        
        # 批次间延迟
        delay = random.uniform(1.0, 2.5)
        time.sleep(delay)
        
        # 强制垃圾回收
        gc.collect()
        
        # 检查是否接近超时（Render 5 分钟 = 300 秒）
        elapsed = time.time() - start_time
        if elapsed > 240:  # 4 分钟后停止
            print(f"⏳ 已运行 {elapsed:.1f} 秒，接近 Render 超时，提前退出")
            break
    
    total_time = time.time() - start_time
    print("\n" + "="*50)
    print(f"🛑 任务结束 | 成功: {success_count}/{completed_count} | 耗时: {total_time:.1f}s")
    print("💡 提示：若 completed_count << 500，说明 Render 已 kill 进程")

if __name__ == "__main__":
    main()
