import time
import traceback
import os

from info_process_agent import InfoProcessAgent
from cex_withdraw_agent import CEXWithdrawAgent
from specific_coin_whale_agent import SpecificCoinWhaleAgent
from freq_tx_agent import FreqTxAgent
from contract_monitor_agent import ContractMonitorAgent
from basic_coin_info_agent import BasicCoinInfoAgent
from data_clean_agent import DataCleanAgent
from central_agent import CentralAgent
from user_agent import UserAgent
from alarm_agent import AlarmAgent
from wallet_agent import WalletAgent
from cex_agent import CEXAgent
from auto_trade_agent import AutoTradeAgent

def print_banner(text):
    """打印带边框的横幅"""
    width = len(text) + 4
    print("=" * width)
    print(f"| {text} |")
    print("=" * width)

def initialize_agents():
    """初始化所有代理并建立连接"""
    print_banner("初始化代理")
    
    # 创建所有代理实例
    info_process_agent = InfoProcessAgent()
    cex_withdraw_agent = CEXWithdrawAgent()
    specific_coin_whale_agent = SpecificCoinWhaleAgent()
    freq_tx_agent = FreqTxAgent()
    contract_monitor_agent = ContractMonitorAgent()
    basic_coin_info_agent = BasicCoinInfoAgent()
    data_clean_agent = DataCleanAgent()
    central_agent = CentralAgent()
    user_agent = UserAgent()
    alarm_agent = AlarmAgent()
    wallet_agent = WalletAgent()
    cex_agent = CEXAgent()
    auto_trade_agent = AutoTradeAgent()
    
    # 建立连接关系
    # 1. InfoProcessAgent 向其他代理分发信息
    print("📡 连接 InfoProcessAgent 与其他代理...")
    info_process_agent.register_agent(cex_withdraw_agent)
    info_process_agent.register_agent(specific_coin_whale_agent)
    info_process_agent.register_agent(freq_tx_agent)
    info_process_agent.register_agent(contract_monitor_agent)
    info_process_agent.register_agent(basic_coin_info_agent)
    
    # 2. 处理信息的代理向DataCleanAgent发送处理后的数据
    print("📡 连接处理代理与 DataCleanAgent...")
    cex_withdraw_agent.set_data_clean_agent(data_clean_agent)
    specific_coin_whale_agent.set_data_clean_agent(data_clean_agent)
    freq_tx_agent.set_data_clean_agent(data_clean_agent)
    contract_monitor_agent.set_data_clean_agent(data_clean_agent)
    basic_coin_info_agent.set_data_clean_agent(data_clean_agent)
    
    # 3. 中央代理连接其他功能代理
    print("📡 连接 CentralAgent 与其他功能代理...")
    central_agent.register_agents({
        "info_process_agent": info_process_agent,
        "data_clean_agent": data_clean_agent,
        "cex_withdraw_agent": cex_withdraw_agent,
        "specific_coin_whale_agent": specific_coin_whale_agent,
        "freq_tx_agent": freq_tx_agent,
        "contract_monitor_agent": contract_monitor_agent,
        "basic_coin_info_agent": basic_coin_info_agent,
        "wallet_agent": wallet_agent,
        "cex_agent": cex_agent,
        "auto_trade_agent": auto_trade_agent,
        "alarm_agent": alarm_agent
    })
    
    # 4. 用户代理连接中央代理
    print("📡 连接 UserAgent 与 CentralAgent...")
    user_agent.set_central_agent(central_agent)
    
    # 5. 警报代理连接信息处理代理和数据清理代理
    print("📡 连接 AlarmAgent 与相关代理...")
    alarm_agent.set_agents(info_process_agent, data_clean_agent)
    
    # 6. 钱包代理连接中央代理
    print("📡 连接 WalletAgent 与 CentralAgent...")
    wallet_agent.set_central_agent(central_agent)
    
    # 7. 交易所代理连接中央代理
    print("📡 连接 CEXAgent 与 CentralAgent...")
    cex_agent.set_central_agent(central_agent)
    
    # 8. 自动交易代理连接中央代理、钱包代理和交易所代理
    print("📡 连接 AutoTradeAgent 与相关代理...")
    auto_trade_agent.set_agents(central_agent, wallet_agent, cex_agent)
    
    # 返回初始化完成的代理
    return {
        "info_process_agent": info_process_agent,
        "cex_withdraw_agent": cex_withdraw_agent,
        "specific_coin_whale_agent": specific_coin_whale_agent,
        "freq_tx_agent": freq_tx_agent,
        "contract_monitor_agent": contract_monitor_agent,
        "basic_coin_info_agent": basic_coin_info_agent,
        "data_clean_agent": data_clean_agent,
        "central_agent": central_agent,
        "user_agent": user_agent,
        "alarm_agent": alarm_agent,
        "wallet_agent": wallet_agent,
        "cex_agent": cex_agent,
        "auto_trade_agent": auto_trade_agent
    }

def process_user_query(user_agent, query):
    """处理用户查询"""
    print_banner(f"处理用户查询: {query}")
    try:
        return user_agent.process_user_request(query)
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"❌ 处理用户查询时发生错误: {str(e)}\n{error_detail}")
        return {
            "status": "error",
            "message": f"处理查询时发生错误: {str(e)}"
        }

def main():
    """主程序入口"""
    # 清除旧的日志文件
    if os.path.exists("logs.txt"):
        os.remove("logs.txt")
        print("🧹 已清除旧的日志文件")
    
    # 清除旧的LLM调用记录
    if os.path.exists("llm.txt"):
        os.remove("llm.txt")
        print("🧹 已清除旧的LLM调用记录")
    
    print_banner("启动区块链multi-agent系统")
    try:
        agents = initialize_agents()
        user_agent = agents["user_agent"]
        
        print_banner("系统初始化完成")
        
        # 设置一些示例合约监控
        contract_monitor_agent = agents["contract_monitor_agent"]
        contract_monitor_agent.add_monitored_contract(
            "0xdac17f958d2ee523a2206206994597c13d831ec7", 
            "USDT Token Contract"
        )
        
        # 开始处理用户查询的循环
        while True:
            try:
                print("\n请输入您的查询 (输入'quit'退出):")
                query = input("> ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print_banner("退出系统")
                    break
                
                if query.strip():
                    print("⏳ 正在处理您的请求...")
                    result = process_user_query(user_agent, query)
                    
                    if result["status"] == "success" and "formatted_response" in result:
                        print_banner("处理结果")
                        print(f"✅ {result['formatted_response']}")
                    else:
                        print_banner("处理失败")
                        print(f"❌ {result.get('message', '未知错误')}")
                        if "original_result" in result:
                            print("原始结果:", result["original_result"])
            except KeyboardInterrupt:
                print("\n❗ 操作被中断")
                break
            except Exception as e:
                error_detail = traceback.format_exc()
                print(f"\n❌ 发生错误: {str(e)}\n{error_detail}")
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"❌ 系统初始化失败: {str(e)}\n{error_detail}")
    
    print_banner("系统已关闭")

if __name__ == "__main__":
    main() 