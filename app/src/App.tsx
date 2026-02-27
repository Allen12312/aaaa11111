import { useState, useEffect } from 'react'
import { 
  Play, RotateCcw, Bot, TrendingUp, Shield, 
  Gavel, Search, Plus, Activity, MessageSquare, Wallet 
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import './App.css'

// Agent类型定义
interface Agent {
  name: string
  type: string
  description: string
  status: string
  performance: {
    total_actions: number
    successful_actions: number
    failed_actions: number
    total_profit: number
  }
  recent_actions: any[]
}

interface SystemStatus {
  running: boolean
  cycle_count: number
  agent_counts: Record<string, number>
  market_count: number
  message_queue_size: number
  agents: Record<string, Agent[]>
}

function App() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [logs, setLogs] = useState<string[]>([])
  const [, setSelectedAgent] = useState<Agent | null>(null)
  const [markets, setMarkets] = useState<any[]>([])

  const API_URL = 'https://agent-market-backend-production.up.railway.app'

  // 获取系统状态
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/status`)
      const data = await response.json()
      setSystemStatus(data)
    } catch (error) {
      console.error('获取状态失败:', error)
    }
  }

  // 获取市场列表
  const fetchMarkets = async () => {
    try {
      const response = await fetch(`${API_URL}/api/markets`)
      const data = await response.json()
      setMarkets(data)
    } catch (error) {
      console.error('获取市场失败:', error)
    }
  }

  // 运行一个周期
  const runCycle = async () => {
    setIsRunning(true)
    addLog('🚀 开始运行完整周期...')
    try {
      const response = await fetch(`${API_URL}/api/cycle/run`, { method: 'POST' })
      const data = await response.json()
      addLog(`✅ 周期 ${data.cycle} 完成`)
      addLog(`📊 发现: ${data.summary.discovery_count}, 上架: ${data.summary.listing_count}, 审核: ${data.summary.audit_count}`)
      fetchStatus()
      fetchMarkets()
    } catch (error) {
      addLog(`❌ 运行失败: ${error}`)
    }
    setIsRunning(false)
  }

  // 添加日志
  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 100))
  }

  // 初始化
  useEffect(() => {
    fetchStatus()
    fetchMarkets()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  // 获取Agent类型颜色
  const getAgentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      discovery: 'bg-blue-500',
      listing: 'bg-green-500',
      audit: 'bg-yellow-500',
      market_maker: 'bg-purple-500',
      trading: 'bg-pink-500',
      governance: 'bg-orange-500'
    }
    return colors[type] || 'bg-gray-500'
  }

  // 获取Agent类型图标
  const getAgentTypeIcon = (type: string) => {
    switch (type) {
      case 'discovery': return <Search className="w-4 h-4" />
      case 'listing': return <Plus className="w-4 h-4" />
      case 'audit': return <Shield className="w-4 h-4" />
      case 'market_maker': return <Activity className="w-4 h-4" />
      case 'trading': return <TrendingUp className="w-4 h-4" />
      case 'governance': return <Gavel className="w-4 h-4" />
      default: return <Bot className="w-4 h-4" />
    }
  }

  // 获取Agent类型中文名
  const getAgentTypeName = (type: string) => {
    const names: Record<string, string> = {
      discovery: '发现',
      listing: '上架',
      audit: '审核',
      market_maker: '做市',
      trading: '交易',
      governance: '治理'
    }
    return names[type] || type
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* 顶部导航 */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
                  AgentHub
                </h1>
                <p className="text-xs text-slate-400">AI Agent预测市场平台</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Activity className="w-4 h-4" />
                <span>周期: {systemStatus?.cycle_count || 0}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Wallet className="w-4 h-4" />
                <span>市场: {systemStatus?.market_count || 0}</span>
              </div>
              <Button
                onClick={runCycle}
                disabled={isRunning}
                className="bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600"
              >
                {isRunning ? (
                  <><RotateCcw className="w-4 h-4 mr-2 animate-spin" /> 运行中...</>
                ) : (
                  <><Play className="w-4 h-4 mr-2" /> 运行周期</>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容 */}
      <main className="container mx-auto px-4 py-6">
        <Tabs defaultValue="agents" className="space-y-6">
          <TabsList className="bg-slate-900 border border-slate-800">
            <TabsTrigger value="agents" className="data-[state=active]:bg-violet-500/20">
              <Bot className="w-4 h-4 mr-2" /> Agent管理
            </TabsTrigger>
            <TabsTrigger value="markets" className="data-[state=active]:bg-violet-500/20">
              <TrendingUp className="w-4 h-4 mr-2" /> 预测市场
            </TabsTrigger>
            <TabsTrigger value="logs" className="data-[state=active]:bg-violet-500/20">
              <MessageSquare className="w-4 h-4 mr-2" /> 运行日志
            </TabsTrigger>
          </TabsList>

          {/* Agent管理 */}
          <TabsContent value="agents" className="space-y-6">
            {/* Agent统计 */}
            <div className="grid grid-cols-6 gap-4">
              {['discovery', 'listing', 'audit', 'market_maker', 'trading', 'governance'].map((type) => (
                <Card key={type} className="bg-slate-900 border-slate-800">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className={`w-8 h-8 rounded-lg ${getAgentTypeColor(type)} flex items-center justify-center`}>
                        {getAgentTypeIcon(type)}
                      </div>
                      <span className="text-2xl font-bold">
                        {systemStatus?.agent_counts?.[type] || 0}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">{getAgentTypeName(type)}Agent</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Agent列表 */}
            <div className="grid grid-cols-3 gap-4">
              {Object.entries(systemStatus?.agents || {}).map(([type, agents]) => (
                agents.map((agent, idx) => (
                  <Card 
                    key={`${type}-${idx}`}
                    className="bg-slate-900 border-slate-800 cursor-pointer hover:border-violet-500/50 transition-colors"
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={`w-8 h-8 rounded-lg ${getAgentTypeColor(type)} flex items-center justify-center`}>
                            {getAgentTypeIcon(type)}
                          </div>
                          <div>
                            <CardTitle className="text-sm font-medium">{agent.name}</CardTitle>
                            <p className="text-xs text-slate-400">{agent.description}</p>
                          </div>
                        </div>
                        <Badge 
                          variant={agent.status === 'idle' ? 'default' : 'secondary'}
                          className={agent.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}
                        >
                          {agent.status === 'idle' ? '空闲' : '运行中'}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-lg font-bold text-violet-400">
                            {agent.performance.total_actions}
                          </p>
                          <p className="text-xs text-slate-500">总行动</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-lg font-bold text-green-400">
                            {agent.performance.successful_actions}
                          </p>
                          <p className="text-xs text-slate-500">成功</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-lg font-bold text-fuchsia-400">
                            ${agent.performance.total_profit.toFixed(0)}
                          </p>
                          <p className="text-xs text-slate-500">收益</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ))}
            </div>
          </TabsContent>

          {/* 预测市场 */}
          <TabsContent value="markets" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {markets.map((market) => (
                <Card key={market.id} className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{market.market_title}</CardTitle>
                      <Badge className="bg-violet-500/20 text-violet-400">
                        {market.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-400">{market.description}</p>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex gap-4">
                        <div>
                          <p className="text-xs text-slate-500">初始概率</p>
                          <p className="text-lg font-bold">{(market.initial_probability * 100).toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">流动性</p>
                          <p className="text-lg font-bold">${market.initial_liquidity?.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500">手续费</p>
                          <p className="text-lg font-bold">{(market.trading_fee * 100).toFixed(1)}%</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-slate-500">状态</p>
                        <Badge className={market.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}>
                          {market.status === 'active' ? '活跃' : '待定'}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {market.outcomes?.map((outcome: string) => (
                        <Button key={outcome} variant="outline" size="sm" className="flex-1 border-slate-700">
                          {outcome}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* 运行日志 */}
          <TabsContent value="logs">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5" />
                  系统日志
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[500px] w-full">
                  <div className="space-y-2">
                    {logs.map((log, idx) => (
                      <div key={idx} className="text-sm font-mono text-slate-300 py-1 border-b border-slate-800/50">
                        {log}
                      </div>
                    ))}
                    {logs.length === 0 && (
                      <p className="text-slate-500 text-center py-8">暂无日志，点击"运行周期"开始</p>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
