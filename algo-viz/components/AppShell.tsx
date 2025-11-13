'use client'
import { useState } from 'react'
import {
  BookOpen,
  Menu,
  X,
  Home,
  Calculator,
  Wrench,
  Activity,
  Flame,
  Settings,
  Brain,
  FileText,
  Video,
  Zap,
  ChevronLeft,
  ChevronRight,
  Search,
  User
} from 'lucide-react'
import { usePathname } from 'next/navigation'

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  const subjects = [
    {
      id: 1,
      name: 'Operational Research',
      icon: <Calculator className="w-5 h-5" />,
      path: '/operational-research',
      available: true
    },
    {
      id: 2,
      name: 'Mechanical Systems',
      icon: <Settings className="w-5 h-5" />,
      path: '/mechanical-systems',
      available: true
    },
    {
      id: 3,
      name: 'Strength of Materials',
      icon: <Activity className="w-5 h-5" />,
      path: '/strength-of-materials',
      available: true
    },
    {
      id: 4,
      name: 'Engineering Mathematics',
      icon: <Flame className="w-5 h-5" />,
      path: '/engineering-mathematics',
      available: true
    },
    {
      id: 5,
      name: 'Control Systems',
      icon: <Wrench className="w-5 h-5" />,
      path: '/control-systems',
      available: false
    },
    {
      id: 6,
      name: 'Machine Learning',
      icon: <Brain className="w-5 h-5" />,
      path: '/machine-learning',
      available: false
    }
  ]

  const isActive = (path: string) => pathname === path

  return (
    <div className="min-h-screen bg-slate-900 text-gray-100">
      {/* Topbar */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/6 backdrop-blur bg-slate-900/40">
        <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-md text-gray-300 hover:text-white hover:bg-white/5 transition"
              aria-label="Toggle menu"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            <a href="/" className="flex items-center gap-3 group">
              <BookOpen className="w-8 h-8 text-purple-400 group-hover:text-purple-300 transition-colors" />
              <h1 className="text-lg sm:text-2xl font-semibold tracking-tight text-white">
                Algo-Viz
              </h1>
            </a>

            <div className="hidden md:flex items-center ml-4 bg-slate-800/50 px-3 py-1 rounded-lg border border-white/3">
              <Search className="w-4 h-4 text-gray-300 mr-2" />
              <input
                className="bg-transparent outline-none text-sm text-gray-200 placeholder:text-gray-400"
                placeholder="Search solvers, topics..."
                aria-label="Search"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <nav className="hidden lg:flex items-center gap-4">
              <a className="text-sm text-gray-300 hover:text-white transition" href="#">
                Docs
              </a>
              <a className="text-sm text-gray-300 hover:text-white transition" href="#about">
                About
              </a>
              <a className="text-sm text-gray-300 hover:text-white transition" href="#contact">
                Contact
              </a>
            </nav>

            <button className="hidden md:inline-flex items-center gap-2 bg-gradient-to-br from-purple-600 to-purple-500 px-3 py-1.5 rounded-lg text-sm font-medium shadow-sm hover:opacity-95 transition">
              Sign in
            </button>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={`fixed top-14 left-0 z-40 h-[calc(100vh-4rem)] transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${collapsed ? 'w-20' : 'w-64'}
        `}
      >
        <div
          className="h-full flex flex-col bg-gradient-to-b from-slate-800/90 to-slate-900/95 backdrop-blur border-r border-white/6 shadow-lg"
          style={{ minWidth: collapsed ? 80 : 256 }}
        >
          {/* header inside sidebar */}
          <div className="flex items-center justify-between px-4 py-4">
            <div className="flex items-center gap-3">
              <BookOpen className="w-7 h-7 text-purple-400" />
              {!collapsed && <div className="text-white font-semibold">Algo-Viz</div>}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setCollapsed(!collapsed)}
                className="p-1 rounded-md hover:bg-white/5 transition"
                aria-label="Toggle collapse"
                title={collapsed ? 'Expand' : 'Collapse'}
              >
                {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="px-3">
            {/* subjects */}
            <div className="mt-2">
              <div className={`text-xs font-semibold text-gray-400 uppercase tracking-wide px-2 mb-2 ${collapsed ? 'hidden' : ''}`}>
                Subjects
              </div>

              <nav className="space-y-0">
                {subjects.map((subject) => {
                  const active = isActive(subject.path)
                  return (
                    <a
                      key={subject.id}
                      href={subject.available ? subject.path : '#'}
                      onClick={() => setSidebarOpen(false)}
                      className={`group flex items-center gap-3 px-2 py-2 rounded-md transition relative overflow-hidden
                        ${active ? 'bg-gradient-to-r from-purple-600/80 to-purple-500/70 text-white shadow-[0_6px_18px_rgba(124,58,237,0.18)]' : 'text-gray-300 hover:bg-white/5'}
                        ${subject.available ? '' : 'opacity-60 cursor-not-allowed'}
                      `}
                      aria-current={active ? 'page' : undefined}
                    >
                      <div className={`flex items-center justify-center w-8 h-8 rounded-md ${active ? 'bg-white/10' : ''}`}>
                        {subject.icon}
                      </div>

                      {!collapsed && (
                        <>
                          <span className="flex-1 text-sm font-medium truncate">{subject.name}</span>
                          {!subject.available && (
                            <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">Soon</span>
                          )}
                        </>
                      )}

                      {/* active indicator bar */}
                      {active && (
                        <span
                          className="absolute -right-1 top-1/2 -translate-y-1/2 h-10 w-1 rounded-l-md"
                          style={{ background: 'linear-gradient(180deg,#9f7aea,#6d28d9)' }}
                          aria-hidden
                        />
                      )}
                    </a>
                  )
                })}
              </nav>
            </div>
          </div>

          <div className="mt-auto px-3 pb-4">
            <div className="border-t border-white/6 pt-4">
              <div className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-white/3 transition">
                <div className="w-9 h-9 bg-gradient-to-br from-purple-600 to-purple-500 rounded-full flex items-center justify-center text-white">
                  <User className="w-4 h-4" />
                </div>

                {!collapsed && (
                  <div className="flex-1">
                    <div className="text-sm font-medium">Ahmed</div>
                    <div className="text-xs text-gray-400">Student</div>
                  </div>
                )}

                {!collapsed && (
                  <button className="text-xs bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded-md transition">
                    Logout
                  </button>
                )}
              </div>

              {!collapsed && (
                <div className="mt-3 px-2">
                  <div className="text-xs text-gray-400 mb-2">Need help?</div>
                  <button className="w-full bg-gradient-to-br from-purple-600 to-purple-500 text-white py-2 rounded-md shadow-sm">
                    View Docs
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile when sidebar open */}
      {sidebarOpen && (
        <div onClick={() => setSidebarOpen(false)} className="fixed inset-0 z-30 bg-black/40 lg:hidden" />
      )}

      {/* Main content */}
      <main className={`pt-16 transition-all duration-300 ${collapsed ? 'lg:pl-20' : 'lg:pl-64'}`}>
        {children}
      </main>
    </div>
  )
}
