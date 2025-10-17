"use client";

import { formatDistanceToNow } from "date-fns";
import { ru } from "date-fns/locale";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { RecentMessage } from "@/lib/types";

interface RecentMessagesProps {
  messages: RecentMessage[];
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
}

export function RecentMessages({ messages }: RecentMessagesProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Messages</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="block md:hidden space-y-4" role="list" aria-label="Последние сообщения">
          {messages.map((message, idx) => (
            <Card key={idx} className="p-4 min-h-[44px]" role="listitem">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm" aria-label={`Пользователь ${message.telegram_id}`}>
                  User {message.telegram_id}
                </span>
                <Badge
                  variant={message.role === "user" ? "default" : "secondary"}
                  aria-label={`Роль: ${message.role}`}
                >
                  {message.role}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                {truncateText(message.preview, 50)}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatDistanceToNow(new Date(message.created_at), {
                  addSuffix: true,
                  locale: ru,
                })}
              </p>
            </Card>
          ))}
        </div>

        <div className="hidden md:block">
          <Table aria-label="Таблица последних сообщений">
            <TableHeader>
              <TableRow>
                <TableHead>User ID</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Preview</TableHead>
                <TableHead className="text-right">Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {messages.map((message, idx) => (
                <TableRow key={idx}>
                  <TableCell className="font-medium">
                    {message.telegram_id}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={message.role === "user" ? "default" : "secondary"}
                      aria-label={`Роль: ${message.role}`}
                    >
                      {message.role}
                    </Badge>
                  </TableCell>
                  <TableCell className="max-w-md">
                    {truncateText(message.preview, 100)}
                  </TableCell>
                  <TableCell className="text-right text-sm text-muted-foreground">
                    {formatDistanceToNow(new Date(message.created_at), {
                      addSuffix: true,
                      locale: ru,
                    })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

