-- Insert a test transit card for development
-- UUID: 12345678-1234-1234-1234-123456789abc (fixed for easy configuration)
INSERT INTO transit_cards (uuid, balance, created_at)
VALUES ('12345678-1234-1234-1234-123456789abc', 25.00, datetime('now'))
ON CONFLICT(uuid) DO UPDATE SET balance=excluded.balance;