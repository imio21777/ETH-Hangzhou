// 全局变量
const agents = [
    // 中央代理放在中心位置
    { id: "CentralAgent", name: "Central Agent", type: "central-agent", x: 500, y: 300, width: 120, height: 40 },

    // 左侧节点垂直布局，避免重叠
    { id: "InfoProcessAgent", name: "Info. process agent", type: "info-process-agent", x: 150, y: 150, width: 120, height: 40 },
    { id: "MultiAgents", name: "MultiAgents", type: "multi-agents", x: 300, y: 200, width: 120, height: 40 },
    { id: "DataCleanAgent", name: "DataClean Agent", type: "data-clean-agent", x: 400, y: 250, width: 120, height: 40 },

    // 专用代理整体上移，放置到上部
    { id: "CEXWithdrawAgent", name: "CEX Withdraw Agents", type: "specialized-agent", x: 250, y: 20, width: 140, height: 40 },
    { id: "WhaleAgent", name: "Specific Coin Whale Agent", type: "specialized-agent", x: 420, y: 20, width: 140, height: 40 },
    { id: "TxAgent", name: "Freq. tx send/receive Agent", type: "specialized-agent", x: 250, y: 70, width: 140, height: 40 },
    { id: "ContractMonitorAgent", name: "Contract Monitor Agent", type: "specialized-agent", x: 420, y: 70, width: 140, height: 40 },
    { id: "BasicInfoAgent", name: "Basic Coin Info. Agent", type: "specialized-agent", x: 335, y: 120, width: 140, height: 40 },

    // 用户节点放在下方中央
    { id: "User", name: "User", type: "user-node", x: 350, y: 400, width: 120, height: 40 },

    // 云API节点移到右上角
    { id: "BlockchainAPI", name: "Blockchain API", type: "cloud-node", x: 700, y: 20, width: 120, height: 80 },
    { id: "LLMAPI", name: "LLM API", type: "cloud-node", x: 800, y: 40, width: 120, height: 80 },
    { id: "CEXAPI", name: "CEX API", type: "cloud-node", x: 900, y: 20, width: 120, height: 80 },

    // 右侧功能代理分散布局
    { id: "AlarmAgent", name: "Alarm Agent", type: "alarm-agent", x: 650, y: 300, width: 120, height: 40 },
    { id: "AutoTradeAgent", name: "AutoTrade Agent", type: "execution-agent", x: 650, y: 200, width: 120, height: 40 },
    { id: "WalletAgent", name: "Wallet Agent", type: "execution-agent", x: 800, y: 150, width: 120, height: 40 },
    { id: "CEXAgent", name: "CEX Agent", type: "execution-agent", x: 800, y: 250, width: 120, height: 40 },

    // 结果节点放在最右侧
    { id: "ApprovalTx", name: "Approval\nSubmit tx", type: "result-node", x: 950, y: 150, width: 120, height: 40 },
    { id: "PlaceOrder", name: "Place Order", type: "result-node", x: 950, y: 250, width: 120, height: 40 },
    { id: "MessageCall", name: "Messages/Phone call", type: "result-node", x: 950, y: 350, width: 120, height: 40 }
];

// 存储原始节点位置
const originalAgentPositions = agents.map(agent => ({
    id: agent.id,
    x: agent.x,
    y: agent.y
}));

// 预定义的连接关系
const predefinedConnections = [
    { source: "InfoProcessAgent", target: "MultiAgents" },
    { source: "MultiAgents", target: "CEXWithdrawAgent" },
    { source: "MultiAgents", target: "WhaleAgent" },
    { source: "MultiAgents", target: "TxAgent" },
    { source: "MultiAgents", target: "ContractMonitorAgent" },
    { source: "MultiAgents", target: "BasicInfoAgent" },
    { source: "MultiAgents", target: "DataCleanAgent" },
    { source: "DataCleanAgent", target: "CentralAgent" },
    { source: "User", target: "CentralAgent" },
    { source: "CentralAgent", target: "AutoTradeAgent" },
    { source: "CentralAgent", target: "AlarmAgent" },
    { source: "AutoTradeAgent", target: "WalletAgent" },
    { source: "AutoTradeAgent", target: "CEXAgent" },
    { source: "WalletAgent", target: "ApprovalTx" },
    { source: "CEXAgent", target: "PlaceOrder" },
    { source: "AlarmAgent", target: "MessageCall" }
];

// 信息框数据
const infoBoxes = [
    // 删除Segment Format信息框
];

// 存储原始信息框位置和尺寸
const originalInfoBoxes = infoBoxes.map(box => ({
    x: box.x,
    y: box.y,
    width: box.width,
    height: box.height
}));

// 图表相关变量
let width, height, svg, link, node, messages;
let interactionHistory = [];
let agentRelations = [];

// 当文档加载完成时执行初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化WebSocket连接
    initializeSocket();

    // 初始化D3可视化图
    initializeGraph();

    // 设置事件监听器
    document.getElementById('submitRequest').addEventListener('click', handleRequestSubmission);

    // 加载历史交互（如果有）
    loadInteractionHistory();

    // 双击背景重置视图
    d3.select("#agent-graph").on("dblclick", resetView);
});

// 初始化WebSocket连接
function initializeSocket() {
    const socket = io();

    socket.on('connect', () => {
        console.log('已连接到服务器');
        addSystemMessage('已连接到区块链多代理可视化系统');
    });

    socket.on('disconnect', () => {
        console.log('与服务器断开连接');
        addSystemMessage('与服务器断开连接');
    });

    socket.on('message', (data) => {
        try {
            const interaction = typeof data === 'string' ? JSON.parse(data) : data;
            processInteraction(interaction);
        } catch (e) {
            console.error('处理消息出错:', e);
        }
    });

    window.socket = socket;
}

// 初始化D3可视化图
function initializeGraph() {
    // 获取容器尺寸
    const graphContainer = document.getElementById('agent-graph');
    width = graphContainer.clientWidth;
    height = graphContainer.clientHeight;

    // 调整节点位置以适应初始容器大小
    adjustNodePositions(width, height);

    svg = d3.select("#agent-graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // 添加定义，用于绘制云图标的滤镜效果
    const defs = svg.append("defs");

    // 添加模糊滤镜，使云朵看起来更柔和
    defs.append("filter")
        .attr("id", "cloud-blur")
        .append("feGaussianBlur")
        .attr("in", "SourceGraphic")
        .attr("stdDeviation", "2");

    // 创建箭头标记定义
    defs.append("marker")
        .attr("id", "arrowhead")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 10) // 调整箭头位置
        .attr("refY", 0)
        .attr("orient", "auto")
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("xoverflow", "visible")
        .append("path")
        .attr("d", "M 0,-5 L 10,0 L 0,5")
        .attr("fill", "#ffffff")
        .style("stroke", "none");

    // 添加缩放功能
    const zoomHandler = d3.zoom()
        .scaleExtent([0.5, 3]) // 缩放范围
        .on("zoom", (event) => {
            svg.select("g.everything").attr("transform", event.transform);
        });

    // 应用缩放功能
    svg.call(zoomHandler);

    // 创建一个包含所有内容的组
    const everything = svg.append("g")
        .attr("class", "everything");

    // 初始化连接线和节点组
    link = everything.append("g")
        .attr("class", "links")
        .selectAll("line");

    node = everything.append("g")
        .attr("class", "nodes")
        .selectAll("g");

    messages = everything.append("g")
        .attr("class", "messages")
        .selectAll("circle");

    // 初始信息框组
    everything.append("g")
        .attr("class", "info-boxes");

    // 更新图表
    updateGraph();

    // 添加预定义的连接
    addPredefinedConnections();

    // 添加动画效果，让云朵微微浮动
    animateClouds();

    // 自动将视图居中并适应整个图表
    const bounds = everything.node().getBBox();
    const scale = Math.min(
        width / bounds.width,
        height / bounds.height
    ) * 0.9; // 留出一些边距

    const translateX = width / 2 - (bounds.x + bounds.width / 2) * scale;
    const translateY = height / 2 - (bounds.y + bounds.height / 2) * scale;

    // 应用初始变换，确保整个图表可见
    svg.transition()
        .duration(750)
        .call(
            zoomHandler.transform,
            d3.zoomIdentity
                .translate(translateX, translateY)
                .scale(scale)
        );
}

// 调整节点位置以适应容器大小
function adjustNodePositions(newWidth, newHeight) {
    // 定义参考宽高 (原设计基于的尺寸)
    const referenceWidth = 1000;
    const referenceHeight = 500;

    // 计算缩放比例
    const scaleX = newWidth / referenceWidth;
    const scaleY = newHeight / referenceHeight;

    // 对每个节点应用缩放
    agents.forEach((agent, index) => {
        const original = originalAgentPositions[index];
        agent.x = original.x * scaleX;
        agent.y = original.y * scaleY;
    });

    // 对信息框应用缩放
    infoBoxes.forEach((box, index) => {
        const original = originalInfoBoxes[index];
        box.x = original.x * scaleX;
        box.y = original.y * scaleY;
        box.width = original.width * scaleX;
        box.height = original.height * scaleY;
    });
}

// 绘制信息框
function drawInfoBoxes() {
    // 首先移除现有的信息框
    svg.select(".info-boxes").selectAll("*").remove();

    const boxes = svg.select(".info-boxes")
        .selectAll("g")
        .data(infoBoxes)
        .enter()
        .append("g");

    // 添加外框
    boxes.append("rect")
        .attr("class", "info-box")
        .attr("x", d => d.x)
        .attr("y", d => d.y)
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .attr("rx", 5)
        .attr("ry", 5);

    // 添加标题
    boxes.append("text")
        .attr("class", "info-box-text")
        .attr("x", d => d.x + 10)
        .attr("y", d => d.y + 20)
        .text(d => d.title);

    // 添加内容行
    boxes.each(function(d) {
        const g = d3.select(this);
        d.lines.forEach((line, i) => {
            g.append("text")
                .attr("class", "info-box-text")
                .attr("x", d.x + 10)
                .attr("y", d.y + 40 + i * 20)
                .text(line);
        });
    });
}

// 添加预定义的连接
function addPredefinedConnections() {
    predefinedConnections.forEach(conn => {
        const sourceNode = agents.find(a => a.id === conn.source);
        const targetNode = agents.find(a => a.id === conn.target);

        if (sourceNode && targetNode) {
            agentRelations.push({
                source: sourceNode,
                target: targetNode,
                value: 1
            });
        }
    });

    updateAgentConnections();
}

// 更新可视化图
function updateGraph() {
    // 获取最新的容器尺寸
    const graphContainer = document.getElementById('agent-graph');
    width = graphContainer.clientWidth;
    height = graphContainer.clientHeight;

    // 更新SVG尺寸
    d3.select("#agent-graph svg")
        .attr("width", width)
        .attr("height", height);

    // 重新调整节点位置
    adjustNodePositions(width, height);

    // 更新节点
    const nodeElements = node.data(agents, d => d.id);
    nodeElements.exit().remove();

    // 创建新节点组
    const newNodes = nodeElements.enter()
        .append("g")
        .attr("class", d => `node ${d.type}`)
        .attr("transform", d => `translate(${d.x},${d.y})`)
        .on("dblclick", focusOnNode); // 添加双击事件监听

    // 为不同类型的节点添加不同形状
    // 云节点使用路径绘制云形状
    newNodes.filter(d => d.type === "cloud-node")
        .append("path")
        .attr("d", d => {
            // 定义云朵路径 - 设计一个简单的云形状
            const w = d.width;
            const h = d.height;
            // 云朵路径，使用贝塞尔曲线绘制一个简单的云形状
            return `M ${-w/2 + w*0.2},${0}
                   a ${w*0.2},${h*0.25} 0 1,1 ${w*0.2},${-h*0.1}
                   a ${w*0.25},${h*0.25} 0 1,1 ${w*0.3},${h*0.05}
                   a ${w*0.2},${h*0.2} 0 1,1 ${w*0.2},${h*0.15}
                   a ${w*0.2},${h*0.2} 0 1,1 ${-w*0.2},${h*0.15}
                   a ${w*0.25},${h*0.25} 0 1,1 ${-w*0.3},${-h*0.05}
                   a ${w*0.2},${h*0.2} 0 1,1 ${-w*0.2},${-h*0.2}
                   z`;
        });

    // 其他节点使用矩形
    newNodes.filter(d => d.type !== "cloud-node")
        .append("rect")
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .attr("x", d => -d.width/2)
        .attr("y", d => -d.height/2)
        .attr("rx", 10)
        .attr("ry", 10);

    // 添加节点文本
    newNodes.append("text")
        .attr("class", "node-label")
        .attr("x", 0)
        .attr("y", d => d.type === "cloud-node" ? 0 : 0) // 云节点的文本位置调整
        .each(function(d) {
            const text = d3.select(this);
            const lines = d.name.split('\n');

            if (lines.length === 1) {
                text.text(d.name);
            } else {
                lines.forEach((line, i) => {
                    const lineHeight = 14;
                    const yOffset = (i - (lines.length - 1) / 2) * lineHeight;
                    text.append("tspan")
                        .attr("x", 0)
                        .attr("y", yOffset)
                        .attr("dy", "0.35em")
                        .text(line);
                });
            }
        });

    node = newNodes.merge(nodeElements);

    // 更新代理间关系连接
    updateAgentConnections();

    // 更新信息框
    drawInfoBoxes();
}

// 更新代理间连接关系
function updateAgentConnections() {
    // 首先移除现有连接线
    svg.select(".links").selectAll("*").remove();

    // 创建弯曲的路径生成器
    const linkGenerator = d3.linkHorizontal()
        .x(d => d.x)
        .y(d => d.y);

    // 为每个连接创建曲线路径
    const linkPaths = svg.select(".links")
        .selectAll("path")
        .data(agentRelations)
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("d", d => {
            // 根据节点类型调整连接线的曲率
            // 如果是水平方向相距较远的节点，使用更平滑的曲线
            const dx = Math.abs(d.source.x - d.target.x);
            const dy = Math.abs(d.source.y - d.target.y);

            // 如果是垂直排列的节点，使用不同的曲线类型
            if (dx < 100 && dy > 50) {
                return `M${d.source.x},${d.source.y}
                       C${d.source.x},${(d.source.y + d.target.y) / 2}
                        ${d.target.x},${(d.source.y + d.target.y) / 2}
                        ${d.target.x},${d.target.y}`;
            }

            // 对于其他情况，使用水平曲线
            return linkGenerator({
                source: {x: d.source.x, y: d.source.y},
                target: {x: d.target.x, y: d.target.y}
            });
        })
        .attr("marker-end", "url(#arrowhead)");

    // 更新全局变量
    link = linkPaths;
}

// 处理代理交互事件
function processInteraction(interaction) {
    // 添加到历史记录
    interactionHistory.push(interaction);

    // 记录到日志
    addInteractionLog(interaction);

    // 显示消息动画
    showMessageAnimation(interaction);
}

// 显示消息日志
function addInteractionLog(interaction) {
    const logDiv = document.getElementById('interactionLog');

    // 确定消息类型的样式类
    let className = 'agent-message';
    if (interaction.type === 'api_call') className = 'api-call';
    if (interaction.type === 'api_response') className = 'api-response';
    if (interaction.type === 'llm_request') className = 'llm-request';
    if (interaction.type === 'llm_response') className = 'llm-response';
    if (interaction.type === 'error') className = 'error-message';
    if (interaction.type === 'system') className = 'system-message';

    // 格式化时间
    const time = new Date(interaction.timestamp * 1000).toLocaleTimeString();

    // 创建消息内容
    let messageContent = `[${time}] ${interaction.source} → ${interaction.target}`;
    if (interaction.type) {
        messageContent += ` (${interaction.type})`;
    }

    // 创建日志条目
    const logEntry = document.createElement('div');
    logEntry.className = className;
    logEntry.innerText = messageContent;

    // 为详细内容添加可点击展开
    if (interaction.content) {
        const detailsButton = document.createElement('button');
        detailsButton.className = 'details-button';
        detailsButton.innerText = '查看详情';
        detailsButton.onclick = function() {
            toggleDetails(this, interaction.content);
        };
        logEntry.appendChild(detailsButton);
    }

    // 添加到日志容器
    logDiv.appendChild(logEntry);
    logDiv.scrollTop = logDiv.scrollHeight;
}

// 切换显示详情
function toggleDetails(button, content) {
    const parent = button.parentNode;
    const detailsDiv = parent.querySelector('.details-content');

    if (detailsDiv) {
        // 详情已存在，切换显示/隐藏
        if (detailsDiv.style.display === 'none') {
            detailsDiv.style.display = 'block';
            button.innerText = '隐藏详情';
        } else {
            detailsDiv.style.display = 'none';
            button.innerText = '查看详情';
        }
    } else {
        // 创建新的详情div
        const newDetailsDiv = document.createElement('div');
        newDetailsDiv.className = 'details-content';

        // 尝试格式化JSON内容
        try {
            const contentObj = typeof content === 'string' ? JSON.parse(content) : content;
            newDetailsDiv.innerHTML = '<pre>' + JSON.stringify(contentObj, null, 2) + '</pre>';
        } catch (e) {
            // 不是有效的JSON，显示原始内容
            newDetailsDiv.innerText = content;
        }

        parent.appendChild(newDetailsDiv);
        button.innerText = '隐藏详情';
    }
}

// 显示消息传递动画
function showMessageAnimation(interaction) {
    // 查找源节点和目标节点
    const sourceAgentId = getMatchingAgentId(interaction.source);
    const targetAgentId = getMatchingAgentId(interaction.target);

    const sourceNode = agents.find(a => a.id === sourceAgentId);
    const targetNode = agents.find(a => a.id === targetAgentId);

    if (!sourceNode || !targetNode) return;

    // 确定消息颜色
    let messageColor = "#6666ff";  // 默认颜色-蓝色(代理间通信)
    if (interaction.type === 'api_call') messageColor = "#ff6666";  // 红色(API调用)
    if (interaction.type === 'api_response') messageColor = "#66ff66";  // 绿色(API响应)
    if (interaction.type === 'llm_request') messageColor = "#ff66ff";  // 粉色(LLM请求)
    if (interaction.type === 'llm_response') messageColor = "#ffff66";  // 黄色(LLM响应)
    if (interaction.type === 'error') messageColor = "#ff0000";  // 亮红色(错误)
    if (interaction.type === 'system') messageColor = "#cccccc";  // 灰色(系统)

    // 创建云到其他节点或节点到云的特殊动画效果
    const isCloudSource = sourceNode.type === "cloud-node";
    const isCloudTarget = targetNode.type === "cloud-node";

    // 如果是从云发出或到云的消息，使用特殊的动画
    if (isCloudSource || isCloudTarget) {
        // 从云发出用降落状效果，到云用上升效果
        const message = svg.select(".messages")
            .append("circle")
            .attr("class", "message")
            .attr("r", 5)
            .attr("fill", messageColor)
            .attr("cx", sourceNode.x)
            .attr("cy", sourceNode.y)
            .style("opacity", 0.8);

        // 添加发光效果
        message.style("filter", "drop-shadow(0 0 3px " + messageColor + ")");

        // 动画路径
        message.transition()
            .duration(1500)
            .attr("cx", targetNode.x)
            .attr("cy", targetNode.y)
            .on("end", () => {
                message.remove();
            });
    } else {
        // 创建常规消息圆圈
        const message = svg.select(".messages")
            .append("circle")
            .attr("class", "message")
            .attr("r", 5)
            .attr("fill", messageColor)
            .attr("cx", sourceNode.x)
            .attr("cy", sourceNode.y);

        // 动画
        message.transition()
            .duration(1500)
            .attr("cx", targetNode.x)
            .attr("cy", targetNode.y)
            .on("end", () => {
                message.remove();
            });
    }
}

// 将交互消息中的代理名称映射到图表中的代理ID
function getMatchingAgentId(agentName) {
    const nameToId = {
        "CentralAgent": "CentralAgent",
        "InfoProcessAgent": "InfoProcessAgent",
        "CEXWithdrawAgent": "CEXWithdrawAgent",
        "WhaleAgent": "WhaleAgent",
        "TxAgent": "TxAgent",
        "ContractMonitorAgent": "ContractMonitorAgent",
        "BasicInfoAgent": "BasicInfoAgent",
        "DataCleanAgent": "DataCleanAgent",
        "AlarmAgent": "AlarmAgent",
        "WalletAgent": "WalletAgent",
        "CEXAgent": "CEXAgent",
        "LLM": "LLMAPI", // 将LLM映射到LLMAPI云
        "BlockchainAPI": "BlockchainAPI",
        "LLMAPI": "LLMAPI",
        "CEXAPI": "CEXAPI",
        "User": "User",
        "System": "User"
    };

    return nameToId[agentName] || agentName;
}

// 处理请求提交
function handleRequestSubmission() {
    const content = document.getElementById('requestContent').value;

    if (!content) {
        alert('请输入请求内容!');
        return;
    }

    // 清除结果日志
    document.getElementById('responseLog').innerHTML = '';

    // 显示加载提示
    document.getElementById('responseLog').innerHTML = '<div class="loading">处理中...</div>';

    // 发送请求
    fetch('/api/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        // 显示结果
        const responseLog = document.getElementById('responseLog');

        // 构建响应显示字符串，判断数据结构显示翻译后的内容
        let displayContent = '';

        // 检查不同可能的数据结构，确保能提取出翻译内容
        if (typeof data === 'string') {
            // 如果直接返回了字符串
            displayContent = data;
        } else if (data.content && typeof data.content === 'string') {
            // 有content字段
            displayContent = data.content;
        } else if (data.result && data.result.content) {
            // 嵌套在result中的content
            displayContent = data.result.content;
        } else {
            // 其他情况，格式化显示整个JSON
            displayContent = JSON.stringify(data, null, 2);
        }

        responseLog.innerHTML = '<pre>' + displayContent + '</pre>';
        responseLog.scrollTop = responseLog.scrollHeight;

        // 添加系统消息
        addSystemMessage(`请求处理完成: ${content}`);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('responseLog').innerHTML = '<div class="error">请求处理失败，请查看控制台了解详情。</div>';
    });
}

// 添加系统消息
function addSystemMessage(message) {
    // 创建系统消息对象
    const systemMessage = {
        type: 'system',
        source: 'System',
        target: 'User',
        content: message,
        timestamp: Date.now() / 1000
    };

    // 处理消息
    processInteraction(systemMessage);
}

// 加载历史交互
function loadInteractionHistory() {
    fetch('/api/interactions')
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                // 按时间顺序处理所有历史交互
                data.sort((a, b) => a.timestamp - b.timestamp)
                    .forEach(interaction => {
                        processInteraction(interaction);
                    });
            }
        })
        .catch(error => {
            console.error('加载历史交互出错:', error);
        });
}

// 添加窗口大小变化监听
window.addEventListener('resize', function() {
    // 避免频繁触发，使用防抖
    clearTimeout(window.resizeTimer);
    window.resizeTimer = setTimeout(function() {
        updateGraph();
        updateAgentConnections();
    }, 250);
});

// 添加云朵动画效果
function animateClouds() {
    // 选择所有云节点
    d3.selectAll(".node.cloud-node")
        .each(function() {
            const cloud = d3.select(this);

            // 应用随机的轻微上下浮动动画
            function animateFloat() {
                const randomDuration = 2000 + Math.random() * 2000; // 2-4秒随机持续时间
                const randomOffset = 5 + Math.random() * 5; // 5-10px的随机偏移量

                // 获取当前transform值，提取出当前的x坐标
                const currentTransform = cloud.attr("transform");
                const match = /translate\(([^,]+),([^)]+)\)/.exec(currentTransform);
                let currentX = 0, currentY = 0;

                if (match) {
                    currentX = parseFloat(match[1]);
                    currentY = parseFloat(match[2]);
                }

                cloud.transition()
                    .duration(randomDuration)
                    .attr("transform", function(d) {
                        return `translate(${d.x},${d.y - randomOffset})`;
                    })
                    .transition()
                    .duration(randomDuration)
                    .attr("transform", function(d) {
                        return `translate(${d.x},${d.y + randomOffset})`;
                    })
                    .on("end", animateFloat);
            }

            // 启动动画
            animateFloat();
        });
}

// 双击节点时聚焦
function focusOnNode(event, d) {
    event.stopPropagation(); // 阻止事件冒泡

    // 获取缩放处理器
    const zoomHandler = d3.zoom().on("zoom", (event) => {
        svg.select("g.everything").attr("transform", event.transform);
    });

    // 计算放大参数
    const scale = 1.5; // 放大倍数
    const translateX = width / 2 - d.x * scale;
    const translateY = height / 2 - d.y * scale;

    // 应用转换，聚焦在选中的节点
    svg.transition()
        .duration(750)
        .call(
            zoomHandler.transform,
            d3.zoomIdentity
                .translate(translateX, translateY)
                .scale(scale)
        );
}

// 重置视图函数
function resetView() {
    // 获取缩放处理器
    const zoomHandler = d3.zoom().on("zoom", (event) => {
        svg.select("g.everything").attr("transform", event.transform);
    });

    // 获取整个图表的边界框
    const bounds = svg.select("g.everything").node().getBBox();
    const scale = Math.min(
        width / bounds.width,
        height / bounds.height
    ) * 0.9; // 留出一些边距

    const translateX = width / 2 - (bounds.x + bounds.width / 2) * scale;
    const translateY = height / 2 - (bounds.y + bounds.height / 2) * scale;

    // 应用转换，重置视图
    svg.transition()
        .duration(750)
        .call(
            zoomHandler.transform,
            d3.zoomIdentity
                .translate(translateX, translateY)
                .scale(scale)
        );
}
