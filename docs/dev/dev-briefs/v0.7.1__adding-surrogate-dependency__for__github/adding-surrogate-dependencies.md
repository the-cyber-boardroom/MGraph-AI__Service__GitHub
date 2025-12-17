# Surrogate Dependencies with OSBot-Fast-API

**Purpose**: Guide for LLMs building surrogate dependencies using OSBot Fast_API and Type_Safe  
**Scope**: Architecture, patterns, and implementation strategies for offline-first development  
**Prerequisites**: Type_Safe documentation (v3.1.1+), Fast_API Routes Guide (v0.24.2+)  
**Version**: v0.1.0 (December 2025)

## What Are Surrogate Dependencies?

Surrogate dependencies are **stand-in implementations** of external services that allow applications to run without network connectivity. Unlike traditional testing approaches:

| Approach | Data Source | Purpose | Realism |
|----------|-------------|---------|---------|
| **Stub** | Hand-crafted minimal responses | Unit testing | Low |
| **Mock** | Behavior expectations | Verification | Low |
| **Surrogate** | Real captured API responses | Offline development | High |

Surrogates act as an **"evolved cache"** — they replay actual API responses, preserving the exact structure, edge cases, and quirks of the real service. This enables:

- **Offline-first development**: Work without connectivity or backend availability
- **Fast feedback loops**: No network latency, no rate limits
- **Contract locking**: Captured responses document actual API behavior
- **Deterministic testing**: Same inputs always produce same outputs
- **Security testing**: Explore edge cases without hitting production

## Core Concepts

### The Surrogate Triad

Every surrogate implementation has three components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Surrogate Service                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Surrogate      │  │    Routes       │  │   Schemas   │ │
│  │    State        │──│  (Fast_API      │──│  (Type_Safe │ │
│  │  (Type_Safe)    │  │   __Routes)     │  │   models)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

1. **Surrogate State**: In-memory Type_Safe class holding service data
2. **Routes**: Fast_API__Routes class exposing HTTP endpoints
3. **Schemas**: Type_Safe request/response models matching real API contracts

### Design Principles

1. **Mirror the Real API**: Surrogate endpoints should match real API paths and response shapes
2. **Use Real Data**: Capture actual responses rather than inventing test data
3. **Isolate State**: Each surrogate manages its own state, resettable between tests
4. **Type Everything**: Use Type_Safe for state, schemas, and service classes
5. **No Pydantic**: Always Type_Safe — consistent with the rest of the stack

## Architecture

### File Structure

```
project/
├── surrogates/
│   ├── [service_name]/
│   │   ├── Surrogate__Service__[Service].py      # Main service wrapper
│   │   ├── Surrogate__State__[Service].py        # In-memory data store
│   │   ├── routes/
│   │   │   └── Routes__Surrogate__[Service].py   # HTTP endpoints
│   │   └── schemas/
│   │       └── Schema__[Service]__*.py           # Request/response models
│   └── surrogate_data/
│       └── [service_name]/
│           └── *.json                            # Captured responses
├── services/
│   └── [service_name]/
│       └── Client__[Service].py                  # Client with surrogate toggle
└── tests/
    └── surrogates/
        └── test__Surrogate__[Service].py
```

### Naming Conventions

| Component | Pattern | Example |
|-----------|---------|---------|
| State class | `Surrogate__State__[Service]` | `Surrogate__State__Stripe` |
| Service class | `Surrogate__Service__[Service]` | `Surrogate__Service__Stripe` |
| Routes class | `Routes__Surrogate__[Service]` | `Routes__Surrogate__Stripe` |
| Feature routes | `Routes__Surrogate__[Service]__[Feature]` | `Routes__Surrogate__Stripe__Payments` |
| URL tag | `[service]-surrogate` | `stripe-surrogate` |

## Implementation Patterns

### Pattern 1: Surrogate State

The state class holds all in-memory data for the surrogate:

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing                          import Dict, List, Optional

class Surrogate__State__[Service](Type_Safe):
    # Data stores - use Dict for indexed access, List for collections
    [entities]    : Dict[str, Dict]                                          # id -> entity data
    [collections] : List[Dict]                                               # ordered items
    
    # Configuration - realistic defaults matching real service
    [config_field]: str = '[default_value]'
    
    def reset(self):                                                         # REQUIRED - clean state for tests
        self.[entities]    = {}
        self.[collections] = []
        return self
    
    # Helper methods for consistent key generation
    def [entity]_key(self, *args) -> str:
        return '/'.join(str(arg) for arg in args)
```

**Key principles**:
- All fields must have type annotations
- Collections auto-initialize (Type_Safe behavior)
- Always implement `reset()` for test isolation
- Add helper methods for key generation patterns

### Pattern 2: Schema Design

Schemas define the contract between client and surrogate:

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing                          import List, Optional, Literal

# Request schemas - match real API input
class Schema__[Service]__[Action]__Request(Type_Safe):
    [required_field] : Safe_Str__[Domain]                                    # Use appropriate Safe type
    [optional_field] : Optional[Safe_Str__[Domain]] = None
    [enum_field]     : Literal['option_a', 'option_b'] = 'option_a'

# Response wrapper - consistent structure
class Schema__Response__Context(Type_Safe):
    success     : bool       = True
    status_code : int        = 200
    errors      : List[str]
    messages    : List[str]

# Response schemas - match real API output
class Schema__[Service]__[Entity](Type_Safe):
    id         : str
    [field]    : [Type]
    created_at : str = ''
    updated_at : str = ''
```

**Key principles**:
- Use Safe_* primitives for validated input (see Safe Primitives Reference)
- Match real API field names exactly
- Use consistent response wrapper pattern
- Keep schemas pure — no business logic

### Pattern 3: Route Implementation

Routes expose surrogate endpoints via Fast_API__Routes:

```python
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from typing                                     import Dict, Any, List

TAG__ROUTES_[SERVICE]_SURROGATE = '[service]-surrogate'
ROUTES_PATHS__[SERVICE]_SURROGATE = [
    f'/{TAG__ROUTES_[SERVICE]_SURROGATE}/[endpoint-a]',
    f'/{TAG__ROUTES_[SERVICE]_SURROGATE}/[endpoint-b]',
]

class Routes__Surrogate__[Service](Fast_API__Routes):
    tag             : str = TAG__ROUTES_[SERVICE]_SURROGATE
    surrogate_state : Surrogate__State__[Service]                            # Auto-initialized by Type_Safe
    
    # GET endpoint - retrieve data
    def [endpoint_name](self) -> Dict[str, Any]:
        return dict(response_context = dict(success     = True ,
                                            status_code = 200  ),
                    response_data    = self.surrogate_state.[data])
    
    # POST endpoint - with request body
    def [endpoint_name](self, request: Schema__[Service]__Request
                        ) -> Dict[str, Any]:
        # Process request, update state
        key = self.surrogate_state.[entity]_key(request.[field])
        self.surrogate_state.[entities][key] = request.obj()
        
        return dict(response_context = dict(success     = True ,
                                            status_code = 201  ),
                    response_data    = dict(created = True))
    
    # Error handling pattern
    def [get_endpoint](self, request: Schema__Request) -> Dict[str, Any]:
        key = self.surrogate_state.[entity]_key(request.[field])
        
        if key not in self.surrogate_state.[entities]:
            return dict(response_context = dict(success     = False          ,
                                                status_code = 404            ,
                                                errors      = ['Not found']  ),
                        response_data    = {}                                )
        
        return dict(response_context = dict(success     = True  ,
                                            status_code = 200   ),
                    response_data    = self.surrogate_state.[entities][key])
    
    def setup_routes(self):                                                  # REQUIRED
        self.add_route_get   (self.[get_endpoint]   )
        self.add_route_post  (self.[create_endpoint])
        self.add_route_put   (self.[update_endpoint])
        self.add_route_delete(self.[delete_endpoint])
        return self
```

**Key principles**:
- Method names generate URL paths (underscores → hyphens, double underscore → path segment)
- Always return consistent response structure
- Handle error cases explicitly with appropriate status codes
- Implement `setup_routes()` to register all endpoints

### Pattern 4: Service Wrapper

The service class wires everything together:

```python
from osbot_fast_api.api.Fast_API__Service import Fast_API__Service
from starlette.testclient                 import TestClient

class Surrogate__Service__[Service](Fast_API__Service):
    service_name : str = '[Service] Surrogate Service'
    
    routes_[feature] : Routes__Surrogate__[Service]                          # Auto-initialized
    
    def setup_routes(self):
        self.routes_[feature].setup_routes()
        return self
    
    def setup(self):
        super().setup()
        self.setup_routes()
        return self
    
    def reset_state(self):                                                   # Reset all route states
        self.routes_[feature].surrogate_state.reset()
        return self
    
    def create_client(self) -> TestClient:
        return TestClient(self.app())
```

### Pattern 5: Live/Surrogate Toggle

Design clients to switch between real and surrogate modes:

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from typing                          import Literal
import os

class Client__[Service](Type_Safe):
    mode             : Literal['live', 'surrogate'] = 'live'
    live_base_url    : str = 'https://api.[service].com'
    surrogate_client : TestClient = None
    
    @classmethod
    def from_env(cls) -> 'Client__[Service]':
        mode = 'surrogate' if os.environ.get('USE_SURROGATES') == 'true' else 'live'
        return cls(mode=mode)
    
    def [api_method](self, **kwargs):
        if self.mode == 'surrogate':
            response = self.surrogate_client.post(
                '/[service]-surrogate/[endpoint]',
                json=kwargs)
            return response.json()
        
        # Real API call
        return self._http_post('/[endpoint]', kwargs)
```

## Testing Strategies

### Unit Testing Routes Directly

```python
from unittest import TestCase

class Test__Routes__Surrogate__[Service](TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.surrogate = Surrogate__Service__[Service]().setup()
        cls.routes    = cls.surrogate.routes_[feature]
    
    def setUp(self):
        self.routes.surrogate_state.reset()                                  # Isolate each test
    
    def test__[endpoint]__success(self):
        request  = Schema__[Service]__Request([field]='value')
        response = self.routes.[endpoint](request)
        
        assert response['response_context']['success'] is True
    
    def test__[endpoint]__not_found(self):
        request  = Schema__[Service]__Request([field]='nonexistent')
        response = self.routes.[endpoint](request)
        
        assert response['response_context']['success']     is False
        assert response['response_context']['status_code'] == 404
```

### Integration Testing via HTTP

```python
class Test__Surrogate__[Service]__Integration(TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.surrogate = Surrogate__Service__[Service]().setup()
        cls.client    = TestClient(cls.surrogate.app())
    
    def setUp(self):
        self.surrogate.reset_state()
    
    def test__roundtrip__create_and_retrieve(self):
        # Create
        create_response = self.client.post(
            '/[service]-surrogate/[create-endpoint]',
            json={'[field]': 'test-value'})
        assert create_response.status_code == 200
        
        # Retrieve
        get_response = self.client.post(
            '/[service]-surrogate/[get-endpoint]',
            json={'[field]': 'test-value'})
        assert get_response.json()['response_context']['success'] is True
```

## Advanced Patterns

### Recording Real Responses

Capture live API responses for replay:

```python
from osbot_utils.type_safe.Type_Safe import Type_Safe
from pathlib                         import Path
import json

class Surrogate__Recorder(Type_Safe):
    enabled       : bool = False
    output_path   : str  = './surrogates/surrogate_data'
    
    def record(self, service  : str  ,
                     endpoint : str  ,
                     request  : dict ,
                     response : dict ):
        if not self.enabled:
            return
        
        path = Path(self.output_path) / service / endpoint.replace('/', '_')
        path.mkdir(parents=True, exist_ok=True)
        
        filepath = path / f"{hash(json.dumps(request, sort_keys=True)) % 100000}.json"
        filepath.write_text(json.dumps(dict(request  = request ,
                                            response = response), indent=2))
```

### Loading Captured Data

Initialize surrogate state from recorded JSON:

```python
class Surrogate__State__[Service](Type_Safe):
    # ... fields ...
    
    def load_from_json(self, json_path: str):
        data = json.loads(Path(json_path).read_text())
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self
    
    def load_from_directory(self, dir_path: str):
        for json_file in Path(dir_path).glob('*.json'):
            self.load_from_json(str(json_file))
        return self
```

### Simulating Service Behaviors

#### Rate Limiting

```python
class Surrogate__State__With_Rate_Limit(Type_Safe):
    requests_remaining : int = 1000
    requests_limit     : int = 1000
    
    def consume_request(self) -> bool:                                       # Returns True if allowed
        if self.requests_remaining <= 0:
            return False
        self.requests_remaining -= 1
        return True
    
    def rate_limit_response(self) -> Dict[str, Any]:
        return dict(response_context = dict(success     = False             ,
                                            status_code = 429               ,
                                            errors      = ['Rate limited']  ),
                    response_data    = dict(retry_after = 60))
```

#### Error Injection

```python
class Surrogate__State__With_Errors(Type_Safe):
    fail_next_request : bool = False
    fail_after_n      : int  = 0
    request_count     : int  = 0
    error_response    : Dict = None
    
    def should_fail(self) -> bool:
        self.request_count += 1
        if self.fail_next_request:
            self.fail_next_request = False
            return True
        if self.fail_after_n > 0 and self.request_count >= self.fail_after_n:
            return True
        return False
```

#### Latency Simulation

```python
import asyncio

class Surrogate__State__With_Latency(Type_Safe):
    latency_ms : int  = 0
    enabled    : bool = False
    
    async def apply_latency(self):
        if self.enabled and self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)
```

## Quick Start Checklist

When creating a new surrogate:

- [ ] Create `Surrogate__State__[Service]` with all data fields and `reset()` method
- [ ] Create request/response schemas matching real API contracts
- [ ] Create `Routes__Surrogate__[Service]` with endpoints mirroring real API
- [ ] Implement `setup_routes()` registering all endpoints
- [ ] Create `Surrogate__Service__[Service]` wiring routes together
- [ ] Write tests covering success paths, error cases, and state mutations
- [ ] Optionally: record real API responses for realistic test data
- [ ] Optionally: implement client toggle for live/surrogate switching

## Critical Rules

### ALWAYS
- Use Type_Safe for state, schemas, and services (never Pydantic)
- Implement `reset()` on state classes
- Implement `setup_routes()` on route classes
- Return consistent response structure (`response_context` + `response_data`)
- Match real API paths and response shapes
- Document routes in `ROUTES_PATHS__*` constant

### NEVER
- Use FastAPI decorators (`@app.get`, `@app.post`)
- Use Pydantic BaseModel
- Store state outside Type_Safe classes
- Skip error handling
- Invent response structures — mirror the real API

## Related Documentation

- **Type_Safe & Python Formatting Guide** (v3.1.1) — Core type system
- **OSBot-Utils Safe Primitives Reference** (v3.28.0) — Domain-specific types
- **OSBot-Fast-API Routes Development Guide** (v0.24.2) — Route implementation
- **Surrogate Dependencies: Simulating Backends for Offline-First Development** (Dinis Cruz) — Conceptual foundation