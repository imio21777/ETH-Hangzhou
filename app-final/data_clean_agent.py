from base_agent import BaseAgent
import json
import time
import os

class DataCleanAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="DataCleanAgent")
        self.initialize_database()
    
    def initialize_database(self):
        """初始化数据库结构"""
        # 创建需要的表格
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        # 币种信息表
        coin_info_table = """
        CREATE TABLE IF NOT EXISTS coin_info (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            contract TEXT,
            price REAL,
            market_cap REAL,
            volume_24h REAL,
            change_24h REAL,
            description TEXT,
            features TEXT,
            last_updated INTEGER
        )
        """
        
        # 鲸鱼交易表
        whale_transaction_table = """
        CREATE TABLE IF NOT EXISTS whale_transactions (
            tx_hash TEXT PRIMARY KEY,
            from_address TEXT,
            to_address TEXT,
            value REAL,
            coin TEXT,
            block_number INTEGER,
            timestamp INTEGER
        )
        """
        
        # 交易所提款表
        cex_withdrawal_table = """
        CREATE TABLE IF NOT EXISTS cex_withdrawals (
            tx_hash TEXT PRIMARY KEY,
            from_address TEXT,
            to_address TEXT,
            value REAL,
            timestamp INTEGER
        )
        """
        
        # 合约活动表
        contract_activity_table = """
        CREATE TABLE IF NOT EXISTS contract_activities (
            tx_hash TEXT PRIMARY KEY,
            contract_address TEXT,
            contract_type TEXT,
            from_address TEXT,
            value REAL,
            timestamp INTEGER,
            block_number INTEGER
        )
        """
        
        # 高频交易地址表
        frequent_address_table = """
        CREATE TABLE IF NOT EXISTS frequent_addresses (
            address TEXT PRIMARY KEY,
            transaction_count INTEGER,
            first_seen INTEGER,
            last_seen INTEGER
        )
        """
        
        # 执行创建表的SQL
        self.api_caller.execute_sql(coin_info_table)
        self.api_caller.execute_sql(whale_transaction_table)
        self.api_caller.execute_sql(cex_withdrawal_table)
        self.api_caller.execute_sql(contract_activity_table)
        self.api_caller.execute_sql(frequent_address_table)
    
    def receive_message(self, message):
        """接收消息"""
        if message["type"] == "processed_data":
            return self.process_data(message["content"])
        elif message["type"] == "sql_query":
            if "query" in message["content"]:
                return self.execute_query(message["content"]["query"])
            return {"status": "error", "message": "未提供SQL查询"}
        return {"status": "error", "message": "未支持的消息类型"}
    
    def process_data(self, content):
        """处理各种类型的数据并存储到数据库"""
        if "type" not in content or "data" not in content:
            return {"status": "error", "message": "数据格式不正确"}
        
        data_type = content["type"]
        data = content["data"]
        
        if data_type == "basic_coin_info":
            return self._process_coin_info(data)
        elif data_type == "whale_activities":
            return self._process_whale_activities(data)
        elif data_type == "cex_withdrawals":
            return self._process_cex_withdrawals(data)
        elif data_type == "contract_activities":
            return self._process_contract_activities(data)
        elif data_type == "frequent_transactions":
            return self._process_frequent_transactions(data)
        
        return {"status": "error", "message": f"未知的数据类型: {data_type}"}
    
    def execute_query(self, query):
        """执行SQL查询"""
        result = self.api_caller.execute_sql(query)
        return {
            "status": "success" if "error" not in result else "error",
            "result": result
        }
    
    def process(self, data=None):
        """处理任务"""
        if not data:
            return {"status": "error", "message": "未提供数据"}
        
        if "type" in data and data["type"] == "sql_query":
            if "query" in data:
                return self.execute_query(data["query"])
            return {"status": "error", "message": "未提供SQL查询"}
        
        return {"status": "error", "message": "未支持的任务类型"}
    
    def _process_coin_info(self, data):
        """处理币种信息数据"""
        if "coins" not in data:
            return {"status": "error", "message": "币种数据格式不正确"}
        
        coins = data["coins"]
        timestamp = data.get("timestamp", int(time.time()))
        
        for coin in coins:
            # 准备数据
            coin_data = {
                "symbol": coin.get("symbol", ""),
                "name": coin.get("name", ""),
                "contract": coin.get("contract", ""),
                "price": coin.get("price"),
                "market_cap": coin.get("market_cap"),
                "volume_24h": coin.get("volume_24h"),
                "change_24h": coin.get("change_24h"),
                "description": coin.get("description", ""),
                "features": json.dumps(coin.get("features", {})) if isinstance(coin.get("features"), dict) else coin.get("features", ""),
                "last_updated": timestamp
            }
            
            # 过滤掉None值
            coin_data = {k: v for k, v in coin_data.items() if v is not None}
            
            # 构建SQL
            placeholders = ", ".join(["?" for _ in coin_data])
            columns = ", ".join(coin_data.keys())
            values = tuple(coin_data.values())
            
            # 更新币种信息
            upsert_sql = f"""
            INSERT OR REPLACE INTO coin_info ({columns})
            VALUES ({placeholders})
            """
            
            self.api_caller.execute_sql(upsert_sql, values)
        
        return {"status": "success", "message": f"已处理 {len(coins)} 个币种信息"}
    
    def _process_whale_activities(self, data):
        """处理鲸鱼活动数据"""
        if "whale_transactions" not in data:
            return {"status": "error", "message": "鲸鱼交易数据格式不正确"}
        
        transactions = data["whale_transactions"]
        
        for tx in transactions:
            # 准备数据
            tx_data = {
                "tx_hash": tx.get("hash", ""),
                "from_address": tx.get("from", ""),
                "to_address": tx.get("to", ""),
                "value": float(tx.get("value", 0)) / 1e18 if tx.get("value", "").isdigit() else 0,
                "coin": tx.get("detected_coin", "ETH"),
                "block_number": int(tx.get("blockNumber", 0)) if tx.get("blockNumber", "").isdigit() else 0,
                "timestamp": int(tx.get("timeStamp", 0)) if tx.get("timeStamp", "").isdigit() else 0
            }
            
            # 过滤掉空哈希值
            if not tx_data["tx_hash"]:
                continue
            
            # 构建SQL
            placeholders = ", ".join(["?" for _ in tx_data])
            columns = ", ".join(tx_data.keys())
            values = tuple(tx_data.values())
            
            # 插入鲸鱼交易
            insert_sql = f"""
            INSERT OR REPLACE INTO whale_transactions ({columns})
            VALUES ({placeholders})
            """
            
            self.api_caller.execute_sql(insert_sql, values)
        
        return {"status": "success", "message": f"已处理 {len(transactions)} 个鲸鱼交易"}
    
    def _process_cex_withdrawals(self, data):
        """处理交易所提款数据"""
        if "withdrawals" not in data:
            return {"status": "error", "message": "交易所提款数据格式不正确"}
        
        withdrawals = data["withdrawals"]
        
        for withdrawal in withdrawals:
            # 准备数据
            withdrawal_data = {
                "tx_hash": withdrawal.get("hash", ""),
                "from_address": withdrawal.get("from", ""),
                "to_address": withdrawal.get("to", ""),
                "value": float(withdrawal.get("value", 0)) / 1e18 if withdrawal.get("value", "").isdigit() else 0,
                "timestamp": int(withdrawal.get("timeStamp", 0)) if withdrawal.get("timeStamp", "").isdigit() else 0
            }
            
            # 过滤掉空哈希值
            if not withdrawal_data["tx_hash"]:
                continue
            
            # 构建SQL
            placeholders = ", ".join(["?" for _ in withdrawal_data])
            columns = ", ".join(withdrawal_data.keys())
            values = tuple(withdrawal_data.values())
            
            # 插入交易所提款
            insert_sql = f"""
            INSERT OR REPLACE INTO cex_withdrawals ({columns})
            VALUES ({placeholders})
            """
            
            self.api_caller.execute_sql(insert_sql, values)
        
        return {"status": "success", "message": f"已处理 {len(withdrawals)} 个交易所提款"}
    
    def _process_contract_activities(self, data):
        """处理合约活动数据"""
        if "contracts" not in data:
            return {"status": "error", "message": "合约活动数据格式不正确"}
        
        contracts = data["contracts"]
        
        for contract in contracts:
            contract_address = contract.get("address", "")
            contract_type = contract.get("type", "未知")
            interactions = contract.get("interactions", [])
            
            for interaction in interactions:
                # 准备数据
                interaction_data = {
                    "tx_hash": interaction.get("hash", ""),
                    "contract_address": contract_address,
                    "contract_type": contract_type,
                    "from_address": interaction.get("from", ""),
                    "value": float(interaction.get("value", 0)) / 1e18 if interaction.get("value", "").isdigit() else 0,
                    "timestamp": int(interaction.get("timeStamp", 0)) if interaction.get("timeStamp", "").isdigit() else 0,
                    "block_number": int(interaction.get("blockNumber", 0)) if interaction.get("blockNumber", "").isdigit() else 0
                }
                
                # 过滤掉空哈希值
                if not interaction_data["tx_hash"]:
                    continue
                
                # 构建SQL
                placeholders = ", ".join(["?" for _ in interaction_data])
                columns = ", ".join(interaction_data.keys())
                values = tuple(interaction_data.values())
                
                # 插入合约活动
                insert_sql = f"""
                INSERT OR REPLACE INTO contract_activities ({columns})
                VALUES ({placeholders})
                """
                
                self.api_caller.execute_sql(insert_sql, values)
        
        return {"status": "success", "message": f"已处理 {len(contracts)} 个合约的活动数据"}
    
    def _process_frequent_transactions(self, data):
        """处理频繁交易数据"""
        if "frequent_addresses" not in data:
            return {"status": "error", "message": "频繁交易数据格式不正确"}
        
        addresses = data["frequent_addresses"]
        timestamp = data.get("timestamp", int(time.time()))
        
        for addr_data in addresses:
            address = addr_data.get("address", "")
            transaction_count = addr_data.get("transaction_count", 0)
            
            if not address:
                continue
            
            # 查询地址是否已存在
            query_sql = "SELECT first_seen FROM frequent_addresses WHERE address = ?"
            result = self.api_caller.execute_sql(query_sql, (address,))
            
            first_seen = timestamp
            if result and len(result) > 0:
                first_seen = result[0].get("first_seen", timestamp)
            
            # 准备数据
            address_data = {
                "address": address,
                "transaction_count": transaction_count,
                "first_seen": first_seen,
                "last_seen": timestamp
            }
            
            # 构建SQL
            placeholders = ", ".join(["?" for _ in address_data])
            columns = ", ".join(address_data.keys())
            values = tuple(address_data.values())
            
            # 更新频繁交易地址信息
            upsert_sql = f"""
            INSERT OR REPLACE INTO frequent_addresses ({columns})
            VALUES ({placeholders})
            """
            
            self.api_caller.execute_sql(upsert_sql, values)
        
        return {"status": "success", "message": f"已处理 {len(addresses)} 个频繁交易地址"} 