export function describeOutboxPolicy() {
  return {
    retries: 5,
    backoff: "exponential",
    deadLetterAfter: 5,
    conflictPolicy: "review_on_server"
  };
}
