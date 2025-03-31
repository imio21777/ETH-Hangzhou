#!/usr/bin/env python
import sys
import json
from main import create_agent_system, process_transaction, process_user_request

def print_help():
    """打印帮助信息"""
    print("""
区块链多代理系统演示工具

使用方法:
  python run_demo.py [命令] [参数]

可用命令:
  tx [交易哈希]       - 分析指定的区块链交易
  alert [消息]        - 设置市场提醒
  trade [指令]        - 执行交易操作
  help               - 显示此帮助信息

示例:
  python run_demo.py tx 0x7d3c5142ef8063322ad0815155a6627365a5b0548f1b488588b54bf6a242a7c8
  python run_demo.py alert "ETH价格超过2500美元时通过邮件提醒我"
  python run_demo.py trade "在Binance上以40000美元的价格购买0.5个比特币"
""")

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    # 创建代理系统
    try:
        central_agent = create_agent_system()
    except Exception as e:
        print(f"创建代理系统时出错: {str(e)}")
        return

    if command == "help":
        print_help()
        return

    elif command == "tx":
        if len(sys.argv) < 3:
            print("错误: 未提供交易哈希")
            return

        tx_hash = sys.argv[2]
        print(f"正在分析交易: {tx_hash}")
        try:
            result = process_transaction(central_agent, tx_hash)
            print_result(result)
        except Exception as e:
            print(f"处理交易时出错: {str(e)}")

    elif command == "alert":
        if len(sys.argv) < 3:
            print("错误: 未提供提醒消息")
            return

        message = " ".join(sys.argv[2:])
        print(f"正在设置提醒: {message}")
        try:
            result = process_user_request(central_agent, message)
            print_result(result)
        except Exception as e:
            print(f"设置提醒时出错: {str(e)}")

    elif command == "trade":
        if len(sys.argv) < 3:
            print("错误: 未提供交易指令")
            return

        message = " ".join(sys.argv[2:])
        print(f"正在处理交易指令: {message}")
        try:
            result = process_user_request(central_agent, message)
            print_result(result)
        except Exception as e:
            print(f"处理交易指令时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    else:
        print(f"未知命令: {command}")
        print_help()

def print_result(result):
    """格式化并打印结果"""
    # 当结果为None时提供错误信息
    if result is None:
        print("\n错误: 处理请求时发生未知错误，未收到有效响应")
        return

    # 打印结果的简略版本
    if not result.get("success", False):
        print(f"\n错误: {result.get('error', '未知错误')}")
        if "details" in result:
            print(f"详细信息: {result['details']}")
        return

    response_type = result.get("response_type", "unknown")

    if response_type == "transaction_analysis":
        # 打印交易分析摘要
        analysis = result.get("analysis", {})
        print("\n=== 交易分析结果 ===")

        # 交易基本信息
        tx = analysis.get("transaction", {})
        print(f"交易哈希: {tx.get('hash', 'N/A')}")
        print(f"发送方: {tx.get('sender', 'N/A')}")
        print(f"接收方: {tx.get('receiver', 'N/A')}")
        print(f"金额: {tx.get('value', '0')} {tx.get('token', 'ETH')}")

        # 分析摘要
        print(f"\n摘要: {analysis.get('summary', '无摘要')}")

        # 标签信息
        labels = analysis.get("analysis", {}).get("labels", {})
        if labels:
            print("\n标签:")
            for key, value in labels.items():
                print(f"  {key}: {'是' if value else '否'}")

        # 洞察
        insights = analysis.get("insights", [])
        if insights:
            print("\n洞察:")
            for insight in insights:
                print(f"  {insight.get('source', '来源')}: {insight.get('content', '')}")

        # 建议
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            print("\n建议:")
            for rec in recommendations:
                print(f"  {rec.get('action', '')} (优先级: {rec.get('priority', '低')})")

        # 警报
        alerts = result.get("alerts", [])
        if alerts:
            print("\n警报:")
            for alert in alerts:
                print(f"  {alert.get('type', '未知')} ({alert.get('severity', '低')}): {alert.get('message', '')}")

        # 交易操作
        actions = result.get("trading_actions", [])
        if actions:
            print("\n建议交易操作:")
            for action in actions:
                print(f"  {action.get('type', '未知')} - {action.get('reasoning', '')}")

    elif response_type == "market_alert":
        alert_setup = result.get("alert_setup", {})
        print("\n=== 市场提醒设置 ===")
        print(f"状态: {'成功' if alert_setup.get('success', False) else '失败'}")
        print(f"提醒ID: {alert_setup.get('alert_id', 'N/A')}")
        print(f"消息: {alert_setup.get('message', 'N/A')}")

        notification = alert_setup.get("notification_setup", {})
        if notification:
            print(f"通知方式: {notification.get('method', 'N/A')}")
            print(f"发送目标: {notification.get('target', 'N/A')}")

    elif response_type == "trading_action":
        trading_result = result.get("trading_result", {})
        print("\n=== 交易执行结果 ===")
        print(f"状态: {'成功' if trading_result.get('success', False) else '失败'}")

        if "tx_hash" in trading_result:  # 钱包交易
            print(f"交易哈希: {trading_result.get('tx_hash', 'N/A')}")
            print(f"操作: {trading_result.get('action', 'N/A')}")
            print(f"代币: {trading_result.get('token', 'N/A')}")
            print(f"数量: {trading_result.get('amount', 'N/A')}")
            print(f"价格: {trading_result.get('price', 'N/A')}")
            print(f"状态: {trading_result.get('status', 'N/A')}")

        elif "order_id" in trading_result:  # 交易所交易
            print(f"订单ID: {trading_result.get('order_id', 'N/A')}")
            print(f"交易所: {trading_result.get('exchange', 'N/A')}")
            print(f"市场: {trading_result.get('market', 'N/A')}")
            print(f"类型: {trading_result.get('type', 'N/A')}")
            print(f"方向: {trading_result.get('side', 'N/A')}")
            print(f"数量: {trading_result.get('amount', 'N/A')}")
            print(f"价格: {trading_result.get('price', 'N/A')}")

    else:
        # 对于未知响应类型，直接打印整个结果
        print("\n=== 响应 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
