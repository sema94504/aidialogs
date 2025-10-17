import { Users, MessageSquare, Activity, MessageCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Metrics, MetricType } from "@/lib/types";

interface MetricsCardsProps {
  metrics: Metrics;
  selectedMetrics: MetricType[];
  onMetricToggle: (metric: MetricType) => void;
}

const METRIC_CONFIGS = [
  {
    key: "total_users" as keyof Metrics,
    metricType: "total_users" as MetricType,
    title: "Total Users",
    icon: Users,
    description: "Всего пользователей",
    chartLabel: "Активные пользователи",
    chartKey: "active_users" as const,
    hasChart: true,
  },
  {
    key: "total_messages" as keyof Metrics,
    metricType: "total_messages" as MetricType,
    title: "Total Messages",
    icon: MessageSquare,
    description: "Всего сообщений",
    chartLabel: "Сообщения",
    chartKey: "messages" as const,
    hasChart: true,
  },
  {
    key: "active_today" as keyof Metrics,
    metricType: null,
    title: "Active Today",
    icon: Activity,
    description: "Активных сегодня",
    hasChart: false,
  },
  {
    key: "avg_message_length" as keyof Metrics,
    metricType: "avg_message_length" as MetricType,
    title: "Avg Message Length",
    icon: MessageCircle,
    description: "Средняя длина",
    chartLabel: "Символов в день",
    chartKey: "avg_length" as const,
    hasChart: true,
  },
];

export function MetricsCards({ metrics, selectedMetrics, onMetricToggle }: MetricsCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4" role="region" aria-label="Метрики">
      {METRIC_CONFIGS.map((config) => {
        const Icon = config.icon;
        const value = metrics[config.key];
        const isSelected = config.metricType && selectedMetrics.includes(config.metricType);
        const canSelect = config.hasChart;
        
        return (
          <Card
            key={config.key}
            className={`
              transition-all touch-manipulation
              ${canSelect ? "cursor-pointer hover:scale-105 md:hover:scale-105" : ""}
              ${isSelected ? "ring-2 ring-primary shadow-lg" : ""}
            `}
            onClick={() => {
              if (config.metricType && canSelect) {
                onMetricToggle(config.metricType);
              }
            }}
            role={canSelect ? "button" : undefined}
            tabIndex={canSelect ? 0 : undefined}
            aria-pressed={canSelect ? (isSelected ? "true" : "false") : undefined}
            onKeyDown={(e) => {
              if (canSelect && config.metricType && (e.key === "Enter" || e.key === " ")) {
                e.preventDefault();
                onMetricToggle(config.metricType);
              }
            }}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {config.title}
              </CardTitle>
              <Icon 
                className={`h-4 w-4 transition-colors ${isSelected ? "text-primary" : "text-muted-foreground"}`}
                aria-hidden="true" 
              />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" aria-label={`${config.title}: ${value}`}>
                {typeof value === "number"
                  ? value.toLocaleString("ru-RU", {
                      maximumFractionDigits: 1,
                    })
                  : value}
              </div>
              <p className="text-xs text-muted-foreground">
                {config.description}
                {canSelect && <span className="ml-1 text-primary">• График</span>}
              </p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

export { METRIC_CONFIGS };

