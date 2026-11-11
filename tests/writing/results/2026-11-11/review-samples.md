# Samples for human voice calibration

These are verbatim excerpts from the pilot, with version labels omitted. For each pair, choose A, B, or no preference and name the phrase that influenced you. Judge ease of understanding and useful precision, rather than length alone. The complete responses and version key are in `run.json`.

## 1. Opening a change report

### A

I restricted `retry_invoice` to explicit 429 rejections so a timeout cannot trigger an automatic resend of an invoice the provider may already have accepted.

### B

Callers now receive `DeliveryUnknown` after a timeout and must check delivery status before trying again. The provider may have accepted the invoice before the connection timed out, and it has no idempotency-key support, so retrying could send the invoice twice.

## 2. Explaining a recovery risk

These excerpts cover the same recovery findings from a queue comparison.

### A

Recovery also needs separate assessment. Postgres lost no jobs in its forced-restart exercise, but that exercise did not measure throughput or duplicates. Redis recovered all pending messages after a process restart, with 12 duplicates in 10,000 deliveries. VM restart and loss of recent AOF writes remain untested, so that result does not establish the required machine-restart recovery. SMS idempotency needs attention whichever queue we use: both systems permit redelivery, and the unmeasured Postgres duplicate rate prevents a fair comparison.

### B

Recovery is still a material concern for either choice. Redis reclaimed and delivered all pending messages after a process restart, with 12 duplicates out of 10,000. That test did not establish recovery after a VM restart or loss of recent AOF writes. Postgres lost no jobs in its separate forced-restart exercise, but throughput and duplicate frequency were not measured there. The results do not establish that either system duplicates less. Include SMS idempotency in the prototype because both queues permit redelivery and the current SMS handler cannot safely absorb it.
