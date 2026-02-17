# Azure Service Bus - Topic & Pub/Sub Flow

## Kiến trúc tổng quan

```mermaid
flowchart TB
    subgraph Publishers["📤 PUBLISHERS (Gửi tin)"]
        direction LR
        P1["Order Service"]
        P2["Payment Service"]
        P3["User Service"]
    end
    
    subgraph ServiceBus["☁️ AZURE SERVICE BUS"]
        direction TB
        Topic["📢 Topic: orders-events"]
        
        subgraph Subscriptions["Subscriptions (Mailboxes)"]
            direction TB
            Sub1["📬 email-service<br/>Queue: [msg1, msg2, msg3]"]
            Sub2["📬 sms-service<br/>Queue: [msg1, msg2, msg3]"]
            Sub3["📬 analytics<br/>Queue: [msg1, msg2, msg3]"]
            Sub4["📬 inventory<br/>Filter: OrderType='Physical'<br/>Queue: [msg1, msg3]"]
        end
        
        Topic --> Sub1
        Topic --> Sub2
        Topic --> Sub3
        Topic --> Sub4
    end
    
    subgraph Consumers["📥 CONSUMERS (Nhận & Xử lý)"]
        direction LR
        C1["Email Service<br/>✉️ Send Email"]
        C2["SMS Service<br/>📱 Send SMS"]
        C3["Analytics<br/>📊 Log Data"]
        C4["Inventory<br/>📦 Update Stock"]
    end
    
    P1 -->|"Publish<br/>OrderCreated"| Topic
    P2 -->|"Publish<br/>PaymentReceived"| Topic
    P3 -->|"Publish<br/>UserRegistered"| Topic
    
    Sub1 -.->|Poll Messages| C1
    Sub2 -.->|Poll Messages| C2
    Sub3 -.->|Poll Messages| C3
    Sub4 -.->|Poll Messages| C4
    
    style Publishers fill:#e1f5ff,stroke:#01579b
    style ServiceBus fill:#fff3e0,stroke:#e65100
    style Consumers fill:#e8f5e9,stroke:#1b5e20
    style Topic fill:#ffeb3b,stroke:#f57f17,stroke-width:3px
    style Subscriptions fill:#f3e5f5,stroke:#4a148c
```

## Message Flow chi tiết

```mermaid
sequenceDiagram
    participant OS as Order Service
    participant T as Topic: orders
    participant S1 as Sub: email
    participant S2 as Sub: sms
    participant S3 as Sub: analytics
    participant S4 as Sub: inventory
    participant ES as Email Service
    participant SMS as SMS Service
    participant AN as Analytics
    participant INV as Inventory
    
    Note over OS,T: 1️⃣ PUBLISH MESSAGE
    OS->>T: Publish OrderCreated #123<br/>{OrderId:123, Type:Physical, Amount:500k}
    
    Note over T,S4: 2️⃣ TOPIC DUPLICATES TO ALL SUBS
    T->>S1: Copy message to email queue
    T->>S2: Copy message to sms queue
    T->>S3: Copy message to analytics queue
    T->>S4: Copy (filtered by Type=Physical)
    
    Note over S1,INV: 3️⃣ CONSUMERS POLL & PROCESS
    
    par Email Processing
        ES->>S1: Poll message
        S1-->>ES: Order #123
        ES->>ES: Send email to customer
        ES->>S1: Complete message ✅
    and SMS Processing
        SMS->>S2: Poll message
        S2-->>SMS: Order #123
        SMS->>SMS: Send SMS notification
        SMS->>S2: Complete message ✅
    and Analytics Processing
        AN->>S3: Poll message
        S3-->>AN: Order #123
        AN->>AN: Log to database
        AN->>S3: Complete message ✅
    and Inventory Processing
        INV->>S4: Poll message
        S4-->>INV: Order #123
        INV->>INV: Update stock -1
        INV->>S4: Complete message ✅
    end
    
    Note over OS,INV: ✅ All services processed independently!
```

## Subscription với Filter Rules

```mermaid
flowchart LR
    subgraph Input["📨 INCOMING MESSAGES"]
        direction TB
        M1["Message 1<br/>OrderType: Physical<br/>Amount: 300k"]
        M2["Message 2<br/>OrderType: Digital<br/>Amount: 150k"]
        M3["Message 3<br/>OrderType: Physical<br/>Amount: 1.2M"]
    end
    
    Topic["Topic: orders"]
    
    subgraph Subs["SUBSCRIPTIONS"]
        direction TB
        
        subgraph S1["Sub: all-orders"]
            F1["Filter: NONE<br/>(Accept ALL)"]
            Q1["Queue:<br/>✅ Msg1<br/>✅ Msg2<br/>✅ Msg3"]
        end
        
        subgraph S2["Sub: physical-only"]
            F2["Filter:<br/>OrderType='Physical'"]
            Q2["Queue:<br/>✅ Msg1<br/>❌ Msg2<br/>✅ Msg3"]
        end
        
        subgraph S3["Sub: high-value"]
            F3["Filter:<br/>Amount > 1000000"]
            Q3["Queue:<br/>❌ Msg1<br/>❌ Msg2<br/>✅ Msg3"]
        end
        
        subgraph S4["Sub: physical-high-value"]
            F4["Filter:<br/>Type='Physical'<br/>AND Amount>1M"]
            Q4["Queue:<br/>❌ Msg1<br/>❌ Msg2<br/>✅ Msg3"]
        end
    end
    
    Input --> Topic
    Topic --> S1
    Topic --> S2
    Topic --> S3
    Topic --> S4
    
    style M1 fill:#81c784
    style M2 fill:#64b5f6
    style M3 fill:#ffb74d
    style Topic fill:#ffeb3b,stroke:#f57f17,stroke-width:3px
    style Q1 fill:#c8e6c9
    style Q2 fill:#ffccbc
    style Q3 fill:#f8bbd0
    style Q4 fill:#d1c4e9
```

## Lifecycle của 1 Message

```mermaid
flowchart TD
    Start(("🚀 START"))
    
    Publish["📤 Publisher sends message<br/>to Topic"]
    
    Duplicate{"🔄 Topic duplicates<br/>to subscriptions"}
    
    Filter1["📬 Sub 1: Check filter"]
    Filter2["📬 Sub 2: Check filter"]
    Filter3["📬 Sub 3: Check filter"]
    
    Queue1["✅ Add to Queue 1"]
    Queue2["✅ Add to Queue 2"]
    Queue3["✅ Add to Queue 3"]
    
    Reject1["❌ Rejected by filter"]
    Reject2["❌ Rejected by filter"]
    
    Wait1["⏳ Wait in queue<br/>(Max 14 days)"]
    Wait2["⏳ Wait in queue<br/>(Max 14 days)"]
    Wait3["⏳ Wait in queue<br/>(Max 14 days)"]
    
    Consume1["👤 Consumer 1 polls"]
    Consume2["👤 Consumer 2 polls"]
    Consume3["👤 Consumer 3 polls"]
    
    Lock1["🔒 Message locked<br/>(60s default)"]
    Lock2["🔒 Message locked<br/>(60s default)"]
    Lock3["🔒 Message locked<br/>(60s default)"]
    
    Process1["⚙️ Process message"]
    Process2["⚙️ Process message"]
    Process3["⚙️ Process message"]
    
    Success1{"✅ Success?"}
    Success2{"✅ Success?"}
    Success3{"✅ Success?"}
    
    Complete1["🗑️ Complete & Delete"]
    Complete2["🗑️ Complete & Delete"]
    Complete3["🗑️ Complete & Delete"]
    
    Retry1["🔄 Return to queue<br/>Retry count +1"]
    Retry2["🔄 Return to queue<br/>Retry count +1"]
    Retry3["🔄 Return to queue<br/>Retry count +1"]
    
    MaxRetry1{"Max retries<br/>reached?"}
    MaxRetry2{"Max retries<br/>reached?"}
    MaxRetry3{"Max retries<br/>reached?"}
    
    DLQ1["☠️ Move to<br/>Dead Letter Queue"]
    DLQ2["☠️ Move to<br/>Dead Letter Queue"]
    DLQ3["☠️ Move to<br/>Dead Letter Queue"]
    
    End1(("✅ END"))
    End2(("✅ END"))
    End3(("✅ END"))
    
    Start --> Publish
    Publish --> Duplicate
    
    Duplicate --> Filter1
    Duplicate --> Filter2
    Duplicate --> Filter3
    
    Filter1 -->|Pass| Queue1
    Filter1 -->|Fail| Reject1
    Filter2 -->|Pass| Queue2
    Filter2 -->|Fail| Reject2
    Filter3 -->|Pass| Queue3
    
    Reject1 --> End1
    Reject2 --> End2
    
    Queue1 --> Wait1
    Queue2 --> Wait2
    Queue3 --> Wait3
    
    Wait1 --> Consume1
    Wait2 --> Consume2
    Wait3 --> Consume3
    
    Consume1 --> Lock1
    Consume2 --> Lock2
    Consume3 --> Lock3
    
    Lock1 --> Process1
    Lock2 --> Process2
    Lock3 --> Process3
    
    Process1 --> Success1
    Process2 --> Success2
    Process3 --> Success3
    
    Success1 -->|Yes| Complete1
    Success2 -->|Yes| Complete2
    Success3 -->|Yes| Complete3
    
    Success1 -->|No| Retry1
    Success2 -->|No| Retry2
    Success3 -->|No| Retry3
    
    Complete1 --> End1
    Complete2 --> End2
    Complete3 --> End3
    
    Retry1 --> MaxRetry1
    Retry2 --> MaxRetry2
    Retry3 --> MaxRetry3
    
    MaxRetry1 -->|No| Wait1
    MaxRetry2 -->|No| Wait2
    MaxRetry3 -->|No| Wait3
    
    MaxRetry1 -->|Yes| DLQ1
    MaxRetry2 -->|Yes| DLQ2
    MaxRetry3 -->|Yes| DLQ3
    
    DLQ1 --> End1
    DLQ2 --> End2
    DLQ3 --> End3
    
    style Start fill:#4caf50,stroke:#2e7d32,color:#fff
    style Publish fill:#2196f3,stroke:#1565c0,color:#fff
    style Duplicate fill:#ff9800,stroke:#e65100,color:#fff
    style Queue1 fill:#81c784,stroke:#388e3c
    style Queue2 fill:#81c784,stroke:#388e3c
    style Queue3 fill:#81c784,stroke:#388e3c
    style Complete1 fill:#4caf50,stroke:#2e7d32,color:#fff
    style Complete2 fill:#4caf50,stroke:#2e7d32,color:#fff
    style Complete3 fill:#4caf50,stroke:#2e7d32,color:#fff
    style DLQ1 fill:#f44336,stroke:#c62828,color:#fff
    style DLQ2 fill:#f44336,stroke:#c62828,color:#fff
    style DLQ3 fill:#f44336,stroke:#c62828,color:#fff
    style Reject1 fill:#ffcdd2,stroke:#c62828
    style Reject2 fill:#ffcdd2,stroke:#c62828
    style End1 fill:#4caf50,stroke:#2e7d32,color:#fff
    style End2 fill:#4caf50,stroke:#2e7d32,color:#fff
    style End3 fill:#4caf50,stroke:#2e7d32,color:#fff
```

## So sánh Queue vs Topic/Subscription

```mermaid
flowchart TB
    subgraph Queue["🔵 QUEUE Pattern (Point-to-Point)"]
        direction LR
        QP["Producer"]
        QQ["Queue"]
        QC["Consumer"]
        
        QP -->|Send| QQ
        QQ -->|1 message| QC
        
        Note1["✅ 1 sender → 1 receiver<br/>✅ Simple job processing<br/>❌ Chỉ 1 consumer"]
    end
    
    subgraph Topic["🟢 TOPIC/SUBSCRIPTION Pattern (Pub/Sub)"]
        direction TB
        TP["Publisher"]
        TT["Topic"]
        
        subgraph TSubs["Subscriptions"]
            TS1["Sub 1"]
            TS2["Sub 2"]
            TS3["Sub 3"]
        end
        
        TC1["Consumer 1"]
        TC2["Consumer 2"]
        TC3["Consumer 3"]
        
        TP -->|Publish| TT
        TT -->|Copy| TS1
        TT -->|Copy| TS2
        TT -->|Copy| TS3
        TS1 -.-> TC1
        TS2 -.-> TC2
        TS3 -.-> TC3
        
        Note2["✅ 1 sender → Many receivers<br/>✅ Event broadcasting<br/>✅ Independent processing<br/>✅ Filter messages"]
    end
    
    style Queue fill:#e3f2fd,stroke:#1565c0
    style Topic fill:#e8f5e9,stroke:#2e7d32
    style QQ fill:#64b5f6,stroke:#1976d2,stroke-width:2px
    style TT fill:#81c784,stroke:#388e3c,stroke-width:2px
```
