export interface Metrics {
  total_users: number;
  total_messages: number;
  active_today: number;
  avg_message_length: number;
}

export interface ActivityDataPoint {
  date: string;
  count: number;
}

export interface RecentMessage {
  telegram_id: number;
  role: "user" | "assistant";
  preview: string;
  created_at: string;
}

export interface DashboardStats {
  metrics: Metrics;
  activity_chart: ActivityDataPoint[];
  recent_messages: RecentMessage[];
}

