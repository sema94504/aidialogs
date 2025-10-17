import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AIDialogs Dashboard",
  description: "Telegram bot analytics dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <header className="border-b" role="banner">
          <nav 
            className="container mx-auto px-4 py-4 flex items-center justify-between" 
            role="navigation"
            aria-label="Основная навигация"
          >
            <div className="flex items-center gap-6">
              <Link 
                href="/" 
                className="text-xl font-bold focus:outline-none focus:ring-2 focus:ring-primary rounded-sm"
                aria-label="Главная страница AIDialogs"
              >
                AIDialogs
              </Link>
              <div className="hidden md:flex gap-4" role="menubar">
                <Link
                  href="/dashboard"
                  className="text-sm font-medium hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded-sm px-2 py-1"
                  role="menuitem"
                >
                  Dashboard
                </Link>
                <Link
                  href="/chat"
                  className="text-sm font-medium text-muted-foreground hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded-sm px-2 py-1"
                  role="menuitem"
                >
                  Chat
                </Link>
              </div>
            </div>
          </nav>
        </header>
        
        <main className="flex-1" role="main">{children}</main>
        
        <footer className="border-t py-4 mt-8" role="contentinfo">
          <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
            AIDialogs Dashboard v0.1.0
          </div>
        </footer>
      </body>
    </html>
  );
}
