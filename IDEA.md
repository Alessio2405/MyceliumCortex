# Hierarchical Multi-Agent System: Complete Architecture

## Table of Contents
1. [Philosophy & Design Principles](#philosophy--design-principles)
2. [System Overview](#system-overview)
3. [Layer-by-Layer Deep Dive](#layer-by-layer-deep-dive)
4. [Communication Protocols](#communication-protocols)
5. [Message Flow Patterns](#message-flow-patterns)
6. [Gateway Architecture](#gateway-architecture)
7. [State Management](#state-management)
8. [Scalability & Resilience](#scalability--resilience)
9. [Real-World Scenarios](#real-world-scenarios)
10. [Comparison to Flat Architectures](#comparison-to-flat-architectures)

---

## Philosophy & Design Principles

### Core Tenets

**1. Hierarchy Mirrors Human Organizations**

Just like a company has executives, managers, and workers, this system has:
- **Strategic Layer** = Executives (set vision, allocate resources)
- **Tactical Layer** = Managers (coordinate teams, make day-to-day decisions)
- **Execution Layer** = Workers (do actual tasks)

**2. Temporal Stratification**

Each layer operates on different time scales:
```
Strategic:  Hours → Days → Weeks
            "Should we prioritize Telegram over WhatsApp this month?"
            
Tactical:   Minutes → Hours
            "User message came in, which agent should handle it?"
            
Execution:  Milliseconds → Seconds
            "Send this WhatsApp message now"
```

**3. Separation of Concerns**

- **Strategic**: WHAT goals to pursue, WHERE to allocate resources
- **Tactical**: HOW to accomplish goals, WHICH agents to use
- **Execution**: DO the actual work, REPORT results

**4. Information Abstraction**

Higher layers see simplified views:
```
Execution Agent:
  "Sent message to +1234567890 at 14:23:05, 145 bytes, took 234ms"

Tactical Supervisor (aggregates):
  "Sent 47 messages in the last hour, avg latency 198ms, 2 failures"

Strategic Coordinator (further abstracts):
  "WhatsApp channel performing well, 98% success rate this week"
```

**5. Autonomy at Each Level**

Each layer makes decisions appropriate to its scope:
- Strategic doesn't micromanage how supervisors route messages
- Tactical doesn't dictate exactly when execution agents send bytes
- Execution doesn't question why it got a directive

---

## System Overview

### The Big Picture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          STRATEGIC LAYER                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │Resource Allocator│  │   Goal Planner   │  │ Health Monitor   │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                      │            │
│           └─────────────────────┼──────────────────────┘            │
│                                 │                                   │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │        GATEWAY            │
                    │   (Message Bus + Registry)│
                    └─────────────┬─────────────┘
                                  │
┌─────────────────────────────────┼───────────────────────────────────┐
│                          TACTICAL LAYER                             │
│  ┌──────────────┐    ┌───────────────┐    ┌──────────────────┐     │
│  │   Channel    │    │     Tool      │    │   Conversation   │     │
│  │  Supervisor  │    │  Supervisor   │    │   Supervisor     │     │
│  └──────┬───────┘    └───────┬───────┘    └────────┬─────────┘     │
│         │                    │                      │               │
└─────────┼────────────────────┼──────────────────────┼───────────────┘
          │                    │                      │
          └──────────┬─────────┴──────────┬───────────┘
                     │                    │
┌────────────────────┼────────────────────┼──────────────────────────┐
│                          EXECUTION LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ WhatsApp │  │ Telegram │  │ Browser  │  │  Canvas  │  ...      │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Count by Layer

```
Strategic Layer:   3-5 agents   (few, high-level coordinators)
Tactical Layer:    5-15 agents  (supervisors for each domain)
Execution Layer:   20-100+ agents (many specialized workers)
```

---

## Layer-by-Layer Deep Dive

### Strategic Layer

**Purpose**: Long-term planning, resource allocation, system-wide optimization

**Time Horizon**: Hours to Days

**Key Responsibilities**:
1. Set system-wide goals and priorities
2. Allocate computational/financial resources across domains
3. Monitor overall system health
4. Adapt strategies based on long-term patterns
5. Make high-level routing decisions

**Example Agents**:

#### 1. Resource Allocator
```typescript
class ResourceAllocator {
  // Analyzes system usage and allocates resources
  
  async analyzeUsagePatterns() {
    // Last 7 days: user sends 90% of messages via WhatsApp
    // Decision: Allocate more resources to WhatsApp channel
    
    return {
      whatsapp: { priority: 'high', budget: 1000 },
      telegram: { priority: 'medium', budget: 500 },
      slack: { priority: 'low', budget: 100 },
    };
  }
  
  async allocateResources(allocation: ResourceAllocation) {
    // Send directives to tactical supervisors
    await this.sendDirective(['channel-supervisor'], {
      action: 'set_priorities',
      priorities: allocation,
    });
  }
}
```

#### 2. Goal Planner
```typescript
class GoalPlanner {
  // Creates execution plans from high-level goals
  
  async decomposeGoal(goal: string) {
    // Goal: "Prepare weekly status report"
    // Decomposition:
    return [
      { domain: 'channels', task: 'gather_message_stats' },
      { domain: 'tools', task: 'generate_usage_charts' },
      { domain: 'conversation', task: 'summarize_interactions' },
      { domain: 'channels', task: 'send_report_via_email' },
    ];
  }
}
```

#### 3. Health Monitor
```typescript
class HealthMonitor {
  // Monitors system-wide health
  
  async checkSystemHealth() {
    const metrics = await this.gatherMetrics();
    
    if (metrics.errorRate > 0.05) {
      // More than 5% error rate - escalate
      await this.alert('high_error_rate', metrics);
    }
    
    if (metrics.avgLatency > 5000) {
      // Responses taking > 5s - redistribute load
      await this.sendDirective(['resource-allocator'], {
        action: 'optimize_distribution',
      });
    }
  }
}
```

**Decision Examples**:
- "WhatsApp is our primary channel, allocate 70% of resources there"
- "User activity peaks between 9am-5pm, scale up execution agents then"
- "Browser automation costs too much, limit to 10 sessions per hour"
- "Error rate spiked, pause non-critical tasks and focus on stability"

---

### Tactical Layer

**Purpose**: Domain-specific coordination, task routing, resource management

**Time Horizon**: Minutes to Hours

**Key Responsibilities**:
1. Route work to appropriate execution agents
2. Manage agent lifecycle (spawn/kill execution agents as needed)
3. Aggregate reports for strategic layer
4. Make tactical decisions (retries, failover, load balancing)
5. Coordinate cross-agent tasks within a domain

**Example Supervisors**:

#### 1. Channel Supervisor
```typescript
class ChannelSupervisor {
  // Manages all messaging channel agents
  
  children: {
    'whatsapp-agent': WhatsAppAgent,
    'telegram-agent': TelegramAgent,
    'slack-agent': SlackAgent,
    'discord-agent': DiscordAgent,
  }
  
  async routeOutboundMessage(message: OutboundMessage) {
    // Decision logic:
    
    // 1. Does user have a preferred channel?
    if (message.to.preferredChannel === 'whatsapp') {
      return this.delegate('whatsapp-agent', message);
    }
    
    // 2. Is the user online on any channel?
    const onlineChannels = await this.checkUserPresence(message.to);
    if (onlineChannels.includes('telegram')) {
      return this.delegate('telegram-agent', message);
    }
    
    // 3. Which channel has the best success rate recently?
    const stats = this.getChannelStats();
    const bestChannel = this.selectBestChannel(stats);
    return this.delegate(`${bestChannel}-agent`, message);
  }
  
  async handleInboundMessage(fromAgent: string, message: InboundMessage) {
    // Message came from WhatsApp
    // Should we respond on WhatsApp or route to different channel?
    
    // Mark this conversation as active on WhatsApp
    await this.setActiveChannel(message.from, 'whatsapp');
    
    // Route to conversation supervisor for processing
    await this.reportToParent({
      type: 'inbound_message',
      channel: 'whatsapp',
      message,
    });
  }
  
  async handleAgentFailure(agentId: string, error: Error) {
    // Execution agent failed
    
    // 1. Log the failure
    this.logFailure(agentId, error);
    
    // 2. Should we retry?
    if (this.shouldRetry(error)) {
      await this.retry(agentId, 3, { exponentialBackoff: true });
    }
    
    // 3. Should we failover to another channel?
    if (this.isCritical(error)) {
      await this.failoverToAlternateChannel(agentId);
    }
    
    // 4. Report to strategic layer if this is a pattern
    const failureRate = this.calculateFailureRate(agentId);
    if (failureRate > 0.1) {
      await this.reportToParent({
        type: 'high_failure_rate',
        agent: agentId,
        rate: failureRate,
      });
    }
  }
}
```

#### 2. Tool Supervisor
```typescript
class ToolSupervisor {
  // Manages tool execution agents (browser, canvas, file system, etc.)
  
  children: {
    'browser-1': BrowserAgent,
    'browser-2': BrowserAgent,  // Can have multiple instances
    'canvas-agent': CanvasAgent,
    'file-agent': FileAgent,
  }
  
  async executeToolSequence(sequence: ToolTask[]) {
    // Complex task: "Search Google, screenshot results, save to file"
    
    const results = [];
    
    // 1. Delegate to browser agent
    const searchResults = await this.delegate('browser-1', {
      action: 'search',
      query: sequence[0].query,
    });
    
    // 2. Screenshot
    const screenshot = await this.delegate('browser-1', {
      action: 'screenshot',
      url: searchResults.url,
    });
    
    // 3. Save to file
    await this.delegate('file-agent', {
      action: 'write',
      path: '/screenshots/result.png',
      data: screenshot,
    });
    
    // 4. Report completion to strategic layer
    await this.reportToParent({
      type: 'tool_sequence_complete',
      results,
    });
  }
  
  async manageBrowserPool() {
    // Load balancing logic
    
    const activeBrowsers = this.children.filter(
      c => c.type === 'browser' && c.status === 'busy'
    );
    
    if (activeBrowsers.length >= 2) {
      // All browsers busy, queue the request
      this.queueRequest(request);
    } else {
      // Find idle browser
      const idleBrowser = this.findIdleBrowser();
      await this.delegate(idleBrowser.id, request);
    }
  }
}
```

#### 3. Conversation Supervisor
```typescript
class ConversationSupervisor {
  // Manages conversation context, memory, and LLM agents
  
  children: {
    'context-agent': ContextAgent,      // Manages conversation history
    'memory-agent': MemoryAgent,        // Long-term memory storage
    'llm-agent': LLMAgent,              // LLM API calls
    'persona-agent': PersonaAgent,      // Multi-personality routing
  }
  
  async handleConversationTurn(message: UserMessage) {
    // User sent a message, process it
    
    // 1. Get conversation context
    const context = await this.delegate('context-agent', {
      action: 'get_context',
      conversationId: message.conversationId,
    });
    
    // 2. Check long-term memory for relevant info
    const memories = await this.delegate('memory-agent', {
      action: 'search',
      query: message.text,
      limit: 5,
    });
    
    // 3. Determine which persona to use
    const persona = await this.delegate('persona-agent', {
      action: 'select_persona',
      context,
      message,
    });
    
    // 4. Generate response via LLM
    const response = await this.delegate('llm-agent', {
      action: 'generate',
      context,
      memories,
      persona,
      message: message.text,
    });
    
    // 5. Update context
    await this.delegate('context-agent', {
      action: 'append',
      conversationId: message.conversationId,
      turn: { user: message.text, assistant: response },
    });
    
    // 6. Report back to strategic layer
    await this.reportToParent({
      type: 'conversation_turn_complete',
      conversationId: message.conversationId,
      response,
    });
  }
}
```

**Decision Examples**:
- "Route this message to WhatsApp because user is online there"
- "Browser agent failed, retry 3 times with exponential backoff"
- "This task needs browser + file agents, coordinate them"
- "Conversation context is getting large, trigger summarization"

---

### Execution Layer

**Purpose**: Perform actual work, interact with external systems

**Time Horizon**: Milliseconds to Seconds

**Key Responsibilities**:
1. Execute single, well-defined tasks
2. Interact with external APIs/services
3. Report results and errors
4. Maintain minimal state
5. Be fast and focused

**Example Agents**:

#### 1. WhatsApp Agent
```typescript
class WhatsAppAgent {
  level = 'execution';
  capabilities = ['send_message', 'send_media', 'read_message'];
  
  private client: WAWebJS.Client;
  
  async onDirective(message: AgentMessage) {
    const { action, payload } = message.payload;
    
    switch (action) {
      case 'send_message':
        const start = Date.now();
        try {
          const result = await this.client.sendMessage(
            payload.to,
            payload.text
          );
          
          // Report success
          await this.reportToParent({
            action: 'send_message',
            status: 'success',
            messageId: result.id,
            latency: Date.now() - start,
            bytessent: payload.text.length,
          });
        } catch (error) {
          // Report failure
          await this.reportToParent({
            action: 'send_message',
            status: 'failed',
            error: error.message,
            latency: Date.now() - start,
          });
        }
        break;
        
      case 'send_media':
        // Similar pattern for media
        break;
    }
  }
  
  // Listen for incoming messages
  private setupIncomingHandler() {
    this.client.on('message', async (msg) => {
      await this.reportToParent({
        type: 'inbound_message',
        from: msg.from,
        text: msg.body,
        timestamp: msg.timestamp,
      });
    });
  }
}
```

#### 2. Browser Agent
```typescript
class BrowserAgent {
  level = 'execution';
  capabilities = ['navigate', 'screenshot', 'extract', 'click'];
  
  private browser: Browser;
  private page: Page;
  
  async onDirective(message: AgentMessage) {
    const { action, payload } = message.payload;
    
    switch (action) {
      case 'navigate':
        await this.page.goto(payload.url);
        await this.reportToParent({
          action: 'navigate',
          status: 'success',
          url: payload.url,
        });
        break;
        
      case 'screenshot':
        const screenshot = await this.page.screenshot({
          fullPage: payload.fullPage,
        });
        
        await this.reportToParent({
          action: 'screenshot',
          status: 'success',
          data: screenshot.toString('base64'),
          size: screenshot.length,
        });
        break;
        
      case 'extract':
        const data = await this.page.evaluate(payload.script);
        await this.reportToParent({
          action: 'extract',
          status: 'success',
          data,
        });
        break;
    }
  }
}
```

#### 3. LLM Agent
```typescript
class LLMAgent {
  level = 'execution';
  capabilities = ['generate', 'embed', 'moderate'];
  
  private client: AnthropicSDK;
  
  async onDirective(message: AgentMessage) {
    const { action, payload } = message.payload;
    
    switch (action) {
      case 'generate':
        const start = Date.now();
        
        const response = await this.client.messages.create({
          model: payload.model || 'claude-sonnet-4-20250514',
          max_tokens: payload.maxTokens || 1000,
          messages: payload.messages,
        });
        
        await this.reportToParent({
          action: 'generate',
          status: 'success',
          response: response.content[0].text,
          usage: {
            inputTokens: response.usage.input_tokens,
            outputTokens: response.usage.output_tokens,
          },
          latency: Date.now() - start,
          model: payload.model,
        });
        break;
    }
  }
}
```

**Characteristics**:
- Single responsibility (one capability per agent)
- Fast execution (< 5 seconds typical)
- Detailed error reporting
- No complex decision-making
- Stateless or minimal state

---

## Communication Protocols

### Message Types

```typescript
type MessageType = 
  | 'directive'      // Command from higher layer
  | 'report'         // Status update to higher layer
  | 'query'          // Question to peer or parent
  | 'coordinate'     // Collaboration proposal to peer
  | 'event';         // Notification (can go any direction)
```

### Message Structure

```typescript
interface AgentMessage {
  id: string;                    // Unique message ID
  from: string;                  // Sender agent ID
  to: string[];                  // Recipient agent IDs (can be multiple)
  type: MessageType;             // Message type
  payload: any;                  // Arbitrary payload
  timestamp: number;             // Unix timestamp
  priority: number;              // 0-10 (0=low, 10=critical)
  requiresResponse?: boolean;    // Does sender expect a reply?
  correlationId?: string;        // For tracking related messages
  ttl?: number;                  // Time to live (ms)
}
```

### Communication Patterns

#### 1. Top-Down Directive Flow

```
Strategic Agent
    │
    │ sends directive
    ▼
Tactical Supervisor
    │
    │ decomposes & routes
    ▼
Execution Agent(s)
    │
    │ execute & report
    ▼
Tactical Supervisor
    │
    │ aggregates & reports
    ▼
Strategic Agent
```

Example flow:
```typescript
// Strategic Layer
await this.sendDirective(['channel-supervisor'], {
  action: 'send_notification',
  payload: {
    message: 'System maintenance in 1 hour',
    channels: ['whatsapp', 'telegram'],
  },
}, priority: 9);

// Tactical Layer (Channel Supervisor)
async onDirective(msg) {
  // Decompose into channel-specific tasks
  for (const channel of msg.payload.channels) {
    await this.sendDirective([`${channel}-agent`], {
      action: 'send_message',
      payload: {
        to: 'all_users',
        text: msg.payload.message,
      },
    });
  }
}

// Execution Layer (WhatsApp Agent)
async onDirective(msg) {
  // Do the actual work
  await this.client.sendMessage(msg.payload.to, msg.payload.text);
  
  // Report back
  await this.reportToParent({
    action: 'send_message',
    status: 'success',
  });
}
```

#### 2. Bottom-Up Report Flow

```
Execution Agent
    │
    │ reports result
    ▼
Tactical Supervisor
    │
    │ aggregates from multiple children
    ▼
Strategic Agent
    │
    │ analyzes trends
    ▼
Makes strategic decision
```

Example flow:
```typescript
// Execution Layer
await this.reportToParent({
  type: 'message_sent',
  channel: 'whatsapp',
  latency: 234,
  success: true,
});

// Tactical Layer
async onReport(msg) {
  // Aggregate reports from multiple execution agents
  this.stats.whatsapp.messagesSent++;
  this.stats.whatsapp.totalLatency += msg.payload.latency;
  
  // If we've collected enough data, report to strategic
  if (this.stats.whatsapp.messagesSent % 100 === 0) {
    await this.reportToParent({
      type: 'channel_performance',
      channel: 'whatsapp',
      messagesSent: this.stats.whatsapp.messagesSent,
      avgLatency: this.stats.whatsapp.totalLatency / this.stats.whatsapp.messagesSent,
      successRate: this.calculateSuccessRate(),
    });
  }
}

// Strategic Layer
async onReport(msg) {
  // Analyze long-term trends
  if (msg.payload.avgLatency > this.thresholds.maxLatency) {
    // WhatsApp is getting slow, reduce load
    await this.sendDirective(['channel-supervisor'], {
      action: 'reduce_load',
      channel: 'whatsapp',
      maxConcurrent: 5,
    });
  }
}
```

#### 3. Horizontal Coordination

```
Execution Agent A  ←────→  Execution Agent B
        │                        │
        └────────┬───────────────┘
                 │
          Both report to
                 │
                 ▼
        Tactical Supervisor
```

Example flow:
```typescript
// Browser Agent needs file system access
class BrowserAgent {
  async coordinateWithFileAgent() {
    // Ask peer agent for help
    await this.coordinateWithPeers(['file-agent'], {
      proposal: 'save_screenshot',
      data: screenshot,
      path: '/tmp/screenshot.png',
    });
  }
}

// File Agent responds
class FileAgent {
  async onCoordinate(msg) {
    if (msg.payload.proposal === 'save_screenshot') {
      // Do the work
      await fs.writeFile(msg.payload.path, msg.payload.data);
      
      // Send response
      await this.sendMessage({
        from: this.id,
        to: [msg.from],
        type: 'report',
        payload: {
          proposal: 'save_screenshot',
          status: 'completed',
          path: msg.payload.path,
        },
      });
      
      // Also report to supervisor
      await this.reportToParent({
        type: 'coordination_completed',
        with: msg.from,
        action: 'save_screenshot',
      });
    }
  }
}
```

#### 4. Event Broadcasting

```
       Strategic Layer
              │
              │ event: system_maintenance
              ▼
       ┌──────┴──────┐
       │   Gateway   │
       └──────┬──────┘
              │
     ┌────────┼────────┐
     │        │        │
     ▼        ▼        ▼
Tactical  Tactical  Tactical
```

Example:
```typescript
// Strategic layer broadcasts event
await this.gateway.broadcast('tactical', {
  from: this.id,
  type: 'event',
  payload: {
    event: 'system_maintenance_starting',
    eta: Date.now() + 3600000, // 1 hour
  },
  timestamp: Date.now(),
  priority: 8,
});

// All tactical supervisors receive it
async onEvent(msg) {
  if (msg.payload.event === 'system_maintenance_starting') {
    // Prepare for maintenance
    await this.prepareForMaintenance(msg.payload.eta);
  }
}
```

---

## Gateway Architecture

### Gateway as Central Nervous System

The Gateway is the **message bus**, **agent registry**, and **routing engine**.

```
┌─────────────────────────────────────────────────────────────┐
│                         GATEWAY                             │
│                                                             │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │  Agent Registry │         │  Routing Engine  │          │
│  │                 │         │                  │          │
│  │  - Agent IDs    │         │  - Routes        │          │
│  │  - Metadata     │◄────────┤  - Filters       │          │
│  │  - Capabilities │         │  - Priorities    │          │
│  │  - Health       │         │                  │          │
│  └─────────────────┘         └──────────────────┘          │
│           │                           │                     │
│           ▼                           ▼                     │
│  ┌─────────────────────────────────────────────┐           │
│  │          Message Queue & Dispatcher         │           │
│  │                                             │           │
│  │  - Priority queue                           │           │
│  │  - Rate limiting                            │           │
│  │  - Dead letter queue                        │           │
│  └─────────────────────────────────────────────┘           │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────┐           │
│  │          WebSocket Server                   │           │
│  │          (for remote agents)                │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Gateway Responsibilities

#### 1. Agent Registration & Discovery

```typescript
class Gateway {
  private agents = new Map<string, Agent>();
  
  async registerAgent(agent: Agent) {
    // Store agent reference
    this.agents.set(agent.id, agent);
    
    // Index by capabilities for discovery
    for (const cap of agent.capabilities) {
      this.capabilityIndex.add(cap.name, agent.id);
    }
    
    // Start health monitoring
    this.monitorHealth(agent.id);
    
    // Emit registration event
    this.emit('agent-registered', agent.getMetadata());
  }
  
  findAgentsByCapability(capability: string): Agent[] {
    const agentIds = this.capabilityIndex.get(capability);
    return agentIds.map(id => this.agents.get(id));
  }
}
```

#### 2. Message Routing

```typescript
class Gateway {
  private routes: MessageRoute[] = [];
  
  async routeMessage(message: AgentMessage) {
    // 1. Apply routing rules
    const effectiveRecipients = this.applyRoutes(message);
    
    // 2. Priority queue
    await this.messageQueue.enqueue(message, message.priority);
    
    // 3. Rate limiting check
    if (!this.rateLimiter.allow(message.from)) {
      await this.handleRateLimit(message);
      return;
    }
    
    // 4. Deliver to each recipient
    for (const recipientId of effectiveRecipients) {
      const agent = this.agents.get(recipientId);
      
      if (agent) {
        try {
          await agent.handleMessage(message);
          this.metrics.messagesSent++;
        } catch (error) {
          // Dead letter queue for failed deliveries
          await this.deadLetterQueue.add(message, error);
        }
      }
    }
  }
  
  addRoute(route: MessageRoute) {
    // Route example: "All reports from execution agents go to their supervisor"
    this.routes.push({
      condition: (msg) => 
        msg.type === 'report' && 
        this.agents.get(msg.from)?.level === 'execution',
      transform: (msg) => {
        const agent = this.agents.get(msg.from);
        return {
          ...msg,
          to: [agent.parent.id], // Route to parent
        };
      },
    });
  }
}
```

#### 3. Health Monitoring

```typescript
class Gateway {
  async monitorHealth(agentId: string) {
    setInterval(async () => {
      const agent = this.agents.get(agentId);
      const metadata = agent.getMetadata();
      
      // Check last seen
      const lastSeen = metadata.health.lastSeen;
      const now = Date.now();
      
      if (now - lastSeen > 60000) {
        // Agent hasn't been seen in 1 minute
        this.emit('agent-unhealthy', agentId);
        
        // If it's a critical agent, alert strategic layer
        if (this.isCriticalAgent(agentId)) {
          await this.broadcast('strategic', {
            from: 'gateway',
            type: 'event',
            payload: {
              event: 'critical_agent_offline',
              agentId,
              lastSeen,
            },
            timestamp: now,
            priority: 10,
          });
        }
      }
    }, 30000); // Check every 30s
  }
}
```

#### 4. WebSocket Support (for remote agents)

```typescript
class Gateway {
  private wss: WebSocketServer;
  private remoteAgents = new Map<WebSocket, string>(); // ws -> agentId
  
  startWebSocketServer() {
    this.wss = new WebSocketServer({ port: 8080 });
    
    this.wss.on('connection', (ws) => {
      ws.on('message', async (data) => {
        const message = JSON.parse(data.toString());
        
        // Handle registration
        if (message.type === 'register') {
          const agentId = message.agentId;
          this.remoteAgents.set(ws, agentId);
          
          // Create proxy agent
          const proxy = new RemoteAgentProxy(agentId, ws);
          await this.registerAgent(proxy);
        }
        
        // Handle regular messages
        else {
          await this.routeMessage(message);
        }
      });
    });
  }
  
  // When routing to remote agent, send via WebSocket
  async deliverToRemoteAgent(agentId: string, message: AgentMessage) {
    const ws = this.findWebSocketForAgent(agentId);
    ws.send(JSON.stringify(message));
  }
}
```

---

## State Management

### State Distribution

```
Strategic Layer:   Global state (goals, policies, resource allocations)
Tactical Layer:    Domain state (active tasks, agent health, queues)
Execution Layer:   Minimal state (connection handles, temp data)
```

### State Patterns

#### 1. Strategic State (Persistent)

```typescript
class ResourceAllocator {
  private state = {
    currentGoals: [],
    resourceAllocations: {},
    performanceHistory: [],
    policies: {},
  };
  
  // Persist to database
  async saveState() {
    await db.save('strategic-state', this.state);
  }
  
  // Restore on restart
  async loadState() {
    this.state = await db.load('strategic-state');
  }
}
```

#### 2. Tactical State (Session-based)

```typescript
class ChannelSupervisor {
  private state = {
    activeTasks: new Map(),      // task ID -> task info
    channelStats: {},             // channel -> stats
    agentHealth: new Map(),       // agent ID -> health
    messageQueue: [],             // pending messages
  };
  
  // State is ephemeral, cleared on restart
  // But can checkpoint to handle supervisor crashes
  async checkpoint() {
    await redis.set(`supervisor:${this.id}:state`, JSON.stringify(this.state));
  }
  
  async restore() {
    const saved = await redis.get(`supervisor:${this.id}:state`);
    if (saved) {
      this.state = JSON.parse(saved);
    }
  }
}
```

#### 3. Execution State (Minimal)

```typescript
class WhatsAppAgent {
  private client: WAWebJS.Client;  // Connection handle
  private pendingMessages = [];     // Very small buffer
  
  // No persistent state
  // If agent crashes, supervisor recreates it
}
```

---

## Scalability & Resilience

### Horizontal Scaling

```
Single Machine:
┌─────────────────────────────┐
│  Strategic Layer (1 agent)  │
│  Tactical Layer (3 agents)  │
│  Execution Layer (10 agents)│
└─────────────────────────────┘

Scaled Out:
┌──────────────────┐  ┌──────────────────┐
│ Machine 1        │  │ Machine 2        │
│ - Strategic (1)  │  │ - Tactical (2)   │
│ - Tactical (1)   │  │ - Execution (10) │
│ - Execution (5)  │  │                  │
└──────────────────┘  └──────────────────┘
         │                     │
         └──────┬──────────────┘
                │
        ┌───────▼────────┐
        │ Shared Gateway │
        │   (WebSocket)  │
        └────────────────┘
```

### Resilience Patterns

#### 1. Supervisor Restart Recovery

```typescript
class TaskSupervisor {
  async initialize() {
    // Try to restore state
    await this.restore();
    
    // If restoration failed, query children for their state
    if (!this.state.restored) {
      await this.reconstructStateFromChildren();
    }
    
    // Register with gateway
    await super.initialize();
  }
  
  async reconstructStateFromChildren() {
    // Ask all children what they're working on
    for (const [childId, child] of this.children) {
      await this.sendMessage({
        from: this.id,
        to: [childId],
        type: 'query',
        payload: { query: 'current_task' },
        timestamp: Date.now(),
        priority: 10,
      });
    }
  }
}
```

#### 2. Execution Agent Pool

```typescript
class ToolSupervisor {
  private browserAgentPool = new Pool<BrowserAgent>({
    min: 2,
    max: 10,
    createAgent: () => new BrowserAgent(...),
    destroyAgent: (agent) => agent.shutdown(),
  });
  
  async executeTask(task: BrowserTask) {
    // Get agent from pool
    const agent = await this.browserAgentPool.acquire();
    
    try {
      const result = await agent.execute(task);
      return result;
    } finally {
      // Return to pool
      await this.browserAgentPool.release(agent);
    }
  }
}
```

#### 3. Circuit Breaker

```typescript
class ChannelSupervisor {
  private circuitBreakers = new Map<string, CircuitBreaker>();
  
  async sendViaChannel(channelId: string, message: any) {
    const breaker = this.getCircuitBreaker(channelId);
    
    return await breaker.execute(async () => {
      const agent = this.children.get(channelId);
      return await agent.send(message);
    });
  }
  
  getCircuitBreaker(channelId: string) {
    if (!this.circuitBreakers.has(channelId)) {
      this.circuitBreakers.set(channelId, new CircuitBreaker({
        threshold: 5,           // Open after 5 failures
        timeout: 60000,         // Try again after 1 minute
        onOpen: () => {
          // Report to strategic layer
          this.reportToParent({
            type: 'circuit_breaker_opened',
            channel: channelId,
          });
        },
      }));
    }
    return this.circuitBreakers.get(channelId);
  }
}
```

---

## Real-World Scenarios

### Scenario 1: User Sends WhatsApp Message

**Complete Flow**:

```
1. WhatsApp Agent (Execution)
   ↓ receives message from WhatsApp API
   ↓ reports: "inbound_message from +1234567890"
   
2. Channel Supervisor (Tactical)
   ↓ receives report
   ↓ looks up conversation context
   ↓ decides: route to Conversation Supervisor
   ↓ sends directive to Conversation Supervisor
   
3. Conversation Supervisor (Tactical)
   ↓ receives directive
   ↓ delegates to Context Agent: "get history"
   ↓ delegates to Memory Agent: "search memories"
   ↓ delegates to LLM Agent: "generate response"
   ↓ receives reports from all three
   ↓ reports to Channel Supervisor: "response ready"
   
4. Channel Supervisor (Tactical)
   ↓ receives response
   ↓ delegates to WhatsApp Agent: "send response"
   
5. WhatsApp Agent (Execution)
   ↓ sends message via API
   ↓ reports: "message sent, latency 234ms"
   
6. Channel Supervisor (Tactical)
   ↓ aggregates stats
   ↓ every 100 messages, reports to Strategic
   
7. Resource Allocator (Strategic)
   ↓ analyzes long-term patterns
   ↓ if WhatsApp is main channel, allocates more resources
```

**Detailed Code Flow**:

```typescript
// 1. WhatsApp Agent receives message
class WhatsAppAgent {
  private setupIncomingHandler() {
    this.client.on('message', async (msg) => {
      await this.reportToParent({
        type: 'inbound_message',
        channel: 'whatsapp',
        from: msg.from,
        text: msg.body,
        timestamp: msg.timestamp,
      });
    });
  }
}

// 2. Channel Supervisor routes
class ChannelSupervisor {
  async onReport(message: AgentMessage) {
    if (message.payload.type === 'inbound_message') {
      // Route to conversation supervisor
      await this.coordinateWithPeers(['conversation-supervisor'], {
        action: 'process_message',
        message: message.payload,
        replyChannel: 'whatsapp',
      });
    }
  }
}

// 3. Conversation Supervisor orchestrates
class ConversationSupervisor {
  async onCoordinate(message: AgentMessage) {
    if (message.payload.action === 'process_message') {
      const msg = message.payload.message;
      
      // Get context (parallel)
      const [context, memories] = await Promise.all([
        this.delegate('context-agent', { action: 'get', id: msg.from }),
        this.delegate('memory-agent', { action: 'search', query: msg.text }),
      ]);
      
      // Generate response
      const response = await this.delegate('llm-agent', {
        action: 'generate',
        context,
        memories,
        message: msg.text,
      });
      
      // Send back to channel supervisor
      await this.coordinateWithPeers([message.from], {
        action: 'send_response',
        response: response.text,
        channel: message.payload.replyChannel,
        to: msg.from,
      });
    }
  }
}

// 4. Channel Supervisor sends response
class ChannelSupervisor {
  async onCoordinate(message: AgentMessage) {
    if (message.payload.action === 'send_response') {
      const { channel, to, response } = message.payload;
      
      await this.sendDirective([`${channel}-agent`], {
        action: 'send_message',
        payload: { to, text: response },
      });
    }
  }
}
```

### Scenario 2: Strategic Decision to Reduce Browser Usage

**Trigger**: Browser costs are high this month

```
1. Health Monitor (Strategic)
   ↓ analyzes monthly costs
   ↓ sees browser automation at $500 (budget: $200)
   ↓ sends directive to Resource Allocator
   
2. Resource Allocator (Strategic)
   ↓ decides: reduce browser usage by 60%
   ↓ sends directive to Tool Supervisor
   
3. Tool Supervisor (Tactical)
   ↓ receives directive
   ↓ reduces browser agent pool from 10 to 4
   ↓ implements rate limiting: max 20 browser tasks/hour
   ↓ reports: "browser usage reduced"
   
4. Throughout the day
   ↓ Tool Supervisor queues excess browser requests
   ↓ reports queue depth to Strategic layer
   
5. Resource Allocator (Strategic)
   ↓ monitors queue depth
   ↓ if queue > 50 items, slightly increase budget
   ↓ adaptive optimization
```

### Scenario 3: Execution Agent Crashes

**Failure**: WhatsApp Agent crashes

```
1. Gateway
   ↓ detects agent hasn't sent heartbeat in 1 minute
   ↓ emits event: "agent_offline"
   
2. Channel Supervisor (Tactical)
   ↓ receives event
   ↓ checks if agent is critical
   ↓ WhatsApp is critical (main channel)
   ↓ spawns new WhatsApp Agent
   ↓ re-registers with Gateway
   ↓ reports to Strategic: "recovered from whatsapp failure"
   
3. Resource Allocator (Strategic)
   ↓ sees failure report
   ↓ increments failure counter for WhatsApp
   ↓ if failures > 5 in 1 hour, consider alternatives
   ↓ might send directive: "failover to telegram"
```

---

## Comparison to Flat Architectures

### Flat Architecture (like original openclaw)

```
┌──────────┐
│   User   │
└─────┬────┘
      │
      ▼
┌─────────────────┐
│  Single Agent   │ ←── Makes ALL decisions
│  (Pi/Claude)    │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
WhatsApp  Telegram  Browser  Canvas
```

**Problems**:
- Single agent overwhelmed with decisions
- No separation of strategic vs tactical concerns
- Hard to scale (can't parallelize easily)
- No specialization (one agent does everything)
- Failure of main agent = total failure

### Hierarchical Architecture (proposed)

```
┌──────────┐
│   User   │
└─────┬────┘
      │
      ▼
┌──────────────────┐
│Strategic Layer   │ ←── Long-term decisions
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│Tactical │ │Tactical │ ←── Domain coordination
│Channel  │ │  Tool   │
└────┬────┘ └────┬────┘
     │           │
┌────┴───┐   ┌───┴────┐
▼    ▼   ▼   ▼   ▼    ▼
WA   TG  SL  Br  Ca   FS  ←── Specialized workers
```

**Advantages**:
✅ Specialized agents (each good at one thing)
✅ Scales horizontally (add more execution agents)
✅ Resilient (supervisor can restart failed agents)
✅ Clear decision boundaries (strategic vs tactical)
✅ Efficient (strategic layer doesn't process every message)

---

## Summary

### Key Architectural Principles

1. **Hierarchical Layers**: Strategic → Tactical → Execution
2. **Temporal Stratification**: Days → Hours → Seconds
3. **Message-Based Communication**: Directives down, Reports up
4. **Gateway as Nervous System**: Central routing + registry
5. **Specialized Agents**: Single responsibility per agent
6. **State Distribution**: Global → Domain → Minimal
7. **Resilience Patterns**: Supervisors manage agent lifecycle
8. **Scalability**: Horizontal scaling at execution layer

### When to Use This Architecture

**Use hierarchical multi-agent when**:
- System has multiple distinct domains (channels, tools, etc.)
- Need to scale execution independently
- Want clear separation of strategic vs tactical decisions
- Require resilience (supervisor can restart failed agents)
- Building a long-running system (not just one-off tasks)

**Stick with flat architecture when**:
- Simple use case (< 5 agents)
- All decisions are similar complexity
- No need for different time horizons
- Prototype or MVP

### Next Steps

1. Start with the step-by-step guide
2. Build execution layer first (bottom-up)
3. Add tactical supervisors
4. Finally add strategic coordinators
5. Iterate and refine based on your specific needs

This architecture is **extensible**, **maintainable**, and **production-ready**. 🚀
