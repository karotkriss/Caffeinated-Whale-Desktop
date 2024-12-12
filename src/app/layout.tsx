import type { Metadata } from "next";
import { ThemeProvider } from "@/components/theme-provider"
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { Home, Settings, Database } from 'lucide-react';
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Caffeinated Whale Desktop",
  description: "Manage Frappe Docker instances",
};

const sidebarLinks = [
  { label: "Home", href: "/", icon: <Home size={20} /> },
  { label: "Instances", href: "/instances", icon: <Database size={20} /> },
  { label: "Settings", href: "/settings", icon: <Settings size={20} /> },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex h-screen overflow-hidden">
            <Sidebar>
              <SidebarBody>
                {sidebarLinks.map((link) => (
                  <SidebarLink key={link.href} link={link} />
                ))}
              </SidebarBody>
            </Sidebar>
            <main className="flex-1 overflow-y-auto p-4">
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}

