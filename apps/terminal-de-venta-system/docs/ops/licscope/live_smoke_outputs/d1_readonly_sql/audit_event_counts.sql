SELECT event_type, COUNT(*) AS count FROM audit_events GROUP BY event_type ORDER BY count DESC LIMIT 50;
