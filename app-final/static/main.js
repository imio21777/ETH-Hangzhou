// 全局变量
const agents = [
  // 左侧专用代理
  {
    id: "CEXWithdrawAgent",
    name: "CEX Withdraw Agents",
    type: "specialized-agent",
    x: 226,
    y: 137,
    width: 140,
    height: 40,
    color: "#74b9ff",
  },
  {
    id: "WhaleAgent",
    name: "Specific Coin Whale Agent",
    type: "specialized-agent",
    x: 397,
    y: 137,
    width: 140,
    height: 40,
    color: "#74b9ff",
  },
  {
    id: "TxAgent",
    name: "Freq. tx send/receive Agent",
    type: "specialized-agent",
    x: 226,
    y: 211,
    width: 140,
    height: 40,
    color: "#74b9ff",
  },
  {
    id: "ContractMonitorAgent",
    name: "Contract Monitor Agent",
    type: "specialized-agent",
    x: 397,
    y: 211,
    width: 140,
    height: 40,
    color: "#74b9ff",
  },
  {
    id: "BasicInfoAgent",
    name: "Basic Coin Info. Agent",
    type: "specialized-agent",
    x: 311,
    y: 285,
    width: 140,
    height: 40,
    color: "#74b9ff",
  },

  // 中间代理层
  {
    id: "InfoProcessAgent",
    name: "Info. process agent",
    type: "info-process-agent",
    x: 125,
    y: 330,
    width: 140,
    height: 40,
    color: "#74b9ff",
  },
  {
    id: "MultiAgents",
    name: "MultiAgents",
    type: "multi-agents",
    x: 276,
    y: 403,
    width: 120,
    height: 40,
    color: "#a29bfe",
  },
  {
    id: "DataCleanAgent",
    name: "DataClean Agent",
    type: "data-clean-agent",
    x: 376,
    y: 477,
    width: 120,
    height: 40,
    color: "#55efc4",
  },

  // 中央代理
  {
    id: "CentralAgent",
    name: "Central Agent",
    type: "central-agent",
    x: 478,
    y: 550,
    width: 120,
    height: 40,
    color: "#ff7675",
  },

  // 右侧功能代理
  {
    id: "AlarmAgent",
    name: "Alarm Agent",
    type: "alarm-agent",
    x: 629,
    y: 550,
    width: 120,
    height: 40,
    color: "#fd79a8",
  },
  {
    id: "AutoTradeAgent",
    name: "AutoTrade Agent",
    type: "execution-agent",
    x: 629,
    y: 403,
    width: 120,
    height: 40,
    color: "#d6a2e8",
  },
  {
    id: "WalletAgent",
    name: "Wallet Agent",
    type: "execution-agent",
    x: 780,
    y: 330,
    width: 120,
    height: 40,
    color: "#d6a2e8",
  },
  {
    id: "CEXAgent",
    name: "CEX Agent",
    type: "execution-agent",
    x: 780,
    y: 477,
    width: 120,
    height: 40,
    color: "#d6a2e8",
  },

  // 用户节点
  {
    id: "User",
    name: "User",
    type: "user-node",
    x: 326,
    y: 699,
    width: 100,
    height: 40,
    color: "#ffeaa7",
  },

  // 云API节点
  {
    id: "BlockchainAPI",
    name: "Blockchain API",
    type: "cloud-node",
    x: 680,
    y: 142,
    width: 150,
    height: 80,
    color: "#74b9ff",
  },
  {
    id: "LLMAPI",
    name: "LLM API",
    type: "cloud-node",
    x: 780,
    y: 175,
    width: 120,
    height: 80,
    color: "#74b9ff",
  },
  {
    id: "CEXAPI",
    name: "CEX API",
    type: "cloud-node",
    x: 880,
    y: 142,
    width: 120,
    height: 80,
    color: "#74b9ff",
  },

  // 结果节点
  {
    id: "ApprovalTx",
    name: "Approval\nSubmit tx",
    type: "result-node",
    x: 930,
    y: 330,
    width: 120,
    height: 40,
    color: "#ffeaa7",
  },
  {
    id: "PlaceOrder",
    name: "Place Order",
    type: "result-node",
    x: 930,
    y: 477,
    width: 120,
    height: 40,
    color: "#ffeaa7",
  },
  {
    id: "MessageCall",
    name: "Messages/Phone call",
    type: "result-node",
    x: 930,
    y: 624,
    width: 140,
    height: 40,
    color: "#ffeaa7",
  },
];

// 存储原始节点位置
const originalAgentPositions = agents.map((agent) => ({
  id: agent.id,
  x: agent.x,
  y: agent.y,
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
  { source: "AlarmAgent", target: "MessageCall" },
];

// 图表相关变量
let width, height, svg, link, node, messages;
let interactionHistory = [];
let agentRelations = [];
let activeDataFlows = [];

// 添加用户交互标志，初始为false
let userInteractionStarted = false;

// 添加警报定时器变量
let alarmTimer = null;

// 配置参数
let alarmConfig = {
  interval: 20000, // 默认值20秒
  initialDelay: 5000, // 默认值5秒
};

// 全局变量，用于跟踪合约调用状态
let contractCallInProgress = false;

// 当文档加载完成时执行初始化
document.addEventListener("DOMContentLoaded", function () {
  // 加载配置
  loadConfig();

  // 初始化WebSocket连接
  initializeSocket();

  // 初始化D3可视化图
  initializeGraph();

  // 设置事件监听器
  document
    .getElementById("submitRequest")
    .addEventListener("click", handleRequestSubmission);

  // 双击背景重置视图
  d3.select("#agent-graph").on("dblclick", resetView);
});

// 从服务器加载配置
function loadConfig() {
  fetch("/api/config")
    .then((response) => response.json())
    .then((data) => {
      console.log("已加载配置:", data);
      alarmConfig.interval = data.alarm_interval || 20000;
      alarmConfig.initialDelay = data.alarm_initial_delay || 5000;
    })
    .catch((error) => {
      console.error("加载配置失败:", error);
      // 使用默认值继续
    });
}

// 初始化WebSocket连接
function initializeSocket() {
  const socket = io();

  socket.on("connect", () => {
    console.log("已连接到服务器");
    // 不在初始化时添加系统消息
    // addSystemMessage("已连接到区块链多代理可视化系统");
  });

  socket.on("disconnect", () => {
    console.log("与服务器断开连接");
    if (userInteractionStarted) {
      addSystemMessage("与服务器断开连接");
    }
  });

  socket.on("message", (data) => {
    try {
      // 只有用户已交互后才处理消息
      if (userInteractionStarted) {
        const interaction = typeof data === "string" ? JSON.parse(data) : data;
        processInteraction(interaction);
      }
    } catch (e) {
      console.error("处理消息出错:", e);
    }
  });

  window.socket = socket;
}

// 初始化D3可视化图
function initializeGraph() {
  // 获取容器尺寸
  const graphContainer = document.getElementById("agent-graph");
  width = graphContainer.clientWidth;
  height = graphContainer.clientHeight;

  // 调整节点位置以适应初始容器大小
  adjustNodePositions(width, height);

  svg = d3
    .select("#agent-graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  // 添加定义，用于绘制云图标和其他形状
  const defs = svg.append("defs");

  // 添加发光效果
  const glow = defs
    .append("filter")
    .attr("id", "glow")
    .attr("x", "-30%")
    .attr("y", "-30%")
    .attr("width", "160%")
    .attr("height", "160%");

  glow
    .append("feGaussianBlur")
    .attr("stdDeviation", "6")
    .attr("result", "blur");

  glow
    .append("feComposite")
    .attr("in", "SourceGraphic")
    .attr("in2", "blur")
    .attr("operator", "over");

  // 添加更强的发光效果用于API节点
  const apiGlow = defs
    .append("filter")
    .attr("id", "api-glow")
    .attr("x", "-50%")
    .attr("y", "-50%")
    .attr("width", "200%")
    .attr("height", "200%");

  apiGlow
    .append("feGaussianBlur")
    .attr("stdDeviation", "15")
    .attr("result", "blur");

  apiGlow
    .append("feComposite")
    .attr("in", "SourceGraphic")
    .attr("in2", "blur")
    .attr("operator", "over");

  // 添加模糊滤镜，使云朵看起来更柔和
  defs
    .append("filter")
    .attr("id", "cloud-blur")
    .append("feGaussianBlur")
    .attr("in", "SourceGraphic")
    .attr("stdDeviation", "3");

  // 创建箭头标记定义
  defs
    .append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 20)
    .attr("refY", 0)
    .attr("orient", "auto")
    .attr("markerWidth", 8)
    .attr("markerHeight", 8)
    .attr("xoverflow", "visible")
    .append("path")
    .attr("d", "M 0,-5 L 10,0 L 0,5")
    .attr("fill", "#ffffff")
    .style("stroke", "none");

  // 添加虚线边框图案
  defs
    .append("pattern")
    .attr("id", "dashed-stroke")
    .attr("patternUnits", "userSpaceOnUse")
    .attr("width", 10)
    .attr("height", 10)
    .append("path")
    .attr("d", "M0,5 L10,5")
    .attr("stroke", "#ffeaa7")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "5,5");

  // 添加缩放功能
  const zoomHandler = d3
    .zoom()
    .scaleExtent([0.5, 2])
    .on("zoom", (event) => {
      svg.select("g.everything").attr("transform", event.transform);
    });

  // 应用缩放功能
  svg.call(zoomHandler);

  // 创建一个包含所有内容的组
  const everything = svg.append("g").attr("class", "everything");

  // 初始化连接线组
  link = everything.append("g").attr("class", "links").selectAll("path");

  // 初始化节点组
  node = everything.append("g").attr("class", "nodes").selectAll("g");

  // 初始化消息组
  messages = everything
    .append("g")
    .attr("class", "messages")
    .selectAll("circle");

  // 构建图表
  updateGraph();

  // 添加自适应大小调整
  window.addEventListener("resize", () => {
    width = graphContainer.clientWidth;
    height = graphContainer.clientHeight;

    svg.attr("width", width).attr("height", height);

    adjustNodePositions(width, height);
    updateGraph();
  });

  // 取消初始化时的模拟数据流动
  // setInterval(() => {
  //   simulateRandomDataFlow();
  // }, 5000);
}

// 检查节点是否与AlarmAgent相关
function isAlarmRelated(node) {
  // 如果节点本身是AlarmAgent
  if (node.id === "AlarmAgent") {
    return true;
  }

  // 检查节点是否与AlarmAgent有连接关系
  const hasDirectConnection = predefinedConnections.some(
    (conn) =>
      (conn.source === "AlarmAgent" && conn.target === node.id) ||
      (conn.source === node.id && conn.target === "AlarmAgent")
  );

  return hasDirectConnection;
}

// 模拟随机数据流动
function simulateRandomDataFlow() {
  // 只选择预定义连接中的连接进行模拟
  const connections = [...predefinedConnections];
  const randomIndex = Math.floor(Math.random() * connections.length);
  const randomConnection = connections[randomIndex];

  const sourceNode = agents.find((a) => a.id === randomConnection.source);
  const targetNode = agents.find((a) => a.id === randomConnection.target);

  if (sourceNode && targetNode) {
    // 检查是否与AlarmAgent相关
    if (isAlarmRelated(sourceNode) || isAlarmRelated(targetNode)) {
      // 获取要高亮的节点
      const alarmNode = agents.find((a) => a.id === "AlarmAgent");

      // 高亮相关节点边框
      if (sourceNode.id !== "AlarmAgent") highlightAgentBorder(sourceNode);
      if (targetNode.id !== "AlarmAgent") highlightAgentBorder(targetNode);
      highlightAgentBorder(alarmNode);
    } else {
      // 其他关系依然使用数据流动画，但只沿着实际的连接线
      animateDataFlow(sourceNode, targetNode, getRandomColor());
    }
  }
}

// 获取随机颜色
function getRandomColor() {
  const colors = [
    "#74b9ff",
    "#a29bfe",
    "#55efc4",
    "#ffeaa7",
    "#ff7675",
    "#fd79a8",
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}

// 调整节点位置，使其适应不同大小的容器
function adjustNodePositions(containerWidth, containerHeight) {
  const baseWidth = 1000; // 设计宽度
  const baseHeight = 800; // 设计高度

  const scaleX = containerWidth / baseWidth;
  const scaleY = containerHeight / baseHeight;

  agents.forEach((agent, i) => {
    // 使用原始位置进行缩放
    const originalPos = originalAgentPositions[i];
    agent.x = originalPos.x * scaleX;
    agent.y = originalPos.y * scaleY;
  });
}

// 更新图表
function updateGraph() {
  // 创建连接关系数据
  const links = predefinedConnections.map((conn) => {
    const sourceNode = agents.find((a) => a.id === conn.source);
    const targetNode = agents.find((a) => a.id === conn.target);
    return {
      source: sourceNode,
      target: targetNode,
    };
  });

  // 使用弧线路径绘制连接线
  link = link.data(links);
  link.exit().remove();

  const linkEnter = link
    .enter()
    .append("path")
    .attr("class", "link")
    .attr("marker-end", "url(#arrowhead)")
    .style("stroke", "#ffffff")
    .style("stroke-opacity", 0.6)
    .style("stroke-width", 1.5)
    .style("fill", "none");

  link = linkEnter.merge(link);

  link.attr("d", (d) => {
    const sourceX = d.source.x + d.source.width / 2;
    const sourceY = d.source.y + d.source.height / 2;
    const targetX = d.target.x + d.target.width / 2;
    const targetY = d.target.y + d.target.height / 2;

    // 计算控制点
    const dx = targetX - sourceX;
    const dy = targetY - sourceY;
    const dr = Math.sqrt(dx * dx + dy * dy) * 1.2; // 控制弧度

    // 使用弧线绘制
    return `M${sourceX},${sourceY}A${dr},${dr} 0 0,1 ${targetX},${targetY}`;
  });

  // 绘制节点
  node = node.data(agents);
  node.exit().remove();

  // 节点外部容器
  const nodeEnter = node
    .enter()
    .append("g")
    .attr("class", (d) => `node ${d.type}`)
    .attr("id", (d) => `node-${d.id}`);

  // 根据节点类型添加不同形状
  nodeEnter
    .filter((d) => d.type === "cloud-node")
    .append("path")
    .attr("d", (d) => generateCloudPath(d.width, d.height))
    .style("fill", (d) => d.color)
    .style("stroke", "#ffffff")
    .style("stroke-width", 2)
    .style("filter", "url(#api-glow)")
    .style("opacity", 0.9)
    .each(function (d) {
      // 添加内部小云朵装饰
      const parent = d3.select(this.parentNode);

      // 添加内部装饰小云朵
      parent
        .append("path")
        .attr("d", () => {
          const w = d.width * 0.4;
          const h = d.height * 0.4;
          const x = d.width * 0.3;
          const y = d.height * 0.3;

          return `
            M${x},${y + h * 0.5}
            C${x - h * 0.1},${y + h * 0.4} ${x - h * 0.1},${y + h * 0.2} ${
            x + h * 0.2
          },${y + h * 0.2}
            C${x + h * 0.2},${y + h * 0.05} ${x + h * 0.4},${y + h * 0.05} ${
            x + h * 0.5
          },${y + h * 0.15}
            C${x + h * 0.6},${y + h * 0.05} ${x + h * 0.7},${y + h * 0.1} ${
            x + h * 0.75
          },${y + h * 0.3}
            C${x + h * 0.8},${y + h * 0.2} ${x + h * 0.9},${y + h * 0.3} ${
            x + h * 0.8
          },${y + h * 0.5}
            Z
          `;
        })
        .style("fill", "#ffffff")
        .style("opacity", 0.3);
    });

  nodeEnter
    .filter((d) => d.type === "result-node")
    .append("rect")
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("width", (d) => d.width)
    .attr("height", (d) => d.height)
    .style("fill", "none")
    .style("stroke", (d) => d.color)
    .style("stroke-width", 2)
    .style("stroke-dasharray", "5,3");

  nodeEnter
    .filter((d) => ["specialized-agent", "info-process-agent"].includes(d.type))
    .append("rect")
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("width", (d) => d.width)
    .attr("height", (d) => d.height)
    .style("fill", (d) => d.color)
    .style("stroke", "#ffffff")
    .style("stroke-width", 2)
    .style("filter", "url(#glow)")
    .style("stroke-dasharray", "3,0");

  nodeEnter
    .filter(
      (d) =>
        ![
          "cloud-node",
          "result-node",
          "specialized-agent",
          "info-process-agent",
        ].includes(d.type)
    )
    .append("rect")
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("width", (d) => d.width)
    .attr("height", (d) => d.height)
    .style("fill", (d) => d.color)
    .style("stroke", "#ffffff")
    .style("stroke-width", 2)
    .style("filter", "url(#glow)");

  // 为所有节点添加文本标签，确保完全居中
  nodeEnter
    .append("text")
    .attr("class", "node-label")
    .attr("x", (d) => d.width / 2)
    .attr("y", (d) => d.height / 2)
    .style("text-anchor", "middle")
    .style("dominant-baseline", "central")
    .style("fill", (d) => (d.type === "result-node" ? d.color : "#ffffff"))
    .style("font-weight", "bold")
    .style("font-size", "12px")
    .style("pointer-events", "none")
    .each(function (d) {
      // 处理多行文本
      const text = d3.select(this);
      // 处理可能的换行符和空格
      const lines = d.name.split(/\n/).map((line) => line.trim());

      // 清除现有文本
      text.text(null);

      if (lines.length > 1) {
        // 如果有多行，分别添加每行
        const lineHeight = 1.1; // 行高
        const totalHeight = lineHeight * (lines.length - 1);

        lines.forEach((line, i) => {
          text
            .append("tspan")
            .attr("x", d.width / 2)
            .attr("dy", i === 0 ? -totalHeight / 2 + "em" : lineHeight + "em")
            .text(line);
        });
      } else if (d.name.length > 15) {
        // 如果单行文本过长，尝试按空格拆分
        const words = d.name.split(/\s+/).filter((w) => w.length > 0);

        if (words.length > 1) {
          // 将单词分成两行
          const midpoint = Math.ceil(words.length / 2);
          const line1 = words.slice(0, midpoint).join(" ");
          const line2 = words.slice(midpoint).join(" ");

          text
            .append("tspan")
            .attr("x", d.width / 2)
            .attr("dy", "-0.55em")
            .text(line1);

          text
            .append("tspan")
            .attr("x", d.width / 2)
            .attr("dy", "1.1em")
            .text(line2);
        } else {
          // 无法拆分，使用原文本
          text.text(d.name);
        }
      } else {
        // 正常单行文本
        text.text(d.name);
      }
    });

  // 更新节点位置
  node = nodeEnter.merge(node);
  node.attr("transform", (d) => `translate(${d.x}, ${d.y})`);
}

// 生成云形状路径
function generateCloudPath(width, height) {
  const w = width;
  const h = height;

  // 新的云朵形状，更圆润更大
  return `
    M${w * 0.2},${h * 0.5}
    C${w * 0.05},${h * 0.4} ${w * 0.05},${h * 0.15} ${w * 0.3},${h * 0.15}
    C${w * 0.35},${h * 0.0} ${w * 0.55},${h * 0.0} ${w * 0.65},${h * 0.15}
    C${w * 0.8},${h * 0.05} ${w * 0.9},${h * 0.1} ${w * 0.95},${h * 0.3}
    C${w * 1.1},${h * 0.3} ${w * 1.1},${h * 0.55} ${w * 0.95},${h * 0.65}
    C${w * 1.0},${h * 0.8} ${w * 0.9},${h * 0.95} ${w * 0.7},${h * 0.95}
    C${w * 0.6},${h * 1.0} ${w * 0.35},${h * 1.0} ${w * 0.25},${h * 0.85}
    C${w * 0.1},${h * 0.85} ${w * 0.0},${h * 0.65} ${w * 0.05},${h * 0.5}
    C${w * 0.0},${h * 0.4} ${w * 0.05},${h * 0.35} ${w * 0.2},${h * 0.5}
    Z
  `;
}

// 处理用户请求提交
function handleRequestSubmission() {
  const requestContent = document.getElementById("requestContent").value.trim();

  if (!requestContent) {
    addSystemMessage("请输入请求内容");
    return;
  }

  // 提取连续3位字母和3位数字的模式
  const extracted = extractKeyPatterns(requestContent);
  if (extracted.length > 0) {
    displayExtractedKeys(extracted);
    // 保存提取的key到key.txt
    saveExtractedKeys(extracted);
  }

  // 第一次用户交互时设置标志
  if (!userInteractionStarted) {
    userInteractionStarted = true;

    // 启动周期性模拟数据流
    setInterval(() => {
      simulateRandomDataFlow();
    }, 5000);

    // 添加连接成功的系统消息
    addSystemMessage("已连接到区块链多代理可视化系统");

    // 启动警报代理的定时请求
    startAlarmAgentTimer();
  }

  // 显示加载状态
  const responseLog = document.getElementById("responseLog");
  responseLog.innerHTML = '<div class="loading">正在处理请求...</div>';

  // 记录用户请求
  addUserMessage(requestContent);

  // 添加用户到中央代理的动画
  const userNode = agents.find((a) => a.id === "User");
  const centralNode = agents.find((a) => a.id === "CentralAgent");

  if (userNode && centralNode) {
    animateDataFlow(userNode, centralNode, "#ffeaa7");
  }

  // 发送请求到服务器
  fetch("/api/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: requestContent }),
  })
    .then((response) => response.json())
    .then((data) => {
      // 清除加载状态
      responseLog.innerHTML = "";

      // 处理响应
      if (data.error) {
        responseLog.innerHTML = `<div class="error">${data.error}</div>`;
      } else if (data.formatted_response) {
        responseLog.innerHTML = `<div class="response-content">${data.formatted_response}</div>`;
      } else {
        responseLog.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
      }

      // 让中央代理向其他代理发送消息的动画
      setTimeout(() => {
        const targetAgents = [
          "InfoProcessAgent",
          "AlarmAgent",
          "AutoTradeAgent",
          "DataCleanAgent",
        ];
        targetAgents.forEach((targetId) => {
          const targetNode = agents.find((a) => a.id === targetId);
          if (targetNode) {
            animateDataFlow(centralNode, targetNode, centralNode.color);
          }
        });
      }, 500);
    })
    .catch((error) => {
      responseLog.innerHTML = `<div class="error">请求处理失败: ${error.message}</div>`;
    });

  // 清空输入框
  document.getElementById("requestContent").value = "";
}

// 启动警报代理的定时请求
function startAlarmAgentTimer() {
  // 根据配置设置初始延迟
  setTimeout(() => {
    simulateAlarmAgentRequest();

    // 根据配置设置定时间隔
    alarmTimer = setInterval(() => {
      simulateAlarmAgentRequest();
    }, alarmConfig.interval);
  }, alarmConfig.initialDelay);

  console.log(
    `已启动Alarm Agent定时器，初始延迟: ${alarmConfig.initialDelay}ms，间隔: ${alarmConfig.interval}ms`
  );
}

// 模拟警报代理请求数据的过程
function simulateAlarmAgentRequest() {
  console.log("AlarmAgent 正在请求数据更新...");

  // 定义代理请求路径
  const requestPath = [
    {
      from: "AlarmAgent",
      to: "CentralAgent",
      delay: 0,
      message: "请求最新警报数据",
    },
    {
      from: "CentralAgent",
      to: "DataCleanAgent",
      delay: 1000,
      message: "获取最新处理数据",
    },
    {
      from: "DataCleanAgent",
      to: "InfoProcessAgent",
      delay: 1000,
      message: "请求新数据",
    },
    {
      from: "InfoProcessAgent",
      to: "API",
      delay: 1000,
      message: "调用API获取最新数据",
      type: "api_call",
    },
    {
      from: "API",
      to: "InfoProcessAgent",
      delay: 1500,
      message: "返回API数据",
      type: "api_response",
    },
  ];

  // 定义数据分发和汇总路径
  const processingPath = [
    {
      from: "InfoProcessAgent",
      to: "MultiAgents",
      delay: 1000,
      message: "分发数据处理任务",
    },
    {
      from: "MultiAgents",
      to: "CEXWithdrawAgent",
      delay: 500,
      message: "处理交易所提款数据",
    },
    {
      from: "MultiAgents",
      to: "WhaleAgent",
      delay: 700,
      message: "处理大额交易数据",
    },
    {
      from: "MultiAgents",
      to: "TxAgent",
      delay: 900,
      message: "处理交易频率数据",
    },
    {
      from: "MultiAgents",
      to: "ContractMonitorAgent",
      delay: 1100,
      message: "处理合约调用数据",
    },
    {
      from: "MultiAgents",
      to: "BasicInfoAgent",
      delay: 1300,
      message: "处理基础币种信息",
    },
  ];

  // 定义返回路径
  const responsePath = [
    {
      from: "MultiAgents",
      to: "DataCleanAgent",
      delay: 2500,
      message: "汇总处理结果",
    },
    {
      from: "DataCleanAgent",
      to: "CentralAgent",
      delay: 1000,
      message: "提交整合数据",
    },
    {
      from: "CentralAgent",
      to: "AlarmAgent",
      delay: 1000,
      message: "返回警报数据分析结果",
    },
  ];

  // 执行请求路径动画
  executePathAnimation(requestPath, () => {
    // 完成请求路径后，执行处理路径动画
    executePathAnimation(processingPath, () => {
      // 完成处理路径后，执行返回路径动画
      executePathAnimation(responsePath, () => {
        console.log("AlarmAgent 数据请求周期完成");
      });
    });
  });
}

// 执行路径动画
function executePathAnimation(path, callback) {
  let currentStep = 0;

  function executeNextStep() {
    if (currentStep >= path.length) {
      if (callback) callback();
      return;
    }

    const step = path[currentStep];
    currentStep++;

    const sourceNode = agents.find((a) => a.id === step.from);
    const targetNode = agents.find((a) => a.id === step.to);

    if (sourceNode && targetNode) {
      // 高亮源节点
      highlightAgentWithRedBorder(sourceNode);

      // 发送消息或调用API
      setTimeout(() => {
        // 高亮目标节点
        highlightAgentWithRedBorder(targetNode);

        // 显示消息流动
        const messageType = step.type || "message";
        const messageColor = getMessageColor(messageType);

        if (messageType === "message") {
          // 广播消息，通知其他客户端
          broadcast_interaction(
            step.from,
            step.to,
            step.message || "更新数据",
            messageType
          );
        }

        animateDataFlow(sourceNode, targetNode, messageColor);

        // 执行下一步
        setTimeout(executeNextStep, step.delay || 1000);
      }, 500);
    } else {
      console.error(`未找到节点: ${step.from} 或 ${step.to}`);
      setTimeout(executeNextStep, 500);
    }
  }

  // 开始执行第一步
  executeNextStep();
}

// 使用红色边框高亮代理
function highlightAgentWithRedBorder(node) {
  // 选择节点
  const nodeElement = d3.select(`#node-${node.id}`);

  // 添加红色边框高亮类
  nodeElement.classed("red-highlight", true);

  // 高亮效果 - 改变边框颜色和宽度
  nodeElement
    .select("rect, path")
    .transition()
    .duration(300)
    .style("stroke", "#ff3333")
    .style("stroke-width", 4)
    .transition()
    .duration(2000)
    .style("stroke", "#ffffff")
    .style("stroke-width", 2)
    .on("end", function () {
      // 动画结束后移除高亮类
      nodeElement.classed("red-highlight", false);
    });
}

// 模拟消息广播函数
function broadcast_interaction(source, target, content, type = "message") {
  // 可以在这里添加实际的WebSocket广播代码
  // 或者调用服务器端API记录交互
  // 这里我们仅在控制台记录
  console.log(`[${type}] ${source} → ${target}: ${content}`);

  // 在日志中添加交互记录
  displayInteraction({
    source: source,
    target: target,
    content: content,
    type: type,
    timestamp: Date.now() / 1000,
  });
}

// 处理交互
function processInteraction(interaction) {
  // 记录交互历史
  interactionHistory.push(interaction);

  // 在交互日志中显示
  displayInteraction(interaction);

  // 在图表上显示动画
  visualizeInteraction(interaction);

  // 将交互保存到history.txt
  saveInteractionToHistory(interaction);
}

// 将交互保存到history.txt
function saveInteractionToHistory(interaction) {
  // 生成消息ID和时间戳
  const timestamp = Date.now() / 1000;
  const messageId = `${Date.now()}${Math.floor(Math.random() * 10000)}`;

  // 构建MCP协议格式的消息
  const mcpMessage = {
    version: "1.0",
    protocol: "MCP",
    message_id: messageId,
    timestamp: timestamp,
    source: {
      agent_id: interaction.source,
      agent_type: getAgentType(interaction.source),
    },
    target: {
      agent_id: interaction.target,
      agent_type: getAgentType(interaction.target),
    },
    type: interaction.type || "message",
    content: interaction.content || interaction.message || "",
    metadata: {
      priority: "normal",
      processed: false,
      client_generated: true,
    },
  };

  // 发送到服务器保存
  fetch("/api/save_history", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(mcpMessage),
  }).catch((error) => {
    console.error("保存交互历史失败:", error);
  });
}

// 获取代理类型
function getAgentType(agentId) {
  const agentTypes = {
    CentralAgent: "central",
    InfoProcessAgent: "processor",
    MultiAgents: "dispatcher",
    DataCleanAgent: "data_cleaner",
    CEXWithdrawAgent: "specialist",
    WhaleAgent: "specialist",
    TxAgent: "specialist",
    ContractMonitorAgent: "specialist",
    BasicInfoAgent: "specialist",
    AlarmAgent: "notification",
    WalletAgent: "executor",
    CEXAgent: "executor",
    AutoTradeAgent: "executor",
    API: "external_service",
    BlockchainAPI: "external_service",
    LLMAPI: "external_service",
    System: "system",
    User: "user",
    Client: "user",
    ApprovalTx: "action",
    PlaceOrder: "action",
    MessageCall: "action",
  };

  // 特殊情况处理
  if (agentId === "API") return "external_service";
  if (agentId === "LLM") return "external_service";
  if (agentId.includes("InfoProcessAgent")) return "processor";
  if (agentId.includes("CentralAgent")) return "central";
  if (agentId.includes("DataCleanAgent")) return "data_cleaner";
  if (agentId.includes("UserAgent")) return "user";
  if (agentId.includes("CEXWithdrawAgent")) return "specialist";
  if (agentId.includes("SpecificCoinWhaleAgent")) return "specialist";
  if (agentId.includes("FreqTxAgent")) return "specialist";
  if (agentId.includes("ContractMonitorAgent")) return "specialist";
  if (agentId.includes("BasicCoinInfoAgent")) return "specialist";
  if (agentId.includes("AlarmAgent")) return "notification";
  if (agentId.includes("WalletAgent")) return "executor";
  if (agentId.includes("CEXAgent")) return "executor";
  if (agentId.includes("AutoTradeAgent")) return "executor";

  return agentTypes[agentId] || "unknown";
}

// 可视化交互
function visualizeInteraction(interaction) {
  try {
    // 获取源节点和目标节点
    const sourceId = getNodeIdFromAgentName(interaction.source);
    const targetId = getNodeIdFromAgentName(interaction.target);

    if (!sourceId || !targetId) {
      console.warn(
        "未找到源或目标节点:",
        interaction.source,
        interaction.target
      );
      return;
    }

    const sourceNode = agents.find((a) => a.id === sourceId);
    const targetNode = agents.find((a) => a.id === targetId);

    if (!sourceNode || !targetNode) {
      console.warn("未找到源或目标节点对象");
      return;
    }

    // 首先检查这两个节点之间是否有预定义的连接
    const hasConnection = predefinedConnections.some(
      (conn) =>
        (conn.source === sourceId && conn.target === targetId) ||
        (conn.source === targetId && conn.target === sourceId)
    );

    // 如果没有直接连接，则尝试找到一个中转节点
    if (!hasConnection) {
      console.log(
        `未找到 ${sourceId} 和 ${targetId} 之间的直接连接，尝试找到中转节点`
      );

      // 尝试通过中央代理作为中转
      const centralNode = agents.find((a) => a.id === "CentralAgent");
      if (centralNode) {
        // 检查源节点到中央节点是否有连接
        const sourceToCenter = predefinedConnections.some(
          (conn) =>
            (conn.source === sourceId && conn.target === "CentralAgent") ||
            (conn.source === "CentralAgent" && conn.target === sourceId)
        );

        // 检查目标节点到中央节点是否有连接
        const targetToCenter = predefinedConnections.some(
          (conn) =>
            (conn.source === targetId && conn.target === "CentralAgent") ||
            (conn.source === "CentralAgent" && conn.target === targetId)
        );

        // 如果都有连接，则通过中央节点中转
        if (sourceToCenter && targetToCenter) {
          const messageColor = getMessageColor(interaction.type);

          // 先从源节点到中央节点
          setTimeout(() => {
            if (isAlarmRelated(sourceNode) || isAlarmRelated(centralNode)) {
              highlightAgentBorder(sourceNode);
              highlightAgentBorder(centralNode);
            } else {
              animateDataFlow(sourceNode, centralNode, messageColor);
            }

            // 再从中央节点到目标节点
            setTimeout(() => {
              if (isAlarmRelated(centralNode) || isAlarmRelated(targetNode)) {
                highlightAgentBorder(centralNode);
                highlightAgentBorder(targetNode);
              } else {
                animateDataFlow(centralNode, targetNode, messageColor);
              }
            }, 500);
          }, 0);

          return;
        }
      }

      // 如果无法通过中央代理中转，则尝试通过其他节点
      const multiAgentsNode = agents.find((a) => a.id === "MultiAgents");
      if (multiAgentsNode) {
        // 检查源节点到MultiAgents是否有连接
        const sourceToMulti = predefinedConnections.some(
          (conn) =>
            (conn.source === sourceId && conn.target === "MultiAgents") ||
            (conn.source === "MultiAgents" && conn.target === sourceId)
        );

        // 检查目标节点到MultiAgents是否有连接
        const targetToMulti = predefinedConnections.some(
          (conn) =>
            (conn.source === targetId && conn.target === "MultiAgents") ||
            (conn.source === "MultiAgents" && conn.target === targetId)
        );

        // 如果都有连接，则通过MultiAgents中转
        if (sourceToMulti && targetToMulti) {
          const messageColor = getMessageColor(interaction.type);

          // 先从源节点到MultiAgents
          setTimeout(() => {
            if (isAlarmRelated(sourceNode) || isAlarmRelated(multiAgentsNode)) {
              highlightAgentBorder(sourceNode);
              highlightAgentBorder(multiAgentsNode);
            } else {
              animateDataFlow(sourceNode, multiAgentsNode, messageColor);
            }

            // 再从MultiAgents到目标节点
            setTimeout(() => {
              if (
                isAlarmRelated(multiAgentsNode) ||
                isAlarmRelated(targetNode)
              ) {
                highlightAgentBorder(multiAgentsNode);
                highlightAgentBorder(targetNode);
              } else {
                animateDataFlow(multiAgentsNode, targetNode, messageColor);
              }
            }, 500);
          }, 0);

          return;
        }
      }

      // 如果仍然没有找到合适的路径，则不显示动画，只记录日志
      console.warn(
        `无法找到从 ${sourceId} 到 ${targetId} 的连接路径，无法显示动画`
      );
      return;
    }

    // 获取消息颜色
    const messageColor = getMessageColor(interaction.type);

    // 检查是否与AlarmAgent相关
    if (isAlarmRelated(sourceNode) || isAlarmRelated(targetNode)) {
      // 对所有与警报相关的交互使用高亮效果
      highlightAgentBorder(sourceNode);
      highlightAgentBorder(targetNode);

      // 如果其中一个不是AlarmAgent，还需要高亮警报节点
      if (sourceNode.id !== "AlarmAgent" && targetNode.id !== "AlarmAgent") {
        const alarmNode = agents.find((a) => a.id === "AlarmAgent");
        if (alarmNode) {
          highlightAgentBorder(alarmNode);
        }
      }
    } else {
      // 其他关系依然使用数据流动画
      animateDataFlow(sourceNode, targetNode, messageColor);
    }
  } catch (e) {
    console.error("可视化交互失败:", e);
  }
}

// 动画展示数据流
function animateDataFlow(sourceNode, targetNode, color) {
  // 首先检查这两个节点之间是否有预定义的连接
  const hasConnection = predefinedConnections.some(
    (conn) =>
      (conn.source === sourceNode.id && conn.target === targetNode.id) ||
      (conn.source === targetNode.id && conn.target === sourceNode.id)
  );

  // 如果没有连接，则不显示动画
  if (!hasConnection) {
    console.log(
      `未找到 ${sourceNode.id} 和 ${targetNode.id} 之间的连接，不显示动画`
    );
    return;
  }

  // 为每个数据流创建唯一ID
  const flowId = `flow-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  // 创建一个消息组
  const messageGroup = svg.select("g.messages");

  // 计算路径
  const sourceX = sourceNode.x + sourceNode.width / 2;
  const sourceY = sourceNode.y + sourceNode.height / 2;
  const targetX = targetNode.x + targetNode.width / 2;
  const targetY = targetNode.y + targetNode.height / 2;

  // 计算控制点
  const dx = targetX - sourceX;
  const dy = targetY - sourceY;
  const dr = Math.sqrt(dx * dx + dy * dy) * 1.2; // 控制弧度

  // 创建路径
  const pathData = `M${sourceX},${sourceY}A${dr},${dr} 0 0,1 ${targetX},${targetY}`;

  // 添加不可见路径用于动画
  const path = messageGroup
    .append("path")
    .attr("id", flowId)
    .attr("d", pathData)
    .style("stroke", "none")
    .style("fill", "none");

  // 创建消息圆点
  const circle = messageGroup
    .append("circle")
    .attr("r", 4)
    .style("fill", color)
    .style("filter", "url(#glow)")
    .style("opacity", 0.8);

  // 获取路径总长度
  const pathLength = path.node().getTotalLength();

  // 添加到活动数据流列表
  activeDataFlows.push({
    id: flowId,
    path: path,
    circle: circle,
  });

  // 创建动画
  circle
    .transition()
    .duration(1000) // 动画时长
    .attrTween("transform", () => {
      return (t) => {
        // 获取路径上的点
        const point = path.node().getPointAtLength(t * pathLength);
        return `translate(${point.x}, ${point.y})`;
      };
    })
    .on("end", () => {
      // 动画结束时添加脉冲效果
      targetNode.pulse = messageGroup
        .append("circle")
        .attr("cx", targetX)
        .attr("cy", targetY)
        .attr("r", 0)
        .style("fill", color)
        .style("opacity", 0.6)
        .transition()
        .duration(600)
        .attr("r", 20)
        .style("opacity", 0)
        .on("end", function () {
          d3.select(this).remove();
        });

      // 移除路径和圆点
      path.remove();
      circle.remove();

      // 从活动数据流列表中移除
      activeDataFlows = activeDataFlows.filter((flow) => flow.id !== flowId);

      // 如果是API调用，模拟API响应
      if (targetNode.type === "cloud-node") {
        setTimeout(() => {
          animateDataFlow(targetNode, sourceNode, color);
        }, 500);
      }
    });
}

// 获取消息类型对应的颜色
function getMessageColor(type) {
  switch (type) {
    case "message":
      return "#3498db"; // 蓝色
    case "api_call":
      return "#e74c3c"; // 红色
    case "api_response":
      return "#2ecc71"; // 绿色
    case "system":
      return "#f39c12"; // 橙色
    default:
      return "#95a5a6"; // 灰色
  }
}

// 从代理名称获取节点ID
function getNodeIdFromAgentName(name) {
  // 处理特殊情况
  if (name === "API") return "BlockchainAPI";
  if (name === "LLM") return "LLMAPI";
  if (name === "System") return "User";
  if (name === "Client") return "User";

  // 处理常规代理
  if (name.includes("InfoProcessAgent")) return "InfoProcessAgent";
  if (name.includes("CentralAgent")) return "CentralAgent";
  if (name.includes("DataCleanAgent")) return "DataCleanAgent";
  if (name.includes("UserAgent")) return "User";
  if (name.includes("CEXWithdrawAgent")) return "CEXWithdrawAgent";
  if (name.includes("SpecificCoinWhaleAgent")) return "WhaleAgent";
  if (name.includes("FreqTxAgent")) return "TxAgent";
  if (name.includes("ContractMonitorAgent")) return "ContractMonitorAgent";
  if (name.includes("BasicCoinInfoAgent")) return "BasicInfoAgent";
  if (name.includes("AlarmAgent")) return "AlarmAgent";
  if (name.includes("WalletAgent")) return "WalletAgent";
  if (name.includes("CEXAgent")) return "CEXAgent";
  if (name.includes("AutoTradeAgent")) return "AutoTradeAgent";

  // 默认情况
  return null;
}

// 在日志中显示交互
function displayInteraction(interaction) {
  const interactionLog = document.getElementById("interactionLog");

  // 格式化时间戳
  const timestamp = new Date(interaction.timestamp * 1000).toLocaleTimeString(
    [],
    { hour: "2-digit", minute: "2-digit", second: "2-digit" }
  );

  // 创建交互元素
  const interactionElement = document.createElement("div");
  interactionElement.className = "system-message";

  // 添加数据属性，用于CSS选择器
  interactionElement.setAttribute("data-source", interaction.source);
  interactionElement.setAttribute("data-target", interaction.target);

  // 对于警报代理相关的消息，添加特殊样式
  if (
    interaction.source === "AlarmAgent" ||
    interaction.target === "AlarmAgent"
  ) {
    interactionElement.classList.add("alarm-related");
  }

  // 设置内容
  interactionElement.innerHTML = `
    <span class="timestamp">[${timestamp}]</span>
    <span class="source">${interaction.source}</span>
    <span class="direction">→</span>
    <span class="target">${interaction.target}</span>
    <span class="content">${interaction.content || "(system)"}</span>
    <button class="details-button">查看详情</button>
  `;

  // 添加到日志
  interactionLog.appendChild(interactionElement);
  interactionLog.scrollTop = interactionLog.scrollHeight;
}

// 添加系统消息
function addSystemMessage(message) {
  const interactionLog = document.getElementById("interactionLog");

  const timestamp = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  const messageElement = document.createElement("div");
  messageElement.className = "system-message";
  messageElement.innerHTML = `
        <span class="timestamp">[${timestamp}]</span>
        <span class="source">System</span>
        <span class="direction">→</span>
        <span class="target">Client</span>
        <span class="content">(system)</span>
    `;

  interactionLog.appendChild(messageElement);
  interactionLog.scrollTop = interactionLog.scrollHeight;
}

// 添加用户消息
function addUserMessage(message) {
  const interactionLog = document.getElementById("interactionLog");

  const timestamp = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  const messageElement = document.createElement("div");
  messageElement.className = "system-message";
  messageElement.innerHTML = `
        <span class="timestamp">[${timestamp}]</span>
        <span class="source">System</span>
        <span class="direction">→</span>
        <span class="target">User</span>
        <span class="content">(system)</span>
    `;

  interactionLog.appendChild(messageElement);
  interactionLog.scrollTop = interactionLog.scrollHeight;
}

// 加载交互历史
function loadInteractionHistory() {
  fetch("/api/get_messages")
    .then((response) => response.json())
    .then((data) => {
      // 处理消息历史
      const messages = data.messages || [];
      const apiCalls = data.api_calls || [];

      // 按时间合并排序
      const allInteractions = [...messages, ...apiCalls].sort(
        (a, b) => a.timestamp - b.timestamp
      );

      // 依次处理每个交互
      allInteractions.forEach((interaction) => {
        processInteraction(interaction);
      });
    })
    .catch((error) => {
      console.error("加载交互历史失败:", error);
      addSystemMessage("无法加载历史交互");
    });
}

// 重置视图
function resetView() {
  // 恢复原始位置
  agents.forEach((agent, i) => {
    agent.x = originalAgentPositions[i].x;
    agent.y = originalAgentPositions[i].y;
  });

  // 更新图表
  updateGraph();

  // 重置缩放
  const zoomIdentity = d3.zoomIdentity;
  svg.call(d3.zoom().transform, zoomIdentity);
}

// 添加高亮节点边框的函数
function highlightAgentBorder(node) {
  // 选择节点
  const nodeElement = d3.select(`#node-${node.id}`);

  // 添加高亮类
  nodeElement.classed("highlight", true);

  // 设置不同的高亮颜色和效果
  let highlightColor = "#ffcc00"; // 默认高亮颜色
  let pulseEffect = false; // 是否添加脉冲效果

  // 如果是Alarm节点或与Alarm相关，使用特殊的颜色
  if (node.id === "AlarmAgent") {
    highlightColor = "#fd79a8"; // 警报节点使用粉色
    pulseEffect = true;
  } else if (isAlarmRelated(node)) {
    highlightColor = "#ffcc00"; // 相关节点使用黄色
  }

  // 高亮效果 - 改变边框颜色和宽度
  nodeElement
    .select("rect, path")
    .transition()
    .duration(300)
    .style("stroke", highlightColor)
    .style("stroke-width", 4)
    .transition()
    .duration(1000)
    .style("stroke", "#ffffff")
    .style("stroke-width", 2)
    .on("end", function () {
      // 动画结束后移除高亮类
      nodeElement.classed("highlight", false);
    });

  // 如果是警报节点或需要脉冲效果，添加脉冲效果
  if (pulseEffect || node.id === "AlarmAgent") {
    // 创建一个临时的大圆表示波纹扩散
    const pulse = svg
      .select("g.messages")
      .append("circle")
      .attr("cx", node.x + node.width / 2)
      .attr("cy", node.y + node.height / 2)
      .attr("r", Math.max(node.width, node.height) / 2)
      .style("fill", "none")
      .style("stroke", "#fd79a8")
      .style("stroke-width", 2)
      .style("opacity", 0.8);

    // 动画：脉冲向外扩散并淡出
    pulse
      .transition()
      .duration(1500)
      .attr("r", Math.max(node.width, node.height) * 2)
      .style("stroke-width", 0.5)
      .style("opacity", 0)
      .on("end", function () {
        d3.select(this).remove();
      });
  }
}

// 提取连续3位字母和3位数字的模式
function extractKeyPatterns(text) {
  const pattern = /[A-Za-z]{3}|\d{3}/g;
  const matches = text.match(pattern) || [];
  return matches;
}

// 显示提取的结果
function displayExtractedKeys(keys) {
  const extractedKeyElement = document.getElementById("extractedKey");
  if (keys.length > 0) {
    extractedKeyElement.textContent = `提取字段：${keys.join(", ")}`;
    extractedKeyElement.classList.add("show");

    // 提取后自动调用合约
    callContractWithExtractedData();
  } else {
    extractedKeyElement.textContent = "";
    extractedKeyElement.classList.remove("show");
  }
}

// 保存提取的key到服务器
function saveExtractedKeys(keys) {
  if (keys.length === 0) return;

  fetch("/api/save_key", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ key: keys.join(", ") }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("保存key结果:", data);

      // 保存成功后调用合约
      if (data.success) {
        callContractWithExtractedData();
      }
    })
    .catch((error) => {
      console.error("保存key失败:", error);
    });
}

// 使用提取的数据调用合约
function callContractWithExtractedData() {
  // 如果已经有调用在进行中，则不执行
  if (contractCallInProgress) {
    console.log("合约调用已在进行中，请等待当前交易完成");
    return;
  }

  // 设置调用状态为进行中
  contractCallInProgress = true;

  // 显示调用合约的消息
  const responseLog = document.getElementById("responseLog");
  responseLog.innerHTML = '<div class="loading">正在准备调用合约...</div>';

  // 获取合约参数
  fetch("/api/call_contract", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}), // 后端会从key.txt读取数据
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        responseLog.innerHTML = `<div class="error">${data.error}</div>`;
        // 重置状态
        contractCallInProgress = false;
      } else if (data.success) {
        const contract = data.contract_call;

        // 显示合约调用准备信息
        const prepareHtml = `
          <div class="contract-result">
            <h3>合约调用准备中</h3>
            <div class="contract-details">
              <div class="contract-address">
                <div class="address-label">合约地址:</div>
                <div class="address-value">${contract.contract_address}</div>
              </div>
              <div class="token-exchange">
                <div class="token from-token">
                  <div class="token-symbol">${contract.from_token.symbol}</div>
                  <div class="token-amount">${contract.amount}</div>
                  <div class="token-address">${contract.from_token.address}</div>
                </div>
                <div class="exchange-arrow">→</div>
                <div class="token to-token">
                  <div class="token-symbol">${contract.to_token.symbol}</div>
                  <div class="token-address">${contract.to_token.address}</div>
                </div>
              </div>
              <div class="loading">正在请求钱包签名...</div>
            </div>
          </div>
        `;

        responseLog.innerHTML = prepareHtml;

        // 现在尝试进行实际的合约调用
        callBlockchainContract(contract)
          .then((txResult) => {
            // 交易成功
            const resultHtml = `
              <div class="contract-result">
                <h3>合约调用成功</h3>
                <div class="contract-details">
                  <div class="contract-address">
                    <div class="address-label">合约地址:</div>
                    <div class="address-value">${
                      contract.contract_address
                    }</div>
                  </div>
                  <div class="token-exchange">
                    <div class="token from-token">
                      <div class="token-symbol">${
                        contract.from_token.symbol
                      }</div>
                      <div class="token-amount">${contract.amount}</div>
                      <div class="token-address">${
                        contract.from_token.address
                      }</div>
                    </div>
                    <div class="exchange-arrow">→</div>
                    <div class="token to-token">
                      <div class="token-symbol">${
                        contract.to_token.symbol
                      }</div>
                      <div class="token-address">${
                        contract.to_token.address
                      }</div>
                    </div>
                  </div>
                  <div class="transaction-info">
                    <div class="tx-hash">交易哈希: ${
                      txResult.hash || contract.tx_hash
                    }</div>
                    ${
                      txResult.approveHash
                        ? `<div class="tx-approve-hash">授权交易哈希: ${txResult.approveHash}</div>`
                        : ""
                    }
                    <div class="tx-status">状态: ${
                      txResult.status || "completed"
                    }</div>
                    <div class="tx-timestamp">时间: ${new Date().toLocaleString()}</div>
                  </div>
                </div>
              </div>
            `;

            responseLog.innerHTML = resultHtml;
            // 重置状态
            contractCallInProgress = false;
          })
          .catch((error) => {
            // 显示错误信息
            responseLog.innerHTML = `
              <div class="contract-result">
                <h3>合约调用失败</h3>
                <div class="contract-details">
                  <div class="error">
                    <p>调用合约时出现错误:</p>
                    <p>${error.message || "用户拒绝交易或钱包未连接"}</p>
                  </div>
                  <div class="contract-address">
                    <div class="address-label">合约地址:</div>
                    <div class="address-value">${
                      contract.contract_address
                    }</div>
                  </div>
                </div>
              </div>
            `;
            // 重置状态
            contractCallInProgress = false;
          });
      } else {
        responseLog.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        // 重置状态
        contractCallInProgress = false;
      }
    })
    .catch((error) => {
      responseLog.innerHTML = `<div class="error">合约调用准备失败: ${error.message}</div>`;
      // 重置状态
      contractCallInProgress = false;
    });
}

// 实际调用区块链合约函数
async function callBlockchainContract(contractData) {
  return new Promise(async (resolve, reject) => {
    try {
      // 添加交易状态跟踪
      let transactionInProgress = false;

      // 检查是否可以通过父窗口获取钱包
      if (window.parentWalletProvider) {
        // 创建命名的消息处理函数，这样可以在完成后移除
        function messageHandler(event) {
          if (event.data.type === "CONTRACT_CALL_RESULT") {
            // 移除事件监听器，防止重复处理
            window.removeEventListener("message", messageHandler);

            // 重置交易状态
            transactionInProgress = false;

            if (event.data.success) {
              resolve({
                hash: event.data.txHash,
                status: event.data.status,
                approveHash: event.data.approveHash,
              });
            } else {
              reject(new Error(event.data.error || "合约调用失败"));
            }
          }
        }

        // 设置消息事件监听器，等待父窗口返回交易结果
        window.addEventListener("message", messageHandler);

        // 设置交易状态为进行中
        transactionInProgress = true;

        // 通过父窗口的钱包提供商调用合约
        window.parent.postMessage(
          {
            type: "CALL_CONTRACT",
            contractAddress: contractData.contract_address,
            fromToken: contractData.from_token.address,
            toToken: contractData.to_token.address,
            amount: contractData.amount,
            chainId: contractData.chain_id || 97, // 使用BSC测试网
            needApprove: true, // 标记需要先调用approve
            method: "swapTokens", // 指定调用的方法名
            checkAllowanceBeforeApprove: true, // 在approve前检查授权状态
          },
          "*"
        );

        // 如果父窗口10秒内没有响应，则使用模拟数据
        setTimeout(() => {
          // 只有在交易仍处于进行中时才执行
          if (transactionInProgress) {
            // 移除事件监听器
            window.removeEventListener("message", messageHandler);

            console.log("父窗口10秒内未响应，使用模拟数据");
            resolve({
              hash: contractData.tx_hash,
              status: "completed (simulated)",
            });
          }
        }, 10000);
      } else if (window.ethereum) {
        // 如果iframe本身有访问MetaMask的权限
        try {
          // 设置交易状态为进行中，防止重复调用
          if (transactionInProgress) {
            console.log("已有交易正在进行中，请等待当前交易完成");
            reject(new Error("已有交易正在进行中，请等待当前交易完成"));
            return;
          }

          transactionInProgress = true;

          const web3 = new Web3(window.ethereum);
          await window.ethereum.request({ method: "eth_requestAccounts" });

          // 检查当前链ID是否为BSC测试网
          const chainId = await web3.eth.getChainId();
          console.log(
            `当前链ID: ${chainId}, 目标链ID: ${contractData.chain_id || 97}`
          );

          // 如果不是BSC测试网，尝试切换网络
          if (chainId !== (contractData.chain_id || 97)) {
            try {
              // 尝试切换到BSC测试网
              await window.ethereum.request({
                method: "wallet_switchEthereumChain",
                params: [{ chainId: "0x61" }], // 0x61 是97的16进制表示
              });
              console.log("已切换到BSC测试网");
            } catch (switchError) {
              // 如果网络未添加，尝试添加BSC测试网
              if (switchError.code === 4902) {
                try {
                  await window.ethereum.request({
                    method: "wallet_addEthereumChain",
                    params: [
                      {
                        chainId: "0x61",
                        chainName: "BSC Testnet",
                        nativeCurrency: {
                          name: "BNB",
                          symbol: "BNB",
                          decimals: 18,
                        },
                        rpcUrls: [
                          "https://data-seed-prebsc-1-s1.binance.org:8545/",
                        ],
                        blockExplorerUrls: ["https://testnet.bscscan.com/"],
                      },
                    ],
                  });
                  console.log("已添加并切换到BSC测试网");
                } catch (addError) {
                  console.error("添加BSC测试网失败:", addError);
                  reject(
                    new Error("添加BSC测试网失败，请手动切换到BSC测试网后重试")
                  );
                  return;
                }
              } else {
                console.error("切换到BSC测试网失败:", switchError);
                reject(
                  new Error("切换到BSC测试网失败，请手动切换到BSC测试网后重试")
                );
                return;
              }
            }
          }

          // 获取用户账户
          const accounts = await web3.eth.getAccounts();
          const userAddress = accounts[0];

          // ERC20代币ABI（包含approve、balanceOf和allowance函数）
          const erc20ABI = [
            {
              constant: false,
              inputs: [
                { name: "spender", type: "address" },
                { name: "amount", type: "uint256" },
              ],
              name: "approve",
              outputs: [{ name: "", type: "bool" }],
              payable: false,
              stateMutability: "nonpayable",
              type: "function",
            },
            {
              constant: true,
              inputs: [{ name: "owner", type: "address" }],
              name: "balanceOf",
              outputs: [{ name: "", type: "uint256" }],
              payable: false,
              stateMutability: "view",
              type: "function",
            },
            {
              constant: true,
              inputs: [
                { name: "owner", type: "address" },
                { name: "spender", type: "address" },
              ],
              name: "allowance",
              outputs: [{ name: "", type: "uint256" }],
              payable: false,
              stateMutability: "view",
              type: "function",
            },
          ];

          // 创建TKA代币合约实例
          const fromTokenContract = new web3.eth.Contract(
            erc20ABI,
            contractData.from_token.address
          );

          // 检查代币余额
          const tokenBalance = await fromTokenContract.methods
            .balanceOf(userAddress)
            .call();
          const tokenBalanceInEther = web3.utils.fromWei(tokenBalance, "ether");
          console.log(
            `代币余额: ${tokenBalanceInEther} ${contractData.from_token.symbol}`
          );

          if (Number(tokenBalanceInEther) < contractData.amount) {
            reject(
              new Error(
                `代币余额不足。当前余额: ${tokenBalanceInEther} ${contractData.from_token.symbol}, 需要: ${contractData.amount} ${contractData.from_token.symbol}`
              )
            );
            return;
          }

          // 计算要授权的金额（加10%作为缓冲）
          const amountToApprove = web3.utils.toWei(
            (parseFloat(contractData.amount) * 1.1).toString(),
            "ether"
          );

          // 检查是否已经授权足够的代币
          console.log("检查代币授权状态...");
          const currentAllowance = await fromTokenContract.methods
            .allowance(userAddress, contractData.contract_address)
            .call();

          console.log(
            `当前授权额度: ${web3.utils.fromWei(currentAllowance, "ether")} ${
              contractData.from_token.symbol
            }`
          );

          // 更新UI状态
          const responseLog = document.getElementById("responseLog");

          // 声明变量用于存储approve交易的结果
          let approveResult;

          // 如果当前授权额度足够，则跳过approve步骤
          if (
            web3.utils
              .toBN(currentAllowance)
              .gte(web3.utils.toBN(amountToApprove))
          ) {
            console.log("已有足够授权，无需再次授权");

            // 更新UI状态显示已有授权
            responseLog.innerHTML = `
              <div class="contract-result">
                <h3>合约调用进行中</h3>
                <div class="contract-details">
                  <div class="loading">已有足够授权，正在调用swapTokens函数...</div>
                </div>
              </div>
            `;

            // 使用已有授权
            approveResult = { transactionHash: "使用已有授权" };
          } else {
            // 更新UI状态显示需要授权
            responseLog.innerHTML = `
              <div class="contract-result">
                <h3>合约调用进行中</h3>
                <div class="contract-details">
                  <div class="loading">正在请求代币授权...</div>
                </div>
              </div>
            `;

            console.log(
              `正在授权合约使用 ${contractData.amount} ${contractData.from_token.symbol}...`
            );

            // 调用approve函数授权合约使用代币
            try {
              approveResult = await fromTokenContract.methods
                .approve(contractData.contract_address, amountToApprove)
                .send({ from: userAddress });

              console.log("代币授权成功:", approveResult);

              // 更新UI状态显示授权成功
              responseLog.innerHTML = `
                <div class="contract-result">
                  <h3>合约调用进行中</h3>
                  <div class="contract-details">
                    <div class="loading">授权成功！正在调用swapTokens函数...</div>
                  </div>
                </div>
              `;
            } catch (approveError) {
              console.error("代币授权失败:", approveError);

              // 重置交易状态
              transactionInProgress = false;

              // 拒绝Promise并返回
              reject(new Error("代币授权失败: " + approveError.message));
              return;
            }
          }

          // 合约ABI（简化版，仅包含swapTokens函数）
          const swapABI = contractData.contract_abi || [
            {
              inputs: [
                { internalType: "address", name: "tokenA", type: "address" },
                { internalType: "address", name: "tokenB", type: "address" },
                { internalType: "uint256", name: "amount", type: "uint256" },
              ],
              name: "swapTokens",
              outputs: [{ internalType: "bool", name: "", type: "bool" }],
              stateMutability: "nonpayable",
              type: "function",
            },
          ];

          // 创建交换合约实例
          const swapContract = new web3.eth.Contract(
            swapABI,
            contractData.contract_address
          );

          // 调用swapTokens函数
          console.log(
            `正在调用合约 ${contractData.contract_address} 的swapTokens函数，交换 ${contractData.amount} ${contractData.from_token.symbol} 到 ${contractData.to_token.symbol}...`
          );

          // 直接使用Wei单位调用swapTokens函数
          try {
            // 转换为Wei单位
            const amountInWei = web3.utils.toWei(
              contractData.amount.toString(),
              "ether"
            );

            console.log("调用参数:", {
              tokenA: contractData.from_token.address,
              tokenB: contractData.to_token.address,
              amount: amountInWei,
            });

            const result = await swapContract.methods
              .swapTokens(
                contractData.from_token.address,
                contractData.to_token.address,
                amountInWei
              )
              .send({ from: userAddress });

            console.log("交换成功:", result);

            // 重置交易状态
            transactionInProgress = false;

            resolve({
              hash: result.transactionHash,
              status: "completed",
              approveHash: approveResult.transactionHash,
            });
          } catch (error) {
            console.error("调用swapTokens函数失败:", error);

            // 重置交易状态
            transactionInProgress = false;

            reject(new Error("交换失败: " + error.message));
          }
        } catch (error) {
          console.error("Web3调用合约失败:", error);

          // 重置交易状态
          transactionInProgress = false;

          reject(error);
        }
      } else {
        // 如果没有可用的钱包连接，则使用模拟数据
        console.log("未找到钱包连接，使用模拟数据");

        // 设置交易状态为进行中
        transactionInProgress = true;

        setTimeout(() => {
          // 重置交易状态
          transactionInProgress = false;

          resolve({
            hash: contractData.tx_hash,
            status: "completed (simulated)",
          });
        }, 2000);
      }
    } catch (error) {
      console.error("调用区块链合约失败:", error);
      reject(error);
    }
  });
}
