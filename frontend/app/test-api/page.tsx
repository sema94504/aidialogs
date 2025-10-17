"use client";

import { useEffect, useState } from "react";
import { getStats, APIError } from "@/lib/api-client";
import type { DashboardStats } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function TestAPIPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStats();
      setStats(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError(`API Error: ${err.message}`);
      } else {
        setError("Unknown error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-6">API Test Page</h1>

      <div className="mb-4">
        <Button onClick={fetchStats} disabled={loading}>
          {loading ? "Loading..." : "Refresh Stats"}
        </Button>
      </div>

      {error && (
        <Card className="mb-6 border-red-500">
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {stats && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Metrics</CardTitle>
              <CardDescription>Key statistics from the API</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Total Users</p>
                  <p className="text-2xl font-bold">{stats.metrics.total_users}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Messages</p>
                  <p className="text-2xl font-bold">{stats.metrics.total_messages}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Active Today</p>
                  <p className="text-2xl font-bold">{stats.metrics.active_today}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg Message Length</p>
                  <p className="text-2xl font-bold">
                    {stats.metrics.avg_message_length.toFixed(1)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Activity Chart</CardTitle>
              <CardDescription>Last 7 days activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {stats.activity_chart.map((point) => (
                  <div key={point.date} className="flex justify-between items-center">
                    <span className="text-sm">{point.date}</span>
                    <span className="font-semibold">{point.count} messages</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Messages</CardTitle>
              <CardDescription>Latest messages from users</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.recent_messages.map((msg, idx) => (
                  <div key={idx} className="border-b pb-3 last:border-b-0">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-sm font-medium">
                        User {msg.telegram_id}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(msg.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm">
                      <span
                        className={
                          msg.role === "user"
                            ? "text-blue-600 font-semibold"
                            : "text-green-600 font-semibold"
                        }
                      >
                        [{msg.role}]
                      </span>{" "}
                      {msg.preview}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

