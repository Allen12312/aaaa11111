#!/usr/bin/env python3
"""
AI Agent预测市场平台 - 启动脚本
"""
import os
import sys
import subprocess
import time

def start_backend():
    print("🚀 启动后端服务...")
    backend_dir = "/mnt/okcomputer/output/agent-backend"
    env = os.environ.copy()
    env["PYTHONPATH"] = backend_dir
    env["DEEPSEEK_API_KEY"] = "sk-"
    
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(3)
    return process

def start_frontend():
    print("🌐 启动前端服务...")
    frontend_dir = "/mnt/okcomputer/output/app/dist"
    
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(2)
    return process

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🤖 AI Agent 预测市场平台                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    backend = start_backend()
    frontend = start_frontend()
    
    print("✅ 系统启动成功！")
    print("📡 后端: http://localhost:8000")
    print("🌐 前端: http://localhost:3000")
    print("\n按 Ctrl+C 停止")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 停止系统...")
        backend.terminate()
        frontend.terminate()
