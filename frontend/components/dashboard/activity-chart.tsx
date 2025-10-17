"use client";

import { format } from "date-fns";
import { ru } from "date-fns/locale";
import {
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ChartDataPoint, MetricType } from "@/lib/types";
import { METRIC_CONFIGS } from "./metrics-cards";

interface ActivityChartProps {
  data: ChartDataPoint[];
  selectedMetrics: MetricType[];
}

const CHART_COLORS = {
  total_users: "#3b82f6",      // blue
  total_messages: "#10b981",   // green
  avg_message_length: "#f59e0b", // amber
};

export function ActivityChart({ data, selectedMetrics }: ActivityChartProps) {
  const formattedData = data.map((point) => ({
    ...point,
    dateFormatted: format(new Date(point.date), "dd MMM", { locale: ru }),
  }));

  if (selectedMetrics.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Activity Chart</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            Нажмите на метрику выше, чтобы показать график
          </div>
        </CardContent>
      </Card>
    );
  }

  const selectedConfigs = METRIC_CONFIGS.filter(
    (config) => config.metricType && selectedMetrics.includes(config.metricType)
  );

  const firstMetric = selectedConfigs[0];
  const secondMetric = selectedConfigs[1];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Chart</CardTitle>
      </CardHeader>
      <CardContent>
        <div role="img" aria-label="График активности по дням">
          <ResponsiveContainer width="100%" height={300} className="md:h-[300px] lg:h-[400px]">
            <ComposedChart data={formattedData}>
              <defs>
                {selectedMetrics.map((metricType) => {
                  const color = CHART_COLORS[metricType];
                  return (
                    <linearGradient key={metricType} id={`color-${metricType}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={color} stopOpacity={0.4}/>
                      <stop offset="95%" stopColor={color} stopOpacity={0}/>
                    </linearGradient>
                  );
                })}
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="dateFormatted"
                tick={{ fontSize: 12 }}
                className="text-xs"
              />
              
              {/* Левая ось Y для первой метрики */}
              {firstMetric && (
                <YAxis 
                  yAxisId="left"
                  tick={{ fontSize: 12 }}
                  label={{ 
                    value: firstMetric.chartLabel, 
                    angle: -90, 
                    position: "insideLeft", 
                    fontSize: 12,
                    fill: CHART_COLORS[firstMetric.metricType!]
                  }}
                  stroke={CHART_COLORS[firstMetric.metricType!]}
                />
              )}
              
              {/* Правая ось Y для второй метрики */}
              {secondMetric && (
                <YAxis 
                  yAxisId="right"
                  orientation="right"
                  tick={{ fontSize: 12 }}
                  label={{ 
                    value: secondMetric.chartLabel, 
                    angle: 90, 
                    position: "insideRight", 
                    fontSize: 12,
                    fill: CHART_COLORS[secondMetric.metricType!]
                  }}
                  stroke={CHART_COLORS[secondMetric.metricType!]}
                />
              )}
              
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
                labelStyle={{ color: "hsl(var(--foreground))" }}
              />
              <Legend />
              
              {/* Первая метрика на левой оси */}
              {firstMetric && firstMetric.chartKey && (
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey={firstMetric.chartKey}
                  name={firstMetric.chartLabel}
                  stroke={CHART_COLORS[firstMetric.metricType!]}
                  strokeWidth={2}
                  fill={`url(#color-${firstMetric.metricType})`}
                  dot={{ fill: CHART_COLORS[firstMetric.metricType!], r: 3 }}
                  activeDot={{ r: 5 }}
                />
              )}
              
              {/* Вторая метрика на правой оси */}
              {secondMetric && secondMetric.chartKey && (
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey={secondMetric.chartKey}
                  name={secondMetric.chartLabel}
                  stroke={CHART_COLORS[secondMetric.metricType!]}
                  strokeWidth={2}
                  fill={`url(#color-${secondMetric.metricType})`}
                  dot={{ fill: CHART_COLORS[secondMetric.metricType!], r: 3 }}
                  activeDot={{ r: 5 }}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

