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

export interface ChartDataPoint {
  date: string;
  active_users?: number;
  messages?: number;
  avg_length?: number;
}

export interface RecentMessage {
  telegram_id: number;
  role: "user" | "assistant";
  preview: string;
  full_text: string;
  created_at: string;
}

export interface DashboardStats {
  metrics: Metrics;
  activity_chart: ActivityDataPoint[];
  chart_data: ChartDataPoint[];
  recent_messages: RecentMessage[];
}

export type MetricType = "total_users" | "total_messages" | "avg_message_length";

