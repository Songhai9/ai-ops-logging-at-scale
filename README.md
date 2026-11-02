# Logging and alerting lab

A local Docker Compose lab with Grafana, Loki, Alloy, Prometheus, Node Exporter
and Alertmanager. It demonstrates centralized JSON logs, metrics, dashboard
links, severity routing and inhibition. It is a single-host learning stack.

## Run the complete stack

From the repository root:

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Grafana: http://localhost:3000 (admin/admin). Prometheus: http://localhost:9090.
Alertmanager: http://localhost:9093. Application: http://localhost:5000.
Loki readiness is http://localhost:3100/ready; Loki has no equivalent of Grafana's UI.

The dashboard is provisioned in the **AIOps Labs** folder. Prometheus and Loki
have explicit UIDs matching its references. Data links are configured on its
first three metric panels, rather than promised on every dashboard.

## Generate data and exercise alerts

```bash
curl http://localhost:5000/generate-logs
curl http://localhost:5000/simulate-slow-requests
```

`HighErrorRate` uses `rate(http_errors_total[5m]) > 0.05` for one minute:
the threshold means **0.05 error events per second per series**, not 5%.
The synthetic `/simulate-incident` endpoint increments this counter for internal
payment failures even though its HTTP response is 200. Do not divide that
counter by HTTP requests to claim an HTTP failure percentage. To obtain that
percentage, first instrument actual HTTP responses consistently and then use
the 5xx request count divided by total request count over the same window.
One burst is not a reliable alert test: `rate()` needs at least two scrapes of
the same series, and the condition must remain true for `for`.

The p95 query currently produces one value per label combination (including
endpoint/method/instance). That is valid. To compute p95 across replicas, sum
the bucket rates by the desired dimensions **and `le`** before applying
`histogram_quantile`.

To test a stopped application while keeping the notification receiver alive:

```bash
docker compose stop sample-app
docker compose logs -f alert-receiver
# After checking Prometheus /alerts and Alertmanager, in another terminal:
docker compose start sample-app
```

`ServiceDown` requires 30 seconds in firing condition, plus scrape/evaluation
scheduling and Alertmanager grouping delay. `alert-receiver` is a separate
container reusing the sample application image; it receives and logs webhooks
even while `sample-app` is stopped. This only separates application failures:
the entire stack still shares a Docker host.

## Important semantics

- `resolve_timeout` is a fallback for alerts without `EndsAt`. Prometheus sends
  `EndsAt`, so this setting does not determine resolution of its alerts.
- `group_interval` checks for changed alert groups; it does not send an update
  every interval when nothing changed. Repetition is governed by
  `repeat_interval`, checked on that schedule.
- Inhibition matches the same cluster/environment/service/instance to avoid
  suppressing warnings for a different instance of the service.
- Alloy keeps its positions under `/var/lib/alloy/data` in a named volume.
  This preserves its local state when the collector container is replaced;
  it is not a guarantee of exactly-once delivery or zero log loss.
- `logging=enabled` is a Docker label only; the current discovery configuration
  collects all discovered containers and does not filter using that label.

## Retention is not configured

`reject_old_samples_max_age: 168h` rejects late-arriving logs. It is **not** a
7-day deletion policy. The current stack does not enable automatic log deletion.
If a 31-day retention is desired, add these blocks to the Loki configuration
after choosing that policy:

```yaml
compactor:
  working_directory: /tmp/loki/compactor
  retention_enabled: true
  delete_request_store: filesystem

limits_config:
  # Merge this with the existing limits_config; do not duplicate the section.
  retention_period: 744h
```

The existing TSDB/v13 schema has the required 24-hour index period. Keep the
Compactor working directory persistent, as it is here under the Loki volume.

## Lab directories

- `lab1/`: centralized logs.
- `lab2/`: varied structured logs for LogQL practice.
- `lab3/`: metrics/log correlation and its dashboard, without Alertmanager.
- repository root: complete metrics-alerting demonstration.

Run one stack at a time: the lab files intentionally reuse ports and container
names. For lab 3, use `docker compose -f lab3/docker-compose.yml up -d --build`
from the repository root. Switch off the previous stack first using its same
Compose file. Do not remove volumes unless you intend to discard their data.

## Boundaries of this lab

- The current alerts are PromQL rules evaluated by Prometheus. There are no
  configured LogQL alert rules in Loki. Setting `ruler.alertmanager_url` alone
  does not create such rules. The Ruler uses the Docker service address and
  explicitly enables Alertmanager API v2 for compatibility with Loki 3.0.0.
- `cardinality_limit` limits index-query cardinality; it is not a cap on the
  number of ingested streams. For an explicit active-stream limit, inspect
  `max_global_streams_per_user` and size it for the workload.
- No Tempo service, real trace instrumentation or AI anomaly detector is
  included. Synthetic trace IDs in JSON do not create distributed traces.
- Filesystem storage, replication factor 1 and an in-memory ring are suitable
  for this local exercise; they do not demonstrate high availability or scaling.
- Pin container versions or digests after validating them. Several images still
  use `latest`; this patch does not claim to validate a version upgrade.
- On Docker Desktop, Node Exporter observes the Linux VM/container environment,
  not native macOS host metrics. Its value depends on the host/mount setup.
- Local lab defaults (anonymous Grafana viewer, demo credentials, published
  service ports and root containers) require a separate deployment design before
  using the stack on a shared or public host.

## Validation commands

```bash
docker compose config --quiet
docker compose run --rm --no-deps --entrypoint promtool prometheus check config /etc/prometheus/prometheus.yml
docker compose run --rm --no-deps --entrypoint amtool alertmanager check-config /etc/alertmanager/alertmanager.yml
docker compose run --rm --no-deps loki -config.file=/etc/loki/config.yml -verify-config=true
docker compose run --rm --no-deps alloy validate /etc/alloy/config.alloy
```

Configuration validation is necessary but does not replace live checks of
ingestion, dashboard rendering, alert transitions and webhook delivery.
