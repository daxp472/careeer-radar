'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api } from '@/lib/api';
import { NotificationItem } from '@/types';
import {
  Radar,
  Briefcase,
  Activity,
  User,
  LogOut,
  Sparkles,
  Bell,
  Check,
  Clock,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [showNotifications, setShowNotifications] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const navLinks = [
    { href: '/analyze', label: 'Live Search', icon: Radar },
    { href: '/jobs', label: 'Job Database', icon: Briefcase },
    { href: '/dashboard', label: 'Command Center', icon: Activity },
    { href: '/progress', label: 'Progress', icon: Sparkles },
    { href: '/profile', label: 'Profile & Settings', icon: User },
  ];

  // Fetch notifications if logged in
  const fetchNotifications = async () => {
    if (!user) return;
    try {
      const res = await api.getNotifications(false);
      setNotifications(res.notifications || []);
      setUnreadCount(res.unread_count || 0);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, [user]);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkRead = async (id: string) => {
    try {
      await api.markNotificationRead(id);
      setNotifications(prev =>
        prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (e) {
      console.error(e);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Radar className="w-5 h-5 text-cyan-400 group-hover:rotate-45 transition-transform duration-300" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              CAREER<span className="text-blue-500">RADAR</span>
            </span>
            <span className="text-[10px] tracking-widest text-slate-400 font-mono -mt-1 uppercase">
              Continuous Market Radar
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition ${
                  isActive
                    ? 'text-blue-400 bg-blue-500/10 border border-blue-500/20 shadow-sm shadow-blue-500/5'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right Section: Auth + Notifications */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-2 sm:gap-3">
              {/* Notification Bell */}
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-900 border border-slate-800/80 transition"
                  title="Notifications"
                >
                  <Bell className="w-4 h-4" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-blue-600 px-1 text-[10px] font-bold text-white shadow-md shadow-blue-500/50 animate-pulse">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>

                {/* Notifications Dropdown */}
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
                      <div className="flex items-center gap-2">
                        <Bell className="w-4 h-4 text-blue-400" />
                        <span className="font-semibold text-sm text-slate-200">Notifications</span>
                        {unreadCount > 0 && (
                          <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full font-mono">
                            {unreadCount} new
                          </span>
                        )}
                      </div>
                      {unreadCount > 0 && (
                        <button
                          onClick={handleMarkAllRead}
                          className="text-xs text-slate-400 hover:text-blue-400 transition"
                        >
                          Mark all as read
                        </button>
                      )}
                    </div>

                    <div className="max-h-80 overflow-y-auto space-y-2.5 pr-1 custom-scrollbar">
                      {notifications.length === 0 ? (
                        <div className="py-8 text-center text-slate-500 text-xs">
                          No notifications yet.
                        </div>
                      ) : (
                        notifications.map((n) => (
                          <div
                            key={n.id}
                            className={`p-3 rounded-xl border text-xs transition relative group ${
                              n.is_read
                                ? 'bg-slate-950/40 border-slate-800/50 text-slate-400'
                                : 'bg-slate-800/40 border-blue-500/30 text-slate-200 shadow-sm'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-2 mb-1">
                              <span className="font-semibold text-slate-200 text-xs">
                                {n.title}
                              </span>
                              {!n.is_read && (
                                <button
                                  onClick={() => handleMarkRead(n.id)}
                                  className="text-[10px] text-blue-400 hover:text-blue-300 flex items-center gap-1 opacity-80 group-hover:opacity-100"
                                  title="Mark as read"
                                >
                                  <Check className="w-3 h-3" /> Read
                                </button>
                              )}
                            </div>
                            <p className="text-slate-300 text-[11px] leading-relaxed mb-2">
                              {n.message}
                            </p>
                            <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {new Date(n.created_at).toLocaleDateString()}
                              </span>
                              <Link
                                href="/dashboard"
                                onClick={() => setShowNotifications(false)}
                                className="text-blue-400 hover:text-blue-300 flex items-center gap-0.5"
                              >
                                View Radar <ChevronRight className="w-3 h-3" />
                              </Link>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* User badge */}
              <span className="text-xs font-mono text-slate-300 hidden sm:inline-block px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
                {user.display_name}
              </span>

              {/* Logout */}
              <button
                onClick={logout}
                className="flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-red-400 px-3 py-1.5 rounded-lg hover:bg-slate-900 border border-transparent hover:border-slate-800 transition"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/auth/login"
                className="text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 transition"
              >
                Sign In
              </Link>
              <Link
                href="/analyze"
                className="flex items-center gap-1.5 text-sm font-medium bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-4 py-1.5 rounded-lg shadow-md shadow-blue-500/20 hover:shadow-blue-500/30 transition"
              >
                <Sparkles className="w-3.5 h-3.5" />
                Check Market
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
