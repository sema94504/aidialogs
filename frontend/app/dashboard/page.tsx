"use client";

import { useState, useEffect } from "react";
import { getStats } from "@/lib/api-client";
import type { DashboardStats, MetricType } from "@/lib/types";
import { PeriodFilter } from "@/components/dashboard/period-filter";
import { MetricsCards } from "@/components/dashboard/metrics-cards";
import { ActivityChart } from "@/components/dashboard/activity-chart";
import { RecentMessages } from "@/components/dashboard/recent-messages";

export default function DashboardPage() {
  const [period, setPeriod] = useState<number>(7);
  const [data, setData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMetrics, setSelectedMetrics] = useState<MetricType[]>(["total_messages"]);

  const handleMetricToggle = (metric: MetricType) => {
    setSelectedMetrics((prev) => {
      if (prev.includes(metric)) {
        // Убрать метрику
        return prev.filter((m) => m !== metric);
      } else {
        // Добавить метрику (максимум 2)
        if (prev.length >= 2) {
          // Заменить первую метрику
          return [prev[1], metric];
        }
        return [...prev, metric];
      }
    });
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const stats = await getStats(period);
        setData(stats);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Не удалось загрузить данные"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [period]);

  if (loading) {
    return (
      <div className="container mx-auto p-4 md:p-6 lg:p-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Dashboard</h1>
        </div>
        <div className="flex items-center justify-center h-64" role="status" aria-live="polite">
          <div className="text-lg text-muted-foreground">Загрузка...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4 md:p-6 lg:p-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Dashboard</h1>
        </div>
        <div 
          className="flex items-center justify-center h-64" 
          role="alert" 
          aria-live="assertive"
        >
          <div className="text-lg text-red-500">Ошибка: {error}</div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="container mx-auto p-4 md:p-6 lg:p-8 2xl:p-10 space-y-6">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <PeriodFilter value={period} onChange={setPeriod} />
      </header>

      <section aria-label="Ключевые метрики">
        <MetricsCards 
          metrics={data.metrics} 
          selectedMetrics={selectedMetrics}
          onMetricToggle={handleMetricToggle}
        />
      </section>

      <section aria-label="График активности">
        <ActivityChart 
          data={data.chart_data} 
          selectedMetrics={selectedMetrics}
        />
      </section>

      <section aria-label="Последние сообщения">
        <RecentMessages messages={data.recent_messages} />
      </section>
    </div>
  );
}

