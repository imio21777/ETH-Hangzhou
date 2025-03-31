from base_agent import BaseAgent
import time
import threading

class AlarmAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AlarmAgent")
        self.info_process_agent = None
        self.data_clean_agent = None
        self.monitoring_tasks = {}  # 监控任务列表
        self.monitoring_running = False
        self.monitoring_thread = None
        self.monitoring_interval = 300  # 默认5分钟检查一次
    
    def set_agents(self, info_process_agent, data_clean_agent):
        """设置关联的其他代理"""
        self.info_process_agent = info_process_agent
        self.data_clean_agent = data_clean_agent
    
    def set_monitoring_interval(self, seconds):
        """设置监控间隔"""
        if isinstance(seconds, int) and seconds > 0:
            self.monitoring_interval = seconds
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "set_alarm":
            return self.set_alarm(message["content"])
        elif message["type"] == "remove_alarm":
            return self.remove_alarm(message["content"])
        elif message["type"] == "list_alarms":
            return self.list_alarms()
        elif message["type"] == "start_monitoring":
            return self.start_monitoring()
        elif message["type"] == "stop_monitoring":
            return self.stop_monitoring()
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data:
            if data["type"] == "set_alarm":
                return self.set_alarm(data.get("params", {}))
            elif data["type"] == "remove_alarm":
                return self.remove_alarm(data.get("params", {}))
            elif data["type"] == "list_alarms":
                return self.list_alarms()
            elif data["type"] == "start_monitoring":
                return self.start_monitoring()
            elif data["type"] == "stop_monitoring":
                return self.stop_monitoring()
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def set_alarm(self, params):
        """设置警报"""
        if "id" not in params or "condition" not in params:
            return {"status": "error", "message": "缺少必要的参数(id或condition)"}
        
        alarm_id = params["id"]
        condition = params["condition"]
        description = params.get("description", "")
        
        # 检查SQL条件语法
        if not self._is_valid_sql_condition(condition):
            return {"status": "error", "message": "无效的SQL条件"}
        
        # 添加到监控任务
        self.monitoring_tasks[alarm_id] = {
            "condition": condition,
            "description": description,
            "created_at": time.time(),
            "last_triggered": None,
            "trigger_count": 0
        }
        
        # 如果监控未运行，自动启动
        if not self.monitoring_running:
            self.start_monitoring()
        
        return {
            "status": "success",
            "message": f"已设置警报 {alarm_id}"
        }
    
    def remove_alarm(self, params):
        """移除警报"""
        if "id" not in params:
            return {"status": "error", "message": "缺少警报ID"}
        
        alarm_id = params["id"]
        
        if alarm_id in self.monitoring_tasks:
            del self.monitoring_tasks[alarm_id]
            return {
                "status": "success",
                "message": f"已移除警报 {alarm_id}"
            }
        
        return {
            "status": "error",
            "message": f"未找到警报 {alarm_id}"
        }
    
    def list_alarms(self):
        """列出所有警报"""
        alarms = []
        for alarm_id, alarm_data in self.monitoring_tasks.items():
            alarms.append({
                "id": alarm_id,
                "description": alarm_data["description"],
                "condition": alarm_data["condition"],
                "created_at": alarm_data["created_at"],
                "last_triggered": alarm_data["last_triggered"],
                "trigger_count": alarm_data["trigger_count"]
            })
        
        return {
            "status": "success",
            "alarms": alarms
        }
    
    def start_monitoring(self):
        """启动监控线程"""
        if self.monitoring_running:
            return {"status": "warning", "message": "监控已经在运行"}
        
        self.monitoring_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        return {"status": "success", "message": "监控已启动"}
    
    def stop_monitoring(self):
        """停止监控线程"""
        if not self.monitoring_running:
            return {"status": "warning", "message": "监控未在运行"}
        
        self.monitoring_running = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
        
        return {"status": "success", "message": "监控已停止"}
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_running:
            # 首先更新市场信息
            if self.info_process_agent:
                update_message = self.create_mcp_message("request_info_update", {})
                self.send_message(self.info_process_agent, update_message)
            
            # 检查所有警报
            for alarm_id, alarm_data in list(self.monitoring_tasks.items()):
                try:
                    self._check_alarm(alarm_id, alarm_data)
                except Exception as e:
                    print(f"检查警报 {alarm_id} 时出错: {str(e)}")
            
            # 等待下一个检查周期
            time.sleep(self.monitoring_interval)
    
    def _check_alarm(self, alarm_id, alarm_data):
        """检查单个警报"""
        if not self.data_clean_agent:
            return
        
        # 构建SQL查询
        condition = alarm_data["condition"]
        sql_query = f"SELECT COUNT(*) as count FROM ({condition}) as subquery"
        
        # 执行查询
        message = self.create_mcp_message("sql_query", {"query": sql_query})
        result = self.send_message(self.data_clean_agent, message)
        
        # 检查是否触发警报
        if result.get("status") == "success" and "result" in result:
            result_data = result["result"]
            if result_data and isinstance(result_data, list) and len(result_data) > 0:
                count = result_data[0].get("count", 0)
                
                if count > 0:
                    # 触发警报
                    self._trigger_alarm(alarm_id, alarm_data, count)
    
    def _trigger_alarm(self, alarm_id, alarm_data, count):
        """触发警报"""
        # 更新警报状态
        now = time.time()
        alarm_data["last_triggered"] = now
        alarm_data["trigger_count"] += 1
        
        # 打印警报信息
        print(f"\n===== 警报触发 =====")
        print(f"警报ID: {alarm_id}")
        print(f"描述: {alarm_data['description']}")
        print(f"条件: {alarm_data['condition']}")
        print(f"匹配记录数: {count}")
        print(f"触发时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))}")
        print(f"触发次数: {alarm_data['trigger_count']}")
        print("=====================\n")
        
        # 这里还可以添加其他通知方式，如发送邮件、短信等
    
    def _is_valid_sql_condition(self, condition):
        """验证SQL条件的有效性"""
        # 这里可以添加更复杂的SQL语法检查
        # 简单起见，我们只检查是否包含基本关键字
        condition = condition.lower()
        if "select" not in condition:
            return False
        if "from" not in condition:
            return False
        return True 