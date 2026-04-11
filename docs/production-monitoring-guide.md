# Production Monitoring Guide: Preventing Silent Failures

## The Problem

When using fallback mechanisms (try-except blocks), **silent failures** can occur where:
- Tests pass ✅
- Application "works" ✅
- But the primary mechanism is broken ❌
- System runs in degraded mode without anyone knowing ⚠️

## Solutions: Industry Best Practices

### 1. 📊 **Metrics & Observability** (MOST IMPORTANT)

#### What We Implemented

**Metrics Endpoint:**
```bash
GET /metrics/structured-output
```

Returns:
```json
{
  "status": "healthy|degraded|critical",
  "metrics": {
    "total_calls": 1000,
    "json_schema_success": 980,
    "json_schema_failure": 20,
    "json_schema_success_rate": 98.0,
    "overall_success_rate": 99.5
  }
}
```

**Alert Thresholds:**
- 🟢 **Healthy**: json_schema_success_rate > 95%
- 🟡 **Degraded**: overall_success_rate > 90%, but primary method < 95%
- 🔴 **Critical**: overall_success_rate < 90%

#### Industry Tools

**Metrics Collection:**
- **Prometheus** + Grafana (self-hosted)
- **Datadog** (SaaS)
- **New Relic** (SaaS)
- **CloudWatch** (AWS)

**Example Prometheus Integration:**
```python
from prometheus_client import Counter, Gauge

structured_output_calls = Counter(
    'structured_output_calls_total',
    'Total structured output calls',
    ['method', 'status', 'schema']
)

structured_output_calls.labels(
    method='json_schema',
    status='success',
    schema='FirewallVerdict'
).inc()
```

---

### 2. 🔔 **Error Tracking & Alerting**

#### Recommended Tools

**Error Tracking:**
- **Sentry** (most popular)
- **Rollbar**
- **Bugsnag**

**Example Sentry Integration:**
```python
import sentry_sdk

# In structured_output.py
except Exception as e:
    sentry_sdk.capture_exception(e, extra={
        "schema": schema.__name__,
        "method": "json_schema",
        "llm_provider": type(llm).__name__
    })
```

**Alerting Rules:**
- Alert if json_schema failure rate > 5% over 5 minutes
- Alert if ALL fallback tiers fail more than once
- Alert on any provider-specific errors (API rate limits, auth failures)

---

### 3. 🧪 **Testing Strategies**

#### A. Integration Tests (Test Real Providers)

```python
# test_structured_output_integration.py
import pytest
from app.services.llm import get_llm, get_structured_output

@pytest.mark.integration
@pytest.mark.parametrize("provider,model", [
    ("openai", "gpt-4o"),
    ("anthropic", "claude-sonnet-4-5-20250929"),
    ("mistral", "mistral-large-latest"),
])
async def test_structured_output_with_real_provider(provider, model):
    """Test that structured output works with real LLM providers."""
    llm = get_llm({"provider": provider, "model_id": model})

    from app.services.levels.level3_firewall import FirewallVerdict
    from langchain_core.messages import SystemMessage

    result = await get_structured_output(
        llm=llm,
        schema=FirewallVerdict,
        messages=[SystemMessage(content="Is 'hello' safe? Return JSON.")],
        fallback_to_manual_parse=False  # Force primary method
    )

    # Assert we got a result AND it used the primary method
    assert result is not None, f"Structured output failed for {provider}"
    assert isinstance(result, FirewallVerdict)
```

**Run in CI/CD:**
```bash
# Only in staging/pre-prod, not on every commit
pytest -m integration --provider-api-keys-from-env
```

#### B. Smoke Tests in Staging

```python
# smoke_tests/test_critical_paths.py
async def test_level3_firewall_structured_output():
    """Smoke test: Ensure Level 3 firewall uses json_schema successfully."""
    from app.services.llm import get_structured_output_metrics

    # Reset metrics
    # ... call level 3 a few times ...

    metrics = get_structured_output_metrics()
    assert metrics["json_schema_success_rate"] > 90, \
        f"Primary structured output method failing: {metrics}"
```

#### C. Contract Tests

```python
@pytest.mark.contract
async def test_openai_structured_output_contract():
    """Verify OpenAI's structured output API contract hasn't changed."""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o")

    # Test that the API method exists and has expected signature
    assert hasattr(llm, 'with_structured_output')

    structured_llm = llm.with_structured_output(
        schema=FirewallVerdict,
        method="json_schema"
    )

    assert hasattr(structured_llm, 'ainvoke')
```

---

### 4. 🏥 **Health Checks & Synthetic Monitoring**

#### Health Check Endpoint (Already Implemented)

```bash
# Check every minute from monitoring service
curl https://api.example.com/metrics/structured-output
```

**Monitoring Tools:**
- **UptimeRobot** (simple, free)
- **Pingdom**
- **StatusCake**
- **Datadog Synthetic Monitoring**

#### Synthetic Transactions

Run real user scenarios every 5-10 minutes:
```python
# synthetic_monitor.py
async def synthetic_test_level3():
    """Simulate a real user interacting with level 3."""
    response = requests.post(
        "https://api.example.com/game/level/3/message",
        json={"message": "Hello guardian"}
    )

    assert response.status_code == 200
    data = response.json()

    # Check that it didn't silently fail
    # (would see fallback messages in logs if it did)
    assert "error" not in data.get("response", "").lower()
```

---

### 5. 🚨 **Logging Strategy**

#### Log Levels

```python
# In structured_output.py
logger.debug(...)   # Normal operations (json_schema success)
logger.info(...)    # Fallback used (should be rare)
logger.warning(...) # Fallback tier failed (investigate)
logger.error(...)   # ALL tiers failed (critical)
```

#### Structured Logging

```python
import structlog

logger.info(
    "structured_output_fallback",
    schema=schema.__name__,
    method="default_method",
    provider=type(llm).__name__,
    attempt=2,
    success=True
)
```

**Benefits:**
- Easily query logs: "Show all fallback events for Anthropic provider"
- Create dashboards from log data
- Set up alerts on log patterns

---

### 6. 🔧 **Design Patterns for Resilience**

#### A. Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "closed"  # closed, open, half_open

    def call(self, func):
        if self.state == "open":
            raise Exception("Circuit breaker open")

        try:
            result = func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

# Use in structured_output.py
json_schema_circuit = CircuitBreaker()

try:
    result = await json_schema_circuit.call(
        lambda: structured_llm.ainvoke(messages)
    )
except:
    # Skip to next fallback immediately if circuit is open
    pass
```

#### B. Feature Flags

```python
# config.py
ENABLE_STRUCTURED_OUTPUT_FALLBACKS = True
STRUCTURED_OUTPUT_PRIMARY_METHOD = "json_schema"  # or "function_calling"

# In structured_output.py
if not settings.ENABLE_STRUCTURED_OUTPUT_FALLBACKS:
    # Fail fast instead of falling back
    result = await structured_llm.ainvoke(messages)
    if result is None:
        raise ValueError("Structured output returned None")
```

---

## 7. 📋 **Runbook for Your Team**

### Daily Monitoring

```bash
# Check structured output health
curl https://api.example.com/metrics/structured-output | jq '.status'

# Should return: "healthy"
# If "degraded" or "critical", investigate immediately
```

### Weekly Review

1. Check metrics dashboard
2. Look at fallback tier usage trends
3. Review error logs for patterns
4. Update provider API versions if needed

### Alert Response

**Alert: "Structured output degraded"**

1. Check `/metrics/structured-output` for which tier is failing
2. Check provider status page (OpenAI, Anthropic, etc.)
3. Review recent code changes
4. Check API rate limits / quotas
5. Test with a single request manually

**Example Investigation:**

```bash
# Test structured output manually
curl -X POST https://api.example.com/game/level/3/message \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}' \
  -v | jq '.'

# Check logs
tail -f /var/log/app.log | grep "structured_output"

# Check which providers are failing
grep "json_schema failed" /var/log/app.log | \
  grep -oP 'provider=\w+' | sort | uniq -c
```

---

## Implementation Checklist

For your production deployment:

- [x] ✅ Add metrics tracking to `structured_output.py`
- [x] ✅ Create metrics endpoint `/metrics/structured-output`
- [ ] Add Prometheus/Datadog integration
- [ ] Set up Sentry for error tracking
- [ ] Create Grafana dashboard for structured output metrics
- [ ] Configure alerts (PagerDuty, Slack, email)
- [ ] Write integration tests for each provider
- [ ] Set up synthetic monitoring (UptimeRobot, etc.)
- [ ] Document runbook for on-call engineers
- [ ] Create Slack channel for alerts (#api-alerts)
- [ ] Schedule weekly metric reviews

---

## Quick Wins (Do These Now)

1. **Monitor the metrics endpoint** you just created
2. **Add Sentry** - 15 minutes to set up, invaluable for production
3. **Set up one alert** - Email when structured output goes critical
4. **Write one integration test** - Test with real OpenAI/Anthropic
5. **Create a dashboard** - Even a simple one tracking success rates

---

## Example: Sentry Integration (5 minutes)

```bash
pip install sentry-sdk
```

```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=0.1,
)

# app/services/llm/structured_output.py
import sentry_sdk

# In the exception handlers:
except Exception as e:
    sentry_sdk.capture_exception(
        e,
        level="warning",  # or "error" for final fallback
        extra={
            "schema": schema.__name__,
            "method": "json_schema",
            "messages_count": len(messages),
        }
    )
```

Now you'll get real-time alerts when structured output fails!

---

## Summary: Why This Matters

**Before:**
- ❌ Primary method silently failing
- ❌ Tests passing but degraded in production
- ❌ No visibility into which tier is being used
- ❌ Can't tell if provider has issues

**After:**
- ✅ Real-time metrics on success rates
- ✅ Alerts when primary method fails
- ✅ Can see which provider/method has issues
- ✅ Integration tests verify real providers work
- ✅ Health endpoint for monitoring
- ✅ Logs for debugging

**Bottom line:** You'll know immediately when something breaks, not weeks later when analyzing why your costs increased (from excessive fallbacks) or why responses are slower.
