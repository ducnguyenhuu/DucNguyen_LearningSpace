# IT Helpdesk AI Chatbot - Research Project Definition

**Project Name:** Multi-Agent IT Helpdesk Self-Service Portal  
**Date Created:** February 4, 2026  
**Status:** Research & Exploration Phase  
**Owner:** Duc Nguyen

---

## 1. Executive Summary

This research project aims to develop an AI-powered chatbot system that acts as a self-service portal for IT helpdesk operations. The system will use a multi-agent architecture built with Microsoft Agent Framework (Python) and hosted on Azure Foundry, with a focus on intelligent ticket classification, prioritization, and routing while minimizing Azure costs.

**Key Innovation:** The research focuses on the **intelligence layer** - agents that understand issues and identify appropriate actions - without implementing actual system integrations. This allows validation of the multi-agent coordination patterns before committing to production integrations.

---

## 2. Problem Statement

IT helpdesk teams handle repetitive, common requests that could be automated through self-service:
- Password resets
- User onboarding/boarding to systems
- [Additional common requests to be identified]

**Current Pain Points:**
- High volume of repetitive tickets
- Delayed response times
- After-hours support limitations
- Manual ticket classification and routing

---

## 3. Project Goals & Objectives

### Primary Goals:
1. **Explore Multi-Agent Coordination Patterns** for IT helpdesk automation
2. **Validate Intelligent Routing** - Test agent capability to understand, classify, prioritize, and route requests
3. **Cost-Effective Azure Implementation** - Identify optimal Azure services and configurations for minimal cost
4. **Research Prototype Development** - Build working system that demonstrates the intelligence layer

### Learning Objectives:
- Understand multi-agent architecture patterns using Microsoft Agent Framework
- Evaluate different Azure AI services and their cost implications
- Test conversational AI effectiveness for IT support scenarios
- Explore RAG (Retrieval Augmented Generation) for knowledge base integration
- Validate classification and routing algorithms

---

## 4. Scope Definition

### In Scope (Research Phase):
✅ **Conversational UI** - User interface for chatbot interaction  
✅ **Issue Understanding** - Agent comprehends user's IT problem  
✅ **Ticket Classification** - Categorizes issue type (Account, Access, Hardware, Software, Network)  
✅ **Priority Assessment** - Determines urgency and impact  
✅ **Intelligent Routing** - Routes to appropriate specialist agent  
✅ **Action Identification** - Agent identifies what action should be taken  
✅ **Intent Structure Output** - Returns structured recommendation (e.g., `{action: "reset_password", user: "john@company.com", confidence: 0.95}`)

### Out of Scope (Production Phase):
❌ **Actual System Integration** - No direct execution of password resets, user provisioning, etc.  
❌ **Backend Service Connections** - No integration with Active Directory, HR systems, etc.  
❌ **Production-Level Security** - Basic auth sufficient for research  
❌ **Enterprise Scale Testing** - Focus on proof of concept, not high-volume testing

### Research Boundary:
The system will **stop at action recommendation** - demonstrating the agent knows what to do, without actually doing it. This allows:
- Faster iteration on AI logic
- Reduced complexity and cost
- Focus on the intelligence and routing patterns
- Easy transition to production (attach action executors later)

---

## 5. Architecture Design

### Multi-Agent System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (Web)                     │
│                  Chat Interface + History                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                          │
│  • Receives user input                                       │
│  • Manages conversation flow                                 │
│  • Coordinates specialist agents                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               CLASSIFICATION AGENT                           │
│  • Understands user issue                                    │
│  • Classifies ticket type                                    │
│  • Determines priority (Low/Medium/High/Critical)            │
│  • Routes to appropriate specialist                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┬───────────────┐
          ▼                       ▼               ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ ACCOUNT MGT      │  │ ONBOARDING       │  │ ESCALATION       │
│ AGENT            │  │ AGENT            │  │ AGENT            │
│                  │  │                  │  │                  │
│ • Password reset │  │ • New user setup │  │ • Complex issues │
│ • Access rights  │  │ • System access  │  │ • Human handoff  │
│ • Permissions    │  │ • Provisioning   │  │ • Ticket creation│
└──────────────────┘  └──────────────────┘  └──────────────────┘
          │                       │               │
          └───────────┬───────────┴───────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  ACTION IDENTIFIER                           │
│  Returns structured intent:                                  │
│  {                                                           │
│    "action": "reset_password",                              │
│    "target_user": "john@company.com",                       │
│    "confidence": 0.95,                                       │
│    "reasoning": "User explicitly requested password reset"  │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities:

**1. Orchestrator Agent:**
- Entry point for all user interactions
- Maintains conversation context
- Coordinates between specialist agents
- Handles clarifying questions

**2. Classification Agent:**
- Analyzes user input to understand the issue
- Classifies into categories: Account, Access, Hardware, Software, Network
- Assesses priority based on urgency keywords, user role, impact
- Routes to appropriate specialist agent

**3. Specialist Agents:**
- **Account Management Agent:** Password resets, permissions, access rights
- **Onboarding Agent:** New user setup, system access provisioning
- **Escalation Agent:** Complex issues, human handoff, ticket creation
- *[Additional agents can be added based on needs]*

**4. Action Identifier:**
- Outputs structured intent with action, parameters, and confidence
- Validates action feasibility
- Provides reasoning for transparency

---

## 6. Technical Stack

### Core Technologies:
- **Agent Framework:** Microsoft Agent Framework (Python)
- **LLM Service:** Azure OpenAI Service
- **Platform:** Azure Foundry
- **Programming Language:** Python
- **UI Framework:** [TBD - Web-based chat interface]

### Azure Services (Cost-Optimized):
- **Azure OpenAI Service** - Pay-per-token model with rate limiting
- **Azure AI Search** - For knowledge base retrieval (if using RAG)
- **Azure Functions** - Lightweight orchestration (Consumption Plan)
- **Azure Storage** - Conversation history and logs (lowest tier)
- **Azure Container Apps** - Agent hosting (scale-to-zero enabled)

### Cost Optimization Strategies:
1. Use **Dev/Test tiers** where available
2. Implement **aggressive caching** to reduce LLM calls
3. **Rate limiting** and request throttling
4. **Scale-to-zero** for non-production hours
5. **Prompt optimization** to minimize token usage
6. **Local development** using mock services where possible

---

## 7. Use Cases

### Primary Use Cases (Research Phase):

#### Use Case 1: Password Reset
**User Input:** "I forgot my password and can't log in"  
**Expected Flow:**
1. Orchestrator receives request
2. Classification Agent identifies → Account Management issue, High Priority
3. Routes to Account Management Agent
4. Agent asks clarifying questions (username, email verification)
5. Action Identifier outputs:
   ```json
   {
     "action": "reset_password",
     "target_user": "john@company.com",
     "confidence": 0.98,
     "next_steps": ["Send password reset email", "Verify user identity"]
   }
   ```

#### Use Case 2: New User Onboarding
**User Input:** "We have a new employee starting Monday, need to set them up"  
**Expected Flow:**
1. Orchestrator receives request
2. Classification Agent identifies → Onboarding issue, Medium Priority
3. Routes to Onboarding Agent
4. Agent collects information (name, department, role, start date)
5. Action Identifier outputs:
   ```json
   {
     "action": "onboard_user",
     "user_details": {
       "name": "Jane Smith",
       "department": "Marketing",
       "start_date": "2026-02-10"
     },
     "confidence": 0.92,
     "required_systems": ["Email", "VPN", "Slack", "CRM"]
   }
   ```

#### Use Case 3: Complex Issue (Escalation)
**User Input:** "My computer keeps freezing and I have a presentation in 30 minutes"  
**Expected Flow:**
1. Orchestrator receives request
2. Classification Agent identifies → Hardware issue, Critical Priority, Complex
3. Routes to Escalation Agent
4. Agent attempts basic troubleshooting questions
5. Action Identifier outputs:
   ```json
   {
     "action": "create_urgent_ticket",
     "priority": "critical",
     "category": "hardware",
     "confidence": 0.85,
     "reasoning": "Time-sensitive, requires hands-on support",
     "escalate_to": "Senior Technician"
   }
   ```

---

## 8. Knowledge Base & Context

### Information Sources:
- **IT Policies & Procedures** - Company-specific guidelines
- **Common Troubleshooting Steps** - Knowledge articles for common issues
- **FAQ Database** - Frequently asked questions and answers
- **System Documentation** - Technical documentation for internal systems

### Context Requirements:
- **User History** - Previous tickets/interactions (simulated for research)
- **System Status** - Current known outages/issues (simulated)
- **User Profile** - Role, department, permissions level (mock data)

### RAG Implementation:
- Azure AI Search for semantic search over knowledge base
- Vector embeddings for similarity matching
- Chunking strategy for large documents
- Relevance scoring and re-ranking

---

## 9. Classification & Priority Logic

### Classification Categories:
1. **Account Management** - Passwords, permissions, access rights
2. **Onboarding/Offboarding** - New users, departing users
3. **Hardware** - Computer issues, peripherals, equipment
4. **Software** - Application problems, licenses, installation
5. **Network** - Connectivity, VPN, Wi-Fi issues
6. **General Inquiry** - Questions, documentation requests

### Priority Determination:

**Critical:**
- Impacts multiple users or entire team
- Business-critical system down
- Time-sensitive (urgent meeting, deadline)
- Security incident

**High:**
- Single user unable to work
- Key system degraded performance
- Urgent keywords ("ASAP", "emergency", "urgent")

**Medium:**
- Partial functionality impaired
- Workaround available
- Standard requests (password reset, access request)

**Low:**
- Information requests
- Non-urgent improvements
- Documentation questions

---

## 10. Conversation Flow Design

### User Experience:

**Scenario: Visible Single-Agent Interface**
```
User: "I can't log into my email"

Bot: "I understand you're having trouble accessing your email. Let me help you 
      with that. Can you tell me:
      1. Are you getting an error message?
      2. Have you tried resetting your password recently?"

User: "Yes, it says invalid password. I haven't reset it."

Bot: "Got it. I can help you reset your password. To verify your identity, 
      can you confirm your username or employee email address?"

User: "john.doe@company.com"

Bot: "✓ I've identified this as an Account Management issue (High Priority).
     
     Recommended Action: Reset Password
     User: john.doe@company.com
     Confidence: 98%
     
     In production, this would trigger a password reset email to your 
     registered email address. You would receive instructions within 
     5 minutes."
```

### Clarification Handling:
- Agent asks targeted follow-up questions when confidence is low
- Maximum 3 clarifying questions before escalation
- Provides options/suggestions when user is unclear

---

## 11. Success Metrics & Validation

### Research Success Criteria:

**Technical Validation:**
- [ ] Multi-agent system successfully routes 90%+ of test cases to correct specialist
- [ ] Classification accuracy > 85% on test dataset
- [ ] Priority assessment aligns with manual assessment in 80%+ cases
- [ ] Action identification has >90% confidence on clear requests
- [ ] System responds within 3 seconds for simple queries

**Cost Validation:**
- [ ] Monthly Azure cost stays under $[specify budget] during research phase
- [ ] Token usage per conversation tracked and optimized
- [ ] Cost per interaction calculated and documented

**User Experience Validation:**
- [ ] Conversation feels natural (subjective team evaluation)
- [ ] Clarifying questions are relevant and minimal
- [ ] Agent correctly handles ambiguous requests
- [ ] System gracefully handles out-of-scope questions

### Deliverables:

**Code Artifacts:**
- [ ] Working multi-agent chatbot prototype
- [ ] Agent implementation in Microsoft Agent Framework
- [ ] Web-based UI for interaction
- [ ] Test suite with sample conversations

**Documentation:**
- [ ] Architecture decision records (ADRs)
- [ ] Agent design specifications
- [ ] Knowledge base structure and examples
- [ ] Cost analysis report

**Research Outputs:**
- [ ] Multi-agent coordination pattern analysis
- [ ] Azure service comparison and cost breakdown
- [ ] Lessons learned and recommendations
- [ ] Production implementation roadmap

---

## 12. Risk Assessment & Mitigation

### Potential Risks:

**1. High Azure Costs:**
- **Mitigation:** Implement rate limiting, aggressive caching, use dev tiers
- **Monitoring:** Daily cost tracking with alerts

**2. Low Classification Accuracy:**
- **Mitigation:** Iterative prompt engineering, expanded training examples
- **Fallback:** Escalation agent for uncertain cases

**3. Complex Agent Coordination:**
- **Mitigation:** Start with simple 2-3 agent system, expand gradually
- **Testing:** Comprehensive test cases for routing logic

**4. Scope Creep (Adding Real Integrations):**
- **Mitigation:** Clear research boundary, document "production phase" separately
- **Discipline:** Focus on intelligence layer validation

**5. Knowledge Base Quality:**
- **Mitigation:** Start with curated subset, expand iteratively
- **Validation:** Test retrieval relevance regularly

---

## 13. Open Questions & Decisions Needed

### Questions to Resolve:

**Architecture:**
- [ ] How many specialist agents are needed? (Start with 3, expand to 5+?)
- [ ] Should users see agent handoffs or transparent single interface?
- [ ] How to handle multi-turn conversations and context retention?

**Technical:**
- [ ] Which Azure OpenAI model to use? (GPT-4 vs GPT-4 Turbo vs GPT-3.5)
- [ ] RAG approach - Azure AI Search vs custom vector DB vs simple keyword search?
- [ ] How to structure agent prompts for consistency?

**Testing:**
- [ ] How many test conversations needed for validation?
- [ ] Real user testing vs synthetic test cases?
- [ ] How to create realistic test dataset?

**Knowledge Base:**
- [ ] Build from scratch or use existing IT documentation?
- [ ] How much content needed for MVP?
- [ ] Update frequency and maintenance approach?

---

## 14. Next Steps & Action Plan

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up Azure Foundry environment with cost controls
- [ ] Configure Azure OpenAI Service with rate limiting
- [ ] Install Microsoft Agent Framework and dependencies
- [ ] Create simple single-agent proof of concept
- [ ] Develop basic web UI for chat interaction

### Phase 2: Multi-Agent Architecture (Weeks 3-4)
- [ ] Design agent communication protocol
- [ ] Implement Orchestrator Agent
- [ ] Implement Classification Agent with routing logic
- [ ] Create 2-3 specialist agents (Account Mgmt, Onboarding, Escalation)
- [ ] Test agent coordination with sample conversations

### Phase 3: Intelligence Layer (Weeks 5-6)
- [ ] Develop classification taxonomy and priority logic
- [ ] Build action identification structure and templates
- [ ] Create test dataset of common helpdesk scenarios
- [ ] Implement and test routing accuracy
- [ ] Optimize prompts for token efficiency

### Phase 4: Knowledge Base & RAG (Weeks 7-8)
- [ ] Curate initial knowledge base content (policies, FAQs, procedures)
- [ ] Implement RAG with Azure AI Search
- [ ] Test retrieval accuracy and relevance
- [ ] Optimize chunking and embedding strategy

### Phase 5: Testing & Validation (Weeks 9-10)
- [ ] Run comprehensive test suite
- [ ] Measure classification and routing accuracy
- [ ] Calculate cost per conversation
- [ ] Conduct internal user testing
- [ ] Document findings and lessons learned

### Phase 6: Documentation & Recommendations (Weeks 11-12)
- [ ] Write architecture decision records
- [ ] Create production implementation roadmap
- [ ] Document cost optimization strategies
- [ ] Prepare research findings presentation
- [ ] Identify gaps and future research areas

---

## 15. Budget & Resource Allocation

### Estimated Azure Costs (Research Phase):
- **Azure OpenAI Service:** $50-150/month (with rate limiting)
- **Azure AI Search:** $20-50/month (Basic tier)
- **Azure Container Apps:** $10-30/month (Consumption plan)
- **Azure Storage:** $5-10/month (Minimal usage)
- **Total Estimated:** $85-240/month

### Time Investment:
- **Research & Planning:** 20 hours
- **Development:** 60-80 hours
- **Testing & Validation:** 20-30 hours
- **Documentation:** 15-20 hours
- **Total:** ~120-150 hours (3-4 months part-time)

---

## 16. Future Considerations (Production Phase)

When transitioning to production, address:

**System Integrations:**
- Active Directory / Entra ID for authentication
- HR systems for user provisioning
- Ticketing system (ServiceNow, Jira, etc.)
- Notification services (email, SMS, Teams)

**Security & Compliance:**
- Production-level authentication and authorization
- Data encryption at rest and in transit
- Audit logging and compliance tracking
- PII handling and data retention policies

**Scale & Performance:**
- Load testing and capacity planning
- High availability and disaster recovery
- Performance monitoring and alerting
- Auto-scaling configuration

**Governance:**
- Agent behavior monitoring and guardrails
- Feedback loop for continuous improvement
- Model versioning and rollback strategy
- Incident response procedures

---

## 17. References & Resources

### Microsoft Agent Framework:
- [Microsoft Agent Framework Documentation](https://docs.microsoft.com/azure/ai/)
- [Azure OpenAI Service Best Practices](https://docs.microsoft.com/azure/openai/)
- [Multi-Agent Patterns and Examples](https://github.com/microsoft/agent-framework/)

### Related Research:
- Multi-agent system design patterns
- Conversational AI for enterprise support
- RAG optimization techniques
- Azure cost optimization strategies

---

## Document Control

**Version:** 1.0  
**Last Updated:** February 4, 2026  
**Next Review:** [After Phase 1 completion]  
**Status:** Active Research Project

**Change Log:**
- 2026-02-04: Initial research project definition created via Advanced Elicitation workflow

---

## Notes & Observations

This research project focuses on validating the intelligence and coordination aspects of a multi-agent IT helpdesk system. By stopping at action identification rather than execution, we can:

1. **Iterate faster** on the AI logic without complex integration overhead
2. **Validate core patterns** before committing to production architecture
3. **Minimize costs** during the learning and experimentation phase
4. **Demonstrate value** with a working prototype that shows intelligence
5. **Smooth transition** to production by adding action executors to validated agents

The modular architecture allows for easy expansion - additional specialist agents can be added as new use cases emerge, and the action execution layer can be built incrementally based on priority.

---

**🎯 Ready to begin Phase 1: Foundation Setup**
