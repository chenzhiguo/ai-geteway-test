# AI Gateway测试项目术语表

## 核心概念

### AI Gateway
大模型代理网关，类似于OpenRouter的LLM API网关。对外提供OpenAI兼容的统一接口，对内路由到多个LLM提供商。

### RequestType
请求类型，标识不同的LLM接口：
- `chat_completion`：聊天补全接口
- `embedding`：文本嵌入接口
- `image_generation`：图像生成接口
- `responses`：OpenAI Responses接口
- `model_list`：模型列表接口

### Provider
LLM提供商，如OpenAI、Anthropic、Google、DeepSeek等。

### Pipeline
请求处理管线，按RequestType匹配，包含InboundFilter链、Invoker和OutboundFilter链。

### Invoker
调用抽象，三种类型：
- `ProviderInvoker`：叶子节点，封装一个Provider + Endpoint
- `ClusterInvoker`：编排器，串联Discovery → RouterChain → LoadBalancer → ProviderInvoker
- `FallbackInvoker`：模型降级编排器

### Filter
过滤器，两种类型：
- `InboundFilter`：请求进入前执行（Auth、RateLimit、Validate）
- `OutboundFilter`：响应离开后执行（TokenSettlement、StickySession、Metrics、AccessLog）

### Router
路由器，Endpoint列表的硬约束过滤器：
- `CapabilityRouter`：过滤不支持RequestType的endpoint
- `TagRouter`：标签过滤
- `CircuitBreakerRouter`：熔断过滤

### LoadBalancer
负载均衡器，8种策略：
- RoundRobin：轮询
- WeightedRoundRobin：加权轮询
- Random：随机
- LeastConnections：最少连接
- LeastLatency：最低延迟
- Cost：最低成本
- Sticky：粘性会话
- Composite：复合策略

### StateStore
状态存储，存储限流、熔断、Sticky Session等状态，支持Memory和Redis两种实现。

## 测试相关术语

### E2E测试
端到端测试，通过HTTP调用测试完整的请求流程。

### 性能测试
测试网关的性能指标：
- **吞吐量（Throughput）**：QPS（每秒请求数）
- **延迟（Latency）**：响应时间，包括P50、P95、P99
- **并发（Concurrency）**：同时处理的请求数

### Mock服务器
模拟LLM提供商的HTTP服务器，用于测试。

### 测试夹具（Fixture）
pytest中用于提供测试数据和资源的函数。

### 测试标记（Marker）
pytest中用于分类和过滤测试的装饰器。

## 网关特性术语

### Failover
故障转移，当一个Provider失败时自动切换到另一个Provider。

### 熔断（Circuit Breaker)
保护机制，当Provider连续失败时暂时停止调用，避免雪崩。

### 限流（Rate Limiting)
流量控制机制，限制请求速率，防止过载。

### Sticky Session
粘性会话，将同一Session的请求路由到同一Endpoint，用于Prompt Caching。

### Fallback
模型降级，当首选模型失败时自动降级到备选模型。

### TTFT
Time To First Token，首字节时间，流式响应中从请求开始到收到第一个字节的时间。

## 配置相关术语

### PolicyMatcher
策略匹配器，按维度（apikey+model+user等）匹配限流策略。

### ErrorMatcher
错误匹配器，用于识别错误类型，被retry、circuit_breaker、fallback使用。

### Pipeline extends
Pipeline继承，允许一个Pipeline继承另一个Pipeline的配置。

### 配置热加载
运行时动态更新配置，无需重启服务。

## 测试数据术语

### 测试用例（Test Case)
一个独立的测试场景。

### 测试套件（Test Suite)
一组相关的测试用例。

### 测试数据（Test Data)
测试使用的输入数据。

### 测试报告（Test Report)
测试执行结果的汇总报告。