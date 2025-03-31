document.addEventListener('DOMContentLoaded', () => {
    // 增强渐变背景效果
    enhanceBackground();
    
    // 添加粒子效果
    initParticles();
    
    // 添加平滑滚动
    setupSmoothScroll();
    
    // 添加导航栏滚动效果
    setupNavScrollEffect();
    
    // 添加特性卡片悬停效果
    setupFeatureCards();
    
    // 添加区块链网络图标动画
    setupChainLogos();
    
    // 添加新的特性盒子交互效果
    setupFeatureBoxes();
    
    // 初始化钱包连接功能
    setupWalletConnection();
    
    // 添加日志以便排查问题
    console.log('页面加载完成，检查钱包连接状态:', {
        connected: localStorage.getItem('walletConnected'),
        walletType: localStorage.getItem('walletType'),
        address: localStorage.getItem('walletAddress')
    });

    const launchAppBtn = document.getElementById('launchAppBtn');
    if (launchAppBtn) {
        launchAppBtn.addEventListener('click', async () => {
            // 检查是否已连接钱包
            const walletConnected = localStorage.getItem('walletConnected') === 'true';
            
            if (!walletConnected) {
                // 未连接钱包，打开钱包模态框
                const walletModal = document.getElementById('walletModal');
                if (walletModal) {
                    walletModal.classList.add('show');
                }
                return;
            }
            
            try {
                showNotification('正在连接应用...', 'info');
                
                // 在这里可以添加实际的智能合约交互
                // 例如：
                const web3Instance = new Web3(provider);
                const accounts = await web3Instance.eth.getAccounts();
                const chainId = await web3Instance.eth.getChainId();
                
                showNotification(`成功连接到${getNetworkName(chainId)}上的应用`, 'success');
                
                // 这里可以添加跳转到应用页面的逻辑
                // window.location.href = 'app.html';
            } catch (error) {
                console.error('启动应用失败:', error);
                showNotification('启动应用失败: ' + error.message, 'error');
            }
        });
    }
});

/**
 * 增强背景效果，添加浮动元素
 */
function enhanceBackground() {
    const gradientBg = document.querySelector('.gradient-bg');
    const floatingElementsCount = 15;
    
    // 添加浮动元素样式
    const style = document.createElement('style');
    style.textContent = `
        .floating-element {
            position: absolute;
            border-radius: 50%;
            background: radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, transparent 70%);
            pointer-events: none;
            opacity: 0.3;
            z-index: -1;
        }
        
        @keyframes float {
            0% { transform: translate(0, 0) rotate(0deg); }
            25% { transform: translate(-10px, 10px) rotate(5deg); }
            50% { transform: translate(10px, 20px) rotate(0deg); }
            75% { transform: translate(20px, 10px) rotate(-5deg); }
            100% { transform: translate(0, 0) rotate(0deg); }
        }
    `;
    document.head.appendChild(style);
    
    // 创建浮动元素
    for (let i = 0; i < floatingElementsCount; i++) {
        const element = document.createElement('div');
        element.classList.add('floating-element');
        
        // 随机大小、位置和动画
        const size = Math.floor(Math.random() * 300) + 100; // 100-400px
        const posX = Math.random() * 100; // 0-100%
        const posY = Math.random() * 100; // 0-100%
        const duration = Math.floor(Math.random() * 30) + 20; // 20-50s
        const delay = Math.random() * 10; // 0-10s
        
        element.style.width = `${size}px`;
        element.style.height = `${size}px`;
        element.style.left = `${posX}%`;
        element.style.top = `${posY}%`;
        element.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
        
        gradientBg.appendChild(element);
    }
}

/**
 * 初始化粒子效果
 */
function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 设置canvas大小为窗口大小
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // 在窗口大小改变时重设canvas大小
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
    
    // 粒子配置
    const particlesArray = [];
    const numberOfParticles = Math.min(window.innerWidth / 20, 100); // 根据屏幕宽度调整数量
    const connectDistance = 150; // 线条连接距离
    
    // 设置粒子颜色主题 - 深蓝色系列
    const colors = [
        'rgba(26, 59, 102, 0.8)',   // 深蓝色
        'rgba(19, 44, 77, 0.8)',    // 中深蓝色
        'rgba(13, 30, 54, 0.8)',    // 藏蓝色
        'rgba(8, 19, 35, 0.8)',     // 极深蓝色
        'rgba(5, 12, 22, 0.8)',     // 近黑色深蓝
        'rgba(2, 6, 12, 0.8)',      // 近黑色
        'rgba(7, 16, 30, 0.8)'      // 深邃蓝色
    ];
    
    // 粒子类
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 3 + 1;
            this.speedX = Math.random() * 1 - 0.5;
            this.speedY = Math.random() * 1 - 0.5;
            
            // 根据位置决定颜色 - 左侧更多亮蓝色系
            if (this.x < canvas.width * 0.4) {
                // 左侧70%几率是亮蓝色系
                this.color = Math.random() < 0.7 ? 
                    colors[Math.floor(Math.random() * 3)] : // 亮蓝色系(前三个)
                    colors[Math.floor(Math.random() * colors.length)]; // 任意颜色
            } else {
                // 其他区域均匀分布各种颜色
                this.color = colors[Math.floor(Math.random() * colors.length)];
            }
            
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        
        // 更新粒子位置
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            // 边界检测，如果粒子超出画布，则从对面重新进入
            if (this.x > canvas.width) {
                this.x = 0;
                // 从左侧重新进入时，有更大几率变成亮蓝色系
                if (Math.random() < 0.7) {
                    this.color = colors[Math.floor(Math.random() * 3)]; // 亮蓝色系(前三个)
                }
            } else if (this.x < 0) {
                this.x = canvas.width;
            }
            
            if (this.y > canvas.height) {
                this.y = 0;
            } else if (this.y < 0) {
                this.y = canvas.height;
            }
        }
        
        // 绘制粒子
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color.replace('0.8', this.opacity);
            ctx.fill();
        }
    }
    
    // 创建粒子
    function createParticles() {
        for (let i = 0; i < numberOfParticles; i++) {
            particlesArray.push(new Particle());
        }
    }
    
    // 处理粒子
    function handleParticles() {
        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
            particlesArray[i].draw();
            
            // 创建粒子间连线
            for (let j = i; j < particlesArray.length; j++) {
                const dx = particlesArray[i].x - particlesArray[j].x;
                const dy = particlesArray[i].y - particlesArray[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < connectDistance) {
                    // 根据距离计算不透明度
                    const opacity = 1 - (distance / connectDistance);
                    
                    // 获取两个粒子的颜色
                    const color1 = particlesArray[i].color;
                    const color2 = particlesArray[j].color;
                    
                    // 计算线条渐变色
                    const gradient = ctx.createLinearGradient(
                        particlesArray[i].x, 
                        particlesArray[i].y, 
                        particlesArray[j].x, 
                        particlesArray[j].y
                    );
                    
                    gradient.addColorStop(0, color1.replace('0.8', opacity * 0.5));
                    gradient.addColorStop(1, color2.replace('0.8', opacity * 0.5));
                    
                    // 绘制连线
                    ctx.beginPath();
                    ctx.strokeStyle = gradient;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                    ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                    ctx.stroke();
                }
            }
        }
    }
    
    // 动画循环
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        handleParticles();
        requestAnimationFrame(animate);
    }
    
    // 鼠标交互
    const mouse = {
        x: undefined,
        y: undefined,
        radius: 100
    };
    
    canvas.addEventListener('mousemove', (e) => {
        mouse.x = e.x;
        mouse.y = e.y;
        
        // 添加鼠标附近粒子的交互效果
        for (let i = 0; i < particlesArray.length; i++) {
            const dx = mouse.x - particlesArray[i].x;
            const dy = mouse.y - particlesArray[i].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < mouse.radius) {
                const forceX = dx / 20; // 调整数值控制斥力大小
                const forceY = dy / 20;
                particlesArray[i].speedX -= forceX;
                particlesArray[i].speedY -= forceY;
            }
        }
    });
    
    // 初始化粒子并开始动画
    createParticles();
    animate();
}

/**
 * 平滑滚动设置
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * 导航栏滚动效果
 */
function setupNavScrollEffect() {
    const header = document.querySelector('.site-header');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // 向下滚动时收起导航栏，向上滚动时显示
        if (scrollTop > lastScrollTop && scrollTop > 80) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        // 滚动超过一定距离时改变导航栏背景
        if (scrollTop > 50) {
            header.style.background = 'rgba(13, 11, 33, 0.95)';
            header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        } else {
            header.style.background = 'rgba(13, 11, 33, 0.8)';
            header.style.boxShadow = 'none';
        }
        
        lastScrollTop = scrollTop;
    });
    
    // 添加平滑过渡效果
    header.style.transition = 'transform 0.3s ease, background 0.3s ease, box-shadow 0.3s ease';
}

/**
 * 特性卡片悬停效果
 */
function setupFeatureCards() {
    const cards = document.querySelectorAll('.feature-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; // x 鼠标相对于卡片的位置
            const y = e.clientY - rect.top; // y 鼠标相对于卡片的位置
            
            // 计算倾斜角度
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20; // 调整数字控制倾斜程度
            const rotateY = (centerX - x) / 20;
            
            // 应用3D变换
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', () => {
            // 重置变换
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0) scale(1)';
        });
    });
}

/**
 * 区块链网络图标动画
 */
function setupChainLogos() {
    const chainImgContainers = document.querySelectorAll('.chain-img-container');
    
    // 添加图标悬停发光效果
    chainImgContainers.forEach(container => {
        // 获取父元素
        const logoElement = container.closest('.chain-logo');
        
        container.addEventListener('mouseenter', function() {
            this.classList.add('glow');
            // 确保当前元素有额外空间，防止被裁剪
            if (logoElement) {
                // 添加样式类，而不是直接修改style属性
                logoElement.classList.add('hovered');
            }
        });
        
        container.addEventListener('mouseleave', function() {
            this.classList.remove('glow');
            if (logoElement) {
                logoElement.classList.remove('hovered');
            }
        });
    });
    
    // 无限滚动优化
    const scrollContainer = document.querySelector('.chain-logos-scroll');
    if (scrollContainer) {
        // 初始化时克隆第一个元素添加到末尾以实现无缝循环
        const setupContinuousScroll = () => {
            const logos = Array.from(scrollContainer.children);
            
            // 计算容器总宽度
            const totalWidth = logos.reduce((width, logo) => {
                return width + logo.offsetWidth + 
                    parseInt(getComputedStyle(logo).marginLeft) + 
                    parseInt(getComputedStyle(logo).marginRight);
            }, 0);
            
            // 设置动画时间 (调整为更快的速度)
            const totalLogoCount = 8; // 总共8个不同的网络标志
            const visibleLogoCount = 6; // 可视区域显示6个
            const baseScrollTime = 10; // 基础滚动时间，秒
            
            // 计算合适的动画时间
            const animationDuration = baseScrollTime * (totalLogoCount / visibleLogoCount);
            
            // 限制动画时间，确保速度适中
            const finalDuration = Math.min(12, Math.max(4, animationDuration));
            scrollContainer.style.animationDuration = `${finalDuration}s`;
            
            // 当动画结束时，瞬间重置位置
            scrollContainer.addEventListener('animationiteration', () => {
                // 重置到起始位置，无需用户感知
                scrollContainer.style.animationPlayState = 'running';
            });
        };
        
        // 页面加载后设置动画
        setupContinuousScroll();
        
        // 窗口大小改变时重新计算
        window.addEventListener('resize', setupContinuousScroll);
        
        // 鼠标交互：悬停时暂停，离开时继续
        const chainLogosContainer = document.querySelector('.chain-logos');
        if (chainLogosContainer) {
            chainLogosContainer.addEventListener('mouseenter', () => {
                scrollContainer.style.animationPlayState = 'paused';
            });
            
            chainLogosContainer.addEventListener('mouseleave', () => {
                scrollContainer.style.animationPlayState = 'running';
            });
        }
    }
}

/**
 * 创建倒计时效果（促销或新产品发布倒计时）
 */
function setupCountdown() {
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;
    
    // 设置结束时间 - 一周后
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 7);
    
    const countdownInterval = setInterval(() => {
        const now = new Date().getTime();
        const distance = endDate - now;
        
        if (distance < 0) {
            clearInterval(countdownInterval);
            countdownElement.innerHTML = "已发布!";
            return;
        }
        
        // 计算天、时、分、秒
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        countdownElement.innerHTML = `
            <div class="countdown-item">${days}<span>天</span></div>
            <div class="countdown-item">${hours}<span>时</span></div>
            <div class="countdown-item">${minutes}<span>分</span></div>
            <div class="countdown-item">${seconds}<span>秒</span></div>
        `;
    }, 1000);
}

/**
 * 设置特性卡片交互效果 - 增强版
 */
function setupFeatureBoxes() {
    const featureBoxes = document.querySelectorAll('.feature-box');
    
    featureBoxes.forEach(box => {
        // 添加悬停效果
        box.addEventListener('mouseenter', () => {
            const svg = box.querySelector('svg');
            const paths = svg.querySelectorAll('path');
            const circles = svg.querySelectorAll('circle');
            
            // 给SVG添加发光效果
            svg.style.filter = 'drop-shadow(0 0 8px rgba(255, 255, 255, 0.5))';
            
            // 让SVG暂停主旋转但内部元素产生微动画
            svg.style.animation = 'none';
            svg.style.transform = 'scale(1.1)';
            svg.style.transition = 'transform 0.4s ease, filter 0.4s ease';
            
            // 为路径添加动画效果
            paths.forEach((path, index) => {
                // 保存原始描边宽度
                const originalWidth = path.getAttribute('stroke-width') || '1';
                const originalDasharray = path.getAttribute('stroke-dasharray') || '';
                
                // 增加描边宽度
                path.style.strokeWidth = parseFloat(originalWidth) * 1.3;
                
                // 对虚线路径添加动画
                if (originalDasharray) {
                    path.style.strokeDashoffset = '0';
                    path.style.animation = `dashOffset 3s linear ${index * 0.1}s infinite`;
                }
                
                // 添加过渡效果
                path.style.transition = 'stroke-width 0.4s ease, opacity 0.4s ease';
                
                // 增加不透明度
                if (path.getAttribute('opacity')) {
                    path.style.opacity = Math.min(parseFloat(path.getAttribute('opacity')) * 1.5, 1);
                }
            });
            
            // 为圆圈添加脉冲效果
            circles.forEach((circle, index) => {
                circle.style.transform = 'scale(1.2)';
                circle.style.transformOrigin = 'center';
                circle.style.transition = 'transform 0.4s ease, opacity 0.4s ease';
                circle.style.animation = `pulse 2s ease-in-out ${index * 0.15}s infinite alternate`;
                
                // 增加亮度
                if (circle.getAttribute('fill') === '#fff') {
                    circle.style.filter = 'brightness(1.3)';
                }
            });
        });
        
        box.addEventListener('mouseleave', () => {
            const svg = box.querySelector('svg');
            const paths = svg.querySelectorAll('path');
            const circles = svg.querySelectorAll('circle');
            
            // 恢复SVG效果
            svg.style.filter = 'none';
            svg.style.animation = 'svgRotate 30s linear infinite';
            svg.style.transform = 'scale(1)';
            
            // 恢复路径效果
            paths.forEach(path => {
                path.style.strokeWidth = '';
                path.style.strokeDashoffset = '';
                path.style.animation = '';
                path.style.opacity = '';
                path.style.transition = '';
            });
            
            // 恢复圆圈效果
            circles.forEach(circle => {
                circle.style.transform = '';
                circle.style.transition = '';
                circle.style.animation = '';
                circle.style.filter = '';
            });
        });
    });
}

// 钱包连接功能 - 实际实现
function setupWalletConnection() {
    // DOM 元素
    const connectWalletBtn = document.getElementById('connectWalletBtn');
    const walletInfo = document.getElementById('walletInfo');
    const walletAddress = document.getElementById('walletAddress');
    const walletBalance = document.getElementById('walletBalance');
    const disconnectWalletBtn = document.getElementById('disconnectWalletBtn');
    
    // Web3实例
    let web3;
    let provider;
    let web3Modal;
    let currentAccount = null;
    
    // 初始化Web3Modal - 简化版，只需要基本功能
    function initWeb3Modal() {
        try {
            // 简化的provider配置，避免依赖WalletConnectProvider
            const providerOptions = {};
            
            if (typeof Web3Modal !== 'undefined') {
                web3Modal = new Web3Modal({
                    cacheProvider: true,
                    providerOptions,
                    theme: "dark"
                });
            } else {
                console.warn('Web3Modal 库未找到，将仅支持 MetaMask');
                web3Modal = null;
            }
        } catch (error) {
            console.error('初始化Web3Modal失败:', error);
            web3Modal = null;
        }
    }
    
    // 连接钱包 - 使用Web3Modal (非MetaMask钱包使用)
    async function connectWallet() {
        try {
            if (!web3Modal) {
                throw new Error('Web3Modal 未初始化');
            }
            
            // 打开Web3Modal
            provider = await web3Modal.connect();
            
            // 创建Web3实例
            web3 = new Web3(provider);
            
            // 获取连接的账户
            const accounts = await web3.eth.getAccounts();
            currentAccount = accounts[0];
            
            // 获取账户余额
            const balanceWei = await web3.eth.getBalance(currentAccount);
            const balanceEth = web3.utils.fromWei(balanceWei, 'ether');
            
            // 保存到本地存储
            localStorage.setItem('walletConnected', 'true');
            
            // 保存钱包类型 - 确保设置正确的钱包类型
            if (window.ethereum && window.ethereum.isMetaMask) {
                localStorage.setItem('walletType', 'metamask');
            } else {
                localStorage.setItem('walletType', 'walletconnect');
            }
            
            // 更新UI
            updateWalletUI(currentAccount, parseFloat(balanceEth).toFixed(4));
            
            // 显示钱包信息
            connectWalletBtn.style.display = 'none';
            walletInfo.style.display = 'flex';
            
            // 添加连接成功消息
            showNotification('钱包连接成功', 'success');
            
            // 监听账户变化
            setupAccountsChangedListener();
            
            return {
                address: currentAccount,
                balance: balanceEth
            };
        } catch (error) {
            console.error('连接钱包失败:', error);
            showNotification('钱包连接失败: ' + (error.message || '未知错误'), 'error');
            throw error;
        }
    }
    
    // 直接连接MetaMask - 不通过Web3Modal
    async function connectMetaMask() {
        console.log('尝试连接MetaMask...');
        
        // 检查是否安装了MetaMask
        if (typeof window.ethereum === 'undefined') {
            alert('未检测到MetaMask。请安装MetaMask扩展程序');
            window.open('https://metamask.io/download/', '_blank');
            return;
        }
        
        // 检查是否是MetaMask
        if (window.ethereum.isMetaMask) {
            // 请求账户授权
            window.ethereum.request({
                method: 'eth_requestAccounts'
            })
            .then(accounts => {
                if (accounts && accounts.length > 0) {
                    const account = accounts[0];
                    console.log('成功连接账户:', account);
                    
                    // 创建Web3实例以便获取余额
                    web3 = new Web3(window.ethereum);
                    
                    // 获取账户余额
                    web3.eth.getBalance(account).then(balanceWei => {
                        const balanceEth = web3.utils.fromWei(balanceWei, 'ether');
                        
                        // 显示地址的前几位和后几位
                        const shortAddress = account.substring(0, 6) + '...' + account.substring(account.length - 4);
                        
                        // 保存连接状态
                        localStorage.setItem('walletConnected', 'true');
                        localStorage.setItem('walletType', 'metamask');
                        localStorage.setItem('walletAddress', account);
                        
                        // 更新当前账户
                        currentAccount = account;
                        
                        // 更新界面
                        connectWalletBtn.style.display = 'none';
                        walletInfo.style.display = 'flex';
                        updateWalletUI(account, parseFloat(balanceEth).toFixed(4));
                        
                        // 显示成功消息
                        showNotification(`成功连接到钱包: ${shortAddress}`, 'success');
                        
                        // 设置监听器
                        setupMetamaskListeners();
                    }).catch(error => {
                        console.error('获取余额失败:', error);
                    });
                }
            })
            .catch(error => {
                console.error('MetaMask连接错误:', error);
                
                if (error.code === 4001) {
                    // 用户拒绝连接
                    showNotification('您拒绝了连接请求，请在MetaMask中允许连接', 'error');
                } else {
                    // 其他错误，可能需要用户手动操作
                    showNotification('连接出错，请手动点击浏览器右上角的MetaMask图标并连接', 'error');
                }
            });
        } else {
            showNotification('检测到的钱包不是MetaMask，请确保已安装MetaMask', 'error');
        }
    }
    
    // 断开钱包连接
    async function disconnectWallet() {
        if (provider && provider.close) {
            await provider.close();
        }
        
        // 清除缓存
        if (web3Modal) {
            web3Modal.clearCachedProvider();
        }
        
        // 清除本地存储
        localStorage.removeItem('walletConnected');
        localStorage.removeItem('walletType');
        
        // 重置状态变量
        currentAccount = null;
        web3 = null;
        
        // 更新UI
        connectWalletBtn.style.display = 'block';
        walletInfo.style.display = 'none';
        
        // 清除区块链信息更新定时器
        if (window.blockchainInfoInterval) {
            clearInterval(window.blockchainInfoInterval);
            window.blockchainInfoInterval = null;
        }
    }
    
    // 更新钱包UI
    function updateWalletUI(address, balance) {
        if (!walletAddress || !walletBalance) {
            console.error('钱包UI元素未找到');
            return;
        }
        
        // 显示地址的前6位和后4位
        const shortAddress = address.substring(0, 6) + '...' + address.substring(address.length - 4);
        walletAddress.textContent = shortAddress;
        walletBalance.textContent = `${balance} ETH`;
        
        // 详细信息面板功能已移除
    }
    
    // 新增：更新区块链信息 - 整个函数已不需要，但保留函数定义以避免调用错误
    async function updateBlockchainInfo() {
        // 详细信息面板功能已移除
    }
    
    // 设置 MetaMask 特定的事件监听器
    function setupMetamaskListeners() {
        if (window.ethereum) {
            // 账户变更监听
            window.ethereum.on('accountsChanged', async (accounts) => {
                if (accounts.length === 0) {
                    // 用户断开了连接
                    await disconnectWallet();
                    showNotification('MetaMask 已断开连接', 'info');
                } else {
                    // 账户已切换
                    currentAccount = accounts[0];
                    
                    // 获取新账户余额
                    const balanceWei = await web3.eth.getBalance(currentAccount);
                    const balanceEth = web3.utils.fromWei(balanceWei, 'ether');
                    
                    // 更新UI
                    updateWalletUI(currentAccount, parseFloat(balanceEth).toFixed(4));
                    
                    showNotification('MetaMask 账户已切换', 'info');
                }
            });
            
            // 链变更监听
            window.ethereum.on('chainChanged', (chainId) => {
                // 刷新页面以适应新的网络
                window.location.reload();
            });
            
            // 连接状态变更监听
            window.ethereum.on('connect', (connectInfo) => {
                try {
                    showNotification(`已连接到链 ID: ${parseInt(connectInfo.chainId)}`, 'success');
                } catch (error) {
                    console.error('连接事件处理错误:', error);
                }
            });
            
            // 断开连接监听
            window.ethereum.on('disconnect', (error) => {
                disconnectWallet();
                showNotification('MetaMask 连接已断开', 'info');
            });
        }
    }
    
    // 设置账户变化监听器 - 用于非MetaMask钱包
    function setupAccountsChangedListener() {
        if (provider && provider.on) {
            // 账户变化监听
            provider.on("accountsChanged", async (accounts) => {
                if (accounts.length === 0) {
                    // 用户断开了连接
                    await disconnectWallet();
                    showNotification('钱包已断开连接', 'info');
                } else {
                    // 账户已切换
                    currentAccount = accounts[0];
                    
                    // 获取新账户余额
                    const balanceWei = await web3.eth.getBalance(currentAccount);
                    const balanceEth = web3.utils.fromWei(balanceWei, 'ether');
                    
                    // 更新UI
                    updateWalletUI(currentAccount, parseFloat(balanceEth).toFixed(4));
                    
                    showNotification('已切换账户', 'info');
                }
            });
            
            // 链变化监听
            provider.on("chainChanged", (chainId) => {
                // 页面刷新以适应新的链
                window.location.reload();
            });
            
            // 断开连接监听
            provider.on("disconnect", async (error) => {
                await disconnectWallet();
                showNotification('钱包已断开连接', 'info');
            });
        }
    }
    
    // 检查是否已连接钱包（页面加载时）
    async function checkWalletConnection() {
        const walletType = localStorage.getItem('walletType');
        
        if (walletType === 'metamask' && window.ethereum) {
            try {
                // 检查MetaMask是否已经连接
                const accounts = await ethereum.request({ method: 'eth_accounts' });
                if (accounts.length > 0) {
                    await connectMetaMask();
                } else {
                    localStorage.removeItem('walletConnected');
                }
            } catch (error) {
                console.error('MetaMask自动连接失败:', error);
                localStorage.removeItem('walletConnected');
            }
        } else if (web3Modal && web3Modal.cachedProvider) {
            try {
                await connectWallet();
            } catch (error) {
                console.error('自动连接失败:', error);
                localStorage.removeItem('walletConnected');
            }
        }
    }
    
    // 创建钱包选择模态框
    const modalHtml = `
        <div id="walletModal" class="wallet-modal">
            <div class="wallet-modal-content">
                <div class="wallet-modal-header">
                    <h3 class="wallet-modal-title">连接钱包</h3>
                    <button class="wallet-modal-close">&times;</button>
                </div>
                <div class="wallet-list">
                    <div class="wallet-option" data-wallet="metamask">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/3/36/MetaMask_Fox.svg" alt="MetaMask" class="wallet-icon">
                        <span class="wallet-name">MetaMask</span>
                    </div>
                    <div class="wallet-option" data-wallet="walletconnect">
                        <img src="https://1000logos.net/wp-content/uploads/2022/05/WalletConnect-Logo.jpg" alt="WalletConnect" class="wallet-icon">
                        <span class="wallet-name">WalletConnect</span>
                    </div>
                    <div class="wallet-option" data-wallet="coinbase">
                        <img src="https://play-lh.googleusercontent.com/PjoJoG27miSglVBXoXrxBSLveV6e3EeBPpNY55aiUUBM9Q1RCETKCOqdOkX2ZydqVf0" alt="Coinbase Wallet" class="wallet-icon">
                        <span class="wallet-name">Coinbase 钱包</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 将模态框添加到body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 获取模态框元素
    const walletModal = document.getElementById('walletModal');
    const closeModalBtn = walletModal.querySelector('.wallet-modal-close');
    const walletOptions = walletModal.querySelectorAll('.wallet-option:not(.disabled)');
    
    // 打开钱包模态框
    connectWalletBtn.addEventListener('click', () => {
        walletModal.classList.add('show');
    });
    
    // 关闭钱包模态框
    closeModalBtn.addEventListener('click', () => {
        walletModal.classList.remove('show');
    });
    
    // 点击模态框外部关闭
    walletModal.addEventListener('click', (e) => {
        if (e.target === walletModal) {
            walletModal.classList.remove('show');
        }
    });
    
    // 新增：显示MetaMask连接引导
    function showMetaMaskGuidance() {
        // 创建引导框
        const guidanceWrapper = document.createElement('div');
        guidanceWrapper.className = 'metamask-guidance';
        guidanceWrapper.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
        
        // 创建内容
        const guidanceContent = document.createElement('div');
        guidanceContent.style.cssText = `
            background: #0d2b45;
            border: 1px solid #1a4a7c;
            border-radius: 12px;
            width: 90%;
            max-width: 500px;
            padding: 2rem;
            color: white;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            font-family: 'Inter', sans-serif;
        `;
        
        // 检查是否已安装MetaMask (更全面的检测)
        // 由于即使安装了MetaMask，有时候window.ethereum也可能为undefined
        // 所以这里使用更多指标来检测
        const isMetaMaskInstalled = 
            (typeof window.ethereum !== 'undefined') || 
            (typeof window.web3 !== 'undefined') || 
            document.querySelector('head > meta[name="ethereum-dapp-url"]') !== null ||
            !!window.ethereum;
        
        // 添加引导内容 - 无论是否检测到已安装MetaMask，都显示连接指南
        guidanceContent.innerHTML = `
            <h2 style="margin-top: 0; color: white; font-size: 1.5rem; font-weight: 600;">连接 MetaMask</h2>
            <p style="margin: 1rem 0; line-height: 1.6; font-size: 1rem;">请按照以下步骤连接您的MetaMask钱包：</p>
            <ol style="margin: 1.5rem 0; padding-left: 1.5rem; line-height: 1.8; font-size: 1rem;">
                <li>检查Chrome浏览器右上角的扩展图标区域</li>
                <li>找到并点击MetaMask图标 <img src="https://upload.wikimedia.org/wikipedia/commons/3/36/MetaMask_Fox.svg" style="height: 20px; vertical-align: middle; display: inline-block;"></li>
                <li>如果没有看到MetaMask图标，点击扩展菜单(拼图图标)，找到并固定MetaMask</li>
                <li>如果MetaMask已锁定，请输入密码解锁</li>
                <li>在MetaMask中，点击底部的"连接"或"连接到此网站"按钮</li>
                <li>连接成功后，关闭此窗口并刷新页面</li>
            </ol>
            
            <div style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
                <details style="margin-bottom: 1rem;">
                    <summary style="cursor: pointer; color: #4da3ff; margin-bottom: 0.5rem;">MetaMask 连接常见问题</summary>
                    <div style="padding: 0.5rem 0; font-size: 0.9rem;">
                        <p style="margin: 0.5rem 0;"><strong>问题 1: 我已安装MetaMask但网站无法检测到</strong><br>
                        解决方案: 请确保MetaMask已解锁，尝试刷新页面，或在MetaMask中手动添加此网站。</p>
                        
                        <p style="margin: 0.5rem 0;"><strong>问题 2: 点击连接后没有反应</strong><br>
                        解决方案: 检查MetaMask弹窗是否被浏览器阻止，点击地址栏右侧的图标允许弹窗。</p>
                        
                        <p style="margin: 0.5rem 0;"><strong>问题 3: 连接请求被阻止</strong><br>
                        解决方案: 在Chrome设置中允许此网站的弹出窗口，或直接在MetaMask扩展中添加连接。</p>
                    </div>
                </details>
            </div>
            
            <div style="margin-top: 2rem; text-align: center;">
                <button id="guidanceCloseBtn" style="background: #1a4a7c; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-size: 1rem; cursor: pointer;">关闭指南</button>
                <button id="guidanceRefreshBtn" style="background: #1d3043; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-size: 1rem; margin-left: 1rem; cursor: pointer;">刷新页面</button>
                <button id="guidanceManualConnectBtn" style="background: #1a7c4a; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-size: 1rem; margin-left: 1rem; cursor: pointer;">尝试重新连接</button>
            </div>
        `;
        
        // 添加到DOM
        guidanceWrapper.appendChild(guidanceContent);
        document.body.appendChild(guidanceWrapper);
        
        // 添加事件监听
        document.getElementById('guidanceCloseBtn').addEventListener('click', () => {
            document.body.removeChild(guidanceWrapper);
        });
        
        document.getElementById('guidanceRefreshBtn').addEventListener('click', () => {
            window.location.reload();
        });
        
        document.getElementById('guidanceManualConnectBtn').addEventListener('click', () => {
            // 尝试通过简单方式再次连接
            if (window.ethereum) {
                simpleConnectMetaMask();
                // 连接尝试后关闭指南
                setTimeout(() => {
                    try {
                        document.body.removeChild(guidanceWrapper);
                    } catch(e) {}
                }, 1000);
            } else {
                alert('无法检测到MetaMask，请确保您已安装并解锁MetaMask扩展');
            }
        });
    }

    // 修改钱包选项点击事件中的MetaMask处理
    walletOptions.forEach(option => {
        option.addEventListener('click', async () => {
            const walletType = option.getAttribute('data-wallet');
            
            try {
                // 关闭模态框
                walletModal.classList.remove('show');
                
                if (walletType === 'metamask') {
                    console.log('选择了MetaMask钱包');
                    
                    // 简化处理：直接尝试连接或显示引导
                    if (typeof window.ethereum !== 'undefined') {
                        // 使用简化的连接方法
                        simpleConnectMetaMask();
                    } else {
                        // 直接显示引导
                        showMetaMaskGuidance();
                    }
                } else {
                    // 其他钱包类型使用Web3Modal
                    if (!web3Modal) {
                        showNotification('不支持该钱包类型，请选择MetaMask', 'warning');
                        return;
                    }
                    await connectWallet();
                }
            } catch (error) {
                console.error('连接钱包失败:', error);
                showNotification('连接钱包失败: ' + error.message, 'error');
            }
        });
    });
    
    // 断开钱包连接按钮事件
    disconnectWalletBtn.addEventListener('click', async (e) => {
        e.stopPropagation(); // 防止触发父元素的hover事件
        await disconnectWallet();
        showNotification('钱包已断开连接', 'info');
    });
    
    // 初始化
    initWeb3Modal();
    
    // 检查是否已有连接的钱包
    if (localStorage.getItem('walletConnected') === 'true') {
        console.log('检测到已保存的钱包连接状态，尝试自动连接...');
        checkWalletConnection();
    }

    // 在setupWalletConnection函数内添加网络选择处理
    function setupNetworkSelector() {
        const networkSelector = document.getElementById('networkSelector');
        if (!networkSelector) return;
        
        // 根据当前连接的网络ID更新选择器
        async function updateNetworkSelector() {
            if (!web3) return;
            
            try {
                const chainId = await web3.eth.getChainId();
                networkSelector.value = chainId.toString();
                
                // 根据链ID更新余额单位
                updateBalanceUnit(chainId);
            } catch (error) {
                console.error("获取链ID失败:", error);
            }
        }
        
        // 更新余额单位
        function updateBalanceUnit(chainId) {
            const balanceText = walletBalance.textContent;
            const balanceValue = balanceText.split(' ')[0];
            
            let unit = 'ETH';
            if (chainId == 56) unit = 'BNB';
            else if (chainId == 137) unit = 'MATIC';
            else if (chainId == 43114) unit = 'AVAX';
            
            walletBalance.textContent = `${balanceValue} ${unit}`;
        }
        
        // 监听网络选择变化
        networkSelector.addEventListener('change', async () => {
            const newChainId = parseInt(networkSelector.value);
            
            // 如果没有连接钱包，提示用户
            if (!web3 || !currentAccount) {
                showNotification('请先连接钱包', 'warning');
                return;
            }
            
            const success = await switchNetwork(newChainId);
            if (success) {
                showNotification(`已切换到${getNetworkName(newChainId)}`, 'success');
            } else {
                // 切换失败，恢复之前的选择
                updateNetworkSelector();
                showNotification('网络切换失败', 'error');
            }
        });
        
        // 初始化时更新网络选择器
        if (web3) {
            updateNetworkSelector();
        }
        
        // 当钱包连接状态改变时更新网络选择器
        return updateNetworkSelector;
    }

    // 获取网络名称
    function getNetworkName(chainId) {
        const networks = {
            1: '以太坊主网',
            56: '币安智能链',
            137: 'Polygon',
            42161: 'Arbitrum',
            10: 'Optimism',
            43114: 'Avalanche'
        };
        
        return networks[chainId] || '未知网络';
    }

    // 新增：尝试简单方式连接MetaMask
    function simpleConnectMetaMask() {
        console.log('尝试最简方式连接MetaMask...');
        
        // 检测MetaMask的多种方式
        const hasEthereum = typeof window.ethereum !== 'undefined';
        const hasWeb3 = typeof window.web3 !== 'undefined';
        
        console.log('检测结果:', { hasEthereum, hasWeb3 });
        
        // 如果检测到任何一种MetaMask存在的迹象
        if (hasEthereum || hasWeb3) {
            try {
                console.log('找到以太坊提供者，尝试连接...');
                
                // 获取正确的提供者
                const provider = window.ethereum || window.web3?.currentProvider;
                
                if (provider) {
                    console.log('使用检测到的提供者连接...');
                    
                    // 尝试激活MetaMask弹窗
                    try {
                        // 使用不同方法尝试连接
                        if (provider.request) {
                            // 标准EIP-1193方法
                            provider.request({ method: 'eth_requestAccounts' })
                                .then(accounts => {
                                    if (accounts && accounts.length > 0) {
                                        console.log('成功连接账户:', accounts[0]);
                                        showSuccessAndReload(accounts[0]);
                                    }
                                })
                                .catch(err => {
                                    console.error('连接请求被拒绝:', err);
                                    // 当连接被拒绝时，引导用户手动操作
                                    alert('请在MetaMask弹窗中点击"连接"按钮，如果没有看到弹窗，请点击浏览器右上角的MetaMask图标，然后连接此网站。');
                                });
                            
                            return true;
                        } 
                        else if (provider.enable) {
                            // 旧版方法
                            provider.enable()
                                .then(accounts => {
                                    if (accounts && accounts.length > 0) {
                                        console.log('通过enable方法成功连接:', accounts[0]);
                                        showSuccessAndReload(accounts[0]);
                                    }
                                })
                                .catch(err => {
                                    console.error('enable方法连接失败:', err);
                                });
                                
                            return true;
                        }
                        else if (window.web3?.eth?.requestAccounts) {
                            // 尝试使用web3.js
                            window.web3.eth.requestAccounts()
                                .then(accounts => {
                                    console.log('通过web3.eth成功连接:', accounts[0]);
                                    showSuccessAndReload(accounts[0]);
                                })
                                .catch(err => console.error('web3.eth连接失败:', err));
                                
                            return true;
                        }
                    } catch (mainError) {
                        console.error('主要连接方法失败:', mainError);
                    }
                    
                    // 如果上述方法都失败，则提示用户手动连接
                    setTimeout(() => {
                        // 提示用户手动打开MetaMask
                        alert('自动连接失败。请手动打开MetaMask扩展并连接此网站。');
                    }, 500);
                    
                    return false;
                }
            } catch (error) {
                console.error('连接过程中出错:', error);
            }
        }
        
        // 如果未检测到MetaMask
        console.log('未检测到MetaMask或其他Web3提供者');
        showMetaMaskGuidance();
        return false;
        
        // 内部函数：显示成功并重载页面
        function showSuccessAndReload(address) {
            // 保存连接状态
            localStorage.setItem('walletConnected', 'true');
            localStorage.setItem('walletType', 'metamask');
            localStorage.setItem('walletAddress', address);
            
            // 创建Web3实例以便获取余额
            try {
                if (!web3 && window.ethereum) {
                    web3 = new Web3(window.ethereum);
                    
                    // 获取并显示余额
                    web3.eth.getBalance(address).then(balanceWei => {
                        const balanceEth = web3.utils.fromWei(balanceWei, 'ether');
                        
                        // 更新当前账户
                        currentAccount = address;
                        
                        // 更新界面
                        connectWalletBtn.style.display = 'none';
                        walletInfo.style.display = 'flex';
                        updateWalletUI(address, parseFloat(balanceEth).toFixed(4));
                        
                        // 设置监听器
                        setupMetamaskListeners();
                        
                        // 显示成功提示
                        showNotification(`已成功连接到钱包: ${address.substring(0, 6)}...${address.substring(address.length - 4)}`, 'success');
                    }).catch(err => {
                        console.error('获取余额失败:', err);
                        // 如果获取余额失败，仍然刷新页面
                        reloadPage();
                    });
                } else {
                    // 无法创建Web3实例，刷新页面
                    reloadPage();
                }
            } catch (error) {
                console.error('在连接后创建Web3实例失败:', error);
                // 出错则刷新页面
                reloadPage();
            }
            
            // 辅助函数：刷新页面
            function reloadPage() {
                // 显示成功提示
                showNotification(`已成功连接到钱包: ${address.substring(0, 6)}...${address.substring(address.length - 4)}`, 'success');
                // 1秒后刷新页面
                setTimeout(() => window.location.reload(), 1000);
            }
        }
    }
}

// 显示通知消息
function showNotification(message, type = 'info') {
    // 创建通知容器（如果不存在）
    let notificationContainer = document.querySelector('.notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
        
        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 300px;
            }
            
            .notification {
                padding: 12px 16px;
                border-radius: 8px;
                color: white;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                animation: slideIn 0.3s ease forwards, fadeOut 0.5s ease 4.5s forwards;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .notification.success {
                background: rgba(25, 135, 84, 0.85);
                border-left: 4px solid #198754;
            }
            
            .notification.error {
                background: rgba(220, 53, 69, 0.85);
                border-left: 4px solid #dc3545;
            }
            
            .notification.info {
                background: rgba(13, 110, 253, 0.85);
                border-left: 4px solid #0d6efd;
            }
            
            .notification.warning {
                background: rgba(255, 193, 7, 0.85);
                border-left: 4px solid #ffc107;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; visibility: hidden; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // 添加到容器
    notificationContainer.appendChild(notification);
    
    // 5秒后移除通知
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// 更新网络切换函数，确保能正确处理 MetaMask
async function switchNetwork(chainId) {
    try {
        // 检查当前是否使用 MetaMask
        if (window.ethereum && window.ethereum.isMetaMask) {
            // 使用 MetaMask API 切换网络
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: '0x' + chainId.toString(16) }], // 将数字转为十六进制
            });
            return true;
        } else if (web3 && web3.currentProvider) {
            // 使用 Web3 切换网络
            await web3.currentProvider.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: web3.utils.toHex(chainId) }],
            });
            return true;
        }
        return false;
    } catch (switchError) {
        // 特定错误码处理
        if (switchError.code === 4902) {
            try {
                // 网络不存在，尝试添加网络
                const networkParams = getNetworkParams(chainId);
                
                // 根据使用的提供者选择 API
                if (window.ethereum && window.ethereum.isMetaMask) {
                    await window.ethereum.request({
                        method: 'wallet_addEthereumChain',
                        params: [networkParams],
                    });
                } else if (web3 && web3.currentProvider) {
                    await web3.currentProvider.request({
                        method: 'wallet_addEthereumChain',
                        params: [networkParams],
                    });
                }
                return true;
            } catch (addError) {
                console.error('添加网络失败:', addError);
                return false;
            }
        }
        
        // 用户拒绝错误
        if (switchError.code === 4001) {
            showNotification('用户拒绝了网络切换请求', 'warning');
        } else {
            console.error('切换网络失败:', switchError);
            showNotification('切换网络失败: ' + (switchError.message || '未知错误'), 'error');
        }
        
        return false;
    }
}

// 更新 getNetworkParams 函数，添加更多网络支持
function getNetworkParams(chainId) {
    // 主要网络的参数
    const networks = {
        1: {
            chainId: '0x1',
            chainName: '以太坊主网',
            nativeCurrency: {
                name: 'Ether',
                symbol: 'ETH',
                decimals: 18
            },
            rpcUrls: ['https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'],
            blockExplorerUrls: ['https://etherscan.io']
        },
        56: {
            chainId: '0x38',
            chainName: '币安智能链',
            nativeCurrency: {
                name: 'Binance Coin',
                symbol: 'BNB',
                decimals: 18
            },
            rpcUrls: ['https://bsc-dataseed1.binance.org'],
            blockExplorerUrls: ['https://bscscan.com']
        },
        137: {
            chainId: '0x89',
            chainName: 'Polygon',
            nativeCurrency: {
                name: 'MATIC',
                symbol: 'MATIC',
                decimals: 18
            },
            rpcUrls: ['https://polygon-rpc.com'],
            blockExplorerUrls: ['https://polygonscan.com']
        },
        42161: {
            chainId: '0xA4B1',
            chainName: 'Arbitrum One',
            nativeCurrency: {
                name: 'Ether',
                symbol: 'ETH',
                decimals: 18
            },
            rpcUrls: ['https://arb1.arbitrum.io/rpc'],
            blockExplorerUrls: ['https://arbiscan.io']
        },
        10: {
            chainId: '0xA',
            chainName: 'Optimism',
            nativeCurrency: {
                name: 'Ether',
                symbol: 'ETH',
                decimals: 18
            },
            rpcUrls: ['https://mainnet.optimism.io'],
            blockExplorerUrls: ['https://optimistic.etherscan.io']
        },
        43114: {
            chainId: '0xA86A',
            chainName: 'Avalanche C-Chain',
            nativeCurrency: {
                name: 'Avalanche',
                symbol: 'AVAX',
                decimals: 18
            },
            rpcUrls: ['https://api.avax.network/ext/bc/C/rpc'],
            blockExplorerUrls: ['https://snowtrace.io']
        }
    };
    
    return networks[chainId] || networks[1]; // 默认返回以太坊主网
} 