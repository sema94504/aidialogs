"use client";

import { useState } from "react";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import type { RecentMessage } from "@/lib/types";

interface RecentMessagesProps {
  messages: RecentMessage[];
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
}

export function RecentMessages({ messages }: RecentMessagesProps) {
  const [selectedMessage, setSelectedMessage] = useState<RecentMessage | null>(null);

  const handleMessageClick = (message: RecentMessage) => {
    setSelectedMessage(message);
  };

  const handleCloseDialog = () => {
    setSelectedMessage(null);
  };

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
              <p 
                className="text-sm text-muted-foreground mb-2 cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleMessageClick(message)}
              >
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

        <div className="hidden md:block overflow-x-auto">
          <Table aria-label="Таблица последних сообщений">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[120px]">User ID</TableHead>
                <TableHead className="w-[100px]">Role</TableHead>
                <TableHead className="min-w-[200px]">Preview</TableHead>
                <TableHead className="w-[160px] text-right whitespace-nowrap">Timestamp</TableHead>
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
                  <TableCell 
                    className="max-w-[400px] truncate cursor-pointer hover:text-foreground transition-colors"
                    onClick={() => handleMessageClick(message)}
                    title="Нажмите для просмотра полного текста"
                  >
                    {message.preview}
                  </TableCell>
                  <TableCell className="text-right text-sm text-muted-foreground whitespace-nowrap">
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

      <Dialog open={!!selectedMessage} onOpenChange={handleCloseDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Полный текст сообщения</DialogTitle>
            <DialogDescription>
              {selectedMessage && (
                <div className="space-y-2 text-sm">
                  <div><strong>User ID:</strong> {selectedMessage.telegram_id}</div>
                  <div>
                    <strong>Role:</strong>{" "}
                    <Badge variant={selectedMessage.role === "user" ? "default" : "secondary"}>
                      {selectedMessage.role}
                    </Badge>
                  </div>
                  <div>
                    <strong>Timestamp:</strong>{" "}
                    {formatDistanceToNow(new Date(selectedMessage.created_at), {
                      addSuffix: true,
                      locale: ru,
                    })}
                  </div>
                </div>
              )}
            </DialogDescription>
          </DialogHeader>
          {selectedMessage && (
            <div className="mt-4 p-4 bg-muted rounded-lg whitespace-pre-wrap break-words">
              {selectedMessage.full_text}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
}

