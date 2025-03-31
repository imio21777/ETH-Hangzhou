# 区块链多代理系统安装和运行指南

本文档提供安装和运行区块链多代理系统的详细步骤。

## 系统要求

- Python 3.7 或更高版本
- 互联网连接（用于LLM API调用）
- 有效的API密钥（在config.txt中配置）

## 安装步骤

1. 克隆或下载代码库到本地

2. 安装所需依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置API密钥
   确保`config.txt`文件中包含有效的API密钥和相关配置。默认配置如下：
   ```
   BASE_URL = "https://api2.aigcbest.top/v1"
   API_KEY = "sk-NiMvTTja0AQMrEkNgOElafUVP6HnOcrBu0tJhfTeucBSJzU3"
   MODEL = "claude-3-7-sonnet-20250219-thinking"
   ```

   如果需要使用其他API服务，请相应修改BASE_URL和API_KEY。

## 运行系统

系统提供了两种运行方式：

### 方式1：使用run_demo.py脚本

这是一个简单的命令行工具，支持三种主要功能：

**1. 分析区块链交易**
```bash
python run_demo.py tx 0x7d3c5142ef8063322ad0815155a6627365a5b0548f1b488588b54bf6a242a7c8
```

**2. 设置市场警报**
```bash
python run_demo.py alert "ETH价格超过2500美元时通过邮件提醒我"
```

**3. 执行交易操作**
```bash
python run_demo.py trade "在Binance上以40000美元的价格购买0.5个比特币"
```

**获取帮助**
```bash
python run_demo.py help
```

### 方式2：使用main.py内置演示

系统提供了一个内置的演示程序，可运行预定义的示例：

```bash
python main.py --demo all
```

可选参数：
- `--demo tx`: 仅运行交易分析演示
- `--demo alert`: 仅运行市场警报演示
- `--demo trade`: 仅运行交易执行演示
- `--demo all`: 运行所有演示（默认）

### 方式3：在自己的Python代码中使用

您也可以在自己的Python程序中导入并使用多代理系统：

```python
from main import create_agent_system, process_transaction, process_user_request

# 创建代理系统
central_agent = create_agent_system()

# 分析交易
result = process_transaction(central_agent, "0x7d3c5142ef8063322ad0815155a6627365a5b0548f1b488588b54bf6a242a7c8")
print(result)

# 或者处理用户请求
result = process_user_request(central_agent, "ETH价格超过2500美元时通过邮件提醒我")
print(result)
```

## 注意事项

1. 当前系统仅对LLM API实现了真实调用，区块链和交易所API仍使用模拟数据。

2. 为了保护API密钥安全，系统会在控制台输出中对API密钥进行部分遮蔽。

3. 如果LLM API调用失败，系统会自动回退到使用模拟数据。

4. 模拟数据由系统生成，不代表真实区块链状态。

## 常见问题解决

**问题：API调用失败**
- 检查config.txt中的API密钥是否有效
- 确认互联网连接正常
- 查看API_KEY是否有足够的使用额度

**问题：缺少依赖库**
- 运行`pip install -r requirements.txt`安装所有需要的依赖

**问题：运行缓慢**
- LLM API调用可能需要一些时间，特别是在网络状况不佳时
- 系统会在控制台显示API调用进度

## 自定义和扩展

请参考README.md中的"扩展系统"部分，了解如何添加新代理或自定义API调用。
