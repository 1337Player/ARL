#!/usr/bin/env python3
"""ARL 统一启动入口

用法:
    python3 run.py                启动全部组件
    python3 run.py --web          仅启动 Web 服务
    python3 run.py --worker       仅启动 Celery Workers
    python3 run.py --scheduler    仅启动调度器
    python3 run.py --port 8080    指定 Web 端口 (默认 5003)

环境变量:
    ARL_PORT                      指定 Web 端口
"""

import argparse
import os
import signal
import subprocess
import sys
import time

PROCS: list[subprocess.Popen] = []


def color(name: str) -> str:
    colors = {
        "web": "\033[36m",
        "worker/arltask": "\033[33m",
        "worker/arlgithub": "\033[35m",
        "scheduler": "\033[32m",
        "run.py": "\033[1m",
    }
    c = colors.get(name, "\033[0m")
    return f"{c}[{name}]\033[0m"


def log(name: str, msg: str) -> None:
    print(f"{color(name)} {msg}")


def check_mongo() -> bool:
    try:
        from app.utils.conn import conn_db
        conn_db('task').find_one()
        return True
    except Exception as e:
        log("run.py", f"MongoDB 连接失败: {e}")
        return False


def check_redis() -> bool:
    try:
        import redis
        from app.config import Config
        r = redis.from_url(Config.CELERY_BROKER_URL)
        r.ping()
        r.close()
        return True
    except Exception as e:
        log("run.py", f"Redis 连接失败: {e}")
        return False


def stop_all(signum=None, frame=None):
    if not PROCS:
        return
    log("run.py", f"收到信号 {signum}, 正在停止所有组件...")
    for p in PROCS:
        if p.poll() is None:
            p.send_signal(signal.SIGTERM)
    time.sleep(2)
    for p in PROCS:
        if p.poll() is None:
            p.kill()
    sys.exit(0)


def start_web(port: int) -> subprocess.Popen:
    log("web", f"启动 Flask @ http://0.0.0.0:{port}")
    code = (
        f"from app.main import arl_app; "
        f"arl_app.run(host='0.0.0.0', port={port}, debug=False, threaded=True)"
    )
    return subprocess.Popen(
        [sys.executable, "-c", code],
        stdout=sys.stdout, stderr=sys.stderr,
    )


def start_worker(queue: str, name: str) -> subprocess.Popen:
    log(f"worker/{name}", f"启动 Celery worker, 队列={queue}")
    return subprocess.Popen(
        [sys.executable, "-m", "celery", "-A", "app.celerytask.celery",
         "worker", "-Q", queue, "-n", name, "-c", "2", "--loglevel=info"],
        stdout=sys.stdout, stderr=sys.stderr,
    )


def start_scheduler() -> subprocess.Popen:
    log("scheduler", "启动调度器")
    return subprocess.Popen(
        [sys.executable, "-m", "app.scheduler"],
        stdout=sys.stdout, stderr=sys.stderr,
    )


def main():
    parser = argparse.ArgumentParser(description="ARL 统一启动入口")
    parser.add_argument("--web", action="store_true", help="仅启动 Web 服务")
    parser.add_argument("--worker", action="store_true", help="仅启动 Celery Workers")
    parser.add_argument("--scheduler", action="store_true", help="仅启动调度器")
    parser.add_argument("--port", type=int, default=None, help="Web 端口 (默认: 5003)")
    args = parser.parse_args()

    port = args.port or int(os.environ.get("ARL_PORT", 5003))

    components = {"web": args.web, "worker": args.worker, "scheduler": args.scheduler}
    start_all = not any(components.values())

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    signal.signal(signal.SIGINT, stop_all)
    signal.signal(signal.SIGTERM, stop_all)

    log("run.py", "检查 MongoDB 连接...")
    if not check_mongo():
        sys.exit(1)
    log("run.py", "MongoDB 连接 OK")

    log("run.py", "检查 Redis 连接...")
    if not check_redis():
        sys.exit(1)
    log("run.py", "Redis 连接 OK")

    if start_all or components["web"]:
        PROCS.append(start_web(port))

    if start_all or components["worker"]:
        PROCS.append(start_worker("arltask", "arltask"))
        PROCS.append(start_worker("arlgithub", "arlgithub"))

    if start_all or components["scheduler"]:
        PROCS.append(start_scheduler())

    log("run.py", f"全部组件运行中 ({len(PROCS)} 个进程), Ctrl+C 停止")

    try:
        for p in PROCS:
            p.wait()
    except KeyboardInterrupt:
        pass
    finally:
        stop_all()


if __name__ == "__main__":
    main()
