"use client";
import type { Metadata } from "next";
import { ThemeProvider } from "@/components/theme-provider"
import { useState, useEffect } from "react"
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import localFont from "next/font/local";
import "./globals.css";
import { IconBrandTabler, IconSettings, IconHome, IconSun, IconMoon } from "@tabler/icons-react";
import Link from "next/link";
import { motion } from "framer-motion";
import Image from "next/image";
import { Toaster } from "@/components/ui/toaster"
import { useTheme } from "next-themes"

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

const metadata: Metadata = {
  title: "Caffeinated Whale Desktop",
  description: "Manage Frappe Docker instances",
};

const links = [
  {
    label: "Home",
    href: "#",
    icon: (
      <IconHome className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
    ),
  },
  {
    label: "Terminal",
    href: "#",
    icon: (
      <IconBrandTabler className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
    ),
  },
  {
    label: "Settings",
    href: "#",
    icon: (
      <IconSettings className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
    ),
  },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [open, setOpen] = useState(false);
  console.log(metadata)
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          <div className="h-screen rounded-md flex flex-col md:flex-row bg-gray-100 dark:bg-neutral-800 w-full flex-1 max-w-100vh mx-auto border border-neutral-200 dark:border-neutral-700 overflow-hidden">
            <Sidebar open={open} setOpen={setOpen}>
              <SidebarBody className="flex flex-col h-full">
                <div className="flex-1 overflow-y-auto overflow-x-hidden">
                  <Logo />
                  <div className="mt-8 flex flex-col gap-2">
                    {links.map((link, idx) => (
                      <SidebarLink key={idx} link={link} />
                    ))}
                  </div>
                </div>
                <div className="mt-auto">
                  <ThemeToggle />
                </div>
              </SidebarBody>
            </Sidebar>
            <main className="flex-1 overflow-y-auto">
              {children}
            </main>
            <Toaster />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}

export const Logo = () => {
  return (
    <Link
      href="#"
      className="font-normal flex space-x-2 items-center text-sm text-black dark:text-white py-1 relative z-20"
    >
      <Image src="/cw.png" alt="Logo" width={25} height={25} />
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-medium whitespace-pre"
      >
        Caffeinated Whale
      </motion.span>
    </Link>
  );
};

export const LogoIcon = () => {
  return (
    <Link
      href="#"
      className="font-normal flex space-x-2 items-center text-sm text-black dark:text-white py-1 relative z-20"
    >
      <Image src="/cw.png" alt="Logo" width={25} height={25} />
    </Link>
  );
};

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  return (
    <SidebarLink
      link={{
        label: theme === 'dark' ? 'Light Mode' : 'Dark Mode',
        href: "#",
        icon: theme === 'dark' ? (
          <IconSun className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
        ) : (
          <IconMoon className="text-neutral-700 dark:text-neutral-200 h-5 w-5 flex-shrink-0" />
        ),
      }}
      onClick={toggleTheme}
    />
  )
}

